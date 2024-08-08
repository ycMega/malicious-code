import argparse
import asyncio
import importlib.util
import inspect
import os
import time

from typeguard import typechecked

from src.io.async_logger import GLOBAL_LOGGER, catch_exceptions

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
def main(*args, **kwargs):
    if args:
        print("Positional arguments:", args)
    feature_registry = FeatureRegistry()  # 注册表，区分已有提取器和新增提取器
    input_directory = "webpages/bilibili"  # 修改为实际路径
    GLOBAL_LOGGER.remove()  # 移除默认处理器
    GLOBAL_LOGGER.add(
        f"logs/{os.path.basename(input_directory)}.log",
        mode="w",  # 覆盖原文件
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        enqueue=True,  # 线程安全？
    )
    web_data = WebData(input_directory)

    start_time = time.time()
    GLOBAL_LOGGER.info(
        f"Loading web data from {input_directory} and creating metadata.yaml......"
    )
    try:
        web_data.aysnc_load_data()
        metadata = web_data.create_metadata_yaml()
        info_list = [
            f"url:{metadata['website']['url']}",
            f"crawled time: {metadata['website']['crawled_at']}",
            f"{metadata['content_info']['html']['count']} HTML files:{[x['filename'] for x in metadata['content_info']['html']['meta']]}",
            f"{metadata['content_info']['js']['count']} JavaScript files:{[x['filename'] for x in metadata['content_info']['js']['meta']]}",
            f"{metadata['content_info']['css']['count']} CSS files:{[x['filename'] for x in metadata['content_info']['css']['meta']]}",
        ]
        for info in info_list:
            GLOBAL_LOGGER.info(info)

    except Exception as e:
        GLOBAL_LOGGER.error(f"Exception caught: {e}")
        print(f"Exception caught: {e}")
    # elapsed_time_ms =
    GLOBAL_LOGGER.info(
        f"Loading web data finished. Time: {((time.time() - start_time) * 1000):.2f}ms"
    )
    features_dir = "src/static_features/"  # 特征提取脚本目录

    start_time = time.time()
    GLOBAL_LOGGER.info("=" * 50)
    GLOBAL_LOGGER.info(f"Loading feature extractors from {features_dir}......")
    extractors = load_extractors_recursive(features_dir, web_data, [])
    for extractor in extractors:
        feature_registry.register(extractor, is_user_feature=False)
    if kwargs and "feature_path" in kwargs and kwargs["feature_path"]:
        GLOBAL_LOGGER.info(
            f"Loading additional feature extractors from {kwargs['feature_path']}......"
        )
        extractors_added = load_extractors_recursive(
            kwargs["feature_path"], web_data, []
        )
        for extractor_added in extractors_added:
            if feature_registry.is_registered(extractor_added):
                GLOBAL_LOGGER.error(
                    f"Error: feature extractor {type(extractor_added).__name__} conflicts with internal extractor. Exiting."
                )
                return -1
            feature_registry.register(extractor_added, is_user_feature=True)
        extractors.extend(extractors_added)
    GLOBAL_LOGGER.info("-" * 50)
    GLOBAL_LOGGER.info(
        f"Finished loading feature extractors. Time: {((time.time() - start_time) * 1000):.2f}ms"
    )
    overall_results = OverallExtractionResult(web_data)
    start_time = time.time()
    GLOBAL_LOGGER.info("=" * 50)
    GLOBAL_LOGGER.info("Extracting features......")
    extract_features(overall_result=overall_results, extractors=extractors)

    # 下面是规则执行
    feature_loaded = OverallExtractionResult.load_from_json(
        os.path.join(web_data.dir_path, "features.json")
    )

    start_time = time.time()
    rules_dir = "src/static_rules/"  # 规则脚本目录
    GLOBAL_LOGGER.info("*" * 50)
    GLOBAL_LOGGER.info(f"Now start loading rules from {rules_dir}......")
    all_rules = load_rules_recursive(rules_dir, feature_loaded, [])
    if kwargs and "rule_path" in kwargs and kwargs["rule_path"]:
        GLOBAL_LOGGER.info(f"Loading additional rules from {kwargs['rule_path']}......")
        origin_rule_names = [type(rule).__name__ for rule in all_rules]
        rules_added = load_rules_recursive(kwargs["rule_path"], feature_loaded, [])
        added_rule_names = [type(rule).__name__ for rule in rules_added]
        same_name_added = [
            name for name in added_rule_names if added_rule_names.count(name) > 1
        ]
        if same_name_added:
            GLOBAL_LOGGER.error(
                f"Error: duplicate rule names {same_name_added}. Exiting."
            )
            return -1
        same_name_with_origin = [
            name for name in added_rule_names if name in origin_rule_names
        ]
        if same_name_with_origin:
            GLOBAL_LOGGER.error(
                f"Error: rule names conflict with origin rules {same_name_with_origin}. Exiting."
            )
            return -1

        all_rules.extend(rules_added)
    GLOBAL_LOGGER.info(
        f"Finished loading rules. Time: {((time.time() - start_time) * 1000):.2f}ms"
    )
    overall_analysis_result = OverallAnalysisResult(web_data.dir_path)
    GLOBAL_LOGGER.info("=" * 50)
    GLOBAL_LOGGER.info("Analyzing rules......")
    analyze_rules(overall_analysis_result, all_rules)
    score_dict = overall_analysis_result.judge()
    GLOBAL_LOGGER.info("-" * 50)
    GLOBAL_LOGGER.info("Final score: ")
    max_filename_len = max([len(filename) for filename in score_dict])
    for filename, score in score_dict.items():
        GLOBAL_LOGGER.info(f"{filename:<{max_filename_len+1}}: {score:<.3f}")
    # GLOBAL_LOGGER.info(f"Final score: {score}")
    GLOBAL_LOGGER.info("All finished.")
    print("All finished.")


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

        main(
            *unknown,
            web_dir=args.web_dir,
            feature_path=args.feature,
            rule_path=args.rule,
        )
