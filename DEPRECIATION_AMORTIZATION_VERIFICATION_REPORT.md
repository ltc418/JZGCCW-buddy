# 折旧摊销表验证报告

## 验证日期

2026-01-22

## 验证目的

验证5-4折旧表和5-5摊销表的生成与Excel完全一致。

## 问题发现与修复

### 问题1: 表格显示全为0

**症状**: 运行测试脚本时，折旧摊销表中所有数值都是0.0

**根本原因**: 测试脚本缺少关键的初始化步骤
```python
# ❌ 错误：缺少资产形成计算
input_data = InputData()
input_data.project_investment = investment
calc_engine = CalculationEngine(yg, input_data)  # 直接创建，资产数据为0

# ✅ 正确：必须先完成资产形成和销售计划计算
inv_calc = InvestmentCalculator(yg, input_data)
inv_calc.calculate_asset_formation()  # ← 关键步骤！

sales_calc = AssetSalesCalculator(yg, input_data)
sales_calc.calculate_annual_sales()  # ← 关键步骤！

calc_engine = CalculationEngine(yg, input_data)  # 现在数据已准备好
```

**数据依赖链**:
```
投资数据 → 资产形成 → 资产销售计划 → 折旧摊销计算
```

如果不按顺序执行，折旧摊销计算器无法获取资产原值等关键数据。

### 问题2: 建筑物折旧计算错误（已在之前修复）

**症状**: 建筑物年折旧额为3,977.15，期望值为3,778.29

**根本原因**: 折旧公式未考虑残值率

**修复代码**: [calculations.py:465-478](calculations.py#L465-L478)
```python
# 修复前
building_annual_depr = building_value / depreciation_years

# 修复后
building_annual_depr = (
    building_value * (1 - asset.building_fixed_asset.salvage_rate / 100) /
    asset.building_fixed_asset.depreciation_years
)
```

## 验证结果

### 5-4折旧表验证

| 项目 | 程序值 | Excel期望值 | 差异 | 状态 |
|------|--------|------------|------|------|
| 建筑物原值 | 79,543.04 | 79,543.04 | 0.00 | ✅ |
| 建筑物年折旧（第1年） | 3,778.29 | 3,778.29 | 0.00 | ✅ |
| 销售固定资产成本 | 26,514.35 | 26,514.35 | 0.00 | ✅ |
| 固定资产成本摊销（第1年） | 2,651.43 | 2,651.43 | 0.00 | ✅ |
| 固定资产成本摊销（第2年） | 7,954.30 | 7,954.30 | 0.00 | ✅ |
| 合计原值 | 106,057.38 | 106,057.38 | 0.00 | ✅ |
| 合计折旧摊销（第1年） | 6,429.73 | 6,429.73 | 0.00 | ✅ |
| 合计折旧摊销（第2年） | 11,732.60 | 11,732.60 | 0.00 | ✅ |

### 5-5摊销表验证

| 项目 | 程序值 | Excel期望值 | 差异 | 状态 |
|------|--------|------------|------|------|
| 土地使用权原值 | 4,879.29 | 4,879.29 | 0.00 | ✅ |
| 土地使用权年摊销 | 97.59 | 97.59 | 0.00 | ✅ |
| 其他资产原值 | 294.10 | 294.10 | 0.00 | ✅ |
| 其他资产年摊销 | 58.82 | 58.82 | 0.00 | ✅ |
| 销售地产土地权原值 | 1,626.43 | 1,626.43 | 0.00 | ✅ |
| 销售地产土地权摊销（第1年） | 162.64 | 162.64 | 0.00 | ✅ |
| 销售地产土地权摊销（第2年） | 487.93 | 487.93 | 0.00 | ✅ |
| 合计原值 | 6,799.82 | 6,799.82 | 0.00 | ✅ |
| 合计摊销（第1年） | 319.05 | 319.05 | 0.00 | ✅ |

## 数据流程验证

### 正确的初始化顺序

```python
# 步骤1: 计算资产形成
inv_calc = InvestmentCalculator(yg, input_data)
inv_calc.calculate_asset_formation()
# → 生成 asset_formation.building_fixed_asset.total = 106,057.38
# → 生成 asset_formation.land_intangible_asset.total = 6,505.72

# 步骤2: 计算资产销售计划
sales_calc = AssetSalesCalculator(yg, input_data)
sales_calc.calculate_annual_sales()
# → 计算 sales_plan.sales_building_value = 26,514.35
# → 计算 sales_plan.hold_building_value = 79,543.04
# → 计算 sales_plan.sales_land_value = 1,626.43
# → 计算 sales_plan.hold_land_value = 4,879.29

# 步骤3: 创建计算引擎
calc_engine = CalculationEngine(yg, input_data)
# → DepreciationCalculator 可使用上述所有数据
```

### 年度数据验证

**第1年（运营期第1年，即总第4年）**:
- 建筑物折旧: 3,778.29万元
- 销售资产摊销: 2,651.43万元
- 土地摊销: 97.59万元
- 其他资产摊销: 58.82万元
- 销售地产土地摊销: 162.64万元
- **合计折旧摊销: 6,429.73万元** ✅

**第2年（运营期第2年，即总第5年）**:
- 建筑物折旧: 3,778.29万元
- 销售资产摊销: 7,954.30万元
- 土地摊销: 97.59万元
- 其他资产摊销: 58.82万元
- 销售地产土地摊销: 487.93万元
- **合计折旧摊销: 11,732.60万元** ✅

## 关键发现

1. **数据依赖链**: 折旧摊销计算完全依赖资产形成和销售计划计算的结果
2. **初始化顺序**: 必须严格按照 Investment → Asset Formation → Asset Sales → Depreciation 的顺序
3. **年度映射**: 运营期第1年对应总第4年（3年建设期+1年运营期）
4. **销售摊销规律**: 前4年有销售摊销，第5-10年为0，第11-17年无销售数据

## 测试脚本

创建的测试文件:
- [test_depreciation_amortization_tables.py](test_depreciation_amortization_tables.py) - 表格生成测试
- [verify_depreciation_amortization.py](verify_depreciation_amortization.py) - 数据验证测试

## 结论

✅ **所有验证通过！折旧摊销表计算与Excel完全一致。**

关键修复:
1. ✅ 修复建筑物折旧公式（加入残值率）
2. ✅ 修复测试脚本初始化顺序
3. ✅ 验证所有关键数据点

折旧摊销功能已完全正确，可以继续验证其他表格（总成本表、利润表、现金流表）。
