# Streamlit 财务应用最佳实践

## 页面配置

### 基础配置
```python
import streamlit as st

st.set_page_config(
    page_title="JZGCCW 财务分析系统",
    page_icon="🏗️",
    layout="wide",           # 使用宽布局，适合表格显示
    initial_sidebar_state="expanded"  # 默认展开侧边栏
)
```

### 自定义CSS样式
```python
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)
```

## 侧边栏组织

### 模块化输入表单
使用expander组织复杂输入：

```python
with st.sidebar:
    st.header("📝 数据输入")

    # 使用expander分组
    with st.expander("1️⃣ 基础信息"):
        project_name = st.text_input("项目名称", key="project_name")

    with st.expander("2️⃣ 项目投资"):
        building_cost = st.number_input(
            "建筑工程费",
            value=67062.86,
            format="%.2f",
            key="building_cost"
        )
```

### 动态表单生成
基于参数动态生成输入项：

```python
construction_period = st.number_input("建设期（年）", value=3)
operation_period = st.number_input("运营期（年）", value=17)

# 动态生成年份输入
year_generator = YearGenerator(construction_period, operation_period)
years = year_generator.generate_year_names()

for year in years:
    year_num = year_generator.get_year_index(year)
    if year_generator.is_operation_year(year_num):
        revenue = st.number_input(
            year,
            value=10000.0,
            format="%.2f",
            key=f"sales_{year}"
        )
    else:
        # 建设期自动设为0
        st.session_state[f"sales_{year}"] = 0.0
```

### 分列布局
使用columns组织相关输入：

```python
col1, col2, col3 = st.columns(3)

with col1:
    construction_period = st.number_input("建设期（年）", value=3)

with col2:
    operation_period = st.number_input("运营期（年）", value=17)

with col3:
    st.metric("计算期", f"{construction_period + operation_period}年")
```

## 输入组件最佳实践

### 数字输入
```python
value = st.number_input(
    label="金额（万元）",
    value=1000.0,
    min_value=0.0,
    max_value=100000.0,
    step=0.01,
    format="%.2f",  # 2位小数
    key="amount_input"
)
```

### 文本输入
```python
text = st.text_input(
    label="项目名称",
    value="默认项目",
    max_chars=50,
    key="project_name"
)
```

### 选择框
```python
option = st.selectbox(
    label="还款方式",
    options=["等额本金", "等额本息"],
    index=0,
    key="repayment_method"
)
```

### 滑块输入
```python
percentage = st.slider(
    label="比率（%）",
    min_value=0.0,
    max_value=100.0,
    value=10.0,
    step=0.1,
    key="rate_input"
)
```

## 数据状态管理

### Session State 使用
```python
# 初始化session state
if 'calculated' not in st.session_state:
    st.session_state.calculated = False
if 'calculation_results' not in st.session_state:
    st.session_state.calculation_results = {}

# 更新session state
st.session_state.calculated = True
st.session_state.calculation_results = results

# 读取session state
if st.session_state.get('calculated', False):
    results = st.session_state.calculation_results
```

### 清理Session State
```python
# 当参数改变时清除旧结果
if new_construction != old_construction:
    st.session_state.calculated = False
    st.session_state.calculation_results = {}
```

## 数据显示

### 表格显示
```python
# 显示DataFrame
st.dataframe(
    df,
    use_container_width=True,  # 使用容器宽度
    height=400,              # 固定高度
    hide_index=True,           # 隐藏索引
)

# 带列高亮的表格
st.dataframe(
    df,
    use_container_width=True,
    column_config={
        "金额": st.column_config.NumberColumn(
            "金额（万元）",
            format="%.2f"
        )
    }
)
```

### 指标显示
```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="净现值(NPV)",
        value=f"{npv:,.2f}",
        delta=f"折现率{discount_rate:.1%}"
    )

with col2:
    st.metric(
        label="内部收益率(IRR)",
        value=f"{irr:.2f}%",
        delta="高于基准收益率"
    )
```

### 进度条和状态
```python
# 加载状态
with st.spinner("正在计算中..."):
    results = perform_calculation()

# 成功状态
st.success("✅ 计算完成！")

# 信息提示
st.info("📊 请在下方的结果区域查看计算表格")

# 警告提示
st.warning("⚠️ 请先填写所有必需参数")

# 错误提示
st.error("❌ 计算过程中发生错误")
```

## 文件操作

### 文件上传
```python
uploaded_file = st.file_uploader(
    label="上传Excel文件",
    type=['xls', 'xlsx'],
    accept_multiple_files=False,
    key="file_upload"
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, engine='xlrd')
    st.dataframe(df)
```

### 文件下载
```python
# CSV下载
csv = df.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="下载CSV",
    data=csv,
    file_name="result.csv",
    mime="text/csv"
)

# Excel下载
from io import BytesIO
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
buffer.seek(0)
st.download_button(
    label="下载Excel",
    data=buffer,
    file_name="result.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```

## 布局技巧

### 分隔线
```python
st.divider()  # 水平分隔线
st.markdown("---")  # Markdown分隔线
```

### 标题层级
```python
st.title("🏗️ JZGCCW 建设工程财务分析系统")
st.header("📊 计算结果")
st.subheader("利润表")
st.markdown("### 选择要查看的表格")
st.markdown("#### 利润表")
```

