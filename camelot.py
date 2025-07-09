import requests
import logging

def get_trade_data(token_address):
    try:
        # ApeChain chainId = 8453, Camelot V3 endpoint
        url = f"https://api.camelot.exchange/api/v2/token/{token_address}?chainId=8453"
        response = requests.get(url)

        if response.status_code != 200:
            logging.warning(f"Non-200 Camelot response: {response.status_code}")
            return None

        data = response.json().get("data", {})

        return {
            "price_usd": data.get("priceUsd"),
            "price_native": data.get("price"),
            "liquidity_usd": data.get("liquidityUsd"),
            "market_cap_usd": data.get("fdvUsd")
        }

    except Exception as e:
        logging.error(f"Error fetching Camelot data: {e}")
        return None
