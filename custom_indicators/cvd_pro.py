import pandas as pd
import numpy as np

def run_indicator(df):
    """
    Cumulative Volume Delta (CVD) - Theo dõi Dòng tiền Cá mập
    Đã tích hợp thuật toán phát hiện Bán ngầm (Distribution) và Mua ngầm (Accumulation)
    """
    d = df.copy()
    
    # Ép dữ liệu về 1 chiều (1D) chống lỗi Series
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    close = get_1d('Close')
    open_p = get_1d('Open')
    volume = get_1d('Volume')

    # ======================================================================
    # 1. TÍNH TOÁN DELTA (CHÊNH LỆCH MUA/BÁN CHỦ ĐỘNG TỪNG NẾN)
    # Mô phỏng lại logic Up/Dn Volume của Pine Script
    # ======================================================================
    delta = pd.Series(0.0, index=d.index)

    # Nến tăng -> Volume Mua ; Nến giảm -> Volume Bán
    mask_up = close > open_p
    mask_dn = close < open_p
    
    # Xử lý các nến Doji (Open == Close)
    mask_eq_up = (close == open_p) & (close > close.shift(1))
    mask_eq_dn = (close == open_p) & (close < close.shift(1))

    delta[mask_up] = volume[mask_up]
    delta[mask_dn] = -volume[mask_dn]
    delta[mask_eq_up] = volume[mask_eq_up]
    delta[mask_eq_dn] = -volume[mask_eq_dn]
    
    # Trường hợp ngoại lệ chưa quét được, mặc định cho dòng tiền Mua (giống Pine Script)
    delta[(delta == 0)] = volume[(delta == 0)] 

    # ======================================================================
    # 2. TÍNH TOÁN CVD (CUMULATIVE VOLUME DELTA)
    # ======================================================================
    cvd = delta.cumsum()

    # ======================================================================
    # 3. QUÉT "BÁN NGẦM" VÀ "MUA NGẦM" (DIVERGENCE LOGIC)
    # ======================================================================
    # A. Phân kỳ Vĩ mô (Đo 10 nến gần nhất)
    recent_close = close.tail(10)
    recent_cvd = cvd.tail(10)

    price_trend = recent_close.iloc[-1] - recent_close.iloc[0]
    cvd_trend = recent_cvd.iloc[-1] - recent_cvd.iloc[0]

    macro_status = "Đang bơm tiền (Dòng tiền dương)" if cvd_trend > 0 else "Đang rút tiền (Dòng tiền âm)"

    if price_trend > 0 and cvd_trend < 0:
        macro_status = "❌ PHÂN KỲ ÂM (BÁN NGẦM): Giá kéo tăng tạo fomo, nhưng Cá mập đang xả hàng (CVD cắm đầu)."
    elif price_trend < 0 and cvd_trend > 0:
        macro_status = "✅ PHÂN KỲ DƯƠNG (MUA NGẦM): Giá bị đè đỏ để rũ bỏ, nhưng Cá mập đang gom ngầm (CVD tăng)."

    # B. Phân kỳ Vi mô (Bắt vị nến hiện tại)
    current_delta = delta.iloc[-1]
    c_open = open_p.iloc[-1]
    c_close = close.iloc[-1]

    candle_polarity = 1 if c_close > c_open else (-1 if c_close < c_open else 0)
    delta_polarity = 1 if current_delta > 0 else (-1 if current_delta < 0 else 0)

    warning = "Đồng thuận (Giá và Dòng tiền đi cùng hướng)."
    if candle_polarity == 1 and delta_polarity == -1:
        warning = "⚠️ CẢNH BÁO BÁN NGẦM MÀU XANH: Nến đóng màu xanh nhưng thực chất lệnh Bán chủ động đang áp đảo!"
    elif candle_polarity == -1 and delta_polarity == 1:
        warning = "⚠️ CẢNH BÁO MUA NGẦM MÀU ĐỎ: Nến đóng màu đỏ nhưng thực chất lệnh Mua chủ động đang gom sạch hàng!"

    # ======================================================================
    # 4. ĐÓNG GÓI GỬI AI
    # ======================================================================
    text_for_ai = (
        f"Chỉ báo CVD (Cumulative Volume Delta):\n"
        f"  + Trạng thái Dòng tiền (10 nến): {macro_status}\n"
        f"  + Hành vi nến hiện tại: {warning}\n"
        f"  + Áp lực lệnh (Bar Delta): {'Phe BÁN' if current_delta < 0 else 'Phe MUA'} đang kiểm soát."
    )

    return text_for_ai