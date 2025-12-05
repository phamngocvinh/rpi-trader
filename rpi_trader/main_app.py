import time
import os
import config
import datetime
from utils.helpers import fetch_market_data, send_telegram_message
from modules import (
    close_order_by_rsi,
    kijun_sen_trailing_stop,
    ichimoku_entry_finder,
    sr_finder
)

def read_trigger_mode():
    """Reads trigger.txt file to get the mode (0, 1, or 2)"""
    try:
        if not os.path.exists(config.TRIGGER_FILE):
            # Create default file if it doesn't exist
            with open(config.TRIGGER_FILE, "w") as f:
                f.write("0")
            return "0"
            
        with open(config.TRIGGER_FILE, "r") as f:
            content = f.read().strip()
            # Ensure only valid modes are returned, default to '0' if corrupted
            if content in ["0", "1", "2"]:
                return content
            else:
                return "0"
                
    except Exception as e:
        print(f"Error reading trigger file: {e}")
        return "0"

def execute_trading_logic():
    """
    Executes the trading logic once. Cron handles the 15-minute scheduling.
    """
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Running trading logic once...")
    
    # #7: Read trigger mode
    mode = read_trigger_mode()
    print(f"Current Trigger Mode: {mode}")

    # #1 & #5: Fetch Data only once
    # Dictionary containing keys: '15min', '30min', '1h'
    market_data = fetch_market_data()
    
    if market_data:
        # Divide data for easier use
        df_m15 = market_data.get('15min')
        df_m30 = market_data.get('30min')
        df_h1  = market_data.get('1h')

        # #7: Process by Mode
        if mode == "1" or mode == "2":
            # --- Mode 1 (BUY) or 2 (SELL): Order Management (Close/Trailing) ---
            
            # 1. Close Order by RSI (M30)
            rsi_signal, rsi_msg = close_order_by_rsi.check_condition(df_m30)
            
            if rsi_signal:
                # Filter RSI message based on current trade mode
                if mode == "1" and "Bearish" in rsi_msg:
                    # Mode 1 (Active BUY) only cares about Bearish divergence (Close BUY)
                    send_telegram_message(rsi_msg)
                elif mode == "2" and "Bullish" in rsi_msg:
                    # Mode 2 (Active SELL) only cares about Bullish divergence (Close SELL)
                    send_telegram_message(rsi_msg)

            # 2. Kijun Trailing Stop (H1) - Pass the current mode
            kijun_signal, kijun_msg = kijun_sen_trailing_stop.check_condition(df_h1, mode)
            if kijun_signal:
                # This module only returns True if Kijun moved favorably for the current mode
                send_telegram_message(kijun_msg)

        elif mode == "0":
            # --- Mode 0: Opportunity Search (Entry) ---
            
            # 1. Ichimoku Entry Finder
            ichi_signal, ichi_msg = ichimoku_entry_finder.check_condition(market_data)
            
            # If there is an Ichimoku signal (or partial), send message
            if ichi_msg: 
                send_telegram_message(ichi_msg)
            
            # Only call S/R finder if Ichimoku is satisfied (Signal = True)
            if ichi_signal:
                sr_signal, sr_msg = sr_finder.check_condition(df_h1)
                if sr_signal:
                    send_telegram_message(sr_msg)
        
        else:
            print("Invalid mode in trigger.txt. Please use '0', '1', or '2'.")

    else:
        print("Failed to fetch market data.")


def main():
    print(f"Starting Forex Bot for {config.SYMBOL}...")
    
    # Send startup message only on the very first run (which will be managed by Cron)
    send_telegram_message(f"🤖 Bot started. Monitoring {config.SYMBOL}...")

    try:
        execute_trading_logic()

    except Exception as e:
        print(f"Critical Error during execution: {e}")
        send_telegram_message(f"⚠️ Bot Critical Error: {e}")

if __name__ == "__main__":
    main()