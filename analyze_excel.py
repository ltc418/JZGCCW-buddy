"""
分析 Excel 文件，提取关键数据用于验证程序
"""
import pandas as pd
import sys

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def analyze_input_sheet():
    """分析输入参数表"""
    print("=" * 100)
    print("【1. 建筑工程财务模型参数】- 输入参数表")
    print("=" * 100)

    df = pd.read_excel('JZGCCW01.xls', sheet_name='1 建筑工程财务模型参数', header=None)
    print(f"\n表格维度: {df.shape[0]} 行 x {df.shape[1]} 列\n")

    # 1. 基础信息
    print(">>> 基础信息 (Row 1-8)")
    print("-" * 100)
    for i in range(8):
        row_data = []
        for j in range(min(10, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                row_data.append(f"Col{j+1}: {val}")
        if row_data:
            print(f"Row {i+1:2d}: {' | '.join(row_data)}")

    # 2. 项目投资估算
    print("\n>>> 项目投资估算 (Row 9-31)")
    print("-" * 100)
    for i in range(8, 32):
        row_data = []
        for j in range(min(8, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                row_data.append(f"Col{j+1}: {val}")
        if row_data:
            print(f"Row {i+1:2d}: {' | '.join(row_data)}")

    # 3. 资产形成
    print("\n>>> 资产形成计算 (Row 32-45)")
    print("-" * 100)
    for i in range(31, 46):
        row_data = []
        for j in range(min(10, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                row_data.append(f"Col{j+1}: {val}")
        if row_data:
            print(f"Row {i+1:2d}: {' | '.join(row_data)}")

    # 4. 资产销售计划
    print("\n>>> 资产销售计划 (Row 46-56)")
    print("-" * 100)
    for i in range(45, 57):
        row_data = []
        for j in range(min(12, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                row_data.append(f"Col{j+1}: {val}")
        if row_data:
            print(f"Row {i+1:2d}: {' | '.join(row_data)}")


def analyze_depreciation_table():
    """分析折旧表"""
    print("\n" + "=" * 100)
    print("【5-4折旧】- 固定资产折旧费估算表")
    print("=" * 100)

    df = pd.read_excel('JZGCCW01.xls', sheet_name='5-4折旧', header=None)
    print(f"\n表格维度: {df.shape[0]} 行 x {df.shape[1]} 列\n")

    print("前30行数据:")
    print("-" * 100)
    for i in range(min(30, len(df))):
        row_data = []
        for j in range(min(10, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                val_str = str(val)[:20]
                row_data.append(f"Col{j+1}: {val_str}")
        if row_data:
            print(f"Row {i+1:2d}: {' | '.join(row_data)}")


def analyze_amortization_table():
    """分析摊销表"""
    print("\n" + "=" * 100)
    print("【5-5摊销】- 无形资产摊销估算表")
    print("=" * 100)

    df = pd.read_excel('JZGCCW01.xls', sheet_name='5-5摊销', header=None)
    print(f"\n表格维度: {df.shape[0]} 行 x {df.shape[1]} 列\n")

    print("前30行数据:")
    print("-" * 100)
    for i in range(min(30, len(df))):
        row_data = []
        for j in range(min(10, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                val_str = str(val)[:20]
                row_data.append(f"Col{j+1}: {val_str}")
        if row_data:
            print(f"Row {i+1:2d}: {' | '.join(row_data)}")


def analyze_summary():
    """分析财务汇总表"""
    print("\n" + "=" * 100)
    print("【财务分析结果汇总】")
    print("=" * 100)

    df = pd.read_excel('JZGCCW01.xls', sheet_name='财务分析结果汇总', header=None)
    print(f"\n表格维度: {df.shape[0]} 行 x {df.shape[1]} 列\n")

    print("全部数据:")
    print("-" * 100)
    for i in range(len(df)):
        row_data = []
        for j in range(min(6, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                val_str = str(val)[:30]
                row_data.append(f"Col{j+1}: {val_str}")
        if row_data:
            print(f"Row {i+1:2d}: {' | '.join(row_data)}")


if __name__ == "__main__":
    analyze_input_sheet()
    analyze_depreciation_table()
    analyze_amortization_table()
    analyze_summary()
