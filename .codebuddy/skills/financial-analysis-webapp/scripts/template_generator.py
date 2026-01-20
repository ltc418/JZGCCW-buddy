#!/usr/bin/env python3
"""
Financial Analysis WebApp Template Generator
Generates boilerplate code for a new financial analysis Streamlit application
"""
import os
from pathlib import Path

def generate_project_template(project_name, output_dir):
    """
    Generate a complete project template for financial analysis webapp

    Args:
        project_name: Name of the project
        output_dir: Output directory path
    """
    # Create directory structure
    project_dir = Path(output_dir) / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create directories
    (project_dir / "__pycache__").mkdir(exist_ok=True)
    (project_dir / ".codebuddy" / "skills").mkdir(parents=True, exist_ok=True)

    # Generate main app file
    app_content = f'''"""
{project_name} - 财务分析系统
基于Streamlit的Web应用
"""
import streamlit as st
import pandas as pd
from data_models import InputData
from year_generator import YearGenerator
from calculation_engine import CalculationEngine
from input_collector import collect_input_data
import config


def format_dataframe(df: pd.DataFrame, decimals: int = 2) -> pd.DataFrame:
    """
    格式化DataFrame中的数值列为指定小数位数

    Args:
        df: 原始DataFrame
        decimals: 小数位数，默认2位

    Returns:
        格式化后的DataFrame
    """
    df_formatted = df.copy()
    for col in df_formatted.columns:
        if col == "项目":
            continue
        if pd.api.types.is_numeric_dtype(df_formatted[col]):
            df_formatted[col] = df_formatted[col].astype(float).round(decimals)
    return df_formatted


# 页面配置
st.set_page_config(**config.PAGE_CONFIG)

# 初始化session state
if 'construction_period' not in st.session_state:
    st.session_state.construction_period = config.DEFAULT_CONSTRUCTION_PERIOD
if 'operation_period' not in st.session_state:
    st.session_state.operation_period = config.DEFAULT_OPERATION_PERIOD
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# 标题
st.title(f"🏗️ {project_name}")
st.markdown("基于《建设项目经济评价方法与参数(第三版)》编制的财务分析计算系统")

# ===== 全局设置 =====
st.markdown("## ⚙️ 全局设置")

col1, col2, col3 = st.columns(3)

with col1:
    new_construction = st.number_input(
        "建设期（年）",
        min_value=1,
        max_value=10,
        value=st.session_state.construction_period,
        key="cp_input"
    )

with col2:
    new_operation = st.number_input(
        "运营期（年）",
        min_value=1,
        max_value=30,
        value=st.session_state.operation_period,
        key="op_input"
    )

with col3:
    total_period = new_construction + new_operation
    st.metric("计算期", f"{{total_period}}年")

# 更新session state
if new_construction != st.session_state.construction_period or new_operation != st.session_state.operation_period:
    st.session_state.construction_period = new_construction
    st.session_state.operation_period = new_operation
    st.session_state.calculated = False

st.divider()

# ===== 侧边栏输入 =====
with st.sidebar:
    st.header("📝 数据输入")

    # TODO: 添加输入表单
    st.info("请在这里添加您的输入表单")

# ===== 执行计算按钮 =====
st.divider()

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 执行计算", type="primary", use_container_width=True):
        with st.spinner("正在计算中..."):
            try:
                # 收集输入数据
                input_data = collect_input_data(new_construction, new_operation)

                # 创建计算引擎
                year_generator = YearGenerator(new_construction, new_operation)
                calc_engine = CalculationEngine(year_generator, input_data)

                # 执行计算
                results = calc_engine.run_all_calculations()

                # 保存结果到session state
                st.session_state.calculated = True
                st.session_state.calculation_results = results

                st.success("✅ 计算完成！")
                st.info("📊 请在下方的结果区域查看计算表格")

            except Exception as e:
                st.error(f"❌ 计算过程中发生错误: {{str(e)}}")
                import traceback
                st.code(traceback.format_exc())

# ===== 结果展示 =====
if st.session_state.get('calculated', False):
    st.divider()
    st.header("📊 计算结果")

    if 'calculation_results' in st.session_state and st.session_state.calculation_results:
        results = st.session_state.calculation_results

        # 显示所有计算结果表格
        for sheet_name in results.keys():
            st.markdown(f"#### {{config.SHEET_MAPPING.get(sheet_name, sheet_name)}}")

            # 显示计算结果表格（格式化为2位小数）
            df = results[sheet_name]
            df_display = format_dataframe(df, decimals=2)
            st.dataframe(
                df_display,
                use_container_width=True,
                height=min(400, 100 + len(df) * 30)
            )

            # 下载按钮
            csv = df_display.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label=f"下载 {{config.SHEET_MAPPING.get(sheet_name, sheet_name)}}",
                data=csv,
                file_name=f"{{sheet_name}}_result.csv",
                mime="text/csv"
            )

            st.divider()

# ===== 页脚 =====
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
        {project_name} | 基于《建设项目经济评价方法与参数(第三版)》
    </div>
    """,
    unsafe_allow_html=True
)
'''

    with open(project_dir / "app.py", "w", encoding="utf-8") as f:
        f.write(app_content)

    # Generate config.py
    config_content = '''"""
配置文件
"""
import streamlit as st

# 页面配置
PAGE_CONFIG = {
    "page_title": "Financial Analysis System",
    "page_icon": "🏗️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 默认参数
DEFAULT_CONSTRUCTION_PERIOD = 3  # 建设期（年）
DEFAULT_OPERATION_PERIOD = 17   # 运营期（年）

# 工作表名称映射
SHEET_MAPPING = {
    "1建设投资": "建设投资估算表",
    "2流动资金": "流动资金估算表",
    "3投资计划": "项目总投资使用计划与资金筹措表",
    "5-4折旧": "固定资产折旧费估算表",
    "5-5摊销": "无形资产摊销估算表",
    "5总成本": "总成本费用估算表",
    "6收入 ": "营业收入、营业税金及附加和增值税估算表",
    "7利润": "利润与利润分配表",
    "8财务现金": "项目财务现金流量表",
    "10项目现金": "项目投资现金流量表",
    "11资本金现金 ": "项目资本金现金流量表",
    "财务分析结果汇总": "财务分析结果汇总",
}
'''

    with open(project_dir / "config.py", "w", encoding="utf-8") as f:
        f.write(config_content)

    # Generate requirements.txt
    requirements_content = '''streamlit>=1.28.0
pandas>=2.0.0
xlrd>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
'''

    with open(project_dir / "requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)

    # Generate README.md
    readme_content = f'''# {project_name}

## 项目说明

基于Streamlit的财务分析Web应用系统，用于建设项目的经济评价。

## 功能特点

- 动态年份管理（建设期 + 运营期）
- 完整的财务计算引擎
- 横向展示财务表格
- 2位小数格式化
- CSV文件下载

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
streamlit run app.py
```

## 开发

项目基于《建设项目经济评价方法与参数(第三版)》编制。
'''

    with open(project_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Generate .gitignore
    gitignore_content = '''__pycache__/
*.pyc
.DS_Store
*.py[cod]
*$py.class
.pytest_cache/
.coverage
dist/
build/
*.egg-info/
'''

    with open(project_dir / ".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)

    print(f"✅ 项目模板已生成到: {project_dir}")
    print(f"\n下一步:")
    print(f"1. cd {project_dir}")
    print(f"2. 根据需求修改 app.py 和其他文件")
    print(f"3. streamlit run app.py")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate financial analysis webapp template")
    parser.add_argument("project_name", help="项目名称")
    parser.add_argument("--output", "-o", default=".", help="输出目录")

    args = parser.parse_args()

    generate_project_template(args.project_name, args.output)
