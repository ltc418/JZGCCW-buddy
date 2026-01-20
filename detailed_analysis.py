import pandas as pd

# 读取所有工作表，只读取前100行以了解结构
xl = pd.ExcelFile('JZGCCW01.xls', engine='xlrd')
sheet_names = xl.sheet_names

output = []

for sheet_name in sheet_names:
    print(f"\nProcessing sheet: {sheet_name}")
    df = pd.read_excel(xl, sheet_name=sheet_name, nrows=100)
    output.append(f"\n{'='*80}")
    output.append(f"Sheet: {sheet_name}")
    output.append(f"{'='*80}")
    output.append(f"Shape: {df.shape}")
    output.append(f"\nColumns ({len(df.columns)}):")
    for i, col in enumerate(df.columns):
        output.append(f"  {i}: {col}")
    output.append(f"\nFirst 10 rows:")
    for idx, row in df.head(10).iterrows():
        output.append(f"Row {idx}: {dict(row)}")

# 保存到文件
with open('detailed_analysis.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Analysis saved to detailed_analysis.txt")
