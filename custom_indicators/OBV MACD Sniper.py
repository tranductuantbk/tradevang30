import pandas as pd
import numpy as np

def run_indicator(df):
    d = df.copy()
    def get_1d(col_name):
        return d[col_name].iloc[:, 0] if isinstance(d[col_name], pd.DataFrame) else d[col_name]

    close = get_1d('Close')
    high = get_1d('High')
    low = get_1d('Low')
    volume = get_1d('Volume')

    window_len, v_len, macd_slow = 28, 14, 26 [cite: 14]
    price_spread = (high - low).rolling(window=window_len).std(ddof=0) [cite: 14, 15]
    
    change = close.diff()
    sign = np.sign(change)
    v = (sign * volume).cumsum() [cite: 14, 15]
    
    smooth = v.rolling(window=v_len).mean() [cite: 14, 15]
    v_spread = (v - smooth).rolling(window=window_len).std(ddof=0) [cite: 14, 15]
    
    shadow = np.where(v_spread != 0, (v - smooth) / v_spread * price_spread, 0) [cite: 14, 15]
    shadow_series = pd.Series(shadow, index=d.index)
    
    out = np.where(shadow_series > 0, high + shadow_series, low + shadow_series) [cite: 15, 16]
    slow_ma = close.ewm(span=macd_slow, adjust=False).mean() [cite: 16]
    macd_val = pd.Series(out, index=d.index) - slow_ma [cite: 16]

    def get_linreg(series, length):
        x = np.arange(length)
        x_mean = x.mean()
        x_diff = x - x_mean
        sum_x_diff_sq = np.sum(x_diff**2)
        result = pd.Series(np.nan, index=series.index)
        y_values = series.values
        for i in range(length - 1, len(y_values)):
            y_slice = y_values[i - length + 1 : i + 1]
            if np.isnan(y_slice).any(): continue
            y_mean = y_slice.mean()
            slope = np.sum(x_diff * (y_slice - y_mean)) / sum_x_diff_sq
            intercept = y_mean - slope * x_mean
            result.iloc[i] = intercept + slope * (length - 1)
        return result

    signal_val = get_linreg(macd_val, 5) [cite: 16]
    sma_50 = signal_val.rolling(window=50).mean() [cite: 17]

    if len(signal_val) < 50 or pd.isna(sma_50.iloc[-1]):
        return "Chỉ báo OBV MACD Pro: Đang tải...", {}

    buy_labels = pd.Series(np.nan, index=d.index)
    sell_labels = pd.Series(np.nan, index=d.index)

    for i in range(2, len(df)):
        sig_0, sig_1, sig_2 = signal_val.iloc[i], signal_val.iloc[i-1], signal_val.iloc[i-2]
        sma50_1 = sma_50.iloc[i-1]
        
        hook_up = (sig_0 > sig_1) and (sig_1 <= sig_2) [cite: 17]
        hook_dn = (sig_0 < sig_1) and (sig_1 >= sig_2) [cite: 17]

        if hook_dn and (sig_1 > sma50_1): sell_labels.iloc[i-1] = sig_1 [cite: 17]
        if hook_up and (sig_1 < sma50_1): buy_labels.iloc[i-1] = sig_1 [cite: 17]

    sig_0, sig_1, sig_2 = float(signal_val.iloc[-1]), float(signal_val.iloc[-2]), float(signal_val.iloc[-3])
    sma50_1 = float(sma_50.iloc[-2])
    
    can_cau = (sig_0 < sig_1) and (sig_1 >= sig_2) and (sig_1 > sma50_1) [cite: 17]
    can_cung = (sig_0 > sig_1) and (sig_1 <= sig_2) and (sig_1 < sma50_1) [cite: 17]

    status = "Tích lũy"
    if can_cau: status = "🔴 CẠN CẦU (SHORT)" [cite: 18, 20]
    elif can_cung: status = "🟢 CẠN CUNG (LONG)" [cite: 17, 20]

    text_for_ai = f"OBV MACD Sniper: {status}"
    plot_data = {"signal_val": signal_val, "buy_labels": buy_labels, "sell_labels": sell_labels}
    
    return text_for_ai, plot_data
