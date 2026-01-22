"""
测试加载验证
"""
print("="*50)
print("测试 app_v3.py 和数据收集模块")
print("="*50)

try:
    from app_v3 import format_dataframe
    print("[√] app_v3.py 导入成功")
except Exception as e:
    print(f"[!] app_v3.py 导入失败: {e}")

try:
    from input_collector import collect_input_data
    print("[√] input_collector.py 导入成功")
except Exception as e:
    print(f"[!] input_collector.py 导入失败: {e}")

try:
    from data_models import InputData, BankLoanPlan
    print("[√] data_models.py 导入成功")
except Exception as e:
    print(f"[!] data_models.py 导入失败: {e}")

# 检查 grace_period 字段
try:
    loan = BankLoanPlan()
    print(f"[√] grace_period 字段存在: {loan.grace_period}")
except Exception as e:
    print(f"[!] grace_period 检查失败: {e}")

# 检查 input_collector 源码
try:
    import inspect
    source = inspect.getsource(collect_input_data)
    if 'grace_period' in source:
        print("[√] input_collector.py 已更新 grace_period 收集")
    else:
        print("[!] input_collector.py 缺少 grace_period 收集")

    if 'investment_plan' in source:
        print("[√] input_collector.py 已更新投资计划收集")
    else:
        print("[!] input_collector.py 缺少投资计划收集")

    if 'fuel_8' in source:
        print("[√] input_collector.py 已完整收集8种燃料")
    else:
        print("[!] input_collector.py 燃料收集不完整")

    if 'material_8' in source:
        print("[√] input_collector.py 已完整收集8种材料")
    else:
        print("[!] input_collector.py 材料收集不完整")
except Exception as e:
    print(f"[!] input_collector 源码检查失败: {e}")

print("="*50)
print("测试完成")
print("="*50)
