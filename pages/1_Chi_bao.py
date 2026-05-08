import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import os
import importlib.util
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Module Chỉ Báo", layout="wide")
st_autorefresh(interval=60000, key="live_refresh")

tf_mapping = {
    "M15": {"yf_interval": "15m", "yf_period": "1mo", "td_interval": "15min"},
    "M30": {"yf_interval": "30m", "yf_period": "1mo", "td_interval": "30min"},
    "H1":  {"yf_interval": "60m", "yf_period": "1mo", "td_interval": "1h"},
    "D1":  {"yf_interval": "1d",  "yf_period": "2y",  "td_interval": "1day"}
}

st.title("⚙️ Engine Phân Tích Chỉ Báo (Bản API Chuyên Nghiệp)")

# ======================================================================
# QUAN TRỌNG: Hãy điền API Key thật của bạn vào đây
# ======================================================================
API_KEY = "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY" 

col_t, col_m, col_f = st.columns([2, 1, 1])
with col_m: selected_ticker = st.text_input("📈 Mã Giao dịch:", value="XAU/USD")
with col_f: selected_tf = st.selectbox("⏳ Khung thời gian:", list(tf_mapping.keys()), index=1)

@st.cache_data(ttl=60)
def load_data(ticker, tf_label, api_key):
    try:
        if ticker.upper() == "XAU/USD":
            if not api_key or api_key == "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY":
                return pd.DataFrame(), "Vui lòng điền API Key của Twelve Data vào code (dòng 21) để lấy dữ liệu XAU/USD."
                
            td_interval = tf_mapping[tf_label]["td_interval"]
            url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval={td_interval}&outputsize=1000&apikey={api_key}"
            response = requests.get(url).json()
            
            if "values" not in response:
                return pd.DataFrame(), f"Lỗi API Twelve Data: {response.get('message', 'Lỗi kết nối.')}"
            
            df = pd.DataFrame(response['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime').sort_index(ascending=True)
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            return df, "OK"
        else:
            # Dành cho các mã khác như GC=F
            interval = tf_mapping[tf_label]["yf_interval"]
            period = tf_mapping[tf_label]["yf_period"]
            data = yf.Ticker(ticker).history(period=period, interval=interval)
            if data.empty: return pd.DataFrame(), "Lỗi dữ liệu."
            if data.index.tz is not None: data.index = data.index.tz_localize(None)
            return data, "OK"
    except Exception as e: return pd.DataFrame(), str(e)

df, error_msg = load_data(selected_ticker, selected_tf, API_KEY)

if not df.empty:
    col_left, col_right = st.columns([1, 2])
    active_summaries = []
    
    with col_left:
        st.subheader("🛠️ Kho Chỉ Báo")
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

    st.markdown("---")
    if active_summaries:
        summary = f"📊 [BỐI CẢNH {selected_ticker} - {selected_tf}]\n" + "\n".join([f"- {s}" for s in active_summaries])
        st.info(summary)
        # LƯU TRỮ DỮ LIỆU ĐỂ TRUYỀN SANG TRANG CHỦ
        st.session_state['tech_indicators'] = summary
        st.session_state['current_price'] = float(df['Close'].iloc[-1])
else:
    st.error(f"❌ {error_msg}")
