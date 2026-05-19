import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# Cấu hình trang
st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 1. HÀM TẠO PDF (TỐI ƯU CHO iOS - UTF-8)
# ==========================================================
def create_pdf(text):
    # Sử dụng fpdf2, bật chế độ hỗ trợ Unicode
    pdf = FPDF()
    pdf.add_page()
    # fpdf2 có font Helvetica hỗ trợ Unicode tốt
    pdf.set_font("Helvetica", size=12)
    # Ghi nội dung, tự động xuống dòng
    pdf.multi_cell(0, 10, txt=text)
    # Trả về bytes
    return pdf.output()

# ==========================================================
# 2. KHỞI TẠO AI & ĐĂNG NHẬP
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

# Khởi tạo AI (chỉ chạy khi đã đăng nhập)
model = None
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if models: model = genai.GenerativeModel(models[0].name)
except: pass

# ==========================================================
# 3. GIAO DIỆN CHÍNH
# ==========================================================
st.title("⚡ Quant Trading Hub")
indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu.")

c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("⚙️ Dữ liệu đầu vào")
    st.code(indicator_data, language="text")

with c2:
    st.subheader("🤖 AI Phân tích")
    if st.button("🚀 KÍCH HOẠT PHÂN TÍCH", type="primary", use_container_width=True):
        if not model: st.error("Lỗi AI.")
        else:
            with st.spinner("Đang lập báo cáo..."):
                try:
                    response = model.generate_content(f"Phân tích dữ liệu: {indicator_data}. Đưa ra chiến lược giao dịch chuyên nghiệp cho XAU/USD.")
                    st.session_state['ai_report'] = response.text
                    st.success("✅ Phân tích xong!")
                except Exception as e: st.error(f"Lỗi: {e}")

    # Xuất PDF
    if 'ai_report' in st.session_state:
        st.markdown("---")
        pdf_data = create_pdf(st.session_state['ai_report'])
        st.download_button(
            label="📄 TẢI BÁO CÁO (PDF - Tối ưu iOS)",
            data=pdf_data,
            file_name="Bao_Cao_Trading.pdf",
            mime="application/pdf",
            use_container_width=True
        )
