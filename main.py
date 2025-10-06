from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pytz
from data.sheets_helper import add_transaction, get_all_transactions
from fastapi.responses import JSONResponse
from collections import defaultdict
from chatbot.telegram_bot import run_bot

app = FastAPI()

class TransactionRequest(BaseModel):
    date: Optional[str] = None
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
    transaction_date = request.date or timestamp
    response = add_transaction(
        transaction_date, request.category, request.amount, request.status, request.description
    )
    return response

@app.get("/analytics/")
def get_analytics():
    data = get_all_transactions()

    if isinstance(data, dict) and data.get("status") == "error":
        return JSONResponse(content=data, status_code=500)

    total_income = 0
    total_outcome = 0
    category_summary = defaultdict(float)

    for row in data:
        row = {k.lower(): v for k, v in row.items()}
        try:
            amount = float(row['amount'])
            status = row['status'].lower()
            category = row['category']

            if status == "income":
                total_income += amount
            elif status == "outcome":
                total_outcome += amount

            category_summary[category] += amount
        except Exception as e:
            print(f"❌ Skipping row due to error: {e}")

    return {
        "total_income": total_income,
        "total_outcome": total_outcome,
        "saldo": total_income - total_outcome,
        "category_summary": category_summary
    }

if __name__ == "__main__":
    run_bot()