"""
Excel数据加载模块
"""
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill
import config
from utils import is_yellow_cell, get_input_module_ranges

# 检查xlrd是否可用
try:
    import xlrd
    XLRD_AVAILABLE = True
except ImportError:
    XLRD_AVAILABLE = False


class DataLoader:
    """Excel数据加载器"""

    def __init__(self, excel_file=None):
        """
        初始化数据加载器

        Args:
            excel_file: Excel文件路径，默认为config.EXCEL_FILE
        """
        self.excel_file = excel_file or config.EXCEL_FILE
        self.input_df = None
        self.yellow_mask = None
        self.all_sheets = None

    def load_input_sheet(self):
        """
        加载输入工作表

        Returns:
            tuple: (DataFrame, 黄色标记DataFrame)
        """
        # 使用pandas读取数据
        if XLRD_AVAILABLE:
            self.input_df = pd.read_excel(
                self.excel_file,
                sheet_name=config.INPUT_SHEET_NAME,
                engine='xlrd'
            )
        else:
            self.input_df = pd.read_excel(
                self.excel_file,
                sheet_name=config.INPUT_SHEET_NAME
            )

        # 暂时创建一个空的黄色标记DataFrame（后续需要用xlrd支持颜色读取）
        self.yellow_mask = pd.DataFrame(
            False,
            index=self.input_df.index,
            columns=self.input_df.columns
        )

        return self.input_df, self.yellow_mask

    def load_all_sheets(self):
        """
        加载所有工作表

        Returns:
            dict: 工作表名称到DataFrame的映射
        """
        self.all_sheets = {}

        # 使用pandas读取所有工作表
        if XLRD_AVAILABLE:
            xls = pd.ExcelFile(self.excel_file, engine='xlrd')
        else:
            xls = pd.ExcelFile(self.excel_file)

        for sheet_name in xls.sheet_names:
            self.all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)

        return self.all_sheets

    def get_sheet(self, sheet_name):
        """
        获取指定工作表

        Args:
            sheet_name: 工作表名称

        Returns:
            DataFrame
        """
        if self.all_sheets is None:
            self.load_all_sheets()
        return self.all_sheets.get(sheet_name)

    def get_sheet_raw_data(self, sheet_name):
        """
        获取指定工作表的原始数据（不使用缓存）

        Args:
            sheet_name: 工作表名称

        Returns:
            DataFrame
        """
        if XLRD_AVAILABLE:
            return pd.read_excel(self.excel_file, sheet_name=sheet_name, engine='xlrd')
        else:
            return pd.read_excel(self.excel_file, sheet_name=sheet_name)

    def get_input_module(self, module_name):
        """
        获取输入模块的数据和黄色标记

        Args:
            module_name: 模块名称，如"1. 基础信息"

        Returns:
            tuple: (模块DataFrame, 模块黄色标记DataFrame)
        """
        if self.input_df is None or self.yellow_mask is None:
            self.load_input_sheet()

        ranges = get_input_module_ranges()
        if module_name not in ranges:
            raise ValueError(f"未知模块: {module_name}")

        start_row, end_row = ranges[module_name]

        # openpyxl行索引从1开始，pandas从0开始
        module_df = self.input_df.iloc[start_row-1:end_row].copy()
        module_yellow = self.yellow_mask.iloc[start_row-1:end_row].copy()

        return module_df, module_yellow

    def get_yellow_cells_by_module(self, module_name):
        """
        获取模块的黄色单元格坐标

        Args:
            module_name: 模块名称

        Returns:
            list: [(row, col), ...] 的列表
        """
        module_df, module_yellow = self.get_input_module(module_name)
        yellow_coords = []

        for row_idx in range(len(module_yellow)):
            for col_idx in range(len(module_yellow.columns)):
                if module_yellow.iloc[row_idx, col_idx]:
                    yellow_coords.append((row_idx, col_idx))

        return yellow_coords

    def extract_input_values(self, construction_period=3, operation_period=17):
        """
        提取所有输入值，生成年份列

        Args:
            construction_period: 建设期（年）
            operation_period: 运营期（年）

        Returns:
            dict: 模块名称到输入数据的映射
        """
        from utils import generate_years

        years = generate_years(construction_period, operation_period)
        input_data = {}

        # 加载所有工作表
        self.load_input_sheet()

        for module_name in config.INPUT_MODULES:
            module_df, module_yellow = self.get_input_module(module_name)

            # 提取黄色单元格的值
            yellow_values = {}
            for row_idx, col_idx in self.get_yellow_cells_by_module(module_name):
                value = module_df.iloc[row_idx, col_idx]
                label = module_df.iloc[row_idx, 0]  # 第一列是标签

                if pd.notna(value) and pd.notna(label):
                    yellow_values[label] = value

            input_data[module_name] = yellow_values

        return input_data

    def get_original_results(self, sheet_name):
        """
        获取原始计算结果，用于验证

        Args:
            sheet_name: 工作表名称

        Returns:
            DataFrame
        """
        return self.get_sheet(sheet_name)
