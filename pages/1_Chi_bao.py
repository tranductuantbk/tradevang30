import streamlit as st
import pandas as pd
import yfinance as yf
import os
import importlib.util
from streamlit_autorefresh import st_autorefresh
import requests # Thêm thư viện giả lập kết nối

st.set_page_config(page_title="Module Chỉ Báo", layout="wide")
st_autorefresh(interval=60000, key="live_refresh")

tf_mapping = {
    "M15": {"interval": "15m", "period": "1mo"},
    "M30": {"interval": "30m", "period": "1mo"},
    "H1": {"interval": "60m", "period": "1mo"},
    "D1": {"interval": "1d", "period": "2y"}
}

st.title("⚙️ Engine Phân Tích Chỉ Báo")

col_t, col_m, col_f = st.columns([2, 1, 1])
with col_m: selected_ticker = st.text_input("📈 Mã YFinance:", value="XAUUSD=X")
with col_f: selected_tf = st.selectbox("⏳ Khung thời gian:", list(tf_mapping.keys()), index=1)

# ==========================================================
# HÀM TẢI DỮ LIỆU ĐÃ ĐƯỢC LẮP "MẶT NẠ" VƯỢT TƯỜNG LỬA
# ==========================================================
@st.cache_data(ttl=60)
def load_data(ticker, interval, period):
    try:
        # 1. Tạo một phiên kết nối giả lập trình duyệt Chrome trên Windows
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })
        
        # 2. Ép yfinance sử dụng phiên kết nối giả lập này
        data = yf.download(ticker, period=period, interval=interval, session=session, progress=False)
        return data
    except Exception as e: 
        print(f"Lỗi tải dữ liệu: {e}") # In lỗi ngầm để dễ kiểm tra trên Terminal
        return pd.DataFrame()

df = load_data(selected_ticker, tf_mapping[selected_tf]["interval"], tf_mapping[selected_tf]["period"])

# ==========================================================
# KHU VỰC QUÉT CHỈ BÁO BÊN DƯỚI (Giữ nguyên)
# ==========================================================
if not df.empty:
    col_left, col_right = st.columns([1, 2])
    active_summaries = []
    
    with col_left:
        st.subheader("🛠️ Kho Chỉ Báo")
        folder = "custom_indicators"
        if not os.path.exists(folder): os.makedirs(folder)
        files = [f for f in os.listdir(folder) if f.endswith('.py') and f != '__init__.py']
        
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
        st.session_state['tech_indicators'] = summary
else:
    st.error("❌ Không tải được dữ liệu. Yahoo Finance có thể đang bảo trì hoặc chặn kết nối. Hãy thử đổi mã thành GC=F.")
