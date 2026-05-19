import streamlit as st
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 1. CẤU HÌNH & KHỞI TẠO AI (DÒ TÌM TỰ ĐỘNG)
# ==========================================================
# Lấy key từ secrets
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    
    # --- TỰ ĐỘNG DÒ TÌM MODEL ---
    # Lấy danh sách tất cả model khả dụng
    all_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if all_models:
        # Chọn model đầu tiên tìm được
        model_name = all_models[0].name
        model = genai.GenerativeModel(model_name)
        st.sidebar.success(f"✅ Đã kết nối: {model_name}")
    else:
        model = None
        st.sidebar.error("❌ Không tìm thấy model nào hỗ trợ!")
        
except Exception as e:
    model = None
    st.sidebar.error(f"❌ Lỗi: {e}")

# ==========================================================
# 2. BẢO MẬT HỆ THỐNG
# ==========================================================
SECRET_PASSWORD = "tbk1102"
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    col_b = st.columns([1, 1, 1])[1]
    with col_b:
        st.title("🔒 Security Portal")
        pwd = st.text_input("Nhập mật khẩu:", type="password")
        if st.button("Truy cập"):
            if pwd == SECRET_PASSWORD:
                st.session_state["logged_in"] = True
                st.rerun()
            else: st.error("Sai mật khẩu!")
    st.stop()

# ==========================================================
# 3. GIAO DIỆN CHÍNH
# ==========================================================
st.title("⚡ Quant Trading Hub")

# Phần Debug: Hiển thị các model bạn đang có
with st.sidebar.expander("🛠️ Debug Model"):
    st.write("Các model khả dụng của bạn:")
    try:
        for m in all_models: st.write(f"- {m.name}")
    except: st.write("Chưa kết nối được.")

indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu.")

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("⚙️ Dữ liệu")
    with st.expander("Dữ liệu thô"):
        st.code(indicator_data, language="text")

with c2:
    st.subheader("🤖 Phân Tích & Xuất Báo Cáo")
    if st.button("🚀 KÍCH HOẠT AI PHÂN TÍCH", use_container_width=True, type="primary"):
        if not model:
            st.error("❌ Chưa kết nối được Model AI. Kiểm tra phần Debug ở Sidebar.")
        else:
            with st.spinner("🧠 AI đang lập báo cáo..."):
                try:
                    response = model.generate_content(f"Phân tích dữ liệu: {indicator_data}. Đưa ra kế hoạch hành động.")
                    st.session_state['ai_report'] = response.text
                    st.success("✅ Phân tích xong!")
                except Exception as e:
                    st.error(f"❌ Lỗi API: {e}")

    if 'ai_report' in st.session_state:
        st.download_button(
            label="📄 TẢI BÁO CÁO (.md)",
            data=st.session_state['ai_report'],
            file_name="Bao_Cao_Giao_Dich.md",
            mime="text/markdown",
            use_container_width=True
        )
