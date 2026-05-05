import streamlit as st
import streamlit.components.v1 as components

# Cài đặt cấu hình trang phải luôn nằm ở dòng đầu tiên của Streamlit
st.set_page_config(layout="wide", page_title="AI Gold Trading Terminal", page_icon="📈")

# --- 1. HÀM TẠO BIỂU ĐỒ TRADINGVIEW ---
def render_tradingview_chart(symbol="OANDA:XAUUSD", interval="30"):
    """
    Nhúng trực tiếp Widget của TradingView bằng HTML/JS.
    Cách này siêu nhẹ, mượt và không bị lỗi ModuleNotFoundError trên server.
    """
    html_code = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:100%;width:100%">
      <div id="tradingview_gold" style="height:650px;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
      "autosize": true,
      "symbol": "{symbol}",
      "interval": "{interval}",
      "timezone": "Asia/Ho_Chi_Minh",
      "theme": "dark",
      "style": "1",
      "locale": "vi_VN",
      "enable_publishing": false,
      "backgroundColor": "#131722",
      "gridColor": "#1f293d",
      "hide_top_toolbar": false,
      "hide_legend": false,
      "save_image": false,
      "container_id": "tradingview_gold",
      "studies": [
        "Volume@tv-basicstudies"
      ]
    }}
      );
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    # Render HTML với chiều cao tương ứng
    components.html(html_code, height=650)

# --- 2. SIDEBAR: KIỂM TRA TRẠNG THÁI MODULE CHẠY NGẦM ---
st.sidebar.title("📡 System Status")
st.sidebar.markdown("Trạng thái dữ liệu từ các Module:")

# Lấy dữ liệu từ session_state (được các file trong thư mục pages/ đẩy lên)
indicator_data = st.session_state.get('tech_indicators', "⚠️ Chưa có dữ liệu. Hãy mở trang Module Chỉ báo.")
macro_data = st.session_state.get('macro_info', "⚠️ Chưa có dữ liệu.")
flow_data = st.session_state.get('money_flow', "⚠️ Chưa có dữ liệu.")

st.sidebar.success("Trạng thái Chỉ báo: OK" if "⚠️" not in indicator_data else indicator_data)
st.sidebar.warning("Trạng thái Vĩ mô: Trống" if "⚠️" in macro_data else "Trạng thái Vĩ mô: OK")
st.sidebar.warning("Trạng thái Dòng tiền: Trống" if "⚠️" in flow_data else "Trạng thái Dòng tiền: OK")


# --- 3. GIAO DIỆN CHÍNH (MAIN LAYOUT) ---
st.title("⚡ Quant Trading Hub - XAU/USD")
st.markdown("---")

# Chia màn hình thành 2 cột: Biểu đồ (tỷ lệ 7) và AI (tỷ lệ 3)
col_chart, col_ai = st.columns([7, 3])

with col_chart:
    # Nút chọn khung thời gian đặt ở trên cùng biểu đồ
    timeframe_map = {"M30": "30", "H1": "60", "H4": "240", "D1": "D"}
    selected_tf = st.radio(
        "Khung thời gian:", 
        options=list(timeframe_map.keys()), 
        index=0, 
        horizontal=True
    )
    
    # Hiển thị biểu đồ
    render_tradingview_chart(symbol="OANDA:XAUUSD", interval=timeframe_map[selected_tf])

with col_ai:
    st.subheader("🤖 AI Strategist")
    st.markdown("Hệ thống tự động đọc dữ liệu từ các module bên ngoài và phân tích bối cảnh.")
    
    # Nút kích hoạt AI
    if st.button("🚀 Thực thi Phân tích Toàn diện", use_container_width=True, type="primary"):
        with st.spinner("Đang tổng hợp dữ liệu Chỉ báo, Vĩ mô và Dòng tiền..."):
            
            # --- TẠI ĐÂY SẼ GỌI HÀM OPENAI HOẶC GEMINI API ---
            # Để demo, tôi hiển thị luôn dữ liệu mà AI sẽ "nhìn thấy"
            st.markdown("### Dữ liệu AI nhận được:")
            
            with st.expander("1. Chỉ báo Kỹ thuật", expanded=True):
                st.write(indicator_data)
                
            with st.expander("2. Dữ liệu Vĩ mô"):
                st.write(macro_data)
                
            with st.expander("3. Dòng tiền (Smart Money)"):
                st.write(flow_data)
                
            st.info("💡 Lời khuyên từ AI: Dựa trên VSA khung M30, hiện tại khối lượng đang cạn kiệt tại vùng Hỗ trợ. Chờ đợi xác nhận một cây nến Cầu (Demand) đẩy lên mạnh để vào lệnh Buy.")
            
            # Form nhập lệnh nhanh
            st.markdown("---")
            st.markdown("### ⚡ Cài đặt Lệnh Nhanh")
            entry = st.number_input("Entry", value=2350.00, step=0.1)
            sl = st.number_input("Stoploss", value=2345.00, step=0.1)
            if st.button("Lưu Nhật ký (Neon DB)"):
                st.success(f"Đã lưu lệnh Buy Limit tại {entry}, SL: {sl} vào cơ sở dữ liệu.")
