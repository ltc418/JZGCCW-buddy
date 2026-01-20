import pandas as pd
import json

# 读取所有工作表
xl = pd.ExcelFile('JZGCCW01.xls', engine='xlrd')
sheet_names = xl.sheet_names

analysis = {}

for sheet_name in sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet_name)
    analysis[sheet_name] = {
        'shape': df.shape,
        'columns': list(df.columns),
        'first_rows': df.head(10).to_dict('records')
    }

# 保存分析结果
with open('excel_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis, f, ensure_ascii=False, indent=2)

print("Analysis saved to excel_analysis.json")
print(f"Total sheets: {len(sheet_names)}")
print(f"Sheet names: {sheet_names}")
