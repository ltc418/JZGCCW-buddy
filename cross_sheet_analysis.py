import pandas as pd
import json

# 读取Excel文件
xl = pd.ExcelFile('JZGCCW01.xls', engine='xlrd')

def get_sheet_summary(sheet_name):
    """获取工作表的摘要信息"""
    df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
    df = df.fillna('')

    # 获取前3行作为标题
    header = []
    for i in range(min(3, len(df))):
        row_data = {}
        for j in range(min(10, len(df.columns))):
            val = df.iloc[i, j]
            if val and str(val).strip() and str(val) != 'nan':
                row_data[f"Col{j+1}"] = str(val)[:50]
        if row_data:
            header.append(row_data)

    # 获取行标签（第1列有内容的行）
    row_labels = []
    for i in range(len(df)):
        label = str(df.iloc[i, 0]).strip()
        if label and label != 'nan' and label != '':
            row_labels.append({
                'row': i + 1,
                'label': label[:100]
            })

    return {
        'shape': df.shape,
        'header': header,
        'row_labels': row_labels[:50]  # 前50个标签
    }

# 分析关键工作表
sheets = {
    "5-4折旧": "折旧摊销计算表",
    "1建设投资": "建设投资估算表",
    "1 建筑工程财务模型参数": "参数设置表",
    "5总成本": "总成本费用表",
    "7利润": "利润表",
    "9资产负债": "资产负债表",
    "4还本付息": "还本付息计划表"
}

print("="*100)
print("工作表结构分析")
print("="*100)

analysis = {}
for sheet_name, desc in sheets.items():
    if sheet_name in xl.sheet_names:
        summary = get_sheet_summary(sheet_name)
        analysis[sheet_name] = {
            'description': desc,
            'shape': summary['shape'],
            'header': summary['header'],
            'row_labels': summary['row_labels']
        }

        print(f"\n{sheet_name} - {desc}")
        print(f"  形状: {summary['shape'][0]} 行 × {summary['shape'][1]} 列")
        print(f"  标题行: {len(summary['header'])} 行")
        print(f"  主要行标签: {len(summary['row_labels'])} 个")

        # 显示前10个行标签
        if summary['row_labels']:
            print("  前10个标签:")
            for i, row_info in enumerate(summary['row_labels'][:10]):
                print(f"    行{row_info['row']:3d}: {row_info['label']}")
    else:
        print(f"\n{sheet_name} - {desc}")
        print("  警告: 工作表不存在")

print("\n" + "="*100)
print("5-4折旧详细行结构分析")
print("="*100)

# 详细分析5-4折旧的行结构
df_54 = pd.read_excel(xl, sheet_name="5-4折旧", header=None)
df_54 = df_54.fillna('')

print(f"\n总行数: {len(df_54)}")
print(f"总列数: {len(df_54.columns)}")

# 分析每一行的结构
print("\n行结构明细:")
for i in range(len(df_54)):
    row_data = []
    has_label = False
    has_data = False

    # 检查第1列（标签）
    label = str(df_54.iloc[i, 0]).strip()
    if label and label != 'nan' and label != '':
        has_label = True
        row_data.append(f"【{label}】")

    # 检查第2-4列（数据）
    for j in range(1, min(5, len(df_54.columns))):
        val = df_54.iloc[i, j]
        if pd.notna(val) and str(val).strip() and str(val) != 'nan' and str(val) != '0':
            has_data = True
            if isinstance(val, (int, float)) and val != 0:
                row_data.append(f"{val:.2f}")
            else:
                row_data.append(str(val)[:20])

    if has_label or has_data:
        print(f"  行{i+1:3d}: {'  '.join(row_data)}")

print("\n" + "="*100)
print("资产类别分析")
print("="*100)

# 分析资产类别结构
assets = {
    "建筑物": {"rows": [5, 6, 7], "items": ["原值", "当期折旧费", "净值"]},
    "机器设备": {"rows": [9, 10, 11], "items": ["原值", "当期折旧费", "净值"]},
    "销售固定资产": {"rows": [13, 14, 15], "items": ["销售固定资产成本", "固定资产成本摊销额", "剩余待销售资产净值"]},
    "合计": {"rows": [17, 18, 19], "items": ["原值", "当期折旧、摊销", "净值"]}
}

for asset_name, asset_info in assets.items():
    print(f"\n{asset_name}:")
    for i, item_name in enumerate(asset_info["items"]):
        row_idx = asset_info["rows"][i] - 1  # 转换为0-based索引
        if row_idx < len(df_54):
            # 获取该行的关键数据（D列合计，以及运营期的前几列）
            d_val = df_54.iloc[row_idx, 3]
            if pd.isna(d_val) or d_val == '' or str(d_val).strip() == '':
                d_val = 0
            else:
                try:
                    d_val = float(d_val)
                except:
                    d_val = str(d_val)

            print(f"  {item_name}:")
            if isinstance(d_val, (int, float)):
                print(f"    合计(D列): {d_val:.2f}")
            else:
                print(f"    合计(D列): {d_val}")

            # 显示运营期前几年的数据
            op_data = []
            for j in range(7, min(12, len(df_54.columns))):  # H-L列（运营期1-5）
                val = df_54.iloc[row_idx, j]
                if pd.notna(val) and val != 0 and str(val).strip() != '':
                    col_letter = chr(65 + j) if j < 26 else chr(64 + j // 26) + chr(65 + j % 26)
                    try:
                        val_float = float(val)
                        op_data.append(f"{col_letter}列(运营期{j-6}): {val_float:.2f}")
                    except:
                        op_data.append(f"{col_letter}列(运营期{j-6}): {val}")

            if op_data:
                print(f"    运营期数据: {'  '.join(op_data[:3])}")

print("\n" + "="*100)
print("关键数据提取")
print("="*100)

# 提取关键数据
key_data = {
    "建筑物原值": df_54.iloc[4, 3],  # 行5, D列
    "建筑物折旧": df_54.iloc[5, 3],  # 行6, D列
    "销售资产成本": df_54.iloc[12, 3],  # 行13, D列
    "折旧摊销合计": df_54.iloc[17, 3],  # 行18, D列
}

print("\n5-4折旧表关键数据:")
for key, value in key_data.items():
    try:
        value_float = float(value)
        print(f"  {key}: {value_float:.2f} 万元")
    except:
        if pd.notna(value):
            print(f"  {key}: {value}")

# 保存分析结果
with open('cross_sheet_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis, f, ensure_ascii=False, indent=2)

print("\n" + "="*100)
print("分析完成！详细数据已保存到 cross_sheet_analysis.json")
print("="*100)
