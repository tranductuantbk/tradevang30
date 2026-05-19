import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import io

# Cấu hình trang
st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 1. HÀM TẠO PDF
# ==========================================================
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Xử lý ký tự tiếng Việt đơn giản (ép về latin-1 để không lỗi font)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S')

# ==========================================================
# 2. KHỞI TẠO AI (DÒ TÌM TỰ ĐỘNG)
# ==========================================================
model = None
try:
    # Ưu tiên lấy Key từ Secrets, nếu không có thì lấy từ Sidebar (để tiện test)
    api_key = st.secrets["API_KEY"] if "API_KEY" in st.secrets else None
    
    if api_key:
        genai.configure(api_key=api_key)
        all_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if all_models:
            model = genai.GenerativeModel(all_models[0].name)
except:
    pass

# ==========================================================
# 3. BẢO MẬT & ĐĂNG NHẬP
# ==========================================================
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    col_b = st.columns([1, 1, 1])[1]
    with col_b:
        st.title("🔒 Security Portal")
        if st.text_input("Nhập mật khẩu:", type="password") == "tbk1102":
            st.session_state["logged_in"] = True
            st.rerun()
    st.stop()

# ==========================================================
# 4. GIAO DIỆN CHÍNH
# ==========================================================
st.sidebar.title("📡 System Status")
if model: st.sidebar.success("✅ AI ĐÃ KẾT NỐI")
else: st.sidebar.error("❌ CHƯA CÓ API KEY")

indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu.")
st.title("⚡ Quant Trading Hub")

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("⚙️ Dữ liệu đầu vào")
    st.code(indicator_data, language="text")

with c2:
    st.subheader("🤖 AI Phân tích")
    if st.button("🚀 KÍCH HOẠT PHÂN TÍCH", type="primary"):
        if not model:
            st.error("❌ Cần thiết lập API Key trong Secrets.")
        else:
            with st.spinner("🧠 AI đang làm việc..."):
                response = model.generate_content(f"Phân tích dữ liệu: {indicator_data}. Đưa ra chiến lược.")
                st.session_state['ai_report'] = response.text
                st.success("✅ Phân tích xong!")

    if 'ai_report' in st.session_state:
        st.info(st.session_state['ai_report'])
        # Nút tải PDF
        pdf_data = create_pdf(st.session_state['ai_report'])
        st.download_button(
            label="📄 TẢI XUỐNG PDF",
            data=pdf_data,
            file_name="Bao_Cao_Trading.pdf",
            mime="application/pdf",
            use_container_width=True
        )
