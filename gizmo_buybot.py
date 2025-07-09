import time
import requests
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

BOT_TOKEN = "8091393191:AAHrLWwaHgAIXBTNLBNDxad9gtKaYcOScLA"
CHAT_ID = "-1002233988866"  # Replace with your actual group chat ID
VIDEO_FILE_ID = "BAACAgEAAxkBAAMEaGyzUGywKUYSQPU0KMpiKwqkbgoAArwGAAKp5QlFpIxB-SExnjI2BA"

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/pairs/apechain/0x2b34F0Dd63Aab54563918a4C82e85f5f39EfA2f7"
CHECK_INTERVAL = 10  # seconds
last_tx_hash = None

def fetch_latest_buy():
    try:
        response = requests.get(DEXSCREENER_API)
        data = response.json()
        txns = data["pair"]["txns"]["m5"]
        return data["pair"], txns
    except Exception as e:
        print("Error fetching buy:", e)
        return None, None

def format_paws(amount_spent):
    paws = "🐾" * int(float(amount_spent) / 5)
    return paws[:25]  # cap at 25 paws

def send_buy_alert(bot, tx_data):
    global last_tx_hash
    if tx_data["txns"] and tx_data["txns"][0]["tx"] == last_tx_hash:
        return  # skip if no new tx
    last_tx_hash = tx_data["txns"][0]["tx"]

    info, _ = tx_data
    price = info["priceUsd"]
    liquidity = info["liquidity"]["usd"]
    market_cap = info["fdv"]

    spent = 10.34  # placeholder or fetch real if available
    amount = 381_588  # placeholder or fetch real if available
    position = "🆕"

    paws = format_paws(spent)

    caption = (
        f"*GIZMO BUY!*\n\n"
        f"{paws}\n\n"
        f"💸 Spent: {spent} $WAPE ($11.79)\n"
        f"💰 Got: {amount:,} $GIZMO\n"
        f"🔄 Buy Position: {position}\n"
        f"✅ Dex: Camelot | 🔗Book Trending - ADS\n"
        f"🏷️ Price: ${float(price):.8f}\n"
        f"🏦 Liquidity: ${float(liquidity):,.2f}\n"
        f"📊 Market Cap: ${float(market_cap):,.2f}\n\n"
        f"[TX](https://apechain.calderaexplorer.xyz/) | "
        f"[Chart](https://dexscreener.com/apechain/0x2b34F0Dd63Aab54563918a4C82e85f5f39EfA2f7) | "
        f"[TG](https://t.me/apegizmo) | "
        f"[X](https://x.com/apegizmo) | "
        f"[Website](https://gizmoape.net)"
    )

    buttons = [[InlineKeyboardButton("YOUR AD HERE", url="https://t.me/ApechainADSBot")]]
    markup = InlineKeyboardMarkup(buttons)

    try:
        bot.send_video(
            chat_id=CHAT_ID,
            video=VIDEO_FILE_ID,
            caption=caption,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        print("✅ Buy alert sent.")
    except TelegramError as e:
        print("Telegram error:", e)

def main():
    bot = Bot(token=BOT_TOKEN)
    print("🚀 GIZMO BuyBot is running...")

    while True:
        tx_data, txns = fetch_latest_buy()
        if tx_data and txns:
            send_buy_alert(bot, {"pair": tx_data, "txns": txns})
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
