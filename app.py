import streamlit as st
import google.generativeai as genai

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
# 1. CẤU HÌNH AI & TRẠNG THÁI
# ==========================================================
st.sidebar.title("🔑 Cấu hình AI (Gemini)")
user_api_key = st.sidebar.text_input("Nhập Gemini API Key:", type="password", help="Dán API Key lấy từ Google AI Studio")

if user_api_key:
    try:
        genai.configure(api_key=user_api_key)
        # Sử dụng model Flash ổn định nhất
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.sidebar.success("✅ Đã kết nối não AI!")
    except Exception as e:
        model = None
        st.sidebar.error("❌ Lỗi cấu hình AI.")
else:
    model = None
    st.sidebar.warning("⚠️ Nhập API Key để kích hoạt AI.")

st.sidebar.markdown("---")
st.sidebar.title("📡 System Status")

indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu Kỹ thuật.")
live_price = st.session_state.get('current_price', 0.0)
fed_news_data = st.session_state.get('fed_news', "Chưa có dữ liệu tin tức FED.")

if "⚠️" in indicator_data:
    st.sidebar.warning("Kỹ thuật: Chờ dữ liệu")
else:
    st.sidebar.success(f"✅ Giá: {live_price:,.2f}")
    st.sidebar.success("✅ Kỹ thuật: ONLINE")
    
if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state["logged_in"] = False
    st.rerun()

# ==========================================================
# 2. BẢNG ĐIỀU KHIỂN & PHÂN TÍCH AI
# ==========================================================
st.title("⚡ Quant Trading Hub - AI Strategist")
st.markdown(f"**Mã theo dõi:** XAU/USD | **Giá hiện tại:** `{live_price:,.2f}`")
st.markdown("---")

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("⚙️ Chọn Module Phân Tích")
    analysis_mode = st.selectbox(
        "🧠 Bạn muốn AI tập trung vào nguồn dữ liệu nào?",
        [
            "1. Phân tích Kỹ thuật (Chỉ báo VZO, CMF, MACD...)",
            "2. Phân tích Vĩ mô (Đọc tin FED, Lãi suất)",
            "3. Tổng hợp Toàn diện (Kỹ thuật + Vĩ mô)"
        ]
    )
    
    with st.expander("Dữ liệu thô đầu vào"):
        st.code(indicator_data, language="text")

with c2:
    st.subheader("🤖 Phân Tích & Xuất Báo Cáo")
    
    if st.button("🚀 KÍCH HOẠT AI PHÂN TÍCH", use_container_width=True, type="primary"):
        if model is None:
            st.error("❌ Bạn chưa nhập API Key hợp lệ!")
        else:
            with st.spinner("🧠 AI đang âm thầm lập kế hoạch..."):
                data_to_analyze = f"Dữ liệu Kỹ thuật: {indicator_data}\n Dữ liệu Vĩ mô: {fed_news_data}"
                
                system_prompt = f"""
                Bạn là một Giám đốc Đầu tư (Quant Strategist). 
                Dựa trên dữ liệu: {data_to_analyze}.
                Hãy đưa ra báo cáo chi tiết:
                1. Đánh giá dòng tiền và xu hướng.
                2. Phân tích tác động vĩ mô (nếu có).
                3. Dự báo xu hướng và KẾ HOẠCH GIAO DỊCH (BUY/SELL/WAIT).
                Format: Báo cáo chuyên nghiệp bằng Markdown.
                """
                
                try:
                    response = model.generate_content(system_prompt)
                    # Lưu vào session để xuất file, không in ra màn hình
                    st.session_state['ai_report'] = response.text
                    st.success("✅ AI đã hoàn tất phân tích! Bạn có thể tải báo cáo bên dưới.")
                except Exception as e:
                    st.error(f"❌ Lỗi AI: {e}")

    # Chỉ hiển thị nút Tải về khi có báo cáo
    if 'ai_report' in st.session_state:
        st.download_button(
            label="📄 TẢI BÁO CÁO PHÂN TÍCH (.md)",
            data=st.session_state['ai_report'],
            file_name="Bao_Cao_Giao_Dich.md",
            mime="text/markdown",
            use_container_width=True
        )
