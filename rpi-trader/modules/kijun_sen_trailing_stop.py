import pandas as pd

def check_condition(df_h1):
    """
    Description: Calculates H1 Kijun-sen and reports the value for Trailing Stop.
    This value is used to protect Buy orders (below price) or Sell orders (above price).
    Return: (bool, message) - Always returns True to report the value
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
    
    # Add guidance for the user
    if current_kijun < current_price:
        trailing_tip = "Used as Trailing Stop for BUY ORDER (Value is below current price)."
    elif current_kijun > current_price:
        trailing_tip = "Used as Trailing Stop for SELL ORDER (Value is above current price)."
    else:
        trailing_tip = "Kijun is close to price (Sideways market)."


    msg = f"🛑 **Kijun-Sen Trailing (H1)**:\nCurrent Price: `{current_price:.2f}`\nKijun Value: `{current_kijun:.2f}`\n*Tips: {trailing_tip}*"
    
    # This module's task is to report the value every time it is called
    return True, msg