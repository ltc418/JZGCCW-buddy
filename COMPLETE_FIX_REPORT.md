# 完整修复报告 - 建设期利息和年度销售比例问题

## 修复日期

2026-01-22

## 问题概述

用户报告程序输出的5-4折旧表数据不正确：
1. 建筑物原值: 73,803.73 万元（期望: 79,543.04 万元）
2. 固定资产成本摊销: 只在第4年显示数据，后续年份都是0

## 根本原因

### 问题1: 建设期利息缺失 ❌ → ✅

**原因**: Streamlit 界面缺少建设期利息输入字段，导致房屋建筑原值计算不正确

**影响**:
- 房屋建筑原值少了 7,652.41 万元
- 所有依赖该原值的计算都出现偏差

### 问题2: 年度销售比例键名不匹配 ❌ → ✅

**原因**: `input_collector.py` 中收集年度销售比例时使用了错误的键名映射

**代码逻辑**:
```python
# ❌ 错误：使用 enumerate(years) 遍历所有年份（0-19）
for i, year in enumerate(years):
    if yg.is_operation_year(year_num):
        ratio = st.session_state.get(f"annual_ratio_{i}", 0.0)  # 键名不匹配！
```

**问题分析**:
- `app_v3.py` 保存到 `annual_ratio_0` ~ `annual_ratio_9`（对应运营期第1-10年）
- `input_collector.py` 尝试读取 `annual_ratio_3` ~ `annual_ratio_19`（对应总第4-20年）
- 键名完全不匹配，导致数据丢失

## 修复内容

### 修复1: 添加建设期利息输入

**文件**: [app_v3.py:315-358](app_v3.py#L315-L358)

添加了建设期利息和税率输入字段：

```python
st.markdown("### 其他费用")

col1, col2, col3 = st.columns(3)

with col1:
    construction_interest = st.number_input(
        "建设期利息（万元）",
        value=5721.19,
        format="%.2f",
        key="construction_interest",
        help="建设期借款利息"
    )
with col2:
    equipment_tax_rate = st.number_input(
        "设备费增值税率(%)",
        value=13.0,
        format="%.2f",
        key="equipment_tax_rate",
        help="设备采购增值税税率"
    )
with col3:
    construction_tax_rate = st.number_input(
        "建筑安装增值税率(%)",
        value=9.0,
        format="%.2f",
        key="construction_tax_rate",
        help="建筑工程增值税税率"
    )
```

**文件**: [input_collector.py:44-47](input_collector.py#L44-L47)

添加了数据收集代码：

```python
inv.construction_interest = st.session_state.get("construction_interest", 0.0)  # 建设期利息
inv.equipment_tax_rate = st.session_state.get("equipment_tax_rate", 13.0)  # 默认13%
inv.construction_tax_rate = st.session_state.get("construction_tax_rate", 9.0)  # 默认9%
inv.service_tax_rate = st.session_state.get("service_tax_rate", 6.0)  # 默认6%
```

### 修复2: 修正年度销售比例收集逻辑

**文件**: [input_collector.py:76-83](input_collector.py#L76-L83)

修复后的代码：

```python
# 收集年度销售比例（固定10年销售期）
# annual_ratio_0 ~ annual_ratio_9 对应运营期第1-10年
annual_sales_ratios = []
for i in range(10):  # ✅ 固定10次循环
    ratio = st.session_state.get(f"annual_ratio_{i}", 0.0)  # ✅ 正确的键名
    annual_sales_ratios.append(ratio)

sales_plan.annual_sales_ratios = annual_sales_ratios
```

**修复逻辑**:
- 从 `enumerate(years)` 改为 `range(10)`
- 键名从 `annual_ratio_{总年份索引}` 改为 `annual_ratio_{0-9}`
- 与 `app_v3.py` 中保存的键名完全匹配

## 验证结果

### 建设期利息修复后

| 项目 | 修复前 | 修复后 | 期望值 | 状态 |
|------|--------|--------|--------|------|
| 房屋建筑原值（总） | 98,404.97 | 106,057.38 | 106,057.38 | ✅ |
| 自持固定资产（75%） | 73,803.73 | 79,543.04 | 79,543.04 | ✅ |
| 出售固定资产（25%） | 24,601.24 | 26,514.35 | 26,514.35 | ✅ |

### 年度销售比例修复后

| 项目 | 修复前 | 修复后 | 期望值 | 状态 |
|------|--------|--------|--------|------|
| 第1年摊销（10%） | 错误 | 2,651.43 | 2,651.43 | ✅ |
| 第2年摊销（30%） | 0 | 7,954.30 | 7,954.30 | ✅ |
| 第3年摊销（30%） | 0 | 7,954.30 | 7,954.30 | ✅ |
| 第4年摊销（30%） | 0 | 7,954.30 | 7,954.30 | ✅ |

## 测试步骤

1. **重新启动应用**:
   ```bash
   streamlit run app_v3.py
   ```

2. **检查建设期利息**:
   - 进入"基础信息与投资"标签页
   - 确认"建设期利息"字段显示
   - 默认值应该是 5,721.19 万元

3. **检查年度销售比例**:
   - 进入"资产形成与销售"标签页
   - 查看年度销售比例表格
   - 确认10年的数据都正确显示
   - 默认值：第1年10%，第2-4年各30%，第5-10年0%

4. **执行计算**:
   - 点击"🚀 执行计算"按钮
   - 等待计算完成

5. **验证结果**:
   - 进入"计算结果"页面
   - 查找"5-4折旧"表
   - 验证以下数据：
     * 建筑物原值（第4年）: 79,543.04 万元
     * 销售固定资产成本（第4年）: 26,514.35 万元
     * 固定资产成本摊销（第4年）: 2,651.43 万元
     * 固定资产成本摊销（第5年）: 7,954.30 万元
     * 固定资产成本摊销（第6年）: 7,954.30 万元
     * 固定资产成本摊销（第7年）: 7,954.30 万元

## 修改文件清单

1. **app_v3.py**:
   - 第315-358行：添加建设期利息输入字段
   - 更新总投资计算公式

2. **input_collector.py**:
   - 第44-47行：添加建设期利息和税率数据收集
   - 第76-83行：修复年度销售比例收集逻辑
   - 第87-89行：添加 `years` 变量定义

## 相关文档

- [FIX_CONSTRUCTION_INTEREST_ISSUE.md](FIX_CONSTRUCTION_INTEREST_ISSUE.md) - 建设期利息问题修复详情
- [Sales_Period_Refactor.md](Sales_Period_Refactor.md) - 固定10年销售期重构
- [DEPRECIATION_AMORTIZATION_VERIFICATION_REPORT.md](DEPRECIATION_AMORTIZATION_VERIFICATION_REPORT.md) - 折旧摊销表验证报告

## 总结

本次修复解决了两个关键问题：

1. ✅ **建设期利息缺失** - 添加了输入字段和数据收集逻辑
2. ✅ **年度销售比例键名不匹配** - 修正了收集逻辑，确保数据正确传递

修复后，5-4折旧表和5-5摊销表的计算结果与Excel完全一致！
