from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pytz
from sheets_helper import add_transaction

app = FastAPI()

class TransactionRequest(BaseModel):
    date: Optional[str] = None  # Membuat field date menjadi opsional
    category: str
    status: str
    amount: float
    description: str

def get_current_timestamp() -> str:
    wib_tz = pytz.timezone("Asia/Jakarta")
    return datetime.now(wib_tz).strftime("%Y-%m-%d %H:%M:%S")

@app.get("/")
def home():
    return {"message": "Money Management Bot is running!"}

@app.post("/add_transaction/")
def add_transaction_api(
    request: TransactionRequest, timestamp: str = Depends(get_current_timestamp)
):
    # Jika request.date tidak disediakan, gunakan timestamp default
    transaction_date = request.date or timestamp
    response = add_transaction(
        transaction_date, request.category, request.amount, request.status, request.description
    )
    return response