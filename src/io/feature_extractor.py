import csv
import os

from click import File

from src.io.file_extractor import WebData
from src.utils.utils import FILE_TYPES

# from enum import Enum, auto


# class FileType(Enum):
#     HTML = "html"
#     CSS = "css"
#     JS = "js"
#     URL = "url"
#     HAR = "har"
#     OTHER = "other"
class ExtractorMeta:
    def __init__(self, filetype, name, author, description, version) -> None:
        self.filetype = filetype
        self.name = name
        self.author = author
        self.description = description
        self.version = version

    def __repr__(self) -> str:
        return f"ExtractorMeta(name={self.name}, filetype={self.filetype}, description={self.description}, version={self.version})"


class FeatureExtractor:
    def __init__(self, web_data: WebData) -> None:
        self.meta = None
        self.web_data = web_data
        # self.result = None
        # self.execution_time = None
        self.logger = self.web_data.logger

    def calculate_score(self):
        raise NotImplementedError("Subclasses must implement this method")

    def log_info(self, message):
        # 这里可以实现日志记录逻辑
        print(message)


class FeatureExtractionResult:
    def __init__(
        self,
        filetype,
        extractor_name,
        feature_count,
        execution_time,
        additional_info=None,
    ) -> None:
        self.filetype = filetype  # 特征类型
        self.extractor_name = extractor_name  # 特征提取器的名称
        self.feature_count = feature_count  # 特征数量
        self.execution_time = execution_time  # 执行时间
        self.additional_info = additional_info or {}  # 其他附加信息（可选）

    def __repr__(self):
        return (
            f"FeatureExtractionResult(extractor_name={self.extractor_name}, "
            f"feature_count={self.feature_count}, "
            f"execution_time={self.execution_time}, "
            f"additional_info={self.additional_info})"
        )


class OverallExtractionResult:
    def __init__(self, web_data: WebData) -> None:
        self.web_data = web_data
        self.results: list[FeatureExtractionResult] = []  # 存储所有特征提取结果
        self.summary: dict[str, dict[str, int]] = {}
        # self.total_features = 0  # 总特征数量
        # self.execution_times = []  # 存储各个提取器的执行时间

    def add_result(self, result: FeatureExtractionResult):
        self.results.append(result)
        # self.total_features += result.feature_count
        # self.execution_times.append(result.execution_time)

    def save_to_csv(self):
        filename = os.path.join(self.web_data.dir_path, "features.csv")
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # 写入表头
            writer.writerow(["Type", "Feature", "Count"])

            # 写入数据
            for key, features in self.summary.items():
                for feature, count in features.items():
                    writer.writerow([key, feature, count])

    def load_from_csv(self, filename):
        data: dict[str, dict[str, int]] = {}

        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)

            # 跳过表头
            next(reader)

            for row in reader:
                type_, feature, count_str = row
                count: int = int(count_str)  # 转换为整数

                if type_ not in data:
                    data[type_] = {}
                data[type_][feature] = count

        return data

    # todo：针对不同类型的特征进行统计
    def do_summary(self):
        for t in FILE_TYPES:
            self.summary[t] = {}
        for result in self.results:
            if result.filetype not in self.summary:
                self.summary[result.filetype] = {}
            self.summary[result.filetype][result.extractor_name] = result.feature_count
        self.save_to_csv()
