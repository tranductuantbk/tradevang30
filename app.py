import streamlit as st
import google.generativeai as genai

# ==========================================================
# 1. ĐỊNH NGHĨA MODULE VĨ MÔ
# ==========================================================
class MacroAnalyzer:
    def __init__(self):
        self.factors = {"FED_Rate": "Neutral", "Geopolitics": "Stable", "USD_DXY": 105.0}

    def render_ui(self):
        st.markdown("**🌍 Tùy chỉnh Dữ liệu Vĩ mô (Tùy chọn)**")
        c1, c2, c3 = st.columns(3)
        with c1: self.factors["FED_Rate"] = st.selectbox("Xu hướng FED:", ["Hawkish", "Dovish", "Neutral"])
        with c2: self.factors["Geopolitics"] = st.selectbox("Căng thẳng ĐC:", ["High Tension", "Stable", "War Risk"])
        with c3: self.factors["USD_DXY"] = st.number_input("Giá trị DXY:", value=105.0, step=0.1)
        return self.factors

    def get_summary(self):
        return f"- Chính sách FED: {self.factors['FED_Rate']}, Địa chính trị: {self.factors['Geopolitics']}, Chỉ số DXY: {self.factors['USD_DXY']}"

# ==========================================================
# 2. CẤU HÌNH TRANG & API KHỞI TẠO
# ==========================================================
st.set_page_config(layout="wide", page_title="Quant Trading Hub", page_icon="⚡")
macro_engine = MacroAnalyzer() 

# ==========================================================
# 3. GIAO DIỆN CHÍNH
# ==========================================================
st.title("⚡ Quant Trading Hub - AI Strategist")
st.markdown("---")

c1, c2 = st.columns([1, 1.2])

with c1:
    # --- BƯỚC 1: CHỌN DỮ LIỆU ĐẦU VÀO ---
    st.subheader("⚙️ 1. Chọn Dữ liệu Đầu vào")
    
    data_type = st.selectbox("Loại dữ liệu bạn muốn AI phân tích:", 
        ["Dữ liệu Chỉ báo (Technical)", "Dữ liệu Vĩ mô (Macro)", "Phân tích Toàn diện (Kỹ thuật + Vĩ mô)"])
    
    indicator_data = ""
    
    if "Chỉ báo" in data_type or "Toàn diện" in data_type:
        indicator_data = st.text_area("📝 Nhập dữ liệu/Tín hiệu Chỉ báo (VD: SQZ PRO báo MUA, OBV MACD tạo đáy...):", height=100)
        
    if "Vĩ mô" in data_type or "Toàn diện" in data_type:
        macro_engine.render_ui()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BƯỚC 2: CHỌN AI VÀ KÍCH HOẠT ---
    st.subheader("🤖 2. Chọn AI Phân tích")
    
    ai_choice = st.selectbox("Chọn bộ não AI:", ["Gemini 1.5 Flash (Xử lý Nhanh)", "Gemini 1.5 Pro (Suy luận Sâu)"])
    ticker = st.text_input("Mã giao dịch (Ticker):", value="XAU/USD")

    if st.button("🚀 YÊU CẦU AI PHÂN TÍCH NGAY", type="primary", use_container_width=True):
        try:
            genai.configure(api_key=st.secrets["API_KEY"])
            
            # --- VÁ LỖI MODEL Ở ĐÂY ---
            # Thêm '-latest' để tương thích với API v1beta
            target_model = 'gemini-1.5-pro-latest' if 'Pro' in ai_choice else 'gemini-1.5-flash-latest'
            
            prompt = f"Đóng vai là một chuyên gia giao dịch định lượng (Quant Trader). Hãy phân tích mã {ticker} dựa trên các dữ liệu sau:\n"
            if indicator_data:
                prompt += f"- Dữ liệu Kỹ thuật (Chỉ báo): {indicator_data}\n"
            if "Vĩ mô" in data_type or "Toàn diện" in data_type:
                prompt += f"- Dữ liệu Vĩ mô: {macro_engine.get_summary()}\n"
            prompt += "\nTừ các dữ liệu trên, hãy đưa ra nhận định thị trường và xây dựng một kế hoạch giao dịch chuyên nghiệp (bao gồm Điểm vào lệnh, Cắt lỗ, Chốt lời). Trình bày bằng tiếng Việt, chia các gạch đầu dòng rõ ràng."

            with st.spinner(f"🧠 {ai_choice} đang suy nghĩ..."):
                try:
                    model = genai.GenerativeModel(target_model)
                    response = model.generate_content(prompt)
                except Exception as model_err:
                    # Lớp bảo hiểm: Nếu key không hỗ trợ Pro, tự động lùi về Flash
                    st.warning(f"⚠️ API Key chưa hỗ trợ bản Pro ({model_err}). Tự động chuyển sang bản Flash...")
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    response = model.generate_content(prompt)
                
                st.session_state['ai_report'] = response.text
                st.session_state['analyzed_ticker'] = ticker
                st.success("✅ Phân tích hoàn tất! Hãy xem kết quả bên phải.")
                
        except Exception as e:
            st.error(f"❌ Lỗi hệ thống: {e}")

with c2:
    # --- BƯỚC 3: HIỂN THỊ KẾT QUẢ ---
    st.subheader("📋 Kết quả Phân tích từ AI")
    
    with st.container(border=True):
        if 'ai_report' in st.session_state:
            st.info(f"**📈 Kế hoạch giao dịch cho mã:** {st.session_state['analyzed_ticker']}")
            st.markdown(st.session_state['ai_report'])
        else:
            st.markdown("👈 *Hãy nhập dữ liệu ở cột bên trái, AI sẽ trả kết quả trực tiếp vào khung này!*")
