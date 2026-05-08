import pandas as pd
import numpy as np

def run_indicator(df):
    """
    Support and Resistance (High Volume Boxes) [ChartPrime]
    Dịch từ Pine Script sang Python: Lọc đỉnh đáy bằng Volume Delta và ATR.
    """
    d = df.copy()
    
    # Ép dữ liệu về 1 chiều (1D) để tránh lỗi Series
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    close = get_1d('Close')
    open_p = get_1d('Open')
    high = get_1d('High')
    low = get_1d('Low')
    volume = get_1d('Volume')

    # 1. THÔNG SỐ CÀI ĐẶT
    lookbackPeriod = 20
    vol_len = 2
    box_withd = 1.0

    # 2. TÍNH TOÁN DELTA VOLUME
    delta_vol = pd.Series(0.0, index=d.index)
    buy_mask = close > open_p
    sell_mask = close < open_p
    
    delta_vol[buy_mask] = volume[buy_mask]
    delta_vol[sell_mask] = -volume[sell_mask]
    
    # Lọc nhiễu Volume (Lấy đỉnh/đáy của Volume/2.5)
    vol_hi = (delta_vol / 2.5).rolling(window=vol_len).max()
    vol_lo = (delta_vol / 2.5).rolling(window=vol_len).min()

    # 3. TÌM PIVOT (ĐỈNH/ĐÁY 20 NẾN)
    # Xác định nến là đỉnh/đáy trong chu kỳ 41 nến (20 trái, 1 giữa, 20 phải)
    is_ph = close == close.rolling(window=2*lookbackPeriod+1, center=True).max()
    is_pl = close == close.rolling(window=2*lookbackPeriod+1, center=True).min()

    # Dịch chuyển (Shift) để lấy thời điểm xác nhận Pivot (sau 20 nến)
    ph_confirmed = is_ph.shift(lookbackPeriod).fillna(False)
    pl_confirmed = is_pl.shift(lookbackPeriod).fillna(False)

    # 4. LỌC ĐỈNH ĐÁY THEO DÒNG TIỀN (SMART MONEY LOGIC)
    sup_cond = pl_confirmed & (delta_vol > vol_hi)
    res_cond = ph_confirmed & (delta_vol < vol_lo)

    pivot_prices = close.shift(lookbackPeriod)
    
    # Lưu lại các mức giá thỏa mãn
    sup_levels = pivot_prices.where(sup_cond, np.nan)
    res_levels = pivot_prices.where(res_cond, np.nan)

    # Kéo dài vùng cản đến hiện tại (Forward Fill)
    active_sup = sup_levels.ffill()
    active_res = res_levels.ffill()

    # 5. TÍNH ĐỘ DÀY CỦA HỘP (BOX WIDTH) BẰNG ATR 200
    tr = pd.concat([
        high - low, 
        (high - close.shift(1)).abs(), 
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    
    atr = tr.rolling(window=200).mean()
    width = atr * box_withd

    # 6. ĐÓNG GÓI DỮ LIỆU GỬI AI STRATEGIST
    c_price = float(close.iloc[-1])
    c_sup = active_sup.iloc[-1]
    c_res = active_res.iloc[-1]
    c_width = width.iloc[-1]
    
    if pd.isna(c_sup) or pd.isna(c_res) or pd.isna(c_width):
        return "Chỉ báo Vùng Cản Volume (ChartPrime): Đang thu thập thêm dữ liệu nến để vẽ Hộp."

    # Tọa độ các Hộp (Box)
    res_bot = float(c_res)
    res_top = float(c_res + c_width)
    
    sup_top = float(c_sup)
    sup_bot = float(c_sup - c_width)

    # Đo lường trạng thái Phá vỡ (Breakout) hay Giữ vững (Hold)
    status = "Đang lơ lửng ở giữa (Biên độ an toàn)."
    if res_bot <= c_price <= res_top:
        status = "⚠️ ĐANG TEST KHÁNG CỰ: Giá nằm sát vách Vùng Cung (Bán) mạnh."
    elif c_price > res_top:
        status = "🚀 ĐÃ PHÁ KHÁNG CỰ (Breakout): Vùng Kháng cự đã chuyển thành Hỗ trợ."
    elif sup_bot <= c_price <= sup_top:
        status = "⚠️ ĐANG TEST HỖ TRỢ: Giá nằm sát vách Vùng Cầu (Mua) mạnh."
    elif c_price < sup_bot:
        status = "💥 ĐÃ THỦNG HỖ TRỢ (Breakdown): Vùng Hỗ trợ đã chuyển thành Kháng cự."

    text_for_ai = (
        f"Chỉ báo Vùng Cản Volume (ChartPrime):\n"
        f"  + Hộp Kháng cự (Cản Trên): {res_bot:.2f} đến {res_top:.2f}\n"
        f"  + Hộp Hỗ trợ (Cản Dưới): {sup_bot:.2f} đến {sup_top:.2f}\n"
        f"  + Hành vi Giá hiện tại: {status}"
    )

    return text_for_ai