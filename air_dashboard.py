import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 设置matplotlib中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="城市空气质量交互式看板", layout="wide")
st.title("🌫️ 城市空气质量交互式数据看板")
st.markdown("### 项目简介")
st.write("本看板基于全国城市空气质量公开数据集，支持切换城市查看污染物时序变化、相关性分析，直观展示空气质量特征。")

# 读取数据
df = pd.read_csv("air_quality.csv")
df['record_date'] = pd.to_datetime(df['record_date'])
df['year'] = df['record_date'].dt.year
df['month'] = df['record_date'].dt.month

# 侧边栏筛选
with st.sidebar:
    st.header("筛选面板")
    city_list = sorted(df['city_name'].unique())
    selected_city = st.selectbox("选择城市", city_list)
    year_list = sorted(df['year'].unique())
    selected_year = st.selectbox("选择年份", year_list)

# 【第一步：先拿到 该城市+该年份 原始全部数据（清洗前）】
df_raw = df[(df['city_name'] == selected_city) & (df['year'] == selected_year)].copy()
raw_count = len(df_raw)

# 【第二步：执行清洗逻辑】
df_clean = df_raw.dropna(subset=['quality_level'])
df_clean = df_clean[(df_clean['pm2_5_val'] >= 0) & (df_clean['pm2_5_val'] <= 500)]
df_clean = df_clean[(df_clean['pm10_val'] >= 0) & (df_clean['pm10_val'] <= 500)]
df_clean = df_clean[(df_clean['aqi_val'] >=0) & (df_clean['aqi_val'] <= 500)]
clean_count = len(df_clean)

# 判断并展示数据说明
if raw_count == 0:
    st.warning(f"⚠️ 数据源本身无记录：【{selected_city}】在【{selected_year}】年原始数据集不存在任何监测数据。")
elif clean_count == 0:
    st.warning(f"⚠️ 原始共有{raw_count}条记录，经过清洗后无有效数据。\n原因：全部记录存在空气质量等级缺失，或PM2.5/PM10/AQI数值异常，已被过滤剔除。")
else:
    st.info(f"✅ 原始共{raw_count}条记录，清洗后有效记录：{clean_count}条")
    # 指标卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("有效监测记录数", clean_count)
    with col2:
        st.metric("全年平均AQI", round(df_clean['aqi_val'].mean(),2))
    with col3:
        st.metric("全年平均PM2.5", round(df_clean['pm2_5_val'].mean(),2))

    # 月度PM2.5折线图
    st.subheader(f"📈 {selected_city} {selected_year}年 月度PM2.5平均浓度")
    month_pm25 = df_clean.groupby('month')['pm2_5_val'].mean()
    fig1, ax1 = plt.subplots(figsize=(10,4))
    ax1.plot(month_pm25.index, month_pm25.values, marker='o', linewidth=2, color="#E74C3C")
    ax1.set_xlabel("月份")
    ax1.set_ylabel("PM2.5 浓度(微克/立方米)")
    ax1.set_xticks(range(1,13))
    ax1.grid(alpha=0.3)
    st.pyplot(fig1)

    # 污染物相关性热力图
    st.subheader(f"🔥 {selected_city} {selected_year}年 污染物相关性热力图")
    corr_data = df_clean[['pm2_5_val','pm10_val','aqi_val','co_val','no2_val','so2_val','o3_val']].corr()
    fig2, ax2 = plt.subplots(figsize=(8,6))
    sns.heatmap(corr_data, annot=True, cmap="Blues", fmt=".2f", ax=ax2)
    st.pyplot(fig2)

    # 空气质量等级饼图
    st.subheader(f"🥧 {selected_city} {selected_year}年 空气质量等级分布")
    level_count = df_clean['quality_level'].value_counts()
    fig3, ax3 = plt.subplots()
    ax3.pie(level_count.values, labels=level_count.index, autopct="%.1f%%")
    st.pyplot(fig3)

    # 分析结论
    st.markdown("### 📝 简要分析结论")
    st.write("1. PM2.5与AQI高度正相关，是影响空气质量的核心指标；")
    st.write("2. 颗粒物污染物与臭氧O3呈负相关，冬夏污染类型不同；")
    st.write("3. 可通过切换城市、年份，对比不同地区空气质量差异。")