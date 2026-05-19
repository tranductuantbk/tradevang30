import streamlit as st
import google.generativeai as genai

# Cấu hình trang
st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 0. BẢO MẬT HỆ THỐNG
# ==========================================================
SECRET_PASSWORD = "tbk1102"

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
# 1. CẤU HÌNH AI
# ==========================================================
st.sidebar.title("🔑 Cấu hình AI")
# Lấy API Key từ Secrets để bảo mật
try:
    api_key = st.secrets["API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.sidebar.error("❌ Chưa thiết lập API_KEY trong Secrets.")
    st.stop()

# ==========================================================
# 2. GIAO DIỆN CHÍNH
# ==========================================================
st.title("⚡ Quant Trading Hub - AI Strategist")

# Mock data (thay thế giá thực nếu cần)
live_price = 2350.5 

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("⚙️ Dữ liệu thị trường")
    indicator_data = st.text_area("Nhập dữ liệu phân tích kỹ thuật:", value="RSI: 30, VZO: -5, Trend: Bearish", height=150)
    
    if st.button("🚀 PHÂN TÍCH AI", type="primary"):
        with st.spinner("Đang phân tích..."):
            prompt = f"""
            Phân tích dữ liệu: {indicator_data}.
            1. Đánh giá xu hướng hiện tại.
            2. Đưa ra KẾ HOẠCH GIAO DỊCH (Entry, SL, TP).
            3. Trình bày chuyên nghiệp bằng tiếng Việt.
            """
            response = model.generate_content(prompt)
            st.session_state['ai_report'] = response.text
            st.success("✅ Phân tích xong!")

with c2:
    st.subheader("📋 Kết quả phân tích")
    if 'ai_report' in st.session_state:
        st.markdown(st.session_state['ai_report'])
        
        # NÚT TẢI BÁO CÁO (Giải pháp Markdown cho iOS)
        st.download_button(
            label="📄 TẢI BÁO CÁO (.md)",
            data=st.session_state['ai_report'],
            file_name="Bao_Cao_Giao_Dich.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.info("Chờ dữ liệu phân tích...")
