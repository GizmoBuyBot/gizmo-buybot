import os
import time
import requests
import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

# Telegram bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Contract info
PAIR_ADDRESS = "0xC8A45b49Dcf4162e6017dEb01E51C10f8D1781e0"  # example
CHAIN = "ethereum"  # or 'solana' or 'base' or 'bsc' etc.

# GeckoTerminal API URL
GECKO_API = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools/{PAIR_ADDRESS}"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Keepalive dummy Flask server
app = Flask(__name__)
@app.route("/")
def home():
    return "BuyBot is running."

def get_latest_buy():
    try:
        res = requests.get(GECKO_API)
        if res.status_code != 200:
            logger.warning("Non-200 response from GeckoTerminal: %s", res.status_code)
            return None
        data = res.json()
        logger.info("GeckoTerminal Response: %s", data)
        # Extract buy transaction from response (adjust as needed)
        return data["data"]["attributes"]["recent_trades"][0]  # Might fail if format changed
    except Exception as e:
        logger.error("Error fetching from GeckoTerminal: %s", e)
        return None

def send_buy_alert(bot, tx):
    try:
        tx_hash = tx.get("tx_hash", "unknown")
        buyer = tx.get("buyer_address", "unknown")
        value = tx.get("amount_usd", "unknown")
        message = f"💰 New Buy!\nBuyer: {buyer}\nUSD: ${value}\nTX: {tx_hash}"
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logger.error("Error sending alert: %s", e)

def main():
    bot = Bot(token=BOT_TOKEN)
    logger.info("🚀 GIZMO BuyBot is running...")
    last_tx_hash = None

    while True:
        tx = get_latest_buy()
        if tx:
            logger.info("Latest TX: %s", tx)
            if tx["tx_hash"] != last_tx_hash:
                send_buy_alert(bot, tx)
                last_tx_hash = tx["tx_hash"]
            else:
                logger.info("No new buy.")
        else:
            logger.warning("❌ No transaction data fetched.")
        time.sleep(15)

if __name__ == "__main__":
    import threading
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 10000}).start()
    main()
