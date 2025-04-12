# chatbot/telegram_bot.py

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os
from dotenv import load_dotenv
from core.service import extract_transaction_from_text

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"{os.getenv('API_URL')}/add_transaction/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hai! Kirimkan deskripsi transaksi, misal: 'beli pulsa 50000', dan saya akan bantu catatkan 📊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    try:
        result = extract_transaction_from_text(user_input)
        api_response = requests.post(API_URL, json=result)

        if api_response.status_code == 200:
            await update.message.reply_text(f"✅ Dicatat: {result['category']} - Rp{result['amount']}")
        else:
            await update.message.reply_text(f"❌ Gagal mencatat transaksi: {api_response.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        raise Exception("❌ TELEGRAM_BOT_TOKEN tidak ditemukan di .env")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram bot is running...")
    app.run_polling()