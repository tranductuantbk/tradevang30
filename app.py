import streamlit as st
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="Quang Quant Hub", page_icon="⚡")

# ==========================================================
# 0. BẢO MẬT & KẾT NỐI API AI (GEMINI)
# ==========================================================
SECRET_PASSWORD = "tbk1102"

# 🔴 QUAN TRỌNG: Lắp API Key của bạn vào giữa 2 dấu ngoặc kép ở dưới
GEMINI_API_KEY = "AIzaSyAq9jRLwgdLgMoF8M1_h2Q0It5RHyceg7w" 

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

# Cấu hình AI (ĐÃ FIX LỖI 404 - Dùng bản Pro ổn định nhất)
if GEMINI_API_KEY != "AIzaSyAq9jRLwgdLgMoF8M1_h2Q0It5RHyceg7w":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    model = None

# ==========================================================
# 1. SIDEBAR TRẠNG THÁI
# ==========================================================
st.sidebar.title("📡 System Status")
indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu Kỹ thuật. Vui lòng mở trang '1_Chi_bao'.")
live_price = st.session_state.get('current_price', 0.0)

# Dữ liệu chờ cho module cào tin tức tự động (Sẽ phát triển sau)
fed_news_data = st.session_state.get('fed_news', "Chưa có dữ liệu tin tức FED. (Module đang được xây dựng)")

if "⚠️" in indicator_data:
    st.sidebar.warning(indicator_data)
else:
    st.sidebar.success(f"✅ Dữ liệu Giá: {live_price:,.2f}")
    st.sidebar.success("✅ Module Kỹ thuật: ONLINE")
    
if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state["logged_in"] = False
    st.rerun()

# ==========================================================
# 2. BẢNG ĐIỀU KHIỂN CHÍNH & AI STRATEGIST
# ==========================================================
st.title("⚡ Quant Trading Hub - AI Strategist")
st.markdown(f"**Mã theo dõi:** XAU/USD | **Giá hiện tại:** `{live_price:,.2f}`")
st.markdown("---")

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("⚙️ Chọn Module Phân Tích")
    
    # Xổ ra các tuỳ chọn Module cho AI
    analysis_mode = st.selectbox(
        "🧠 Bạn muốn AI tập trung vào nguồn dữ liệu nào?",
        [
            "1. Phân tích Kỹ thuật (Chỉ báo VZO, CMF, MACD...)",
            "2. Phân tích Vĩ mô (Đọc tin FED, Lãi suất)",
            "3. Tổng hợp Toàn diện (Kỹ thuật + Vĩ mô)"
        ]
    )
    
    st.markdown("**Dữ liệu thô đang có:**")
    with st.expander("Hiển thị dữ liệu Kỹ Thuật"):
        st.code(indicator_data, language="text")
    with st.expander("Hiển thị dữ liệu Vĩ Mô (FED)"):
        st.code(fed_news_data, language="text")

with c2:
    st.subheader("🤖 Phân Tích & Kế Hoạch Giao Dịch")
    
    if st.button("🚀 KÍCH HOẠT AI PHÂN TÍCH", use_container_width=True, type="primary"):
        if model is None:
            st.error("❌ Bạn chưa điền GEMINI_API_KEY vào code (Dòng 11). Hãy lấy API Key để AI hoạt động.")
        elif "⚠️" in indicator_data and "1" in analysis_mode:
            st.warning("⚠️ Chưa có dữ liệu Kỹ thuật để phân tích. Hãy qua trang Chỉ báo mở lên trước.")
        else:
            with st.spinner("AI đang xử lý dữ liệu và lập kế hoạch..."):
                # Gom dữ liệu để nhét vào não AI
                data_to_analyze = ""
                if "1" in analysis_mode:
                    data_to_analyze += f"\n--- DỮ LIỆU KỸ THUẬT ---\n{indicator_data}\n"
                elif "2" in analysis_mode:
                    data_to_analyze += f"\n--- DỮ LIỆU VĨ MÔ (FED) ---\n{fed_news_data}\n"
                else:
                    data_to_analyze += f"\n--- DỮ LIỆU KỸ THUẬT ---\n{indicator_data}\n--- DỮ LIỆU VĨ MÔ (FED) ---\n{fed_news_data}\n"

                # Lệnh System Prompt ép AI đóng vai Giám đốc Quỹ
                system_prompt = f"""
                Bạn là một Giám đốc Đầu tư (Quant Strategist) tại một quỹ Hedge Fund chuyên giao dịch XAU/USD.
                Giá hiện tại là: {live_price}.
                
                Dưới đây là các dữ liệu hệ thống báo về:
                {data_to_analyze}
                
                Nhiệm vụ của bạn:
                1. Tóm tắt tình hình thị trường (Dòng tiền đang vào hay ra? Lực Mua/Bán phe nào áp đảo?).
                2. Nếu có dữ liệu FED, đánh giá tác động của nó đến Vàng (Hawkish/Dovish).
                3. Đưa ra DỰ BÁO XU HƯỚNG SẮP TỚI.
                4. Đưa ra KẾ HOẠCH GIAO DỊCH RÕ RÀNG (Ưu tiên BUY, SELL hay Đứng ngoài? Đợi tín hiệu gì tiếp theo?).
                
                Hãy trả lời súc tích, chuyên nghiệp, format rõ ràng bằng Markdown, không dùng từ ngữ chung chung.
                """
                
                try:
                    response = model.generate_content(system_prompt)
                    st.success("✅ Phân tích hoàn tất!")
                    st.markdown("### 📋 BÁO CÁO TỪ AI STRATEGIST")
                    st.info(response.text)
                except Exception as e:
                    st.error(f"❌ Lỗi kết nối AI: {e}")

st.markdown("---")

# ==========================================================
# 3. MÁY TÍNH VÀO LỆNH
# ==========================================================
st.subheader("⚡ Máy Tính Vào Lệnh")
entry_col, sl_col, tp_col = st.columns(3)

with entry_col: 
    entry_price = st.number_input("Giá Entry", value=float(live_price), step=0.1, format="%.2f")
with sl_col: 
    st.number_input("Giá Stoploss (Dự kiến -5 giá)", value=float(live_price - 5), step=0.1, format="%.2f")
with tp_col: 
    st.number_input("Giá Take Profit (Dự kiến +15 giá)", value=float(live_price + 15), step=0.1, format="%.2f")

st.caption("Cài đặt giá SL/TP dựa trên kế hoạch giao dịch AI vừa đề xuất ở trên.")
