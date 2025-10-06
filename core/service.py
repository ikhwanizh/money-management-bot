import google.generativeai as genai
import os
import json

from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def clean_response_text(text: str) -> str:
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1].strip()
            if text.lower().startswith("json"):
                text = text[len("json"):].strip()
    return text

def extract_transaction_from_text(user_input: str) -> dict:
    prompt = f"""
    Kamu adalah asisten keuangan yang membantu mencatat transaksi pengguna. 
    Identifikasi jumlah uang, kategori (Food, Transportasi, atau Lain), status pengeluaran atau pemasukan, dan deskripsinya.

    Format output:
    {{
        "category": "Kategori",
        "amount": Jumlah,
        "status": "Expenses/Income",
        "description": "Deskripsi transaksi"
    }}

    Proses input ini: "{user_input}"
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    cleaned = clean_response_text(response.text.strip())

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini error: {e} — raw: {response.text}")