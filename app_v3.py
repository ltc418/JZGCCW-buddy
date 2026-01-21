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

    # 使用标签页组织不同模块
    tab1, tab2, tab3, tab4 = st.tabs([
        "基础信息与投资",
        "资产形成与销售",
        "收入成本",
        "财务参数"
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

            # 项目投资总计
            total_investment = total_engineering + total_reserve_fee
            st.divider()
            st.success(f"""
            **项目静态总投资：{total_investment:.2f}万元**

            计算公式：
            - 工程费合计 = {engineering_fee_total:.2f}万元（建筑工程费 + 设备费 + 安装费）
            - 工程建设其他费用 = {other_fee_total:.2f}万元
            - 工程费+其他费用 = {total_engineering:.2f}万元
            - 预备费合计 = {total_reserve_fee:.2f}万元
            - 项目静态总投资 = {total_engineering:.2f} + {total_reserve_fee:.2f} = {total_investment:.2f}万元
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
            st.markdown("### 固定资产销售设置")

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
                building_original = 106057.38  # 房屋建筑原值
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
                land_original = 6505.72  # 土地使用权原值
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

            st.markdown("---")
            st.markdown("### 年度资产销售计划")
            st.info("""
            **说明**: 横向布置年份，预留10年的位置，由用户填写每年的销售比例。
            销售额将根据销售比例自动计算。
            """)

            # 年度销售比例输入（横向布置，10年）
            year_generator = YearGenerator(st.session_state.construction_period, st.session_state.operation_period)
            years = year_generator.generate_year_names()

            st.markdown("#### 年度销售比例（%）")
            cols = st.columns(10)
            annual_sales_ratios = []

            for i in range(10):  # 最多10年
                with cols[i]:
                    if i < len(years) and year_generator.is_operation_year(year_generator.get_year_index(years[i])):
                        ratio = st.number_input(
                            f"{years[i]}",
                            min_value=0.0,
                            max_value=100.0,
                            value=0.1 if i == 0 else 0.3,
                            format="%.1f",
                            key=f"annual_ratio_{i}",
                            help=f"{years[i]}年销售比例(%)"
                        )
                        annual_sales_ratios.append((years[i], ratio))
                    else:
                        st.markdown(f"**{i+1}**")
                        st.text("-")

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

            # 显示年度销售额计算结果
            st.markdown("#### 年度销售额（万元）")
            sales_cols = st.columns(10)

            for i in range(10):
                with sales_cols[i]:
                    if i < len(annual_sales_ratios):
                        year, ratio = annual_sales_ratios[i]
                        # 按销售比例计算销售额
                        revenue = total_sales_price * (ratio / 100.0)
                        if revenue > 0:
                            st.metric(
                                f"{year}",
                                f"{revenue:.2f}",
                                help=f"总销售价格 × {ratio:.1f}%"
                            )
                        else:
                            st.metric(f"{year}", "0.00")
                    else:
                        st.markdown(f"**{i+1}**")
                        st.text("-")

    # ===== 标签页3：收入成本 =====
    with tab3:
        st.info("📝 收入成本数据输入功能待完善")

    # ===== 标签页4：财务参数 =====
    with tab4:
        st.info("📝 财务参数输入功能待完善")

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
                        f"下载 {config.SHEET_MAPPING.get(sheet_name, sheet_name)}",
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
        JZGCCW 建设工程财务分析系统 v2.0 | 基于《建设项目经济评价方法与参数(第三版)》
    </div>
    """,
    unsafe_allow_html=True
)
