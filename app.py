import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# Cấu hình trang
st.set_page_config(layout="wide", page_title="Quant Trading Hub", page_icon="⚡")

# ==========================================================
# 1. HÀM TẠO PDF (FPD2 + UNICODE HỖ TRỢ TIẾNG VIỆT)
# ==========================================================
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    # FPDF2 mặc định hỗ trợ Unicode tốt với các font tiêu chuẩn
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, txt=text)
    return pdf.output()

# ==========================================================
# 2. KHỞI TẠO AI (BẢO MẬT & DÒ TÌM)
# ==========================================================
model = None
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if models:
        model = genai.GenerativeModel(models[0].name)
except:
    pass

# ==========================================================
# 3. BẢO MẬT HỆ THỐNG
# ==========================================================
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.title("🔒 Security Portal")
        if st.text_input("Nhập mật khẩu:", type="password") == "tbk1102":
            st.session_state["logged_in"] = True
            st.rerun()
    st.stop()

# ==========================================================
# 4. GIAO DIỆN CHÍNH
# ==========================================================
st.title("⚡ Quant Trading Hub - AI Strategist")
st.sidebar.title("📡 System Status")

if model: st.sidebar.success("✅ AI SẴN SÀNG")
else: st.sidebar.error("❌ CHƯA CÓ API KEY")

# Nhập dữ liệu
st.subheader("⚙️ Dữ liệu đầu vào")
indicator_data = st.text_area("Nhập dữ liệu phân tích kỹ thuật:", value="RSI: 30, VZO: -5, Trend: Bearish", height=100)

# Cấu hình AI
st.subheader("🤖 Cấu hình Phân tích")
analysis_focus = st.multiselect(
    "Chọn mục tiêu phân tích:",
    ["Phân tích Kỹ thuật (Technical)", "Phân tích Vĩ mô (Macro)", "Đánh giá Rủi ro (Risk)", "Chiến lược Entry/SL/TP"],
    default=["Phân tích Kỹ thuật (Technical)", "Chiến lược Entry/SL/TP"]
)

if st.button("🚀 KÍCH HOẠT PHÂN TÍCH", type="primary", use_container_width=True):
    if not model:
        st.error("❌ Lỗi kết nối AI.")
    else:
        with st.spinner("🧠 AI đang lập báo cáo chuyên sâu..."):
            try:
                focus_str = ", ".join(analysis_focus)
                prompt = f"""
                Phân tích dữ liệu kỹ thuật: {indicator_data}. 
                Mục tiêu cần tập trung: {focus_str}.
                Hãy đưa ra đánh giá xu hướng và kế hoạch hành động giao dịch chuyên nghiệp cho XAU/USD. 
                Trình bày bằng tiếng Việt.
                """
                response = model.generate_content(prompt)
                st.session_state['ai_report'] = response.text
                st.success("✅ Phân tích xong!")
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")

# Xuất kết quả
if 'ai_report' in st.session_state:
    st.markdown("---")
    st.subheader("📋 Kết quả phân tích")
    st.markdown(st.session_state['ai_report'])
    
    # Xuất PDF
    pdf_bytes = create_pdf(st.session_state['ai_report'])
    st.download_button(
        label="📄 TẢI BÁO CÁO (PDF TỐI ƯU iOS)",
        data=pdf_bytes,
        file_name="Bao_Cao_Trading.pdf",
        mime="application/pdf",
        use_container_width=True
    )
