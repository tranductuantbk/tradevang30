import pandas as pd
import numpy as np

def run_indicator(df):
    """
    WaveTrend Indicator [LazyBear]
    Dịch từ Pine Script sang Python Core cho Quant Trading Hub
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

    # 1. CẤU HÌNH THÔNG SỐ (Chuẩn LazyBear)
    n1 = 10
    n2 = 21
    obLevel1 = 60  # Quá mua 1
    obLevel2 = 53  # Quá mua 2
    osLevel1 = -60 # Quá bán 1
    osLevel2 = -53 # Quá bán 2

    # 2. TÍNH TOÁN WAVETREND
    ap = (high + low + close) / 3
    esa = ap.ewm(span=n1, adjust=False).mean()
    
    # Hàm abs() tính giá trị tuyệt đối
    d_val = (ap - esa).abs().ewm(span=n1, adjust=False).mean()

    # Tính Commodity Channel Index (CI)
    # Thêm thủ thuật replace(0, np.nan) để tránh lỗi chia cho 0 làm sập web
    ci = (ap - esa) / (0.015 * d_val.replace(0, np.nan))
    ci = ci.fillna(0)

    # Làm mượt lần cuối để ra WT1
    tci = ci.ewm(span=n2, adjust=False).mean()

    wt1 = tci
    wt2 = wt1.rolling(window=4).mean() # Đường tín hiệu

    # 3. ĐÓNG GÓI DỮ LIỆU GỬI AI STRATEGIST
    # Xóa NaN ở những nến đầu tiên
    valid_data = pd.concat([wt1, wt2], axis=1).dropna()
    if len(valid_data) < 2:
        return "Chỉ báo WaveTrend: Chưa đủ dữ liệu để tính toán."

    curr_wt1 = float(wt1.iloc[-1])
    curr_wt2 = float(wt2.iloc[-1])
    prev_wt1 = float(wt1.iloc[-2])
    prev_wt2 = float(wt2.iloc[-2])

    # A. Phân tích Vùng Quá Mua / Quá Bán
    zone = "Vùng Trung tính"
    if curr_wt1 >= obLevel1:
        zone = "🔴 QUÁ MUA CỰC ĐẠI (Canh Bán)"
    elif curr_wt1 >= obLevel2:
        zone = "🟠 Vùng Quá Mua"
    elif curr_wt1 <= osLevel1:
        zone = "🟢 QUÁ BÁN CỰC ĐẠI (Canh Mua)"
    elif curr_wt1 <= osLevel2:
        zone = "🟡 Vùng Quá Bán"

    # B. Phân tích Tín hiệu Giao Cắt (Cross)
    cross_signal = "Chưa có điểm giao cắt rõ ràng."
    
    # Cắt lên (Bullish Cross)
    if prev_wt1 <= prev_wt2 and curr_wt1 > curr_wt2:
        if curr_wt1 <= osLevel2:
            cross_signal = "🚀 CẮT LÊN TẠI VÙNG QUÁ BÁN: Tín hiệu LONG/MUA mạnh!"
        else:
            cross_signal = "↗️ Cắt Lên: Phe Mua chớm lấy lại đà."
            
    # Cắt xuống (Bearish Cross)
    elif prev_wt1 >= prev_wt2 and curr_wt1 < curr_wt2:
        if curr_wt1 >= obLevel2:
            cross_signal = "💥 CẮT XUỐNG TẠI VÙNG QUÁ MUA: Tín hiệu SHORT/BÁN mạnh!"
        else:
            cross_signal = "↘️ Cắt Xuống: Phe Bán chớm lấy lại đà."

    text_for_ai = (
        f"Chỉ báo WaveTrend (LazyBear):\n"
        f"  + Giá trị WT Nhanh: {curr_wt1:.2f} | Chậm: {curr_wt2:.2f}\n"
        f"  + Vị thế: {zone}\n"
        f"  + Tín hiệu Hành động: {cross_signal}"
    )

    return text_for_ai