### Tab标签页
```python
tab1, tab2, tab3 = st.tabs(["投资分析", "成本分析", "收益分析"])

with tab1:
    st.write("投资分析内容")

with tab2:
    st.write("成本分析内容")

with tab3:
    st.write("收益分析内容")
```

### 可折叠区域
```python
with st.expander("查看详细计算过程", expanded=False):
    st.code("""
        计算过程：
        1. 年折旧额 = (固定资产原值 - 净残值) / 折旧年限
        2. 累计折旧 = Σ年折旧额
        3. 净值 = 固定资产原值 - 累计折旧
    """, language="python")
```

## 交互设计

### 按钮触发计算
```python
# 主按钮
if st.button("🚀 执行计算", type="primary", use_container_width=True):
    with st.spinner("正在计算中..."):
        results = calculate()

# 次要按钮
if st.button("重置参数", key="reset"):
    st.session_state.clear()
    st.rerun()
```

### 条件显示
```python
if st.session_state.get('calculated', False):
    st.header("📊 计算结果")
    # 显示结果
else:
    st.info("👈 请填写参数后点击'执行计算'按钮")
```

### 多选框
```python
selected_tables = st.multiselect(
    label="选择表格（可多选）",
    options=['投资估算表', '折旧表', '利润表', '现金流量表'],
    default=['利润表'],
    key="table_selection"
)
```

## 性能优化

### 缓存计算结果
```python
@st.cache_data(ttl=3600)  # 缓存1小时
def load_excel_data(file_path):
    return pd.read_excel(file_path, engine='xlrd')

@st.cache_resource
def get_year_generator(construction, operation):
    return YearGenerator(construction, operation)
```

### 避免重复计算
```python
# 只在参数改变时重新计算
if st.session_state.get('params_changed', False):
    results = calculate()
    st.session_state.calculation_results = results
    st.session_state.params_changed = False
```

### 延迟加载大数据
```python
# 对于大量表格，使用分页
page = st.number_input("页码", value=1, min_value=1)
page_size = 10
start_idx = (page - 1) * page_size
end_idx = start_idx + page_size

st.dataframe(df.iloc[start_idx:end_idx])
```

## 错误处理

### Try-Except块
```python
try:
    results = calculation_engine.run_all_calculations()
    st.success("✅ 计算完成！")
except Exception as e:
    st.error(f"❌ 计算过程中发生错误: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
```

### 输入验证
```python
# 验证必需参数
if not project_name:
    st.warning("⚠️ 请输入项目名称")
elif construction_period <= 0:
    st.warning("⚠️ 建设期必须大于0")
else:
    # 执行计算
    results = calculate()
```

### 文件读取错误处理
```python
try:
    import xlrd
except ImportError:
    st.error("❌ 缺少xlrd库，正在尝试使用备用方法...")
    # 使用备用读取方法
```

## 响应式设计

### 基于屏幕宽度的布局
```python
import streamlit as st

container_width = st.get_option("client.displayWidth")

if container_width < 800:
    cols = st.columns(1)
elif container_width < 1200:
    cols = st.columns(2)
else:
    cols = st.columns(3)

with cols[0]:
    st.write("内容1")
```

### 自适应表格高度
```python
height = min(400, 100 + len(df) * 30)
st.dataframe(df, height=height)
```

## 数据可视化

### 折线图
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(years, net_cashflows, marker='o')
ax.set_xlabel('年份')
ax.set_ylabel('净现金流量（万元）')
ax.grid(True)

st.pyplot(fig)
```

### 柱状图
```python
import plotly.express as px

fig = px.bar(
    df_melted,
    x='年份',
    y='金额',
    color='项目',
    barmode='group'
)

st.plotly_chart(fig, use_container_width=True)
```

## 中文支持

### 文件编码
```python
# 保存CSV时使用utf-8-sig编码（带BOM）
csv = df.to_csv(index=False, encoding='utf-8-sig')
```

### 字体设置
```python
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
```

## 用户体验优化

### 加载提示
```python
# 显示进度
progress_bar = st.progress(0)

for i in range(100):
    # 执行计算
    progress_bar.progress(i + 1)

# 完成后隐藏
progress_bar.empty()
```

### 实时更新
```python
# 显示计算步骤
status_text = st.empty()
status_text.text("步骤 1/4: 计算投资估算...")
# 计算投资估算

status_text.text("步骤 2/4: 计算折旧...")
# 计算折旧

status_text.text("步骤 3/4: 计算成本...")
# 计算成本

status_text.text("步骤 4/4: 生成报表...")
# 生成报表

status_text.empty()  # 清除提示
```

### 帮助提示
```python
st.markdown("### 💡 提示")
st.info("""
    - 年份数量会根据建设期和运营期自动调整
    - 填写完成后点击'执行计算'按钮
    - 所有金额单位为万元
""")
```

## 部署建议

### requirements.txt
```
streamlit>=1.28.0
pandas>=2.0.0
xlrd>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
```

### 启动脚本
```batch
@echo off
echo ========================================
echo   JZGCCW 建设工程财务分析系统
echo ========================================
echo.
streamlit run app_v2.py

pause
```

### 运行命令
```bash
# 开发模式
streamlit run app_v2.py

# 生产模式
streamlit run app_v2.py --logger.level=warning

# 自定义端口
streamlit run app_v2.py --server.port=8501
```
