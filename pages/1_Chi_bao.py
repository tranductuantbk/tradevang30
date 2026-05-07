import streamlit as st
import pandas as pd
import yfinance as yf
import os
import importlib.util
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Module Chỉ Báo Tự Động", layout="wide")

# Tự động refresh sau mỗi 60 giây (60000ms)
st_autorefresh(interval=60000, key="chibao_refresh")

# =====================================================================
# 1. TỪ ĐIỂN KHUNG THỜI GIAN
# =====================================================================
tf_mapping = {
    "M15 (15 Phút)": {"interval": "15m", "period": "5d"},
    "M30 (30 Phút)": {"interval": "30m", "period": "5d"},
    "H1 (1 Giờ)": {"interval": "60m", "period": "1mo"},
    "D1 (1 Ngày)": {"interval": "1d", "period": "2y"}
}

st.title("⚙️ Trung tâm Quản lý Chỉ Báo Cá Nhân")

# Tạo giao diện nhập Mã và Khung thời gian
col_text, col_ticker, col_tf = st.columns([2, 1, 1])
with col_text:
    st.markdown("Hệ thống tự động quét và tính toán chỉ báo từ thư mục `custom_indicators`.")
with col_ticker:
    # Gắn ô nhập mã giao dịch (Mặc định là XAUUSD=X cho Vàng Giao ngay)
    selected_ticker = st.text_input("📈 Mã giao dịch (Yahoo Finance):", value="XAUUSD=X")
with col_tf:
    selected_tf_label = st.selectbox("⏳ Khung Thời Gian:", list(tf_mapping.keys()), index=1)

st.markdown("---")

# =====================================================================
# 2. HÀM TẢI DỮ LIỆU ĐỘNG (ĐÃ FIX LỖI "LÀM NÓNG" CHỈ BÁO)
# =====================================================================
selected_interval = tf_mapping[selected_tf_label]["interval"]

# Fix: Đổi từ 60d xuống 59d để lách luật giới hạn API của Yahoo Finance
if selected_interval in ["15m", "30m", "60m"]:
    fetch_period = "59d" 
else:
    fetch_period = tf_mapping[selected_tf_label]["period"]

@st.cache_data(ttl=60) # Cập nhật dữ liệu mới mỗi phút
def get_data(ticker, interval, period):
    return yf.download(ticker, period=period, interval=interval)

df = get_data(selected_ticker, selected_interval, fetch_period)

# =====================================================================
# 3. HỆ THỐNG RADAR QUÉT CHỈ BÁO
# =====================================================================
if not df.empty:
    col1, col2 = st.columns([1, 2])
    active_summaries = [] 
    
    with col1:
        st.subheader("🛠️ Kho Chỉ Báo Của Bạn")
        
        folder_path = "custom_indicators"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        indicator_files = [f for f in os.listdir(folder_path) if f.endswith('.py') and f != '__init__.py']
        
        if len(indicator_files) == 0:
            st.info(f"📂 Thư mục `{folder_path}` đang trống. Hãy thả các file code của bạn vào đây.")
        else:
            for file_name in indicator_files:
                module_name = file_name.replace('.py', '') 
                is_active = st.checkbox(f"Hoạt động: {module_name}", value=True)
                
                if is_active:
                    with col2:
                        try:
                            file_path = os.path.join(folder_path, file_name)
                            spec = importlib.util.spec_from_file_location(module_name, file_path)
                            custom_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(custom_module)
                            
                            result_text = custom_module.run_indicator(df)
                            st.success(f"✅ Đã chạy thành công: `{file_name}`")
                            active_summaries.append(result_text)
                            
                        except Exception as e:
                            st.error(f"❌ Lỗi code trong file `{file_name}`: {e}")

    st.markdown("---")
    st.subheader("🤖 Dữ liệu gói gửi AI Strategist")
    
    if len(active_summaries) > 0:
        # Gắn thêm nhãn KHUNG THỜI GIAN VÀ MÃ TÀI SẢN để AI biết chính xác
        final_summary = f"📊 [BỐI CẢNH MÃ {selected_ticker} - KHUNG {selected_tf_label}]\n" + "\n".join([f"- {text}" for text in active_summaries])
        st.info(final_summary)
        
        # Lưu dữ liệu vào hệ thống cho Trang Chính gọi ra
        st.session_state['tech_indicators'] = final_summary
    else:
        st.warning("Bạn chưa bật chỉ báo nào hoặc chưa có code thành công.")
        st.session_state['tech_indicators'] = "⚠️ Không có dữ liệu."
else:
    st.error(f"Không tải được dữ liệu cho mã '{selected_ticker}'. Vui lòng kiểm tra lại kết nối hoặc mã giao dịch bạn nhập.")
