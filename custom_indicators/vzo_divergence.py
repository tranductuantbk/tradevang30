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
    
    # Ép dữ liệu về 1 chiều (1D) chắc chắn 100%
    def get_1d(col_name):
        col = d[col_name]
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    close_series = get_1d('Close')
    volume_series = get_1d('Volume')
    high_series = get_1d('High')
    low_series = get_1d('Low')
    
    # ----------------------------------------------------------------------
    # 2. TÍNH TOÁN VZO
    # ----------------------------------------------------------------------
    direction = volume_series.copy()
    direction[close_series <= close_series.shift(1)] = -volume_series
    
    vzo_volume = direction.ewm(span=vzo_length, adjust=False).mean()
    total_volume = volume_series.ewm(span=vzo_length, adjust=False).mean()
    
    raw_vzo = pd.Series(0.0, index=d.index)
    mask = total_volume != 0
    raw_vzo[mask] = 100 * (vzo_volume[mask] / total_volume[mask])
    
    d['VZO'] = raw_vzo.ewm(span=vzo_noise, adjust=False).mean()
    
    # ----------------------------------------------------------------------
    # 3. TÌM PIVOT BẰNG SỐ THỨ TỰ VẬT LÝ (TRÁNH LỖI DUPLICATE INDEX)
    # ----------------------------------------------------------------------
    window_size = pivot_left + pivot_right + 1
    
    d['VZO_Max'] = d['VZO'].rolling(window=window_size, center=True).max()
    d['VZO_Min'] = d['VZO'].rolling(window=window_size, center=True).min()
    
    d['Is_Pivot_High'] = (d['VZO'] == d['VZO_Max'])
    d['Is_Pivot_Low']  = (d['VZO'] == d['VZO_Min'])
    
    # Lấy vị trí index chính xác của các điểm Pivot
    pivot_high_indices = np.where(d['Is_Pivot_High'])[0]
    pivot_low_indices  = np.where(d['Is_Pivot_Low'])[0]
    
    # ----------------------------------------------------------------------
    # 4. HÀM KIỂM CHỨNG GIAO ĐIỂM
    # ----------------------------------------------------------------------
    def check_validation(idx_start, idx_end, is_high):
        bars_diff = idx_end - idx_start
        if bars_diff > max_bars or bars_diff < 5:
            return False
        
        start_val = float(d['VZO'].iloc[idx_start])
        end_val = float(d['VZO'].iloc[idx_end])
        slope = (end_val - start_val) / float(bars_diff)
        
        for i in range(1, bars_diff):
            line_val = start_val + (slope * i)
            current_vzo = float(d['VZO'].iloc[idx_start + i])
            if is_high and current_vzo > line_val:
                return False
            if not is_high and current_vzo < line_val:
                return False
        return True

    # ----------------------------------------------------------------------
    # 5. TÌM PHÂN KỲ GẦN NHẤT
    # ----------------------------------------------------------------------
    div_status = "Không phát hiện phân kỳ."
    
    # Phân kỳ Đáy (Bullish)
    if len(pivot_low_indices) >= 2:
        idx1 = pivot_low_indices[-1] # Vị trí nến hiện tại
        idx2 = pivot_low_indices[-2] # Vị trí nến trước đó
        
        if check_validation(idx2, idx1, False):
            vzo1 = float(d['VZO'].iloc[idx1])
            vzo2 = float(d['VZO'].iloc[idx2])
            price1 = float(low_series.iloc[idx1])
            price2 = float(low_series.iloc[idx2])
            
            if price1 < price2 and vzo1 > vzo2:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Thường (Regular Bullish) - ĐẢO CHIỀU TĂNG ({bars_ago} nến trước)."
            elif price1 > price2 and vzo1 < vzo2:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Ẩn (Hidden Bullish) - TIẾP TỤC TĂNG ({bars_ago} nến trước)."

    # Phân kỳ Đỉnh (Bearish)
    if len(pivot_high_indices) >= 2 and "Không" in div_status:
        idx1 = pivot_high_indices[-1]
        idx2 = pivot_high_indices[-2]
        
        if check_validation(idx2, idx1, True):
            vzo1 = float(d['VZO'].iloc[idx1])
            vzo2 = float(d['VZO'].iloc[idx2])
            price1 = float(high_series.iloc[idx1])
            price2 = float(high_series.iloc[idx2])
            
            if price1 > price2 and vzo1 < vzo2:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Thường (Regular Bearish) - ĐẢO CHIỀU GIẢM ({bars_ago} nến trước)."
            elif price1 < price2 and vzo1 > vzo2:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Ẩn (Hidden Bearish) - TIẾP TỤC GIẢM ({bars_ago} nến trước)."

    # ----------------------------------------------------------------------
    # 6. DỊCH VÙNG VZO & ĐÓNG GÓI GỬI AI
    # ----------------------------------------------------------------------
    current_vzo = float(d['VZO'].iloc[-1])
    
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
