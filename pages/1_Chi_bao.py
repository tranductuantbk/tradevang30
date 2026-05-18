import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import os
import importlib.util
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Module Chỉ Báo", layout="wide", initial_sidebar_state="collapsed")

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🔒 Vui lòng quay lại trang chủ để đăng nhập trước khi sử dụng công cụ này.")
    if st.button("Đi tới trang chủ"): st.switch_page("app.py")
    st.stop()

st_autorefresh(interval=60000, key="live_refresh")

tf_mapping = {
    "M15": {"yf_interval": "15m", "yf_period": "1mo", "td_interval": "15min"},
    "M30": {"yf_interval": "30m", "yf_period": "1mo", "td_interval": "30min"},
    "H1":  {"yf_interval": "60m", "yf_period": "1mo", "td_interval": "1h"},
    "D1":  {"yf_interval": "1d",  "yf_period": "2y",  "td_interval": "1day"}
}

st.title("⚡ Quang Quant Hub - TradingView Pro Sync")

API_KEY = "cf03fc875ee64027a947ccab5ceced4b" 

col_t, col_m, col_f = st.columns([2, 1, 1])
with col_m: selected_ticker = st.text_input("📈 Mã Giao dịch:", value="XAU/USD")
with col_f: selected_tf = st.selectbox("⏳ Khung thời gian:", list(tf_mapping.keys()), index=1)

