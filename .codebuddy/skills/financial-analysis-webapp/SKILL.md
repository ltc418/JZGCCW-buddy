---
name: financial-analysis-webapp
description: This skill provides specialized knowledge and workflows for building Streamlit-based financial analysis web applications that process Excel files, generate multi-year financial projections, and display results in tabular format. Use this skill when building financial analysis systems with year-by-year calculations, investment/depreciation/profit tables, and web-based input interfaces.
---

# Financial Analysis WebApp Builder Skill

This skill provides specialized workflows for building Streamlit-based financial analysis web applications, particularly for construction project economic evaluation based on Chinese national standards (建设项目经济评价方法与参数).

## When to Use This Skill

Use this skill when:
- Building financial analysis applications that process Excel templates
- Creating multi-year financial projection systems (construction period + operation period)
- Implementing year-by-year calculation engines for investment, depreciation, costs, profits, cash flows
- Building web-based input interfaces for complex financial models
- Generating standardized financial tables (investment estimates, depreciation schedules, profit statements, cash flow statements, balance sheets)
- Displaying financial results with horizontal year-wise formatting
- Formatting all numeric outputs to consistent decimal precision

## Core Architecture Patterns

### Project Structure

Organize financial analysis webapps with this structure:

```
project/
├── app_v2.py              # Main Streamlit application
├── data_models.py          # Dataclasses for type-safe data structures
├── calculation_engine.py    # Unified calculation interface
├── calculations.py         # Individual calculation modules
├── year_generator.py       # Dynamic year management
├── data_loader.py          # Excel file reading with xlrd support
├── input_collector.py      # Gather form data into InputData objects
├── config.py              # Configuration constants and mappings
└── requirements.txt        # Dependencies
```

### Key Design Principles

1. **Separation of Concerns**: Input collection → Calculation → Display
2. **Type Safety**: Use dataclasses for all data structures
3. **Horizontal Display**: Format year-by-year data horizontally (years as columns)
4. **Consistent Precision**: All numeric outputs formatted to 2 decimal places
5. **Excel Compatibility**: Support .xls format using xlrd engine

## Standard Workflows

### 1. Excel Data Loading

To load Excel financial templates:

```python
from data_loader import DataLoader

loader = DataLoader()
loader.load_all_sheets()
df = loader.get_sheet("SheetName")
```

**Key points:**
- Use xlrd for .xls file support
- Handle missing dependencies gracefully
- Store sheet name mappings in config

### 2. Dynamic Year Generation

Implement year management with construction period and operation period:

```python
from year_generator import YearGenerator

yg = YearGenerator(construction_period=3, operation_period=17)
years = yg.generate_year_names()  # Returns: ["建设期第1年", ..., "运营期第1年", ...]
```

**Required methods:**
- `generate_year_names()`: Get all year names
- `is_construction_year(year_num)`: Check if year is in construction period
- `is_operation_year(year_num)`: Check if year is in operation period
- `get_year_index(year)`: Get sequential year number

### 3. Data Model Design

Use dataclasses for all financial data structures:

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ProjectInvestment:
    building_cost: float = 0.0
    equipment_cost: float = 0.0
    # ... other fields

@dataclass
class InputData:
    basic_info: BasicInfo = field(default_factory=BasicInfo)
    project_investment: ProjectInvestment = field(default_factory=ProjectInvestment)
    # ... other data modules
```

**Benefits:**
- Type safety and IDE autocomplete
- Default values for all fields
- Easy initialization
- Clear data structure documentation

### 4. Calculation Engine Architecture

Implement modular calculators with a unified interface:

```python
class InvestmentCalculator:
    """Handles investment-related calculations"""
    def calculate_total_investment(self) -> Dict[str, float]:
        # Calculate engineering fees, other fees, reserve fees
        pass

class DepreciationCalculator:
    """Handles depreciation and amortization"""
    def get_yearly_depreciation(self) -> Dict[str, float]:
        # Calculate annual depreciation
        pass

class CostCalculator:
    """Handles cost calculations"""
    def get_yearly_costs(self, depreciation, amortization) -> Dict[str, Dict]:
        # Calculate material costs, fuel costs, labor costs
        pass

class ProfitCalculator:
    """Handles profit and loss calculations"""
    def calculate_profit(self) -> Dict[str, float]:
        # Calculate gross profit, income tax, net profit
        pass

