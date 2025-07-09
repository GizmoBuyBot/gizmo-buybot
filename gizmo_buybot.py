import os
import time
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PAIR_ADDRESS = "apechain/0xc3105500CFf134b82e88a7A6809Af00a5Ee186F3"  # GIZMO token pair on ApeChain

bot = Bot(token=BOT_TOKEN)

def fetch_dex_data():
    url = f"https://api.dexscreener.com/latest/dex/pairs/{PAIR_ADDRESS}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("pair")
        else:
            print(f"⚠️ DexScreener response {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching Dex data: {e}")
        return None

def format_alert(data):
    price = float(data["priceUsd"])
    tx_count = data["txCount"]["m5"]
    volume = data["volume"]["h1"]
    liquidity = data["liquidity"]["usd"]

    return (
        f"💥 *New $GIZMO Activity Detected!*\n"
        f"🔹 Price: ${price:.6f}\n"
        f"🔸 5-min TX Count: {tx_count}\n"
        f"💧 Liquidity: ${liquidity:,}\n"
        f"📈 Volume (1h): ${volume:,}\n\n"
        f"[📊 Chart](https://dexscreener.com/apechain/0xc3105500cfF134b82e88a7A6809Af00a5Ee186F3)"
    )

def main():
    print("🚀 GIZMO BuyBot is running with DexScreener...")
    last_tx_count = None

    while True:
        data = fetch_dex_data()
        if data:
            current_tx = data["txCount"]["m5"]
            if last_tx_count is not None and current_tx > last_tx_count:
                alert = format_alert(data)
                try:
                    bot.send_message(chat_id=CHAT_ID, text=alert, parse_mode="Markdown", disable_web_page_preview=False)
                    print("✅ Alert sent.")
                except Exception as e:
                    print(f"❌ Telegram error: {e}")
            last_tx_count = current_tx
        else:
            print("⚠️ No data found.")

        time.sleep(15)

if __name__ == "__main__":
    main()
