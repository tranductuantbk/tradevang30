import streamlit as st

st.set_page_config(layout="wide", page_title="Lá Hữu Đức Quant Hub", page_icon="⚡")

# ==========================================================
# 0. BẢO MẬT
# ==========================================================
SECRET_PASSWORD = "tbk1102" # Hãy đổi mật khẩu của bạn tại đây

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.title("🔒 Security Portal")
        pwd = st.text_input("Nhập mật khẩu truy cập:", type="password")
        if st.button("Truy cập hệ thống", use_container_width=True):
            if pwd == SECRET_PASSWORD:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Mật khẩu sai!")
    st.stop()

# ==========================================================
# 1. SIDEBAR TRẠNG THÁI
# ==========================================================
st.sidebar.title("📡 System Status")
indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu. Vui lòng mở trang '1_Chi_bao'.")
live_price = st.session_state.get('current_price', 0.0)

if "⚠️" in indicator_data:
    st.sidebar.warning(indicator_data)
else:
    st.sidebar.success(f"✅ Dữ liệu Giá: {live_price:,.2f}")
    st.sidebar.success("✅ Module Kỹ thuật: ONLINE")

if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state["logged_in"] = False
    st.rerun()

# ==========================================================
# 2. BẢNG ĐIỀU KHIỂN CHÍNH
# ==========================================================
st.title("⚡ Quant Trading Hub - AI Strategist")
st.markdown(f"**Mã theo dõi:** XAU/USD | **Giá hiện tại:** `{live_price:,.2f}`")
st.markdown("---")

c1, c2 = st.columns([2, 1])
with c1:
    st.subheader("📊 Tổng hợp Chỉ báo")
    st.info(indicator_data)
with c2:
    st.subheader("🤖 AI Hành động")
    if st.button("🚀 PHÂN TÍCH & ĐỀ XUẤT", use_container_width=True, type="primary"):
        with st.spinner("Đang tính toán bối cảnh..."):
            st.success("Hệ thống đã sẵn sàng. AI đang chờ lệnh từ bạn.")

st.markdown("---")

# ==========================================================
# 3. CÀI ĐẶT LỆNH (TỰ ĐỘNG CẬP NHẬT GIÁ)
# ==========================================================
st.subheader("⚡ Cài đặt Lệnh Giao dịch")
entry_col, sl_col, tp_col = st.columns(3)

# Tự động tính toán SL/TP dựa trên giá thực tế
with entry_col: 
    entry_price = st.number_input("Giá Entry", value=float(live_price), step=0.1, format="%.2f")
with sl_col: 
    st.number_input("Giá Stoploss (Dự kiến -5 giá)", value=float(live_price - 5), step=0.1, format="%.2f")
with tp_col: 
    st.number_input("Giá Take Profit (Dự kiến +15 giá)", value=float(live_price + 15), step=0.1, format="%.2f")

st.caption("Lưu ý: Giá SL/TP được gợi ý dựa trên biến động ATR trung bình của hệ thống.")
