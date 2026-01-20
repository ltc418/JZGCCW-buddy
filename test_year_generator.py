"""
测试年份生成器
"""
from year_generator import YearGenerator, DynamicTableBuilder

# 测试基本功能
print("=== 测试基本功能 ===")
generator = YearGenerator(construction_period=3, operation_period=17)

print(f"建设期: {generator.construction_period}年")
print(f"运营期: {generator.operation_period}年")
print(f"计算期: {generator.total_period}年")

print("\n年份名称:")
year_names = generator.generate_year_names()
print(year_names[:5], "...", year_names[-5:])

print("\n年份类型:")
for i in [1, 2, 3, 4, 5, 10, 20]:
    print(f"第{i}年: {generator.get_year_type(i)}")

print("\n创建年份表格:")
df = generator.create_year_dataframe()
print(df.head(10))

print("\n=== 测试年度数据字典 ===")
year_data = generator.initialize_year_data_dict(default_value=100.0)
print(f"初始化数据: {year_data['第1年']}")

print("\n=== 测试动态表格构建器 ===")
builder = DynamicTableBuilder(generator)

row_labels = ["项目1", "项目2", "项目3"]
year_dict = {
    "第1年": [10.0, 20.0, 30.0],
    "第2年": [15.0, 25.0, 35.0],
    "第3年": [12.0, 22.0, 32.0],
}

df = builder.build_table_with_years(row_labels, year_dict)
print("\n动态表格:")
print(df)

print("\n空年度表格:")
empty_df = builder.build_yearly_table(["收入", "成本", "利润"])
print(empty_df)

print("\n测试完成!")
