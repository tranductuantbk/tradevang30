import streamlit as st
import google.generativeai as genai

# ==========================================================
# 1. CẤU HÌNH (ĐIỀN KEY CỦA BẠN VÀO ĐÂY)
# ==========================================================
MY_API_KEY = "AIzaSyAq9jRLwgdLgMoF8M1_h2Q0It5RHyceg7w" 

st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 2. KHỞI TẠO AI (CƠ CHẾ TỰ DÒ TÌM - CHỐNG LỖI 404)
# ==========================================================
model = None
try:
    genai.configure(api_key=MY_API_KEY)
    # Tự động lấy danh sách model và chọn model phù hợp nhất
    models = genai.list_models()
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            # Ưu tiên tìm Flash hoặc Pro
            if 'gemini-1.5-flash' in m.name or 'gemini-1.5-pro' in m.name:
                model = genai.GenerativeModel(m.name)
                break
    # Nếu không tìm thấy bằng vòng lặp, thử gọi mặc định
    if model is None:
        model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Lỗi cấu hình AI: {e}")

# ==========================================================
# 3. BẢO MẬT & TRẠNG THÁI
# ==========================================================
SECRET_PASSWORD = "tbk1102"
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.title("🔒 Security Portal")
        pwd = st.text_input("Nhập mật khẩu:", type="password")
        if st.button("Truy cập"):
            if pwd == SECRET_PASSWORD:
                st.session_state["logged_in"] = True
                st.rerun()
            else: st.error("Sai mật khẩu!")
    st.stop()

# Thanh bên
st.sidebar.title("📡 System Status")
if model: st.sidebar.success("✅ AI ĐÃ KẾT NỐI")
else: st.sidebar.error("❌ AI CHƯA SẴN SÀNG")

indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu Kỹ thuật.")
live_price = st.session_state.get('current_price', 0.0)
fed_news_data = st.session_state.get('fed_news', "Chưa có dữ liệu tin tức FED.")

if "⚠️" not in indicator_data:
    st.sidebar.success(f"✅ Giá: {live_price:,.2f}")
    st.sidebar.success("✅ Kỹ thuật: ONLINE")
    
if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state["logged_in"] = False
    st.rerun()

# ==========================================================
# 4. GIAO DIỆN CHÍNH
# ==========================================================
st.title("⚡ Quant Trading Hub")
c1, c2 = st.columns([1, 1])

with c1:
    analysis_mode = st.selectbox("🧠 Nguồn dữ liệu:", ["1. Phân tích Kỹ thuật", "2. Phân tích Vĩ mô", "3. Tổng hợp Toàn diện"])
    with st.expander("Dữ liệu thô"):
        st.code(indicator_data, language="text")

with c2:
    st.subheader("🤖 Phân Tích & Xuất Báo Cáo")
    if st.button("🚀 KÍCH HOẠT AI PHÂN TÍCH", use_container_width=True, type="primary"):
        if model is None:
            st.error("❌ Hệ thống chưa tìm thấy Model AI khả dụng. Kiểm tra lại API Key.")
        else:
            with st.spinner("🧠 AI đang làm việc..."):
                try:
                    system_prompt = f"Bạn là Giám đốc Đầu tư. Dữ liệu: {indicator_data}. Hãy viết báo cáo chuyên nghiệp gồm: Đánh giá dòng tiền, Phân tích vĩ mô, Dự báo, và Kế hoạch giao dịch cụ thể."
                    response = model.generate_content(system_prompt)
                    st.session_state['ai_report'] = response.text
                    st.success("✅ Phân tích hoàn tất!")
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")

    # Nút tải chỉ hiện khi AI đã phân tích thành công
    if 'ai_report' in st.session_state:
        st.download_button(
            label="📄 TẢI BÁO CÁO PHÂN TÍCH (.md)",
            data=st.session_state['ai_report'],
            file_name="Bao_Cao_Giao_Dich.md",
            mime="text/markdown",
            use_container_width=True
        )
