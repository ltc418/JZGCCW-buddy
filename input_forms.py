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
                    key="building_cost"
                )

            with col2:
                installation_cost = st.number_input(
                    "安装工程费（万元）",
                    value=module_data.get("安装工程费", 0.0),
                    format="%.2f",
                    key="installation_cost"
                )

            with col3:
                other_cost = st.number_input(
                    "工程建设其他费用（万元）",
                    value=module_data.get("工程建设其他费用", 0.0),
                    format="%.2f",
                    key="other_cost"
                )

            st.markdown("### 预备费")

            col1, col2 = st.columns(2)

            with col1:
                basic_reserve = st.number_input(
                    "基本预备费率（%）",
                    value=module_data.get("基本预备费率", 0.0),
                    format="%.2f",
                    key="basic_reserve_rate"
                )

            with col2:
                price_reserve = st.number_input(
                    "涨价预备费率（%）",
                    value=module_data.get("涨价预备费率", 0.0),
                    format="%.2f",
                    key="price_reserve_rate"
                )

            self.input_data["2. 项目投资"] = {
                "建筑工程费": building_cost,
                "安装工程费": installation_cost,
                "工程建设其他费用": other_cost,
                "基本预备费率": basic_reserve,
                "涨价预备费率": price_reserve
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
                    value=int(module_data.get("无形资产摊销年限", 10)),
                    key="amortization_years"
                )

            self.input_data["3. 资产形成"] = {
                "固定资产折旧年限": depreciation_years,
                "残值率": salvage_rate,
                "无形资产摊销年限": amortization_years
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

        # TODO: 实现其他模块
        # self.render_module_4_sales_plan(...)
        # self.render_module_5_investment_plan(...)
        # ...

        # 渲染按年输入的模块
        self.render_module_7_sales_revenue(input_values.get("7. 产品销售收入", {}), years)
        self.render_module_8_material_cost(input_values.get("8. 外购材料成本", {}), years)

        return self.input_data
