import pandas as pd
import numpy as np

def run_indicator(df):
    vzo_len, vzo_smooth, p_left, p_right, max_b = 14, 4, 5, 5, 60
    d = df.copy()
    def g1(n): return d[n].iloc[:, 0] if isinstance(d[n], pd.DataFrame) else d[n]
    c, v, h, l = g1('Close'), g1('Volume'), g1('High'), g1('Low')
    
    # Tính VZO
    diff = v.copy()
    diff[c <= c.shift(1)] = -v
    vzo_v = diff.ewm(span=vzo_len, adjust=False).mean()
    tot_v = v.ewm(span=vzo_len, adjust=False).mean()
    raw = pd.Series(0.0, index=d.index)
    raw[tot_v != 0] = 100 * (vzo_v[tot_v != 0] / tot_v[tot_v != 0])
    d['VZO'] = raw.ewm(span=vzo_smooth, adjust=False).mean()
    
    # Tìm Pivot
    w = p_left + p_right + 1
    d['IsH'] = (d['VZO'] == d['VZO'].rolling(w, center=True).max())
    d['IsL'] = (d['VZO'] == d['VZO'].rolling(w, center=True).min())
    idxH, idxL = np.where(d['IsH'])[0], np.where(d['IsL'])[0]
    
    # Phân kỳ
    status = "Không có phân kỳ."
    if len(idxL) >= 2:
        i1, i2 = idxL[-1], idxL[-2]
        if i1 - i2 <= max_b and i1 - i2 >= 5:
            v1, v2, p1, p2 = float(d['VZO'].iloc[i1]), float(d['VZO'].iloc[i2]), float(l.iloc[i1]), float(l.iloc[i2])
            if p1 < p2 and v1 > v2: status = "Phân kỳ Tăng (Bullish)"
            elif p1 > p2 and v1 < v2: status = "Phân kỳ Ẩn Tăng (Hidden Bullish)"
            
    v_now = float(d['VZO'].iloc[-1])
    zone = "Quá mua" if v_now > 40 else "Quá bán" if v_now < -40 else "Trung tính"
    return f"VZO Pro: Mức {v_now:.2f} ({zone}). {status}"
