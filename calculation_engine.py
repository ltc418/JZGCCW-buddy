"""
财务计算引擎
整合所有计算模块，提供统一的计算接口
"""
import pandas as pd
from typing import Dict, List
from year_generator import YearGenerator
from data_models import InputData
from calculations import (
    InvestmentCalculator,
    DepreciationCalculator,
    CostCalculator,
    ProfitCalculator,
    CashFlowCalculator,
    AssetSalesCalculator
)
from utils import round_dataframe


class CalculationEngine:
    """财务计算引擎"""

    def __init__(self, year_generator: YearGenerator, input_data: InputData):
        """
        初始化计算引擎

        Args:
            year_generator: 年份生成器
            input_data: 输入数据
        """
        self.yg = year_generator
        self.input = input_data

        # 初始化各计算器
        self.investment_calc = InvestmentCalculator(year_generator, input_data)
        self.depreciation_calc = DepreciationCalculator(year_generator, input_data)
        self.cost_calc = CostCalculator(year_generator, input_data)
        self.profit_calc = ProfitCalculator(year_generator, input_data)
        self.cashflow_calc = CashFlowCalculator(year_generator, input_data)
        self.asset_sales_calc = AssetSalesCalculator(year_generator, input_data)

    def run_all_calculations(self) -> Dict[str, pd.DataFrame]:
        """
        运行所有计算，生成所有计算表

        Returns:
            dict: 表名到DataFrame的映射
        """
        results = {}

        # ⚠️ 关键：必须先完成资产形成计算，其他计算才能正常工作
        self.investment_calc.calculate_asset_formation()
        self.asset_sales_calc.calculate_annual_sales()

        # 1. 投资估算表
        results["1建设投资"] = self._create_investment_table()

        # 2. 流动资金估算表
        results["2流动资金"] = self._create_working_capital_table()

        # 3. 投资计划表
        results["3投资计划"] = self._create_investment_plan_table()

        # 4. 借款还本付息表
        results["4还本付息"] = self._create_loan_repayment_table()

        # 5. 折旧摊销表
        results["5-4折旧"] = self._create_depreciation_table()
        results["5-5摊销"] = self._create_amortization_table()

        # 6. 材料燃料工资表
        results["5-1材料"] = self._create_material_cost_table()
        results["5-2燃料"] = self._create_fuel_cost_table()
        results["5-3工资"] = self._create_welfare_cost_table()

        # 5. 总成本表
        results["5总成本"] = self._create_total_cost_table()

        # 6. 收入表
        results["6收入 "] = self._create_revenue_table()

        # 7. 利润表
        results["7利润"] = self._create_profit_table()

        # 8. 现金流表
        results["8财务现金"] = self._create_finance_cashflow_table()
        results["9资产负债"] = self._create_balance_sheet_table()
        results["10项目现金"] = self._create_project_cashflow_table()
        results["11资本金现金 "] = self._create_equity_cashflow_table()
        results["12各方现金"] = self._create_investor_cashflow_table()

        # 9. 财务指标汇总
        results["财务分析结果汇总"] = self._create_financial_indicators_table()

        # 10. 土地增值税相关表格
        results["土地增值税计算"] = self._create_land_tax_table()
        results["房产销售及土增"] = self._create_property_sale_table()

        # 11. 资产销售计划表
        results["资产销售计划"] = self._create_asset_sales_table()

        return results

    def _create_investment_table(self) -> pd.DataFrame:
        """创建建设投资估算表"""
        # 先计算资产形成
        self.investment_calc.calculate_asset_formation()
        investment_summary = self.investment_calc.get_investment_summary()

        data = [
            ["项目", "金额（万元）", "说明"],
            ["建筑工程费", self.input.project_investment.building_cost, "含税投资"],
            ["建筑设备费", self.input.project_investment.building_equipment_cost, "含税投资"],
            ["设备安装费", self.input.project_investment.building_installation_cost, "含税投资"],
            ["生产设备购置费", self.input.project_investment.production_equipment_cost, "含税投资"],
            ["生产设备安装费", self.input.project_investment.production_installation_cost, "含税投资"],
            ["工程费小计", self.investment_calc.calculate_total_investment()["工程费合计"], ""],
            ["工程建设其他费", self.investment_calc.calculate_total_investment()["工程建设其他费合计"], ""],
            ["基本预备费", self.investment_calc.calculate_total_investment()["基本预备费"], ""],
            ["涨价预备费", self.investment_calc.calculate_total_investment()["涨价预备费"], ""],
            ["建设期利息", investment_summary["建设期利息合计"], ""],
            ["流动资金", investment_summary["流动资金"], ""],
            ["项目总投资合计", investment_summary["项目总投资（含利息）"], ""]
        ]

        return round_dataframe(pd.DataFrame(data, columns=["项目", "金额（万元）", "说明"]))

    def _create_working_capital_table(self) -> pd.DataFrame:
        """创建流动资金估算表 - 横向展示"""
        years = self.yg.generate_year_names()

        # 构建数据字典：指标名称 -> 各年份数据
        data = {"项目": ["流动资金（万元）"]}
        for year in years:
            year_num = self.yg.get_year_index(year)
            # 简化：运营期各年流动资金固定为90万元
            if self.yg.is_operation_year(year_num):
                data[year] = [90.0]
            else:
                data[year] = [0.0]

        return round_dataframe(pd.DataFrame(data))

    def _create_investment_plan_table(self) -> pd.DataFrame:
        """创建投资计划表 - 横向展示"""
        years = self.yg.generate_year_names()
        investment_by_year = self.investment_calc.calculate_investment_by_year()

        # 构建数据字典
        data = {
            "项目": ["工程费", "其他费", "预备费", "合计"],
        }

        for year in years:
            inv = investment_by_year[year]
            total = sum(inv.values())
            data[year] = [inv["工程费"], inv["其他费"], inv["预备费"], total]

        return round_dataframe(pd.DataFrame(data))

    def _create_loan_repayment_table(self) -> pd.DataFrame:
        """创建借款还本付息计划表 - 横向展示"""
        years = self.yg.generate_year_names()
        loan_plan = self.input.bank_loan_plan

        # 获取借款数据（简化：假设所有借款在建设期均匀分布）
        loan_amounts = {}
        total_loan = 0.0
        for year in years:
            year_num = self.yg.get_year_index(year)
            if self.yg.is_construction_year(year_num):
                # 建设期每年借款
                loan_amount = 30000.0  # 简化：每年借款3万元
                loan_amounts[year] = loan_amount
                total_loan += loan_amount
            else:
                loan_amounts[year] = 0.0

        # 计算还本付息
        interest_rate = loan_plan.interest_rate / 100
        repayment_years = loan_plan.repayment_period if hasattr(loan_plan, 'repayment_period') else 15
        repayment_method = loan_plan.repayment_method if hasattr(loan_plan, 'repayment_method') else "等额本金"

        balance = 0.0
        annual_principal = 0.0
        if repayment_years > 0:
            annual_principal = total_loan / repayment_years  # 等额本金

        # 构建数据字典
        data = {
            "项目": [
                "期初借款余额",
                "当期借款",
                "当期应计利息",
                "当期还本付息",
                "其中：还本",
                "付息",
                "期末借款余额"
            ]
        }

        cumulative_balance = 0.0
        repayment_start_year = self.yg.construction_period + 1  # 运营期开始还款

        for year in years:
            year_num = self.yg.get_year_index(year)

            # 累计借款余额
            cumulative_balance += loan_amounts[year]

            if year_num < repayment_start_year:
                # 宽限期：只付息不还本
                principal_payment = 0.0
                interest_payment = cumulative_balance * interest_rate
            elif cumulative_balance > 0:
                # 还款期
                principal_payment = min(annual_principal, cumulative_balance)
                interest_payment = cumulative_balance * interest_rate
                cumulative_balance -= principal_payment
            else:
                # 已还清
                principal_payment = 0.0
                interest_payment = 0.0

            total_payment = principal_payment + interest_payment

            data[year] = [
                max(0, cumulative_balance + principal_payment),  # 期初余额
                loan_amounts[year],  # 当期借款
                interest_payment,  # 当期应计利息
                total_payment,  # 当期还本付息
                principal_payment,  # 还本
                interest_payment,  # 付息
                max(0, cumulative_balance)  # 期末余额
            ]

        return round_dataframe(pd.DataFrame(data))

    def _create_depreciation_table(self) -> pd.DataFrame:
        """
        创建固定资产折旧费、成本摊销估算表（按照5-4折旧表结构）

        表格结构：
        - 行4-7: 建筑物（20年）- 原值、当期折旧费、净值
        - 行8-11: 机器设备（10年）- 原值、当期折旧费、净值
        - 行12-15: 销售固定资产 - 销售固定资产成本、固定资产成本摊销额、剩余待销售资产净值
        - 行16-19: 合计 - 原值、当期折旧、摊销、净值
        """
        years = self.yg.generate_year_names()
        depreciation_data = self.depreciation_calc.get_detailed_depreciation_data()
        asset = self.input.asset_formation

        # 构建表格数据
        rows = []

        # 1. 建筑物（20年）
        rows.append(["1. 建筑物（20年）", ""] + [""] * len(years))  # 标题行
        rows.append(["", "原值"] + depreciation_data["building"]["original_value"])
        rows.append(["", "当期折旧费"] + depreciation_data["building"]["depreciation"])
        rows.append(["", "净值"] + depreciation_data["building"]["net_value"])

        # 2. 机器设备（10年）
        rows.append(["2. 机器设备（10年）", ""] + [""] * len(years))  # 标题行
        rows.append(["", "原值"] + depreciation_data["equipment"]["original_value"])
        rows.append(["", "当期折旧费"] + depreciation_data["equipment"]["depreciation"])
        rows.append(["", "净值"] + depreciation_data["equipment"]["net_value"])

        # 3. 销售固定资产
        rows.append(["3. 销售固定资产", ""] + [""] * len(years))  # 标题行
        rows.append(["", "销售固定资产成本"] + depreciation_data["sales_assets"]["cost"])
        rows.append(["", "固定资产成本摊销额"] + depreciation_data["sales_assets"]["amortization"])
        rows.append(["", "剩余待销售资产净值"] + depreciation_data["sales_assets"]["remaining"])

        # 4. 合计
        rows.append(["4. 合计", ""] + [""] * len(years))  # 标题行
        rows.append(["", "原值"] + depreciation_data["total"]["original_value"])
        rows.append(["", "当期折旧、摊销"] + depreciation_data["total"]["depreciation_amortization"])
        rows.append(["", "净值"] + depreciation_data["total"]["net_value"])

        # 构建列名
        columns = ["项目", "说明"] + years

        df = pd.DataFrame(rows, columns=columns)

        # 四舍五入，保留2位小数
        return round_dataframe(df)

    def _create_amortization_table(self) -> pd.DataFrame:
        """
        创建摊销表 - 按照5-5摊销表结构

        表格结构：
        - 行3-6: 土地使用权（50年）- 原值、当期摊销费、净值
        - 行7-10: 专利权（6年）- 原值、当期摊销费、净值
        - 行11-14: 其他资产（5年）- 原值、当期摊销费、净值
        - 行15-18: 销售地产土地权摊销 - 原值、当期摊销费、净值
        - 行19-22: 合计 - 原值、当期摊销费、净值
        """
        years = self.yg.generate_year_names()
        amortization_data = self.depreciation_calc.get_detailed_amortization_data()

        # 构建表格数据
        rows = []

        # 1. 土地使用权（50年）
        rows.append(["1. 土地使用权（50年）", ""] + [""] * len(years))  # 标题行
        rows.append(["", "原值"] + amortization_data["land"]["original_value"])
        rows.append(["", "当期摊销费"] + amortization_data["land"]["amortization"])
        rows.append(["", "净值"] + amortization_data["land"]["net_value"])

        # 2. 专利权（6年）
        rows.append(["2. 专利权（6年）", ""] + [""] * len(years))  # 标题行
        rows.append(["", "原值"] + amortization_data["patent"]["original_value"])
        rows.append(["", "当期摊销费"] + amortization_data["patent"]["amortization"])
        rows.append(["", "净值"] + amortization_data["patent"]["net_value"])

        # 3. 其他资产（5年）
        rows.append(["3. 其他资产（5年）", ""] + [""] * len(years))  # 标题行
        rows.append(["", "原值"] + amortization_data["other_asset"]["original_value"])
        rows.append(["", "当期摊销费"] + amortization_data["other_asset"]["amortization"])
        rows.append(["", "净值"] + amortization_data["other_asset"]["net_value"])

        # 4. 销售地产土地权摊销
        rows.append(["4. 销售地产土地权摊销", ""] + [""] * len(years))  # 标题行
        rows.append(["", "原值"] + amortization_data["sales_land"]["original_value"])
        rows.append(["", "当期摊销费"] + amortization_data["sales_land"]["amortization"])
        rows.append(["", "净值"] + amortization_data["sales_land"]["net_value"])

        # 5. 合计
        rows.append(["5. 合计", ""] + [""] * len(years))  # 标题行
        rows.append(["", "原值"] + amortization_data["total"]["original_value"])
        rows.append(["", "当期摊销费"] + amortization_data["total"]["amortization"])
        rows.append(["", "净值"] + amortization_data["total"]["net_value"])

        # 构建列名
        columns = ["项目", "说明"] + years

        df = pd.DataFrame(rows, columns=columns)

        # 四舍五入，保留2位小数
        return round_dataframe(df)

    def _create_material_cost_table(self) -> pd.DataFrame:
        """创建外购原材料费估算表 - 横向展示"""
        years = self.yg.generate_year_names()
        mat_cost = self.input.material_cost

        # 构建数据字典
        data = {
            "项目": []
        }

        # 添加材料项目
        material_items = [
            ("材料1", mat_cost.material_1),
            ("材料2", mat_cost.material_2),
            # 可以继续添加更多材料
        ]

        for item_name, cost_dict in material_items:
            data["项目"].append(item_name)
            for year in years:
                if year not in data:
                    data[year] = []
                data[year].append(cost_dict.get(year, 0.0))

        # 添加合计行
        total_row = []
        for year in years:
            total = sum(data[year])
            total_row.append(total)
        data["项目"].append("合计")
        for year in years:
            data[year].append(total_row[years.index(year)])

        return round_dataframe(pd.DataFrame(data))

    def _create_fuel_cost_table(self) -> pd.DataFrame:
        """创建外购燃料及动力费估算表 - 横向展示"""
        years = self.yg.generate_year_names()
        fuel_cost = self.input.fuel_cost

        # 构建数据字典
        data = {
            "项目": []
        }

        # 添加燃料项目
        fuel_items = [
            ("燃料动力1", fuel_cost.fuel_1),
            # 可以继续添加更多燃料
        ]

        for item_name, cost_dict in fuel_items:
            data["项目"].append(item_name)
            for year in years:
                if year not in data:
                    data[year] = []
                data[year].append(cost_dict.get(year, 0.0))

        # 添加合计行
        total_row = []
        for year in years:
            total = sum(data[year])
            total_row.append(total)
        data["项目"].append("合计")
        for year in years:
            data[year].append(total_row[years.index(year)])

        return round_dataframe(pd.DataFrame(data))

    def _create_welfare_cost_table(self) -> pd.DataFrame:
        """创建工资及福利费估算表 - 横向展示"""
        years = self.yg.generate_year_names()
        labor = self.input.labor_cost

        # 计算各年工资福利费用
        admin_salary = labor.admin_persons * labor.admin_salary
        tech_salary = labor.tech_persons * labor.tech_salary
        security_salary = labor.security_persons * labor.security_salary
        cleaning_salary = labor.cleaning_persons * labor.cleaning_salary

        total_salary = admin_salary + tech_salary + security_salary + cleaning_salary
        total_welfare = total_salary * labor.welfare_rate

        # 构建数据字典
        data = {
            "项目": [
                "管理人员工资",
                "技术人员工资",
                "保安人员工资",
                "保洁人员工资",
                "工资小计",
                "福利费",
                "合计"
            ]
        }

        for year in years:
            year_num = self.yg.get_year_index(year)
            if self.yg.is_operation_year(year_num):
                data[year] = [
                    admin_salary,
                    tech_salary,
                    security_salary,
                    cleaning_salary,
                    total_salary,
                    total_welfare,
                    total_salary + total_welfare
                ]
            else:
                data[year] = [0.0] * 7

        return round_dataframe(pd.DataFrame(data))

    def _create_total_cost_table(self) -> pd.DataFrame:
        """创建总成本表 - 横向展示"""
        years = self.yg.generate_year_names()
        depreciation_by_year = self.depreciation_calc.get_yearly_depreciation()
        amortization_by_year = self.depreciation_calc.get_yearly_amortization()
        costs_by_year = self.cost_calc.get_yearly_costs(depreciation_by_year, amortization_by_year)

        # 构建数据字典
        data = {
            "项目": ["折旧费", "摊销费", "材料成本", "燃料成本", "人工成本", "修理费", "总成本"]
        }

        for year in years:
            costs = costs_by_year[year]
            total_cost = (
                costs["折旧费"] + costs["摊销费"] + costs["材料成本"] +
                costs["燃料成本"] + costs["人工成本"] + costs["修理费"]
            )

            data[year] = [
                costs["折旧费"],
                costs["摊销费"],
                costs["材料成本"],
                costs["燃料成本"],
                costs["人工成本"],
                costs["修理费"],
                total_cost
            ]

        return round_dataframe(pd.DataFrame(data))

    def _create_revenue_table(self) -> pd.DataFrame:
        """创建收入表 - 横向展示"""
        years = self.yg.generate_year_names()

        # 构建数据字典
        data = {
            "项目": ["营业收入", "营业税金及附加", "增值税", "营业收入净额"]
        }

        for year in years:
            year_num = self.yg.get_year_index(year)

            if self.yg.is_operation_year(year_num):
                revenue = self.input.sales_revenue.annual_revenue.get(year, 0.0)

                # 计算税金（简化）
                tax_param = self.input.tax_params
                city_tax = revenue * (tax_param.city_tax_rate / 100)
                edu_tax = revenue * (tax_param.education_tax_rate / 100)
                total_tax = city_tax + edu_tax

                data[year] = [revenue, total_tax, 0.0, revenue - total_tax]
            else:
                data[year] = [0.0, 0.0, 0.0, 0.0]

        return round_dataframe(pd.DataFrame(data))

    def _create_profit_table(self) -> pd.DataFrame:
        """创建利润表 - 横向展示"""
        years = self.yg.generate_year_names()
        costs_by_year = self.cost_calc.get_yearly_costs({}, {})

        tax_param = self.input.tax_params

        # 构建数据字典
        data = {
            "项目": ["营业收入", "总成本", "利润总额", "所得税", "净利润"]
        }

        for year in years:
            year_num = self.yg.get_year_index(year)

            if self.yg.is_operation_year(year_num):
                revenue = self.input.sales_revenue.annual_revenue.get(year, 0.0)
                costs = costs_by_year[year]
                total_cost = sum(costs.values())

                gross_profit = revenue - total_cost

                if gross_profit > 0:
                    income_tax = gross_profit * (tax_param.corporate_tax_rate / 100)
                else:
                    income_tax = 0.0

                net_profit = gross_profit - income_tax

                data[year] = [revenue, total_cost, gross_profit, income_tax, net_profit]
            else:
                data[year] = [0.0, 0.0, 0.0, 0.0, 0.0]

        return round_dataframe(pd.DataFrame(data))

    def _create_finance_cashflow_table(self) -> pd.DataFrame:
        """创建财务现金流表 - 横向展示"""
        years = self.yg.generate_year_names()

        # 构建数据字典
        data = {
            "项目": ["现金流入", "现金流出", "净现金流", "累计净现金流"]
        }

        # 简化实现
        cumulative = 0.0
        for year in years:
            inflow = 0.0
            outflow = 0.0

            year_num = self.yg.get_year_index(year)

            if self.yg.is_construction_year(year_num):
                # 建设期：主要是投资流出
                inv_by_year = self.investment_calc.calculate_investment_by_year()[year]
                outflow = sum(inv_by_year.values())
            else:
                # 运营期：收入流入，成本流出
                inflow = self.input.sales_revenue.annual_revenue.get(year, 0.0)
                costs = self.cost_calc.get_yearly_costs({}, {})[year]
                outflow = sum(costs.values()) * 0.8  # 简化假设

            net_cf = inflow - outflow
            cumulative += net_cf

            data[year] = [inflow, outflow, net_cf, cumulative]

        return round_dataframe(pd.DataFrame(data))

    def _create_project_cashflow_table(self) -> pd.DataFrame:
        """创建项目投资现金流表 - 横向展示"""
        # 简化实现
        return self._create_finance_cashflow_table()

    def _create_equity_cashflow_table(self) -> pd.DataFrame:
        """创建资本金现金流表 - 横向展示"""
        # 简化实现
        return self._create_finance_cashflow_table()

    def _create_investor_cashflow_table(self) -> pd.DataFrame:
        """创建投资各方现金流量表 - 横向展示"""
        years = self.yg.generate_year_names()

        # 构建数据字典
        data = {
            "项目": [
                "现金流入",
                "实分利润",
                "资产处置收益分配",
                "租赁费收入",
                "技术转让或使用收入",
                "其他现金流入",
                "现金流出",
                "实缴资本",
                "租赁资产支出",
                "其他现金流出",
                "净现金流量"
            ]
        }

        # 简化实现：假设投资者每年投入和回收
        for year in years:
            year_num = self.yg.get_year_index(year)
            if self.yg.is_construction_year(year_num):
                # 建设期：投资者投入
                data[year] = [
                    0.0,  # 现金流入
                    0.0,  # 实分利润
                    0.0,  # 资产处置收益分配
                    0.0,  # 租赁费收入
                    0.0,  # 技术转让或使用收入
                    0.0,  # 其他现金流入
                    10000.0,  # 现金流出（投入）
                    10000.0,  # 实缴资本
                    0.0,  # 租赁资产支出
                    0.0,  # 其他现金流出
                    -10000.0  # 净现金流量
                ]
            elif self.yg.is_operation_year(year_num):
                # 运营期：获得利润分配
                profit = self.input.sales_revenue.annual_revenue.get(year, 0.0) * 0.3  # 假设30%的利润分配给投资者
                data[year] = [
                    profit,  # 现金流入
                    profit,  # 实分利润
                    0.0,  # 资产处置收益分配
                    0.0,  # 租赁费收入
                    0.0,  # 技术转让或使用收入
                    0.0,  # 其他现金流入
                    0.0,  # 现金流出
                    0.0,  # 实缴资本
                    0.0,  # 租赁资产支出
                    0.0,  # 其他现金流出
                    profit  # 净现金流量
                ]
            else:
                data[year] = [0.0] * 11

        return round_dataframe(pd.DataFrame(data))

    def _create_balance_sheet_table(self) -> pd.DataFrame:
        """创建资产负债表 - 横向展示"""
        years = self.yg.generate_year_names()

        # 获取各年数据
        asset_formation = self.input.asset_formation
        depreciation_by_year = self.depreciation_calc.get_yearly_depreciation()

        # 获取投资汇总
        investment_summary = self.investment_calc.get_investment_summary()

        # 累计折旧
        cumulative_depr = {}
        total_depr = 0.0
        for year in years:
            total_depr += depreciation_by_year[year]
            cumulative_depr[year] = total_depr

        # 构建数据字典
        data = {
            "项目": [
                "资产",
                "流动资产",
                "货币资金",
                "应收账款",
                "存货",
                "流动资产合计",
                "在建工程",
                "固定资产净值",
                "无形及其他资产净值",
                "资产合计",
                "负债及所有者权益",
                "流动负债",
                "应付账款",
                "流动负债合计",
                "建设投资借款",
                "负债合计",
                "所有者权益",
                "项目资本金",
                "资本公积",
                "累计未分配利润",
                "负债及所有者权益合计"
            ]
        }

        # 简化实现
        for year in years:
            year_num = self.yg.get_year_index(year)

            if self.yg.is_construction_year(year_num):
                # 建设期
                construction_interest = investment_summary.get("建设期利息合计", 0.0)
                data[year] = [
                    "",  # 资产
                    "",  # 流动资产
                    1000.0,  # 货币资金
                    0.0,  # 应收账款
                    0.0,  # 存货
                    1000.0,  # 流动资产合计
                    construction_interest,  # 在建工程
                    0.0,  # 固定资产净值
                    0.0,  # 无形及其他资产净值
                    1000.0 + construction_interest,  # 资产合计
                    "",  # 负债及所有者权益
                    "",  # 流动负债
                    500.0,  # 应付账款
                    500.0,  # 流动负债合计
                    construction_interest,  # 建设投资借款
                    500.0 + construction_interest,  # 负债合计
                    "",  # 所有者权益
                    500.0,  # 项目资本金
                    0.0,  # 资本公积
                    0.0,  # 累计未分配利润
                    500.0 + construction_interest  # 负债及所有者权益合计
                ]
            else:
                # 运营期
                revenue = self.input.sales_revenue.annual_revenue.get(year, 0.0)
                fixed_asset = asset_formation.fixed_asset_total
                net_value = max(0, fixed_asset - cumulative_depr[year])
                accumulated_profit = revenue * 0.2  # 简化：累计未分配利润

                data[year] = [
                    "",  # 资产
                    "",  # 流动资产
                    revenue * 0.1,  # 货币资金
                    revenue * 0.05,  # 应收账款
                    revenue * 0.02,  # 存货
                    revenue * 0.17,  # 流动资产合计
                    0.0,  # 在建工程
                    net_value,  # 固定资产净值
                    net_value * 0.1,  # 无形及其他资产净值
                    revenue * 0.17 + net_value * 1.1,  # 资产合计
                    "",  # 负债及所有者权益
                    "",  # 流动负债
                    revenue * 0.08,  # 应付账款
                    revenue * 0.08,  # 流动负债合计
                    net_value * 0.5,  # 建设投资借款
                    revenue * 0.08 + net_value * 0.5,  # 负债合计
                    "",  # 所有者权益
                    net_value * 0.5,  # 项目资本金
                    accumulated_profit * 0.2,  # 资本公积
                    accumulated_profit * 0.8,  # 累计未分配利润
                    revenue * 0.17 + net_value * 0.5 + accumulated_profit  # 负债及所有者权益合计
                ]

        return round_dataframe(pd.DataFrame(data))

    def _create_land_tax_table(self) -> pd.DataFrame:
        """创建土地增值税计算表 - 横向展示"""
        years = self.yg.generate_year_names()

        # 获取投资数据
        investment_summary = self.investment_calc.get_investment_summary()

        # 定义项目列表（共13项）
        items = [
            "1. 房地产转让收入",
            "2. 扣除项目金额",
            "2.1 取得土地使用权所支付的金额",
            "2.2 房地产开发成本",
            "2.3 房地产开发费用",
            "2.4 与转让房地产有关的税金",
            "2.5 财政部规定的其他扣除项目",
            "3. 增值额",
            "4. 增值额与扣除项目金额之比",
            "5. 适用税率",
            "6. 速算扣除系数",
            "7. 土地增值税税额"
        ]

        # 构建数据字典，确保所有列长度一致
        data = {"项目": items}

        # 为每个年份初始化列表
        for year in years:
            data[year] = []

        # 简化实现：仅在运营期最后一年计算
        for year in years:
            year_num = self.yg.get_year_index(year)
            if year_num == self.yg.total_period:
                # 最后一年：计算土地增值税
                total_investment = investment_summary["项目总投资（含利息）"]
                revenue = self.input.sales_revenue.annual_revenue.get(year, 0.0)

                land_payment = total_investment * 0.1  # 土地使用权支付金额
                development_cost = total_investment * 0.6  # 开发成本
                development_fee = total_investment * 0.05  # 开发费用
                tax = revenue * 0.055  # 转让税金
                other_deduction = (land_payment + development_cost) * 0.2  # 其他扣除

                total_deduction = land_payment + development_cost + development_fee + tax + other_deduction
                added_value = revenue - total_deduction
                ratio = added_value / total_deduction if total_deduction > 0 else 0

                # 根据比率确定税率和速算扣除系数
                if ratio <= 0.5:
                    tax_rate = 0.3
                    quick_deduction = 0
                elif ratio <= 1.0:
                    tax_rate = 0.4
                    quick_deduction = 0.05
                elif ratio <= 2.0:
                    tax_rate = 0.5
                    quick_deduction = 0.15
                else:
                    tax_rate = 0.6
                    quick_deduction = 0.35

                land_tax = added_value * tax_rate - total_deduction * quick_deduction

                data[year] = [
                    revenue,
                    total_deduction,
                    land_payment,
                    development_cost,
                    development_fee,
                    tax,
                    other_deduction,
                    added_value,
                    ratio,
                    tax_rate,
                    quick_deduction,
                    land_tax
                ]
            else:
                data[year] = [0.0] * len(items)

        return round_dataframe(pd.DataFrame(data))

    def _create_property_sale_table(self) -> pd.DataFrame:
        """创建房产销售及土增表 - 横向展示"""
        years = self.yg.generate_year_names()

        # 构建数据字典
        data = {
            "项目": [
                "销售收入",
                "销售费用",
                "销售税金及附加",
                "土地增值税",
                "营业利润"
            ]
        }

        # 简化实现
        for year in years:
            year_num = self.yg.get_year_index(year)
            if self.yg.is_operation_year(year_num):
                revenue = self.input.sales_revenue.annual_revenue.get(year, 0.0)
                sale_fee = revenue * 0.02  # 销售费用2%
                sale_tax = revenue * 0.055  # 销售税金5.5%

                # 简化：土地增值税为收入的1%
                land_tax = revenue * 0.01

                profit = revenue - sale_fee - sale_tax - land_tax

                data[year] = [
                    revenue,
                    sale_fee,
                    sale_tax,
                    land_tax,
                    profit
                ]
            else:
                data[year] = [0.0] * 5

        return round_dataframe(pd.DataFrame(data))

    def _create_financial_indicators_table(self) -> pd.DataFrame:
        """创建财务指标汇总表"""
        cashflow_df = self._create_finance_cashflow_table()

        # 从横向表格中获取净现金流数据
        # 找到"净现金流"这一行
        net_cf_row = cashflow_df[cashflow_df["项目"] == "净现金流"]
        cumulative_row = cashflow_df[cashflow_df["项目"] == "累计净现金流"]

        # 提取年份列（跳过"项目"列）
        year_columns = [col for col in cashflow_df.columns if col != "项目"]
        net_cashflows = net_cf_row[year_columns].values[0].tolist()
        cumulative = cumulative_row[year_columns].values[0].tolist()

        # 计算NPV
        discount_rate = self.input.tax_params.discount_rate / 100
        npv = self.cashflow_calc.calculate_net_present_value(net_cashflows, discount_rate)

        # 计算IRR
        try:
            irr = self.cashflow_calc.calculate_internal_rate_of_return(net_cashflows)
        except:
            irr = 0.0

        # 计算回收期
        payback_period = self.cashflow_calc.calculate_payback_period(cumulative)

        data = [
            ["指标名称", "数值", "说明"],
            ["项目总投资", self.investment_calc.get_investment_summary()["项目总投资（含利息）"], "万元"],
            ["净现值(NPV)", npv, f"折现率{discount_rate:.1%}"],
            ["内部收益率(IRR)", irr * 100 if isinstance(irr, (int, float)) else irr, "%"],
            ["投资回收期", payback_period, "年"],
            ["建设期", self.yg.construction_period, "年"],
            ["运营期", self.yg.operation_period, "年"],
            ["计算期", self.yg.total_period, "年"]
        ]

        return round_dataframe(pd.DataFrame(data))

    def _create_asset_sales_table(self) -> pd.DataFrame:
        """创建资产销售计划表 - 横向展示"""
        years = self.yg.generate_year_names()
        
        # 计算年度销售数据
        self.asset_sales_calc.calculate_annual_sales()
        sales_plan = self.input.asset_sales_plan
        
        # 构建数据字典
        data = {
            "项目": [
                "固定资产销售成本",
                "固定资产销售收入",
                "土地摊销额",
                "销售比例",
                "自持比例"
            ]
        }
        
        for year in years:
            year_num = self.yg.get_year_index(year)
            
            if self.yg.is_operation_year(year_num):
                # 运营期显示销售数据
                sales_cost = sales_plan.annual_sales_cost.get(year, 0.0)
                sales_revenue = sales_plan.annual_sales_revenue.get(year, 0.0)
                land_amort = sales_plan.annual_land_amortization.get(year, 0.0)
                
                # 计算当年销售比例
                if sales_plan.asset_sales_revenue > 0:
                    sales_ratio = sales_revenue / sales_plan.asset_sales_revenue
                else:
                    sales_ratio = 0.0
                
                data[year] = [
                    sales_cost,
                    sales_revenue,
                    land_amort,
                    sales_ratio,
                    sales_plan.self_hold_ratio
                ]
            else:
                # 建设期无销售
                data[year] = [0.0, 0.0, 0.0, 0.0, sales_plan.self_hold_ratio]
        
        return round_dataframe(pd.DataFrame(data))
