"""Skill web de EVO: buscar y leer con multiples fuentes."""
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, unquote, urlparse, parse_qs

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml",
      "Accept-Language": "es-ES,es;q=0.9"}

def limpiar_url_ddg(href):
    if "duckduckgo.com/l/" in href:
        qs = parse_qs(urlparse(href).query)
        if "uddg" in qs:
            return unquote(qs["uddg"][0])
    return href

def _buscar_ddg(query, n):
    try:
        r = requests.get(f"https://html.duckduckgo.com/html/?q={quote_plus(query)}", headers=UA, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        out = []
        for a in soup.find_all("a", class_="result__a")[:n]:
            href = limpiar_url_ddg(a.get("href", ""))
            if href.startswith("http"):
                out.append({"title": a.get_text(strip=True), "href": href})
        return out
    except Exception as e:
        print(f"[buscar ddg] {e}")
        return []

def _buscar_ddg_lite(query, n):
    try:
        r = requests.post("https://lite.duckduckgo.com/lite/", data={"q": query}, headers=UA, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        out = []
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if href.startswith("http") and "duckduckgo.com" not in href:
                out.append({"title": a.get_text(strip=True), "href": href})
            if len(out) >= n:
                break
        return out
    except Exception as e:
        print(f"[buscar lite] {e}")
        return []

def _buscar_bing(query, n):
    try:
        r = requests.get(f"https://www.bing.com/search?q={quote_plus(query)}", headers=UA, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        out = []
        for li in soup.find_all("li", class_="b_algo")[:n]:
            a = li.find("a")
            if a and a.get("href", "").startswith("http"):
                out.append({"title": a.get_text(strip=True), "href": a["href"]})
        return out
    except Exception as e:
        print(f"[buscar bing] {e}")
        return []

def buscar(query, n=5):
    """Cadena de fuentes: la primera que responde gana."""
    for fn in (_buscar_ddg, _buscar_ddg_lite, _buscar_bing):
        rs = fn(query, n)
        if rs:
            return rs
    return []

def wiki_search(query, n=3):
    """Busqueda en Wikipedia con User-Agent obligatorio + fallback."""
    # Politica de Wikimedia: User-Agent descriptivo
    UA_wiki = {"User-Agent": "EVO-Bot/1.0 (Termux; python-requests) contacto@evo.local"}
    try:
        r = requests.get("https://es.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": query,
                    "srlimit": n, "format": "json"},
            headers=UA_wiki, timeout=15)
        print(f"[wiki-search] status={r.status_code}")
        if r.status_code == 200:
            data = r.json()
            items = data.get("query", {}).get("search", [])
            if items:
                return [{"title": it["title"],
                         "href": "https://es.wikipedia.org/wiki/" + quote_plus(it["title"].replace(" ", "_"))}
                        for it in items]
    except Exception as e:
        print(f"[wiki-api] {e}")
    # Fallback: DuckDuckGo con site:es.wikipedia.org
    try:
        rs = _buscar_ddg(f"site:es.wikipedia.org {query}", n)
        if rs:
            return [{"title": r["title"], "href": r["href"]} for r in rs]
    except Exception as e:
        print(f"[wiki-ddg] {e}")
    return []


def leer_url(url, max_chars=8000):
    """Lee una URL: Jina Reader primero, BeautifulSoup de fallback."""
    try:
        r = requests.get(f"https://r.jina.ai/{url}", timeout=40)
        if r.status_code == 200 and len(r.text) > 200:
            return r.text[:max_chars]
    except Exception:
        pass
    try:
        r = requests.get(url, headers=UA, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        for t in soup(["script", "style", "nav", "footer", "header", "aside"]):
            t.decompose()
        return soup.get_text("\n", strip=True)[:max_chars]
    except Exception as e:
        print(f"[leer] {e}")
        return ""

if __name__ == "__main__":
    print("=== TEST v3 ===")
    rs = buscar("termux android")
    print(f"buscar: {len(rs)} resultados")
    for r in rs[:3]:
        print(f"  - {r['title'][:50]}")
    ws = wiki_search("mate")
    print(f"wiki: {len(ws)} resultados")
    for w in ws[:3]:
        print(f"  - {w['title']}")
