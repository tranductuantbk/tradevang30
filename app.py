import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# ==========================================================
# 1. ĐỊNH NGHĨA MODULE VĨ MÔ (Gộp vào đây để không bị lỗi import)
# ==========================================================
class MacroAnalyzer:
    def __init__(self):
        self.factors = {"FED_Rate": "Neutral", "Geopolitics": "Stable", "USD_DXY": 105.0}

    def render_ui(self):
        st.subheader("🌍 Macro Intel Module")
        c1, c2, c3 = st.columns(3)
        with c1: self.factors["FED_Rate"] = st.selectbox("Xu hướng FED:", ["Hawkish", "Dovish", "Neutral"])
        with c2: self.factors["Geopolitics"] = st.selectbox("Căng thẳng ĐC:", ["High Tension", "Stable", "War Risk"])
        with c3: self.factors["USD_DXY"] = st.number_input("Giá trị DXY:", value=105.0, step=0.1)
        return self.factors

    def get_summary(self):
        return f"- FED: {self.factors['FED_Rate']}, ĐC: {self.factors['Geopolitics']}, DXY: {self.factors['USD_DXY']}"

# ==========================================================
# 2. CẤU HÌNH & KHỞI TẠO
# ==========================================================
st.set_page_config(layout="wide", page_title="Quant Trading Hub", page_icon="⚡")
macro_engine = MacroAnalyzer() # Khởi tạo module ngay tại đây

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, txt=text)
    return pdf.output()

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
    indicator_data = st.text_area("Nhập dữ liệu kỹ thuật:", height=100)
    # Hiển thị UI của module vĩ mô ngay tại đây
    macro_engine.render_ui()
    
    if st.button("🚀 KÍCH HOẠT PHÂN TÍCH", type="primary"):
        if not model:
            st.error("❌ Lỗi kết nối AI.")
        else:
            with st.spinner("🧠 AI đang lập báo cáo..."):
                macro_summary = macro_engine.get_summary()
                prompt = f"Phân tích kỹ thuật: {indicator_data}. Dữ liệu vĩ mô: {macro_summary}. Hãy đưa ra kế hoạch giao dịch chuyên nghiệp cho XAU/USD bằng tiếng Việt."
                response = model.generate_content(prompt)
                st.session_state['ai_report'] = response.text
                st.success("✅ Phân tích xong!")

with c2:
    st.subheader("📋 Kết quả")
    if 'ai_report' in st.session_state:
        st.markdown(st.session_state['ai_report'])
        pdf_bytes = create_pdf(st.session_state['ai_report'])
        st.download_button("📄 TẢI BÁO CÁO PDF", data=pdf_bytes, file_name="Bao_Cao_Trading.pdf", mime="application/pdf", use_container_width=True)
