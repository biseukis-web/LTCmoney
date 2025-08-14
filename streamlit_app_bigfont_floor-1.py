import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import os
import math  # 新增匯入 math 模組

# === 資料讀取 ===
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "計算額度.xlsx")
    df_care = pd.read_excel(file_path, sheet_name="工作表2")
    df_transport = pd.read_excel(file_path, sheet_name="工作表3")
    return df_care, df_transport

df_care, df_transport = load_data()

st.title("長照額度自動查詢工具")

# === 使用者輸入 ===
col1, col2 = st.columns(2)
with col1:
    eval_date = st.date_input("請選擇評估日", value=datetime.today())
with col2:
    care_level = st.selectbox("請選擇長照需要等級", df_care["長照需要等級"].dropna().unique())

transport_type_col = "交通接送類型"
if transport_type_col not in df_transport.columns:
    st.error(f"找不到欄位：{transport_type_col}，請確認 Excel 中欄位名稱是否正確")
    st.stop()

zone = st.selectbox("請選擇交通接送類型", df_transport[transport_type_col].dropna().unique())

# === 當月應計天數計算（包含評估日） ===
month_days = calendar.monthrange(eval_date.year, eval_date.month)[1]
day_of_eval = eval_date.day
active_days = month_days - day_of_eval + 1

# === 查詢額度 ===
row = df_care[df_care["長照需要等級"] == care_level].iloc[0]
care_amount = row["照顧及專業服務給付額度"]

zone_row = df_transport[df_transport[transport_type_col] == zone].iloc[0]
transport_amount = zone_row["交通接送給付額度"]

# === 比例計算（無條件捨去） ===
care_amount_ratio = math.floor(care_amount * active_days / month_days)
transport_amount_ratio = math.floor(transport_amount * active_days / month_days)

# === 扣減額度計算 ===
care_amount_deduction = care_amount - care_amount_ratio
transport_amount_deduction = transport_amount - transport_amount_ratio

# === 結果輸出（放大字體 + 加粗） ===
st.subheader("計算結果")
st.markdown(
    f"<p style='font-size:22px; font-weight:bold;'>當月應計天數：{active_days} 天（共 {month_days} 天）</p>",
    unsafe_allow_html=True
)
st.markdown(
    f"<p style='font-size:22px; font-weight:bold;'>照顧及專業服務 應有額度：{care_amount} 元 → 比例額度：{care_amount_ratio} 元 → 扣減額度：{care_amount_deduction} 元</p>",
    unsafe_allow_html=True
)
st.markdown(
    f"<p style='font-size:22px; font-weight:bold;'>交通接送服務 應有額度：{transport_amount} 元 → 比例額度：{transport_amount_ratio} 元 → 扣減額度：{transport_amount_deduction} 元</p>",
    unsafe_allow_html=True
)
