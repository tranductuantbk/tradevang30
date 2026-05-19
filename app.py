import streamlit as st
import google.generativeai as genai

# ==========================================================
# 1. CẤU HÌNH CỨNG (ĐIỀN KEY CỦA BẠN VÀO ĐÂY)
# ==========================================================
MY_API_KEY = "AIzaSyAq9jRLwgdLgMoF8M1_h2Q0It5RHyceg7w" 

st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 2. KHỞI TẠO VÀ KIỂM TRA KẾT NỐI AI (BỘ PHẬN MỚI)
# ==========================================================
model = None
connection_error = None

try:
    genai.configure(api_key=MY_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    connection_error = str(e)

# ==========================================================
# 3. BẢO MẬT HỆ THỐNG
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
# 4. THANH TRẠNG THÁI (ĐÈN BÁO KẾT NỐI)
# ==========================================================
st.sidebar.title("📡 System Status")

# Hiển thị đèn báo AI
if model is not None:
    st.sidebar.success("✅ AI ĐÃ KẾT NỐI")
else:
    st.sidebar.error(f"❌ LỖI AI: {connection_error}")

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
# 5. BẢNG ĐIỀU KHIỂN CHÍNH
# ==========================================================
st.title("⚡ Quant Trading Hub - AI Strategist")
st.markdown(f"**Mã theo dõi:** XAU/USD | **Giá hiện tại:** `{live_price:,.2f}`")
st.markdown("---")

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("⚙️ Chọn Module Phân Tích")
    analysis_mode = st.selectbox("🧠 Nguồn dữ liệu:", ["1. Phân tích Kỹ thuật", "2. Phân tích Vĩ mô", "3. Tổng hợp Toàn diện"])
    with st.expander("Dữ liệu thô"):
        st.code(indicator_data, language="text")

with c2:
    st.subheader("🤖 Phân Tích AI")
    
    if st.button("🚀 KÍCH HOẠT AI PHÂN TÍCH", use_container_width=True, type="primary"):
        if model is None:
            st.error("❌ Không thể kết nối AI. Kiểm tra đèn báo ở thanh bên!")
        else:
            with st.spinner("🧠 AI đang âm thầm lập báo cáo..."):
                data_to_analyze = f"Kỹ thuật: {indicator_data}\nVĩ mô: {fed_news_data}"
                system_prompt = f"Bạn là Giám đốc Đầu tư. Dựa trên dữ liệu: {data_to_analyze}. Hãy viết báo cáo: 1. Đánh giá dòng tiền. 2. Tác động vĩ mô. 3. Dự báo xu hướng. 4. Kế hoạch hành động (BUY/SELL/WAIT). Format Markdown."
                
                try:
                    response = model.generate_content(system_prompt)
                    st.session_state['ai_report'] = response.text
                    st.success("✅ Phân tích hoàn tất!")
                except Exception as e:
                    st.error(f"❌ Lỗi khi gọi AI: {e}")

    # Xuất file báo cáo
    if 'ai_report' in st.session_state:
        st.download_button(
            label="📄 TẢI BÁO CÁO PHÂN TÍCH (.md)",
            data=st.session_state['ai_report'],
            file_name="Bao_Cao_Giao_Dich.md",
            mime="text/markdown",
            use_container_width=True
        )
