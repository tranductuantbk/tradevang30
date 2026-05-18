import pandas as pd
import numpy as np

def run_indicator(df):
    d = df.copy()
    def get_1d(col_name):
        return d[col_name].iloc[:, 0] if isinstance(d[col_name], pd.DataFrame) else d[col_name]

    open_p, high, low, close, volume = get_1d('Open'), get_1d('High'), get_1d('Low'), get_1d('Close'), get_1d('Volume')

    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    atr = pd.Series(tr).ewm(alpha=1/10, adjust=False).mean()
    hl2 = (high + low) / 2
    basic_ub, basic_lb = hl2 + 3.0 * atr, hl2 - 3.0 * atr

    final_ub, final_lb, direction = pd.Series(0.0, index=df.index), pd.Series(0.0, index=df.index), pd.Series(1, index=df.index)

    for i in range(1, len(df)):
        final_ub.iloc[i] = basic_ub.iloc[i] if basic_ub.iloc[i] < final_ub.iloc[i-1] or close.iloc[i-1] > final_ub.iloc[i-1] else final_ub.iloc[i-1]
        final_lb.iloc[i] = basic_lb.iloc[i] if basic_lb.iloc[i] > final_lb.iloc[i-1] or close.iloc[i-1] < final_lb.iloc[i-1] else final_lb.iloc[i-1]
        
        if direction.iloc[i-1] == 1 and close.iloc[i] < final_lb.iloc[i]: direction.iloc[i] = -1
        elif direction.iloc[i-1] == -1 and close.iloc[i] > final_ub.iloc[i]: direction.iloc[i] = 1
        else: direction.iloc[i] = direction.iloc[i-1]

    vol_dir = np.where(close > close.shift(1), volume, -volume)
    vzo_vol = pd.Series(vol_dir, index=df.index).ewm(span=14, adjust=False).mean()
    tot_vol = volume.ewm(span=14, adjust=False).mean()
    raw_vzo = np.where(tot_vol != 0, 100 * vzo_vol / tot_vol, 0)
    vzo = pd.Series(raw_vzo, index=df.index).ewm(span=4, adjust=False).mean()

    if len(df) < 50 or pd.isna(vzo.iloc[-1]): return "Đỉnh Đáy VZO: Đang tải...", {}

    ready_buy, ready_sell = False, False
    action_signal = "Trung tính"
    buy_signals, sell_signals = pd.Series(np.nan, index=df.index), pd.Series(np.nan, index=df.index)

    for i in range(2, len(df)):
        macro, macro_prev = direction.iloc[i], direction.iloc[i-1]
        v_curr, v_prev, v_prev2 = vzo.iloc[i], vzo.iloc[i-1], vzo.iloc[i-2]

        if macro != macro_prev: ready_buy, ready_sell = False, False

        if macro == 1 and ((v_prev >= 15 and v_curr < 15) or (macro != macro_prev and v_curr <= 15)): ready_buy = True
        if macro == 1 and ready_buy and (v_curr > v_prev and v_prev <= v_prev2) and (close.iloc[i] >= open_p.iloc[i] or close.iloc[i] > low.iloc[i] + (high.iloc[i]-low.iloc[i])*0.3):
            ready_buy = False 
            buy_signals.iloc[i] = v_curr
            if i >= len(df) - 3: action_signal = "🟢 KIỆT SỨC BÁN (MUA)"

        if macro == -1 and ((v_prev <= -15 and v_curr > -15) or (macro != macro_prev and v_curr >= -15)): ready_sell = True
        if macro == -1 and ready_sell and (v_curr < v_prev and v_prev >= v_prev2) and (close.iloc[i] <= open_p.iloc[i] or close.iloc[i] < high.iloc[i] - (high.iloc[i]-low.iloc[i])*0.3):
            ready_sell = False 
            sell_signals.iloc[i] = v_curr
            if i >= len(df) - 3: action_signal = "🔴 KIỆT SỨC MUA (BÁN)"

    text_for_ai = f"VZO: {vzo.iloc[-1]:.2f} | Tín hiệu: {action_signal}"
    plot_data = {"vzo": vzo, "buy_signals": buy_signals, "sell_signals": sell_signals}
    return text_for_ai, plot_data
