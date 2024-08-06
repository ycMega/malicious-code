import csv
import json
import os

from aiologger import Logger
from attr import asdict
from pydantic import BaseModel
from typeguard import typechecked

from src.io.async_logger import GLOBAL_LOGGER, catch_exceptions
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


class FeatureExtractor:

    def __init__(self, web_data: WebData) -> None:
        self.meta = None
        self.web_data = web_data
        # self.result = None
        # self.execution_time = None
        # self.logger = self.web_data.logger

    def calculate_score(self):
        raise NotImplementedError("Subclasses must implement this method")

    def log_info(self, message):
        # 这里可以实现日志记录逻辑
        print(message)


class OverallExtractionResult:

    def __init__(self, web_data: WebData) -> None:
        self.web_data = web_data
        self.results: list[FeatureExtractionResult] = []  # 存储所有特征提取结果
        self.summary: dict[str, dict[str, int]] = {}
        # self.logger = self.web_data.logger
        # self.total_features = 0  # 总特征数量
        # self.execution_times = []  # 存储各个提取器的执行时间

    def add_result(self, result: FeatureExtractionResult):
        self.results.append(result)
        # self.total_features += result.feature_count
        # self.execution_times.append(result.execution_time)

    @catch_exceptions
    async def save_to_csv(self):
        filename = os.path.join(self.web_data.dir_path, "features.csv")
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # 写入表头
            writer.writerow(["Type", "Feature", "Count", "Time(s)"])

            # 写入数据
            try:
                for key, features in self.summary.items():
                    for feature, result in features.items():
                        count, time = result["Count"], result["Time"]
                        writer.writerow([key, feature, count, time])
            except Exception as e:
                print(f"Error saving to CSV: {e}")
                GLOBAL_LOGGER.error(f"Error saving to CSV: {e}")

    @catch_exceptions
    @typechecked
    @classmethod
    async def load_from_csv(cls, filename) -> dict[str, dict[str, dict]]:
        data: dict[str, dict[str, dict]] = {}

        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)

            # 跳过表头
            next(reader)

            for row in reader:
                type_, feature, count_str, time_str = row
                try:
                    count: int = int(count_str)
                    time = float(time_str)
                except ValueError:
                    GLOBAL_LOGGER.error(f"Invalid data in CSV: {row}, skipping")
                    continue

                if type_ not in data:
                    data[type_] = {}
                data[type_][feature] = {"Count": count, "Time": time}

        return data

    async def save_to_json(self):
        filename = os.path.join(self.web_data.dir_path, "features.json")
        try:
            with open(filename, mode="w", encoding="utf-8") as file:
                res_list = []
                for res in self.results:
                    res_dict = {
                        "Type": res.filetype,
                        "Feature": res.extractor_name,
                        "Count": res.feature_count,
                        "Time(s)": round(res.execution_time, 5),
                        "AdditionalInfo": res.additional_info,
                    }
                    res_list.append(res_dict)
                file.write(json.dumps(res_list, indent=4))
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            await GLOBAL_LOGGER.error(f"Error saving to JSON: {e}")

    @classmethod
    @typechecked
    @catch_exceptions
    async def load_from_json(cls, filename) -> list[FeatureExtractionResult]:
        await GLOBAL_LOGGER.info(
            f"Loading from JSON {filename}, clearing previous results"
        )
        results = []
        try:
            with open(filename, mode="r", encoding="utf-8") as file:
                res_list = json.load(file)
                for res in res_list:
                    result = FeatureExtractionResult(
                        res["Type"],
                        res["Feature"],
                        res["Count"],
                        res["Time(s)"],
                        res["AdditionalInfo"],
                    )
                    results.append(result)
        except Exception as e:
            await GLOBAL_LOGGER.error(f"Error loading from JSON: {e}")
        return results

    # todo：针对不同类型的特征进行统计
    async def do_summary(self):
        for t in FILE_TYPES:
            self.summary[t] = {}
        for result in self.results:
            if result.filetype not in self.summary:
                self.summary[result.filetype] = {}
            self.summary[result.filetype][result.extractor_name] = {
                "Count": result.feature_count,
                "Time": round(result.execution_time, 5),
            }
        await self.save_to_csv()
        await self.save_to_json()
