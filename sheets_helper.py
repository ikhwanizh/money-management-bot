import os
import json
import gspread
from google.oauth2.service_account import Credentials

# Load credentials dari file JSON
def get_gspread_client():
    creds = Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)

SPREADSHEET_ID = "1zmJ2tmP64Q8KdgoxrLpi_NqMEUHlhCdu2tNg1Kq3JKI"

def add_transaction(date, category, status, amount, description):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # Ambil sheet pertama
        sheet.append_row([date, category, status, amount, description])
        return {"status": "success", "message": "Transaksi berhasil ditambahkan"}
    except Exception as e:
        return {"status": "error", "message": str(e)}