@st.cache_data(ttl=60)
def load_data(ticker, tf_label, api_key):
    try:
        if ticker.upper() == "XAU/USD":
            if not api_key or api_key == "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY":
                return pd.DataFrame(), "Vui lòng điền API Key."
            td_interval = tf_mapping[tf_label]["td_interval"]
            url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval={td_interval}&outputsize=1000&apikey={api_key}"
            response = requests.get(url).json()
            if "values" not in response: return pd.DataFrame(), f"Lỗi API: {response.get('message', 'Lỗi kết nối.')}"
            df = pd.DataFrame(response['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime').sort_index(ascending=True)
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns: df[col] = df[col].astype(float)
            
            # --- XỬ LÝ KHỐI LƯỢNG ẢO CHO FOREX ---
            df['volume'] = df['volume'].astype(float) if 'volume' in df.columns else 0.0
            if df['volume'].sum() == 0:
                # Giả lập Tick Volume bằng biên độ nến
                df['volume'] = (df['high'] - df['low']) * 100000
            # ---------------------------------------
                
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            return df, "OK"
        else:
            interval = tf_mapping[tf_label]["yf_interval"]
            period = tf_mapping[tf_label]["yf_period"]
            data = yf.Ticker(ticker).history(period=period, interval=interval)
            if data.empty: return pd.DataFrame(), "Lỗi dữ liệu."
            if data.index.tz is not None: data.index = data.index.tz_localize(None)
            
            # --- XỬ LÝ KHỐI LƯỢNG ẢO CHO YAHOO FINANCE ---
            if 'Volume' in data.columns and data['Volume'].sum() == 0:
                data['Volume'] = (data['High'] - data['Low']) * 100000
                
            return data, "OK"
    except Exception as e: return pd.DataFrame(), str(e)

df, error_msg = load_data(selected_ticker, selected_tf, API_KEY)

def get_key(plot_dict, substring):
    for k in plot_dict.keys():
        if substring in k.lower(): return k
    return None

if not df.empty:
    df['time_str'] = df.index.strftime('%Y-%m-%d %H:%M')
    
    col_left, col_right = st.columns([1, 3])
    active_summaries = []
    all_plots = {}
    
    with col_left:
        st.subheader("🛠️ Bộ Chỉ Báo")
        folder = "custom_indicators"
        if not os.path.exists(folder): os.makedirs(folder)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.py') and f != '__init__.py'])
        
        for f in files:
            if st.checkbox(f"Kích hoạt: {f}", value=True):
                try:
                    spec = importlib.util.spec_from_file_location(f.replace('.py',''), os.path.join(folder, f))
                    m = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(m)
                    out = m.run_indicator(df)
                    if isinstance(out, tuple) and len(out) == 2:
                        res, plot_data = out
                        if plot_data: all_plots[f] = plot_data
                    else:
                        res = out
                    st.success(f"✅ {f} đang chạy")
                    active_summaries.append(res)
                except Exception as e: st.error(f"❌ Lỗi {f}: {e}")

    om_key = get_key(all_plots, "obv")
    cmf_key = get_key(all_plots, "cmf")
    vzo_key = get_key(all_plots, "vzo")
    sqz_key = get_key(all_plots, "sqz")
    
    extra_rows = bool(om_key) + bool(cmf_key) + bool(vzo_key) + bool(sqz_key)
    total_rows = 2 + extra_rows
    row_heights = [5, 1] + [2] * extra_rows
    fig = make_subplots(rows=total_rows, cols=1, shared_xaxes=True, vertical_spacing=0.015, row_heights=row_heights)
    
    TV_BG = '#131722'
    TV_GRID = '#2a2e39'
    TV_GREEN = '#26a69a'
    TV_RED = '#ef5350'
    TV_TEXT = '#d1d4dc'
    
    # 1. BIỂU ĐỒ GIÁ
    fig.add_trace(go.Candlestick(x=df['time_str'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    name='Giá', increasing_line_color=TV_GREEN, decreasing_line_color=TV_RED,
                    increasing_fillcolor=TV_GREEN, decreasing_fillcolor=TV_RED), row=1, col=1)
    
    # 2. KHỐI LƯỢNG
    v_colors = [f'rgba(38,166,154,0.4)' if r['Close'] >= r['Open'] else f'rgba(239,83,80,0.4)' for i, r in df.iterrows()]
    fig.add_trace(go.Bar(x=df['time_str'], y=df['Volume'], marker_color=v_colors, name='Volume'), row=2, col=1)
    
    current_row = 3
    
    def plot_markers(fig, y_series, name, text, color, symbol, position, row):
        valid = y_series.dropna()
        if not valid.empty:
            fig.add_trace(go.Scatter(
                x=valid.index.strftime('%Y-%m-%d %H:%M'), y=valid, mode='markers+text',
                text=[text]*len(valid), textposition=position,
                marker=dict(color=color, size=6, symbol=symbol), name=name,
                textfont=dict(size=9, color=color)
            ), row=row, col=1)

    # 3. OBV MACD SNIPER
    if om_key:
        om_data = all_plots[om_key]
        fig.add_trace(go.Scatter(x=df['time_str'], y=om_data["signal_val"], mode='lines', line=dict(width=1.5, color='#2962FF'), name='OBV-MACD'), row=current_row, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)", row=current_row, col=1)
        plot_markers(fig, om_data["buy_labels"], 'Cạn Mua', 'CẠN MUA', TV_GREEN, 'triangle-up', 'bottom center', current_row)
        plot_markers(fig, om_data["sell_labels"], 'Cạn Bán', 'CẠN BÁN', TV_RED, 'triangle-down', 'top center', current_row)
        current_row += 1

    # 4. CMF PRO
    if cmf_key:
        c_data = all_plots[cmf_key]
        fig.add_trace(go.Scatter(x=df['time_str'], y=c_data["mf"], mode='lines', line=dict(width=1.5, color='#E040FB'), name='CMF'), row=current_row, col=1)
        fig.add_hline(y=0, line_color="rgba(255,255,255,0.3)", row=current_row, col=1)
        fig.add_hline(y=0.6, line_dash="dot", line_color="rgba(255,255,255,0.2)", row=current_row, col=1)
        fig.add_hline(y=-0.6, line_dash="dot", line_color="rgba(255,255,255,0.2)", row=current_row, col=1)
        plot_markers(fig, c_data["buy_triggers"], 'CMF Mua', 'MUA', TV_GREEN, 'circle', 'bottom center', current_row)
        plot_markers(fig, c_data["sell_triggers"], 'CMF Bán', 'BÁN', TV_RED, 'circle', 'top center', current_row)
        current_row += 1

    # 5. ĐỈNH ĐÁY VZO
    if vzo_key:
        v_data = all_plots[vzo_key]
        fig.add_trace(go.Scatter(x=df['time_str'], y=v_data["vzo"], mode='lines', line=dict(width=1.5, color='#00BCD4'), name='VZO'), row=current_row, col=1)
        fig.add_hline(y=60, line_dash="dash", line_color="rgba(239,83,80,0.5)", row=current_row, col=1)
        fig.add_hline(y=-60, line_dash="dash", line_color="rgba(38,166,154,0.5)", row=current_row, col=1)
        plot_markers(fig, v_data["buy_signals"], 'VZO Mua', 'KIỆT SỨC', TV_GREEN, 'circle-open', 'bottom center', current_row)
        plot_markers(fig, v_data["sell_signals"], 'VZO Bán', 'KIỆT SỨC', TV_RED, 'circle-open', 'top center', current_row)
        current_row += 1

    # 6. SQUEEZE MOMENTUM
    if sqz_key:
        s_data = all_plots[sqz_key]
        sqz_colors = [TV_GREEN if v > 0 else TV_RED for v in s_data['val']]
        fig.add_trace(go.Bar(x=df['time_str'], y=s_data['val'], marker_color=sqz_colors, name='SQZ'), row=current_row, col=1)
        dot_colors = [TV_RED if sq else TV_GREEN for sq in s_data['sqz_on']]
        fig.add_trace(go.Scatter(x=df['time_str'], y=[0]*len(df), mode='markers', marker=dict(color=dot_colors, size=4)), row=current_row, col=1)
        current_row += 1

    fig.update_layout(
        plot_bgcolor=TV_BG, paper_bgcolor=TV_BG, font=dict(color=TV_TEXT, size=11),
        xaxis_rangeslider_visible=False, height=500 + 180 * extra_rows,
        margin=dict(l=10, r=40, t=30, b=10), showlegend=False, dragmode='pan', hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=TV_GRID)
    fig.update_yaxes(showgrid=True, gridcolor=TV_GRID, side='right')
    
    with col_right:
        st.subheader(f"📊 Live Chart TradingView Pro")
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.markdown("---")
        if active_summaries:
            summary = f"📊 [BỐI CẢNH {selected_ticker} - {selected_tf}]\n" + "\n".join([f"- {s}" for s in active_summaries])
            st.info(summary)
            st.session_state['tech_indicators'] = summary
            st.session_state['current_price'] = float(df['Close'].iloc[-1])
else:
    st.error(f"❌ {error_msg}")
