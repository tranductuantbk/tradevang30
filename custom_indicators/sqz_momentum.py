import pandas as pd
import numpy as np

def run_indicator(df):
    """
    Squeeze Momentum Indicator [LazyBear]
    Bản viết lại: Tối ưu hóa thuật toán Hồi quy tuyến tính, chống sập do lỗi NaN.
    """
    d = df.copy()
    
    # Ép dữ liệu về 1 chiều (1D) để tránh lỗi Series
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    close = get_1d('Close')
    high = get_1d('High')
    low = get_1d('Low')
    
    # 1. CẤU HÌNH THÔNG SỐ 
    length = 20
    mult = 2.0
    lengthKC = 20
    multKC = 1.5

    # 2. TÍNH TOÁN BOLLINGER BANDS
    basis = close.rolling(window=length).mean()
    dev = mult * close.rolling(window=length).std(ddof=0)
    upperBB = basis + dev
    lowerBB = basis - dev

    # 3. TÍNH TOÁN KELTNER CHANNELS
    ma = close.rolling(window=lengthKC).mean()
    tr = pd.concat([
        high - low, 
        (high - close.shift(1)).abs(), 
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    
    rangema = tr.rolling(window=lengthKC).mean()
    upperKC = ma + rangema * multKC
    lowerKC = ma - rangema * multKC

    # 4. TRẠNG THÁI SQUEEZE (NÉN)
    sqzOn  = (lowerBB > lowerKC) & (upperBB < upperKC)

    # 5. TÍNH TOÁN XUNG LƯỢNG (VAL)
    highest_high = high.rolling(window=lengthKC).max()
    lowest_low = low.rolling(window=lengthKC).min()
    
    avg_high_low = (highest_high + lowest_low) / 2
    sma_close = close.rolling(window=lengthKC).mean()
    
    source_val = close - (avg_high_low + sma_close) / 2
    
    # --- THUẬT TOÁN HỒI QUY TUYẾN TÍNH (LINEAR REGRESSION) TỐI ƯU ---
    val = pd.Series(np.nan, index=close.index)
    x = np.arange(lengthKC)
    x_mean = x.mean()
    x_diff = x - x_mean
    sum_x_diff_sq = np.sum(x_diff**2)

    y_values = source_val.values
    for i in range(lengthKC - 1, len(y_values)):
        y_slice = y_values[i - lengthKC + 1 : i + 1]
        
        # Bỏ qua nếu dữ liệu đầu vào bị rỗng (NaN) để tránh crash hệ thống
        if np.isnan(y_slice).any():
            continue
        
        y_mean = y_slice.mean()
        slope = np.sum(x_diff * (y_slice - y_mean)) / sum_x_diff_sq
        intercept = y_mean - slope * x_mean
        
        # Tính giá trị tại nến hiện tại (x = lengthKC - 1)
        val.iloc[i] = intercept + slope * (lengthKC - 1)

    # 6. ĐÓNG GÓI DỮ LIỆU GỬI AI STRATEGIST
    valid_val = val.dropna()
    if len(valid_val) < 2:
        return "Chỉ báo Squeeze Momentum: Không đủ dữ liệu nến để tính toán xung lượng."
        
    current_val = float(valid_val.iloc[-1])
    prev_val = float(valid_val.iloc[-2])
    is_sqz = bool(sqzOn.iloc[-1])
    
    if current_val > 0:
        mom_status = "TĂNG (Bullish)"
        intensity = "Mạnh" if current_val > prev_val else "Yếu dần"
    else:
        mom_status = "GIẢM (Bearish)"
        intensity = "Mạnh" if current_val < prev_val else "Yếu dần"
        
    sqz_text = "ĐANG NÉN (Squeeze On) - Chờ bùng nổ" if is_sqz else "Đang mở rộng (Squeeze Off)"

    text_for_ai = (
        f"Chỉ báo Squeeze Momentum (LazyBear):\n"
        f"  + Xung lượng: {mom_status} và đang {intensity}.\n"
        f"  + Trạng thái: {sqz_text}.\n"
        f"  + Giá trị Val: {current_val:.4f}"
    )
    
    return text_for_ai