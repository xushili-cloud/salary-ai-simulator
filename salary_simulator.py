import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

def get_rent_info(location):
    """调用 AI 获取特定区域的平均房租"""
    try:
        client = OpenAI(
            api_key=st.secrets["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com"
        )

        system_prompt = "你是一个拥有 10 年经验的中国一线城市租房市场专家。请基于 2026 年最新市场行情，给出指定地段一室一厅、中等偏上装修、适合一人独居的平均月租金预估。严禁输出任何文字描述、单位（如“元”）或区间（如“4000-5000”）。只输出一个代表平均月租金的整数。"
        user_prompt = f"地点：{location}。请给出该区域一室一厅的平均月租金数字。"

        response = client.chat.completions.create(
            model="deepseek-chat", # 或者使用 gpt-4o
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False,
            temperature=0.3
        )
        rent_value = int(response.choices[0].message.content.strip())
        return rent_value
    except Exception as e:
        st.warning(f"AI 获取房租失败，使用保底数据: ¥5000。错误信息: {e}")
        return 5000  # 若失败，给一个默认保底价

def main():
    # 设置页面标题（浏览器标签页显示的文字）
    st.set_page_config(page_title="徐诗礼的超级薪资计算器", layout="centered")

    # 在页面顶部显示大标题
    st.title("💰 徐诗礼的超级薪资计算器")

    # 添加小红书品牌副标题
    st.caption("🔍 小红书同名：徐诗礼 | 帮你算清大厂薪资的每一分价值")

    # 添加一条分割线，让界面更整洁
    st.divider()

    # 侧边栏输入模块
    st.sidebar.header("输入你的薪资信息")
    
    base_salary = st.sidebar.number_input("基本工资 (月薪，税前)", min_value=0, value=15000, step=1000)
    bonus = st.sidebar.number_input("奖金 (年终奖，税前)", min_value=0, value=30000, step=1000)
    city = st.sidebar.selectbox("所在城市", ["北京", "上海", "深圳", "广州", "杭州", "其他"], index=0)
    insurance_rate = st.sidebar.slider("五险一金个人承担比例 (%)", min_value=0.0, max_value=25.0, value=10.5, step=0.1)
    work_hours = st.sidebar.number_input("平均工作时长 (每天小时数)", min_value=1, value=8, step=1)
    location = st.sidebar.text_input("平时工作地点 (例如: 北京朝阳区)", value="北京朝朝阳区")

    # ---- 计算引擎 ----

    # 个税计算函数
    def calculate_tax(salary_after_insurance, city):
        # 假设起征点为 5000 元/月
        taxable_income = salary_after_insurance - 5000
        tax = 0
        if taxable_income <= 0:
            tax = 0
        elif taxable_income <= 3000:
            tax = taxable_income * 0.03
        elif taxable_income <= 12000:
            tax = taxable_income * 0.10 - 210
        elif taxable_income <= 25000:
            tax = taxable_income * 0.20 - 1410
        elif taxable_income <= 35000:
            tax = taxable_income * 0.25 - 2660
        elif taxable_income <= 55000:
            tax = taxable_income * 0.30 - 4410
        elif taxable_income <= 80000:
            tax = taxable_income * 0.35 - 7160
        else:
            tax = taxable_income * 0.45 - 15160
        return max(0, tax)

    # 月薪 + 奖金平摊到月
    monthly_total_income = base_salary + (bonus / 12)

    # 五险一金扣除
    insurance_deduction = base_salary * (insurance_rate / 100)
    salary_after_insurance = monthly_total_income - insurance_deduction

    # 计算个税
    monthly_tax = calculate_tax(salary_after_insurance, city)

    # 到手价
    take_home_pay = salary_after_insurance - monthly_tax

    # 获取房租信息
    monthly_rent = get_rent_info(location)

    # 净收入 (到手价 - 房租)
    net_income = take_home_pay - monthly_rent

    # 月工作日固定为 22 天
    daily_base = take_home_pay / 22
    hourly_wage = daily_base / work_hours

    # 新增：体面指数 (Decency Index)
    if take_home_pay > 0:
        decency_index = (take_home_pay - monthly_rent) / take_home_pay
    else:
        decency_index = 0

    # 新增：真实时薪 (True Hourly Rate)
    true_hourly_rate = (take_home_pay - monthly_rent) / (22 * work_hours)

    # 主展示区域
    st.header("计算结果")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("税前月总收入", f"¥{monthly_total_income:,.2f}")
    with col2:
        st.metric("五险一金扣除", f"¥{insurance_deduction:,.2f}")
    with col3:
        st.metric("个税", f"¥{monthly_tax:,.2f}")
    with col4:
        st.metric("税后到手 (月)", f"¥{take_home_pay:,.2f}")
    
    st.markdown("--- --- --- ---")
    
    col5, col6, col7 = st.columns(3)
    with col5:
        st.metric("月租金估算", f"¥{monthly_rent:,.2f}")
    with col6:
        st.metric("月净收入 (扣除房租)", f"¥{net_income:,.2f}")
    with col7:
        st.metric("日薪 (税后)", f"¥{daily_base:,.2f}")
    
    col8, col9 = st.columns(2)
    with col8:
        st.metric("时薪 (税后)", f"¥{hourly_wage:,.2f}")
    with col9:
        st.metric("真实时薪 (扣房租)", f"¥{true_hourly_rate:,.2f}", delta_color="off")

    st.markdown("--- --- --- ---")

    col10, col11 = st.columns(2)
    with col10:
        st.metric("体面指数", f"{decency_index:.2%}", delta_color="off")
    with col11:
        if decency_index < 0.5:
            st.warning("⚠️ 生活质量预警：体面指数低于 50%，请考虑调整！")
        else:
            st.success("✅ 生活质量良好，继续保持！")

    # 租房信息模块
    st.header("AI 房租评估")
    st.info(f"根据 AI 专家评估，在 **{location}** 附近租一个单间的平均月租金大约是 **¥{monthly_rent:,.2f}**。")


if __name__ == "__main__":
    main()
