# JZGCCW 建设工程财务分析系统

基于《建设项目经济评价方法与参数(第三版)》编制的财务分析计算系统。

## 功能特性

- ✅ 完整复现JZGCCW01.xls所有计算逻辑
- ✅ 可动态调整建设期和运营期
- ✅ 可折叠式侧边栏导航
- ✅ 筛选式结果展示
- ✅ 自动对比验证，显示差异百分比
- ✅ 表格布局与原Excel完全一致

## 安装运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 项目结构

```
JZGCCW-buddy/
├── app.py                 # 主应用入口
├── config.py              # 配置文件
├── data_loader.py         # Excel数据加载
├── input_forms.py         # 输入表单模块
├── calculations.py        # 计算逻辑模块
├── results_display.py    # 结果展示模块
├── verification.py       # 验证对比模块
├── utils.py              # 工具函数
├── JZGCCW01.xls          # 原始Excel文件
└── requirements.txt      # 依赖列表
```

## 使用说明

1. 在页面顶部设置建设期和运营期
2. 在左侧侧边栏填写12个输入模块的数据
3. 点击"执行计算"按钮
4. 在结果区域选择需要查看的表格
5. 查看自动验证的差异百分比

## 技术栈

- Python 3.8+
- Streamlit
- Pandas
- OpenPyXL
