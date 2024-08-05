import asyncio
import importlib
import inspect
import os

# 假设 FeatureExtractor 在某个模块中
from src.io.feature_extractor import (
    FeatureExtractionResult,
    FeatureExtractor,
    OverallExtractionResult,
)
from src.io.file_extractor import WebData


def load_extractors_recursive(directory, web_data: WebData, extractors: list):
    print(f"load_extractors_recursive, dir={directory}")
    for root, dirs, files in os.walk(directory):
        print(f"root:{root}, dirs:{dirs}, files:{files}")
        for file in files:
            # 只处理 .py 文件
            if file.endswith(".py") and file != "__init__.py":
                module_name = os.path.splitext(file)[0]
                module_path = os.path.relpath(root, directory).replace(os.sep, ".")
                full_module_name = f"{module_path}.{module_name}"

                # 动态导入模块
                module = importlib.import_module(full_module_name)

                # 查找继承自 FeatureExtractor 的类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, FeatureExtractor)
                        and obj is not FeatureExtractor
                    ):
                        extractors.append(obj(web_data))
        for d in dirs:
            load_extractors_recursive(d, web_data, extractors)

    return extractors


# def load_extractors(directory, web_data: WebData):
#     extractors = []

#     # 遍历目录
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             # 只处理 .py 文件
#             if file.endswith(".py") and file != "__init__.py":
#                 module_name = os.path.splitext(file)[0]
#                 module_path = os.path.relpath(root, directory).replace(os.sep, ".")
#                 full_module_name = f"{module_path}.{module_name}"

#                 # 动态导入模块
#                 module = importlib.import_module(full_module_name)

#                 # 查找继承自 FeatureExtractor 的类
#                 for name, obj in inspect.getmembers(module, inspect.isclass):
#                     if (
#                         issubclass(obj, FeatureExtractor)
#                         and obj is not FeatureExtractor
#                     ):
#                         extractors.append(obj(web_data))

#     return extractors


async def main():
    # 示例用法
    input_directory = "webpages/bilibili/"  # 修改为实际路径
    web_data = WebData(input_directory)
    await web_data.aysnc_load_data()
    await web_data.create_metadata_yaml()
    features_dir = "src/static-features"  # 特征提取脚本目录
    extractors = load_extractors_recursive(features_dir, web_data, [])

    # 调用特征提取方法
    overall_result = OverallExtractionResult(web_data)
    for extractor in extractors:
        try:
            result = extractor.calculate_score()  # 假设有 calculate_score 方法
            overall_result.add_result(result)
        except Exception as e:
            web_data.logger.error(f"Error in {type(extractor).__name__}: {e}")
        print(f"Extractor: {type(extractor).__name__}, Result: {result}")
    overall_result.do_summary()


if __name__ == "__main__":
    asyncio.run(main())
