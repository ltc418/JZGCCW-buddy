"""
输入表单模块
"""
import streamlit as st
import pandas as pd
import config
from utils import generate_years


class InputForms:
    """输入表单类"""

    def __init__(self, data_loader):
        """
        初始化输入表单

        Args:
            data_loader: DataLoader实例
        """
        self.data_loader = data_loader
        self.input_data = {}

    def render_global_settings(self):
        """
        渲染全局设置区域（页面顶部）

        Returns:
            dict: 全局设置数据
        """
        st.markdown("## ⚙️ 全局设置")

        col1, col2, col3 = st.columns(3)

        with col1:
            construction_period = st.number_input(
                "建设期（年）",
                min_value=1,
                max_value=10,
                value=config.DEFAULT_CONSTRUCTION_PERIOD,
                key="construction_period",
                help="项目建设所需的年限"
            )

        with col2:
            operation_period = st.number_input(
                "运营期（年）",
                min_value=1,
                max_value=30,
                value=config.DEFAULT_OPERATION_PERIOD,
                key="operation_period",
                help="项目运营的年限"
            )

        with col3:
            total_period = construction_period + operation_period
            st.metric("计算期", f"{total_period}年")

        st.divider()

        return {
            "construction_period": construction_period,
            "operation_period": operation_period,
            "total_period": total_period
        }

    def render_module_1_basic_info(self, module_data):
        """
        渲染模块1：基础信息

        Args:
            module_data: 模块数据
        """
        with st.expander("1️⃣ 基础信息", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                project_name = st.text_input(
                    "项目名称",
                    value=module_data.get("项目名称", ""),
                    key="project_name"
                )

            with col2:
                project_type = st.text_input(
                    "项目类型",
                    value=module_data.get("项目类型", ""),
                    key="project_type"
                )

            self.input_data["1. 基础信息"] = {
                "项目名称": project_name,
                "项目类型": project_type
            }

    def render_module_2_project_investment(self, module_data, years):
        """
        渲染模块2：项目投资

        Args:
            module_data: 模块数据
            years: 年份列表
        """
        with st.expander("2️⃣ 项目投资", expanded=True):
            st.markdown("### 建筑安装工程费")

            col1, col2, col3 = st.columns(3)

            with col1:
                building_cost = st.number_input(
                    "建筑工程费（万元）",
                    value=module_data.get("建筑工程费", 0.0),
                    format="%.2f",
                    key="building_cost",
                    help="主体建筑工程的费用"
                )

            with col2:
                installation_cost = st.number_input(
                    "安装工程费（万元）",
                    value=module_data.get("安装工程费", 0.0),
                    format="%.2f",
                    key="installation_cost",
                    help="设备安装工程的费用"
                )

            with col3:
                other_cost = st.number_input(
                    "工程建设其他费用（万元）",
                    value=module_data.get("工程建设其他费用", 0.0),
                    format="%.2f",
                    key="other_cost",
                    help="包括土地使用费、勘察设计费等工程建设相关费用"
                )

            # 工程费汇总显示
            st.divider()
            st.markdown("### 📊 工程费汇总")

            engineering_fee_total = building_cost + installation_cost
            total_engineering = engineering_fee_total + other_cost

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "建筑工程费",
                    f"{building_cost:.2f}万元",
                    help="主体建筑工程费用"
                )
            with col2:
                st.metric(
                    "安装工程费",
                    f"{installation_cost:.2f}万元",
                    help="设备安装工程费用"
                )
            with col3:
                st.metric(
                    "工程费合计",
                    f"{engineering_fee_total:.2f}万元",
                    help="建筑工程费 + 安装工程费"
                )
            with col4:
                st.metric(
                    "工程费+其他费用",
                    f"{total_engineering:.2f}万元",
                    help="工程费合计 + 工程建设其他费用"
                )

            st.markdown("### 预备费")

            # 费率基数说明
            st.info("""
            **预备费计算基数说明：**
            - **基本预备费基数** = 建筑工程费 + 安装工程费 + 工程建设其他费用
            - **涨价预备费基数** = 建筑工程费 + 安装工程费 + 工程建设其他费用
            """)

            col1, col2 = st.columns(2)

            with col1:
                basic_reserve_rate = st.number_input(
                    "基本预备费率（%）",
                    value=module_data.get("基本预备费率", 0.0),
                    format="%.2f",
                    key="basic_reserve_rate",
                    help="按工程费和工程建设其他费用的百分比计算"
                )

            with col2:
                price_reserve_rate = st.number_input(
                    "涨价预备费率（%）",
                    value=module_data.get("涨价预备费率", 0.0),
                    format="%.2f",
                    key="price_reserve_rate",
                    help="按工程费和工程建设其他费用的百分比计算"
                )

            # 实时显示预备费结果
            basic_reserve_fee = total_engineering * basic_reserve_rate / 100
            price_reserve_fee = total_engineering * price_reserve_rate / 100
            total_reserve_fee = basic_reserve_fee + price_reserve_fee

            st.divider()
            st.markdown("### 💰 预备费计算结果")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "基本预备费",
                    f"{basic_reserve_fee:.2f}万元",
                    help=f"{total_engineering:.2f} × {basic_reserve_rate:.2f}%"
                )
            with col2:
                st.metric(
                    "涨价预备费",
                    f"{price_reserve_fee:.2f}万元",
                    help=f"{total_engineering:.2f} × {price_reserve_rate:.2f}%"
                )
            with col3:
                st.metric(
                    "预备费合计",
                    f"{total_reserve_fee:.2f}万元",
                    help="基本预备费 + 涨价预备费"
                )

            # 投资总计
            total_investment = total_engineering + total_reserve_fee
            st.divider()
            st.success(f"""
            **项目总投资：{total_investment:.2f}万元**

            计算公式：
            - 工程费 + 其他费用 = {total_engineering:.2f}万元
            - 预备费合计 = {total_reserve_fee:.2f}万元
            - 项目总投资 = {total_engineering:.2f} + {total_reserve_fee:.2f} = {total_investment:.2f}万元
            """)

            self.input_data["2. 项目投资"] = {
                "建筑工程费": building_cost,
                "安装工程费": installation_cost,
                "工程建设其他费用": other_cost,
                "基本预备费率": basic_reserve_rate,
                "涨价预备费率": price_reserve_rate,
                # 计算结果也保存
                "基本预备费": basic_reserve_fee,
                "涨价预备费": price_reserve_fee,
                "预备费合计": total_reserve_fee,
                "项目总投资": total_investment
            }

    def render_module_3_asset_formation(self, module_data):
        """
        渲染模块3：资产形成

        Args:
            module_data: 模块数据
        """
        with st.expander("3️⃣ 资产形成"):
            col1, col2, col3 = st.columns(3)

            with col1:
                depreciation_years = st.number_input(
                    "固定资产折旧年限（年）",
                    min_value=1,
                    max_value=50,
                    value=int(module_data.get("固定资产折旧年限", 20)),
                    key="depreciation_years"
                )

            with col2:
                salvage_rate = st.number_input(
                    "残值率（%）",
                    min_value=0.0,
                    max_value=100.0,
                    value=module_data.get("残值率", 5.0),
                    format="%.2f",
                    key="salvage_rate"
                )

            with col3:
                amortization_years = st.number_input(
                    "无形资产摊销年限（年）",
                    min_value=1,
                    max_value=50,
                    value=int(module_data.get("无形资产摊销年限", 50)),  # Excel中为50
                    key="amortization_years"
                )

            self.input_data["3. 资产形成"] = {
                "固定资产折旧年限": depreciation_years,
                "残值率": salvage_rate,
                "无形资产摊销年限": amortization_years
            }

    def render_module_asset_sales(self, module_data, years, calculation_results=None):
        """
        渲染资产销售计划模块

        参照Excel"1 建筑工程财务模型参数"第48-55行

        Args:
            module_data: 模块数据
            years: 年份列表
            calculation_results: 计算结果（可选），用于显示实际数值
        """
        with st.expander("💰 资产销售计划", expanded=True):
            st.markdown("### 固定资产销售设置")

            col1, col2 = st.columns(2)

            with col1:
                # 出售固定资产占比
                building_sell_ratio = st.number_input(
                    "出售固定资产占比（%）",
                    min_value=0.0,
                    max_value=100.0,
                    value=module_data.get("building_sell_ratio", 25.0),
                    format="%.2f",
                    key="building_sell_ratio",
                    help="基数是房屋建筑原值"
                )

                # 显示出售和自持数值
                building_sell_value = module_data.get("sales_building_value", 0.0)
                building_hold_value = module_data.get("hold_building_value", 0.0)

                st.markdown("#### 出售固定资产数值")
                st.metric(
                    f"占比: {building_sell_ratio:.2f}%",
                    f"{building_sell_value:.2f}万元",
                    help=f"出售固定资产 = 房屋建筑原值 × {building_sell_ratio:.2f}%"
                )

                st.markdown("#### 自持固定资产设置")
                building_hold_ratio = 100.0 - building_sell_ratio
                st.metric(
                    f"自持占比: {building_hold_ratio:.2f}%",
                    f"{building_hold_value:.2f}万元",
                    help=f"自持固定资产 = 房屋建筑原值 × {building_hold_ratio:.2f}%"
                )

            with col2:
                st.markdown("#### 土地使用权销售设置")

                # 出售土地使用权占比
                land_sell_ratio = st.number_input(
                    "出售土地使用权占比（%）",
                    min_value=0.0,
                    max_value=100.0,
                    value=module_data.get("land_sell_ratio", 25.0),
                    format="%.2f",
                    key="land_sell_ratio",
                    help="基数是土地使用权原值"
                )

                # 显示出售和自持数值
                land_sell_value = module_data.get("sales_land_value", 0.0)
                land_hold_value = module_data.get("hold_land_value", 0.0)

                st.markdown("#### 出售土地使用权数值")
                st.metric(
                    f"占比: {land_sell_ratio:.2f}%",
                    f"{land_sell_value:.2f}万元",
                    help=f"出售土地使用权 = 土地使用权原值 × {land_sell_ratio:.2f}%"
                )

                st.markdown("#### 自持土地使用权设置")
                land_hold_ratio = 100.0 - land_sell_ratio
                st.metric(
                    f"自持占比: {land_hold_ratio:.2f}%",
                    f"{land_hold_value:.2f}万元",
                    help=f"自持土地使用权 = 土地使用权原值 × {land_hold_ratio:.2f}%"
                )
            
            st.divider()
            st.markdown("### 年度资产销售计划")
            st.info("""
            **说明**: 横向布置年份，预留10年的位置，由用户填写每年的销售比例。
            销售额将根据销售比例自动计算。
            """)
            
            # 年度销售比例输入（横向布置，10年）
            st.markdown("#### 年度销售比例")
            cols = st.columns(10)
            annual_sales_ratios = []
            
            for i, year in enumerate(years[:10]):  # 最多10年
                with cols[i]:
                    ratio = st.number_input(
                        f"{year}",
                        min_value=0.0,
                        max_value=100.0,
                        value=module_data.get(f"ratio_{i}", 0.0),
                        format="%.1f",
                        key=f"annual_ratio_{i}",
                        help=f"{year}年销售比例(%)"
                    )
                    annual_sales_ratios.append(ratio)
            
            # 总销售价格输入
            st.divider()
            st.markdown("### 销售收入设置")
            
            total_sales_price = st.number_input(
                "总销售价格（万元）",
                min_value=0.0,
                value=module_data.get("total_sales_price", 0.0),
                format="%.2f",
                key="total_sales_price",
                help="所有销售房产的总价格，将按年度销售比例分摊到各年"
            )
            
            # 显示年度销售额计算结果
            st.markdown("#### 年度销售额（万元）")
            sales_cols = st.columns(10)
            annual_sales_revenue = {}
            
            for i, year in enumerate(years[:10]):
                with sales_cols[i]:
                    # 按销售比例计算销售额
                    revenue = total_sales_price * (annual_sales_ratios[i] / 100.0) if i < len(annual_sales_ratios) else 0.0
                    annual_sales_revenue[year] = revenue
                    
                    if revenue > 0:
                        st.metric(
                            f"{year}",
                            f"{revenue:.2f}",
                            help=f"总销售价格 × {annual_sales_ratios[i]:.1f}%"
                        )
                    else:
                        st.metric(f"{year}", "0.00")
            
            # 保存输入数据
            self.input_data["4. 资产销售计划"] = {
                "building_sell_ratio": building_sell_ratio,
                "building_hold_ratio": building_hold_ratio,
                "land_sell_ratio": land_sell_ratio,
                "land_hold_ratio": land_hold_ratio,
                "annual_sales_ratios": annual_sales_ratios,
                "total_sales_price": total_sales_price,
                "annual_sales_revenue": annual_sales_revenue
            }

    def render_module_7_sales_revenue(self, module_data, years):
        """
        渲染模块7：产品销售收入（按年横向布置）

        Args:
            module_data: 模块数据
            years: 年份列表
        """
        with st.expander("7️⃣ 产品销售收入"):
            st.markdown("### 年度销售收入（万元）")

            # 创建按年输入的数据框
            st.write(f"请输入{len(years)}年的销售收入：")

            revenue_data = {}
            for i, year in enumerate(years):
                if i < 10:  # 限制显示数量，避免过长
                    revenue_data[year] = st.number_input(
                        year,
                        value=module_data.get(year, 0.0),
                        format="%.2f",
                        key=f"revenue_{i}"
                    )

            self.input_data["7. 产品销售收入"] = revenue_data

    def render_module_8_material_cost(self, module_data, years):
        """
        渲染模块8：外购材料成本

        Args:
            module_data: 模块数据
            years: 年份列表
        """
        with st.expander("8️⃣ 外购材料成本"):
            st.markdown("### 年度材料成本（万元）")

            material_types = [
                "材料1", "材料2", "材料3", "材料4",
                "材料5", "材料6", "材料7", "材料8"
            ]

            cost_data = {}
            for material in material_types:
                st.markdown(f"**{material}**")
                material_data = {}
                for i, year in enumerate(years):
                    if i < 10:  # 限制显示数量
                        key = f"{material}_{i}"
                        material_data[year] = st.number_input(
                            year,
                            value=module_data.get(key, 0.0),
                            format="%.2f",
                            key=f"material_{material}_{i}"
                        )
                cost_data[material] = material_data

            self.input_data["8. 外购材料成本"] = cost_data

    def render_all_modules(self, construction_period, operation_period):
        """
        渲染所有输入模块

        Args:
            construction_period: 建设期（年）
            operation_period: 运营期（年）

        Returns:
            dict: 所有输入数据
        """
        years = generate_years(construction_period, operation_period)

        # 加载输入数据
        input_values = self.data_loader.extract_input_values(
            construction_period, operation_period
        )

        # 渲染各个模块
        self.render_module_1_basic_info(input_values.get("1. 基础信息", {}))
        self.render_module_2_project_investment(input_values.get("2. 项目投资", {}), years)
        self.render_module_3_asset_formation(input_values.get("3. 资产形成", {}))

        # 渲染资产销售计划模块（新增）
        self.render_module_asset_sales(input_values.get("4. 资产销售计划", {}), years)

        # TODO: 实现其他模块
        # self.render_module_4_sales_plan(...)
        # self.render_module_5_investment_plan(...)
        # ...

        # 渲染按年输入的模块
        self.render_module_7_sales_revenue(input_values.get("7. 产品销售收入", {}), years)
        self.render_module_8_material_cost(input_values.get("8. 外购材料成本", {}), years)

        return self.input_data
