import pandas as pd

# 读取参数工作表
df = pd.read_excel('JZGCCW01.xls', sheet_name='1 建筑工程财务模型参数', engine='xlrd', header=None)

print("查看第80-150行内容:")
print("=" * 120)

for i in range(80, 150):
    row_data = []
    for j, val in enumerate(df.iloc[i]):
        if pd.notna(val):
            # 限制每个单元格显示长度
            val_str = str(val)[:60]
            row_data.append(f"Col{j}:{val_str}")
    if row_data:
        print(f"Row {i}: {' | '.join(row_data)}")
