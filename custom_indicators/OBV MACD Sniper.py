import pandas as pd
import numpy as np

def linreg_end(vals):
    """Tính toán điểm cuối của đường Hồi quy Tuyến tính (Tương đương ta.linreg trong PineScript)"""
    x = np.arange(len(vals))
    slope, intercept = np.polyfit(x, vals, 1)
    return intercept + slope * (len(vals) - 1)

def run_indicator(df):
    # ==========================================================
    # 1. CÀI ĐẶT THÔNG SỐ & BỘ CHỈNH GIỜ
    # ==========================================================
    # Lùi lại 6 tiếng để khớp đúng giờ Việt Nam
    TIME_SHIFT_HOURS = -6
    
    window_len = 28
    v_len = 14
    macd_slow = 26
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    volume = df['Volume']
    
    # ==========================================================
    # 2. TÍNH TOÁN OBV CHUẨN HÓA VÀ BÓNG NẾN (SHADOW)
    # ==========================================================
    # Sử dụng std(ddof=0) để khớp tuyệt đối với thuật toán TradingView
    price_spread = (high - low).rolling(window=window_len).std(ddof=0)
    
    change = close.diff()
    sign = np.sign(change)
    v = (sign * volume).cumsum()
    
    smooth = v.rolling(window=v_len).mean()
    
    v_spread = (v - smooth).rolling(window=window_len).std(ddof=0)
    
    shadow = np.where(v_spread != 0, (v - smooth) / v_spread * price_spread, 0)
    shadow_series = pd.Series(shadow, index=df.index)
    
    out = np.where(shadow_series > 0, high + shadow_series, low + shadow_series)
    
    obvema = pd.Series(out, index=df.index)
    
    slow_ma = close.ewm(span=macd_slow, adjust=False).mean()
    
    # ==========================================================
    # 3. TÍNH TOÁN MACD & ĐƯỜNG TÍN HIỆU (ZERO-LAG)
    # ==========================================================
    macd_val = obvema - slow_ma
    
    signal_val = macd_val.rolling(window=5).apply(linreg_end, raw=True)
    
    # Thuật toán bắt đỉnh/đáy (Hook) thời gian thực
    signal_val_1 = signal_val.shift(1)
    signal_val_2 = signal_val.shift(2)
    
    hook_up = (signal_val > signal_val_1) & (signal_val_1 <= signal_val_2)
    hook_dn = (signal_val < signal_val_1) & (signal_val_1 >= signal_val_2)
    
    # Bộ lọc SMA 50
    sma50 = signal_val.rolling(window=50).mean()
    
    can_cau = hook_dn & (signal_val_1 > sma50) # Cạn cầu (Bán)
    can_cung = hook_up & (signal_val_1 < sma50) # Cạn cung (Mua)
    
    # ==========================================================
    # 4. GHI NHẬN TÍN HIỆU & OFFSET (LÙI 1 NẾN VÀO ĐÚNG CHÓP)
    # ==========================================================
    buy_signals = pd.Series(np.nan, index=df.index)
    sell_signals = pd.Series(np.nan, index=df.index)
    
    for i in range(2, len(df)):
        if can_cung.iloc[i]:
            buy_signals.iloc[i-1] = signal_val.iloc[i-1]
        if can_cau.iloc[i]:
            sell_signals.iloc[i-1] = signal_val.iloc[i-1]

    # ==========================================================
    # 5. TRẢ DỮ LIỆU VỀ STREAMLIT & HIỂN THỊ THỜI GIAN
    # ==========================================================
    # Đã sửa lại key thành buy_labels và sell_labels để khớp với 1_Chi_bao.py
    plot_data = {
        "signal_val": signal_val,
        "buy_labels": buy_signals,
        "sell_labels": sell_signals
    }
    
    last_signal = "Bình thường"
    
    # Quét ngược lịch sử 10 nến gần nhất để lấy tín hiệu và mốc thời gian
    for i in range(len(df)-1, max(0, len(df)-11), -1):
        if not np.isnan(buy_signals.iloc[i]):
            try:
                timestamp = pd.to_datetime(df.index[i])
                timestamp_vn = timestamp + pd.Timedelta(hours=TIME_SHIFT_HOURS)
                time_str = timestamp_vn.strftime('%H:%M:%S %d/%m/%Y')
            except:
                time_str = str(df.index[i])
                
            last_signal = f"OBV MACD: CẠN CUNG lúc {time_str} (Dòng tiền tạo đáy - MUA)"
            break
            
        elif not np.isnan(sell_signals.iloc[i]):
            try:
                timestamp = pd.to_datetime(df.index[i])
                timestamp_vn = timestamp + pd.Timedelta(hours=TIME_SHIFT_HOURS)
                time_str = timestamp_vn.strftime('%H:%M:%S %d/%m/%Y')
            except:
                time_str = str(df.index[i])
                
            last_signal = f"OBV MACD: CẠN CẦU lúc {time_str} (Dòng tiền tạo đỉnh - BÁN)"
            break
            
    if last_signal == "Bình thường":
        last_signal = f"OBV MACD: Tích lũy (Chưa có tín hiệu đảo chiều Dòng tiền)"
        
    return last_signal, plot_data
