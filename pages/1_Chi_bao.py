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

col_text, col_tf = st.columns([3, 1])
with col_text:
    st.markdown("Hệ thống tự động nhận diện các file code chỉ báo của bạn trong thư mục `custom_indicators`.")
with col_tf:
    selected_tf_label = st.selectbox("⏳ Khung Thời Gian:", list(tf_mapping.keys()), index=1)

st.markdown("---")

# =====================================================================
# 2. HÀM TẢI DỮ LIỆU ĐỘNG
# =====================================================================
selected_interval = tf_mapping[selected_tf_label]["interval"]
selected_period = tf_mapping[selected_tf_label]["period"]

@st.cache_data(ttl=60) # Rút ngắn cache xuống 60s để update liên tục
def get_data(interval, period):
    return yf.download("GC=F", period=period, interval=interval)

df = get_data(selected_interval, selected_period)

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
        final_summary = f"📊 [BỐI CẢNH KHUNG {selected_tf_label}]\n" + "\n".join([f"- {text}" for text in active_summaries])
        st.info(final_summary)
        st.session_state['tech_indicators'] = final_summary
    else:
        st.warning("Bạn chưa bật chỉ báo nào hoặc chưa có code thành công.")
        st.session_state['tech_indicators'] = "⚠️ Không có dữ liệu."
else:
    st.error("Không tải được dữ liệu từ Yahoo Finance. Vui lòng kiểm tra lại kết nối.")
