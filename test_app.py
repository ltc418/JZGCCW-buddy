"""
测试应用基本功能
"""
from data_loader import DataLoader
from utils import generate_years

# 测试数据加载
print("测试数据加载...")
loader = DataLoader()
loader.load_all_sheets()

print(f"成功加载 {len(loader.all_sheets)} 个工作表")
print("工作表名称：")
for sheet_name in loader.all_sheets.keys():
    print(f"  - {sheet_name}")

# 测试输入表
print("\n测试输入表加载...")
input_df, _ = loader.load_input_sheet()
print(f"输入表形状: {input_df.shape}")

# 测试年份生成
print("\n测试年份生成...")
years = generate_years(3, 17)
print(f"生成年份: {len(years)} 年")
print(f"前5年: {years[:5]}")
print(f"后5年: {years[-5:]}")

# 测试获取特定工作表
print("\n测试获取财务分析结果汇总...")
result_sheet = loader.get_sheet("财务分析结果汇总")
if result_sheet is not None:
    print(f"财务分析结果汇总表形状: {result_sheet.shape}")
    print("\n前5行：")
    print(result_sheet.head())

print("\n✅ 所有测试通过！")
