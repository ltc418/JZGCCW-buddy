import pandas as pd

print("=" * 140)
print("关键计算表逻辑分析")
print("=" * 140)

# 分析几个关键计算表的结构
key_sheets = {
    "5总成本": "总成本费用估算表",
    "7利润": "利润与利润分配表",
    "10项目现金": "项目投资现金流量表",
    "财务分析结果汇总": "财务分析结果汇总"
}

for sheet_name, desc in key_sheets.items():
    print(f"\n{'='*140}")
    print(f"表: {sheet_name} - {desc}")
    print(f"{'='*140}")

    df = pd.read_excel('JZGCCW01.xls', sheet_name=sheet_name, engine='xlrd', header=None)
    print(f"尺寸: {df.shape[0]}行 x {df.shape[1]}列\n")

    # 显示前20行
    print("前20行内容:")
    for i in range(min(20, df.shape[0])):
        row_data = []
        for j, val in enumerate(df.iloc[i]):
            if pd.notna(val):
                val_str = str(val)[:50]
                row_data.append(f"Col{j}:{val_str}")
        if row_data:
            print(f"Row {i}: {' | '.join(row_data)}")

print("\n" + "="*140)
print("分析完成")
print("="*140)
