import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Module Chỉ Báo", layout="wide")
st.title("⚙️ Engine Phân Tích Chỉ Báo (Chạy ngầm)")

@st.cache_data(ttl=300)
def get_data():
    # Lấy dữ liệu Vàng
    df = yf.download("GC=F", period="5d", interval="30m")
    return df

df = get_data()

if df.empty:
    st.error("Không tải được dữ liệu.")
else:
    # ---------------------------------------------------------
    # TÍNH TOÁN NGẦM BẰNG PANDAS GỐC (Siêu nhẹ, không sợ lỗi)
    # ---------------------------------------------------------
    
    # 1. Tính Volume SMA (Trung bình 20 phiên)
    df['Vol_SMA'] = df['Volume'].rolling(window=20).mean()
    
    # 2. Tính Spread (Biên độ nến cho VSA)
    df['Spread'] = df['High'] - df['Low']
    
    # 3. Tính RSI (14) theo công thức chuẩn của Wilder
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    
    avg_gain = gain.ewm(com=13, adjust=False).mean()
    avg_loss = loss.ewm(com=13, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # ---------------------------------------------------------
    # TRÍCH XUẤT DỮ LIỆU GỬI CHO AI
    # ---------------------------------------------------------
    current_candle = df.iloc[-1]
    
    rsi_val = current_candle['RSI']
    vol_val = current_candle['Volume']
    vol_sma = current_candle['Vol_SMA']
    
    # Logic diễn giải
    rsi_status = "Quá mua" if rsi_val > 70 else "Quá bán" if rsi_val < 30 else "Trung tính"
    vol_status = "Khối lượng cao" if vol_val > vol_sma * 1.5 else "Trung bình"
    
    # Đóng gói thành Text
    indicator_summary = f"""
    - Giá đóng cửa nến M30 hiện tại: {current_candle['Close']:.2f}
    - RSI (14): {rsi_val:.2f} ({rsi_status})
    - Khối lượng: {vol_val:.0f} (Trung bình 20 nến: {vol_sma:.0f}) -> {vol_status}
    - Biên độ (Spread): {current_candle['Spread']:.2f}
    """
    
    # Lưu vào bộ nhớ để Trang chính lấy đọc
    st.session_state['tech_indicators'] = indicator_summary
    
    # Hiển thị cho chúng ta kiểm tra
    st.success("✅ Dữ liệu đã tính toán xong bằng Pandas gốc và gửi ra Trang Chính!")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("RSI (14)", f"{rsi_val:.2f}")
    col2.metric("Volume", f"{vol_val:.0f}")
    col3.metric("Spread", f"{current_candle['Spread']:.2f}")
