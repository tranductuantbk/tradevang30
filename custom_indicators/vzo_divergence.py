import pandas as pd
import numpy as np

def run_indicator(df):
    # ----------------------------------------------------------------------
    # 1. CÀI ĐẶT THÔNG SỐ 
    # ----------------------------------------------------------------------
    vzo_length = 14
    vzo_noise = 4
    pivot_left = 5
    pivot_right = 5
    max_bars = 60
    
    d = df.copy()
    
    # --- FIX LỖI DỮ LIỆU 2D TỪ YFINANCE ---
    # Ép tất cả các cột giá trị về dạng chuỗi 1 chiều (1D Series)
    close_series = d['Close'].squeeze()
    volume_series = d['Volume'].squeeze()
    high_series = d['High'].squeeze()
    low_series = d['Low'].squeeze()
    
    # ----------------------------------------------------------------------
    # 2. TÍNH TOÁN VZO (THUẦN PANDAS)
    # ----------------------------------------------------------------------
    # Xác định hướng dòng tiền (Volume Direction)
    direction = volume_series.copy()
    direction[close_series <= close_series.shift(1)] = -volume_series
    
    vzo_volume = direction.ewm(span=vzo_length, adjust=False).mean()
    total_volume = volume_series.ewm(span=vzo_length, adjust=False).mean()
    
    # Tính VZO gốc (Tránh lỗi chia cho 0)
    raw_vzo = pd.Series(0.0, index=d.index)
    mask = total_volume != 0
    raw_vzo[mask] = 100 * (vzo_volume[mask] / total_volume[mask])
    
    # Làm mượt (Smoothing)
    d['VZO'] = raw_vzo.ewm(span=vzo_noise, adjust=False).mean()
    
    # ----------------------------------------------------------------------
    # 3. TÌM PIVOT ĐỈNH / ĐÁY
    # ----------------------------------------------------------------------
    window_size = pivot_left + pivot_right + 1
    
    d['VZO_Max'] = d['VZO'].rolling(window=window_size, center=True).max()
    d['VZO_Min'] = d['VZO'].rolling(window=window_size, center=True).min()
    
    d['Is_Pivot_High'] = (d['VZO'] == d['VZO_Max'])
    d['Is_Pivot_Low']  = (d['VZO'] == d['VZO_Min'])
    
    pivot_highs = d[d['Is_Pivot_High']]
    pivot_lows  = d[d['Is_Pivot_Low']]
    
    # ----------------------------------------------------------------------
    # 4. HÀM KIỂM CHỨNG GIAO ĐIỂM (CHỐNG NHIỄU)
    # ----------------------------------------------------------------------
    def check_validation(idx_start, idx_end, is_high):
        bars_diff = idx_end - idx_start
        if bars_diff > max_bars or bars_diff < 5:
            return False
        
        start_val = d['VZO'].iloc[idx_start]
        end_val = d['VZO'].iloc[idx_end]
        slope = (end_val - start_val) / bars_diff
        
        for i in range(1, bars_diff):
            line_val = start_val + (slope * i)
            current_vzo = d['VZO'].iloc[idx_start + i]
            if is_high and current_vzo > line_val:
                return False
            if not is_high and current_vzo < line_val:
                return False
        return True

    # ----------------------------------------------------------------------
    # 5. TÌM PHÂN KỲ GẦN NHẤT
    # ----------------------------------------------------------------------
    div_status = "Không phát hiện phân kỳ."
    
    # Kiểm tra Phân kỳ Đáy (Bullish)
    if len(pivot_lows) >= 2:
        pl1 = pivot_lows.iloc[-1]
        pl2 = pivot_lows.iloc[-2]
        
        idx1 = d.index.get_loc(pl1.name)
        idx2 = d.index.get_loc(pl2.name)
        
        if check_validation(idx2, idx1, False):
            if low_series.iloc[idx1] < low_series.iloc[idx2] and pl1['VZO'] > pl2['VZO']:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Thường (Regular Bullish) - ĐẢO CHIỀU TĂNG ({bars_ago} nến trước)."
            elif low_series.iloc[idx1] > low_series.iloc[idx2] and pl1['VZO'] < pl2['VZO']:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Ẩn (Hidden Bullish) - TIẾP TỤC TĂNG ({bars_ago} nến trước)."

    # Kiểm tra Phân kỳ Đỉnh (Bearish)
    if len(pivot_highs) >= 2 and "Không" in div_status:
        ph1 = pivot_highs.iloc[-1]
        ph2 = pivot_highs.iloc[-2]
        
        idx1 = d.index.get_loc(ph1.name)
        idx2 = d.index.get_loc(ph2.name)
        
        if check_validation(idx2, idx1, True):
            if high_series.iloc[idx1] > high_series.iloc[idx2] and ph1['VZO'] < ph2['VZO']:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Thường (Regular Bearish) - ĐẢO CHIỀU GIẢM ({bars_ago} nến trước)."
            elif high_series.iloc[idx1] < high_series.iloc[idx2] and ph1['VZO'] > ph2['VZO']:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Ẩn (Hidden Bearish) - TIẾP TỤC GIẢM ({bars_ago} nến trước)."

    # ----------------------------------------------------------------------
    # 6. DỊCH VÙNG VZO & ĐÓNG GÓI GỬI AI
    # ----------------------------------------------------------------------
    current_vzo = d['VZO'].iloc[-1]
    
    if current_vzo > 60:
        zone_status = "Quá mua mạnh (Phân phối)"
    elif current_vzo > 40:
        zone_status = "Quá mua"
    elif current_vzo > 15:
        zone_status = "Vùng Tăng (Phe Mua kiểm soát)"
    elif current_vzo > -15:
        zone_status = "Vùng Nhiễu (Đi ngang)"
    elif current_vzo > -40:
        zone_status = "Vùng Giảm (Phe Bán kiểm soát)"
    elif current_vzo > -60:
        zone_status = "Quá bán"
    else:
        zone_status = "Quá bán mạnh (Cạn cung)"
        
    text_for_ai = (
        f"Chỉ báo VZO Divergence Pro:\n"
        f"  + Mức VZO hiện tại: {current_vzo:.2f} -> Nằm trong {zone_status}.\n"
        f"  + Trạng thái Phân kỳ: {div_status}"
    )
    
    return text_for_ai
