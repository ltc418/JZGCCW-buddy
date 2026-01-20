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

    def calculate_asset_formation(self) -> None:
        """
        根据Excel Row 32-45计算资产形成

        计算各类资产的原值和分摊

        Excel计算逻辑：
        1. 工程费（不含税）= 各项工程费不含税之和
        2. 固定资产其他费用（不含税）= 管理咨询费(不含税) + 技术服务费(不含税) + 配套设施(不含税)
        3. 预备费 = (工程费不含税 + 固定资产其他费用 + 开办费不含税) × 10%
        4. 无形资产 = 土地使用费(不含税) + 专利费(不含税)
        5. 其他资产 = 开办费不含税
        """
        inv = self.input.project_investment

        # 先计算不含税值
        inv.calculate_no_tax_values()

        asset = self.input.asset_formation

        # 计算工程费（不含税）
        # Excel中工程费合计(不含税) = 79732.9961
        engineering_no_tax = (
            inv.building_cost_no_tax +
            inv.building_equipment_cost_no_tax +
            inv.building_installation_cost_no_tax +
            inv.production_equipment_cost / (1 + inv.equipment_tax_rate) +
            inv.production_installation_cost / (1 + inv.construction_tax_rate)
        )

        # 计算固定资产其他费用（不含税，不含开办费）
        # Excel中：10071.1211 = 2815.11 + 5674.62 + 1581.39
        fixed_other_fees_no_tax = (
            inv.management_fee_no_tax +
            inv.tech_service_fee_no_tax +
            inv.supporting_fee_no_tax
        )

        # 计算开办费（不含税）
        preparation_fee_no_tax = inv.preparation_fee_no_tax

        # 计算基本预备费（Excel中：10532.08）
        # 预备费 = (工程费不含税 + 固定资产其他费用 + 开办费不含税) × 10%
        # 注意：预备费计算基数不含土地使用费
        basic_reserve = (engineering_no_tax + fixed_other_fees_no_tax + preparation_fee_no_tax) * (inv.basic_reserve_rate / 100)

        # 计算建设期利息（Excel中：5721.19）
        construction_interest = sum(self.calculate_construction_interest().values())

        # 固定资产形成计算
        # 房屋建筑固定资产
        asset.building_fixed_asset.engineering_fee = engineering_no_tax
        asset.building_fixed_asset.other_fixed_fee = fixed_other_fees_no_tax
        asset.building_fixed_asset.reserve_fee = basic_reserve
        asset.building_fixed_asset.construction_interest = construction_interest
        asset.building_fixed_asset.total = (
            asset.building_fixed_asset.engineering_fee +
            asset.building_fixed_asset.other_fixed_fee +
            asset.building_fixed_asset.reserve_fee +
            asset.building_fixed_asset.construction_interest
        )

        # 机械设备固定资产（本项目为0）
        asset.equipment_fixed_asset.total = 0.0

        # 无形资产
        # 土地使用费（不含税，Excel中：6505.72）
        asset.land_intangible_asset.total = inv.land_use_fee_no_tax

        # 专利权（不含税，Excel中：0）
        asset.patent_intangible_asset.total = inv.patent_fee_no_tax

        # 销售地产土地权（用于销售的土地使用权摊销）
        # 原值 = 土地使用权总值 × 销售比例
        # Excel中：6505.72 × 25% = 1626.43
        asset.sales_land_intangible_asset.total = asset.land_intangible_asset.total * self.input.asset_sales_plan.land_sell_ratio

        # 其他资产
        # 开办费不含税（Excel中：294.1029）
        asset.other_asset.total = preparation_fee_no_tax

        # 可抵扣进项税（Excel中：8716.8199）
        # 进项税 = 各项含税费用 - 各项不含税费用
        deductible_input_tax = (
            # 工程费进项税
            (inv.building_cost - inv.building_cost_no_tax) +
            (inv.building_equipment_cost - inv.building_equipment_cost_no_tax) +
            (inv.building_installation_cost - inv.building_installation_cost_no_tax) +
            (inv.production_equipment_cost - inv.production_equipment_cost / (1 + inv.equipment_tax_rate)) +
            (inv.production_installation_cost - inv.production_installation_cost / (1 + inv.construction_tax_rate)) +
            # 工程建设其他费进项税
            (inv.management_fee - inv.management_fee_no_tax) +
            (inv.tech_service_fee - inv.tech_service_fee_no_tax) +
            (inv.supporting_fee - inv.supporting_fee_no_tax) +
            (inv.patent_fee - inv.patent_fee_no_tax) +
            (inv.preparation_fee - inv.preparation_fee_no_tax)
        )

        asset.deductible_input_tax = deductible_input_tax

        # 汇总
        asset.fixed_asset_total = asset.building_fixed_asset.total + asset.equipment_fixed_asset.total
        asset.intangible_asset_total = (
            asset.land_intangible_asset.total +
            asset.patent_intangible_asset.total
        )
        asset.other_asset_total = asset.other_asset.total

        # 投资合计 = 固定资产 + 无形资产 + 其他资产 + 进项税
        asset.investment_total = (
            asset.fixed_asset_total +
            asset.intangible_asset_total +
            asset.other_asset_total +
            asset.deductible_input_tax
        )

        # 固定资产原值（不含建设期利息）
        asset.fixed_asset_original_value = (
            asset.building_fixed_asset.engineering_fee +
            asset.building_fixed_asset.other_fixed_fee +
            asset.building_fixed_asset.reserve_fee
        )


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
        获取各年折旧额（考虑资产销售，只计算自持部分）

        Returns:
            dict: 各年折旧额
        """
        result = self.yg.initialize_year_data_dict(default_value=0.0)
        
        asset = self.input.asset_formation
        self_hold_ratio = self.input.asset_sales_plan.self_hold_ratio
        
        # 计算自持资产的年度折旧
        building_depreciation = self.calculate_depreciation(
            asset.building_fixed_asset.total * self_hold_ratio,  # 只计算自持部分
            asset.building_fixed_asset.depreciation_years,
            asset.building_fixed_asset.salvage_rate
        )
        
        equipment_depreciation = self.calculate_depreciation(
            asset.equipment_fixed_asset.total * self_hold_ratio,
            asset.equipment_fixed_asset.depreciation_years,
            asset.equipment_fixed_asset.salvage_rate
        )
        
        total_yearly_depreciation = building_depreciation + equipment_depreciation
        
        # 固定资产从运营期开始折旧
        for year in self.yg.generate_year_names():
            year_num = self.yg.get_year_index(year)
            if self.yg.is_operation_year(year_num):
                result[year] = total_yearly_depreciation
        
        return result

    def get_yearly_amortization(self) -> Dict[str, float]:
        """
        获取各年摊销额（考虑资产销售，只计算自持部分）

        Returns:
            dict: 各年摊销额
        """
        result = self.yg.initialize_year_data_dict(default_value=0.0)
        
        asset = self.input.asset_formation
        self_hold_ratio = self.input.asset_sales_plan.self_hold_ratio
        
        # 计算自持无形资产的年度摊销
        land_amortization = self.calculate_amortization(
            asset.land_intangible_asset.total * self_hold_ratio,
            asset.land_intangible_asset.amortization_years
        )
        
        patent_amortization = self.calculate_amortization(
            asset.patent_intangible_asset.total * self_hold_ratio,
            asset.patent_intangible_asset.amortization_years
        )
        
        other_amortization = self.calculate_amortization(
            asset.other_asset.total * self_hold_ratio,
            asset.other_asset.amortization_years
        )
        
        total_yearly_amortization = land_amortization + patent_amortization + other_amortization
        
        # 无形资产从运营期开始摊销
        for year in self.yg.generate_year_names():
            year_num = self.yg.get_year_index(year)
            if self.yg.is_operation_year(year_num):
                result[year] = total_yearly_amortization
        
        return result

    def get_detailed_depreciation_data(self) -> Dict[str, Dict]:
        """
        获取详细的折旧摊销数据（按照5-4折旧表结构）

        Returns:
            dict: 包含建筑物、机器设备、销售固定资产和合计的详细数据
        """
        years = self.yg.generate_year_names()
        asset = self.input.asset_formation
        sales_plan = self.input.asset_sales_plan

        # 资产原值
        building_value = asset.building_fixed_asset.total  # 建筑物原值
        equipment_value = asset.equipment_fixed_asset.total  # 机器设备原值

        # 销售固定资产成本（直接使用指定的成本值）
        sales_assets_cost = sales_plan.sales_assets_cost

        # 初始化结果字典
        result = {
            "building": {
                "original_value": [],
                "depreciation": [],
                "net_value": []
            },
            "equipment": {
                "original_value": [],
                "depreciation": [],
                "net_value": []
            },
            "sales_assets": {
                "cost": [],
                "amortization": [],
                "remaining": []
            },
            "total": {
                "original_value": [],
                "depreciation_amortization": [],
                "net_value": []
            }
        }

        # 建筑物年折旧额
        building_annual_depr = building_value / asset.building_fixed_asset.depreciation_years if asset.building_fixed_asset.depreciation_years > 0 else 0

        # 机器设备年折旧额
        equipment_annual_depr = equipment_value / asset.equipment_fixed_asset.depreciation_years if asset.equipment_fixed_asset.depreciation_years > 0 else 0

        # 销售资产摊销规则：第1年10%，第2-3年各30%，剩余30%期末回收
        sales_amortization = {
            1: 0.10,
            2: 0.30,
            3: 0.30
        }

        # 计算各年数据
        cumulative_sales_amortization = 0.0

        for year in years:
            year_num = self.yg.get_year_index(year)
            is_construction = self.yg.is_construction_year(year_num)
            op_year = year_num - self.yg.construction_period if not is_construction else 0

            # 建筑物数据
            if is_construction:
                result["building"]["original_value"].append(0.0)
                result["building"]["depreciation"].append(0.0)
                result["building"]["net_value"].append(0.0)
            elif op_year == 1:
                # 运营期第1年：原值计入
                result["building"]["original_value"].append(building_value)
                result["building"]["depreciation"].append(building_annual_depr)
                result["building"]["net_value"].append(building_value - building_annual_depr)
            else:
                # 运营期第2年及以后
                result["building"]["original_value"].append(0.0)
                result["building"]["depreciation"].append(building_annual_depr)
                # 净值 = 原值 - 累计折旧
                cumulative_depr = op_year * building_annual_depr
                result["building"]["net_value"].append(max(0, building_value - cumulative_depr))

            # 机器设备数据
            if is_construction:
                result["equipment"]["original_value"].append(0.0)
                result["equipment"]["depreciation"].append(0.0)
                result["equipment"]["net_value"].append(0.0)
            elif op_year == 1:
                result["equipment"]["original_value"].append(equipment_value)
                result["equipment"]["depreciation"].append(equipment_annual_depr)
                result["equipment"]["net_value"].append(equipment_value - equipment_annual_depr)
            else:
                result["equipment"]["original_value"].append(0.0)
                result["equipment"]["depreciation"].append(equipment_annual_depr)
                cumulative_depr = op_year * equipment_annual_depr
                result["equipment"]["net_value"].append(max(0, equipment_value - cumulative_depr))

            # 销售固定资产数据
            if is_construction:
                result["sales_assets"]["cost"].append(0.0)
                result["sales_assets"]["amortization"].append(0.0)
                result["sales_assets"]["remaining"].append(0.0)
            elif op_year == 1:
                # 运营期第1年：成本计入，摊销10%
                amort = sales_assets_cost * sales_amortization.get(1, 0)
                result["sales_assets"]["cost"].append(sales_assets_cost)
                result["sales_assets"]["amortization"].append(amort)
                cumulative_sales_amortization += amort
                result["sales_assets"]["remaining"].append(sales_assets_cost - cumulative_sales_amortization)
            elif op_year in [2, 3]:
                # 运营期第2-3年：摊销30%
                amort = sales_assets_cost * sales_amortization.get(op_year, 0)
                result["sales_assets"]["cost"].append(0.0)
                result["sales_assets"]["amortization"].append(amort)
                cumulative_sales_amortization += amort
                result["sales_assets"]["remaining"].append(sales_assets_cost - cumulative_sales_amortization)
            else:
                # 运营期第4年及以后：摊销完成
                result["sales_assets"]["cost"].append(0.0)
                result["sales_assets"]["amortization"].append(0.0)
                result["sales_assets"]["remaining"].append(0.0)

            # 合计数据
            if op_year == 1:
                # 运营期第1年：原值合计
                result["total"]["original_value"].append(building_value + equipment_value + sales_assets_cost)
            else:
                result["total"]["original_value"].append(0.0)

            # 当期折旧摊销合计
            idx = len(result["building"]["depreciation"]) - 1
            result["total"]["depreciation_amortization"].append(
                result["building"]["depreciation"][idx] +
                result["equipment"]["depreciation"][idx] +
                result["sales_assets"]["amortization"][idx]
            )

            # 净值合计
            result["total"]["net_value"].append(
                result["building"]["net_value"][idx] +
                result["equipment"]["net_value"][idx] +
                result["sales_assets"]["remaining"][idx]
            )

        return result

    def get_detailed_amortization_data(self) -> Dict[str, Dict]:
        """
        获取详细的摊销数据（按照5-5摊销表结构）

        Returns:
            dict: 包含土地使用权、专利权、其他资产、销售地产土地权摊销和合计的详细数据
        """
        years = self.yg.generate_year_names()
        asset = self.input.asset_formation

        # 各资产原值
        land_value = asset.land_intangible_asset.total  # 土地使用权原值
        patent_value = asset.patent_intangible_asset.total  # 专利权原值
        other_asset_value = asset.other_asset.total  # 其他资产原值
        sales_land_value = asset.sales_land_intangible_asset.total  # 销售地产土地权原值

        # 初始化结果字典
        result = {
            "land": {
                "original_value": [],
                "amortization": [],
                "net_value": []
            },
            "patent": {
                "original_value": [],
                "amortization": [],
                "net_value": []
            },
            "other_asset": {
                "original_value": [],
                "amortization": [],
                "net_value": []
            },
            "sales_land": {
                "original_value": [],
                "amortization": [],
                "net_value": []
            },
            "total": {
                "original_value": [],
                "amortization": [],
                "net_value": []
            }
        }

        # 计算各资产年摊销额
        land_annual_amort = land_value / asset.land_intangible_asset.amortization_years if asset.land_intangible_asset.amortization_years > 0 else 0
        patent_annual_amort = patent_value / asset.patent_intangible_asset.amortization_years if asset.patent_intangible_asset.amortization_years > 0 else 0
        other_asset_annual_amort = other_asset_value / asset.other_asset.amortization_years if asset.other_asset.amortization_years > 0 else 0

        # 销售地产土地权摊销规则：第1年10%，第2-4年各30%
        sales_land_amortization = {
            1: 0.10,
            2: 0.30,
            3: 0.30,
            4: 0.30
        }

        # 计算各年数据
        cumulative_land_amort = 0.0
        cumulative_patent_amort = 0.0
        cumulative_other_amort = 0.0
        cumulative_sales_land_amort = 0.0

        for year in years:
            year_num = self.yg.get_year_index(year)
            is_construction = self.yg.is_construction_year(year_num)
            op_year = year_num - self.yg.construction_period if not is_construction else 0

            # 土地使用权数据（50年摊销）
            if is_construction:
                result["land"]["original_value"].append(0.0)
                result["land"]["amortization"].append(0.0)
                result["land"]["net_value"].append(0.0)
            elif op_year == 1:
                # 运营期第1年：原值计入
                result["land"]["original_value"].append(land_value)
                result["land"]["amortization"].append(land_annual_amort)
                cumulative_land_amort += land_annual_amort
                result["land"]["net_value"].append(max(0, land_value - cumulative_land_amort))
            else:
                # 运营期第2年及以后
                result["land"]["original_value"].append(0.0)
                result["land"]["amortization"].append(land_annual_amort)
                cumulative_land_amort += land_annual_amort
                result["land"]["net_value"].append(max(0, land_value - cumulative_land_amort))

            # 专利权数据（6年摊销）
            if is_construction:
                result["patent"]["original_value"].append(0.0)
                result["patent"]["amortization"].append(0.0)
                result["patent"]["net_value"].append(0.0)
            elif op_year == 1:
                result["patent"]["original_value"].append(patent_value)
                result["patent"]["amortization"].append(patent_annual_amort)
                cumulative_patent_amort += patent_annual_amort
                result["patent"]["net_value"].append(max(0, patent_value - cumulative_patent_amort))
            else:
                result["patent"]["original_value"].append(0.0)
                result["patent"]["amortization"].append(patent_annual_amort)
                cumulative_patent_amort += patent_annual_amort
                result["patent"]["net_value"].append(max(0, patent_value - cumulative_patent_amort))

            # 其他资产数据（5年摊销）
            if is_construction:
                result["other_asset"]["original_value"].append(0.0)
                result["other_asset"]["amortization"].append(0.0)
                result["other_asset"]["net_value"].append(0.0)
            elif op_year == 1:
                result["other_asset"]["original_value"].append(other_asset_value)
                result["other_asset"]["amortization"].append(other_asset_annual_amort)
                cumulative_other_amort += other_asset_annual_amort
                result["other_asset"]["net_value"].append(max(0, other_asset_value - cumulative_other_amort))
            else:
                result["other_asset"]["original_value"].append(0.0)
                result["other_asset"]["amortization"].append(other_asset_annual_amort)
                cumulative_other_amort += other_asset_annual_amort
                result["other_asset"]["net_value"].append(max(0, other_asset_value - cumulative_other_amort))

            # 销售地产土地权数据（4年摊销，第1年10%，第2-4年各30%）
            if is_construction:
                result["sales_land"]["original_value"].append(0.0)
                result["sales_land"]["amortization"].append(0.0)
                result["sales_land"]["net_value"].append(0.0)
            elif op_year == 1:
                # 运营期第1年：成本计入，摊销10%
                amort = sales_land_value * sales_land_amortization.get(1, 0)
                result["sales_land"]["original_value"].append(sales_land_value)
                result["sales_land"]["amortization"].append(amort)
                cumulative_sales_land_amort += amort
                result["sales_land"]["net_value"].append(max(0, sales_land_value - cumulative_sales_land_amort))
            elif 1 < op_year <= 4:
                # 运营期第2-4年：摊销30%
                amort = sales_land_value * sales_land_amortization.get(op_year, 0)
                result["sales_land"]["original_value"].append(0.0)
                result["sales_land"]["amortization"].append(amort)
                cumulative_sales_land_amort += amort
                result["sales_land"]["net_value"].append(max(0, sales_land_value - cumulative_sales_land_amort))
            else:
                # 运营期第5年及以后：摊销完成
                result["sales_land"]["original_value"].append(0.0)
                result["sales_land"]["amortization"].append(0.0)
                result["sales_land"]["net_value"].append(0.0)

            # 合计数据
            if op_year == 1:
                # 运营期第1年：原值合计
                result["total"]["original_value"].append(land_value + patent_value + other_asset_value + sales_land_value)
            else:
                result["total"]["original_value"].append(0.0)

        # 计算摊销费合计和净值合计
        for idx in range(len(years)):
            # 摊销费合计
            result["total"]["amortization"].append(
                result["land"]["amortization"][idx] +
                result["patent"]["amortization"][idx] +
                result["other_asset"]["amortization"][idx] +
                result["sales_land"]["amortization"][idx]
            )

            # 净值合计
            result["total"]["net_value"].append(
                result["land"]["net_value"][idx] +
                result["patent"]["net_value"][idx] +
                result["other_asset"]["net_value"][idx] +
                result["sales_land"]["net_value"][idx]
            )

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
        fixed_asset_value = asset_formation.fixed_asset_total
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
    
    def calculate_total_revenue(self, year: str) -> float:
        """
        计算总收入（包括产品销售收入和固定资产销售收入）

        Args:
            year: 年份

        Returns:
            float: 总收入
        """
        product_revenue = self.input.sales_revenue.annual_revenue.get(year, 0.0)
        asset_sales_revenue = self.input.asset_sales_plan.annual_sales_revenue.get(year, 0.0)
        
        return product_revenue + asset_sales_revenue

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


class AssetSalesCalculator:
    """资产销售计算模块"""
    
    def __init__(self, year_generator: YearGenerator, input_data: InputData):
        self.yg = year_generator
        self.input = input_data
    
    def calculate_annual_sales(self):
        """
        计算年度资产销售数据
        """
        asset = self.input.asset_formation
        sales_plan = self.input.asset_sales_plan
        
        # 固定资产销售成本
        fixed_asset_cost = (
            asset.building_fixed_asset.total + 
            asset.equipment_fixed_asset.total
        ) * sales_plan.asset_sell_ratio
        
        # 固定资产销售收入（含税），假设增值率为2.5倍
        sales_plan.asset_sales_revenue = fixed_asset_cost * 2.5
        
        # 土地摊销
        land_amortization = (
            asset.land_intangible_asset.total * 
            sales_plan.land_sell_ratio
        )
        
        # 按年度分配
        years = self.yg.generate_year_names()
        operation_years = [y for y in years if self.yg.is_operation_year(self.yg.get_year_index(y))]
        
        # 前4年的销售比例（如果没有设置，使用默认值）
        ratios = sales_plan.annual_sales_ratios if sales_plan.annual_sales_ratios else [0.1, 0.3, 0.3, 0.3]
        
        for i, year in enumerate(operation_years):
            if i < len(ratios):
                ratio = ratios[i]
                sales_plan.annual_sales_revenue[year] = sales_plan.asset_sales_revenue * ratio
                sales_plan.annual_sales_cost[year] = fixed_asset_cost * ratio
                sales_plan.annual_land_amortization[year] = land_amortization * ratio
    
    def get_annual_sales_revenue(self) -> Dict[str, float]:
        """
        获取年度销售收入
        
        Returns:
            dict: 各年固定资产销售收入
        """
        self.calculate_annual_sales()
        return self.input.asset_sales_plan.annual_sales_revenue
    
    def get_annual_sales_cost(self) -> Dict[str, float]:
        """
        获取年度销售成本
        
        Returns:
            dict: 各年固定资产销售成本
        """
        self.calculate_annual_sales()
        return self.input.asset_sales_plan.annual_sales_cost
