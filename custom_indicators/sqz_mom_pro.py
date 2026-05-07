import pandas as pd
import numpy as np

def run_indicator(df):
    """
    Squeeze Momentum Pro [Trend + PA Filter]
    Bản dịch từ Pine Script sang Python Core (Không dùng thư viện ngoài)
    """
    d = df.copy()
    
    # Ép dữ liệu về 1 chiều (1D) chống lỗi Series
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    close = get_1d('Close')
    high = get_1d('High')
    low = get_1d('Low')
    open_p = get_1d('Open')
    
    # ----------------------------------------------------------------------
    # 1. THÔNG SỐ GỐC
    # ----------------------------------------------------------------------
    length = 20
    mult = 2.0
    lengthKC = 20
    multKC = 1.5
    ema_length = 50
    lookback_extremes = 50

    # ----------------------------------------------------------------------
    # 2. TÍNH TOÁN BOLLINGER BANDS & KELTNER CHANNELS
    # ----------------------------------------------------------------------
    # Bollinger Bands
    basis = close.rolling(length).mean()
    dev = mult * close.rolling(length).std(ddof=0) 
    upperBB = basis + dev
    lowerBB = basis - dev

    # Keltner Channels (True Range)
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    ma = close.rolling(lengthKC).mean()
    rangema = tr.rolling(lengthKC).mean()
    upperKC = ma + rangema * multKC
    lowerKC = ma - rangema * multKC

    # Trạng thái Squeeze (Nén)
    sqzOn = (lowerBB > lowerKC) & (upperBB < upperKC)
    
    # ----------------------------------------------------------------------
    # 3. TÍNH XUNG LƯỢNG (MOMENTUM) & LINEAR REGRESSION
    # ----------------------------------------------------------------------
    highest_high = high.rolling(lengthKC).max()
    lowest_low = low.rolling(lengthKC).min()
    
    avg_hl = (highest_high + lowest_low) / 2
    avg2 = (avg_hl + ma) / 2
    delta = close - avg2

    # Toán học Hồi quy tuyến tính (Linear Regression) siêu tốc
    val = pd.Series(0.0, index=close.index)
    x = np.arange(lengthKC)
    x_mean = x.mean()
    x_diff = x - x_mean
    sum_x_diff_sq = np.sum(x_diff**2)

    for i in range(lengthKC - 1, len(close)):
        y = delta.iloc[i - lengthKC + 1 : i + 1].values
        slope = np.sum(x_diff * (y - y.mean())) / sum_x_diff_sq
        intercept = y.mean() - slope * x_mean
        val.iloc[i] = intercept + slope * (lengthKC - 1)

    # ----------------------------------------------------------------------
    # 4. TÍNH VÙNG CỰC ĐẠI (EXTREMES)
    # ----------------------------------------------------------------------
    val_mean = val.rolling(lookback_extremes).mean()
    val_stdev = val.rolling(lookback_extremes).std(ddof=0)

    upper_band = val_mean + (2.0 * val_stdev)
    lower_band = val_mean - (2.0 * val_stdev)

    is_ob = val > upper_band
    is_os = val < lower_band

    # ----------------------------------------------------------------------
    # 5. LỌC XU HƯỚNG & HÀNH ĐỘNG GIÁ (PRICE ACTION)
    # ----------------------------------------------------------------------
    # La bàn xu hướng (EMA 50)
    main_trend = close.ewm(span=ema_length, adjust=False).mean()
    is_uptrend = close > main_trend
    is_downtrend = close < main_trend

    # Kiểm tra xem 4 nến gần nhất có nến nào OB/OS không
    was_ob = is_ob | is_ob.shift(1) | is_ob.shift(2) | is_ob.shift(3)
    was_os = is_os | is_os.shift(1) | is_os.shift(2) | is_os.shift(3)

    prev_val = val.shift(1)
    prev_low = low.shift(1)
    prev_high = high.shift(1)

    # Logic Mua/Bán (Khắt khe)
    confirm_sell = was_ob & (val < prev_val) & (close < prev_low) & (close < open_p) & is_downtrend
    confirm_buy = was_os & (val > prev_val) & (close > prev_high) & (close > open_p) & is_uptrend

    # ----------------------------------------------------------------------
    # 6. ĐÓNG GÓI NGỮ NGHĨA CHO AI ĐỌC
    # ----------------------------------------------------------------------
    c_val = float(val.iloc[-1])
    c_sqz = bool(sqzOn.iloc[-1])
    c_sell = bool(confirm_sell.iloc[-1])
    c_buy = bool(confirm_buy.iloc[-1])
    
    # Dịch Squeeze
    sqz_status = "ĐANG BỊ NÉN (Đợi bùng nổ)" if c_sqz else "Đang mở rộng"
    
    # Dịch Xu hướng
    trend_status = "TĂNG (Nằm trên EMA50)" if bool(is_uptrend.iloc[-1]) else "GIẢM (Nằm dưới EMA50)"
    
    # Dịch Tín hiệu Lệnh
    signal_status = "KHÔNG CÓ TÍN HIỆU (Chờ đợi)."
    if c_buy:
        signal_status = "🔥 CÓ TÍN HIỆU MUA: Đã quét xong đáy, xung lượng tăng mạnh, nến xanh bao trùm và đang Đánh thuận xu hướng!"
    elif c_sell:
        signal_status = "🔥 CÓ TÍN HIỆU BÁN: Đã quét xong đỉnh, xung lượng suy yếu, nến đỏ phá đáy và đang Đánh thuận xu hướng!"

    text_for_ai = (
        f"Chỉ báo SQZ Momentum Pro (Kèm Lọc Nhiễu):\n"
        f"  + Xu hướng chính (EMA50): {trend_status}.\n"
        f"  + Trạng thái biến động: {sqz_status}.\n"
        f"  + Xung lượng (Momentum Val): {c_val:.2f}.\n"
        f"  + TÍN HIỆU LỆNH: {signal_status}"
    )
    
    return text_for_ai