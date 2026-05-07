import streamlit as st
import pandas as pd
import yfinance as yf
import os
import importlib.util
from streamlit_autorefresh import st_autorefresh

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
# CHIẾN THUẬT MỚI: DÙNG CLASS "TICKER" ĐỂ NÉ TƯỜNG LỬA
# ==========================================================
@st.cache_data(ttl=60)
def load_data(ticker, interval, period):
    try:
        tk = yf.Ticker(ticker)
        data = tk.history(period=period, interval=interval)
        
        if data.empty:
            return pd.DataFrame(), "Yahoo Finance không trả về dữ liệu. Có thể do sai mã giao dịch hoặc IP máy chủ đám mây đang bị Yahoo tạm khóa."
            
        # Xóa định dạng múi giờ để tránh xung đột hệ thống
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
            
        return data, "OK"
    except Exception as e: 
        return pd.DataFrame(), str(e)

# Chạy hàm tải dữ liệu và lấy thông báo lỗi (nếu có)
df, error_msg = load_data(selected_ticker, tf_mapping[selected_tf]["interval"], tf_mapping[selected_tf]["period"])

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
    # HIỂN THỊ TRỰC TIẾP LÝ DO LỖI RA MÀN HÌNH ĐỂ BẮT BỆNH
    st.error(f"❌ Lỗi truy xuất dữ liệu: {error_msg}")
    st.warning("💡 Gợi ý: Hãy thử xóa mã XAUUSD=X, gõ lại GC=F (Hợp đồng tương lai Vàng) và nhấn Enter xem Yahoo có nhả dữ liệu không.")
