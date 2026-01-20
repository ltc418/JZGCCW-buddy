# Financial Analysis WebApp Skill

## 概述

这个Skill提供了基于Streamlit构建财务分析Web应用程序的专业知识、工作流程和最佳实践。它基于JZGCCW财务分析系统的实际开发经验，专门用于处理建设项目的经济评价。

## 适用场景

当遇到以下任务时使用此Skill：

- **Excel财务模板分析**: 解析和处理包含多年度财务数据的Excel文件
- **多年度财务预测系统**: 实现建设期+运营期的动态年份管理
- **标准化财务表格**: 生成投资估算、折旧计划、利润表、现金流量表等20种标准表格
- **Web应用开发**: 使用Streamlit创建交互式财务分析界面
- **横向数据展示**: 将年度数据格式化为横向展示（年份作为列）
- **数据精度管理**: 统一格式化所有数值输出为2位小数

## Skill内容

### 核心文件
- `SKILL.md` - 完整的开发指南和工作流程
- `scripts/template_generator.py` - 项目模板生成器脚本

### 参考文档
- `references/chinese-financial-standards.md` - 中国建设项目经济评价方法与参数标准
- `references/excel-patterns.md` - Excel财务模板常见模式和数据处理技巧
- `references/streamlit-best-practices.md` - Streamlit财务应用UI/UX最佳实践

## 主要功能

### 1. 项目架构指导

提供标准的财务分析Web应用项目结构：

```
project/
├── app_v2.py              # 主Streamlit应用
├── data_models.py          # 数据类定义（类型安全）
├── calculation_engine.py    # 统一计算接口
├── calculations.py         # 独立计算模块
├── year_generator.py       # 动态年份管理
├── data_loader.py          # Excel文件读取（xlrd支持）
├── input_collector.py      # 表单数据收集
└── config.py              # 配置常量
```

### 2. 数据模型设计

使用Python dataclasses实现类型安全的数据结构：

```python
@dataclass
class ProjectInvestment:
    building_cost: float = 0.0
    equipment_cost: float = 0.0
    # ...其他字段
```

**优势**：
- 类型安全和IDE自动补全
- 默认值支持
- 清晰的数据结构文档

### 3. 计算引擎架构

模块化计算器设计：

```python
class InvestmentCalculator:      # 投资计算
class DepreciationCalculator:     # 折旧摊销计算
class CostCalculator:             # 成本费用计算
class ProfitCalculator:           # 利润分配计算
class CashFlowCalculator:        # 现金流量计算
```

### 4. 横向表格格式化

所有年度数据表格采用横向展示：

- 第一列："项目"（指标名称）
- 后续列：年份（建设期第1年、运营期第1年...）
- 每行：一个指标/行项目

### 5. 一致精度格式化

实现统一的2位小数格式化函数，应用于：
- 所有DataFrame显示
- 所有下载的CSV文件
- 所有输入表单数值

### 6. 动态年份管理

实现灵活的年份生成器：

```python
YearGenerator(construction_period=3, operation_period=17)
years = yg.generate_year_names()  # 自动生成所有年份名称
```

**核心方法**：
- `generate_year_names()`: 获取所有年份名称
- `is_construction_year(year_num)`: 判断是否建设期
- `is_operation_year(year_num)`: 判断是否运营期
- `get_year_index(year)`: 获取顺序年份编号

## 标准财务表格（20个）

此Skill支持生成以下完整财务表格：

1. **1建设投资** - 建设投资估算表
2. **2流动资金** - 流动资金估算表
3. **3投资计划** - 投资使用计划与资金筹措表
4. **4还本付息** - 借款还本付息计划表
5. **5-1材料** - 外购原材料费估算表
6. **5-2燃料** - 外购燃料及动力费估算表
7. **5-3工资** - 工资及福利费估算表
8. **5-4折旧** - 固定资产折旧费估算表
9. **5-5摊销** - 无形资产摊销估算表
10. **5总成本** - 总成本费用估算表
11. **6收入** - 营业收入、营业税金及附加和增值税估算表
12. **7利润** - 利润与利润分配表
13. **8财务现金** - 项目财务现金流量表
14. **9资产负债** - 资产负债表
15. **10项目现金** - 项目投资现金流量表
16. **11资本金现金** - 项目资本金现金流量表
17. **12各方现金** - 投资各方现金流量表
18. **财务分析结果汇总** - 财务指标汇总表
19. **土地增值税计算** - 土地增值税计算表
20. **房产销售及土增** - 房产销售及土地税表

