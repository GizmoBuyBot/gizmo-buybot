import requests
import json
import time
import os
import logging
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from telegram import Bot

# Configs from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = os.getenv("API_URL")
CHECK_INTERVAL = 15

# Initialize bot and scheduler
bot = Bot(token=TELEGRAM_TOKEN)
scheduler = BlockingScheduler(timezone=pytz.UTC)

# Message cache to avoid reposting
last_txn_hash = None

def fetch_buy():
    try:
        response = requests.get(API_URL)
        data = response.json()

        if not data or "data" not in data:
            logging.warning("Invalid response from GeckoTerminal")
            return

        txn = data["data"]["attributes"]["last_trade"]

        if txn["trade_type"] != "buy":
            return

        global last_txn_hash
        if txn["transaction_hash"] == last_txn_hash:
            return

        last_txn_hash = txn["transaction_hash"]

        wape_amount = round(float(txn["base_amount_formatted"]), 2)
        usd_value = round(float(txn["quote_amount_formatted"]), 2)
        token_amount = round(float(txn["token_amount_formatted"]), 2)

        tx_hash = txn["transaction_hash"]
        tx_url = f"https://explorer.apescan.dev/tx/{tx_hash}"

        message = (
            f"🟢 *Buy Alert!*\n"
            f"{wape_amount} WAPE (${'{:.2f}'.format(usd_value)}) just bought\n\n"
            f"🪙 *{token_amount} GIZMO*\n"
            f"[View TX]({tx_url})"
        )

        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error: {e}")

def main():
    scheduler.add_job(fetch_buy, "interval", seconds=CHECK_INTERVAL)
    print("🚀 GIZMO BuyBot is running...")
    scheduler.start()

if __name__ == "__main__":
    main()