class CashFlowCalculator:
    """Handles cash flow analysis"""
    def calculate_npv(self, cashflows, discount_rate) -> float:
        # Net Present Value calculation
        pass
    def calculate_irr(self, cashflows) -> float:
        # Internal Rate of Return calculation
        pass
```

**Unified calculation engine:**

```python
class CalculationEngine:
    def __init__(self, year_generator, input_data):
        self.yg = year_generator
        self.input = input_data
        # Initialize all calculators
        self.investment_calc = InvestmentCalculator(year_generator, input_data)
        self.depreciation_calc = DepreciationCalculator(year_generator, input_data)
        self.cost_calc = CostCalculator(year_generator, input_data)
        self.profit_calc = ProfitCalculator(year_generator, input_data)
        self.cashflow_calc = CashFlowCalculator(year_generator, input_data)

    def run_all_calculations(self) -> Dict[str, pd.DataFrame]:
        results = {}
        # Generate all financial tables
        results["1建设投资"] = self._create_investment_table()
        results["2流动资金"] = self._create_working_capital_table()
        results["5-4折旧"] = self._create_depreciation_table()
        # ... generate all 20 tables
        return results
```

### 5. Horizontal Table Formatting

Format all year-by-year tables horizontally (years as columns):

```python
def _create_depreciation_table(self) -> pd.DataFrame:
    years = self.yg.generate_year_names()

    # Build data dictionary with project names as rows
    data = {
        "项目": ["固定资产原值", "年度折旧额", "累计折旧", "净值"]
    }

    # Add yearly data as columns
    for year in years:
        data[year] = [
            fixed_asset_value,
            annual_depreciation,
            cumulative_depreciation,
            net_value
        ]

    return pd.DataFrame(data)
```

**Key pattern:**
- First column: "项目" (Project/Item names)
- Subsequent columns: Year names (建设期第1年, 运营期第1年, etc.)
- Each row: One metric/line item
- Avoid using iloc[row, col] indexing

### 6. Decimal Precision Formatting

Implement consistent 2-decimal formatting for all displays:

```python
def format_dataframe(df: pd.DataFrame, decimals: int = 2) -> pd.DataFrame:
    df_formatted = df.copy()
    for col in df_formatted.columns:
        if col == "项目":
            continue  # Skip non-numeric column
        if pd.api.types.is_numeric_dtype(df_formatted[col]):
            df_formatted[col] = df_formatted[col].astype(float).round(decimals)
    return df_formatted
```

**Apply formatting to:**
- All displayed DataFrames
- All downloadable CSV files
- Input form values (use `format="%.2f"` in `st.number_input`)

### 7. Streamlit Input Interface

Design modular input forms with expandable sections:

```python
# Global settings
st.markdown("## ⚙️ 全局设置")
construction_period = st.number_input("建设期（年）", value=3)
operation_period = st.number_input("运营期（年）", value=17)

# Input modules with expander
with st.sidebar:
    with st.expander("1️⃣ 基础信息"):
        project_name = st.text_input("项目名称", key="project_name")

    with st.expander("2️⃣ 项目投资"):
        building_cost = st.number_input(
            "建筑工程费",
            value=67062.86,
            format="%.2f",
            key="building_cost"
        )

    # Dynamic year-based inputs
    year_generator = YearGenerator(construction_period, operation_period)
    years = year_generator.generate_year_names()

    for year in years:
        year_num = year_generator.get_year_index(year)
        if year_generator.is_operation_year(year_num):
            sales_revenue = st.number_input(
                year,
                value=10000.0,
                format="%.2f",
                key=f"sales_{year}"
            )
```

**Key patterns:**
- Use session state keys for all inputs
- Apply `format="%.2f"` to all numeric inputs
- Use expanders to organize complex input forms
- Dynamically generate year-based inputs
- Auto-fill construction period data with 0.0

### 8. Data Collection

Gather form data from session state into InputData objects:

```python
def collect_input_data(construction_period: int, operation_period: int) -> InputData:
    input_data = InputData()

    # Collect from session state
    input_data.basic_info.project_name = st.session_state.get("project_name", "")
    input_data.project_investment.building_cost = st.session_state.get("building_cost", 0.0)

    # Handle year-based data
    yg = YearGenerator(construction_period, operation_period)
    years = yg.generate_year_names()

    for year in years:
        year_num = yg.get_year_index(year)
        if yg.is_operation_year(year_num):
            key = f"sales_{year}"
            input_data.sales_revenue.annual_revenue[year] = st.session_state.get(key, 10000.0)
        else:
            input_data.sales_revenue.annual_revenue[year] = 0.0  # Construction period

    return input_data
