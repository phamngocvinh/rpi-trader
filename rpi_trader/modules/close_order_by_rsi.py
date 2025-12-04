import pandas as pd

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    # Avoid division by zero if loss is 0 (or very small)
    rs.replace([float('inf'), -float('inf')], 0, inplace=True)
    return 100 - (100 / (1 + rs))

def check_condition(df_m30):
    """
    Description: Calculates M30 RSI. Checks for divergence (Both Bullish and Bearish) to signal closing orders.
    Return: (bool, message)
    """
    if df_m30 is None or len(df_m30) < 15:
        return False, "Not enough data"

    # Calculate RSI
    df_m30['rsi'] = calculate_rsi(df_m30['close'])
    
    # Get latest data
    curr_price = df_m30['close'].iloc[-1]
    curr_rsi = df_m30['rsi'].iloc[-1]
    
    window = 10
    is_signal = False
    msg = ""

    # --- 1. Bearish Divergence - Signal to Close BUY Orders ---
    # Price makes a higher high, but RSI makes a lower high
    recent_high_price = df_m30['high'].iloc[-window:-1].max()
    idx_recent_high = df_m30['high'].iloc[-window:-1].idxmax()
    rsi_at_recent_high = df_m30['rsi'].iloc[idx_recent_high]

    if curr_price > recent_high_price and curr_rsi < rsi_at_recent_high:
        is_signal = True
        msg = f"⚠️ **ALERT**: Bearish RSI Divergence (M30) detected!\nPrice High: {curr_price}, RSI Lower: {curr_rsi:.2f}.\n**Consider Closing BUY Order.**"
        
    # --- 2. Bullish Divergence - Signal to Close SELL Orders ---
    # Price makes a lower low, but RSI makes a higher low
    recent_low_price = df_m30['low'].iloc[-window:-1].min()
    idx_recent_low = df_m30['low'].iloc[-window:-1].idxmin()
    rsi_at_recent_low = df_m30['rsi'].iloc[idx_recent_low]

    if curr_price < recent_low_price and curr_rsi > rsi_at_recent_low and not is_signal:
        is_signal = True
        msg = f"⚠️ **ALERT**: Bullish RSI Divergence (M30) detected!\nPrice Low: {curr_price}, RSI Higher: {curr_rsi:.2f}.\n**Consider Closing SELL Order.**"
        
    return is_signal, msg