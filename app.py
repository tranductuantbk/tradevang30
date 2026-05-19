import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# Cấu hình trang
st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 1. HÀM TẠO PDF (ĐÃ SỬA LỖI TRANG TRẮNG)
# ==========================================================
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Xử lý tiếng Việt (ép về latin-1 để không lỗi font)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    # Trả về kết quả PDF trực tiếp
    return pdf.output(dest='S').encode('latin-1')

# ==========================================================
# 2. KHỞI TẠO AI
# ==========================================================
model = None
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    # Tự động dò tìm model khả dụng
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if models:
        model = genai.GenerativeModel(models[0].name)
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
        else: st.stop()

# ==========================================================
# 4. GIAO DIỆN CHÍNH (ĐÃ XÓA KHU VỰC TÍNH TOÁN)
# ==========================================================
st.title("⚡ Quant Trading Hub - AI Strategist")
st.sidebar.title("📡 System Status")

if model: st.sidebar.success("✅ AI SẴN SÀNG")
else: st.sidebar.error("❌ CHƯA CÓ API KEY")

indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu.")
st.markdown(f"**Trạng thái:** Hệ thống đang hoạt động ổn định.")

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("⚙️ Dữ liệu đầu vào")
    with st.expander("Dữ liệu thô"):
        st.code(indicator_data, language="text")

with c2:
    st.subheader("🤖 AI Phân tích")
    if st.button("🚀 KÍCH HOẠT PHÂN TÍCH", type="primary", use_container_width=True):
        if not model:
            st.error("❌ Lỗi kết nối AI.")
        else:
            with st.spinner("🧠 AI đang lập báo cáo..."):
                try:
                    response = model.generate_content(f"Phân tích dữ liệu: {indicator_data}. Đưa ra chiến lược.")
                    st.session_state['ai_report'] = response.text
                    st.success("✅ Phân tích xong!")
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")

    # Xuất file PDF sau khi phân tích
    if 'ai_report' in st.session_state:
        st.markdown("---")
        pdf_data = create_pdf(st.session_state['ai_report'])
        st.download_button(
            label="📄 TẢI BÁO CÁO DẠNG PDF",
            data=pdf_data,
            file_name="Bao_Cao_Trading.pdf",
            mime="application/pdf",
            use_container_width=True
        )
