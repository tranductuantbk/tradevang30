import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from unidecode import unidecode

# ==========================================================
# CẤU HÌNH TRANG
# ==========================================================
st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 1. HÀM TẠO PDF (KHỬ DẤU ĐỂ KHÔNG LỖI FONT)
# ==========================================================
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Khử dấu tiếng Việt để PDF hiển thị ổn định 100%
    clean_text = unidecode(text)
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================================
# 2. KHỞI TẠO AI (DÒ TÌM TỰ ĐỘNG)
# ==========================================================
model = None
try:
    # Lấy API Key từ Secrets của Streamlit (bảo mật tuyệt đối)
    genai.configure(api_key=st.secrets["API_KEY"])
    # Tự động lấy model khả dụng
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if models:
        model = genai.GenerativeModel(models[0].name)
except Exception as e:
    st.sidebar.error(f"❌ Lỗi cấu hình AI: {e}")

# ==========================================================
# 3. BẢO MẬT HỆ THỐNG
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
st.title("⚡ Quant Trading Hub - AI Strategist")
st.sidebar.title("📡 System Status")

if model: st.sidebar.success("✅ AI ĐÃ KẾT NỐI")
else: st.sidebar.error("❌ CHƯA CÓ API KEY")

indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu Kỹ thuật.")
st.markdown(f"**Trạng thái:** Hệ thống đang hoạt động ổn định.")

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("⚙️ Dữ liệu đầu vào")
    with st.expander("Dữ liệu thô"):
        st.code(indicator_data, language="text")

with c2:
    st.subheader("🤖 AI Phân tích & Xuất Báo Cáo")
    if st.button("🚀 KÍCH HOẠT PHÂN TÍCH", type="primary", use_container_width=True):
        if not model:
            st.error("❌ Lỗi kết nối AI. Kiểm tra Secrets.")
        else:
            with st.spinner("🧠 AI đang lập báo cáo chuyên sâu..."):
                try:
                    # Gửi prompt cho AI
                    prompt = f"Phân tích dữ liệu kỹ thuật: {indicator_data}. Đưa ra đánh giá xu hướng và kế hoạch hành động giao dịch chuyên nghiệp cho XAU/USD. Format Markdown."
                    response = model.generate_content(prompt)
                    st.session_state['ai_report'] = response.text
                    st.success("✅ Phân tích xong!")
                except Exception as e:
                    st.error(f"❌ Lỗi AI: {e}")

    # Xuất file PDF sau khi có báo cáo
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
