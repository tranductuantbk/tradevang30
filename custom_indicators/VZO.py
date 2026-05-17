import pandas as pd
import numpy as np

def run_indicator(df):
    """
    Đỉnh Đáy VZO [Supertrend Sync]
    Bản dịch Python cho Quang Quant Hub (Đã tùy chỉnh tên theo yêu cầu)
    """
    d = df.copy()
    
    def get_1d(col_name):
        col = d[col_name]
        return col.iloc[:, 0] if isinstance(col, pd.DataFrame) else col

    open_p = get_1d('Open')
    high = get_1d('High')
    low = get_1d('Low')
    close = get_1d('Close')
    volume = get_1d('Volume')

    # ==========================================
    # 1. BỘ LỌC XU HƯỚNG SUPERTREND (ATR=10, Factor=3.0)
    # ==========================================
    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    # Hàm RMA (Mặc định của TradingView cho ATR)
    atr = pd.Series(tr).ewm(alpha=1/10, adjust=False).mean()
    
    hl2 = (high + low) / 2
    basic_ub = hl2 + 3.0 * atr
    basic_lb = hl2 - 3.0 * atr

    # Tính toán dải Supertrend
    final_ub = pd.Series(0.0, index=df.index)
    final_lb = pd.Series(0.0, index=df.index)
    direction = pd.Series(1, index=df.index) # 1 = Tăng, -1 = Giảm

    for i in range(1, len(df)):
        # Upper band logic
        if basic_ub.iloc[i] < final_ub.iloc[i-1] or close.iloc[i-1] > final_ub.iloc[i-1]:
            final_ub.iloc[i] = basic_ub.iloc[i]
        else:
            final_ub.iloc[i] = final_ub.iloc[i-1]
            
        # Lower band logic
        if basic_lb.iloc[i] > final_lb.iloc[i-1] or close.iloc[i-1] < final_lb.iloc[i-1]:
            final_lb.iloc[i] = basic_lb.iloc[i]
        else:
            final_lb.iloc[i] = final_lb.iloc[i-1]
            
        # Direction flip
        if direction.iloc[i-1] == 1 and close.iloc[i] < final_lb.iloc[i]:
            direction.iloc[i] = -1
        elif direction.iloc[i-1] == -1 and close.iloc[i] > final_ub.iloc[i]:
            direction.iloc[i] = 1
        else:
            direction.iloc[i] = direction.iloc[i-1]

    # ==========================================
    # 2. CHỈ BÁO DÒNG TIỀN (VZO)
    # ==========================================
    vol_dir = np.where(close > close.shift(1), volume, -volume)
    vzo_vol = pd.Series(vol_dir).ewm(span=14, adjust=False).mean()
    tot_vol = volume.ewm(span=14, adjust=False).mean()
    
    raw_vzo = np.where(tot_vol != 0, 100 * vzo_vol / tot_vol, 0)
    vzo = pd.Series(raw_vzo).ewm(span=4, adjust=False).mean()

    # ==========================================
    # 3. THUẬT TOÁN ĐỈNH ĐÁY VÀ KIỆT SỨC CHỐNG SPAM
    # ==========================================
    if len(df) < 50 or pd.isna(vzo.iloc[-1]):
        return "Chỉ báo Đỉnh Đáy VZO: Đang nạp dữ liệu Volume."

    ready_buy = False
    ready_sell = False
    action_signal = "Đang rình mồi. Dòng tiền VZO nằm trong biên độ an toàn."

    # Lặp qua các nến gần đây để tái tạo bộ nhớ trạng thái "Lên Nòng" (Arming)
    for i in range(1, len(df)):
        macro = direction.iloc[i]
        macro_prev = direction.iloc[i-1]
        v_curr = vzo.iloc[i]
        v_prev = vzo.iloc[i-1]
        v_prev2 = vzo.iloc[i-2]

        if macro != macro_prev:
            ready_buy, ready_sell = False, False

        # --- LOGIC KIỆT SỨC BÁN (TÌM ĐIỂM MUA) ---
        cross_dn_limit = (v_prev >= 15) and (v_curr < 15)
        if macro == 1 and (cross_dn_limit or (macro != macro_prev and v_curr <= 15)):
            ready_buy = True

        if macro == 1 and ready_buy:
            hook_up = (v_curr > v_prev) and (v_prev <= v_prev2)
            price_ok = (close.iloc[i] >= open_p.iloc[i]) or (close.iloc[i] > low.iloc[i] + (high.iloc[i]-low.iloc[i])*0.3)
            if hook_up and price_ok:
                ready_buy = False # Khóa chốt
                if i >= len(df) - 3:
                    action_signal = "🟢 KIỆT SỨC BÁN (MUA): Phe Gấu hết lực, Supertrend Tăng bảo kê. Bóp cò LONG!"

        # --- LOGIC KIỆT SỨC MUA (TÌM ĐIỂM BÁN) ---
        cross_up_limit = (v_prev <= -15) and (v_curr > -15)
        if macro == -1 and (cross_up_limit or (macro != macro_prev and v_curr >= -15)):
            ready_sell = True

        if macro == -1 and ready_sell:
            hook_dn = (v_curr < v_prev) and (v_prev >= v_prev2)
            price_ok = (close.iloc[i] <= open_p.iloc[i]) or (close.iloc[i] < high.iloc[i] - (high.iloc[i]-low.iloc[i])*0.3)
            if hook_dn and price_ok:
                ready_sell = False # Khóa chốt
                if i >= len(df) - 3:
                    action_signal = "🔴 KIỆT SỨC MUA (BÁN): Phe Bò kiệt sức, Supertrend Giảm bảo kê. Bóp cò SHORT!"

    # ==========================================
    # 4. GÓI DỮ LIỆU GỬI AI STRATEGIST
    # ==========================================
    curr_vzo = float(vzo.iloc[-1])
    curr_trend = "TĂNG" if direction.iloc[-1] == 1 else "GIẢM"
    
    # Phân loại Vùng VZO
    zone = "Vùng Đi Ngang (Chop Zone)"
    if curr_vzo >= 60: zone = "Quá Mua Cực Đại (Rủi ro Đảo chiều Bán)"
    elif curr_vzo >= 40: zone = "Quá Mua"
    elif curr_vzo <= -60: zone = "Quá Bán Cực Đại (Rủi ro Đảo chiều Mua)"
    elif curr_vzo <= -40: zone = "Quá Bán"

    text_for_ai = (
        f"Chỉ báo Đỉnh Đáy VZO:\n"
        f"  + Xu hướng Supertrend: {curr_trend}\n"
        f"  + Mức VZO hiện tại: {curr_vzo:.2f} -> Nằm trong {zone}.\n"
        f"  + Cảnh báo Hành động: {action_signal}"
    )

    return text_for_ai