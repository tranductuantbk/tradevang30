import streamlit as st

# ==========================================================
# CẤU HÌNH TRANG
# ==========================================================
st.set_page_config(layout="wide", page_title="Quant Trading Hub", page_icon="⚡")

st.title("⚡ Quant Trading Hub - Bảng Điều Khiển Tín Hiệu")
st.markdown("---")

c1, c2 = st.columns([1, 1.2])

with c1:
    st.subheader("⚙️ 1. Nguồn Dữ Liệu Chỉ Báo")
    
    # Tự động lấy dữ liệu từ trang 1_Chi_bao.py (nếu bạn đang chạy bên đó)
    auto_data = st.session_state.get('tech_indicators', '')
    
    indicator_data = st.text_area(
        "📝 Dữ liệu hiện tại (Tự động đồng bộ hoặc bạn có thể nhập tay):", 
        value=auto_data, 
        height=200,
        help="Ví dụ: SQZ PRO: QUÁ MUA\nOBV MACD: CẠN BÁN"
    )
    
    analyze_btn = st.button("🚀 ĐỌC TRẠNG THÁI HIỆN TẠI", type="primary", use_container_width=True)

with c2:
    st.subheader("📋 Trạng Thái Biểu Đồ Thực Tế")
    
    if analyze_btn or indicator_data:
        with st.container(border=True):
            if not indicator_data.strip():
                st.warning("Chưa có dữ liệu. Vui lòng bật các chỉ báo bên trang biểu đồ hoặc nhập dữ liệu vào ô bên trái.")
            else:
                st.markdown("### 📊 Chi tiết Tín hiệu")
                lines = indicator_data.split('\n')
                
                buy_count = 0
                sell_count = 0
                
                # Vòng lặp đọc "như thế nào thể hiện thế đó"
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    text_upper = line.upper()
                    # Quét từ khóa để tô màu hiển thị
                    if any(kw in text_upper for kw in ["MUA", "CẠN CUNG", "QUÁ BÁN", "TĂNG"]):
                        st.success(f"🟢 **{line}**")
                        buy_count += 1
                    elif any(kw in text_upper for kw in ["BÁN", "CẠN CẦU", "QUÁ MUA", "GIẢM"]):
                        st.error(f"🔴 **{line}**")
                        sell_count += 1
                    else:
                        st.info(f"⚪ **{line}**")
                        
                st.markdown("---")
                st.markdown("### 🎯 Kết luận chung")
                
                # Tổng hợp trạng thái
                if buy_count > sell_count:
                    st.success(f"🔥 **ƯU TIÊN TÌM ĐIỂM MUA** (Có {buy_count} tín hiệu ủng hộ MUA / {sell_count} tín hiệu BÁN)")
                elif sell_count > buy_count:
                    st.error(f"🩸 **ƯU TIÊN TÌM ĐIỂM BÁN** (Có {sell_count} tín hiệu ủng hộ BÁN / {buy_count} tín hiệu MUA)")
                elif buy_count == 0 and sell_count == 0:
                    st.info("🔎 **CHƯA CÓ TÍN HIỆU ĐẢO CHIỀU** - Giá đang chạy theo xu hướng cũ hoặc đi ngang.")
                else:
                    st.warning(f"⚖️ **TÍN HIỆU XUNG ĐỘT (TRUNG TÍNH)** - Tỉ lệ MUA/BÁN đang là {buy_count}/{sell_count}. Nên đứng ngoài quan sát thêm.")
    else:
        st.markdown("👈 *Dữ liệu sẽ hiển thị trực tiếp tại đây mà không cần chờ AI phân tích.*")
