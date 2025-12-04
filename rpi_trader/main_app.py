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
    """Reads trigger.txt file to get the mode (0 or 1)"""
    try:
        if not os.path.exists(config.TRIGGER_FILE):
            # Create default file if it doesn't exist
            with open(config.TRIGGER_FILE, "w") as f:
                f.write("0")
            return "0"
            
        with open(config.TRIGGER_FILE, "r") as f:
            content = f.read().strip()
            return content
    except Exception as e:
        print(f"Error reading trigger file: {e}")
        return "0"

def main():
    print(f"Starting Forex Bot for {config.SYMBOL} on RPi4...")
    send_telegram_message(f"🤖 Bot started on RPi4. Monitoring {config.SYMBOL}...")

    while True:
        try:
            # PROGRAM STOP LOGIC: Check system time
            now = datetime.datetime.now()
            current_time_str_hm = now.strftime("%H:%M")
            
            # Stop time is 23:30
            if current_time_str_hm == "23:30":
                print("⚠️ System time reached 23:30. Stopping the bot.")
                send_telegram_message("⚠️ Bot received stop signal (23:30). Shutting down.")
                break # Exit the infinite loop

            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Waking up...")
            
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
                if mode == "1":
                    # --- Mode 1: Order Management (Close/Trailing) ---
                    
                    # 1. Close Order by RSI (M30)
                    rsi_signal, rsi_msg = close_order_by_rsi.check_condition(df_m30)
                    if rsi_signal:
                        send_telegram_message(rsi_msg)
                        
                    # 2. Kijun Trailing Stop (H1)
                    kijun_signal, kijun_msg = kijun_sen_trailing_stop.check_condition(df_h1)
                    if kijun_signal:
                        # This module always returns a value to update trailing
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
                    print("Invalid mode in trigger.txt. Use '0' or '1'.")

            else:
                print("Failed to fetch market data.")

            # Sleep for 15 minutes (900 seconds)
            print("Sleeping for 15 minutes...")
            time.sleep(900)

        except KeyboardInterrupt:
            print("Bot stopped by user.")
            break
        except Exception as e:
            print(f"Critical Error in Main Loop: {e}")
            send_telegram_message(f"⚠️ Bot Critical Error: {e}")
            time.sleep(60) # Wait 1 minute and try again if error

if __name__ == "__main__":
    main()