# Excel 财务模板常见模式

## 文件格式

### 文件扩展名
- `.xls` - Excel 97-2003格式（需要xlrd引擎）
- `.xlsx` - Excel 2007+格式（使用openpyxl引擎）

### 读取Excel文件

```python
# 对于.xls文件
import pandas as pd
df = pd.read_excel('file.xls', sheet_name='SheetName', engine='xlrd')

# 对于.xlsx文件
df = pd.read_excel('file.xlsx', sheet_name='SheetName', engine='openpyxl')
```

## 工作表结构

### 标准标题行结构
```
行1: 工作表标题（如"表13-9 借款还本付息计划表"）
行2: 单位说明（如"单位：万元"）
行3: 空行
行4: 序号标题
行5: 年份标题（合计、建设期第1年、运营期第1年...）
行6+: 数据行
```

### 多级表头结构

示例：投资估算表
```
              | 合计 | 建设期       |     | 运营期       |
              |       | 第1年| 第2年 | ... | 第1年 | 第2年 |
项目名称     |       |       |       |     |       |       |
--------------|-------|-------|-------|-----|-------|-------|
建筑工程费    | ...   | ...   | ...   | ... | ...   | ...   |
设备购置费    | ...   | ...   | ...   | ... | ...   | ...   |
```

### 缩进层级结构
示例：成本费用估算表
```
1. 外购原材料费
  1.1 主要原材料A费用
       数量（吨）
       单价（元/吨）
       增值税进项税
  1.2 主要原材料B费用
       ...
2. 外购燃料及动力费
  2.1 燃料1
  2.2 动力1
...
```

## 数据提取模式

### 提取数值数据

```python
# 方式1：按位置提取
value = df.iloc[10, 5]  # 第10行，第5列

# 方式2：按列名提取（如果有列名）
value = df.loc[row_name, column_name]

# 方式3：按条件提取
value = df[df['项目'] == '建筑工程费']['合计'].values[0]
```

### 跳过表头

```python
# 数据通常从第5或6行开始
data_start_row = 5
data_df = df.iloc[data_start_row:, :]

# 清理未命名的列
data_df = data_df.dropna(axis=1, how='all')
```

### 处理合并单元格

Excel中合并的单元格在pandas中读取为：
- 合并区域的左上角单元格有值
- 其他位置为NaN

```python
# 向下填充合并单元格的值
df['项目'] = df['项目'].fillna(method='ffill')

# 向右填充
df['合计'] = df['合计'].fillna(method='ffill')
```

## 常见工作表类型

### 1. 汇总表（单列数据）
示例：建设投资估算表
```
项目           | 金额    | 说明
--------------|---------|--------
建筑工程费    | 67062.86| 含税投资
设备购置费    | 2360.38  | 含税投资
设备安装费    | 18299.19 | 含税投资
...
项目总投资合计 | xxx     |
```

### 2. 年度数据表（横向）
示例：折旧表
```
项目           | 建设期第1年 | 建设期第2年 | 运营期第1年 | 运营期第2年
--------------|-------------|-------------|-------------|-------------
固定资产原值  | xxx         | xxx         | xxx         | xxx
年度折旧额    | 0.0         | 0.0         | xxx         | xxx
累计折旧      | 0.0         | 0.0         | xxx         | xxx
净值          | xxx         | xxx         | xxx         | xxx
```

### 3. 多级明细表（缩进）
示例：总成本费用估算表
```
项目                 | 运营期第1年 | 运营期第2年
--------------------|-------------|-------------
外购原材料费          | xxx         | xxx
  主要原材料A费用     | xxx         | xxx
     数量（吨）       | xxx         | xxx
     单价（元/吨）     | xxx         | xxx
     增值税进项税     | xxx         | xxx
  主要原材料B费用     | xxx         | xxx
...
工资及福利费          | xxx         | xxx
  管理人员工资       | xxx         | xxx
  技术人员工资       | xxx         | xxx
...
```

