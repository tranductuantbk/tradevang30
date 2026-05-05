import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf # Dùng tạm để lấy dữ liệu test, sau này thay bằng API của bạn

st.set_page_config(page_title="Module Chỉ Báo", layout="wide")

st.title("⚙️ Engine Phân Tích Chỉ Báo (Chạy ngầm)")
st.markdown("---")

# 1. HÀM LẤY DỮ LIỆU (Chạy ngầm)
@st.cache_data(ttl=300) # Cache dữ liệu 5 phút để tránh load lại liên tục
def get_data():
    # Lấy dữ liệu vàng (GC=F là mã Gold Futures trên Yahoo Finance)
    df = yf.download("GC=F", period="5d", interval="30m")
    return df

df = get_data()

if df.empty:
    st.error("Không tải được dữ liệu. Vui lòng kiểm tra lại API.")
else:
    # ---------------------------------------------------------
    # 2. KHU VỰC CHÉP CODE CHỈ BÁO (TÍNH TOÁN NGẦM)
    # ---------------------------------------------------------
    
    # Tính RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # Tính Volume Trung bình (để so sánh VSA)
    df['Vol_SMA'] = ta.sma(df['Volume'], length=20)
    
    # Tính Spread (Biên độ nến) cho VSA
    df['Spread'] = df['High'] - df['Low']
    
    # (Bạn có thể dán thêm các logic phức tạp của mình ở đây)
    # Ví dụ: df['Z_Score'] = ... 
    
    # Lấy dòng dữ liệu nến hiện tại (nến gần nhất)
    current_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]

    # ---------------------------------------------------------
    # 3. TRÍCH XUẤT NGỮ NGHĨA & LƯU VÀO SESSION STATE CHO AI
    # ---------------------------------------------------------
    
    # Đánh giá RSI
    rsi_val = current_candle['RSI']
    if rsi_val > 70:
        rsi_status = "Quá mua (Overbought) - Cẩn trọng đảo chiều giảm."
    elif rsi_val < 30:
        rsi_status = "Quá bán (Oversold) - Chờ tín hiệu hấp thụ để mua."
    else:
        rsi_status = "Trung tính."

    # Đánh giá Volume (Logic VSA cơ bản)
    vol_val = current_candle['Volume']
    vol_sma = current_candle['Vol_SMA']
    if vol_val > vol_sma * 1.5:
        vol_status = "Khối lượng siêu cao (Climax/Stopping Volume) - Có dấu chân dòng tiền lớn."
    elif vol_val < vol_sma * 0.5:
        vol_status = "Khối lượng cạn kiệt (No Demand/No Supply) - Dòng tiền lớn đứng ngoài."
    else:
        vol_status = "Khối lượng trung bình."

    # Gói gọn dữ liệu để gửi lên Trang Chính (app.py) cho AI đọc
    indicator_summary = f"""
    - RSI (14): {rsi_val:.2f} ({rsi_status})
    - Khối lượng: {vol_val:.0f} (Trung bình 20 nến: {vol_sma:.0f}) -> {vol_status}
    - Spread (Biên độ nến): {current_candle['Spread']:.2f}
    """
    
    # LƯU VÀO BỘ NHỚ CHUNG (Critical Step)
    st.session_state['tech_indicators'] = indicator_summary

    # ---------------------------------------------------------
    # 4. HIỂN THỊ GIAO DIỆN DIỄN GIẢI (Không vẽ biểu đồ)
    # ---------------------------------------------------------
    
    st.subheader("📊 Trạng thái Chỉ báo Hiện tại (Nến M30)")
    
    # Hiển thị bằng các metric card sạch sẽ
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="RSI (14)", value=f"{rsi_val:.2f}", 
                  delta="Overbought" if rsi_val > 70 else "Oversold" if rsi_val < 30 else "Neutral",
                  delta_color="inverse")
        st.caption(rsi_status)
        
    with col2:
        st.metric(label="Volume M30", value=f"{vol_val:.0f}", 
                  delta=f"{(vol_val/vol_sma)*100 - 100:.1f}% so với MA20")
        st.caption(vol_status)
        
    with col3:
        st.metric(label="Biên độ nến (Spread)", value=f"{current_candle['Spread']:.2f}")
        st.caption("Dùng để đối chiếu với Volume trong VSA.")

    st.markdown("---")
    st.success("✅ Dữ liệu đã được tính toán ngầm và sẵn sàng gửi cho AI Strategist tại Trang Chính.")
    
    # (Tùy chọn) Hiển thị Dataframe dạng bảng rút gọn để kiểm tra chéo
    with st.expander("Xem dữ liệu thô (5 nến gần nhất)"):
        st.dataframe(df.tail(5)[['Open', 'High', 'Low', 'Close', 'Volume', 'RSI']])