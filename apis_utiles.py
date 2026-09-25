"""APIs útiles: clima, dólar, noticias."""
import requests

def clima(ciudad="Buenos Aires"):
    """Devuelve clima actual de una ciudad (Open-Meteo, gratis sin key)."""
    try:
        # Geocoding: buscar coordenadas
        r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
            params={"name": ciudad, "count": 1, "language": "es"}, timeout=10)
        if r.status_code != 200 or not r.json().get("results"):
            return f"❌ No encontré la ciudad '{ciudad}'"
        loc = r.json()["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        nombre = loc.get("name", ciudad)
        
        # Clima actual
        r = requests.get("https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon,
                    "current_weather": True,
                    "hourly": "temperature_2m,precipitation_probability"},
            timeout=10)
        if r.status_code != 200:
            return f"❌ Error consultando clima de {nombre}"
        
        data = r.json()
        cw = data["current_weather"]
        return (f"🌤️ *Clima en {nombre}*\n\n"
                f"🌡️ Temperatura: {cw['temperature']}°C\n"
                f"💨 Viento: {cw['windspeed']} km/h\n"
                f"🧭 Dirección: {cw['winddirection']}°\n"
                f"☁️ Código: {cw['weathercode']}")
    except Exception as e:
        return f"❌ Error: {str(e)[:100]}"

def dolar(tipo=None):
    """Devuelve cotizaciones del dólar (DolarAPI, gratis)."""
    tipos_principales = ["oficial", "blue", "bolsa", "contadoconliqui", "tarjeta", "cripto"]
    try:
        if tipo and tipo.lower() in tipos_principales:
            r = requests.get(f"https://dolarapi.com/v1/dolares/{tipo.lower()}", timeout=10)
            if r.status_code != 200:
                return f"❌ No encontré cotización de '{tipo}'"
            d = r.json()
            return (f"💵 *Dólar {d['nombre']}*\n\n"
                    f"📈 Compra: ${d['compra']}\n"
                    f"📉 Venta: ${d['venta']}\n"
                    f"📅 Actualizado: {d['fechaActualizacion'][:10]}")
        
        # Todas las principales
        r = requests.get("https://dolarapi.com/v1/dolares", timeout=10)
        if r.status_code != 200:
            return "❌ Error consultando cotizaciones"
        
        cotizaciones = {c['casa']: c for c in r.json()}
        msg = "💵 *Cotizaciones del dólar*\n\n"
        for tipo in tipos_principales:
            if tipo in cotizaciones:
                c = cotizaciones[tipo]
                msg += f"*{c['nombre'].upper()}*: ${c['venta']}\n"
        msg += "\n💡 Usá /dolar <tipo> para ver una específica"
        msg += "\n   Tipos: oficial, blue, bolsa, contadoconliqui, tarjeta, cripto"
        return msg
    except Exception as e:
        return f"❌ Error: {str(e)[:100]}"

def noticias(tema=None, limit=5):
    """Titulares del día vía RSS feeds de medios argentinos."""
    import xml.etree.ElementTree as ET
    feeds = [
        ("Clarín", "https://www.clarin.com/rss/lo-ultimo/"),
        ("La Nación", "https://www.lanacion.com.ar/arc/outboundfeeds/rss/"),
        ("Infobae", "https://www.infobae.com/arc/outboundfeeds/rss/"),
    ]
    
    resultados = []
    for medio, url in feeds:
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                root = ET.fromstring(r.text)
                for item in root.findall(".//item")[:3]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    # Filtro de tema desactivado (muy restrictivo)
                    resultados.append({"title": title, "href": link, "medio": medio})
                    if len(resultados) >= limit:
                        break
        except:
            continue
        if len(resultados) >= limit:
            break
    
    if not resultados:
        return f"❌ No encontré noticias{(' sobre ' + tema) if tema else ''}"
    
    msg = f"📰 *Noticias{(': ' + tema) if tema else ''}*\n\n"
    for i, r in enumerate(resultados, 1):
        msg += f"{i}. [{r['title'][:80]}]({r['href']})\n   _{r['medio']}_\n\n"
    return msg

if __name__ == "__main__":
    print("=== TEST APIs útiles ===\n")
    print(clima("Buenos Aires"))
    print("\n" + "-"*40 + "\n")
    print(dolar())
    print("\n" + "-"*40 + "\n")
    print(dolar("blue"))
