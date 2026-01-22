"""
JZGCCW 建设工程财务分析系统 - 界面重构版
将数据输入移到右侧主区域，左侧边栏只保留功能切换
"""
import streamlit as st
import pandas as pd
from data_loader import DataLoader
from year_generator import YearGenerator, DynamicTableBuilder
from data_models import InputData
import config


def format_dataframe(df: pd.DataFrame, decimals: int = 2) -> pd.DataFrame:
    """
    格式化DataFrame中的数值列为指定小数位数

    Args:
        df: 原始DataFrame
        decimals: 小数位数，默认2位

    Returns:
        格式化后的DataFrame
    """
    df_formatted = df.copy()
    for col in df_formatted.columns:
        # 跳过第一列（通常是"项目"列等非数值列）
        if col == "项目":
            continue

        # 检查列是否为数值类型
        if pd.api.types.is_numeric_dtype(df_formatted[col]):
            # 将列转换为 float 类型，然后格式化为指定小数位数
            df_formatted[col] = df_formatted[col].astype(float)
            df_formatted[col] = df_formatted[col].round(decimals)
        else:
            # 如果不是数值类型但包含数值字符串，尝试转换
            try:
                df_formatted[col] = df_formatted[col].astype(float).round(decimals)
            except (ValueError, TypeError):
                # 无法转换，保持原样
                pass

    return df_formatted


# 页面配置
st.set_page_config(**config.PAGE_CONFIG)

# 初始化session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "数据输入"
if 'construction_period' not in st.session_state:
    st.session_state.construction_period = config.DEFAULT_CONSTRUCTION_PERIOD
if 'operation_period' not in st.session_state:
    st.session_state.operation_period = config.DEFAULT_OPERATION_PERIOD
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# 加载数据
def load_data():
    """加载数据"""
    loader = DataLoader()
    loader.load_all_sheets()
    return loader

data_loader = load_data()

# ===== 左侧边栏：功能切换 =====
with st.sidebar:
    st.header("📋 功能导航")

    st.markdown("---")

    # 功能导航
    page_options = [
        "📝 数据输入",
        "🔬 计算结果",
        "📊 图表分析",
        "📑 报告导出"
    ]

    selected_page = st.radio(
        "选择功能模块",
        page_options,
        label_visibility="collapsed"
    )

    st.session_state.current_page = selected_page.split(" ", 1)[1] if " " in selected_page else selected_page

    st.markdown("---")

    # 当前状态信息
    st.info(f"""
    **当前功能：** {st.session_state.current_page}

    **建设期：** {st.session_state.construction_period}年
    **运营期：** {st.session_state.operation_period}年
    **计算期：** {st.session_state.construction_period + st.session_state.operation_period}年
    """)

    if st.session_state.calculated:
        st.success("✅ 计算已完成")
    else:
        st.warning("⚠️ 尚未计算")


# ===== 右侧主区域 =====
st.title("🏗️ JZGCCW 建设工程财务分析系统")
st.markdown("基于《建设项目经济评价方法与参数(第三版)》编制的财务分析计算系统")

st.divider()


