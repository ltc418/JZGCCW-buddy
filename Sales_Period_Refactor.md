# 资产销售计划重构 - 固定10年销售期

## 修改概述

根据Excel实际设计逻辑，将资产销售计划从**动态运营期长度**改为**固定10年销售期**（从运营期第1年开始）。

## 修改日期

2026-01-22

## 修改原因

用户反馈Excel设计逻辑为：
- 销售期固定为10年（从运营期第1年开始）
- Row 49显示"第1年"到"第10年"
- Row 50控制这10年的销售比例
- Row 51-53分别输出到不同的工作表
- 如果运营期少于10年，超出年份的销售比例设为0（选项B）

## 修改内容

### 1. data_models.py

**位置**: [data_models.py:214-216](data_models.py#L214-L216)

**修改前**:
```python
# 年度销售比例（按年横向布置，预留10年位置）
# Excel中：第1年10%，第2-4年各30%
annual_sales_ratios: List[float] = field(default_factory=lambda: [10.0, 30.0, 30.0, 30.0])
```

**修改后**:
```python
# 年度销售比例（固定10年销售期，从运营期第1年开始）
# 默认值：第1年10%，第2-4年各30%，第5-10年0%
annual_sales_ratios: List[float] = field(default_factory=lambda: [10.0, 30.0, 30.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
```

**影响**: 默认值从4年扩展到10年，符合固定10年销售期逻辑。

---

### 2. calculations.py

**位置**: [calculations.py:1095-1123](calculations.py#L1095-L1123)

**修改前**:
```python
# 年度销售数据
years = self.yg.generate_year_names()
operation_years = [y for y in years if self.yg.is_operation_year(self.yg.get_year_index(y))]

# 转换年度销售比例为小数
annual_ratios = [r / 100.0 for r in sales_plan.annual_sales_ratios]

# 清空旧的年度数据
sales_plan.annual_sales_revenue = {}
sales_plan.annual_sales_cost = {}
sales_plan.annual_land_amortization = {}

# 按年度分配
for i, year in enumerate(operation_years):
    if i < len(annual_ratios):
        ratio = annual_ratios[i]
        # ... 计算逻辑
```

**修改后**:
```python
# 年度销售数据
years = self.yg.generate_year_names()
operation_years = [y for y in years if self.yg.is_operation_year(self.yg.get_year_index(y))]

# 转换年度销售比例为小数（固定10年销售期）
annual_ratios = [r / 100.0 for r in sales_plan.annual_sales_ratios]

# 清空旧的年度数据
sales_plan.annual_sales_revenue = {}
sales_plan.annual_sales_cost = {}
sales_plan.annual_land_amortization = {}

# 按年度分配（固定10年销售期，从运营期第1年开始）
# annual_ratios[0]对应运营期第1年，annual_ratios[9]对应运营期第10年
for i, year in enumerate(operation_years):
    if i < 10:  # 最多处理10年销售期
        ratio = annual_ratios[i]
        # ... 计算逻辑
```

**影响**:
- 添加了 `if i < 10` 条件，限制最多处理10年
- 添加注释说明10年销售期与运营期的映射关系
- 保持向后兼容性，支持运营期少于10年的情况

---

### 3. app_v3.py

#### 3.1 快捷预设按钮

**位置**: [app_v3.py:547-586](app_v3.py#L547-L586)

**修改前**:
```python
with col1:
    if st.button("📊 均匀分布", key="preset_even"):
        operation_years_count = st.session_state.operation_period
        avg_ratio = 100.0 / operation_years_count
        for i in range(operation_years_count):
            st.session_state[f"annual_ratio_{i}"] = round(avg_ratio, 1)
        st.rerun()
```

**修改后**:
```python
st.info("💡 销售期固定为10年（从运营期第1年开始），如果运营期少于10年，超出年份保持0%")

with col1:
    if st.button("📊 均匀分布", key="preset_even"):
        # 10年平均分配
        avg_ratio = 100.0 / 10
        for i in range(10):
            st.session_state[f"annual_ratio_{i}"] = round(avg_ratio, 1)
        st.rerun()
```

**影响**: 所有快捷预设按钮都改为固定10年逻辑：
- 均匀分布：10年，每年10%
- 前期销售：第1年50%，第2-10年各5.56%
- 后期销售：第1-9年各5.56%，第10年50%
- 自定义：第1年10%，第2-4年各30%，第5-10年0%

---

#### 3.2 数据编辑器

**位置**: [app_v3.py:588-606](app_v3.py#L588-L606)

**修改前**:
```python
year_generator = YearGenerator(st.session_state.construction_period, st.session_state.operation_period)
years = year_generator.generate_year_names()
operation_years = [y for y in years if year_generator.is_operation_year(year_generator.get_year_index(y))]

# 构建年度销售比例数据
sales_data = []
for i, year in enumerate(operation_years):
    default_ratio = st.session_state.get(f"annual_ratio_{i}", 10.0 if i == 0 else 30.0)
    sales_data.append({
        '年份': year,
        '销售比例(%)': default_ratio
    })
```

**修改后**:
```python
# 固定10年销售期，使用"第1年"到"第10年"标签
# 构建年度销售比例数据
sales_data = []
default_ratios = [10.0, 30.0, 30.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 默认模式：前4年销售
for i in range(10):
    default_ratio = st.session_state.get(f"annual_ratio_{i}", default_ratios[i])
    sales_data.append({
        '年份': f"第{i+1}年",
        '销售比例(%)': default_ratio
    })
```

**影响**:
- 表格固定显示10行（第1年到第10年）
- 不再根据运营期动态变化
- 年份标签从"第4年"、"第5年"等改为"第1年"到"第10年"

---

#### 3.3 汇总计算

**位置**: [app_v3.py:649-663](app_v3.py#L649-L663)

**修改前**:
```python
# 计算汇总数据
annual_sales_ratios = [row['销售比例(%)'] for _, row in edited_df.iterrows()]
total_ratio = sum(annual_sales_ratios)

# 计算年度销售额
annual_revenues = {}
for i, (year, ratio) in enumerate(zip(operation_years, annual_sales_ratios)):
    annual_revenues[year] = total_sales_price * (ratio / 100.0)
```

**修改后**:
```python
# 计算汇总数据
annual_sales_ratios = [row['销售比例(%)'] for _, row in edited_df.iterrows()]
total_ratio = sum(annual_sales_ratios)

# 计算年度销售额（固定10年）
annual_revenues = {}
for i in range(10):
    year_label = f"第{i+1}年"
    ratio = annual_sales_ratios[i]
    annual_revenues[year_label] = total_sales_price * (ratio / 100.0)
```

**影响**: 年度销售额计算改为固定10年循环，键名为"第1年"到"第10年"。

---

#### 3.4 年度销售额显示

**位置**: [app_v3.py:702-718](app_v3.py#L702-L718)

**修改前**:
```python
# 使用更紧凑的布局显示年度数据
display_cols = st.columns(min(len(operation_years), 6))  # 最多6列
for i, year in enumerate(operation_years):
    with display_cols[i % 6]:
        revenue = annual_revenues[year]
        if revenue > 0:
            st.metric(
                f"{year}",
                f"{revenue:.2f}",
                help=f"总销售价格 × {annual_sales_ratios[i]:.1f}%"
            )
        else:
            st.metric(f"{year}", "0.00")
```

**修改后**:
```python
# 使用更紧凑的布局显示10年数据（每行最多5列）
st.info("💡 以下显示10年销售期的各年销售收入，仅显示销售额大于0的年份")
sales_years = [f"第{i+1}年" for i in range(10)]
display_cols = st.columns(5)  # 每行5列
for i, year_label in enumerate(sales_years):
    revenue = annual_revenues[year_label]
    ratio = annual_sales_ratios[i]
    if revenue > 0 or ratio > 0:  # 只显示有销售额或有销售比例的年份
        with display_cols[i % 5]:
            st.metric(
                year_label,
                f"{revenue:.2f}",
                help=f"总销售价格 {total_sales_price:,.2f} × {ratio:.1f}%"
            )
```

**影响**:
- 固定遍历10年
- 每行5列布局（原来是6列）
- 只显示有销售额或销售比例大于0的年份

---

### 4. verify_step3.py

**位置**: [verify_step3.py:123-129](verify_step3.py#L123-L129)

**修改前**:
```python
sales_plan.annual_sales_ratios = [item['ratio'] for item in excel_annual_sales]  # [10.0, 30.0, 30.0, 30.0]
```

**修改后**:
```python
# 固定10年销售期：前4年使用Excel数据，后6年设为0
sales_plan.annual_sales_ratios = [item['ratio'] for item in excel_annual_sales] + [0.0] * 6
```

**影响**: 验证脚本将4年的Excel数据扩展到10年，以匹配新的逻辑。

---

### 5. QUICK_START_SALES_PLAN.md

**更新内容**:
- 说明销售期固定为10年
- 更新所有快捷预设按钮的描述
- 添加Q3解释为什么销售期固定为10年
- 添加场景4：短运营期项目的处理方式
- 更新优化亮点，强调"固定10年销售期"

---

## 测试验证

### 验证脚本测试

运行 `verify_step3.py`：
```bash
python verify_step3.py
```

**结果**: ✅ 所有验证通过

```
====================================================================================================
✓✓✓ 所有验证通过！程序计算与 Excel 一致。
====================================================================================================
```

### 界面测试

启动应用：
```bash
streamlit run app_v3.py
```

**验证点**:
- ✅ 快捷预设按钮正常工作
- ✅ 数据编辑器显示10行（第1年到第10年）
- ✅ 汇总信息正确计算
- ✅ 年度销售额显示正确

---

## 向后兼容性

### 运营期 ≥ 10年

如果运营期为17年：
- 前10年按照销售比例分配
- 第11-17年不会生成销售数据（受 `if i < 10` 限制）

### 运营期 < 10年

如果运营期为5年：
- 前5年按照销售比例分配（第1-5年）
- 第6-10年的销售比例会被忽略（因为没有对应的运营年份）
- 建议将第6-10年的销售比例设为0

---

## 数据流向

根据Excel设计逻辑：

### Row 51: 用于出售的固定资产
- **数值**: 26,514.35万元 = 房屋建筑原值 × 25%
- **流向**: → "5-4折旧" 工作表
- **年度分配**: 26,514.35 × 年度销售比例

### Row 52: 出售固定资产对应的土地使用权摊销额
- **数值**: 1,626.43万元 = 土地使用权原值 × 25%
- **流向**: → 折旧摊销计算
- **年度分配**: 1,626.43 × 年度销售比例

### Row 53: 固定资产销售收入（含税）
- **数值**: 66,285.86万元（总销售价格，用户输入）
- **流向**: → "6收入" 工作表
- **年度分配**: 66,285.86 × 年度销售比例

---

## 用户指南

### 正常场景（运营期17年）

1. 设置销售比例：第1年10%，第2-4年各30%
2. 第5-10年设为0%（或设置其他比例）
3. 系统自动计算前10年的销售收入
4. 第11-17年不会生成销售数据

### 短运营期场景（运营期5年）

1. 设置销售比例：第1年10%，第2-4年各30%
2. 第5-10年设为0%
3. 系统只计算前5年的销售收入
4. 第6-10年的0%不影响结果

---

## 总结

本次修改将资产销售计划从**动态运营期长度**重构为**固定10年销售期**，完全符合Excel的设计逻辑：

✅ **销售期固定10年** - 不受运营期长度影响
✅ **年份标签统一** - 使用"第1年"到"第10年"
✅ **数据流向明确** - Row 51→5-4折旧，Row 52→摊销，Row 53→6收入
✅ **向后兼容** - 支持运营期少于10年的情况
✅ **验证通过** - 所有计算与Excel一致

修改后的程序更加专业、准确，完全符合Excel财务模型的实际需求。
