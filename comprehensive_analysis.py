import pandas as pd

# 读取参数工作表,提取所有黄色格子的输入字段
df_params = pd.read_excel('JZGCCW01.xls', sheet_name='1 建筑工程财务模型参数', engine='xlrd', header=None)

print("=" * 140)
print("JZGCCW01.xls 财务分析模型综合分析")
print("=" * 140)

# 检查所有工作表
xl = pd.ExcelFile('JZGCCW01.xls', engine='xlrd')
print(f"\n1. 工作表列表 (共{len(xl.sheet_names)}个表):")
for i, sheet_name in enumerate(xl.sheet_names, 1):
    df = pd.read_excel(xl, sheet_name=sheet_name, nrows=5)
    print(f"   {i}. {sheet_name} - {df.shape[0]}行 x {df.shape[1]}列")

# 分析输入模块
print("\n2. 输入模块结构分析 ('1 建筑工程财务模型参数'):")
print("-" * 140)

input_modules = {
    "基础信息": [1, 2],  # 项目名称,建设期,运营期
    "项目投资": [9, 28],  # 工程费,工程建设其他费,预备费,建设期利息等
    "资产形成": [32, 45],  # 各类资产形成计算,折旧摊销年限,残值率
    "资产销售计划": [47, 54],  # 固定资产销售计划
    "投融资计划": [59, 93],  # 项目投融资计划
    "银行借款计划": [98, 113],  # 银行借款计划表
    "产品销售收入": [114, 145],  # 产品销售收入
    "外购材料成本": [146, 202],  # 外购材料成本
    "外购燃料及动力": [203, 210],  # 外购燃料及动力
    "工资福利成本": [211, 230],  # 工资福利成本
    "修理费及其他费用": [231, 245],  # 修理费及其他费用
    "销售费用": [246, 260],  # 销售费用
}

for module_name, (start_row, end_row) in input_modules.items():
    print(f"\n   模块 {len(input_modules)}: {module_name} (行 {start_row}-{end_row})")
    # 显示该模块的第一行
    row = df_params.iloc[start_row - 1]
    non_null = [f"Col{j}:{str(v)[:40]}" for j, v in enumerate(row) if pd.notna(v)]
    if non_null:
        print(f"     第一行: {' | '.join(non_null)}")

print("\n3. 计算工作表分析:")
print("-" * 140)

calc_sheets = [
    ("1建设投资", "建设投资估算表"),
    ("2流动资金", "流动资金估算表"),
    ("3投资计划", "项目总投资使用计划与资金筹措表"),
    ("4还本付息", "借款还本付息计划表"),
    ("5-1材料", "外购原材料费估算表"),
    ("5-2燃料", "外购燃料及动力费估算表"),
    ("5-3工资", "工资及福利费估算表"),
    ("5-4折旧", "固定资产折旧费估算表"),
    ("5-5摊销", "无形资产摊销估算表"),
    ("5总成本", "总成本费用估算表"),
    ("6收入 ", "营业收入、营业税金及附加和增值税估算表"),  # 注意空格
    ("7利润", "利润与利润分配表"),
    ("8财务现金", "项目财务现金流量表"),
    ("9资产负债", "资产负债表"),
    ("10项目现金", "项目投资现金流量表"),
    ("11资本金现金 ", "项目资本金现金流量表"),  # 注意空格
    ("12各方现金", "投资各方现金流量表"),
    ("财务分析结果汇总", "财务分析结果汇总"),
    ("土地增值税计算", "土地增值税计算"),
    ("房产销售及土增", "房产销售及土增"),
]

for i, (sheet_name, description) in enumerate(calc_sheets, 1):
    df = pd.read_excel(xl, sheet_name=sheet_name)
    print(f"   {i}. {sheet_name:<20} - {description:<40} ({df.shape[0]}行 x {df.shape[1]}列)")

print("\n4. 关键计算逻辑推测:")
print("-" * 140)
print("   建设期(3年) + 运营期(17年) = 计算期(20年)")
print("   年份横向布置:建设期1-3,运营期4-20")
print("   主要计算流:")
print("   项目投资估算 -> 资金筹措计划 -> 投资计划")
print("   -> 折旧摊销计算 -> 总成本计算")
print("   -> 收入计算 -> 利润计算")
print("   -> 现金流量计算 -> 财务指标分析")

print("\n5. 需要注意的特殊要求:")
print("-" * 140)
print("   - 建设期和运营期必须可调整")
print("   - 年份需要根据建设期+运营期动态生成")
print("   - 所有计算关系必须与原表格一致")
print("   - 需要用原表格数据验证计算结果")
print("   - 收入、成本等参数需要按年横向输入")

print("\n分析完成!")
print("=" * 140)
