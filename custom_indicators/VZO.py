import pandas as pd
import numpy as np

def rma(series, length):
    """Giả lập hàm RMA (Wilder's Smoothing) của TradingView"""
    return series.ewm(alpha=1/length, adjust=False).mean()

def run_indicator(df):
    # ==========================================================
    # 1. CÀI ĐẶT THÔNG SỐ VÀ TÍNH TOÁN SUPERTREND
    # ==========================================================
    VZO_length = 14
    pullback_limit = 15
    atr_period = 10
    st_factor = 3.0
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    open_p = df['Open']
    volume = df['Volume']
    
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = rma(tr, atr_period)
    hl2 = (high + low) / 2
    
    basic_ub = hl2 + (st_factor * atr)
    basic_lb = hl2 - (st_factor * atr)
    
    final_ub = pd.Series(0.0, index=df.index)
    final_lb = pd.Series(0.0, index=df.index)
    supertrend = pd.Series(0.0, index=df.index)
    macro_trend = pd.Series(1, index=df.index) 
    
    for i in range(1, len(df)):
        if basic_ub.iloc[i] < final_ub.iloc[i-1] or close.iloc[i-1] > final_ub.iloc[i-1]:
            final_ub.iloc[i] = basic_ub.iloc[i]
        else:
            final_ub.iloc[i] = final_ub.iloc[i-1]
            
        if basic_lb.iloc[i] > final_lb.iloc[i-1] or close.iloc[i-1] < final_lb.iloc[i-1]:
            final_lb.iloc[i] = basic_lb.iloc[i]
        else:
            final_lb.iloc[i] = final_lb.iloc[i-1]
            
        prev_st = supertrend.iloc[i-1]
        prev_trend = macro_trend.iloc[i-1]
        curr_close = close.iloc[i]
        
        if prev_st == final_ub.iloc[i-1] and curr_close <= final_ub.iloc[i]:
            macro_trend.iloc[i] = -1
        elif prev_st == final_ub.iloc[i-1] and curr_close > final_ub.iloc[i]:
            macro_trend.iloc[i] = 1
        elif prev_st == final_lb.iloc[i-1] and curr_close >= final_lb.iloc[i]:
            macro_trend.iloc[i] = 1
        elif prev_st == final_lb.iloc[i-1] and curr_close < final_lb.iloc[i]:
            macro_trend.iloc[i] = -1
        else:
            macro_trend.iloc[i] = prev_trend
            
        supertrend.iloc[i] = final_lb.iloc[i] if macro_trend.iloc[i] == 1 else final_ub.iloc[i]

    # ==========================================================
    # 2. TÍNH TOÁN DÒNG TIỀN VZO (ĐÃ FIX LỖI INDEX)
    # ==========================================================
    vol_dir = np.where(close > close.shift(1), volume, -volume)
    
    vzo_vol = pd.Series(vol_dir, index=df.index).ewm(span=VZO_length, adjust=False).mean()
    tot_vol = volume.ewm(span=VZO_length, adjust=False).mean()
    
    raw_vzo = np.where(tot_vol.values != 0, 100 * vzo_vol.values / tot_vol.values, 0)
    vzo = pd.Series(raw_vzo, index=df.index).ewm(span=4, adjust=False).mean()

    # ==========================================================
    # 3. THUẬT TOÁN ĐỈNH/ĐÁY VÀ KIỆT SỨC CHỐNG SPAM
    # ==========================================================
    vzo_hook_up = (vzo > vzo.shift(1)) & (vzo.shift(1) <= vzo.shift(2))
    vzo_hook_dn = (vzo < vzo.shift(1)) & (vzo.shift(1) >= vzo.shift(2))
    
    buy_signals = pd.Series(np.nan, index=df.index)
    sell_signals = pd.Series(np.nan, index=df.index)
    
    is_ready_buy = False
    is_ready_sell = False
    
    for i in range(2, len(df)):
        if macro_trend.iloc[i] != macro_trend.iloc[i-1]:
            is_ready_buy = False
            is_ready_sell = False
            
        # LOGIC MUA
        cross_dn_limit = (vzo.iloc[i-1] >= pullback_limit) and (vzo.iloc[i] < pullback_limit)
        if macro_trend.iloc[i] == 1 and (cross_dn_limit or (macro_trend.iloc[i] != macro_trend.iloc[i-1] and vzo.iloc[i] <= pullback_limit)):
            is_ready_buy = True
            
        is_green = close.iloc[i] >= open_p.iloc[i] 
        if macro_trend.iloc[i] == 1 and is_ready_buy and vzo_hook_up.iloc[i] and is_green:
            buy_signals.iloc[i-1] = vzo.iloc[i-1] 
            is_ready_buy = False 
            
        # LOGIC BÁN
        cross_up_limit = (vzo.iloc[i-1] <= -pullback_limit) and (vzo.iloc[i] > -pullback_limit)
        if macro_trend.iloc[i] == -1 and (cross_up_limit or (macro_trend.iloc[i] != macro_trend.iloc[i-1] and vzo.iloc[i] >= -pullback_limit)):
            is_ready_sell = True
            
        is_red = close.iloc[i] <= open_p.iloc[i] 
        if macro_trend.iloc[i] == -1 and is_ready_sell and vzo_hook_dn.iloc[i] and is_red:
            sell_signals.iloc[i-1] = vzo.iloc[i-1] 
            is_ready_sell = False 

    # ==========================================================
    # 4. TRẢ DỮ LIỆU VỀ STREAMLIT (GIỜ GỐC CHUẨN XÁC)
    # ==========================================================
    plot_data = {
        "vzo": vzo,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals
    }
    
    last_signal = "Bình thường"
    
    for i in range(len(df)-1, max(0, len(df)-11), -1):
        if not np.isnan(buy_signals.iloc[i]):
            try:
                timestamp = pd.to_datetime(df.index[i])
                time_str = timestamp.strftime('%H:%M:%S %d/%m/%Y')
            except:
                time_str = str(df.index[i])
                
            last_signal = f"Đỉnh Đáy VZO - KIỆT SỨC BÁN lúc {time_str} (Chuẩn bị Tăng)"
            break
            
        elif not np.isnan(sell_signals.iloc[i]):
            try:
                timestamp = pd.to_datetime(df.index[i])
                time_str = timestamp.strftime('%H:%M:%S %d/%m/%Y')
            except:
                time_str = str(df.index[i])
                
            last_signal = f"Đỉnh Đáy VZO - KIỆT SỨC MUA lúc {time_str} (Chuẩn bị Giảm)"
            break
            
    if last_signal == "Bình thường":
        last_signal = f"Đỉnh Đáy VZO - Đang chạy trong Trend {'TĂNG' if macro_trend.iloc[-1] == 1 else 'GIẢM'}"
        
    return last_signal, plot_data
