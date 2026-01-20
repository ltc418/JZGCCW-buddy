"""
测试计算引擎
"""
from year_generator import YearGenerator
from data_models import InputData
from calculation_engine import CalculationEngine

print("=" * 60)
print("测试财务计算引擎")
print("=" * 60)

# 创建测试数据
year_generator = YearGenerator(construction_period=3, operation_period=17)

input_data = InputData()

# 基础信息
input_data.basic_info.project_name = "测试项目"
input_data.basic_info.construction_period = 3
input_data.basic_info.operation_period = 17

# 项目投资
inv = input_data.project_investment
inv.building_cost = 67062.86
inv.building_equipment_cost = 2360.38
inv.building_installation_cost = 18299.19
inv.production_equipment_cost = 50000.0
inv.production_installation_cost = 30000.0
inv.management_fee = 2994.8
inv.tech_service_fee = 6036.83
inv.supporting_fee = 1737.79
inv.land_use_fee = 6505.72
inv.patent_fee = 0.0
inv.preparation_fee = 323.19
inv.basic_reserve_rate = 10.0
inv.price_reserve_rate = 0.0

# 资产形成
asset_form = input_data.asset_formation
asset_form.depreciation_years = 20
asset_form.salvage_rate = 5.0
asset_form.amortization_years = 10
# 使用新的资产形成结构
asset_form.building_fixed_asset.total = 100000.0
asset_form.equipment_fixed_asset.total = 0.0
asset_form.land_intangible_asset.total = 6505.72
asset_form.patent_intangible_asset.total = 0.0
asset_form.fixed_asset_total = 100000.0
asset_form.intangible_asset_total = 6505.72

# 销售收入
years = year_generator.generate_year_names()
sales_rev = input_data.sales_revenue
for year in years:
    year_num = year_generator.get_year_index(year)
    if year_generator.is_operation_year(year_num):
        sales_rev.annual_revenue[year] = 15000.0

# 人工成本
labor = input_data.labor_cost
labor.admin_persons = 5
labor.admin_salary = 12.0
labor.tech_persons = 15
labor.tech_salary = 10.0
labor.security_persons = 8
labor.security_salary = 8.0
labor.cleaning_persons = 6
labor.cleaning_salary = 6.0
labor.welfare_rate = 0.14

# 其他费用
other = input_data.other_costs
other.repair_rate = 0.005

# 税收
tax = input_data.tax_params
tax.corporate_tax_rate = 0.25
tax.city_tax_rate = 0.07
tax.education_tax_rate = 0.05
tax.discount_rate = 0.06

# 银行借款
loan = input_data.bank_loan_plan
loan.interest_rate = 5.88
loan.repayment_years = 15
loan.repayment_method = "等额本金"

print("\n1. 创建计算引擎...")
calc_engine = CalculationEngine(year_generator, input_data)

print("2. 执行所有计算...")
results = calc_engine.run_all_calculations()

print(f"\n3. 计算完成！生成 {len(results)} 个表格")
print("\n生成的表格:")
for i, sheet_name in enumerate(results.keys(), 1):
    print(f"  {i}. {sheet_name}")

print("\n4. 财务指标汇总表预览:")
if "财务分析结果汇总" in results:
    df = results["财务分析结果汇总"]
    print(df.to_string(index=False))

print("\n5. 建设投资估算表预览:")
if "1建设投资" in results:
    df = results["1建设投资"]
    print(df.to_string(index=False))

print("\n6. 总成本表预览（前5年）:")
if "5总成本" in results:
    df = results["5总成本"]
    print(df.head(6).to_string(index=False))

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
