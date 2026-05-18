import pandas as pd
import numpy as np

def run_indicator(df):
    d = df.copy()
    def get_1d(col_name):
        return d[col_name].iloc[:, 0] if isinstance(d[col_name], pd.DataFrame) else d[col_name]

    close, high, low = get_1d('Close'), get_1d('High'), get_1d('Low')
    
    ema_fast = close.ewm(span=34, adjust=False).mean()
    ema_slow = close.ewm(span=89, adjust=False).mean()
    
    length, mult, lengthKC, multKC = 20, 2.0, 20, 1.5
    basis = close.rolling(length).mean()
    dev = mult * close.rolling(length).std(ddof=0)
    lowerBB, upperBB = basis - dev, basis + dev
    
    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    ma = close.rolling(lengthKC).mean()
    rangema = pd.Series(tr).rolling(lengthKC).mean()
    lowerKC, upperKC = ma - rangema * multKC, ma + rangema * multKC
    
    sqzOn = (lowerBB > lowerKC) & (upperBB < upperKC)

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
    
    if pd.isna(val.iloc[-1]): return "SQZ Pro Sync: Đang tải...", {}

    action_signal = "Trung tính"
    v_0, v_1, v_2 = float(val.iloc[-1]), float(val.iloc[-2]), float(val.iloc[-3])
    
    if (v_0 < v_1) and (v_1 >= v_2) and v_1 > 0: action_signal = "Cảnh báo Đỉnh"
    elif (v_0 > v_1) and (v_1 <= v_2) and v_1 < 0: action_signal = "Cảnh báo Đáy"

    text_for_ai = f"SQZ: {'Nén (Squeeze ON)' if sqzOn.iloc[-1] else 'Xả Nén'} | {action_signal}"
    plot_data = {"val": val, "sqz_on": sqzOn}
    return text_for_ai, plot_data
