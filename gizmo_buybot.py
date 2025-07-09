import os
import time
import requests
import logging
from telegram import Bot
from flask import Flask

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Get Telegram credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PORT = int(os.getenv("PORT", 10000))

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ BOT_TOKEN or CHAT_ID environment variables not set!")

# Flask dummy server
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Gizmo BuyBot is live"

# Pool info
PAIR_ADDRESS = "0xC8A45b49Dcf4162e6017dEb01E51C10f8D1781e0"
CHAIN = "ethereum"
GECKO_API = f"https://api.geckoterminal.com/api/v2/networks/{CHAIN}/pools/{PAIR_ADDRESS}"

def get_latest_buy():
    try:
        res = requests.get(GECKO_API)
        if res.status_code != 200:
            logger.warning("Non-200 Gecko response: %s", res.status_code)
            return None
        data = res.json()
        logger.info("✅ GeckoTerminal response received.")
        return data["data"]["attributes"]["recent_trades"][0]
    except Exception as e:
        logger.error("Error from GeckoTerminal: %s", e)
        return None

def send_buy_alert(bot, tx):
    try:
        tx_hash = tx.get("tx_hash", "unknown")
        buyer = tx.get("buyer_address", "unknown")
        value = tx.get("amount_usd", "unknown")
        message = f"💰 New Buy!\nBuyer: {buyer}\nUSD: ${value}\nTX: {tx_hash}"
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logger.error("❌ Failed to send TG alert: %s", e)

def main():
    bot = Bot(token=BOT_TOKEN)
    logger.info("🚀 Gizmo BuyBot started...")
    last_tx = None
    while True:
        tx = get_latest_buy()
        if tx:
            tx_hash = tx.get("tx_hash")
            if tx_hash != last_tx:
                logger.info("New buy: %s", tx)
                send_buy_alert(bot, tx)
                last_tx = tx_hash
            else:
                logger.info("No new buy yet.")
        time.sleep(15)

if __name__ == "__main__":
    import threading
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": PORT}).start()
    main()
