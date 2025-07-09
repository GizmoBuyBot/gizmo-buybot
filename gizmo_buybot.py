import os
import logging
import time
from web3 import Web3
from dotenv import load_dotenv
from telegram import Bot
from sources.camelot import get_trade_data

load_dotenv()

# === CONFIG ===
RPC_URL = "https://rpc.ape.exchange"  # ApeChain RPC
TOKEN_ADDRESS = Web3.to_checksum_address("0xc3105500CFf134b82e88a7A6809Af00a5Ee186F3")  # GIZMO token
PAIR_ADDRESS = Web3.to_checksum_address("0xf3d7A4eFF01837c27963C3Cb5cDf2A1A21485D1F")  # GIZMO/WAPE pair
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# === WEB3 ===
web3 = Web3(Web3.HTTPProvider(RPC_URL))
bot = Bot(token=BOT_TOKEN)

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === TRACKED BUYS ===
seen_txns = set()

# === MAIN LOOP ===
def monitor_gizmo():
    logger.info("🚀 Gizmo BuyBot started...")

    while True:
        try:
            latest_block = web3.eth.block_number
            block = web3.eth.get_block(latest_block, full_transactions=True)

            for tx in block.transactions:
                if tx.to and tx.to.lower() == PAIR_ADDRESS.lower() and tx.hash.hex() not in seen_txns:
                    seen_txns.add(tx.hash.hex())

                    from_addr = tx["from"]
                    value = web3.from_wei(tx["value"], 'ether')
                    trade_data = get_trade_data(TOKEN_ADDRESS)

                    if trade_data:
                        price_usd = trade_data["price_usd"]
                        market_cap = trade_data["market_cap_usd"]
                        liquidity = trade_data["liquidity_usd"]

                        message = (
                            f"🐾 *$GIZMO Buy Alert!*\n\n"
                            f"🔹 *From:* `{from_addr}`\n"
                            f"💰 *Value:* {value:.4f} WAPE\n"
                            f"📈 *Price:* ${price_usd:.6f}\n"
                            f"💎 *MCap:* ${market_cap:,.0f}\n"
                            f"🌊 *Liquidity:* ${liquidity:,.0f}\n\n"
                            f"[Chart](https://dexscreener.com/ethereum/{PAIR_ADDRESS}) | "
                            f"[TX](https://explorer.ape.exchange/tx/{tx.hash.hex()})"
                        )

                        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown", disable_web_page_preview=True)

            time.sleep(3)

        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_gizmo()
