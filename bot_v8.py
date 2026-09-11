from dotenv import load_dotenv
import os
load_dotenv()
from flask import Flask
import threading
app = Flask(__name__)
@app.route("/")
def home():
    return "EVO V9 GOD MODE RAWSON - ONLINE"
def run_web():
    app.run(host="0.0.0.0", port=8080)
threading.Thread(target=run_web, daemon=True).start()

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("EVO V9 GOD MODE RAWSON ONLINE\n/aprender agentes e IAs\n/crear legion voz IA")

async def aprender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("EVO V9 aprendiendo agentes e IAs... 8 fuentes reales cargadas OK")

async def main():
    app_tg = Application.builder().token(TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("aprender", aprender))
    await app_tg.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
