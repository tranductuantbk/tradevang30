import streamlit as st

st.set_page_config(layout="wide", page_title="AI Gold Trading Terminal", page_icon="⚡")

# --- 1. SIDEBAR: TRẠNG THÁI HỆ THỐNG ---
st.sidebar.title("📡 System Status")
st.sidebar.markdown("Kiểm tra kết nối dữ liệu:")

indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu. Vui lòng mở trang '1_Chi_bao' để kích hoạt máy chủ.")
macro_data = st.session_state.get('macro_info', "⚠️ Chưa có dữ liệu Vĩ mô.")
flow_data = st.session_state.get('money_flow', "⚠️ Chưa có dữ liệu Dòng tiền.")

if "⚠️" in indicator_data:
    st.sidebar.warning(indicator_data)
else:
    st.sidebar.success("✅ Module Chỉ báo: SẴN SÀNG")

st.sidebar.info("Hệ thống tự động quét 1 phút/lần khi module được kích hoạt.")

# --- 2. GIAO DIỆN TRẠM ĐIỀU KHIỂN ---
st.title("⚡ Quant Trading Hub - AI Strategist")
st.markdown("Hệ thống tổng hợp tín hiệu từ các chỉ báo tùy chỉnh và đưa ra quyết định giao dịch.")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Chỉ báo Kỹ thuật")
    if "⚠️" in indicator_data:
        st.warning(indicator_data)
    else:
        st.info(indicator_data)

with col2:
    st.subheader("🌍 Dữ liệu Vĩ mô")
    st.warning(macro_data)

with col3:
    st.subheader("🐋 Dòng tiền (Smart Money)")
    st.warning(flow_data)

st.markdown("---")

# --- 3. BỘ NÃO AI PHÂN TÍCH ---
st.subheader("🤖 Phân tích bối cảnh & Gợi ý")

if st.button("🚀 KÍCH HOẠT AI PHÂN TÍCH TOÀN DIỆN", use_container_width=True, type="primary"):
    if "⚠️" in indicator_data:
        st.error("LỖI: AI không tìm thấy dữ liệu kỹ thuật! Hãy mở trang '1_Chi_bao' rồi quay lại đây.")
    else:
        with st.spinner("AI đang đọc dữ liệu từ các Module chạy ngầm..."):
            # Chờ kết nối API thực tế
            st.success(f"💡 **NHẬN ĐỊNH TỪ AI:** Hệ thống đã ghi nhận bối cảnh. Đang chờ lệnh từ Strategist...")
        
        st.markdown("### ⚡ Cài đặt Lệnh Giao dịch")
        c_entry, c_sl, c_tp = st.columns(3)
        with c_entry: st.number_input("Giá Entry", value=4712.00, step=0.1)
        with c_sl: st.number_input("Giá Stoploss", value=4705.00, step=0.1)
        with c_tp: st.number_input("Giá Take Profit", value=4730.00, step=0.1)
