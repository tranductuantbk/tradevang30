import pandas as pd
import numpy as np

def run_indicator(df):
    """
    RSI Chart Bars [Glaz]
    Dịch từ Pine Script sang Python: Đọc màu nến dựa trên các vùng RSI (Quá mua/Quá bán).
    """
    d = df.copy()
    
    # Ép dữ liệu về 1 chiều (1D) để tránh lỗi Series
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    close = get_1d('Close')

    # 1. THÔNG SỐ CÀI ĐẶT
    length = 14
    upLevel = 70
    downLevel = 30

    # 2. TÍNH TOÁN RSI (Chuẩn RMA của TradingView)
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    # Hàm rma(x, y) của TradingView tương đương ewm(alpha=1/y) trong Pandas
    alpha = 1.0 / length
    rma_up = up.ewm(alpha=alpha, adjust=False).mean()
    rma_down = down.ewm(alpha=alpha, adjust=False).mean()
    
    # Tính RSI và xử lý các trường hợp ngoại lệ (chia cho 0)
    rs = rma_up / rma_down.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    
    # Fix các lỗi toán học theo logic gốc của TradingView
    rsi = rsi.fillna(100)
    rsi[rma_up == 0] = 0

    # 3. ĐÓNG GÓI DỮ LIỆU GỬI AI STRATEGIST
    valid_rsi = rsi.dropna()
    if len(valid_rsi) < 2:
        return "Chỉ báo RSI Chart Bars: Chưa đủ dữ liệu nến để tính toán."
        
    current_rsi = float(valid_rsi.iloc[-1])
    
    # Phân tích logic tô màu nến của tác giả Glaz
    if current_rsi > upLevel:
        color_status = "🟢 NẾN XANH (RSI > 70): Cảnh báo giá đang rướn lên vùng Quá Mua cực đại."
    elif current_rsi < downLevel:
        color_status = "🔴 NẾN ĐỎ (RSI < 30): Cảnh báo giá đang bị ép xuống vùng Quá Bán cực đại."
    else:
        color_status = "⚪ NẾN TRẮNG/BÌNH THƯỜNG: Biên độ dao động an toàn, chưa vi phạm ngưỡng cực đoan."

    text_for_ai = (
        f"Chỉ báo RSI Chart Bars (Glaz):\n"
        f"  + Giá trị RSI(14) hiện tại: {current_rsi:.2f}\n"
        f"  + Nhận diện Biểu đồ: {color_status}"
    )

    return text_for_ai