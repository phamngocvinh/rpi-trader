import requests
import pandas as pd
import config

def send_telegram_message(message):
    """
    #3: Sends a message to the Telegram Bot
    """
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error sending telegram: {e}")
        return None

def fetch_market_data():
    """
    #1 & #5: Calls the API to fetch data for all 3 timeframes simultaneously (or sequentially).
    Returns a dictionary containing DataFrames for M15, M30, H1.
    """
    data_store = {}
    
    for interval in config.INTERVALS:
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol": config.SYMBOL,
            "interval": interval,
            "outputsize": config.HISTORY_SIZE,
            "apikey": config.TD_API_KEY,
            "format": "JSON"
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if "values" in data:
                df = pd.DataFrame(data["values"])
                # Convert columns to numeric
                cols = ['open', 'high', 'low', 'close']
                df[cols] = df[cols].apply(pd.to_numeric)
                # Reverse so index 0 is oldest, last index is newest (standard for indicator calculation)
                df = df.iloc[::-1].reset_index(drop=True)
                data_store[interval] = df
            else:
                print(f"Error API response for {interval}: {data}")
                return None
        except Exception as e:
            print(f"Exception fetching data {interval}: {e}")
            return None
            
    return data_store