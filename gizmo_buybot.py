import os
import time
import requests
from telegram import Bot, ParseMode
from apscheduler.schedulers.blocking import BlockingScheduler

# Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = os.getenv("API_URL")  # Your external API source for buy transactions
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 10))  # Default to 10 seconds

bot = Bot(token=TELEGRAM_TOKEN)
scheduler = BlockingScheduler()
last_tx_hash = None

def fetch_transactions():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch transactions: {e}")
        return None

def build_message(tx_data):
    pair = tx_data.get("pair", "Unknown Pair")
    txns = tx_data.get("txns", [])
    if not txns:
        return f"<b>{pair}</b>\nNo recent buys found."

    txn = txns[0]
    buyer = txn.get("buyer", "Unknown")
    amount = txn.get("amount", "N/A")
    token = txn.get("token", "GIZMO")
    value = txn.get("value_usd", "?")
    tx_hash = txn.get("tx", "")

    return (
        f"🚀 <b>Buy Alert!</b>\n\n"
        f"<b>Token:</b> {token}\n"
        f"<b>Buyer:</b> {buyer}\n"
        f"<b>Amount:</b> {amount}\n"
        f"<b>Value:</b> ${value}\n"
        f"<b>TX:</b> <a href='https://apescan.xyz/tx/{tx_hash}'>View TX</a>"
    )

def send_buy_alert(bot, tx_data):
    global last_tx_hash
    txns = tx_data.get("txns", [])

    if not txns:
        print("No transactions found. Skipping alert.")
        return

    current_tx_hash = txns[0].get("tx")
    if current_tx_hash == last_tx_hash:
        return

    last_tx_hash = current_tx_hash
    message = build_message(tx_data)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def job():
    print("Checking for new transactions...")
    tx_data = fetch_transactions()
    if tx_data:
        send_buy_alert(bot, tx_data)

def main():
    print("🚀 GIZMO BuyBot is running...")
    scheduler.add_job(job, "interval", seconds=CHECK_INTERVAL)
    scheduler.start()

if __name__ == "__main__":
    main()
