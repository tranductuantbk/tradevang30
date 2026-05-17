import pandas as pd
import numpy as np

def run_indicator(df):
    """
    SQZ PRO SYNC [Macro Trend Core]
    Bản nâng cấp tối thượng cho Quang Quant Hub
    """
    d = df.copy()
    
    def get_1d(col_name):
        col = d[col_name]
        return col.iloc[:, 0] if isinstance(col, pd.DataFrame) else col

    close = get_1d('Close')
    high = get_1d('High')
    low = get_1d('Low')
    
    # ==========================================
    # 1. BỘ NÃO XU HƯỚNG: ĐỌC TREND (EMA + ADX)
    # ==========================================
    ema_fast = close.ewm(span=34, adjust=False).mean()
    ema_slow = close.ewm(span=89, adjust=False).mean()
    
    # Tính ADX (Wilder's Smoothing)
    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    up = high - high.shift(1)
    down = low.shift(1) - low
    plus_dm = np.where((up > down) & (up > 0), up, 0)
    minus_dm = np.where((down > up) & (down > 0), down, 0)
    
    atr14 = pd.Series(tr).ewm(alpha=1/14, adjust=False).mean()
    plus_di = 100 * (pd.Series(plus_dm).ewm(alpha=1/14, adjust=False).mean() / atr14)
    minus_di = 100 * (pd.Series(minus_dm).ewm(alpha=1/14, adjust=False).mean() / atr14)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.ewm(alpha=1/14, adjust=False).mean()

    # Nhận diện trạng thái Trend
    is_sideways = adx.iloc[-1] < 20
    macro_trend = 1 if ema_fast.iloc[-1] > ema_slow.iloc[-1] else -1

    # ==========================================
    # 2. SQUEEZE & MOMENTUM LINREG 
    # ==========================================
    length, mult, lengthKC, multKC = 20, 2.0, 20, 1.5
    
    basis = close.rolling(length).mean()
    dev = mult * close.rolling(length).std(ddof=0)
    lowerBB, upperBB = basis - dev, basis + dev
    
    ma = close.rolling(lengthKC).mean()
    rangema = pd.Series(tr).rolling(lengthKC).mean()
    lowerKC, upperKC = ma - rangema * multKC, ma + rangema * multKC
    
    sqzOn = (lowerBB > lowerKC) & (upperBB < upperKC)

    # Động lượng neo theo Vĩ mô (EMA 34/89)
    macro_baseline = (ema_fast + ema_slow) / 2
    source_val = close - macro_baseline
    
    def linreg(series, n):
        x = np.arange(n)
        x_mean = x.mean()
        x_diff = x - x_mean
        sum_x_diff_sq = np.sum(x_diff**2)
        res = pd.Series(np.nan, index=series.index)
        y_vals = series.values
        for i in range(n - 1, len(y_vals)):
            y_slice = y_vals[i - n + 1 : i + 1]
            if np.isnan(y_slice).any(): continue
            y_mean = y_slice.mean()
            slope = np.sum(x_diff * (y_slice - y_mean)) / sum_x_diff_sq
            intercept = y_mean - slope * x_mean
            res.iloc[i] = intercept + slope * (n - 1)
        return res

    val = linreg(source_val, lengthKC)
    
    # Bỏ qua nếu thiếu dữ liệu
    if pd.isna(val.iloc[-1]) or pd.isna(adx.iloc[-1]):
        return "Chỉ báo Squeeze Pro Sync: Đang thu thập dữ liệu (cần ít nhất 89 nến)."

    # ==========================================
    # 3. QUÉT PHÂN KỲ (DIVERGENCE) & MÓC CÂU
    # ==========================================
    v_0, v_1, v_2 = float(val.iloc[-1]), float(val.iloc[-2]), float(val.iloc[-3])
    
    hook_dn = (v_0 < v_1) and (v_1 >= v_2)
    hook_up = (v_0 > v_1) and (v_1 <= v_2)
    
    action_signal = "Không có phân kỳ. Tiếp tục bám xu hướng."
    
    # Quét Phân kỳ Giảm (Bearish Divergence)
    if hook_dn and v_1 > 0:
        curr_p = high.iloc[-4:-1].max() # Sync window
        curr_v = v_1
        
        # Quét lùi về 80 nến để tìm đỉnh cũ
        for i in range(5, 80):
            idx = -2 - i
            if idx < -len(val): break
            # Nhận diện đỉnh cũ (Pivot High)
            if val.iloc[idx] > val.iloc[idx-1] and val.iloc[idx] > val.iloc[idx+1]:
                prev_v = val.iloc[idx]
                if prev_v > 0:
                    prev_p = high.iloc[idx-2:idx+3].max()
                    # Điều kiện Phân kỳ: Giá cao hơn nhưng Động lượng thấp hơn
                    if curr_p > prev_p and curr_v < prev_v:
                        if is_sideways or macro_trend == -1:
                            action_signal = "🔴 [BÁN / SHORT]: Bẫy Giá hoàn tất! Phân kỳ Giảm thuận Trend."
                        break

    # Quét Phân kỳ Tăng (Bullish Divergence)
    elif hook_up and v_1 < 0:
        curr_p = low.iloc[-4:-1].min()
        curr_v = v_1
        
        for i in range(5, 80):
            idx = -2 - i
            if idx < -len(val): break
            # Nhận diện đáy cũ (Pivot Low)
            if val.iloc[idx] < val.iloc[idx-1] and val.iloc[idx] < val.iloc[idx+1]:
                prev_v = val.iloc[idx]
                if prev_v < 0:
                    prev_p = low.iloc[idx-2:idx+3].min()
                    # Điều kiện Phân kỳ: Giá thấp hơn nhưng Động lượng cao hơn
                    if curr_p < prev_p and curr_v > prev_v:
                        if is_sideways or macro_trend == 1:
                            action_signal = "🟢 [MUA / LONG]: Rũ bỏ hoàn tất! Phân kỳ Tăng thuận Trend."
                        break

    # ==========================================
    # 4. GÓI DỮ LIỆU GỬI AI STRATEGIST
    # ==========================================
    sqz_status = "Đang bị nén chặt (Squeeze ON)" if sqzOn.iloc[-1] else "Đang xả nén (Squeeze OFF)"
    trend_status = "ĐI NGANG (Cho phép đánh 2 chiều)" if is_sideways else ("TĂNG (Ưu tiên Buy)" if macro_trend == 1 else "GIẢM (Ưu tiên Sell)")

    text_for_ai = (
        f"Chỉ báo Squeeze Pro Sync (Macro Trend):\n"
        f"  + Xu hướng Vĩ mô (EMA+ADX): {trend_status} | Trạng thái Nén: {sqz_status}\n"
        f"  + Tín hiệu Săn mồi: {action_signal}"
    )

    return text_for_ai