```

### 9. Result Display

Display all results automatically without user selection:

```python
if st.session_state.get('calculated', False):
    st.header("📊 计算结果")
    results = st.session_state.calculation_results

    for sheet_name in results.keys():
        st.markdown(f"#### {SHEET_MAPPING.get(sheet_name, sheet_name)}")

        # Format and display
        df = results[sheet_name]
        df_display = format_dataframe(df, decimals=2)
        st.dataframe(df_display, use_container_width=True)

        # Download button
        csv = df_display.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label=f"下载 {sheet_name}",
            data=csv,
            file_name=f"{sheet_name}_result.csv"
        )

        st.divider()
```

## Standard Financial Tables

Implement these 20 standard financial tables:

1. **1建设投资** - Construction investment estimate
2. **2流动资金** - Working capital estimate
3. **3投资计划** - Investment use plan and funding
4. **4还本付息** - Loan repayment schedule
5. **5-1材料** - Raw material cost estimate
6. **5-2燃料** - Fuel and power cost estimate
7. **5-3工资** - Wages and welfare cost estimate
8. **5-4折旧** - Fixed asset depreciation schedule
9. **5-5摊销** - Intangible asset amortization schedule
10. **5总成本** - Total cost estimate
11. **6收入** - Operating revenue, tax and VAT estimate
12. **7利润** - Profit and profit distribution statement
13. **8财务现金** - Project financial cash flow statement
14. **9资产负债** - Balance sheet
15. **10项目现金** - Project investment cash flow statement
16. **11资本金现金** - Project capital cash flow statement
17. **12各方现金** - Investor cash flow statement
18. **财务分析结果汇总** - Financial indicators summary
19. **土地增值税计算** - Land value-added tax calculation
20. **房产销售及土增** - Property sales and land tax

## Calculation Patterns

### Investment Calculation

Calculate total investment including engineering fees, other fees, reserve fees:

```python
total_engineering = (
    building_cost + building_equipment_cost +
    building_installation_cost + production_equipment_cost +
    production_installation_cost
)

total_other = (
    management_fee + tech_service_fee + supporting_fee +
    land_use_fee + patent_fee + preparation_fee
)

basic_reserve = total_engineering * basic_reserve_rate
price_reserve = (total_engineering + total_other) * price_reserve_rate

total_investment = total_engineering + total_other + basic_reserve + price_reserve
```

### Depreciation Calculation

Calculate annual depreciation using straight-line method:

```python
def get_yearly_depreciation(self):
    years = self.yg.generate_year_names()
    depreciation_by_year = {}

    fixed_asset = self.input.asset_formation.building_asset + \
                  self.input.asset_formation.equipment_asset
    salvage_value = fixed_asset * (self.input.asset_formation.salvage_rate / 100)
    depreciable_value = fixed_asset - salvage_value
    annual_depreciation = depreciable_value / \
                        self.input.asset_formation.depreciation_years

    for year in years:
        year_num = self.yg.get_year_index(year)
        if self.yg.is_operation_year(year_num):
            depreciation_by_year[year] = annual_depreciation
        else:
            depreciation_by_year[year] = 0.0

    return depreciation_by_year
```

### NPV and IRR Calculation

Implement financial indicator calculations:

```python
def calculate_npv(self, cashflows, discount_rate):
    npv = 0.0
    for i, cf in enumerate(cashflows):
        npv += cf / ((1 + discount_rate) ** i)
    return npv

def calculate_irr(self, cashflows):
    # Use numpy's financial functions or implement binary search
    import numpy_financial as nf
    return nf.irr(cashflows)
```

### Cash Flow Statement

Construct cash flow tables:

```python
def _create_finance_cashflow_table(self):
    years = self.yg.generate_year_names()
    data = {"项目": ["现金流入", "现金流出", "净现金流", "累计净现金流"]}

    cumulative = 0.0
    for year in years:
        year_num = self.yg.get_year_index(year)

        if self.yg.is_construction_year(year_num):
            inflow = 0.0
            outflow = sum(investment_by_year[year].values())
        else:
            inflow = self.input.sales_revenue.annual_revenue.get(year, 0.0)
            outflow = sum(costs_by_year[year].values()) * 0.8

        net_cf = inflow - outflow
        cumulative += net_cf

        data[year] = [inflow, outflow, net_cf, cumulative]

    return pd.DataFrame(data)
