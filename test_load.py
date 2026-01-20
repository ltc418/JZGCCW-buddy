"""
测试数据加载是否正常
"""
import pandas as pd

# 测试xlrd是否可用
try:
    import xlrd
    print(f"xlrd version: {xlrd.__VERSION__}")
    XLRD_AVAILABLE = True
except ImportError as e:
    print(f"xlrd not available: {e}")
    XLRD_AVAILABLE = False

# 测试加载Excel
print("\n尝试加载Excel文件...")
try:
    if XLRD_AVAILABLE:
        xls = pd.ExcelFile('JZGCCW01.xls', engine='xlrd')
    else:
        xls = pd.ExcelFile('JZGCCW01.xls')

    print(f"成功加载 {len(xls.sheet_names)} 个工作表")
    print("工作表列表:")
    for sheet in xls.sheet_names[:5]:
        print(f"  - {sheet}")

    print("\n测试读取第一个工作表...")
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    print(f"形状: {df.shape}")
    print("\n成功加载Excel文件！")

except Exception as e:
    print(f"加载失败: {e}")
    import traceback
    traceback.print_exc()
