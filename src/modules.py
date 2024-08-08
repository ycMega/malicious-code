import importlib.util
import inspect
import os
import time

from src.io.async_logger import GLOBAL_LOGGER

# 假设 FeatureExtractor 在某个模块中
from src.io.feature_extractor import (
    FeatureExtractionResult,
    FeatureExtractor,
    FeatureRegistry,
    OverallExtractionResult,
)
from src.io.file_extractor import WebData
from src.io.rule import AnalysisResult, OverallAnalysisResult, Rule
from src.static_features.css import CSSExtractor
from src.static_features.html import HTMLExtractor
from src.static_features.js import JSExtractor
from src.static_features.url import URLExtractor


def load_module(module_path: str):
    base_name = os.path.splitext(module_path)[0]
    module_name = base_name.replace("/", ".").replace("\\", ".")
    # rule_name = os.path.splitext(os.path.basename(rule_path))[0]
    # 创建一个模块的规范（spec），指定模块名称和路径
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        return None
    # 创建模块对象
    module = importlib.util.module_from_spec(spec)
    # 执行模块。加载其内容
    spec.loader.exec_module(module)
    return module


def load_extractors_recursive(directory: str, web_data: WebData, extractors: list):
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
                module = load_module(module_path)
                if module is None:
                    continue

                # 查找继承自 FeatureExtractor 的类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(
                        obj, (HTMLExtractor, CSSExtractor, JSExtractor, URLExtractor)
                    ) and obj not in (
                        HTMLExtractor,
                        CSSExtractor,
                        JSExtractor,
                        URLExtractor,
                    ):
                        extractors.append(obj(web_data))
        for d in dirs:
            load_extractors_recursive(d, web_data, extractors)

    return extractors


def extract_features(
    overall_result: OverallExtractionResult, extractors: list[FeatureExtractor]
):
    # 调用特征提取方法
    for extractor in extractors:
        try:
            start_time = time.time()
            result = extractor.calculate_score()  # 假设有 calculate_score 方法
            if result is not None and isinstance(result, FeatureExtractionResult):
                # 是正确的返回值，接下来检查规则是否有效
                # if result.feature_count >= 0:
                overall_result.add_result(result)
                GLOBAL_LOGGER.info(
                    f"Extractor Finished in {((time.time() - start_time) * 1000):.2f} ms: {type(extractor).__name__}. "
                )
            else:
                GLOBAL_LOGGER.error(
                    f"Error in {type(extractor).__name__}: Invalid result"
                )
                # print_logger_info(web_data.logger)
                try:
                    pass  # 下面的语句会莫名报错[WinError 6] 句柄无效。即使之前输出的logger info没看出异常
                    # web_data.logger.error(
                    #     f"Error in {type(extractor).__name__}: Invalid result"
                    # )
                except Exception as e:
                    GLOBAL_LOGGER.error(
                        f"Error in {type(extractor).__name__}: {str(e)}"
                    )
        except Exception as e:
            GLOBAL_LOGGER.error(f"Error in {type(extractor).__name__}: {e}")
        # print(f"Extractor: {type(extractor).__name__}, Result: {result}")
    GLOBAL_LOGGER.info(
        "Feature extraction finished. Starting writing results to file......"
    )
    start_time = time.time()
    overall_result.do_summary()
    GLOBAL_LOGGER.info(
        f"Writing to file finished. Time: {((time.time() - start_time) * 1000):.2f}ms"
    )


def load_rules_recursive(directory: str, feature_dict: dict, rules: list):
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 只处理 .py 文件
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file)
                module = load_module(module_path)
                if module is None:
                    continue

                # 查找继承自 FeatureExtractor 的类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, (Rule)) and obj not in (Rule,):
                        rules.append(obj(feature_dict=feature_dict))
        for d in dirs:
            load_rules_recursive(d, feature_dict, rules)

    return rules


def analyze_rules(overall_analysis_result: OverallAnalysisResult, rules: list[Rule]):
    for rule in rules:
        try:
            start_time = time.time()
            result = rule.analyze()
            if result is not None and isinstance(result, AnalysisResult):
                overall_analysis_result.add_result(result)
                GLOBAL_LOGGER.info(
                    f"Rule Finished: {type(rule).__name__}. Time: {((time.time() - start_time) * 1000):.2f}ms"
                )
            else:
                GLOBAL_LOGGER.error(f"Error in {type(rule).__name__}: Invalid result")
        except Exception as e:
            GLOBAL_LOGGER.error(f"Error in {type(rule).__name__}: {e}")
    overall_analysis_result.do_summary()

    # print(f"Extractor: {type(extractor).__name__}, Result: {result}")
    # overall_result.do_summary()
