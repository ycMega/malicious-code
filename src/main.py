import argparse
import asyncio
import importlib.util
import inspect
import os

from aiologger import Logger
from typeguard import typechecked

from src.io.async_logger import GLOBAL_LOGGER, catch_exceptions, print_logger_info

# 假设 FeatureExtractor 在某个模块中
from src.io.feature_extractor import (
    FeatureExtractionResult,
    FeatureExtractor,
    FeatureRegistry,
    OverallExtractionResult,
)
from src.io.file_extractor import WebData
from src.io.rule import AnalysisResult, OverallAnalysisResult, Rule
from src.modules import (
    analyze_rules,
    extract_features,
    load_extractors_recursive,
    load_rules_recursive,
)

# todo：禁止用户访问无权限的文件夹？


@catch_exceptions
async def main(*args, **kwargs):
    # 示例用法

    if args:
        print("Positional arguments:", args)
    feature_registry = FeatureRegistry()  # 注册表，区分已有提取器和新增提取器
    input_directory = "webpages/bilibili/"  # 修改为实际路径
    web_data = WebData(input_directory)
    try:
        await web_data.aysnc_load_data()
        await web_data.create_metadata_yaml()
    except Exception as e:
        print(f"Exception caught: {e}")
    features_dir = "src/static_features/"  # 特征提取脚本目录
    extractors = load_extractors_recursive(features_dir, web_data, [])
    for extractor in extractors:
        feature_registry.register(extractor, is_user_feature=False)
    if kwargs and "feature_path" in kwargs and kwargs["feature_path"]:
        extractors_added = load_extractors_recursive(
            kwargs["feature_path"], web_data, []
        )
        for extractor_added in extractors_added:
            if feature_registry.is_registered(extractor_added):
                print(
                    f"Error: feature extractor {type(extractor_added).__name__} conflicts with internal extractor"
                )
                return -1
            feature_registry.register(extractor_added, is_user_feature=True)
        extractors.extend(extractors_added)
    overall_results = OverallExtractionResult(web_data)
    await extract_features(overall_result=overall_results, extractors=extractors)

    feature_loaded = await OverallExtractionResult.load_from_json(
        os.path.join(web_data.dir_path, "features.json")
    )
    rules_dir = "src/static_rules/"  # 规则脚本目录
    all_rules = load_rules_recursive(rules_dir, feature_loaded, [])
    if kwargs and "rule_path" in kwargs and kwargs["rule_path"]:
        origin_rule_names = [type(rule).__name__ for rule in all_rules]
        rules_added = load_rules_recursive(kwargs["rule_path"], feature_loaded, [])
        added_rule_names = [type(rule).__name__ for rule in rules_added]
        same_name_added = [
            name for name in added_rule_names if added_rule_names.count(name) > 1
        ]
        if same_name_added:
            print(f"Error: duplicate rule names {same_name_added}")
            return -1
        same_name_with_origin = [
            name for name in added_rule_names if name in origin_rule_names
        ]
        if same_name_with_origin:
            print(
                f"Error: rule names conflict with origin rules {same_name_with_origin}"
            )
            return -1

        all_rules.extend(rules_added)
    overall_analysis_result = OverallAnalysisResult(web_data.dir_path)
    await analyze_rules(overall_analysis_result, all_rules)
    score = overall_analysis_result.judge()
    print(f"Final score: {score}")
    # await GLOBAL_LOGGER.info(f"Final score: {score}")
    await GLOBAL_LOGGER.shutdown()


if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="Process some modules.")
    parser.add_argument(
        "-d",
        "--web_dir",
        type=str,
        help="directory path of webpages to process",
        default="webpages/bilibili/",
    )
    parser.add_argument(
        "-f",
        "--feature",
        type=str,
        help="directory path of feature module to add, can be recursive",
    )
    parser.add_argument(
        "-r",
        "--rule",
        type=str,
        help="directory path of rule module to add, can be recursive",
    )

    args, unknown = parser.parse_known_args()
    if args.web_dir and not os.path.exists(args.web_dir):
        print(f"Web directory path {args.web_dir} not exists.")
    elif args.feature and not os.path.exists(args.feature):
        print(f"Feature module path {args.feature} not exists.")
    elif args.rule and not os.path.exists(args.rule):
        print(f"Rule module path {args.rule} not exists.")
    else:
        asyncio.run(
            main(
                *unknown,
                web_dir=args.web_dir,
                feature_path=args.feature,
                rule_path=args.rule,
            )
        )
