import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="AI Gold Trading Terminal")

# --- Hàm tạo biểu đồ TradingView chuẩn ---
def render_tradingview_chart(symbol="OANDA:XAUUSD", interval="30"):
    html_code = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:100%;width:100%">
      <div id="tradingview_gold" style="height:600px;width:100%"></div>
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
      "backgroundColor": "rgba(0, 0, 0, 1)",
      "allow_symbol_change": true,
      "container_id": "tradingview_gold"
    }}
      );
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    # Chiều cao của components phải tương xứng với chiều cao thẻ div bên trên
    components.html(html_code, height=600)

# --- MAIN SECTION ---
col_chart, col_ai = st.columns([2, 1])

with col_chart:
    st.subheader("XAU/USD Live Chart")
    
    # Nút chọn khung thời gian
    timeframe_map = {"30m": "30", "1h": "60", "4h": "240", "1d": "D"}
    selected_tf = st.selectbox("Khung thời gian", options=list(timeframe_map.keys()), index=0)
    
    # Gọi hàm hiển thị biểu đồ
    render_tradingview_chart(symbol="OANDA:XAUUSD", interval=timeframe_map[selected_tf])

with col_ai:
    st.subheader("🤖 AI Strategist")
    st.info("Khu vực AI sẽ đọc dữ liệu từ các module...")