def render_data_input_page():
    """渲染数据输入页面"""
    st.header("📝 数据输入")

    # ===== 全局设置 =====
    with st.expander("⚙️ 全局设置", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            new_construction = st.number_input(
                "建设期（年）",
                min_value=1,
                max_value=10,
                value=st.session_state.construction_period,
                key="cp_input_main"
            )

        with col2:
            new_operation = st.number_input(
                "运营期（年）",
                min_value=1,
                max_value=30,
                value=st.session_state.operation_period,
                key="op_input_main"
            )

        with col3:
            total_period = new_construction + new_operation
            st.metric("计算期", f"{total_period}年")

        # 更新session state
        if new_construction != st.session_state.construction_period or new_operation != st.session_state.operation_period:
            st.session_state.construction_period = new_construction
            st.session_state.operation_period = new_operation
            st.session_state.calculated = False
            st.rerun()

    st.divider()

    # 使用标签页组织不同模块 - 重要提示
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        font-size: 24px;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 8px;
        border: 2px solid #ddd;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff6b6b;
        color: white;
        border: 2px solid #ff6b6b;
        font-size: 26px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.info("""
    👆 **重要提示：请点击下方标签页切换不同的输入模块**
    
    - 🔹 **基础信息与投资**：项目名称、建设期、运营期、项目投资费用
    - 🔹 **资产形成与销售**：固定资产折旧、无形资产摊销、资产销售计划
    - 🔹 **收入成本**：产品销售、材料成本、燃料成本、人工成本、其他费用
    - 🔹 **财务参数**：税收参数、投融资计划、银行借款计划、其他参数
    """)

    # 使用标签页组织不同模块
    tab1, tab2, tab3, tab4 = st.tabs([
        "📌 基础信息与投资",
        "📌 资产形成与销售",
        "📌 收入成本",
        "📌 财务参数"
    ])

    # ===== 标签页1：基础信息与投资 =====
    with tab1:
        # 1. 基础信息
        with st.expander("1️⃣ 基础信息", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                project_name = st.text_input(
                    "项目名称",
                    value="东兴电子产业园三期项目财务分析",
                    key="project_name"
                )
            with col2:
                project_type = st.text_input(
                    "项目类型",
                    value="工业项目",
                    key="project_type"
                )

        st.divider()

        # 2. 项目投资
        with st.expander("2️⃣ 项目投资", expanded=True):
            st.markdown("### 工程费（万元）")

            col1, col2, col3 = st.columns(3)

            with col1:
                building_cost = st.number_input(
                    "建筑工程费",
                    value=67062.86,
                    format="%.2f",
                    key="building_cost",
                    help="主体建筑工程的费用"
                )

            with col2:
                building_equipment = st.number_input(
                    "建筑设备费",
                    value=2360.38,
                    format="%.2f",
                    key="building_equipment",
                    help="设备采购的费用"
                )

            with col3:
                building_install = st.number_input(
                    "建筑设备安装费",
                    value=18299.19,
                    format="%.2f",
                    key="building_install",
                    help="设备安装工程的费用"
                )

            st.markdown("### 工程建设其他费（万元）")

            col1, col2 = st.columns(2)

            with col1:
                management_fee = st.number_input(
                    "项目管理咨询费",
                    value=2994.8,
                    format="%.2f",
                    key="management_fee",
                    help="项目管理和咨询相关费用"
                )
                tech_service_fee = st.number_input(
                    "项目建设技术服务费",
                    value=6036.83,
                    format="%.2f",
                    key="tech_service_fee",
                    help="技术勘察、设计等服务费用"
                )

            with col2:
                supporting_fee = st.number_input(
                    "配套设施等其他费用",
                    value=1737.79,
                    format="%.2f",
                    key="supporting_fee",
                    help="配套设施及其他相关费用"
                )
                land_use_fee = st.number_input(
                    "土地使用费",
                    value=6505.72,
                    format="%.2f",
                    key="land_use_fee",
                    help="土地使用权相关费用"
                )

            # 计算工程费合计
            engineering_fee_total = building_cost + building_equipment + building_install
            other_fee_total = management_fee + tech_service_fee + supporting_fee + land_use_fee
            total_engineering = engineering_fee_total + other_fee_total

            st.markdown("### 预备费")

            col1, col2 = st.columns(2)

            with col1:
                basic_reserve_rate = st.number_input(
                    "基本预备费率(%)",
                    value=10.0,
                    format="%.2f",
                    key="basic_reserve_rate",
                    help="按工程费和工程建设其他费用的百分比计算"
                )

            with col2:
                price_reserve_rate = st.number_input(
                    "涨价预备费率(%)",
                    value=0.0,
                    format="%.2f",
                    key="price_reserve_rate",
                    help="按工程费和工程建设其他费用的百分比计算"
                )

            # 计算预备费
            basic_reserve_fee = total_engineering * basic_reserve_rate / 100
            price_reserve_fee = total_engineering * price_reserve_rate / 100
            total_reserve_fee = basic_reserve_fee + price_reserve_fee

            st.divider()
            st.markdown("### 其他费用")

            col1, col2, col3 = st.columns(3)

            with col1:
                construction_interest = st.number_input(
                    "建设期利息（万元）",
                    value=5721.19,
                    format="%.2f",
                    key="construction_interest",
                    help="建设期借款利息"
                )
            with col2:
                equipment_tax_rate = st.number_input(
                    "设备费增值税率(%)",
                    value=13.0,
                    format="%.2f",
                    key="equipment_tax_rate",
                    help="设备采购增值税税率"
                )
            with col3:
                construction_tax_rate = st.number_input(
                    "建筑安装增值税率(%)",
                    value=9.0,
                    format="%.2f",
                    key="construction_tax_rate",
                    help="建筑工程增值税税率"
                )

            # 项目投资总计
            total_investment = total_engineering + total_reserve_fee + construction_interest
            st.divider()
            st.success(f"""
            **项目总投资：{total_investment:.2f}万元**

            计算公式：
            - 工程费合计 = {engineering_fee_total:.2f}万元（建筑工程费 + 设备费 + 安装费）
            - 工程建设其他费用 = {other_fee_total:.2f}万元
            - 工程费+其他费用 = {total_engineering:.2f}万元
            - 预备费合计 = {total_reserve_fee:.2f}万元
            - 建设期利息 = {construction_interest:.2f}万元
            - **项目总投资 = {total_engineering:.2f} + {total_reserve_fee:.2f} + {construction_interest:.2f} = {total_investment:.2f}万元**
            """)

    # ===== 标签页2：资产形成与销售 =====
    with tab2:
        # 3. 资产形成
        with st.expander("3️⃣ 资产形成"):
            st.markdown("### 固定资产")

            # 房屋建筑
            st.markdown("#### 房屋建筑")
            col1, col2, col3 = st.columns(3)

            with col1:
                building_depr_years = st.number_input(
                    "房屋建筑折旧年限（年）",
                    min_value=1,
                    max_value=50,
                    value=20,
                    key="building_depr_years"
                )

            with col2:
                building_salvage_rate = st.number_input(
                    "房屋建筑残值率（%）",
                    min_value=0.0,
                    max_value=100.0,
                    value=5.0,
                    format="%.2f",
                    key="building_salvage_rate"
                )

            with col3:
                st.info("房屋建筑原值：106057.38 万元")

            # 机械设备
            st.markdown("#### 机械设备")
            col1, col2, col3 = st.columns(3)

            with col1:
                equipment_depr_years = st.number_input(
                    "机械设备折旧年限（年）",
                    min_value=1,
                    max_value=50,
                    value=10,
                    key="equipment_depr_years"
                )

            with col2:
                equipment_salvage_rate = st.number_input(
                    "机械设备残值率（%）",
                    min_value=0.0,
                    max_value=100.0,
                    value=5.0,
                    format="%.2f",
                    key="equipment_salvage_rate"
                )

            with col3:
                st.info("机械设备原值：0.00 万元")

            st.markdown("### 无形资产")

            # 土地使用权
            col1, col2 = st.columns(2)

            with col1:
                land_amort_years = st.number_input(
                    "土地使用权摊销年限（年）",
                    min_value=1,
                    max_value=50,
                    value=50,
                    key="land_amort_years"
                )

            with col2:
                st.info("土地使用权：6505.72 万元")

            # 专利权
            col1, col2 = st.columns(2)

            with col1:
                patent_amort_years = st.number_input(
                    "专利权摊销年限（年）",
                    min_value=1,
                    max_value=50,
                    value=6,
                    key="patent_amort_years"
                )

            with col2:
                st.info("专利权：0.00 万元")

            st.markdown("### 其他资产")

            # 开办费
            col1, col2 = st.columns(2)

            with col1:
                other_amort_years = st.number_input(
                    "其他资产摊销年限（年）",
                    min_value=1,
                    max_value=50,
                    value=5,
                    key="other_amort_years"
                )

            with col2:
                st.info("开办费等其他资产：294.10 万元")

            st.markdown("---")
            st.markdown("### 资产形成汇总")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.info("固定资产合计：106057.38 万元")

            with col2:
                st.info("无形资产合计：6505.72 万元")

            with col3:
                st.info("其他资产合计：294.10 万元")

            with col4:
                st.info("可抵扣进项税：8716.82 万元")

        st.divider()

        # 4. 资产销售计划
        with st.expander("4️⃣ 资产销售计划", expanded=True):
            # 数据流程说明
            st.info("""
            💡 **数据流程**: 基础信息与投资 → 资产形成 → 资产销售计划

            - 房屋建筑原值和土地使用权原值来自上方"基础信息与投资"标签页的计算结果
            - 如需修改原值，请先调整投资数据，系统会自动重新计算
            """)

            st.markdown("### 固定资产销售设置")

            # 🔧 优化1: 从session state获取资产原值（如果已计算）
            if 'asset_formation_calculated' in st.session_state and st.session_state.asset_formation_calculated:
                # 从已计算的资产形成数据中获取
                building_original = st.session_state.get('building_fixed_asset_total', 106057.38)
                land_original = st.session_state.get('land_intangible_asset_total', 6505.72)
                st.success("✅ 资产原值已从投资数据自动计算")
            else:
                # 使用默认值（首次加载）
                building_original = 106057.38
                land_original = 6505.72
                st.info("💡 提示：资产原值将根据'基础信息与投资'标签页的输入自动计算，当前使用默认值")

            col1, col2 = st.columns(2)

            with col1:
                # 出售固定资产占比
                building_sell_ratio = st.number_input(
                    "出售固定资产占比（%）",
                    min_value=0.0,
                    max_value=100.0,
                    value=25.0,
                    format="%.2f",
                    key="building_sell_ratio",
                    help="基数是房屋建筑原值"
                )

                # 计算出售和自持数值
                sales_building_value = building_original * (building_sell_ratio / 100)
                hold_building_value = building_original * (1 - building_sell_ratio / 100)

                st.markdown("#### 出售固定资产数值")
                st.metric(
                    f"占比: {building_sell_ratio:.2f}%",
                    f"{sales_building_value:.2f}万元",
                    help=f"出售固定资产 = 房屋建筑原值 × {building_sell_ratio:.2f}%"
                )

                st.markdown("#### 自持固定资产设置")
                building_hold_ratio = 100.0 - building_sell_ratio
                st.metric(
                    f"自持占比: {building_hold_ratio:.2f}%",
                    f"{hold_building_value:.2f}万元",
                    help=f"自持固定资产 = 房屋建筑原值 × {building_hold_ratio:.2f}%"
                )

            with col2:
                st.markdown("#### 土地使用权销售设置")

                # 出售土地使用权占比
                land_sell_ratio = st.number_input(
                    "出售土地使用权占比（%）",
                    min_value=0.0,
                    max_value=100.0,
                    value=25.0,
                    format="%.2f",
                    key="land_sell_ratio",
                    help="基数是土地使用权原值"
                )

                # 计算出售和自持数值
                sales_land_value = land_original * (land_sell_ratio / 100)
                hold_land_value = land_original * (1 - land_sell_ratio / 100)

                st.markdown("#### 出售土地使用权数值")
                st.metric(
                    f"占比: {land_sell_ratio:.2f}%",
                    f"{sales_land_value:.2f}万元",
                    help=f"出售土地使用权 = 土地使用权原值 × {land_sell_ratio:.2f}%"
                )

                st.markdown("#### 自持土地使用权设置")
                land_hold_ratio = 100.0 - land_sell_ratio
                st.metric(
                    f"自持占比: {land_hold_ratio:.2f}%",
                    f"{hold_land_value:.2f}万元",
                    help=f"自持土地使用权 = 土地使用权原值 × {land_hold_ratio:.2f}%"
                )

            st.divider()
            st.markdown("### 年度资产销售计划")

            # 🔧 优化3: 添加快捷预设按钮
            st.markdown("#### 快捷预设")
            st.info("💡 销售期固定为10年（从运营期第1年开始），如果运营期少于10年，超出年份保持0%")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("📊 均匀分布", key="preset_even"):
                    # 10年平均分配
                    avg_ratio = 100.0 / 10
                    for i in range(10):
                        st.session_state[f"annual_ratio_{i}"] = round(avg_ratio, 1)
                    st.rerun()

            with col2:
                if st.button("📈 前期销售", key="preset_early"):
                    # 第1年50%，其余9年平均分配
                    st.session_state["annual_ratio_0"] = 50.0
                    remaining = 50.0 / 9
                    for i in range(1, 10):
                        st.session_state[f"annual_ratio_{i}"] = round(remaining, 1)
                    st.rerun()

            with col3:
                if st.button("📉 后期销售", key="preset_late"):
                    # 最后1年50%，前面9年平均分配
                    st.session_state["annual_ratio_9"] = 50.0
                    remaining = 50.0 / 9
                    for i in range(9):
                        st.session_state[f"annual_ratio_{i}"] = round(remaining, 1)
                    st.rerun()

            with col4:
                if st.button("🔄 自定义", key="preset_custom"):
                    # 第1年10%，第2-4年各30%，其余0%（默认模式）
                    st.session_state["annual_ratio_0"] = 10.0
                    for i in range(1, 4):
                        st.session_state[f"annual_ratio_{i}"] = 30.0
                    for i in range(4, 10):
                        st.session_state[f"annual_ratio_{i}"] = 0.0
                    st.rerun()

            # 🔧 优化2: 使用数据编辑器替代10个独立输入框
            st.markdown("#### 年度销售比例（%）")
            st.info("""
            💡 **提示**: 直接编辑下方表格，修改各年的销售比例。销售期固定为10年（从运营期第1年开始）。
            - 比例为0表示该年不销售
            - 如果运营期少于10年，超出年份自动保持0%
            """)

            # 固定10年销售期，使用"第1年"到"第10年"标签
            # 构建年度销售比例数据
            sales_data = []
            default_ratios = [10.0, 30.0, 30.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 默认模式：前4年销售
            for i in range(10):
                # 从session state获取已有的值，或使用默认值
                default_ratio = st.session_state.get(f"annual_ratio_{i}", default_ratios[i])
                sales_data.append({
                    '年份': f"第{i+1}年",
                    '销售比例(%)': default_ratio
                })

            import pandas as pd
            df_sales = pd.DataFrame(sales_data)

            # 使用data_editor让用户编辑
            edited_df = st.data_editor(
                df_sales,
                num_rows="fixed",
                hide_index=True,
                column_config={
                    '年份': st.column_config.TextColumn('年份', width='medium'),
                    '销售比例(%)': st.column_config.NumberColumn(
                        '销售比例(%)',
                        min_value=0.0,
                        max_value=100.0,
                        step=1.0,
                        format="%.1f"
                    )
                },
                key="sales_ratio_editor"
            )

            # 将编辑后的值保存到session state
            for i, row in edited_df.iterrows():
                st.session_state[f"annual_ratio_{i}"] = row['销售比例(%)']

            # 总销售价格输入
            st.divider()
            st.markdown("### 销售收入设置")

            total_sales_price = st.number_input(
                "总销售价格（万元）",
                min_value=0.0,
                value=66285.86,
                format="%.2f",
                key="total_sales_price",
                help="所有销售房产的总价格，将按年度销售比例分摊到各年"
            )

            # 🔧 优化4: 添加汇总信息卡片和验证
            st.markdown("### 📊 资产销售计划汇总")

            # 计算汇总数据
            annual_sales_ratios = [row['销售比例(%)'] for _, row in edited_df.iterrows()]
            total_ratio = sum(annual_sales_ratios)

            # 计算年度销售额（固定10年）
            annual_revenues = {}
            for i in range(10):
                year_label = f"第{i+1}年"
                ratio = annual_sales_ratios[i]
                annual_revenues[year_label] = total_sales_price * (ratio / 100.0)

            total_revenue = sum(annual_revenues.values())
            total_cost = sales_building_value * (total_ratio / 100.0)  # 总销售成本
            profit = total_revenue - total_cost
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "销售比例合计",
                    f"{total_ratio:.1f}%",
                    help="所有年度销售比例之和"
                )

            with col2:
                st.metric(
                    "预计总收入",
                    f"{total_revenue:,.2f}万元",
                    help="各年销售收入之和"
                )

            with col3:
                st.metric(
                    "总销售成本",
                    f"{total_cost:,.4f}万元",
                    help="出售固定资产数值 × 销售比例合计"
                )

            with col4:
                st.metric(
                    "预计毛利率",
                    f"{profit_margin:.2f}%",
                    delta=f"{profit:,.2f}万元" if profit >= 0 else f"{profit:,.2f}万元",
                    help="(总收入 - 总成本) / 总收入"
                )

            # 验证警告
            if abs(total_ratio - 100.0) > 0.1:
                st.warning(f"⚠️ 注意：年度销售比例合计为 {total_ratio:.1f}%，建议为100%以确保全部资产售出")
            else:
                st.success("✅ 年度销售比例合计为100%，数据合理")

            # 显示年度销售额计算结果
            st.markdown("#### 年度销售收入明细（万元）")
            st.caption("Row 53: 固定资产销售收入（含税）→ 传递到'6收入'工作表")

            # 使用更紧凑的布局显示10年数据（每行最多5列）
            st.info("💡 以下显示10年销售期的各年销售收入，仅显示销售额大于0的年份")
            sales_years = [f"第{i+1}年" for i in range(10)]
            display_cols = st.columns(5)  # 每行5列
            for i, year_label in enumerate(sales_years):
                revenue = annual_revenues[year_label]
                ratio = annual_sales_ratios[i]
                if revenue > 0 or ratio > 0:  # 只显示有销售额或有销售比例的年份
                    with display_cols[i % 5]:
                        st.metric(
                            year_label,
                            f"{revenue:.2f}",
                            help=f"总销售价格 {total_sales_price:,.2f} × {ratio:.1f}%"
                        )

            # 计算年度销售成本（Row 51）
            st.markdown("#### 年度销售成本明细（万元）")
            st.caption("Row 51: 用于出售的固定资产 → 传递到'5-4折旧'工作表")

            annual_sales_costs = {}
            for i in range(10):
                year_label = f"第{i+1}年"
                ratio = annual_sales_ratios[i]
                annual_sales_costs[year_label] = sales_building_value * (ratio / 100.0)

            cost_cols = st.columns(5)
            for i, year_label in enumerate(sales_years):
                cost = annual_sales_costs[year_label]
                ratio = annual_sales_ratios[i]
                if cost > 0 or ratio > 0:
                    with cost_cols[i % 5]:
                        st.metric(
                            year_label,
                            f"{cost:.4f}",
                            help=f"出售固定资产 {sales_building_value:.4f} × {ratio:.1f}%"
                        )

            # 计算年度土地摊销（Row 52）
            st.markdown("#### 年度土地摊销明细（万元）")
            st.caption("Row 52: 出售固定资产对应的土地使用权摊销额")

            annual_land_amortizations = {}
            for i in range(10):
                year_label = f"第{i+1}年"
                ratio = annual_sales_ratios[i]
                annual_land_amortizations[year_label] = sales_land_value * (ratio / 100.0)

            land_cols = st.columns(5)
            for i, year_label in enumerate(sales_years):
                land_amort = annual_land_amortizations[year_label]
                ratio = annual_sales_ratios[i]
                if land_amort > 0 or ratio > 0:
                    with land_cols[i % 5]:
                        st.metric(
                            year_label,
                            f"{land_amort:.4f}",
                            help=f"出售土地使用权 {sales_land_value:.4f} × {ratio:.1f}%"
                        )

            # 保存资产销售计划数据到session state（供后续计算使用）
            st.session_state.sales_plan_building_sell_ratio = building_sell_ratio
            st.session_state.sales_plan_land_sell_ratio = land_sell_ratio
            st.session_state.sales_plan_sales_building_value = sales_building_value
            st.session_state.sales_plan_hold_building_value = hold_building_value
            st.session_state.sales_plan_sales_land_value = sales_land_value
            st.session_state.sales_plan_hold_land_value = hold_land_value
            st.session_state.sales_plan_total_sales_price = total_sales_price
            st.session_state.sales_plan_annual_sales_ratios = annual_sales_ratios
            st.session_state.sales_plan_annual_revenues = annual_revenues
            st.session_state.sales_plan_annual_costs = annual_sales_costs
            st.session_state.sales_plan_annual_land_amortizations = annual_land_amortizations
            st.session_state.sales_plan_data_entered = True

            st.success("✅ 资产销售计划数据已保存，可用于后续计算")

    # ===== 标签页3：收入成本 =====
    with tab3:
        # 5. 产品销售收入（按年）
        with st.expander("5️⃣ 产品销售收入（万元）"):
            st.markdown("### 年度销售收入")

            year_generator = YearGenerator(st.session_state.construction_period, st.session_state.operation_period)
            years = year_generator.generate_year_names()

            sales_revenue = {}

            # 完整计算期年限（建设期 + 运营期）
            for year in years:
                year_num = year_generator.get_year_index(year)
                # 建设期设为0，运营期输入销售收入
                if year_generator.is_construction_year(year_num):
                    st.session_state[f"sales_{year}"] = 0.0  # 建设期自动设为0
                else:
                    sales_revenue[year] = st.number_input(year, value=10000.0, format="%.2f", key=f"sales_{year}")

        # 6. 外购材料成本（按年）
        with st.expander("6️⃣ 外购材料成本（万元）"):
            st.markdown("### 年度材料成本")

            # 完整计算期年限（建设期 + 运营期）
            for year in years:
                year_num = year_generator.get_year_index(year)
                # 建设期设为0，运营期输入材料成本
                if year_generator.is_construction_year(year_num):
                    # 建设期自动设为0
                    for i in range(1, 9):
                        st.session_state[f"mat{i}_{year}"] = 0.0
                else:
                    with st.expander(f"{year}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            mat_1 = st.number_input("材料1", value=100.0, format="%.2f", key=f"mat1_{year}")
                            mat_2 = st.number_input("材料2", value=150.0, format="%.2f", key=f"mat2_{year}")
                            mat_3 = st.number_input("材料3", value=200.0, format="%.2f", key=f"mat3_{year}")
                            mat_4 = st.number_input("材料4", value=120.0, format="%.2f", key=f"mat4_{year}")
                        with col2:
                            mat_5 = st.number_input("材料5", value=180.0, format="%.2f", key=f"mat5_{year}")
                            mat_6 = st.number_input("材料6", value=90.0, format="%.2f", key=f"mat6_{year}")
                            mat_7 = st.number_input("材料7", value=110.0, format="%.2f", key=f"mat7_{year}")
                            mat_8 = st.number_input("材料8", value=80.0, format="%.2f", key=f"mat8_{year}")

        # 7. 外购燃料及动力（按年）
        with st.expander("7️⃣ 外购燃料及动力（万元）"):
            st.markdown("### 年度燃料及动力成本")

            # 完整计算期年限（建设期 + 运营期）
            for year in years:
                year_num = year_generator.get_year_index(year)
                # 建设期设为0，运营期输入燃料成本
                if year_generator.is_construction_year(year_num):
                    # 建设期自动设为0
                    for i in range(1, 9):
                        st.session_state[f"fuel{i}_{year}"] = 0.0
                else:
                    with st.expander(f"{year}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            fuel_1 = st.number_input("燃料动力1", value=50.0, format="%.2f", key=f"fuel1_{year}")
                            fuel_2 = st.number_input("燃料动力2", value=60.0, format="%.2f", key=f"fuel2_{year}")
                            fuel_3 = st.number_input("燃料动力3", value=40.0, format="%.2f", key=f"fuel3_{year}")
                            fuel_4 = st.number_input("燃料动力4", value=70.0, format="%.2f", key=f"fuel4_{year}")
                        with col2:
                            fuel_5 = st.number_input("燃料动力5", value=55.0, format="%.2f", key=f"fuel5_{year}")
                            fuel_6 = st.number_input("燃料动力6", value=65.0, format="%.2f", key=f"fuel6_{year}")
                            fuel_7 = st.number_input("燃料动力7", value=45.0, format="%.2f", key=f"fuel7_{year}")
                            fuel_8 = st.number_input("燃料动力8", value=75.0, format="%.2f", key=f"fuel8_{year}")

        # 8. 工资福利成本
        with st.expander("8️⃣ 工资福利成本（万元）"):
            st.markdown("### 人员构成及工资")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 行政管理人员")
                admin_persons = st.number_input("人数", value=5, min_value=0, key="admin_persons")
                admin_salary = st.number_input("人均年工资（万元）", value=12.0, format="%.2f", key="admin_salary")

            with col2:
                st.markdown("#### 专业技术人员")
                tech_persons = st.number_input("人数", value=15, min_value=0, key="tech_persons")
                tech_salary = st.number_input("人均年工资（万元）", value=10.0, format="%.2f", key="tech_salary")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 安保人员")
                security_persons = st.number_input("人数", value=8, min_value=0, key="security_persons")
                security_salary = st.number_input("人均年工资（万元）", value=8.0, format="%.2f", key="security_salary")

            with col2:
                st.markdown("#### 保洁人员")
                cleaning_persons = st.number_input("人数", value=6, min_value=0, key="cleaning_persons")
                cleaning_salary = st.number_input("人均年工资（万元）", value=6.0, format="%.2f", key="cleaning_salary")

            welfare_rate = st.number_input("福利费率（%）", value=14.0, format="%.2f", key="welfare_rate")

        # 9. 修理费及其他费用
        with st.expander("9️⃣ 修理费及其他费用"):
            st.markdown("### 费用率设置（%）")

            col1, col2 = st.columns(2)

            with col1:
                repair_rate = st.number_input("修理费率", value=0.5, format="%.2f", key="repair_rate",
                                      help="按固定资产原值的百分比")
                other_mfg_rate = st.number_input("其他制造费率", value=2.0, format="%.2f", key="other_mfg_rate")

            with col2:
                other_mgt_rate = st.number_input("其他管理费率", value=1.5, format="%.2f", key="other_mgt_rate")
                other_sales_rate = st.number_input("其他营业费率", value=1.0, format="%.2f", key="other_sales_rate")

    # ===== 标签页4：财务参数 =====
    with tab4:
        # 10. 税收参数
        with st.expander("🔟 税收参数"):
            st.markdown("### 税费设置")

            col1, col2 = st.columns(2)

            with col1:
                corporate_tax_rate = st.number_input("企业所得税税率（%）", value=25.0, format="%.2f", key="corporate_tax_rate")
                city_tax_rate = st.number_input("城市维护建设税税率（%）", value=7.0, format="%.2f", key="city_tax_rate")

            with col2:
                education_tax_rate = st.number_input("教育税附加及地方教育税附加税率（%）", value=5.0, format="%.2f", key="education_tax_rate")
                discount_rate = st.number_input("净现值内部收益率 ic", value=6.0, format="%.2f", key="discount_rate")

        # 11. 投融资计划
        with st.expander("1️⃣1️⃣ 投融资计划（按年）"):
            st.markdown("### 建设期资金投入")

            year_generator = YearGenerator(st.session_state.construction_period, st.session_state.operation_period)
            years = year_generator.generate_year_names()
            investment_years = years[:st.session_state.construction_period]  # 只显示建设期年份

            for year in investment_years:
                st.markdown(f"#### {year}")
                col1, col2 = st.columns(2)

                with col1:
                    equity_input = st.number_input("自有资金投入（万元）", value=10000.0, format="%.2f", key=f"equity_{year}")

                with col2:
                    loan_input = st.number_input("借款金额（万元）", value=5000.0, format="%.2f", key=f"loan_{year}")

        # 12. 银行借款计划
        with st.expander("1️⃣2️⃣ 银行借款计划"):
            st.markdown("### 借款参数")

            col1, col2 = st.columns(2)

            with col1:
                loan_interest_rate = st.number_input("年利率（%）", value=5.88, format="%.2f", key="loan_interest_rate")
                repayment_years = st.number_input("还款期限（年）", min_value=1, max_value=30, value=15, key="repayment_years")

            with col2:
                repayment_method = st.selectbox("还款方式", options=["等额本金", "等额本息", "按期还息到期还本"], key="repayment_method")
                grace_period = st.number_input("宽限期（年）", min_value=0, max_value=5, value=2, key="grace_period")

            st.markdown("### 按年借款安排")

            for year in investment_years:
                yearly_loan = st.number_input(f"{year}借款金额（万元）", value=5000.0, format="%.2f", key=f"yearly_loan_{year}")

        # 13. 其他参数
        with st.expander("1️⃣3️⃣ 其他参数"):
            st.markdown("### 利润分配参数")

            col1, col2 = st.columns(2)

            with col1:
                reserve_fund_rate = st.number_input("盈余公积金比率（%）", value=10.0, format="%.2f", key="reserve_fund_rate")
                loss_carryforward_years = st.number_input("亏损弥补年限（年）", min_value=0, max_value=10, value=5, key="loss_carryforward_years")

            with col2:
                tax_benefit_coeff = st.number_input("年度税收优惠系数", value=1.0, format="%.2f", key="tax_benefit_coeff")
                subsidy_income = st.number_input("补贴收入（万元）", value=0.0, format="%.2f", key="subsidy_income")

    # 计算按钮
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🚀 执行计算", type="primary", use_container_width=True):
            with st.spinner("正在计算中..."):
                try:
                    # 收集输入数据
                    from input_collector import collect_input_data
                    from calculation_engine import CalculationEngine

                    input_data = collect_input_data(st.session_state.construction_period, st.session_state.operation_period)

                    # 创建计算引擎
                    year_generator = YearGenerator(st.session_state.construction_period, st.session_state.operation_period)
                    calc_engine = CalculationEngine(year_generator, input_data)

                    # 执行计算
                    results = calc_engine.run_all_calculations()

                    # 保存结果到session state
                    st.session_state.calculated = True
                    st.session_state.calculation_results = results
                    st.session_state.calculation_engine = calc_engine

                    st.success("✅ 计算完成！")
                    st.info("📊 请在【计算结果】页面查看计算表格")

                except Exception as e:
                    st.error(f"❌ 计算过程中发生错误: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


def render_results_page():
    """渲染计算结果页面"""
    st.header("📊 计算结果")

    # 检查是否有计算结果
    if 'calculated' in st.session_state and st.session_state.calculated:
        if 'calculation_results' in st.session_state and st.session_state.calculation_results:
            results = st.session_state.calculation_results

            # 显示所有表格
            available_sheets = list(results.keys())

            if not available_sheets:
                st.warning("暂无可显示的计算表")
            else:
                # 直接显示所有计算结果表格
                for sheet_name in available_sheets:
                    st.markdown(f"#### {config.SHEET_MAPPING.get(sheet_name, sheet_name)}")

                    # 显示计算结果表格（格式化为2位小数）
                    df = results[sheet_name]
                    df_display = format_dataframe(df, decimals=2)
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        height=min(400, 100 + len(df) * 30)
                    )

                    # 下载按钮（使用格式化后的数据，也是2位小数）
                    csv = df_display.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label=f"下载 {config.SHEET_MAPPING.get(sheet_name, sheet_name)}",
                        data=csv,
                        file_name=f"{sheet_name}_result.csv",
                        mime="text/csv"
                    )

                    st.divider()  # 表格之间的分隔线
    else:
        # 如果没有计算结果，显示原始Excel数据
        st.markdown("### 选择要查看的原始数据表")

        selected_sheets = st.multiselect(
            "选择表格（可多选）",
            options=list(config.SHEET_MAPPING.keys()),
            format_func=lambda x: f"{x} - {config.SHEET_MAPPING[x]}",
            default=["财务分析结果汇总"]
        )

        if selected_sheets:
            for sheet_name in selected_sheets:
                st.markdown(f"#### {config.SHEET_MAPPING[sheet_name]}")
                original_data = data_loader.get_sheet(sheet_name)
                # 格式化为2位小数显示
                original_data_display = format_dataframe(original_data, decimals=2)
                st.dataframe(
                    original_data_display,
                    use_container_width=True,
                    height=300
                )

                # 下载按钮
                csv = original_data_display.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    f"下载 {config.SHEET_MAPPING[sheet_name]}",
                    data=csv,
                    file_name=f"{sheet_name}.csv",
                    mime="text/csv"
                )

                st.divider()
        else:
            st.info("请选择要查看的表格")


def render_charts_page():
    """渲染图表分析页面"""
    st.header("📊 图表分析")

    if not st.session_state.calculated:
        st.warning("⚠️ 请先在【数据输入】页面完成数据填写并执行计算")
        return

    st.info("📝 图表分析功能待完善")


def render_export_page():
    """渲染报告导出页面"""
    st.header("📑 报告导出")

    if not st.session_state.calculated:
        st.warning("⚠️ 请先在【数据输入】页面完成数据填写并执行计算")
        return

    st.info("📝 报告导出功能待完善")


# ===== 页面渲染逻辑 =====
# 根据选择的功能显示不同内容
if st.session_state.current_page == "数据输入":
    render_data_input_page()
elif st.session_state.current_page == "计算结果":
    render_results_page()
elif st.session_state.current_page == "图表分析":
    render_charts_page()
elif st.session_state.current_page == "报告导出":
    render_export_page()


# 页脚
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
        JZGCCW 建设工程财务分析系统 v3.0 | 基于《建设项目经济评价方法与参数(第三版)》
    </div>
    """,
    unsafe_allow_html=True
)
