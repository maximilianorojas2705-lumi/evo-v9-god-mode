import os
from flask import Flask, jsonify

# Esta variable es la que busca gunicorn, si no está explota con status 3
app = Flask(__name__)

@app.route("/")
def home():
    return "EVO V9 GOD MODE - LIVE - Blindado", 200

@app.route("/health")
def health():
    return jsonify({"status": "live", "version": "v9-blindado", "ram": "ok"}), 200

@app.route("/telegram", methods=["POST"])
def telegram_placeholder():
    # Placeholder para que no falle hasta que conectemos el bot
    return jsonify({"ok": True, "msg": "bot listo para conectar"}), 200

# Esto es solo para test local, en Render usa gunicorn
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
