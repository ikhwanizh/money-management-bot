# chatbot/telegram_bot.py

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
import requests
from core.service import extract_transaction_from_text

# === Load environment ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BASE_URL = os.environ.get("API_URL")

# === Handler ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "👋 Hai! Saya adalah bot manajemen keuangan.\n"
        "Kirim transaksi seperti:\n"
        "`beli pulsa 50000`\n"
        "`gaji freelance 1500000`\n\n"
        "Atau ketik /analisis untuk melihat ringkasan keuangan kamu 💹"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    try:
        # Proses dengan AI
        result = extract_transaction_from_text(user_input)

        # Kirim ke backend FastAPI
        response = requests.post(f"{BASE_URL}/add_transaction/", json=result)

        if response.status_code == 200:
            await update.message.reply_text(
                f"✅ Dicatat: {result['category']} - Rp{result['amount']}"
            )
        else:
            await update.message.reply_text(f"❌ Gagal mencatat: {response.text}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Terjadi error: {str(e)}")

async def show_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{BASE_URL}/analytics/")
        data = response.json()

        if "total_income" not in data:
            raise Exception("Data tidak ditemukan")

        msg = (
            f"📊 *Ringkasan Keuangan:*\n"
            f"- Total Pemasukan: Rp{data['total_income']:,}\n"
            f"- Total Pengeluaran: Rp{data['total_outcome']:,}\n"
            f"- Saldo: Rp{data['saldo']:,}\n\n"
            f"📁 *Kategori Pengeluaran:*\n"
        )

        for k, v in data["category_summary"].items():
            msg += f"• {k}: Rp{v:,}\n"

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Gagal mengambil data analitik: {str(e)}")

# === Bot Runner ===

def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        raise Exception("❌ TELEGRAM_BOT_TOKEN tidak ditemukan di .env")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analisis", show_analytics))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction))

    print("🤖 Telegram bot is running...")
    app.run_polling()