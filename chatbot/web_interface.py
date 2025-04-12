# web_interface.py

import gradio as gr
import requests
import os
from dotenv import load_dotenv
from core.service import extract_transaction_from_text

load_dotenv()
API_URL = f"{os.getenv('API_URL')}/add_transaction/"

def process_message(user_input):
    try:
        result = extract_transaction_from_text(user_input)
        api_response = requests.post(API_URL, json=result)

        if api_response.status_code == 200:
            return f"✅ Transaksi berhasil dicatat: {result['category']}, Rp{result['amount']}"
        else:
            return f"❌ Gagal mencatat transaksi: {api_response.json()}"
    except Exception as e:
        return f"⚠️ Terjadi error: {str(e)}"

iface = gr.Interface(
    fn=process_message,
    inputs="text",
    outputs="text",
    title="💰 Money Management Chatbot dengan AI",
    description="Masukkan teks transaksi Anda, dan AI akan mencatatnya ke Google Sheets."
)

if __name__ == "__main__":
    iface.launch()