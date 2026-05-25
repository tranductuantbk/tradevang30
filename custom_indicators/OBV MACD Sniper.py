import pandas as pd
import numpy as np

# Thuật toán Hồi quy tuyến tính (Linear Regression) chuyển từ Pine Script sang Numpy
def rolling_linreg(s, window):
    res = np.full(len(s), np.nan)
    x = np.arange(window)
    x_mean = (window - 1) / 2.0
    var_x = np.sum((x - x_mean)**2)
    
    s_values = s.values
    for i in range(window-1, len(s)):
        y = s_values[i-window+1:i+1]
        if not np.isnan(y).any():
            y_mean = np.mean(y)
            cov = np.sum((x - x_mean) * (y - y_mean))
            slope = cov / var_x
            intercept = y_mean - slope * x_mean
            # Tìm giá trị dự phóng tại điểm hiện tại
            res[i] = slope * (window - 1) + intercept
    return pd.Series(res, index=s.index)

def run_indicator(df):
    # 1. Cài đặt thông số
    window_len = 28
    v_len = 14
    macd_slow = 26
    
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']
    
    # 2. Tính toán OBV Chuẩn hóa
    price_spread = (high - low).rolling(window=window_len).std()
    
    # math.sign(ta.change(src1)) * volume
    sign_change = close.diff().apply(np.sign).fillna(0)
    v = (sign_change * volume).cumsum()
    
    smooth = v.rolling(window=v_len).mean()
    v_spread = (v - smooth).rolling(window=window_len).std()
    
    # Tránh lỗi chia cho 0 (divide by zero)
    v_spread_safe = np.where(v_spread.isna() | (v_spread == 0), 1, v_spread)
    shadow = np.where(
        v_spread.isna() | (v_spread == 0), 
        0, 
        (v - smooth) / v_spread_safe * price_spread
    )
    
    out = np.where(shadow > 0, high + shadow, low + shadow)
    out_series = pd.Series(out, index=df.index)
    
    obvema = out_series # EMA chu kỳ 1 chính là giá trị gốc
    slow_ma = close.ewm(span=macd_slow, adjust=False).mean()
    
    macd_val = obvema - slow_ma
    
    # Tạo đường tín hiệu mượt (Linear Regression Length = 5)
    signal_val = rolling_linreg(macd_val, 5)
    
    # 3. Thuật toán Zero-Lag Hook (Móc câu thời gian thực)
    hook_up = (signal_val > signal_val.shift(1)) & (signal_val.shift(1) <= signal_val.shift(2))
    hook_dn = (signal_val < signal_val.shift(1)) & (signal_val.shift(1) >= signal_val.shift(2))
    
    sma50 = signal_val.rolling(50).mean()
    
    # Logic xác nhận vùng cạn kiệt
    can_cau = hook_dn & (signal_val.shift(1) > sma50)
    can_cung = hook_up & (signal_val.shift(1) < sma50)
    
    # 4. Lưu nhãn Đỉnh / Đáy (Offset = -1)
    buy_labels = pd.Series(np.nan, index=df.index)
    sell_labels = pd.Series(np.nan, index=df.index)
    
    for i in range(2, len(df)):
        if can_cung.iloc[i]:
            # Đẩy nhãn lùi lại 1 nến để cắm đúng vào chóp đáy
            buy_labels.iloc[i-1] = signal_val.iloc[i-1]
        if can_cau.iloc[i]:
            # Đẩy nhãn lùi lại 1 nến để cắm đúng vào chóp đỉnh
            sell_labels.iloc[i-1] = signal_val.iloc[i-1]
            
    # Gói dữ liệu để đẩy lên biểu đồ Plotly
    plot_data = {
        "signal_val": signal_val,
        "buy_labels": buy_labels,
        "sell_labels": sell_labels
    }
    
    # 5. Phân tích tín hiệu hiện tại cho Bảng điều khiển (App.py)
    last_signal = "Bình thường"
    # Quét 5 nến gần nhất xem có tín hiệu nào không
    for i in range(len(df)-1, max(0, len(df)-6), -1):
        if can_cung.iloc[i]:
            last_signal = "OBV MACD: CẠN MUA (Dòng tiền tạo đáy)"
            break
        elif can_cau.iloc[i]:
            last_signal = "OBV MACD: CẠN BÁN (Dòng tiền tạo đỉnh)"
            break
            
    if last_signal == "Bình thường":
        last_signal = "OBV MACD: Trạng thái Trung tính"
        
    return last_signal, plot_data
