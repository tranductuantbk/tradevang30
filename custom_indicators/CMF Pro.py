import pandas as pd
import numpy as np

def run_indicator(df):
    d = df.copy()
    def get_1d(col_name):
        return d[col_name].iloc[:, 0] if isinstance(d[col_name], pd.DataFrame) else d[col_name]

    open_p, high, low, close, volume = get_1d('Open'), get_1d('High'), get_1d('Low'), get_1d('Close'), get_1d('Volume')

    hl_range = high - low
    hl_range_safe = hl_range.replace(0, np.nan)

    ad = np.where((close == high) & (close == low) | (hl_range == 0), 0, ((2 * close - low - high) / hl_range_safe) * volume)
    mf = pd.Series(ad, index=d.index).rolling(20).sum() / volume.rolling(20).sum()

    bv = np.where(hl_range == 0, 0, volume * (close - low) / hl_range_safe)
    sv = np.where(hl_range == 0, 0, volume * (high - close) / hl_range_safe)
    total_v = bv + sv
    bv_pct = np.where(total_v == 0, 0, bv / total_v)

    ll14, hh14 = low.rolling(14).min(), high.rolling(14).max()
    fast_k = 100 * (close - ll14) / (hh14 - ll14).replace(0, np.nan)
    k = fast_k.rolling(3).mean()
    adjk = ((k / 100) - 0.5) * 2
    h0, h1 = 0.6000, -0.6000

    can_sell, can_buy = False, False
    buy_triggers = pd.Series(np.nan, index=d.index)
    sell_triggers = pd.Series(np.nan, index=d.index)
    signal_status = "Trung tính"

    for i in range(2, len(df)):
        if adjk.iloc[i-1] <= h0 and adjk.iloc[i] > h0: can_sell = True
        if adjk.iloc[i-1] >= h1 and adjk.iloc[i] < h1: can_buy = True

        hook_dn = (adjk.iloc[i] < adjk.iloc[i-1]) and (adjk.iloc[i-1] >= adjk.iloc[i-2])
        hook_up = (adjk.iloc[i] > adjk.iloc[i-1]) and (adjk.iloc[i-1] <= adjk.iloc[i-2])

        p_sell = (close.iloc[i] < open_p.iloc[i]) or (close.iloc[i] < close.iloc[i-1])
        p_buy = (close.iloc[i] > open_p.iloc[i]) or (close.iloc[i] > close.iloc[i-1])

        if hook_dn and (adjk.iloc[i-1] >= h0) and can_sell and p_sell:
            can_sell = False
            sell_triggers.iloc[i-1] = adjk.iloc[i-1]
            if i == len(df)-1: signal_status = "🔴 BÁN MẠNH"

        if hook_up and (adjk.iloc[i-1] <= h1) and can_buy and p_buy:
            can_buy = False
            buy_triggers.iloc[i-1] = adjk.iloc[i-1]
            if i == len(df)-1: signal_status = "🟢 MUA MẠNH"

    if pd.isna(mf.iloc[-1]):
        return "CMF Pro: Đang tải...", {}

    text_for_ai = f"CMF Pro: {signal_status} | Lực mua: {bv_pct[-1]*100:.1f}%"
    plot_data = {"mf": mf, "buy_triggers": buy_triggers, "sell_triggers": sell_triggers}
    return text_for_ai, plot_data
