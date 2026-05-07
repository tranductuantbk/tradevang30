import streamlit as st
import pandas as pd
import yfinance as yf
import os
import importlib.util

st.set_page_config(page_title="Module Chỉ Báo Tự Động", layout="wide")

@st.cache_data(ttl=300)
def get_data():
    return yf.download("GC=F", period="5d", interval="30m")

df = get_data()

st.title("⚙️ Trung tâm Quản lý Chỉ Báo Cá Nhân")
st.markdown("Hệ thống tự động nhận diện các file code chỉ báo của bạn trong thư mục `custom_indicators`.")
st.markdown("---")

if not df.empty:
    col1, col2 = st.columns([1, 2])
    
    active_summaries = [] # Chứa các đoạn text để gửi cho AI
    
    with col1:
        st.subheader("🛠️ Kho Chỉ Báo Của Bạn")
        
        # --- THUẬT TOÁN QUÉT THƯ MỤC TỰ ĐỘNG ---
        folder_path = "custom_indicators"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path) # Tự tạo thư mục nếu chưa có
            
        # Tìm tất cả các file đuôi .py trong thư mục (trừ các file hệ thống)
        indicator_files = [f for f in os.listdir(folder_path) if f.endswith('.py') and f != '__init__.py']
        
        if len(indicator_files) == 0:
            st.info(f"📂 Thư mục `{folder_path}` đang trống. Hãy thả các file code của bạn vào đây.")
        else:
            st.write(f"Đã phát hiện **{len(indicator_files)}** chỉ báo độc quyền:")
            
            # Quét từng file và tạo Checkbox tự động
            for file_name in indicator_files:
                module_name = file_name.replace('.py', '') # Bỏ đuôi .py để làm tên
                
                # Tạo checkbox trên màn hình
                is_active = st.checkbox(f"Hoạt động: {module_name}", value=True)
                
                if is_active:
                    with col2:
                        try:
                            # Tải code của bạn lên và chạy ngầm
                            file_path = os.path.join(folder_path, file_name)
                            spec = importlib.util.spec_from_file_location(module_name, file_path)
                            custom_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(custom_module)
                            
                            # Gọi hàm run_indicator trong file của bạn
                            result_text = custom_module.run_indicator(df)
                            
                            st.success(f"✅ Đã chạy thành công: `{file_name}`")
                            active_summaries.append(result_text)
                            
                        except Exception as e:
                            st.error(f"❌ Lỗi code trong file `{file_name}`: {e}")

    st.markdown("---")
    st.subheader("🤖 Dữ liệu gói gửi AI Strategist")
    
    if len(active_summaries) > 0:
        final_summary = "\n".join([f"- {text}" for text in active_summaries])
        st.info(final_summary)
        
        # Gửi toàn bộ vào bộ nhớ cho Trang Chính (app.py) đọc
        st.session_state['tech_indicators'] = final_summary
    else:
        st.warning("Bạn chưa bật chỉ báo nào hoặc chưa có code thành công.")
        st.session_state['tech_indicators'] = "⚠️ Không có dữ liệu."
