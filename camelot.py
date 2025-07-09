import requests
import logging

def get_trade_data(token_address):
    try:
        url = f"https://api.camelot.exchange/api/v2/token/{token_address}?chainId=8453"
        response = requests.get(url)

        if response.status_code != 200:
            logging.warning(f"Non-200 Camelot response: {response.status_code}")
            return None

        data = response.json()

        return {
            "price_usd": data["data"]["priceUsd"],
            "price_native": data["data"]["price"],
            "liquidity_usd": data["data"]["liquidityUsd"],
            "market_cap_usd": data["data"]["fdvUsd"]
        }

    except Exception as e:
        logging.error(f"Error fetching Camelot data: {e}")
        return None
