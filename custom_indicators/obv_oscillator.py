import pandas as pd
import numpy as np

def run_indicator(df):
    """
    On Balance Volume Oscillator [LazyBear]
    Dịch từ Pine Script sang Python Core
    """
    d = df.copy()
    
    # Ép dữ liệu về 1 chiều (1D) để tránh lỗi Series
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    close = get_1d('Close')
    volume = get_1d('Volume')
    
    # 1. THÔNG SỐ
    length = 20

    # 2. TÍNH TOÁN OBV GỐC
    # Logic: Nếu giá đóng cửa tăng so với nến trước -> +Volume; Giảm -> -Volume; Bằng -> 0
    change = close.diff()
    obv_values = pd.Series(0.0, index=d.index)
    
    # Tính Delta cho từng nến
    delta = pd.Series(0.0, index=d.index)
    delta[change > 0] = volume
    delta[change < 0] = -volume
    
    # Cộng dồn tích lũy (Cumulative sum)
    obv_cum = delta.cumsum()
    
    # 3. TÍNH OBV OSCILLATOR
    # obv_osc = (os - ema(os, length))
    obv_ema = obv_cum.ewm(span=length, adjust=False).mean()
    d['OBV_Osc'] = obv_cum - obv_ema
    
    # 4. ĐÓNG GÓI DỮ LIỆU GỬI AI
    current_osc = float(d['OBV_Osc'].iloc[-1])
    prev_osc = float(d['OBV_Osc'].iloc[-2])
    
    # Xác định trạng thái dòng tiền
    if current_osc > 0:
        if current_osc > prev_osc:
            status = "DÒNG TIỀN TĂNG MẠNH (Bullish Momentum)"
        else:
            status = "Dòng tiền dương nhưng đang suy yếu"
    else:
        if current_osc < prev_osc:
            status = "DÒNG TIỀN GIẢM MẠNH (Bearish Momentum)"
        else:
            status = "Dòng tiền âm nhưng đang hồi phục"
            
    # Phát hiện dấu hiệu Đảo chiều sớm
    reversal_hint = ""
    if prev_osc < 0 and current_osc > 0:
        reversal_hint = " -> ⚡ CẮT LÊN KHÔNG: Tín hiệu Mua sớm!"
    elif prev_osc > 0 and current_osc < 0:
        reversal_hint = " -> ⚡ CẮT XUỐNG KHÔNG: Tín hiệu Bán sớm!"

    text_for_ai = (
        f"Chỉ báo OBV Oscillator (LazyBear):\n"
        f"  + Giá trị Oscillator: {current_osc:,.0f}\n"
        f"  + Trạng thái: {status}{reversal_hint}"
    )
    
    return text_for_ai