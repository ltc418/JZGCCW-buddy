"""
数据结构定义
基于Excel分析结果定义的数据模型
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BasicInfo:
    """基础信息"""
    project_name: str = ""
    construction_period: int = 3  # 建设期（年）
    operation_period: int = 17   # 运营期（年）
    
    @property
    def total_period(self) -> int:
        """计算期"""
        return self.construction_period + self.operation_period


@dataclass
class ProjectInvestment:
    """项目投资估算（Excel Row 11-27）"""
    # 工程费（含税）
    building_cost: float = 0.0           # 建筑工程费（万元）
    building_equipment_cost: float = 0.0  # 建筑设备费（万元）
    building_installation_cost: float = 0.0  # 建筑设备安装费（万元）
    production_equipment_cost: float = 0.0    # 生产设备购置费（万元）
    production_installation_cost: float = 0.0 # 生产设备安装费（万元）

    # 工程建设其他费（含税）
    management_fee: float = 0.0          # 项目管理咨询费（万元）
    tech_service_fee: float = 0.0        # 项目建设技术服务费（万元）
    supporting_fee: float = 0.0          # 配套设施等其他费用（万元）
    land_use_fee: float = 0.0            # 土地使用费（万元）
    patent_fee: float = 0.0              # 专利及专有技术费（万元）
    preparation_fee: float = 0.0        # 生产准备及开办费（万元）

    # 预备费
    basic_reserve_rate: float = 0.0      # 基本预备费率（%）
    price_reserve_rate: float = 0.0      # 涨价预备费率（%）

    # 税率（用于计算不含税金额）
    equipment_tax_rate: float = 0.13    # 设备增值税率（%）
    construction_tax_rate: float = 0.09 # 建筑税率（%）
    service_tax_rate: float = 0.06      # 服务税率（%）
    land_tax_type: str = "无形资产"      # 土地费用类型

    # 不含税值（由Excel计算，或系统自动计算）
    # 这些值会根据含税值和税率自动计算
    building_cost_no_tax: float = 0.0           # 建筑工程费不含税（万元）
    building_equipment_cost_no_tax: float = 0.0  # 建筑设备费不含税（万元）
    building_installation_cost_no_tax: float = 0.0  # 建筑设备安装费不含税（万元）
    management_fee_no_tax: float = 0.0          # 项目管理咨询费不含税（万元）
    tech_service_fee_no_tax: float = 0.0        # 项目建设技术服务费不含税（万元）
    supporting_fee_no_tax: float = 0.0          # 配套设施等其他费用不含税（万元）
    land_use_fee_no_tax: float = 0.0            # 土地使用费不含税（万元）
    patent_fee_no_tax: float = 0.0              # 专利及专有技术费不含税（万元）
    preparation_fee_no_tax: float = 0.0        # 生产准备及开办费不含税（万元）

    def calculate_no_tax_values(self):
        """根据含税值和税率计算不含税值"""
        self.building_cost_no_tax = self.building_cost / (1 + self.construction_tax_rate)
        self.building_equipment_cost_no_tax = self.building_equipment_cost / (1 + self.equipment_tax_rate)
        self.building_installation_cost_no_tax = self.building_installation_cost / (1 + self.construction_tax_rate)
        self.management_fee_no_tax = self.management_fee / (1 + self.service_tax_rate)
        self.tech_service_fee_no_tax = self.tech_service_fee / (1 + self.service_tax_rate)
        self.supporting_fee_no_tax = self.supporting_fee / (1 + self.construction_tax_rate)
        self.land_use_fee_no_tax = self.land_use_fee / (1 + 0)  # 土地税率0
        self.patent_fee_no_tax = self.patent_fee / (1 + self.service_tax_rate)
        self.preparation_fee_no_tax = self.preparation_fee / (1 + self.construction_tax_rate)


@dataclass
class FixedAssetDetail:
    """固定资产明细"""
    asset_name: str  # 资产名称（房屋建筑、机械设备）
    engineering_fee: float = 0.0         # 工程费（万元）
    other_fixed_fee: float = 0.0          # 固定资产其他费用（万元）
    reserve_fee: float = 0.0              # 预备费（万元）
    construction_interest: float = 0.0     # 建设期利息（万元）
    total: float = 0.0                     # 合计（万元）
    depreciation_years: int = 20           # 折旧年限（年）
    salvage_rate: float = 5.0              # 残值率（%）


@dataclass
class IntangibleAssetDetail:
    """无形资产明细"""
    asset_name: str  # 资产名称（土地使用权、专利权等）
    total: float = 0.0                     # 合计（万元）
    amortization_years: int = 50            # 摊销年限（年）


@dataclass
class OtherAssetDetail:
    """其他资产明细"""
    asset_name: str  # 资产名称（开办费等）
    total: float = 0.0                     # 合计（万元）
    amortization_years: int = 5             # 摊销年限（年）


@dataclass
class AssetFormation:
    """
    资产形成（根据Excel '1 建筑工程财务模型参数' Row 32-45）
    """
    # 固定资产
    building_fixed_asset: FixedAssetDetail = field(default_factory=lambda: FixedAssetDetail(
        asset_name="房屋建筑",
        depreciation_years=20,
        salvage_rate=5.0
    ))
    equipment_fixed_asset: FixedAssetDetail = field(default_factory=lambda: FixedAssetDetail(
        asset_name="机械设备",
        depreciation_years=10,
        salvage_rate=5.0
    ))

    # 无形资产
    land_intangible_asset: IntangibleAssetDetail = field(default_factory=lambda: IntangibleAssetDetail(
        asset_name="土地使用权",
        amortization_years=50
    ))
    patent_intangible_asset: IntangibleAssetDetail = field(default_factory=lambda: IntangibleAssetDetail(
        asset_name="专利权",
        amortization_years=6
    ))

    # 其他资产
    other_asset: OtherAssetDetail = field(default_factory=lambda: OtherAssetDetail(
        asset_name="开办费",
        amortization_years=5
    ))

    # 进项税
    deductible_input_tax: float = 0.0  # 可抵扣建设投资进项税（万元）

    # 汇总
    fixed_asset_total: float = 0.0      # 固定资产合计（万元）
    intangible_asset_total: float = 0.0  # 无形资产合计（万元）
    other_asset_total: float = 0.0      # 其他资产合计（万元）
    investment_total: float = 0.0       # 投资合计（万元）

    # 固定资产原值（不含建设期利息）
    fixed_asset_original_value: float = 0.0  # 固定资产原值（不含建设期利息）


@dataclass
class AssetSalesPlan:
    """资产销售计划"""
    asset_sell_ratio: float = 0.25       # 出售固定资产占比（%）
    land_sell_ratio: float = 0.25        # 出售土地使用权占比（%）
    self_hold_ratio: float = 0.75       # 自持占比（%）
    
    # 年度销售数据
    annual_sales_ratios: List[float] = field(default_factory=list)  # 年度销售比例 [0.1, 0.3, 0.3, 0.3]
    annual_sales_revenue: Dict[str, float] = field(default_factory=dict)  # 年度销售收入
    annual_sales_cost: Dict[str, float] = field(default_factory=dict)    # 年度销售成本
    annual_land_amortization: Dict[str, float] = field(default_factory=dict)  # 年度土地摊销
    
    # 总销售收入（保留向后兼容）
    asset_sales_revenue: float = 0.0    # 固定资产销售收入（含税）


@dataclass
class InvestmentPlan:
    """投融资计划（按年）"""
    # 自有资金
    equity_fund: List[float] = field(default_factory=list)  # 每年自有资金投入
    
    # 借款
    loan_fund: List[float] = field(default_factory=list)    # 每年借款金额
    
    # 资金使用
    investment_schedule: Dict[str, List[float]] = field(default_factory=dict)  # 各项投资按年度安排


@dataclass
class BankLoanPlan:
    """银行借款计划"""
    loan_years: List[int] = field(default_factory=list)    # 借款年份
    loan_amounts: List[float] = field(default_factory=list) # 借款金额
    interest_rate: float = 0.0588                           # 年利率
    repayment_period: int = 15                              # 还款期限（年）
    repayment_method: str = "等额本金"  # 还款方式


@dataclass
class SalesRevenue:
    """产品销售收入（按年）"""
    annual_revenue: Dict[str, float] = field(default_factory=dict)  # 年度销售收入


@dataclass
class MaterialCost:
    """外购材料成本（按年）"""
    # 8种材料
    material_1: Dict[str, float] = field(default_factory=dict)
    material_2: Dict[str, float] = field(default_factory=dict)
    material_3: Dict[str, float] = field(default_factory=dict)
    material_4: Dict[str, float] = field(default_factory=dict)
    material_5: Dict[str, float] = field(default_factory=dict)
    material_6: Dict[str, float] = field(default_factory=dict)
    material_7: Dict[str, float] = field(default_factory=dict)
    material_8: Dict[str, float] = field(default_factory=dict)
    
    def get_total_material_cost(self, year: str) -> float:
        """获取某年总材料成本"""
        total = 0.0
        materials = [
            self.material_1, self.material_2, self.material_3, self.material_4,
            self.material_5, self.material_6, self.material_7, self.material_8
        ]
        for material in materials:
            total += material.get(year, 0.0)
        return total


@dataclass
class FuelCost:
    """外购燃料及动力成本（按年）"""
    fuel_1: Dict[str, float] = field(default_factory=dict)
    fuel_2: Dict[str, float] = field(default_factory=dict)
    fuel_3: Dict[str, float] = field(default_factory=dict)
    fuel_4: Dict[str, float] = field(default_factory=dict)
    fuel_5: Dict[str, float] = field(default_factory=dict)
    fuel_6: Dict[str, float] = field(default_factory=dict)
    fuel_7: Dict[str, float] = field(default_factory=dict)
    fuel_8: Dict[str, float] = field(default_factory=dict)
    
    def get_total_fuel_cost(self, year: str) -> float:
        """获取某年总燃料成本"""
        total = 0.0
        fuels = [
            self.fuel_1, self.fuel_2, self.fuel_3, self.fuel_4,
            self.fuel_5, self.fuel_6, self.fuel_7, self.fuel_8
        ]
        for fuel in fuels:
            total += fuel.get(year, 0.0)
        return total


@dataclass
class LaborCost:
    """工资福利成本"""
    # 人员构成
    admin_persons: int = 0              # 行政管理人员人数
    admin_salary: float = 0.0           # 行政管理人员人均年工资
    
    tech_persons: int = 0               # 专业技术人员人数
    tech_salary: float = 0.0            # 专业技术人员人均年工资
    
    security_persons: int = 0           # 安保人员人数
    security_salary: float = 0.0        # 安保人员人均年工资
    
    cleaning_persons: int = 0           # 保洁人员人数
    cleaning_salary: float = 0.0        # 保洁人员人均年工资
    
    welfare_rate: float = 0.14         # 福利费率（%）
    
    def get_total_salary(self) -> float:
        """获取工资总额"""
        return (
            self.admin_persons * self.admin_salary +
            self.tech_persons * self.tech_salary +
            self.security_persons * self.security_salary +
            self.cleaning_persons * self.cleaning_salary
        )
    
    def get_total_labor_cost(self) -> float:
        """获取总人工成本（含福利费）"""
        return self.get_total_salary() * (1 + self.welfare_rate)


@dataclass
class OtherCosts:
    """修理费及其他费用"""
    repair_rate: float = 0.005          # 修理费率（固定资产原值的0.5%）
    other_mfg_rate: float = 0.0         # 其他制造费率
    other_mgt_rate: float = 0.0         # 其他管理费率
    other_sales_rate: float = 0.0       # 其他营业费率


@dataclass
class TaxParams:
    """赋税参数及补贴收入"""
    corporate_tax_rate: float = 0.25    # 企业所得税税率（%）
    reserve_fund_rate: float = 0.1      # 盈余公积金比率（%）
    discount_rate: float = 0.06         # 净现值内部收益率ic
    
    # 税收优惠
    loss_carryforward_years: int = 5   # 亏损弥补年限（年）
    tax_benefit_coefficient: float = 1.0  # 年度税收优惠系数
    
    # 其他税费
    city_tax_rate: float = 0.07        # 城市维护建设税税率
    education_tax_rate: float = 0.05   # 教育税附加及地方教育税附加税率
    
    # 土地增值税
    land_increment_tax: float = 0.0    # 土地增值税
    
    # 补贴收入
    subsidy_income: Dict[str, float] = field(default_factory=dict)  # 年度补贴收入


@dataclass
class InputData:
    """完整输入数据"""
    basic_info: BasicInfo = field(default_factory=BasicInfo)
    project_investment: ProjectInvestment = field(default_factory=ProjectInvestment)
    asset_formation: AssetFormation = field(default_factory=AssetFormation)
    asset_sales_plan: AssetSalesPlan = field(default_factory=AssetSalesPlan)
    investment_plan: InvestmentPlan = field(default_factory=InvestmentPlan)
    bank_loan_plan: BankLoanPlan = field(default_factory=BankLoanPlan)
    sales_revenue: SalesRevenue = field(default_factory=SalesRevenue)
    material_cost: MaterialCost = field(default_factory=MaterialCost)
    fuel_cost: FuelCost = field(default_factory=FuelCost)
    labor_cost: LaborCost = field(default_factory=LaborCost)
    other_costs: OtherCosts = field(default_factory=OtherCosts)
    tax_params: TaxParams = field(default_factory=TaxParams)
