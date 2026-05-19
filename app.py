import streamlit as st
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 1. CẤU HÌNH AI (LẤY TỪ SECRETS - KHÔNG ĐỂ LỘ KEY)
# ==========================================================
model = None
try:
    # Tự động lấy API_KEY từ cài đặt bảo mật của Streamlit
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.sidebar.error("❌ Chưa thiết lập Secrets hoặc Key lỗi. Xem hướng dẫn!")

# ==========================================================
# 2. BẢO MẬT HỆ THỐNG
# ==========================================================
SECRET_PASSWORD = "tbk1102"
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    col_b = st.columns([1, 1, 1])[1]
    with col_b:
        st.title("🔒 Security Portal")
        pwd = st.text_input("Nhập mật khẩu:", type="password")
        if st.button("Truy cập"):
            if pwd == SECRET_PASSWORD:
                st.session_state["logged_in"] = True
                st.rerun()
            else: st.error("Sai mật khẩu!")
    st.stop()

# ==========================================================
# 3. GIAO DIỆN CHÍNH
# ==========================================================
st.sidebar.title("📡 System Status")
if model: st.sidebar.success("✅ AI SẴN SÀNG")
else: st.sidebar.error("❌ AI CHƯA KẾT NỐI")

indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu Kỹ thuật.")
live_price = st.session_state.get('current_price', 0.0)

st.title("⚡ Quant Trading Hub")
st.markdown(f"**Mã theo dõi:** XAU/USD | **Giá:** `{live_price:,.2f}`")

c1, c2 = st.columns([1, 1])

with c1:
    analysis_mode = st.selectbox("🧠 Nguồn dữ liệu:", ["1. Phân tích Kỹ thuật", "2. Phân tích Vĩ mô", "3. Tổng hợp"])
    with st.expander("Dữ liệu thô"):
        st.code(indicator_data, language="text")

with c2:
    st.subheader("🤖 Phân Tích & Xuất Báo Cáo")
    if st.button("🚀 KÍCH HOẠT AI PHÂN TÍCH", use_container_width=True, type="primary"):
        if not model:
            st.error("❌ Model AI không hoạt động. Kiểm tra lại API_KEY trong Secrets.")
        else:
            with st.spinner("🧠 AI đang âm thầm lập báo cáo..."):
                try:
                    prompt = f"Phân tích chuyên sâu cho quỹ đầu tư về dữ liệu: {indicator_data}. Đưa ra xu hướng và kế hoạch hành động."
                    response = model.generate_content(prompt)
                    st.session_state['ai_report'] = response.text
                    st.success("✅ Phân tích hoàn tất!")
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")

    if 'ai_report' in st.session_state:
        st.download_button(
            label="📄 TẢI BÁO CÁO PHÂN TÍCH (.md)",
            data=st.session_state['ai_report'],
            file_name="Bao_Cao_Giao_Dich.md",
            mime="text/markdown",
            use_container_width=True
        )
