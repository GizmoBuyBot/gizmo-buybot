import os
import time
import requests
from dotenv import load_dotenv
from telegram import Bot
from flask import Flask

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TOKEN_ADDRESS = "0xc3105500CFf134b82e88a7A6809Af00a5Ee186F3"
DEXSCREENER_API = f"https://api.dexscreener.com/latest/dex/pairs/ethereum/{TOKEN_ADDRESS.lower()}"

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

last_txn_hash = None

@app.route("/")
def home():
    return "Gizmo BuyBot is online."

def format_message(data):
    price_usd = data.get("priceUsd", "?")
    txns = data.get("txns", {}).get("m5", {})
    buys = txns.get("buys", 0)
    volume = txns.get("volume", 0)
    return f"🚀 $GIZMO Buy Detected!\nPrice: ${price_usd}\nBuys (last 5m): {buys}\nVolume: ${volume}"

def check_buys():
    global last_txn_hash
    try:
        response = requests.get(DEXSCREENER_API)
        if response.status_code != 200:
            print("DexScreener error:", response.status_code)
            return

        data = response.json().get("pair", {})
        latest_txn = data.get("lastTransactionHash")

        if latest_txn and latest_txn != last_txn_hash:
            last_txn_hash = latest_txn
            message = format_message(data)
            bot.send_message(chat_id=CHAT_ID, text=message)
            print("✅ Sent Telegram buy alert.")

    except Exception as e:
        print("⚠️ Error in check_buys:", e)

def main_loop():
    print("🚀 Gizmo BuyBot started...")
    while True:
        check_buys()
        time.sleep(20)

if __name__ == "__main__":
    from threading import Thread
    Thread(target=main_loop).start()
    app.run(host="0.0.0.0", port=10000)
