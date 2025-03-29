import gradio as gr
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load API Key dari .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Konfigurasi Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# URL Backend FastAPI
url = os.getenv("API_URL")
API_URL = f"{url}/add_transaction/"

def clean_response_text(text: str) -> str:
    """
    Menghapus marker markdown (misalnya triple backticks) dari response agar dapat diparsing sebagai JSON.
    """
    # Jika response diawali dengan ``` maka hapus bagian tersebut
    if text.startswith("```"):
        # Pisahkan berdasarkan triple backticks
        parts = text.split("```")
        # Jika formatnya ```json\n{ ... }\n``` ambil bagian kedua
        if len(parts) >= 2:
            text = parts[1].strip()
            # Jika ada kata 'json' di awal, hapus juga
            if text.lower().startswith("json"):
                text = text[len("json"):].strip()
    return text

# Fungsi untuk memproses input dengan LLM (Gemini)
def process_message(user_input):
    try:
        # Prompt untuk Gemini agar bisa memahami transaksi finansial
        prompt = f"""
        Kamu adalah asisten keuangan yang membantu mencatat transaksi pengguna. 
        Identifikasi jumlah uang, kategori apakah Food, Transportasi, atau yang Lain, tanggal transaksi, status pengeluaran atau pemasukan, dan deskripsinya.

        **Jangan sertakan tanggal dalam output, karena tanggal akan ditentukan oleh sistem.**

        Contoh input pengguna:
        1. "Saya menghabiskan 50000 untuk makan sate pada 2025-03-29"
        2. "Belanja di supermarket 150000 tanggal 2025-03-28"
        3. "Bayar listrik 200000 bulan ini"

        Tolong keluarkan hasil dalam format JSON berikut:
        {{
            "category": "Kategori",
            "status": "outcome/income",
            "amount": Jumlah,
            "description": "Deskripsi transaksi"
        }}

        Sekarang, proses input ini: "{user_input}"
        """

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        # Pastikan response dalam format teks
        response_text = response.text.strip()

        # Bersihkan response dari marker markdown (jika ada)
        cleaned_text = clean_response_text(response_text)

        # Coba parsing response sebagai JSON
        try:
            result = json.loads(cleaned_text)
        except json.JSONDecodeError:
            return f"⚠️ Gemini API mengembalikan response tidak valid: {response_text}"

        # Kirim hasil ke API FastAPI
        api_response = requests.post(API_URL, json=result)

        if api_response.status_code == 200:
            return f"✅ Transaksi berhasil dicatat: {result['category']}, Rp{result['amount']}"
        else:
            return f"❌ Gagal mencatat transaksi: {api_response.json()}"

    except Exception as e:
        return f"⚠️ Terjadi error: {str(e)}"

# Buat UI dengan Gradio
iface = gr.Interface(
    fn=process_message,
    inputs="text",
    outputs="text",
    title="💰 Money Management Chatbot dengan AI",
    description="Masukkan teks transaksi Anda, dan AI akan secara otomatis memahami serta mencatatnya ke Google Sheets."
)

# Jalankan Gradio
if __name__ == "__main__":
    iface.launch()