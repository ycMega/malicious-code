import csv
import json
import os
from typing import ChainMap

from attr import asdict
from pydantic import BaseModel
from typeguard import typechecked

from src.io.async_logger import GLOBAL_LOGGER, catch_exceptions
from src.io.file_extractor import WebData
from src.utils.utils import FILE_TYPES, make_serializable

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
        info_dict,
        # feature_count,
        # execution_time,
        # additional_info=None,
    ) -> None:
        self.filetype = filetype  # 特征类型
        self.extractor_name = extractor_name  # 特征提取器的名称
        self.info = info_dict  # 特征提取结果信息
        # key: filename, value: dict(count, time, additional_info)
        # self.feature_count = feature_count  # 特征数量
        # self.execution_time = execution_time  # 执行时间
        # self.additional_info = additional_info or {}  # 其他附加信息（可选）

    def __repr__(self):
        return (
            f"FeatureExtractionResult(extractor_name={self.extractor_name}, "
            f"info={self.info}, "
        )


class FeatureRegistry:
    def __init__(self):
        self.registry = {}
        self.user_registry = {}

    def register(self, feature: "FeatureExtractor", is_user_feature=True):
        # 获取 name 属性
        custom_name = getattr(feature.meta, "name", None)
        if not custom_name:
            raise ValueError("Feature name is required.")
        # 检查是否重复
        if not is_user_feature:
            if custom_name in self.registry:
                raise ValueError(
                    f"internal feature name '{custom_name}' is already registered."
                )
            self.registry[custom_name] = feature
        else:
            if custom_name in self.user_registry:
                raise ValueError(
                    f"user feature name '{custom_name}' is already registered."
                )
            self.user_registry[custom_name] = feature

    def unregister(self, feature: "FeatureExtractor"):
        custom_name = getattr(feature.meta, "name", None)
        if custom_name and custom_name in self.registry:
            del self.registry[custom_name]
        elif custom_name and custom_name in self.user_registry:
            del self.user_registry[custom_name]
        else:
            return False
        return True

    def is_registered(self, feature: "FeatureExtractor"):
        custom_name = getattr(feature.meta, "name", None)
        return custom_name and custom_name in dict(
            ChainMap(self.registry, self.user_registry)
        )

    # 必须在完全注册之后才能判断
    def is_user_feature(self, feature: "FeatureExtractor"):
        custom_name = getattr(feature.meta, "name", None)
        return custom_name in self.user_registry

    def get_feature(self, name: str):
        return self.registry.get(name, None) or self.user_registry.get(name, None)


class FeatureExtractor:

    def __init__(self, web_data: WebData) -> None:
        self.meta = None
        self.web_data = web_data
        # self.result = None
        # self.execution_time = None
        # self.logger = self.web_data.logger

    def extract(self):
        raise NotImplementedError("Subclasses must implement this method")

    def log_info(self, message):
        # 这里可以实现日志记录逻辑
        print(message)


class OverallExtractionResult:

    def __init__(self, web_data: WebData) -> None:
        self.web_data = web_data
        self.results: list[FeatureExtractionResult] = []  # 存储所有特征提取结果
        self.summary: dict[str, dict[str, dict]] = {}
        # self.logger = self.web_data.logger
        # self.total_features = 0  # 总特征数量
        # self.execution_times = []  # 存储各个提取器的执行时间

    def add_result(self, result: FeatureExtractionResult):
        self.results.append(result)
        # self.total_features += result.feature_count
        # self.execution_times.append(result.execution_time)

    @catch_exceptions
    def save_to_csv(self):
        filename = os.path.join(self.web_data.dir_path, "features.csv")
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # 写入表头
            writer.writerow(["Type", "Feature", "Filename", "Count", "Time(s)"])

            # 写入数据
            try:
                for key, features in self.summary.items():
                    for feature, result in features.items():
                        for filename, res_dict in result.items():
                            count, time = res_dict["count"], res_dict["time"]
                        writer.writerow([key, feature, filename, count, time])
            except Exception as e:
                print(f"Error saving to CSV: {str(e)}")
                GLOBAL_LOGGER.error(f"Error saving to CSV: {str(e)}")

    @catch_exceptions
    @typechecked
    @classmethod
    def load_from_csv(cls, filename) -> dict[str, dict[str, dict]]:
        data = {}

        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)

            # 跳过表头
            next(reader)

            for row in reader:
                type_, feature, filename, count_str, time_str = row
                try:
                    count: int = int(count_str)
                    time = float(time_str)
                except ValueError:
                    GLOBAL_LOGGER.error(f"Invalid data in CSV: {row}, skipping")
                    continue

                if type_ not in data:
                    data[type_] = {}
                if feature not in data[type_]:
                    data[type_][feature] = {}
                data[type_][feature][filename] = {"count": count, "time": time}

                # data[type_][feature] = {"Count": count, "Time": time}

        return data

    def save_to_json(self):
        filename = os.path.join(self.web_data.dir_path, "features.json")
        try:
            with open(filename, mode="w", encoding="utf-8") as file:
                file.write(json.dumps(self.summary, indent=4))
                # res_list = []
                # for res in self.results:
                #     res_dict = {
                #         "Type": res.filetype,
                #         "Feature": res.extractor_name,
                #         "Count": res.feature_count,
                #         "Time(s)": round(res.execution_time, 5),
                #         "AdditionalInfo": res.additional_info,
                #     }
                #     res_list.append(res_dict)
                # file.write(json.dumps(res_list, indent=4))
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")
            GLOBAL_LOGGER.error(f"Error saving to JSON: {str(e)}")

    # async很难，在这里一旦await就报错OSError: [WinError 6] 句柄无效
    # 一旦有exception也会报这个错
    @classmethod
    @typechecked
    @catch_exceptions
    def load_from_json(cls, filename) -> dict:
        # 一旦在这里await就出错OSError: [WinError 6] 句柄无效 怀疑根本不能await
        # print(f"Loading from JSON {filename}")

        with open(filename, mode="r", encoding="utf-8") as file:
            res_dict = json.load(file)

            # res_list = json.load(file)
            # for res in res_list:
            #     result = FeatureExtractionResult(
            #         res["Type"],
            #         res["Feature"],
            #         res["Count"],
            #         res["Time(s)"],
            #         res["AdditionalInfo"],
            #     )
            #     results.append(result)

        return res_dict

    # todo：针对不同类型的特征进行统计
    def do_summary(self):
        for t in FILE_TYPES:
            self.summary[t] = {}
        for result in self.results:
            if result.filetype not in self.summary:
                self.summary[result.filetype] = {}
            try:
                serialized_info = make_serializable(result.info)
                self.summary[result.filetype][result.extractor_name] = serialized_info
            except Exception as e:
                GLOBAL_LOGGER.error(
                    f"Error serializing info of {result.extractor_name}: {str(e)}. ignoring it."
                )

            # {
            #     "Count": result.feature_count,
            #     "Time": round(result.execution_time, 5),
            #     "AdditionalInfo": result.additional_info,
            # }
        self.save_to_csv()
        self.save_to_json()
