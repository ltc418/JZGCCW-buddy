import pandas as pd
import openpyxl

# 使用openpyxl读取以保持格式信息
wb = openpyxl.load_workbook('JZGCCW01.xls', read_only=False, data_only=False)
ws = wb['1 建筑工程财务模型参数']

print("工作表: 1 建筑工程财务模型参数")
print("=" * 80)

# 遍历前50行，显示单元格内容和背景色
for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=50), 1):
    row_data = []
    for cell in row:
        if cell.value is not None:
            bg_color = cell.fill.start_color.rgb if cell.fill and cell.fill.start_color else None
            if bg_color:
                row_data.append(f"{cell.value}[bg:{bg_color}]")
            else:
                row_data.append(str(cell.value))
    if row_data:
        print(f"Row {row_idx}: {' | '.join(row_data[:20])}")  # 限制显示前20列
        if row_idx >= 50:  # 只显示前50行
            break

wb.close()
