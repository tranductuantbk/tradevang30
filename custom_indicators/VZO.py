# ==========================================================
    # 4. TRẢ DỮ LIỆU VỀ STREAMLIT (CHUẨN GIỜ VIỆT NAM GMT+7)
    # ==========================================================
    plot_data = {
        "vzo": vzo,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals
    }
    
    last_signal = "Bình thường"
    
    for i in range(len(df)-1, max(0, len(df)-11), -1):
        if not np.isnan(buy_signals.iloc[i]):
            try:
                timestamp = pd.to_datetime(df.index[i])
                # Dữ liệu gốc là GMT+3, giờ VN là GMT+7 -> Cộng chênh lệch 4 tiếng
                timestamp_vn = timestamp + pd.Timedelta(hours=4)
                time_str = timestamp_vn.strftime('%H:%M:%S %d/%m/%Y')
            except:
                time_str = str(df.index[i])
                
            last_signal = f"Đỉnh Đáy VZO - KIỆT SỨC BÁN lúc {time_str} (Chuẩn bị Tăng)"
            break
            
        elif not np.isnan(sell_signals.iloc[i]):
            try:
                timestamp = pd.to_datetime(df.index[i])
                # Dữ liệu gốc là GMT+3, giờ VN là GMT+7 -> Cộng chênh lệch 4 tiếng
                timestamp_vn = timestamp + pd.Timedelta(hours=4)
                time_str = timestamp_vn.strftime('%H:%M:%S %d/%m/%Y')
            except:
                time_str = str(df.index[i])
                
            last_signal = f"Đỉnh Đáy VZO - KIỆT SỨC MUA lúc {time_str} (Chuẩn bị Giảm)"
            break
            
    if last_signal == "Bình thường":
        last_signal = f"Đỉnh Đáy VZO - Đang chạy trong Trend {'TĂNG' if macro_trend.iloc[-1] == 1 else 'GIẢM'}"
        
    return last_signal, plot_data
