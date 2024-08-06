import asyncio
import importlib.util
import inspect
import os

from annotated_types import IsInfinite
from typeguard import typechecked

from src.io.async_logger import catch_exceptions, print_logger_info, GLOBAL_LOGGER

# 假设 FeatureExtractor 在某个模块中
from src.io.feature_extractor import (
    FeatureExtractionResult,
    FeatureExtractor,
    OverallExtractionResult,
)
from src.io.file_extractor import WebData
from src.static_features.css import CSSExtractor
from src.static_features.html import HTMLExtractor
from src.static_features.js import JSExtractor
from src.static_features.url import URLExtractor


def load_rule_module(rule_path: str):
    base_name = os.path.splitext(rule_path)[0]
    rule_name = base_name.replace("/", ".").replace("\\", ".")
    # rule_name = os.path.splitext(os.path.basename(rule_path))[0]
    # 创建一个模块的规范（spec），指定模块名称和路径
    spec = importlib.util.spec_from_file_location(rule_name, rule_path)
    if spec is None or spec.loader is None:
        return None
    # 创建模块对象
    module = importlib.util.module_from_spec(spec)
    # 执行模块。加载其内容
    spec.loader.exec_module(module)
    return module


def load_extractors_recursive(directory, web_data: WebData, extractors: list):
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 只处理 .py 文件
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file)
                # module_name = os.path.splitext(file)[0]
                # module_path = os.path.relpath(root, directory).replace(os.sep, ".")
                # full_module_name = f"{module_path}.{module_name}"
                # print(f"full module name:{full_module_name}")
                # 动态导入模块
                # module = importlib.import_module(full_module_name)
                module = load_rule_module(module_path)
                if module is None:
                    continue

                # 查找继承自 FeatureExtractor 的类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, FeatureExtractor) and obj not in (
                        FeatureExtractor,
                        HTMLExtractor,
                        CSSExtractor,
                        JSExtractor,
                        URLExtractor,
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


@catch_exceptions
async def main():
    # 示例用法
    input_directory = "webpages/bilibili/"  # 修改为实际路径
    web_data = WebData(input_directory)
    try:
        await web_data.aysnc_load_data()
        await web_data.create_metadata_yaml()
    except Exception as e:
        print(f"Exception caught: {e}")
    features_dir = "src/static_features/"  # 特征提取脚本目录
    extractors = load_extractors_recursive(features_dir, web_data, [])

    # 调用特征提取方法
    overall_result = OverallExtractionResult(web_data)
    for extractor in extractors:
        try:
            # 尝试添加type checked wrapper但失败了
            # if hasattr(extractor, "calculate_score"):
            #     original_func = extractor.calculate_score

            #     @typechecked
            #     def wrapped_func(
            #         self,
            #     ) -> FeatureExtractionResult:  # 根据需要定义参数类型
            #         return original_func(self)

            #     extractor.calculate_score = wrapped_func  # 替换原方法
            print("Extractor:", type(extractor).__name__)
            result = extractor.calculate_score()  # 假设有 calculate_score 方法
            if result is not None and isinstance(result, FeatureExtractionResult):
                # 是正确的返回值，接下来检查规则是否有效
                if result.feature_count >= 0:
                    overall_result.add_result(result)
            else:
                print(f"Error in {type(extractor).__name__}: Invalid result")
                # print_logger_info(web_data.logger)
                try:
                    pass  # 下面的语句会莫名报错[WinError 6] 句柄无效。即使之前输出的logger info没看出异常
                    # await web_data.logger.error(
                    #     f"Error in {type(extractor).__name__}: Invalid result"
                    # )
                except Exception as e:
                    print(f"Error in {type(extractor).__name__}: {str(e)}")
        except Exception as e:
            await GLOBAL_LOGGER.error(f"Error in {type(extractor).__name__}: {e}")
        # print(f"Extractor: {type(extractor).__name__}, Result: {result}")
    await overall_result.do_summary()


if __name__ == "__main__":
    asyncio.run(main())
