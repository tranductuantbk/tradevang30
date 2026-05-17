import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import os
import importlib.util
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Module Chỉ Báo", layout="wide")

# ==========================================================
# CỔNG BẢO VỆ (SECURITY GATE)
# ==========================================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🔒 Vui lòng quay lại trang chủ để đăng nhập trước khi sử dụng công cụ này.")
    if st.button("Đi tới trang chủ"):
        st.switch_page("app.py")
    st.stop()

# ==========================================================
# PHẦN CODE CHỈ BÁO
# ==========================================================
st_autorefresh(interval=60000, key="live_refresh")

tf_mapping = {
    "M15": {"yf_interval": "15m", "yf_period": "1mo", "td_interval": "15min"},
    "M30": {"yf_interval": "30m", "yf_period": "1mo", "td_interval": "30min"},
    "H1":  {"yf_interval": "60m", "yf_period": "1mo", "td_interval": "1h"},
    "D1":  {"yf_interval": "1d",  "yf_period": "2y",  "td_interval": "1day"}
}

st.title("⚙️ Engine Phân Tích Kỹ Thuật (TradingView Sync)")

# QUAN TRỌNG: Hãy điền API Key thật của bạn vào đây
API_KEY = "cf03fc875ee64027a947ccab5ceced4b" 

col_t, col_m, col_f = st.columns([2, 1, 1])
with col_m: selected_ticker = st.text_input("📈 Mã Giao dịch:", value="XAU/USD")
with col_f: selected_tf = st.selectbox("⏳ Khung thời gian:", list(tf_mapping.keys()), index=1)

@st.cache_data(ttl=60)
def load_data(ticker, tf_label, api_key):
    try:
        if ticker.upper() == "XAU/USD":
            if not api_key or api_key == "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY":
                return pd.DataFrame(), "Vui lòng điền API Key của Twelve Data."
                
            td_interval = tf_mapping[tf_label]["td_interval"]
            url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval={td_interval}&outputsize=1000&apikey={api_key}"
            response = requests.get(url).json()
            
            if "values" not in response:
                return pd.DataFrame(), f"Lỗi API: {response.get('message', 'Lỗi kết nối.')}"
            
            df = pd.DataFrame(response['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime').sort_index(ascending=True)
            
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns: df[col] = df[col].astype(float)
            
            if 'volume' in df.columns:
                df['volume'] = df['volume'].astype(float)
            else:
                df['volume'] = 0.0
                
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            return df, "OK"
        else:
            interval = tf_mapping[tf_label]["yf_interval"]
            period = tf_mapping[tf_label]["yf_period"]
            data = yf.Ticker(ticker).history(period=period, interval=interval)
            if data.empty: return pd.DataFrame(), "Lỗi dữ liệu."
            if data.index.tz is not None: data.index = data.index.tz_localize(None)
            return data, "OK"
    except Exception as e: return pd.DataFrame(), str(e)

df, error_msg = load_data(selected_ticker, selected_tf, API_KEY)

if not df.empty:
    
    # ==========================================================
    # KHU VỰC VẼ BIỂU ĐỒ TRỰC QUAN (GIỐNG TRADINGVIEW)
    # ==========================================================
    st.subheader(f"📊 Biểu đồ Hành vi Giá: {selected_ticker} ({selected_tf})")
    
    # Tạo layout biểu đồ có 2 hàng (Hàng 1: Nến, Hàng 2: Volume)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.7, 0.3])
    
    # Vẽ Nến Nhật
    fig.add_trace(go.Candlestick(x=df.index,
                    open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    name='Price',
                    increasing_line_color='#00E676', decreasing_line_color='#FF1744'),
                    row=1, col=1)
    
    # Vẽ Volume (Màu xanh/đỏ theo nến)
    colors = ['#00E676' if row['Close'] >= row['Open'] else '#FF1744' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'),
                  row=2, col=1)
                  
    # Chỉnh giao diện tối (Dark mode) và tắt thanh kéo trượt để nhìn gọn gàng
    fig.update_layout(
        xaxis_rangeslider_visible=False, 
        height=600, 
        template='plotly_dark',
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False
    )
    
    # Hiển thị biểu đồ ra màn hình
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==========================================================
    # KHU VỰC KÍCH HOẠT CHỈ BÁO & AI SUMMARIES
    # ==========================================================
    col_left, col_right = st.columns([1, 2])
    active_summaries = []
    
    with col_left:
        st.subheader("🛠️ Kho Chỉ Báo Kỹ Thuật")
        folder = "custom_indicators"
        if not os.path.exists(folder): os.makedirs(folder)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.py') and f != '__init__.py'])
        
        for f in files:
            if st.checkbox(f"Kích hoạt: {f}", value=True):
                with col_right:
                    try:
                        spec = importlib.util.spec_from_file_location(f.replace('.py',''), os.path.join(folder, f))
                        m = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(m)
                        res = m.run_indicator(df)
                        st.success(f"✅ {f} đang chạy.")
                        active_summaries.append(res)
                    except Exception as e: st.error(f"❌ Lỗi {f}: {e}")

    if active_summaries:
        summary = f"📊 [BỐI CẢNH {selected_ticker} - {selected_tf}]\n" + "\n".join([f"- {s}" for s in active_summaries])
        st.info(summary)
        st.session_state['tech_indicators'] = summary
        st.session_state['current_price'] = float(df['Close'].iloc[-1])
else:
    st.error(f"❌ {error_msg}")
