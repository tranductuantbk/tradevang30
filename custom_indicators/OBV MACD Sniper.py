import pandas as pd
import numpy as np

def run_indicator(df):
    """
    OBV MACD Pro [Zero Lag] - Dành cho Quang Quant Hub
    Dịch từ Pine Script sang Python: Thuật toán bắt Cạn Cung / Cạn Cầu.
    """
    d = df.copy()
    
    # Ép dữ liệu về 1D
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    close = get_1d('Close')
    high = get_1d('High')
    low = get_1d('Low')
    volume = get_1d('Volume')

    # ==========================================
    # 1. CÀI ĐẶT THÔNG SỐ (Chuẩn gốc)
    # ==========================================
    window_len = 28
    v_len = 14
    macd_slow = 26

    # ==========================================
    # 2. TÍNH TOÁN OBV CHUẨN HÓA VÀ BÓNG (SHADOW)
    # ==========================================
    # Độ lệch chuẩn của Spread giá
    price_spread = (high - low).rolling(window=window_len).std(ddof=0)
    
    # Tích lũy OBV (Dòng tiền)
    change = close.diff()
    sign = np.sign(change)
    v = (sign * volume).cumsum()
    
    # Làm mượt và tính độ lệch chuẩn của Dòng tiền
    smooth = v.rolling(window=v_len).mean()
    v_spread = (v - smooth).rolling(window=window_len).std(ddof=0)
    
    # Shadow logic (Khớp giá và Volume)
    shadow = np.where(v_spread != 0, (v - smooth) / v_spread * price_spread, 0)
    shadow_series = pd.Series(shadow, index=d.index)
    
    # Tính Out và OBV EMA
    out = np.where(shadow_series > 0, high + shadow_series, low + shadow_series)
    obvema = pd.Series(out, index=d.index) # EMA(1) chính là giá trị gốc
    
    # Đường chậm MACD
    slow_ma = close.ewm(span=macd_slow, adjust=False).mean()
    
    # Giá trị MACD
    macd_val = obvema - slow_ma

    # ==========================================
    # 3. THUẬT TOÁN HỒI QUY TUYẾN TÍNH (ZERO-LAG SIGNAL)
    # ==========================================
    def get_linreg(series, length):
        x = np.arange(length)
        x_mean = x.mean()
        x_diff = x - x_mean
        sum_x_diff_sq = np.sum(x_diff**2)
        
        result = pd.Series(np.nan, index=series.index)
        y_values = series.values
        
        for i in range(length - 1, len(y_values)):
            y_slice = y_values[i - length + 1 : i + 1]
            if np.isnan(y_slice).any():
                continue
            y_mean = y_slice.mean()
            slope = np.sum(x_diff * (y_slice - y_mean)) / sum_x_diff_sq
            intercept = y_mean - slope * x_mean
            result.iloc[i] = intercept + slope * (length - 1)
        return result

    # Tính Signal Line bằng Linear Regression 5 nến
    signal_val = get_linreg(macd_val, 5)
    
    # Trục SMA 50 để lọc xu hướng nhiễu
    sma_50 = signal_val.rolling(window=50).mean()

    # Kiểm tra đủ dữ liệu chưa
    if len(signal_val) < 50 or pd.isna(sma_50.iloc[-1]):
        return "Chỉ báo OBV MACD Pro: Đang thu thập đủ 50 nến để kích hoạt Radar."

    # Lấy dữ liệu các nến gần nhất
    sig_0 = float(signal_val.iloc[-1])
    sig_1 = float(signal_val.iloc[-2])
    sig_2 = float(signal_val.iloc[-3])
    sma50_1 = float(sma_50.iloc[-2])

    # ==========================================
    # 4. MÓC CÂU (HOOK) & BẮT CẠN CUNG/CẦU
    # ==========================================
    hook_up = (sig_0 > sig_1) and (sig_1 <= sig_2)
    hook_dn = (sig_0 < sig_1) and (sig_1 >= sig_2)

    # Cạn cầu (Giá cố đẩy lên nhưng Volume MACD móc xuống + nằm trên SMA50)
    can_cau = hook_dn and (sig_1 > sma50_1)
    
    # Cạn cung (Giá bị đè xuống nhưng Volume MACD móc lên + nằm dưới SMA50)
    can_cung = hook_up and (sig_1 < sma50_1)

    # ==========================================
    # 5. GÓI DỮ LIỆU GỬI AI STRATEGIST
    # ==========================================
    status = "Đang tích lũy, chưa có điểm uốn."
    if can_cau:
        status = "🔴 CẠN CẦU (BÁN): Phe Mua đã kiệt sức hoàn toàn. MACD tạo Móc câu đi xuống. Bóp cò SHORT ngay!"
    elif can_cung:
        status = "🟢 CẠN CUNG (MUA): Phe Bán đã hết hàng. MACD tạo Móc câu đi lên. Bóp cò LONG ngay!"
    elif hook_up:
        status = "↗️ Chớm móc lên (Động lượng xanh đang nhen nhóm)."
    elif hook_dn:
        status = "↘️ Chớm móc xuống (Động lượng đỏ đang nhen nhóm)."

    text_for_ai = (
        f"Chỉ báo OBV MACD Sniper (Zero-Lag):\n"
        f"  + Giá trị Động lượng Signal: {sig_0:.4f}\n"
        f"  + Tín hiệu Hành động: {status}"
    )

    return text_for_ai