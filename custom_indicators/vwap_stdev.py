import pandas as pd
import numpy as np

def run_indicator(df):
    """
    VWAP Stdev Bands v2 Mod
    Dịch từ Pine Script sang Python Core: Tính toán VWAP theo phiên (Session) và Dải lệch chuẩn.
    """
    d = df.copy()
    
    # Ép dữ liệu về 1 chiều (1D) để tránh lỗi Series
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    high = get_1d('High')
    low = get_1d('Low')
    close = get_1d('Close')
    volume = get_1d('Volume')

    # 1. TÍNH TOÁN CÁC BIẾN CƠ BẢN
    hl2 = (high + low) / 2
    vol_hl2 = volume * hl2
    vol_hl2_sq = volume * (hl2 ** 2)

    # 2. PHÂN TÁCH THEO PHIÊN GIAO DỊCH (DAILY SESSION)
    # Tương đương với lệnh change(time("D")) trong PineScript
    # Chúng ta nhóm dữ liệu theo từng ngày để cộng dồn
    session_dates = d.index.date
    
    c_vol = volume.groupby(session_dates).cumsum()
    cv_hl2 = vol_hl2.groupby(session_dates).cumsum()
    cv_hl2_sq = vol_hl2_sq.groupby(session_dates).cumsum()

    # 3. TÍNH VWAP VÀ ĐỘ LỆCH CHUẨN (STDEV)
    # Tránh lỗi chia cho 0 nếu Volume = 0
    c_vol_safe = c_vol.replace(0, np.nan)
    
    vwap = cv_hl2 / c_vol_safe
    
    # Công thức: sqrt(max(v2sum/volumesum - myvwap*myvwap, 0))
    variance = (cv_hl2_sq / c_vol_safe) - (vwap ** 2)
    variance = variance.clip(lower=0) # Ép các giá trị âm vi phân về 0
    stdev = np.sqrt(variance)

    # 4. HỆ SỐ CÁC DẢI BĂNG (BANDS MULTIPLIERS)
    dev1, dev2, dev3 = 1.28, 2.01, 2.51

    # 5. ĐÓNG GÓI DỮ LIỆU GỬI AI STRATEGIST
    if pd.isna(vwap.iloc[-1]):
        return "Chỉ báo VWAP Stdev: Đang chờ dữ liệu Volume để kích hoạt tính toán."

    curr_price = float(close.iloc[-1])
    curr_vwap = float(vwap.iloc[-1])
    curr_dev = float(stdev.iloc[-1])

    # Các mốc Band
    u1 = curr_vwap + dev1 * curr_dev
    d1 = curr_vwap - dev1 * curr_dev
    u2 = curr_vwap + dev2 * curr_dev
    d2 = curr_vwap - dev2 * curr_dev
    u3 = curr_vwap + dev3 * curr_dev
    d3 = curr_vwap - dev3 * curr_dev

    # Phân tích xu hướng so với trục VWAP
    if curr_price > curr_vwap:
        trend = "TĂNG (Nằm trên trục VWAP - Bò kiểm soát phiên)"
    elif curr_price < curr_vwap:
        trend = "GIẢM (Nằm dưới trục VWAP - Gấu kiểm soát phiên)"
    else:
        trend = "ĐI NGANG (Cắt ngang trục VWAP)"

    # Phân tích Vị thế (Zone)
    zone = "⚪ Cân bằng (Bên trong dải Band 1)"
    if curr_price >= u3:
        zone = "🔴 QUÁ MUA CỰC ĐẠI (Vượt Band 3 - Độ lệch cao, rủi ro đảo chiều lớn)"
    elif curr_price >= u2:
        zone = "🟠 Quá Mua (Vượt Band 2)"
    elif curr_price >= u1:
        zone = "🟡 Tăng mạnh (Vượt Band 1)"
    elif curr_price <= d3:
        zone = "🟢 QUÁ BÁN CỰC ĐẠI (Thủng Band 3 - Độ lệch cao, khả năng nảy lên lớn)"
    elif curr_price <= d2:
        zone = "🔵 Quá Bán (Thủng Band 2)"
    elif curr_price <= d1:
        zone = "🟣 Giảm mạnh (Thủng Band 1)"

    text_for_ai = (
        f"Chỉ báo VWAP Stdev Bands:\n"
        f"  + Trục Trung tâm (VWAP): {curr_vwap:.2f} | Trạng thái: {trend}\n"
        f"  + Vị thế Giá hiện tại: {zone}\n"
        f"  + Các vách Cản Trên (U1/U2/U3): {u1:.2f} | {u2:.2f} | {u3:.2f}\n"
        f"  + Các vách Hỗ Trợ (D1/D2/D3): {d1:.2f} | {d2:.2f} | {d3:.2f}"
    )

    return text_for_ai