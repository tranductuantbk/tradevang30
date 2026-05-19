import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from macro_intel import MacroAnalyzer # Nhập module vĩ mô của bạn

# Cấu hình trang
st.set_page_config(layout="wide", page_title="Quant Trading Hub", page_icon="⚡")

# Khởi tạo module vĩ mô
macro_engine = MacroAnalyzer()

# ==========================================================
# 1. HÀM TẠO PDF (SỬ DỤNG FPDF2 - GIẢI QUYẾT LỖI UNICODE)
# ==========================================================
def create_pdf(text):
    # FPDF2 hỗ trợ Unicode hoàn toàn bằng font mặc định
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    # Ghi nội dung (fpdf2 xử lý dấu tiếng Việt tự động)
    pdf.multi_cell(0, 10, txt=text)
    # Xuất ra bytes để download
    return pdf.output()

# ==========================================================
# 2. KHỞI TẠO AI
# ==========================================================
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = None

# ==========================================================
# 3. GIAO DIỆN CHÍNH
# ==========================================================
st.title("⚡ Quant Trading Hub - AI Strategist")

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("⚙️ Dữ liệu đầu vào")
    indicator_data = st.text_area("Nhập dữ liệu kỹ thuật:", height=150)
    
    # Hiển thị module vĩ mô
    macro_data = macro_engine.render_ui()
    
    if st.button("🚀 KÍCH HOẠT PHÂN TÍCH", type="primary"):
        with st.spinner("🧠 AI đang lập báo cáo..."):
            macro_summary = macro_engine.get_summary()
            full_prompt = f"""
            Dữ liệu kỹ thuật: {indicator_data}
            Dữ liệu vĩ mô: {macro_summary}
            Hãy phân tích xu hướng và đưa ra kế hoạch giao dịch chuyên nghiệp cho XAU/USD. 
            Trình bày bằng tiếng Việt có dấu.
            """
            response = model.generate_content(full_prompt)
            st.session_state['ai_report'] = response.text
            st.success("✅ Phân tích xong!")

with c2:
    st.subheader("📋 Kết quả")
    if 'ai_report' in st.session_state:
        st.markdown(st.session_state['ai_report'])
        
        # Tải PDF (Đã fix lỗi Unicode)
        pdf_bytes = create_pdf(st.session_state['ai_report'])
        st.download_button(
            label="📄 TẢI BÁO CÁO PDF (Bản sửa lỗi)",
            data=pdf_bytes,
            file_name="Bao_Cao_Trading.pdf",
            mime="application/pdf",
            use_container_width=True
        )
