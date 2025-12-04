import pandas as pd

def check_condition(df_h1):
    """
    Description: Finds Support and Resistance (S/R) within the last 100 H1 candles.
    This module is called only when the Ichimoku Entry returns True.
    Return: (bool, message) - Always returns True to report the values
    """
    if df_h1 is None:
        return False, ""
        
    lookback = 100
    subset = df_h1.iloc[-lookback:]
    
    # Find the highest (Resistance) and lowest (Support) level within 100 candles
    resistance = subset['high'].max()
    support = subset['low'].min()
    
    msg = f"📊 **Support & Resistance (H1)**:\nResistance (Resistance): `{resistance:.2f}` (Used for Sell Stop Loss/Buy Take Profit)\nSupport (Support): `{support:.2f}` (Used for Buy Stop Loss/Sell Take Profit)"
    
    return True, msg