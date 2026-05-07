import pandas as pd
import numpy as np

def run_indicator(df):
    d = df.copy()
    def g1(n): return d[n].iloc[:, 0] if isinstance(d[n], pd.DataFrame) else d[n]
    c, h, l, o = g1('Close'), g1('High'), g1('Low'), g1('Open')
    
    # Bollinger & Keltner
    ma = c.rolling(20).mean()
    std = c.rolling(20).std(ddof=0)
    upBB, loBB = ma + 2*std, ma - 2*std
    tr = pd.concat([h-l, (h-c.shift(1)).abs(), (l-c.shift(1)).abs()], axis=1).max(axis=1)
    rma = tr.rolling(20).mean()
    upKC, loKC = ma + 1.5*rma, ma - 1.5*rma
    
    sqz = (loBB > loKC) & (upBB < upKC)
    
    # Momentum
    val = c - ((h.rolling(20).max() + l.rolling(20).min())/2 + ma)/2
    # Xu hướng EMA50
    ema50 = c.ewm(span=50, adjust=False).mean()
    trend = "TĂNG" if c.iloc[-1] > ema50.iloc[-1] else "GIẢM"
    
    sig = "CHỜ ĐỢI"
    if c.iloc[-1] > ema50.iloc[-1] and val.iloc[-1] > val.iloc[-2]: sig = "CANH BUY"
    if c.iloc[-1] < ema50.iloc[-1] and val.iloc[-1] < val.iloc[-2]: sig = "CANH SELL"
    
    return f"SQZ Mom: Xu hướng {trend}. Trạng thái: {'NÉN' if sqz.iloc[-1] else 'MỞ'}. Lệnh: {sig}"
