import pandas as pd
import json

# 读取参数工作表
df = pd.read_excel('JZGCCW01.xls', sheet_name='1 建筑工程财务模型参数', engine='xlrd', header=None)

print("工作表尺寸:", df.shape)
print("\n前80行内容:")
print("=" * 100)

for i in range(80):
    row_data = []
    for j, val in enumerate(df.iloc[i]):
        if pd.notna(val):
            row_data.append(f"Col{j}:{val}")
    if row_data:
        print(f"Row {i}: {' | '.join(str(x)[:50] for x in row_data)}")

# 保存完整数据供参考
df.to_excel('params_sheet_raw.xlsx', index=False)
print("\n原始数据已保存到 params_sheet_raw.xlsx")
