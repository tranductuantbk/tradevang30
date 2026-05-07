import pandas as pd
import numpy as np

def run_indicator(df):
    """
    Chỉ báo VZO Divergence Pro
    Dịch từ Pine Script v6 sang Python Core (Pandas + Numpy)
    """
    # ----------------------------------------------------------------------
    # 1. CÀI ĐẶT THÔNG SỐ (Giống y hệt Pine Script)
    # ----------------------------------------------------------------------
    vzo_length = 14
    vzo_noise = 4
    pivot_left = 5
    pivot_right = 5
    max_bars = 60
    
    # Sao chép dataframe để không làm ảnh hưởng dữ liệu gốc
    d = df.copy()
    
    # ----------------------------------------------------------------------
    # 2. TÍNH TOÁN VZO
    # ----------------------------------------------------------------------
    # Volume_Direction = close > close[1] ? volume : -volume
    direction = np.where(d['Close'] > d['Close'].shift(1), d['Volume'], -d['Volume'])
    
    # VZO_volume = ta.ema(Volume_Direction, VZO_length)
    vzo_volume = pd.Series(direction).ewm(span=vzo_length, adjust=False).mean()
    
    # Total_volume = ta.ema(volume, VZO_length)
    total_volume = d['Volume'].ewm(span=vzo_length, adjust=False).mean()
    
    # raw_VZO = Total_volume != 0 ? 100 * VZO_volume / Total_volume : 0
    raw_vzo = np.where(total_volume != 0, 100 * vzo_volume / total_volume, 0)
    
    # VZO = ta.ema(raw_VZO, VZO_noise)
    d['VZO'] = pd.Series(raw_vzo).ewm(span=vzo_noise, adjust=False).mean()
    
    # ----------------------------------------------------------------------
    # 3. TÌM PIVOT ĐỈNH / ĐÁY
    # ----------------------------------------------------------------------
    # Dùng Rolling Window có độ rộng = left + right + 1 (5 + 5 + 1 = 11)
    window_size = pivot_left + pivot_right + 1
    
    # Tìm Max/Min trong cửa sổ (center=True để đối chiếu với nến chính giữa)
    d['VZO_Max'] = d['VZO'].rolling(window=window_size, center=True).max()
    d['VZO_Min'] = d['VZO'].rolling(window=window_size, center=True).min()
    
    d['Is_Pivot_High'] = (d['VZO'] == d['VZO_Max'])
    d['Is_Pivot_Low']  = (d['VZO'] == d['VZO_Min'])
    
    # Lấy ra danh sách các Pivot
    pivot_highs = d[d['Is_Pivot_High']]
    pivot_lows  = d[d['Is_Pivot_Low']]
    
    # ----------------------------------------------------------------------
    # 4. HÀM KIỂM CHỨNG GIAO ĐIỂM (CHECK_VALIDATION)
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
    bars_ago = 0
    
    # Kiểm tra Phân kỳ Đáy (Bullish)
    if len(pivot_lows) >= 2:
        pl1 = pivot_lows.iloc[-1] # Đáy gần nhất
        pl2 = pivot_lows.iloc[-2] # Đáy trước đó
        
        idx1 = d.index.get_loc(pl1.name)
        idx2 = d.index.get_loc(pl2.name)
        
        if check_validation(idx2, idx1, False):
            if pl1['Low'] < pl2['Low'] and pl1['VZO'] > pl2['VZO']:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Thường (Regular Bullish) - Báo hiệu ĐẢO CHIỀU TĂNG (Xuất hiện {bars_ago} nến trước)."
            elif pl1['Low'] > pl2['Low'] and pl1['VZO'] < pl2['VZO']:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Ẩn (Hidden Bullish) - Báo hiệu TIẾP TỤC TĂNG (Xuất hiện {bars_ago} nến trước)."

    # Kiểm tra Phân kỳ Đỉnh (Bearish)
    if len(pivot_highs) >= 2 and "Không" in div_status:
        ph1 = pivot_highs.iloc[-1]
        ph2 = pivot_highs.iloc[-2]
        
        idx1 = d.index.get_loc(ph1.name)
        idx2 = d.index.get_loc(ph2.name)
        
        if check_validation(idx2, idx1, True):
            if ph1['High'] > ph2['High'] and ph1['VZO'] < ph2['VZO']:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Thường (Regular Bearish) - Báo hiệu ĐẢO CHIỀU GIẢM (Xuất hiện {bars_ago} nến trước)."
            elif ph1['High'] < ph2['High'] and ph1['VZO'] > ph2['VZO']:
                bars_ago = len(d) - 1 - idx1
                div_status = f"Phân kỳ Ẩn (Hidden Bearish) - Báo hiệu TIẾP TỤC GIẢM (Xuất hiện {bars_ago} nến trước)."

    # ----------------------------------------------------------------------
    # 6. DỊCH VÙNG VZO & ĐÓNG GÓI CHO AI
    # ----------------------------------------------------------------------
    current_vzo = d['VZO'].iloc[-1]
    
    if current_vzo > 60:
        zone_status = "Quá mua mạnh (OB Upper)"
    elif current_vzo > 40:
        zone_status = "Quá mua (OB Lower)"
    elif current_vzo > 15:
        zone_status = "Vùng Tăng (Bullish Zone)"
    elif current_vzo > -15:
        zone_status = "Vùng Nhiễu (Chop Zone)"
    elif current_vzo > -40:
        zone_status = "Vùng Giảm (Bearish Zone)"
    elif current_vzo > -60:
        zone_status = "Quá bán (OS Lower)"
    else:
        zone_status = "Quá bán mạnh (OS Upper)"
        
    text_for_ai = (
        f"Chỉ báo VZO Divergence Pro:\n"
        f"  + Mức VZO hiện tại: {current_vzo:.2f} -> Nằm trong {zone_status}.\n"
        f"  + Trạng thái Phân kỳ: {div_status}"
    )
    
    return text_for_ai