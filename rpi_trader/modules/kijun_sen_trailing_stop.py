import pandas as pd
from utils import storage_manager

# Constant key used to store the Kijun value in the state.json file
KIJUN_H1_KEY = "kijun_h1_value"

def check_condition(df_h1, mode):
    """
    Description: Calculates H1 Kijun-sen and reports the value for Trailing Stop.
    - Mode 1 (BUY): Only notifies if Kijun has INCREASED.
    - Mode 2 (SELL): Only notifies if Kijun has DECREASED.
    - Mode 0: This function is not called in mode 0.
    Return: (bool, message) - True if value changed favorably, False otherwise.
    """
    if df_h1 is None:
        return False, "No Data"

    # Kijun-sen (Base Line) formula: (Max High + Min Low) / 2 over 26 periods
    period = 26
    high_26 = df_h1['high'].rolling(window=period).max()
    low_26 = df_h1['low'].rolling(window=period).min()
    
    df_h1['kijun_sen'] = (high_26 + low_26) / 2
    
    current_kijun = df_h1['kijun_sen'].iloc[-1]
    current_price = df_h1['close'].iloc[-1]

    # --- Persistence Logic ---
    
    # Load previous Kijun value (defaults to None if not found)
    last_kijun = storage_manager.load_state(KIJUN_H1_KEY)
    
    # Tolerance to prevent excessive notifications due to minor floating point changes
    MIN_CHANGE_THRESHOLD = 0.01 
    should_notify = False
    
    if last_kijun is None:
        # First run: always save and notify to set the baseline
        should_notify = True
        
    # Mode 1 (BUY): Kijun must INCREASE to move the trailing stop up (protecting profit)
    elif mode == "1":
        if current_kijun > last_kijun and abs(current_kijun - last_kijun) >= MIN_CHANGE_THRESHOLD:
            should_notify = True
            
    # Mode 2 (SELL): Kijun must DECREASE to move the trailing stop down (protecting profit)
    elif mode == "2":
        if current_kijun < last_kijun and abs(current_kijun - last_kijun) >= MIN_CHANGE_THRESHOLD:
            should_notify = True
            
    # If Kijun moves against the trade (decreases for Buy, increases for Sell), 
    # we don't notify, but we still update the saved value if it changes to be accurate for next time.

    # 1. Check if the value has changed significantly (for saving purposes)
    has_changed_significantly = last_kijun is None or abs(last_kijun - current_kijun) >= MIN_CHANGE_THRESHOLD
    
    # 2. Save the new value if it has changed, regardless of notification status, 
    # to maintain the correct "last_kijun" baseline.
    if has_changed_significantly:
        storage_manager.save_state(KIJUN_H1_KEY, current_kijun)
    
    # If we shouldn't notify OR if the value hasn't changed enough to warrant a message
    if not should_notify or not has_changed_significantly:
        return False, None
    
    # --- Message Creation ---
    
    # Add guidance for the user
    if mode == "1":
        trailing_tip = "Notify only if Kijun INCREASES (protecting BUY order)."
        order_type = "BUY ORDER"
    elif mode == "2":
        trailing_tip = "Notify only if Kijun DECREASES (protecting SELL order)."
        order_type = "SELL ORDER"
    else:
        trailing_tip = "Current Kijun value reported."
        order_type = "GENERAL INFORMATION"

    msg = f"🛑 **Kijun-Sen Trailing (H1) UPDATE - {order_type}**:\nNew Kijun Value: `{current_kijun:.2f}`\nCurrent Price: `{current_price:.2f}`\n*Hint: {trailing_tip}*"
    
    # Return True to signal that a notification should be sent
    return True, msg