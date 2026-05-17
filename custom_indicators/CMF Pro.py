import pandas as pd
import numpy as np

def run_indicator(df):
    """
    CMF Pro [Chống Nhiễu - Khớp Giá]
    Bản dịch Python cho Quang Quant Hub
    """
    d = df.copy()
    
    # Ép dữ liệu về 1D
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame): return col.iloc[:, 0]
        return col

    open_p = get_1d('Open')
    high = get_1d('High')
    low = get_1d('Low')
    close = get_1d('Close')
    volume = get_1d('Volume')

    # Xử lý ngoại lệ chia cho 0
    hl_range = high - low
    hl_range_safe = hl_range.replace(0, np.nan)

    # ==========================================
    # 1. CHAIKIN MONEY FLOW (CMF)
    # ==========================================
    ad = np.where((close == high) & (close == low) | (hl_range == 0), 0, 
                  ((2 * close - low - high) / hl_range_safe) * volume)
    ad = pd.Series(ad, index=d.index).fillna(0)
    
    mf = ad.rolling(20).sum() / volume.rolling(20).sum()

    # ==========================================
    # 2. BUY/SELL VOLUME PERCENTAGE
    # ==========================================
    bv = np.where(hl_range == 0, 0, volume * (close - low) / hl_range_safe)
    sv = np.where(hl_range == 0, 0, volume * (high - close) / hl_range_safe)
    
    total_v = bv + sv
    bv_pct = np.where(total_v == 0, 0, bv / total_v)
    sv_pct = np.where(total_v == 0, 0, sv / total_v)

    # ==========================================
    # 3. STOCHASTIC OSCILLATOR (Chuẩn hóa)
    # ==========================================
    ll14 = low.rolling(14).min()
    hh14 = high.rolling(14).max()
    fast_k = 100 * (close - ll14) / (hh14 - ll14).replace(0, np.nan)
    
    k = fast_k.rolling(3).mean()
    d_stoch = k.rolling(3).mean()

    # Thang đo -1 đến 1
    adjk = ((k / 100) - 0.5) * 2
    adjd = ((d_stoch / 100) - 0.5) * 2
    h0, h1 = 0.6000, -0.6000

    # ==========================================
    # 4. LOGIC ĐỈNH ĐÁY VÀ BÓP CÒ (CHỐNG NHIỄU)
    # ==========================================
    can_sell = False
    can_buy = False
    signal_status = "Đang tích lũy, chưa có điểm nổ."

    # Chạy vòng lặp để mô phỏng bộ nhớ trạng thái (State Machine) của PineScript
    for i in range(2, len(df)):
        # Lên nòng khi tiến vào vùng Cực đại
        if adjk.iloc[i-1] <= h0 and adjk.iloc[i] > h0:
            can_sell = True
        if adjk.iloc[i-1] >= h1 and adjk.iloc[i] < h1:
            can_buy = True

        # Nhận diện Móc câu (Hook)
        hook_dn = (adjk.iloc[i] < adjk.iloc[i-1]) and (adjk.iloc[i-1] >= adjk.iloc[i-2])
        hook_up = (adjk.iloc[i] > adjk.iloc[i-1]) and (adjk.iloc[i-1] <= adjk.iloc[i-2])

        # Xác nhận giá thực tế (Nến thuận chiều)
        price_confirm_sell = (close.iloc[i] < open_p.iloc[i]) or (close.iloc[i] < close.iloc[i-1])
        price_confirm_buy = (close.iloc[i] > open_p.iloc[i]) or (close.iloc[i] > close.iloc[i-1])

        # Bóp cò (Trigger)
        is_ob_peak = hook_dn and (adjk.iloc[i-1] >= h0) and can_sell and price_confirm_sell
        is_os_trough = hook_up and (adjk.iloc[i-1] <= h1) and can_buy and price_confirm_buy

        if is_ob_peak:
            can_sell = False  # Khóa chốt
            # Chỉ báo tín hiệu nếu nó xảy ra ở nến hiện tại hoặc nến sát vách
            if i >= len(df) - 2: 
                signal_status = "🔴 BÁN MẠNH: Stoch tạo đỉnh + Giá giảm xác nhận (Bẫy Bò hoàn tất)!"
                
        elif is_os_trough:
            can_buy = False   # Khóa chốt
            if i >= len(df) - 2:
                signal_status = "🟢 MUA MẠNH: Stoch tạo đáy + Giá tăng xác nhận (Bẫy Gấu hoàn tất)!"

    # ==========================================
    # 5. GÓI DỮ LIỆU GỬI AI STRATEGIST
    # ==========================================
    curr_cmf = float(mf.iloc[-1])
    curr_buy = float(bv_pct[-1]) * 100
    curr_sell = float(sv_pct[-1]) * 100
    
    if pd.isna(curr_cmf):
        return "Chỉ báo CMF Pro: Đang thu thập thêm dữ liệu."

    cmf_status = "Bơm tiền VÀO (Tích lũy)" if curr_cmf > 0 else "Rút tiền RA (Phân phối)"

    text_for_ai = (
        f"Chỉ báo CMF Pro (Chống Nhiễu - Khớp Giá):\n"
        f"  + Trạng thái Dòng tiền (CMF): {curr_cmf:.4f} -> Cá mập đang {cmf_status}.\n"
        f"  + Áp lực Volume nến: MUA {curr_buy:.1f}% | BÁN {curr_sell:.1f}%\n"
        f"  + Tín hiệu Bóp cò: {signal_status}"
    )

    return text_for_ai