import pandas as pd

def calculate_ichimoku_components(df):
    # Tenkan (9)
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    df['tenkan_sen'] = (high_9 + low_9) / 2
    
    # Kijun (26)
    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    df['kijun_sen'] = (high_26 + low_26) / 2
    
    # Senkou Span A (Shifted forward 26 - but for current value analysis we look at current index)
    df['span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    
    # Senkou Span B (52) -> Shifted 26
    high_52 = df['high'].rolling(window=52).max()
    low_52 = df['low'].rolling(window=52).min()
    df['span_b'] = ((high_52 + low_52) / 2).shift(26)
    
    # Chikou: Close price shifted back 26 (Future looking back)
    # To check current Chikou, we compare Close[-1] with High/Low[-27] (Price 26 candles ago)
    return df

def check_condition(data_store):
    """
    Input: data_store contains M15, M30, H1
    Logic: Checks Entry signals for both Buy and Sell.
    """
    
    df_h1 = data_store.get('1h').copy()
    df_m30 = data_store.get('30min').copy()
    df_m15 = data_store.get('15min').copy()

    # Calculate Ichimoku for all timeframes
    df_h1 = calculate_ichimoku_components(df_h1)
    df_m30 = calculate_ichimoku_components(df_m30)
    df_m15 = calculate_ichimoku_components(df_m15)
    
    # Get current values
    current_close_h1 = df_h1['close'].iloc[-1]
    current_span_a_h1 = df_h1['span_a'].iloc[-1]
    current_span_b_h1 = df_h1['span_b'].iloc[-1]

    # --- SIGNAL INITIALIZATION ---
    buy_signal_conditions = []
    sell_signal_conditions = []
    
    # --- 1. BUY SIGNAL ANALYSIS ---
    
    # 1.1 H1: Price above Kumo
    cond_h1_buy = (current_close_h1 > current_span_a_h1) and (current_close_h1 > current_span_b_h1)
    if cond_h1_buy:
        buy_signal_conditions.append("✅ H1: Price is above Kumo Cloud.")

    # 1.2 M30: Chikou above Past Price (For Buy)
    cond_m30_buy = False
    idx_past = -27
    if len(df_m30) >= 27:
        current_chikou_val = df_m30['close'].iloc[-1]
        past_price_high = df_m30['high'].iloc[idx_past] # Compare with Past High (resistance)
        if current_chikou_val >= past_price_high:
            cond_m30_buy = True
            buy_signal_conditions.append("✅ M30: Chikou Span > Past High.")

    # 1.3 M15: Tenkan crossed UP Kijun (Stable Crossover)
    cond_m15_buy = False
    if len(df_m15) >= 2:
        # Current candle value
        tenkan_curr = df_m15['tenkan_sen'].iloc[-1]
        kijun_curr = df_m15['kijun_sen'].iloc[-1]
        # Previous candle value
        tenkan_prev = df_m15['tenkan_sen'].iloc[-2]
        kijun_prev = df_m15['kijun_sen'].iloc[-2]
        
        # Stable Crossover Logic (Cross UP: Buy Signal)
        # Previous candle: Tenkan <= Kijun
        # Current candle: Tenkan > Kijun
        is_buy_crossover = (tenkan_prev <= kijun_prev) and (tenkan_curr > kijun_curr)
        if is_buy_crossover:
            cond_m15_buy = True
            buy_signal_conditions.append("✅ M15: Tenkan crossed UP Kijun.")


    # --- 2. SELL SIGNAL ANALYSIS ---
    
    # 2.1 H1: Price below Kumo
    cond_h1_sell = (current_close_h1 < current_span_a_h1) and (current_close_h1 < current_span_b_h1)
    if cond_h1_sell:
        sell_signal_conditions.append("✅ H1: Price is below Kumo Cloud.")
        
    # 2.2 M30: Chikou below Past Price (For Sell)
    cond_m30_sell = False
    if len(df_m30) >= 27:
        current_chikou_val = df_m30['close'].iloc[-1]
        past_price_low = df_m30['low'].iloc[idx_past] # Compare with Past Low (support)
        if current_chikou_val <= past_price_low:
            cond_m30_sell = True
            sell_signal_conditions.append("✅ M30: Chikou Span < Past Low.")

    # 2.3 M15: Tenkan crossed DOWN Kijun (Stable Crossover)
    cond_m15_sell = False
    if len(df_m15) >= 2:
        # Current candle value
        tenkan_curr = df_m15['tenkan_sen'].iloc[-1]
        kijun_curr = df_m15['kijun_sen'].iloc[-1]
        # Previous candle value
        tenkan_prev = df_m15['tenkan_sen'].iloc[-2]
        kijun_prev = df_m15['kijun_sen'].iloc[-2]
        
        # Stable Crossover Logic (Cross DOWN: Sell Signal)
        # Previous candle: Tenkan >= Kijun
        # Current candle: Tenkan < Kijun
        is_sell_crossover = (tenkan_prev >= kijun_prev) and (tenkan_curr < kijun_curr)
        if is_sell_crossover:
            cond_m15_sell = True
            sell_signal_conditions.append("✅ M15: Tenkan crossed DOWN Kijun.")

    # --- RESULT AGGREGATION ---
    
    is_buy_signal = cond_h1_buy and cond_m30_buy and cond_m15_buy
    is_sell_signal = cond_h1_sell and cond_m30_sell and cond_m15_sell
    
    full_msg = ""
    is_signal = False
    
    if is_buy_signal:
        is_signal = True
        full_msg = "🚀 **BUY ENTRY SIGNAL DETECTED** (Ichimoku)\n" + "\n".join(buy_signal_conditions)
    
    if is_sell_signal:
        is_signal = True
        if full_msg: # Prevent case where both Buy and Sell signals exist (Sideways market)
            full_msg += "\n\n" 
        full_msg += "🔻 **SELL ENTRY SIGNAL DETECTED** (Ichimoku)\n" + "\n".join(sell_signal_conditions)
    
    # Only return message if at least one signal exists
    if not is_buy_signal and not is_sell_signal:
        return False, None

    return is_signal, full_msg