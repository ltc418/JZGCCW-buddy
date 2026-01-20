"""
JZGCCW 建设工程财务分析系统 - 主应用
"""
import streamlit as st
from data_loader import DataLoader
from input_forms import InputForms
import config

# 页面配置
st.set_page_config(**config.PAGE_CONFIG)

# 标题
st.title("🏗️ JZGCCW 建设工程财务分析系统")
st.markdown("基于《建设项目经济评价方法与参数(第三版)》编制的财务分析计算系统")

# 初始化session state
if 'input_data' not in st.session_state:
    st.session_state.input_data = {}
if 'calculation_results' not in st.session_state:
    st.session_state.calculation_results = {}
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# 加载数据
def load_data():
    """加载数据"""
    loader = DataLoader()
    loader.load_all_sheets()
    return loader

data_loader = load_data()

# 全局设置区域
settings = InputForms(data_loader).render_global_settings()

# 侧边栏输入表单
with st.sidebar:
    st.header("📝 数据输入")
    st.markdown("---")

    input_forms = InputForms(data_loader)
    input_data = input_forms.render_all_modules(
        settings['construction_period'],
        settings['operation_period']
    )

    st.markdown("---")
    st.markdown("### 💡 提示")
    st.info("- 黄色格子为必填项\n- 年份数量会根据建设期和运营期自动调整\n- 填写完成后点击下方按钮")

# 保存输入数据到session state
st.session_state.input_data = input_data

# 计算按钮
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 执行计算", type="primary", use_container_width=True):
        with st.spinner("正在计算中..."):
            # TODO: 执行计算逻辑
            st.session_state.calculated = True
            st.success("计算完成！")

# 结果展示区域
if st.session_state.calculated:
    st.divider()
    st.header("📊 计算结果")

    # 结果筛选器
    st.markdown("### 选择要查看的表格")

    # 创建多选框
    selected_sheets = st.multiselect(
        "选择表格（可多选）",
        options=list(config.SHEET_MAPPING.keys()),
        format_func=lambda x: f"{x} - {config.SHEET_MAPPING[x]}",
        default=["财务分析结果汇总"]
    )

    # 显示选中的表格
    if selected_sheets:
        for sheet_name in selected_sheets:
            st.markdown(f"#### {config.SHEET_MAPPING[sheet_name]}")

            # 获取原始数据
            original_data = data_loader.get_sheet(sheet_name)

            # 显示表格
            st.dataframe(
                original_data,
                use_container_width=True,
                height=300
            )

            # 下载按钮
            csv = original_data.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                f"下载 {config.SHEET_MAPPING[sheet_name]}",
                data=csv,
                file_name=f"{sheet_name}.csv",
                mime="text/csv"
            )

    else:
        st.info("请选择要查看的表格")

# 页脚
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
        JZGCCW 建设工程财务分析系统 v1.0 | 基于《建设项目经济评价方法与参数(第三版)》
    </div>
    """,
    unsafe_allow_html=True
)
