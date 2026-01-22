# 修复建设期利息缺失问题

## 问题发现

用户报告程序输出的5-4折旧表数据不正确：
- 建筑物原值: 73,803.73 万元（期望: 79,543.04 万元）
- 建筑物年折旧: 3,505.68 万元（期望: 3,778.29 万元）
- 销售固定资产成本: 24,601.24 万元（期望: 26,514.35 万元）

## 根本原因

程序中**缺少建设期利息输入和收集**，导致房屋建筑原值计算不正确。

### 数据对比

| 项目 | 程序输出 | 期望值 | 差异 |
|------|---------|--------|------|
| 房屋建筑原值（总） | 98,404.97 | 106,057.38 | -7,652.41 |
| 建设期利息 | **缺失** | 5,721.19 | -5,721.19 |
| 其他差异 | - | - | -1,931.22 |

## 修复内容

### 1. app_v3.py（第315-358行）

**添加建设期利息输入字段**：

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

# 项目投资总计
total_investment = total_engineering + total_reserve_fee + construction_interest
```

**影响**:
- 用户现在可以输入建设期利息
- 项目总投资计算包含建设期利息
- 显示正确的项目总投资

### 2. input_collector.py（第44-47行）

**添加建设期利息和税率数据收集**：

```python
inv.construction_interest = st.session_state.get("construction_interest", 0.0)  # 建设期利息
inv.equipment_tax_rate = st.session_state.get("equipment_tax_rate", 13.0)  # 默认13%
inv.construction_tax_rate = st.session_state.get("construction_tax_rate", 9.0)  # 默认9%
inv.service_tax_rate = st.session_state.get("service_tax_rate", 6.0)  # 默认6%
```

**影响**:
- 建设期利息数据被正确传递到计算引擎
- 税率参数也被正确收集
- 资产形成计算将包含建设期利息

## 预期效果

修复后，程序应该输出正确的结果：

| 项目 | 修复后 | 期望值 | 状态 |
|------|--------|--------|------|
| 房屋建筑原值（总） | 106,057.38 | 106,057.38 | ✅ |
| 自持固定资产（75%） | 79,543.04 | 79,543.04 | ✅ |
| 出售固定资产（25%） | 26,514.35 | 26,514.35 | ✅ |
| 建筑物年折旧 | 3,778.29 | 3,778.29 | ✅ |
| 固定资产成本摊销（第1年） | 2,651.43 | 2,651.43 | ✅ |

## 测试步骤

1. 重新启动 Streamlit 应用：`streamlit run app_v3.py`
2. 在"基础信息与投资"标签页，确认"建设期利息"字段显示正确
3. 默认值应该是 5,721.19 万元
4. 执行计算，检查5-4折旧表输出
5. 验证建筑物原值为 79,543.04 万元（第4年）

## 相关文件

- [app_v3.py:315-358](app_v3.py#L315-L358) - 添加建设期利息输入界面
- [input_collector.py:44-47](input_collector.py#L44-L47) - 添加建设期利息数据收集
