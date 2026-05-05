import streamlit as st
from streamlit_tradingview_chart import build_chart # Thư viện hỗ trợ TV Chart
import pandas as pd
from utils.ai_engine import analyze_market

st.set_page_config(layout="wide", page_title="AI Gold Trading Terminal")

# --- SIDEBAR (Dữ liệu ngầm tự cập nhật) ---
st.sidebar.title("📡 System Modules Status")
# Giả sử các module đã ghi dữ liệu vào session_state
indicator_data = st.session_state.get('tech_indicators', "Đang tải...")
macro_data = st.session_state.get('macro_info', "Đang tải...")
flow_data = st.session_state.get('money_flow', "Đang tải...")

# --- MAIN SECTION ---
col_chart, col_ai = st.columns([2, 1])

with col_chart:
    st.subheader("XAU/USD Live Chart")
    timeframe = st.selectbox("Timeframe", ["30m", "1h", "4h", "1d"], index=0)
    
    # Tích hợp biểu đồ TradingView chuyên nghiệp
    # Lưu ý: Cần cài đặt streamlit-tradingview-chart
    build_chart(symbol="OANDA:XAU_USD", interval=timeframe)

with col_ai:
    st.subheader("🤖 AI Strategist")
    if st.button("🚀 Đọc & Phân tích toàn bộ Module"):
        with st.spinner("AI đang tổng hợp dữ liệu vĩ mô, dòng tiền và chỉ báo..."):
            # Gửi tất cả dữ liệu từ session_state cho AI
            context = {
                "indicators": indicator_data,
                "macro": macro_data,
                "flow": flow_data,
                "current_price": "23xx.x" 
            }
            analysis_result = analyze_market(context)
            st.markdown(analysis_result)
            
            # Lưu phân tích này vào Neon DB để theo dõi sau
            # save_to_neon(analysis_result)