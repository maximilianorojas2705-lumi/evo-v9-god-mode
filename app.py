def get_precio(symbol="BTCUSDT"):
    symbol = symbol.upper().replace("USDT","")
    # 1. Intento con Binance (nunca falla)
    try:
        b_sym = f"{symbol}USDT"
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={b_sym}", timeout=5).json()
        if "lastPrice" in r:
            price = float(r["lastPrice"])
            cambio = float(r["priceChangePercent"])
            coin_id = MAPA.get(b_sym, "bitcoin")
            return price, cambio, coin_id
    except: pass
    # 2. Fallback CoinGecko
    try:
        coin_id = MAPA.get(symbol.upper(),"bitcoin")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"}).json()
        return float(r[coin_id]["usd"]), float(r[coin_id].get("usd_24h_change",0)), coin_id
    except:
        return None, None, None
