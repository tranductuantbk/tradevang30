import streamlit as st

# Cài đặt trang cơ bản
st.set_page_config(layout="wide", page_title="AI Trading Terminal")

st.title("⚡ Quant Trading Hub - Trạng thái: Đang hoạt động!")
st.success("✅ Hệ thống Streamlit đã khởi động thành công. Môi trường không có lỗi.")

st.markdown("---")
st.markdown("### ⚡ Bảng Test Giao Diện")

# Chia cột đơn giản
col1, col2, col3 = st.columns(3)
with col1:
    entry = st.number_input("Giá Entry", value=2350.0)
with col2:
    sl = st.number_input("Giá Stoploss", value=2345.0)
with col3:
    st.write("")
    st.write("") # Đẩy nút xuống cho cân bằng
    if st.button("Test Hệ Thống", use_container_width=True):
        st.info(f"Đã nhận tín hiệu. Entry: {entry} - SL: {sl}")