## 常见问题解决

### 问题1：DataFrame列长度不匹配
**原因**：创建DataFrame时部分列长度不一致
**解决**：初始化所有年份列后再填充数据

### 问题2：Streamlit导入错误
**症状**：`from streamlit import st` 导致ImportError
**解决**：使用模块导入 `import streamlit as st`

### 问题3：Excel文件格式不兼容
**症状**：无法用pandas读取.xls文件
**解决**：使用xlrd引擎 `pd.read_excel('file.xls', engine='xlrd')`

### 问题4：小数位过多
**症状**：数值输出显示8+位小数
**解决**：实现统一的格式化函数并应用于所有显示

### 问题5：数据类属性名错误
**症状**：使用错误的属性名如`repayment_years`而非`repayment_period`
**解决**：检查dataclass定义并使用准确的属性名

## 使用方法

### 1. 加载Skill

将 `financial-analysis-webapp.zip` 解压到合适的目录，或在支持的IDE中加载。

### 2. 阅读SKILL.md

首先阅读 `SKILL.md` 文件以了解：
- 完整的开发工作流程
- 各个组件的实现模式
- 数据处理和展示的最佳实践

### 3. 查看参考文档

根据需要查阅参考文档：

- **chinese-financial-standards.md**: 理解财务评价标准和计算公式
- **excel-patterns.md**: 学习Excel数据处理技巧
- **streamlit-best-practices.md**: 掌握UI/UX设计原则

### 4. 使用模板生成器

使用项目模板生成器快速启动新项目：

```bash
python scripts/template_generator.py MyFinancialProject
```

这会创建包含以下内容的项目框架：
- app.py（主应用）
- config.py（配置文件）
- requirements.txt（依赖）
- README.md（项目说明）
- .gitignore

### 5. 遵循标准工作流程

按照SKILL.md中定义的工作流程：
1. Excel数据加载
2. 动态年份生成
3. 数据模型设计
4. 计算引擎实现
5. 横向表格格式化
6. 小数精度格式化
7. Streamlit输入界面
8. 数据收集
9. 结果显示

## 最佳实践

1. **始终使用dataclasses** - 提供类型安全和清晰的文档
2. **格式化所有数值输出** - 保持一致性（2位小数）
3. **横向显示表格** - 年份作为列，提高可读性
4. **使用expanders** - 组织复杂的输入表单
5. **初始化所有年份列** - 避免长度不匹配
6. **一致使用session state keys** - 用于表单输入
7. **分离关注点** - 输入 → 计算 → 显示
8. **提供下载按钮** - 用于所有结果表格
9. **使用xlrd引擎** - 支持.xls文件
10. **优雅处理缺失依赖** - 在数据加载器中

## 依赖项

Skill中提到的标准依赖：

```
streamlit>=1.28.0
pandas>=2.0.0
xlrd>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
```

## 测试建议

使用以下场景测试应用：

1. **默认值** - 确保计算在默认输入下正常工作
2. **边界情况** - 零值、负值、最大值
3. **年份转换** - 建设期到运营期的过渡
4. **完整工作流** - 从数据输入到计算到显示
5. **下载功能** - 验证CSV下载包含格式化数据

## 技术特点

### 数据处理
- 支持Excel .xls 和 .xlsx 格式
- 处理合并单元格
- 清理和验证数据
- 横向数据组织

### 计算引擎
- 模块化计算器设计
- 统一接口
- 完整的财务指标（NPV, IRR, 投资回收期）
- 折旧摊销计算（直线法）
- 借款还本付息计算

### 用户界面
- 响应式布局
- 模块化输入表单
- 自动格式化输出
- 即时计算反馈
- 多格式下载支持

## 贡献者

本Skill基于JZGCCW财务分析系统的实际开发经验创建，该系统实现了完整的中国建设项目经济评价功能。

## 许可

此Skill作为知识资源提供，旨在帮助开发者更高效地构建财务分析应用。

## 更新日志

### v1.0.0 (2026-01-19)
- 初始版本
- 完整的20种财务表格支持
- 横向展示和2位小数格式化
- Excel数据处理最佳实践
- Streamlit UI/UX指南
- 中国财务评价标准参考
- 项目模板生成器脚本
