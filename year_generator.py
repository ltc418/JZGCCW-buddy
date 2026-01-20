"""
动态年份生成器
根据建设期和运营期动态生成年份列和相关数据结构
"""
from typing import Dict, List
import pandas as pd


class YearGenerator:
    """动态年份生成器"""

    def __init__(self, construction_period: int = 3, operation_period: int = 17):
        """
        初始化年份生成器

        Args:
            construction_period: 建设期（年）
            operation_period: 运营期（年）
        """
        self.construction_period = construction_period
        self.operation_period = operation_period
        self.total_period = construction_period + operation_period

    def generate_year_names(self) -> List[str]:
        """
        生成年份名称列表

        Returns:
            list: ["第1年", "第2年", ..., "第20年"]
        """
        return [f"第{i+1}年" for i in range(self.total_period)]

    def generate_year_numbers(self) -> List[int]:
        """
        生成年份数字列表

        Returns:
            list: [1, 2, ..., 20]
        """
        return list(range(1, self.total_period + 1))

    def is_construction_year(self, year_num: int) -> bool:
        """
        判断是否为建设期年份

        Args:
            year_num: 年份数字（从1开始）

        Returns:
            bool: 是否为建设期
        """
        return 1 <= year_num <= self.construction_period

    def is_operation_year(self, year_num: int) -> bool:
        """
        判断是否为运营期年份

        Args:
            year_num: 年份数字（从1开始）

        Returns:
            bool: 是否为运营期
        """
        return self.construction_period < year_num <= self.total_period

    def get_year_type(self, year_num: int) -> str:
        """
        获取年份类型

        Args:
            year_num: 年份数字

        Returns:
            str: "建设期" 或 "运营期"
        """
        return "建设期" if self.is_construction_year(year_num) else "运营期"

    def get_year_index(self, year_name: str) -> int:
        """
        从年份名称获取年份数字

        Args:
            year_name: 年份名称，如"第1年"

        Returns:
            int: 年份数字
        """
        # 移除"第"和"年"
        return int(year_name.replace("第", "").replace("年", ""))

    def create_year_dataframe(self) -> pd.DataFrame:
        """
        创建包含年份信息的DataFrame

        Returns:
            DataFrame: 包含年份信息的表格
        """
        year_names = self.generate_year_names()
        year_numbers = self.generate_year_numbers()

        data = {
            "年份名称": year_names,
            "年份数字": year_numbers,
            "年份类型": [self.get_year_type(y) for y in year_numbers],
            "是否建设期": [self.is_construction_year(y) for y in year_numbers],
            "是否运营期": [self.is_operation_year(y) for y in year_numbers],
        }

        return pd.DataFrame(data)

    def initialize_year_data_dict(self, default_value=0.0) -> Dict[str, float]:
        """
        初始化按年存储的字典

        Args:
            default_value: 默认值

        Returns:
            dict: {"第1年": 0.0, "第2年": 0.0, ..., "第20年": 0.0}
        """
        years = self.generate_year_names()
        return {year: default_value for year in years}

    def filter_construction_years(self, data_dict: Dict[str, float]) -> Dict[str, float]:
        """
        过滤出建设期的数据

        Args:
            data_dict: 按年存储的字典

        Returns:
            dict: 只包含建设期数据的字典
        """
        filtered = {}
        for year_name, value in data_dict.items():
            year_num = self.get_year_index(year_name)
            if self.is_construction_year(year_num):
                filtered[year_name] = value
        return filtered

    def filter_operation_years(self, data_dict: Dict[str, float]) -> Dict[str, float]:
        """
        过滤出运营期的数据

        Args:
            data_dict: 按年存储的字典

        Returns:
            dict: 只包含运营期数据的字典
        """
        filtered = {}
        for year_name, value in data_dict.items():
            year_num = self.get_year_index(year_name)
            if self.is_operation_year(year_num):
                filtered[year_name] = value
        return filtered

    def get_cumulative_sum(self, data_dict: Dict[str, float]) -> Dict[str, float]:
        """
        计算累计值

        Args:
            data_dict: 按年存储的字典

        Returns:
            dict: 累计值字典
        """
        years = self.generate_year_names()
        cumulative = {}
        total = 0.0

        for year in years:
            total += data_dict.get(year, 0.0)
            cumulative[year] = total

        return cumulative

    def scale_data(self, data_dict: Dict[str, float], scale_factor: float) -> Dict[str, float]:
        """
        按比例缩放年度数据

        Args:
            data_dict: 原始数据字典
            scale_factor: 缩放因子

        Returns:
            dict: 缩放后的数据字典
        """
        return {year: value * scale_factor for year, value in data_dict.items()}


class DynamicTableBuilder:
    """动态表格构建器"""

    def __init__(self, year_generator: YearGenerator):
        """
        初始化动态表格构建器

        Args:
            year_generator: 年份生成器实例
        """
        self.year_generator = year_generator
        self.years = year_generator.generate_year_names()

    def build_table_with_years(self, row_labels: List[str], year_data: Dict[str, List[float]]) -> pd.DataFrame:
        """
        构建包含年份列的表格

        Args:
            row_labels: 行标签列表
            year_data: 年份数据字典，格式为 {"第1年": [值1, 值2, ...], "第2年": [...]}

        Returns:
            DataFrame: 构建的表格
        """
        columns = ["项目名称"] + self.years

        data = []
        for i, label in enumerate(row_labels):
            row = [label]
            for year in self.years:
                if year in year_data and i < len(year_data[year]):
                    row.append(year_data[year][i])
                else:
                    row.append(0.0)
            data.append(row)

        return pd.DataFrame(data, columns=columns)

    def build_yearly_table(self, row_labels: List[str]) -> pd.DataFrame:
        """
        构建空的年度表格

        Args:
            row_labels: 行标签列表

        Returns:
            DataFrame: 空表格，包含所有年份列
        """
        columns = ["项目名称"] + self.years
        data = [[label] + [0.0] * len(self.years) for label in row_labels]
        return pd.DataFrame(data, columns=columns)

    def expand_to_years(self, base_data: Dict[str, float], year_data: Dict[str, float]) -> Dict[str, float]:
        """
        将基础数据扩展到各年（用于将年度数据分配到各年）

        Args:
            base_data: 基础数据（如年度总数）
            year_data: 各年数据

        Returns:
            dict: 合并后的年度数据
        """
        result = self.year_generator.initialize_year_data_dict()

        # 优先使用年度数据
        for year, value in year_data.items():
            result[year] = value

        # 如果没有年度数据，使用基础数据
        for year, value in result.items():
            if value == 0.0 and base_data:
                # 将基础数据平均分配到各年（可根据需要调整逻辑）
                total_years = len(self.years)
                avg_value = sum(base_data.values()) / total_years if base_data else 0.0
                result[year] = avg_value

        return result
