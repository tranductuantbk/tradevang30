import streamlit as st

class MacroAnalyzer:
    def __init__(self):
        # Lưu trữ trạng thái 3 yếu tố
        self.factors = {
            "FED_Rate": "Neutral",    # Hawkish, Dovish, Neutral
            "Geopolitics": "Stable",  # High Tension, Stable
            "USD_DXY": 105.0          # Giá trị DXY hiện tại
        }

    def render_ui(self):
        st.subheader("🌍 Macro Intel Module")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            self.factors["FED_Rate"] = st.selectbox("Xu hướng FED:", ["Hawkish", "Dovish", "Neutral"])
        with c2:
            self.factors["Geopolitics"] = st.selectbox("Căng thẳng ĐC:", ["High Tension", "Stable", "War Risk"])
        with c3:
            self.factors["USD_DXY"] = st.number_input("Giá trị DXY:", value=105.0, step=0.1)
            
        return self.factors

    def get_summary(self):
        # Chuyển đổi dữ liệu thành text để AI đọc
        return f"""
        - Xu hướng FED: {self.factors['FED_Rate']}
        - Căng thẳng ĐC: {self.factors['Geopolitics']}
        - Chỉ số DXY: {self.factors['USD_DXY']}
        """