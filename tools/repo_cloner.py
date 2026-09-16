import requests, base64, os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = "maximilianorojas2705-lumi"
REPO = "evo-v9-god-mode"

# TOP 7 REPOS DE AUTOEVOLUCION QUE VAMOS A FUSIONAR
EVOLUTION_REPOS = {
    "darwin-godel-machine": "https://github.com/0xSero/Darwin-Godel-Machine",
    "autogpt": "https://github.com/Significant-Gravitas/AutoGPT",
    "babyagi": "https://github.com/yoheinakajima/babyagi",
    "voyager-minecraft": "https://github.com/MineDojo/Voyager",
    "swe-agent": "https://github.com/princeton-nlp/SWE-agent",
    "openhands": "https://github.com/All-Hands-AI/OpenHands",
    "evo-ninja": "https://github.com/cstrnt/awesome-evo-ninja-clone"
}

def clone_and_adhere(repo_url, name):
    """Clona repo público y lo adhiere a evo-v9-god-mode/tools_evolution/"""
    print(f"Clonando {name}: {repo_url}")
    # Usamos API de GitHub para traer archivos sin git
    api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/contents"
    r = requests.get(api_url)
    if r.status_code != 200:
        return f"Error {name}: {r.text[:200]}"
    
    # Copiamos README y tools principales
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    for file_info in r.json()[:10]: # top 10 archivos
        if file_info["type"] == "file" and file_info["name"].endswith(".py"):
            file_content = requests.get(file_info["download_url"]).text
            path = f"tools_evolution/{name}_{file_info['name']}"
            content_b64 = base64.b64encode(file_content.encode()).decode()
            url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{path}"
            data = {"message": f"GOD MODE: adherir {name} - {file_info['name']}", "content": content_b64}
            requests.put(url, headers=headers, json=data)
    
    return f"✅ {name} adherido en tools_evolution/"

def main():
    for name, url in EVOLUTION_REPOS.items():
        result = clone_and_adhere(url, name)
        print(result)

if __name__ == "__main__":
    main()
