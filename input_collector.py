"""
输入数据收集器
从Streamlit表单收集数据并构建InputData对象
"""
import streamlit as st
from data_models import InputData
from year_generator import YearGenerator


def collect_input_data(construction_period: int, operation_period: int) -> InputData:
    """
    从Streamlit session state收集输入数据

    Args:
        construction_period: 建设期（年）
        operation_period: 运营期（年）

    Returns:
        InputData: 输入数据对象
    """
    # 获取session state中的所有输入值
    input_data = InputData()

    # 1. 基础信息
    input_data.basic_info.project_name = st.session_state.get("project_name", "")
    input_data.basic_info.construction_period = construction_period
    input_data.basic_info.operation_period = operation_period

    # 2. 项目投资
    inv = input_data.project_investment
    inv.building_cost = st.session_state.get("building_cost", 0.0)
    inv.building_equipment_cost = st.session_state.get("building_equipment", 0.0)
    inv.building_installation_cost = st.session_state.get("building_install", 0.0)
    inv.production_equipment_cost = st.session_state.get("production_equipment", 0.0)
    inv.production_installation_cost = st.session_state.get("production_install", 0.0)
    inv.management_fee = st.session_state.get("management_fee", 0.0)
    inv.tech_service_fee = st.session_state.get("tech_service_fee", 0.0)
    inv.supporting_fee = st.session_state.get("supporting_fee", 0.0)
    inv.land_use_fee = st.session_state.get("land_use_fee", 0.0)
    inv.patent_fee = st.session_state.get("patent_fee", 0.0)
    inv.preparation_fee = st.session_state.get("preparation_fee", 0.0)
    inv.basic_reserve_rate = st.session_state.get("basic_reserve_rate", 0.0)
    inv.price_reserve_rate = st.session_state.get("price_reserve_rate", 0.0)

    # 3. 资产形成（根据Excel Row 32-45）
    asset_form = input_data.asset_formation

    # 固定资产 - 房屋建筑
    asset_form.building_fixed_asset.depreciation_years = st.session_state.get("building_depr_years", 20)
    asset_form.building_fixed_asset.salvage_rate = st.session_state.get("building_salvage_rate", 5.0)

    # 固定资产 - 机械设备
    asset_form.equipment_fixed_asset.depreciation_years = st.session_state.get("equipment_depr_years", 10)
    asset_form.equipment_fixed_asset.salvage_rate = st.session_state.get("equipment_salvage_rate", 5.0)

    # 无形资产 - 土地使用权
    asset_form.land_intangible_asset.amortization_years = st.session_state.get("land_amort_years", 50)

    # 无形资产 - 专利权
    asset_form.patent_intangible_asset.amortization_years = st.session_state.get("patent_amort_years", 6)

    # 其他资产
    asset_form.other_asset.amortization_years = st.session_state.get("other_amort_years", 5)

    # 4. 销售收入
    yg = YearGenerator(construction_period, operation_period)
    years = yg.generate_year_names()

    sales_rev = input_data.sales_revenue
    sales_rev.annual_revenue = {}
    for year in years:
        year_num = yg.get_year_index(year)
        if yg.is_construction_year(year_num):
            # 建设期自动设为0
            sales_rev.annual_revenue[year] = 0.0
        else:
            key = f"sales_{year}"
            sales_rev.annual_revenue[year] = st.session_state.get(key, 10000.0)

    # 5. 材料成本
    mat_cost = input_data.material_cost
    for year in years:
        year_num = yg.get_year_index(year)
        if yg.is_construction_year(year_num):
            # 建设期自动设为0
            mat_cost.material_1[year] = 0.0
            mat_cost.material_2[year] = 0.0
        else:
            # 简化：只使用前几种材料
            mat_cost.material_1[year] = st.session_state.get(f"mat1_{year}", 0.0)
            mat_cost.material_2[year] = st.session_state.get(f"mat2_{year}", 0.0)

    # 6. 燃料成本
    fuel_cost = input_data.fuel_cost
    for year in years:
        year_num = yg.get_year_index(year)
        if yg.is_construction_year(year_num):
            # 建设期自动设为0
            fuel_cost.fuel_1[year] = 0.0
        else:
            fuel_cost.fuel_1[year] = st.session_state.get(f"fuel1_{year}", 0.0)

    # 7. 人工成本
    labor = input_data.labor_cost
    labor.admin_persons = st.session_state.get("admin_persons", 0)
    labor.admin_salary = st.session_state.get("admin_salary", 0.0)
    labor.tech_persons = st.session_state.get("tech_persons", 0)
    labor.tech_salary = st.session_state.get("tech_salary", 0.0)
    labor.security_persons = st.session_state.get("security_persons", 0)
    labor.security_salary = st.session_state.get("security_salary", 0.0)
    labor.cleaning_persons = st.session_state.get("cleaning_persons", 0)
    labor.cleaning_salary = st.session_state.get("cleaning_salary", 0.0)
    labor.welfare_rate = st.session_state.get("welfare_rate", 14.0) / 100

    # 8. 其他费用
    other = input_data.other_costs
    other.repair_rate = st.session_state.get("repair_rate", 0.5) / 100
    other.other_mfg_rate = st.session_state.get("other_mfg_rate", 0.0) / 100
    other.other_mgt_rate = st.session_state.get("other_mgt_rate", 0.0) / 100
    other.other_sales_rate = st.session_state.get("other_sales_rate", 0.0) / 100

    # 9. 税收参数
    tax = input_data.tax_params
    tax.corporate_tax_rate = st.session_state.get("corporate_tax_rate", 25.0) / 100
    tax.city_tax_rate = st.session_state.get("city_tax_rate", 7.0) / 100
    tax.education_tax_rate = st.session_state.get("education_tax_rate", 5.0) / 100
    tax.discount_rate = st.session_state.get("discount_rate", 6.0) / 100

    # 10. 银行借款
    loan = input_data.bank_loan_plan
    loan.interest_rate = st.session_state.get("loan_interest_rate", 5.88)
    loan.repayment_years = st.session_state.get("repayment_years", 15)
    loan.repayment_method = st.session_state.get("repayment_method", "等额本金")

    # 11. 其他参数
    tax.reserve_fund_rate = st.session_state.get("reserve_fund_rate", 10.0) / 100
    tax.loss_carryforward_years = st.session_state.get("loss_carryforward_years", 5)

    return input_data
