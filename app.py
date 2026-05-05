import streamlit as st

# Cài đặt cấu hình trang
st.set_page_config(layout="wide", page_title="AI Gold Trading Terminal", page_icon="⚡")

# --- 1. SIDEBAR: KIỂM TRA TRẠNG THÁI MODULE CHẠY NGẦM ---
st.sidebar.title("📡 System Status")
st.sidebar.markdown("Trạng thái dữ liệu từ các Module:")

# Lấy dữ liệu từ session_state 
indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu. Hãy mở trang Module Chỉ báo.")
macro_data = st.session_state.get('macro_info', "⚠️ Chưa có dữ liệu.")
flow_data = st.session_state.get('money_flow', "⚠️ Chưa có dữ liệu.")

st.sidebar.success("Trạng thái Chỉ báo: OK" if "⚠️" not in indicator_data else indicator_data)
st.sidebar.warning("Trạng thái Vĩ mô: Trống" if "⚠️" in macro_data else "Trạng thái Vĩ mô: OK")
st.sidebar.warning("Trạng thái Dòng tiền: Trống" if "⚠️" in flow_data else "Trạng thái Dòng tiền: OK")

# --- 2. GIAO DIỆN CHÍNH (DÀNH CHO DỮ LIỆU & AI) ---
st.title("⚡ Quant Trading Hub - AI Strategist")
st.markdown("Hệ thống tự động tổng hợp dữ liệu từ các module chạy ngầm và đưa ra phân tích bối cảnh.")
st.markdown("---")

# Chia 3 cột để hiển thị tóm tắt dữ liệu mà AI sẽ đọc
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Chỉ báo Kỹ thuật")
    st.info(indicator_data)

with col2:
    st.subheader("🌍 Dữ liệu Vĩ mô")
    st.info(macro_data)

with col3:
    st.subheader("🐋 Dòng tiền (Smart Money)")
    st.info(flow_data)

st.markdown("---")

# --- 3. KHU VỰC AI ĐÁNH GIÁ VÀ VÀO LỆNH ---
st.subheader("🤖 Phân tích bối cảnh & Gợi ý")

# Nút kích hoạt AI
if st.button("🚀 Kích hoạt AI Phân tích Toàn diện", use_container_width=True, type="primary"):
    with st.spinner("AI đang xử lý dữ liệu từ các module và tìm kiếm điểm vào lệnh..."):
        
        st.success("""
        💡 **Đánh giá từ AI (Demo):** 
        Dựa trên dữ liệu hội tụ hiện tại:
        - VSA trên M30 cho thấy khối lượng cạn kiệt ở nhịp giảm (No Supply).
        - Dòng tiền lớn chưa có dấu hiệu phân phối mạnh.
        - **Khuyến nghị:** Cấu trúc thuận lợi để canh BUY.
        """)
        
        st.markdown("### ⚡ Cài đặt Lệnh / Lưu Nhật ký")
        with st.container():
            col_entry, col_sl, col_btn = st.columns([2, 2, 2])
            
            with col_entry:
                entry = st.number_input("Giá Entry", value=2350.00, step=0.1)
            with col_sl:
                sl = st.number_input("Giá Stoploss", value=2345.00, step=0.1)
            with col_btn:
                st.write("") 
                st.write("")
                if st.button("Lưu vào Neon DB", use_container_width=True):
                    st.success(f"Đã lưu nhật ký: Canh Buy quanh {entry}, Stoploss tại {sl}!")
