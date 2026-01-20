"""
提取Excel输入表结构和数据
使用xlrd读取.xls文件，提取输入表的结构和数据
"""
import xlrd
import pandas as pd
import json

# 打开Excel文件
workbook = xlrd.open_workbook('JZGCCW01.xls')

# 读取输入工作表
sheet = workbook.sheet_by_name('1 建筑工程财务模型参数')

print(f"输入工作表: {sheet.name}")
print(f"行数: {sheet.nrows}")
print(f"列数: {sheet.ncols}")
print()

# 提取所有数据
input_structure = {}

for row_idx in range(sheet.nrows):
    row_data = []
    for col_idx in range(sheet.ncols):
        cell_value = sheet.cell_value(row_idx, col_idx)
        row_data.append({
            'row': row_idx,
            'col': col_idx,
            'value': cell_value,
            'type': sheet.cell_type(row_idx, col_idx)
        })
    input_structure[f"row_{row_idx}"] = row_data

# 保存到JSON文件
with open('input_structure.json', 'w', encoding='utf-8') as f:
    json.dump(input_structure, f, ensure_ascii=False, indent=2, default=str)

print("输入表结构已保存到 input_structure.json")

# 分析前260行的关键数据
print("\n=== 输入表关键数据 ===\n")

# 定义关键行范围
key_ranges = {
    "基础信息": (0, 2),
    "项目投资": (8, 28),
    "资产形成": (31, 45),
    "资产销售计划": (46, 54),
    "投融资计划": (58, 93),
    "银行借款计划": (97, 113),
    "产品销售收入": (113, 145),
    "外购材料成本": (145, 202),
    "外购燃料及动力": (202, 210),
    "工资福利成本": (210, 230),
    "修理费及其他费用": (230, 245),
    "销售费用": (245, 260)
}

for section, (start_row, end_row) in key_ranges.items():
    print(f"--- {section} (行 {start_row}-{end_row}) ---")

    for row_idx in range(start_row, min(end_row + 1, sheet.nrows)):
        # 读取前10列
        row_values = []
        for col_idx in range(min(10, sheet.ncols)):
            cell_value = sheet.cell_value(row_idx, col_idx)
            if cell_value and str(cell_value).strip():
                row_values.append(f"列{col_idx}: {cell_value}")

        if row_values:
            print(f"行{row_idx}: {' | '.join(row_values[:5])}")  # 限制显示

    print()

# 分析包含年份数据的行（第4-36列可能是年份列）
print("\n=== 年份列分析 ===")
print("查找包含年份模式的行...")

year_data = []
for row_idx in range(sheet.nrows):
    row_has_data = False
    row_values = []
    for col_idx in range(3, min(37, sheet.ncols)):  # 列3-36可能是年份
        cell_value = sheet.cell_value(row_idx, col_idx)
        if cell_value and cell_value != '':
            row_has_data = True
            row_values.append((col_idx - 2, cell_value))  # 年份从1开始

    if row_has_data and len(row_values) > 5:  # 至少有5个年份有数据
        label = sheet.cell_value(row_idx, 0) if sheet.cell_value(row_idx, 0) else f"行{row_idx}"
        year_data.append({
            'row': row_idx,
            'label': label,
            'data': row_values
        })

print(f"找到 {len(year_data)} 行包含年度数据")

for item in year_data[:5]:  # 显示前5行
    print(f"\n行{item['row']} - {item['label']}")
    for year, value in item['data'][:5]:
        print(f"  第{year}年: {value}")

# 保存年度数据到JSON
with open('year_data.json', 'w', encoding='utf-8') as f:
    json.dump(year_data, f, ensure_ascii=False, indent=2, default=str)

print("\n年度数据已保存到 year_data.json")
print("\n分析完成!")
