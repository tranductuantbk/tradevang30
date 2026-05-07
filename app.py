import streamlit as st

# Cài đặt cấu hình trang
st.set_page_config(layout="wide", page_title="AI Gold Trading Terminal", page_icon="⚡")

# --- 1. SIDEBAR: KIỂM TRA TRẠNG THÁI MODULE ---
st.sidebar.title("📡 System Status")
st.sidebar.markdown("Trạng thái dữ liệu từ các Module:")

# Lấy dữ liệu từ session_state (bộ nhớ tạm)
indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu. Vui lòng mở trang '1 Chi bao' để hệ thống tính toán lần đầu.")
macro_data = st.session_state.get('macro_info', "⚠️ Chưa có dữ liệu Vĩ mô.")
flow_data = st.session_state.get('money_flow', "⚠️ Chưa có dữ liệu Dòng tiền.")

# Logic hiển thị màu sắc chuẩn: Lỗi màu vàng, Thành công màu xanh
if "⚠️" in indicator_data:
    st.sidebar.warning(indicator_data)
else:
    st.sidebar.success("✅ Trạng thái Chỉ báo: OK")

if "⚠️" in macro_data:
    st.sidebar.warning(macro_data)
else:
    st.sidebar.success("✅ Trạng thái Vĩ mô: OK")

if "⚠️" in flow_data:
    st.sidebar.warning(flow_data)
else:
    st.sidebar.success("✅ Trạng thái Dòng tiền: OK")


# --- 2. GIAO DIỆN CHÍNH ---
st.title("⚡ Quant Trading Hub - AI Strategist")
st.markdown("Hệ thống tự động tổng hợp dữ liệu từ các module chạy ngầm và đưa ra phân tích bối cảnh.")
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
    st.warning(macro_data) # Module chưa phát triển

with col3:
    st.subheader("🐋 Dòng tiền (Smart Money)")
    st.warning(flow_data) # Module chưa phát triển

st.markdown("---")

# --- 3. KHU VỰC AI ĐÁNH GIÁ VÀ VÀO LỆNH ---
st.subheader("🤖 Phân tích bối cảnh & Gợi ý")

if st.button("🚀 Kích hoạt AI Phân tích Toàn diện", use_container_width=True, type="primary"):
    if "⚠️" in indicator_data:
        st.error("Hệ thống chưa có đủ dữ liệu! Vui lòng mở Module Chỉ báo trước để nạp dữ liệu vào bộ nhớ.")
    else:
        with st.spinner("AI đang xử lý dữ liệu từ các module và tìm kiếm điểm vào lệnh..."):
            
            # (Sau này sẽ nối API thật của Gemini/OpenAI vào đây)
            st.success(f"""
            💡 **Đánh giá từ AI (Mô phỏng):** Dữ liệu đã nạp thành công. Đang chờ kết nối bộ não AI để đọc và phân tích cấu trúc giá...
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
