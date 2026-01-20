"""
完整计算模块
包含所有财务计算逻辑
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from year_generator import YearGenerator, DynamicTableBuilder
from data_models import InputData


class InvestmentCalculator:
    """投资计算模块"""

    def __init__(self, year_generator: YearGenerator, input_data: InputData):
        """
        初始化投资计算器

        Args:
            year_generator: 年份生成器
            input_data: 输入数据
        """
        self.yg = year_generator
        self.input = input_data
        self.builder = DynamicTableBuilder(year_generator)

    def calculate_total_investment(self) -> Dict[str, float]:
        """
        计算项目总投资

        Returns:
            dict: 各项投资金额
        """
        inv = self.input.project_investment

        # 工程费合计
        total_engineering = (
            inv.building_cost +
            inv.building_equipment_cost +
            inv.building_installation_cost +
            inv.production_equipment_cost +
            inv.production_installation_cost
        )

        # 工程建设其他费合计
        total_other = (
            inv.management_fee +
            inv.tech_service_fee +
            inv.supporting_fee +
            inv.land_use_fee +
            inv.patent_fee +
            inv.preparation_fee
        )

        # 基本预备费
        basic_reserve = (total_engineering + total_other) * (inv.basic_reserve_rate / 100)

        # 涨价预备费（简化计算，假设按建设期每年投资的一定比例）
        # 这里简化为0，实际应根据建设期投资计划计算
        price_reserve = 0.0

        # 项目总投资（不含建设期利息和流动资金）
        total_investment = total_engineering + total_other + basic_reserve + price_reserve

        return {
            "工程费合计": total_engineering,
            "工程建设其他费合计": total_other,
            "基本预备费": basic_reserve,
            "涨价预备费": price_reserve,
            "项目总投资（不含利息）": total_investment
        }

    def calculate_investment_by_year(self) -> Dict[str, Dict[str, float]]:
        """
        计算各年投资分布

        Returns:
            dict: 各年的投资明细
        """
        years = self.yg.generate_year_names()
        investment_by_year = {}

        total_investment = self.calculate_total_investment()["项目总投资（不含利息）"]

        # 简化：平均分配到建设期各年（实际应根据投资计划）
        construction_years_count = self.yg.construction_period
        avg_annual_investment = total_investment / construction_years_count if construction_years_count > 0 else 0

        for year in years:
            year_num = self.yg.get_year_index(year)
            if self.yg.is_construction_year(year_num):
                investment_by_year[year] = {
                    "工程费": avg_annual_investment * 0.7,  # 假设70%是工程费
                    "其他费": avg_annual_investment * 0.2,  # 假设20%是其他费
                    "预备费": avg_annual_investment * 0.1,  # 假设10%是预备费
                }
            else:
                investment_by_year[year] = {
                    "工程费": 0.0,
                    "其他费": 0.0,
                    "预备费": 0.0,
                }

        return investment_by_year

    def calculate_construction_interest(self) -> Dict[str, float]:
        """
        计算建设期利息

        Returns:
            dict: 各年建设期利息
        """
        years = self.yg.generate_year_names()
        interest_by_year = self.yg.initialize_year_data_dict()

        loan_plan = self.input.bank_loan_plan
        interest_rate = loan_plan.interest_rate / 100 if hasattr(loan_plan, 'interest_rate') else 0.0588

        # 简化计算：假设每年借款在年中投入
        cumulative_loan = 0.0

        for year in years:
            year_num = self.yg.get_year_index(year)

            if self.yg.is_construction_year(year_num):
                # 假设每年借款金额（从投资计划中估算）
                annual_investment = sum(self.calculate_investment_by_year()[year].values())

                # 简化：假设投资中50%是借款
                annual_loan = annual_investment * 0.5

                # 计算当年利息 = (年初贷款 + 当年贷款/2) * 利率
                annual_interest = (cumulative_loan + annual_loan / 2) * interest_rate

                interest_by_year[year] = annual_interest
                cumulative_loan += annual_loan
            else:
                interest_by_year[year] = 0.0

        total_construction_interest = sum(interest_by_year.values())

        return interest_by_year

    def get_investment_summary(self) -> Dict[str, float]:
        """
        获取投资汇总

        Returns:
            dict: 投资汇总数据
        """
        total_investment = self.calculate_total_investment()
        construction_interest = self.calculate_construction_interest()

        return {
            **total_investment,
            "建设期利息合计": sum(construction_interest.values()),
            "项目总投资（含利息）": total_investment["项目总投资（不含利息）"] + sum(construction_interest.values()),
            "流动资金": 90.0,  # 从Excel中读取的固定值
        }


class DepreciationCalculator:
    """折旧摊销计算模块"""

    def __init__(self, year_generator: YearGenerator, input_data: InputData):
        """
        初始化折旧摊销计算器

        Args:
            year_generator: 年份生成器
            input_data: 输入数据
        """
        self.yg = year_generator
        self.input = input_data

    def calculate_depreciation(self, asset_value: float, years: int, salvage_rate: float) -> float:
        """
        计算年度折旧额（直线法）

        Args:
            asset_value: 资产原值
            years: 折旧年限
            salvage_rate: 残值率

        Returns:
            float: 年度折旧额
        """
        if years <= 0:
            return 0.0
        return asset_value * (1 - salvage_rate / 100) / years

    def calculate_amortization(self, asset_value: float, years: int) -> float:
        """
        计算年度摊销额（直线法）

        Args:
            asset_value: 资产原值
            years: 摊销年限

        Returns:
            float: 年度摊销额
        """
        if years <= 0:
            return 0.0
        return asset_value / years

    def get_yearly_depreciation(self) -> Dict[str, float]:
        """
        获取各年折旧额

        Returns:
            dict: 各年折旧额
        """
        result = self.yg.initialize_year_data_dict(default_value=0.0)

        asset_formation = self.input.asset_formation

        # 固定资产折旧
        fixed_asset_value = (
            asset_formation.building_asset +
            asset_formation.equipment_asset
        )

        yearly_depreciation = self.calculate_depreciation(
            fixed_asset_value,
            asset_formation.depreciation_years,
            asset_formation.salvage_rate
        )

        # 固定资产从运营期开始折旧
        for year in self.yg.generate_year_names():
            year_num = self.yg.get_year_index(year)
            if self.yg.is_operation_year(year_num):
                result[year] = yearly_depreciation

        return result

    def get_yearly_amortization(self) -> Dict[str, float]:
        """
        获取各年摊销额

        Returns:
            dict: 各年摊销额
        """
        result = self.yg.initialize_year_data_dict(default_value=0.0)

        asset_formation = self.input.asset_formation

        # 无形资产摊销
        intangible_asset_value = (
            asset_formation.land_asset +
            asset_formation.patent_asset
        )

        yearly_amortization = self.calculate_amortization(
            intangible_asset_value,
            asset_formation.amortization_years
        )

        # 无形资产从运营期开始摊销
        for year in self.yg.generate_year_names():
            year_num = self.yg.get_year_index(year)
            if self.yg.is_operation_year(year_num):
                result[year] = yearly_amortization

        return result


class CostCalculator:
    """成本计算模块"""

    def __init__(self, year_generator: YearGenerator, input_data: InputData):
        """
        初始化成本计算器

        Args:
            year_generator: 年份生成器
            input_data: 输入数据
        """
        self.yg = year_generator
        self.input = input_data

    def calculate_material_cost(self, year: str) -> float:
        """
        计算某年材料成本

        Args:
            year: 年份名称

        Returns:
            float: 年度材料成本
        """
        return self.input.material_cost.get_total_material_cost(year)

    def calculate_fuel_cost(self, year: str) -> float:
        """
        计算某年燃料及动力成本

        Args:
            year: 年份名称

        Returns:
            float: 年度燃料成本
        """
        return self.input.fuel_cost.get_total_fuel_cost(year)

    def calculate_labor_cost(self) -> float:
        """
        计算年度人工成本（年总额）

        Returns:
            float: 年度人工成本
        """
        return self.input.labor_cost.get_total_labor_cost()

    def calculate_repair_cost(self, fixed_asset_value: float) -> float:
        """
        计算年度修理费

        Args:
            fixed_asset_value: 固定资产原值

        Returns:
            float: 年度修理费
        """
        return fixed_asset_value * self.input.other_costs.repair_rate

    def calculate_total_cost(self, depreciation: float, amortization: float,
                            material_cost: float, fuel_cost: float,
                            labor_cost: float, repair_cost: float) -> float:
        """
        计算总成本费用

        Returns:
            float: 总成本费用
        """
        return (
            depreciation +
            amortization +
            material_cost +
            fuel_cost +
            labor_cost +
            repair_cost
        )

    def get_yearly_costs(self, depreciation_dict: Dict[str, float],
                         amortization_dict: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """
        获取各年成本明细

        Returns:
            dict: 各年成本明细字典
        """
        result = {}
        years = self.yg.generate_year_names()

        # 固定成本
        annual_labor_cost = self.calculate_labor_cost()
        asset_formation = self.input.asset_formation
        fixed_asset_value = asset_formation.building_asset + asset_formation.equipment_asset
        annual_repair_cost = self.calculate_repair_cost(fixed_asset_value)

        for year in years:
            year_num = self.yg.get_year_index(year)

            # 材料和燃料成本（只在运营期有）
            if self.yg.is_operation_year(year_num):
                material_cost = self.calculate_material_cost(year)
                fuel_cost = self.calculate_fuel_cost(year)
            else:
                material_cost = 0.0
                fuel_cost = 0.0

            result[year] = {
                "折旧费": depreciation_dict.get(year, 0.0),
                "摊销费": amortization_dict.get(year, 0.0),
                "材料成本": material_cost,
                "燃料成本": fuel_cost,
                "人工成本": annual_labor_cost if self.yg.is_operation_year(year_num) else 0.0,
                "修理费": annual_repair_cost if self.yg.is_operation_year(year_num) else 0.0
            }

        return result


class ProfitCalculator:
    """利润计算模块"""

    def __init__(self, year_generator: YearGenerator, input_data: InputData):
        """
        初始化利润计算器

        Args:
            year_generator: 年份生成器
            input_data: 输入数据
        """
        self.yg = year_generator
        self.input = input_data

    def calculate_gross_profit(self, revenue: float, cost: float) -> float:
        """
        计算毛利润

        Args:
            revenue: 营业收入
            cost: 总成本

        Returns:
            float: 毛利润
        """
        return revenue - cost

    def calculate_taxable_income(self, gross_profit: float) -> float:
        """
        计算应纳税所得额

        Args:
            gross_profit: 毛利润

        Returns:
            float: 应纳税所得额
        """
        if gross_profit <= 0:
            return 0.0
        return gross_profit

    def calculate_income_tax(self, taxable_income: float) -> float:
        """
        计算企业所得税

        Args:
            taxable_income: 应纳税所得额

        Returns:
            float: 企业所得税
        """
        return taxable_income * self.input.tax_params.corporate_tax_rate

    def calculate_net_profit(self, gross_profit: float, income_tax: float) -> float:
        """
        计算净利润

        Args:
            gross_profit: 毛利润
            income_tax: 企业所得税

        Returns:
            float: 净利润
        """
        return gross_profit - income_tax


class CashFlowCalculator:
    """现金流计算模块"""

    def __init__(self, year_generator: YearGenerator, input_data: InputData):
        """
        初始化现金流计算器

        Args:
            year_generator: 年份生成器
            input_data: 输入数据
        """
        self.yg = year_generator
        self.input = input_data

    def calculate_investment_cash_flow(self, investment_dict: Dict[str, float]) -> Dict[str, float]:
        """
        计算投资现金流

        Args:
            investment_dict: 投资年度分布

        Returns:
            dict: 投资现金流（负值表示流出）
        """
        return {year: -value for year, value in investment_dict.items()}

    def calculate_operating_cash_flow(self, revenue: float, cost: float, tax: float,
                                     depreciation: float) -> float:
        """
        计算经营现金流

        Args:
            revenue: 营业收入
            cost: 经营成本（不含折旧）
            tax: 所得税
            depreciation: 折旧

        Returns:
            float: 经营现金流
        """
        # 经营现金流 = 营业收入 - 经营成本 - 所得税
        return revenue - cost - tax

    def calculate_net_present_value(self, cash_flows: List[float], discount_rate: float) -> float:
        """
        计算净现值（NPV）

        Args:
            cash_flows: 现金流列表
            discount_rate: 折现率

        Returns:
            float: 净现值
        """
        npv = 0.0
        for i, cf in enumerate(cash_flows):
            # 确保现金流是数值类型
            cf_value = float(cf) if cf is not None else 0.0
            npv += cf_value / ((1 + discount_rate) ** i)
        return npv

    def calculate_internal_rate_of_return(self, cash_flows: List[float]) -> float:
        """
        计算内部收益率（IRR）
        使用牛顿迭代法

        Args:
            cash_flows: 现金流列表

        Returns:
            float: 内部收益率
        """
        # 使用numpy的irr函数
        return np.irr(cash_flows)

    def calculate_payback_period(self, cumulative_cash_flows: List[float]) -> int:
        """
        计算投资回收期

        Args:
            cumulative_cash_flows: 累计现金流列表

        Returns:
            int: 投资回收期（年）
        """
        for i, cum_cf in enumerate(cumulative_cash_flows):
            if cum_cf >= 0:
                return i + 1
        return len(cumulative_cash_flows)