### 4. 现金流量表
示例：项目投资现金流量表
```
项目           | 合计 | 建设期 | 运营期 | ...
--------------|-------|--------|--------|-------
现金流入        | xxx   | xxx    | xxx    |
  营业收入      | xxx   | 0      | xxx    |
  回收固定资产余值| xxx   | 0      | xxx    |
  回收流动资金  | xxx   | 0      | xxx    |
现金流出        | xxx   | xxx    | xxx    |
  建设投资      | xxx   | xxx    | 0      |
  流动资金      | xxx   | 0      | xxx    |
  经营成本      | xxx   | 0      | xxx    |
  营业税金及附加| xxx   | 0      | xxx    |
  所得税        | xxx   | 0      | xxx    |
净现金流量      | xxx   | xxx    | xxx    |
累计净现金流量  | xxx   | xxx    | xxx    |
```

## 数据类型识别

### 数值列
- 包含数字的列（整数或小数）
- 需要转换为float类型
```python
df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
```

### 文本列
- 项目名称、说明等
- 需要清洗空白和特殊字符
```python
df['项目'] = df['项目'].str.strip()
```

### 公式列
- Excel中的公式（=SUM(A1:B10)）在pandas中读取为计算后的值
- 无需特殊处理

## 数据验证

### 检查缺失值
```python
missing_values = df.isnull().sum()
print("缺失值统计：")
print(missing_values)
```

### 检查数据类型
```python
print("数据类型：")
print(df.dtypes)
```

### 检查异常值
```python
print("数值统计：")
print(df.describe())
```

## 常见问题处理

### 问题1：列名未识别
```
Unnamed: 0 | Unnamed: 1 | ...
```
**原因**：Excel文件没有明确的列标题行
**解决**：
```python
# 指定表头行
df = pd.read_excel('file.xls', header=4)  # 第5行作为列名

# 或手动设置列名
df.columns = ['项目', '合计', '建设期第1年', ...]
```

### 问题2：合并单元格数据丢失
**原因**：Excel合并单元格在pandas中只有左上角有值
**解决**：
```python
# 向前填充
df = df.fillna(method='ffill', axis=0)  # 按列向下填充
```

### 问题3：文件编码问题
**症状**：中文显示为乱码
**解决**：
```python
# 读取时指定编码（如果是CSV）
df = pd.read_csv('file.csv', encoding='utf-8-sig')

# 或使用gbk编码
df = pd.read_csv('file.csv', encoding='gbk')
```

## 数据输出到Excel

### 创建新的Excel文件
```python
import pandas as pd

# 创建DataFrame
df = pd.DataFrame({
    '项目': ['建筑工程费', '设备购置费', ...],
    '金额': [67062.86, 2360.38, ...],
    '说明': ['含税投资', '含税投资', ...]
})

# 写入Excel
df.to_excel('output.xlsx', index=False, encoding='utf-8-sig')
```

### 写入多个工作表
```python
with pd.ExcelWriter('output.xlsx') as writer:
    df1.to_excel(writer, sheet_name='投资估算', index=False)
    df2.to_excel(writer, sheet_name='折旧表', index=False)
    df3.to_excel(writer, sheet_name='利润表', index=False)
```

### 格式化Excel输出
```python
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

# 加载工作簿
wb = load_workbook('output.xlsx')
ws = wb.active

# 设置格式
ws['A1'].font = Font(bold=True)
ws['A1'].fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

# 设置列宽
ws.column_dimensions['A'].width = 20
ws.column_dimensions['B'].width = 15

# 保存
wb.save('output.xlsx')
```

## 性能优化

### 大文件读取
```python
# 只读取需要的行
df = pd.read_excel('large_file.xls', nrows=100)

# 只读取需要的列
df = pd.read_excel('file.xls', usecols=['项目', '金额', '说明'])
```

### 内存优化
```python
# 指定数据类型减少内存
dtypes = {'金额': 'float32', '数量': 'int32'}
df = pd.read_excel('file.xls', dtype=dtypes)
```

## 文件路径处理

### Windows路径
```python
import os
file_path = r'H:\GIT\project\data\file.xls'  # 使用原始字符串
# 或
file_path = os.path.join('H:', 'GIT', 'project', 'data', 'file.xls')
```

### 相对路径
```python
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'data', 'file.xls')
```

### 跨平台路径
```python
from pathlib import Path
file_path = Path('data') / 'file.xls'
file_path = file_path.absolute()
```