```

## Common Issues and Solutions

### Issue 1: DataFrame Column Length Mismatch

**Problem**: Creating DataFrame where some columns have different lengths.

**Solution**: Initialize all year columns before populating:

```python
# Wrong approach:
data = {"项目": items}
for year in years:
    if condition:
        data[year] = [...]
    # Missing else clause causes length mismatch

# Correct approach:
data = {"项目": items}
for year in years:
    data[year] = []  # Initialize first
    if condition:
        data[year] = [...]
    else:
        data[year] = [0.0] * len(items)
```

### Issue 2: Importing st from streamlit

**Problem**: `from streamlit import st` causes ImportError.

**Solution**: Use module import: `import streamlit as st`

### Issue 3: Wrong Attribute Names in Data Classes

**Problem**: Using incorrect attribute names like `repayment_years` instead of `repayment_period`.

**Solution**: Check dataclass definition and use exact attribute names.

### Issue 4: Excel File Format Incompatibility

**Problem**: Cannot read .xls files with pandas default engine.

**Solution**: Use xlrd engine:

```python
import xlrd
df = pd.read_excel('file.xls', sheet_name='SheetName', engine='xlrd')
```

### Issue 5: Too Many Decimal Places

**Problem**: Numeric outputs show 8+ decimal places.

**Solution**: Implement consistent formatting function applied to all displays:

```python
def format_dataframe(df, decimals=2):
    # Format all numeric columns to specified decimals
    pass
```

## Best Practices

1. **Always use dataclasses** for data structures - provides type safety and clear documentation
2. **Format all numeric outputs** to 2 decimal places for consistency
3. **Display tables horizontally** with years as columns for better readability
4. **Use expanders** to organize complex input forms
5. **Initialize all year columns** before populating to avoid length mismatches
6. **Use session state keys** consistently for form inputs
7. **Separate concerns** - Input → Calculation → Display
8. **Provide download buttons** for all result tables
9. **Use xlrd engine** for .xls file support
10. **Handle missing dependencies** gracefully in data loaders

## Dependencies

Include these in requirements.txt:

```
streamlit
pandas
xlrd
numpy
openpyxl
```

## Testing

Test the application with:

1. **Default values** - Ensure calculations work with default inputs
2. **Edge cases** - Zero values, negative values, maximum values
3. **Year transitions** - Construction period to operation period handoff
4. **Complete workflow** - From data entry to calculation to display
5. **Download functionality** - Verify CSV downloads contain formatted data

## Quick Start Template

Use this template to start a new financial analysis project:

```python
"""
Financial Analysis WebApp
"""
import streamlit as st
import pandas as pd
from data_models import InputData
from year_generator import YearGenerator
from calculation_engine import CalculationEngine
from input_collector import collect_input_data

def format_dataframe(df: pd.DataFrame, decimals: int = 2) -> pd.DataFrame:
    # Format all numeric columns
    df_formatted = df.copy()
    for col in df_formatted.columns:
        if col == "项目":
            continue
        if pd.api.types.is_numeric_dtype(df_formatted[col]):
            df_formatted[col] = df_formatted[col].astype(float).round(decimals)
    return df_formatted

# Page setup
st.set_page_config(page_title="Financial Analysis", layout="wide")

# Input section
with st.sidebar:
    st.header("📝 Data Input")
    # ... add input forms

# Calculation trigger
if st.button("🚀 Calculate"):
    with st.spinner("Calculating..."):
        input_data = collect_input_data(construction_period, operation_period)
        yg = YearGenerator(construction_period, operation_period)
        calc = CalculationEngine(yg, input_data)
        results = calc.run_all_calculations()
        st.session_state.calculation_results = results

# Display results
if 'calculation_results' in st.session_state:
    results = st.session_state.calculation_results
    for sheet_name, df in results.items():
        st.markdown(f"#### {sheet_name}")
        st.dataframe(format_dataframe(df))
```

## References

- `references/chinese-financial-standards.md` - Chinese national financial evaluation standards
- `references/excel-patterns.md` - Common Excel financial template patterns
- `references/streamlit-best-practices.md` - Streamlit UI best practices for financial apps
