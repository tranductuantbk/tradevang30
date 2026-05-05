import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf

st.set_page_config(page_title="Module Chỉ Báo", layout="wide")
st.title("⚙️ Engine Phân Tích Chỉ Báo (Chạy ngầm)")

@st.cache_data(ttl=300)
def get_data():
    df = yf.download("GC=F", period="5d", interval="30m")
    return df

df = get_data()

if df.empty:
    st.error("Không tải được dữ liệu.")
else:
    # Tính toán ngầm
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['Vol_SMA'] = ta.sma(df['Volume'], length=20)
    df['Spread'] = df['High'] - df['Low']
    
    current_candle = df.iloc[-1]
    
    # Tạo ngữ nghĩa
    rsi_val = current_candle['RSI']
    vol_val = current_candle['Volume']
    vol_sma = current_candle['Vol_SMA']
    
    rsi_status = "Quá mua" if rsi_val > 70 else "Quá bán" if rsi_val < 30 else "Trung tính"
    vol_status = "Khối lượng cao" if vol_val > vol_sma * 1.5 else "Trung bình"
    
    # Gói dữ liệu gửi ra ngoài
    indicator_summary = f"""
    - Giá đóng cửa nến hiện tại: {current_candle['Close']:.2f}
    - RSI (14): {rsi_val:.2f} ({rsi_status})
    - Khối lượng: {vol_val:.0f} (Trung bình 20 nến: {vol_sma:.0f}) -> {vol_status}
    - Biên độ (Spread): {current_candle['Spread']:.2f}
    """
    
    # LƯU VÀO SESSION STATE
    st.session_state['tech_indicators'] = indicator_summary
    
    st.success("✅ Dữ liệu đã được tính toán ngầm và gửi ra Trang Chính cho AI.")
    
    # Hiển thị nhanh
    col1, col2 = st.columns(2)
    col1.metric("RSI", f"{rsi_val:.2f}")
    col2.metric("Volume", f"{vol_val:.0f}")
