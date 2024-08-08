import asyncio
import glob
import json
import os
import time
from collections import OrderedDict
from datetime import datetime
from math import e

import yaml
from typeguard import typechecked

from src.io.async_logger import GLOBAL_LOGGER, catch_exceptions
from src.utils import url
from src.utils.utils import HAR_FILE, METADATA_FILE, extract_urls


class SafeDumperWithOrder(yaml.SafeDumper):
    pass


def dict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items()
    )


SafeDumperWithOrder.add_representer(dict, dict_representer)


# 在初始化之后，必须调用async_load_data()方法来加载数据
class HARProcessor:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.har_data = None
        self.page_time = None
        self.url = None
        self.total_requests = -1
        self.response_times = []
        # self.logger = GLOBAL_LOGGER

    @typechecked
    @catch_exceptions
    def load_data(self) -> bool:
        if not os.path.exists(os.path.join(self.dir_path, HAR_FILE)):
            GLOBAL_LOGGER.info(f"No HAR file found at {self.dir_path}")
            return False
        try:
            har_path = os.path.join(self.dir_path, HAR_FILE)
            with open(har_path, "r", encoding="utf-8") as file:
                self.har_data = json.load(file)
            return True
        except Exception as e:
            GLOBAL_LOGGER.error(f"Error loading HAR file: {e}")
            return False

    @typechecked
    def extract_url(self) -> str | None:
        entries = self.har_data["log"]["pages"]
        if entries and len(entries) > 0:
            # 获取第一个页面的时间
            self.url = entries[0]["title"]
        return self.url

    @typechecked
    def extract_page_time(self) -> str | None:
        # Q：存在不同的har格式吗
        entries = self.har_data["log"]["pages"]
        if entries and len(entries) > 0:
            # 获取第一个页面的时间
            self.page_time = entries[0]["startedDateTime"]
        return self.page_time

    def extract_total_requests(self) -> int:
        # 提取总请求数
        self.total_requests = len(self.har_data["log"]["entries"])
        return self.total_requests

    def extract_response_time(self) -> list:
        self.response_times = []
        for entry in self.har_data["log"]["entries"]:
            self.response_times.append(entry["time"])
        return self.response_times

    def format_folder_name(self, index):
        if self.page_time:
            # 解析时间
            dt = datetime.fromisoformat(self.page_time[:-1])  # 去掉最后的 'Z'
            folder_name = f"{dt.strftime('%Y%m%d')}_{index}"
            return folder_name
        return None

    def extract_http_requests(self) -> dict:
        if not self.har_data:
            return {}
        total_requests = self.extract_total_requests()
        response_times = self.extract_response_time()
        crawled_time = self.extract_page_time()
        return {
            "total": total_requests,
            "average_response_time": (
                sum(response_times) / total_requests if total_requests > 0 else 0
            ),
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "crawl_time": crawled_time,
        }


# 示例用法
# har_processor = HARProcessor("example.har")
# har_processor.extract_page_time()

# folder_name = har_processor.format_folder_name(1)  # 假设 index 为 1
# print(folder_name)  # 输出格式: yyyymmdd_1


# 在初始化之后，必须调用async_load_data()方法来加载数据。其中也进行了HARProcessor的异步初始化
class WebData:
    def __init__(self, dir_path: str):
        self.dir_path: str = dir_path
        self.metadata: dict | None = None
        self.url: str | None = None
        self.content: dict[str, list[dict[str, str]]] | None = None
        self.har_processor = HARProcessor(dir_path)
        # self.logger = Logger.with_default_handlers(level="DEBUG")

    # 在其中执行需要涉及到logger的内容
    @catch_exceptions
    def aysnc_load_data(self):
        if self.har_processor:
            self.har_processor.load_data()
        try:
            metadata_path = os.path.join(self.dir_path, METADATA_FILE)
            with open(metadata_path, "r", encoding="utf-8") as file:
                self.metadata = yaml.safe_load(file)
        except Exception as e:
            GLOBAL_LOGGER.error(f"Error loading metadata.yaml: {e}")

    def extract_url_from_meta(self) -> str:
        # 从metadata.yaml中提取URL
        return self.metadata.get("website", {}).get("url", "")

    def extract_url_from_har(self):
        # 从HAR文件中提取URL
        return self.har_processor.extract_url() if self.har_processor else None

    # def extract_content_sizes(self):
    #     # 获取各类内容的大小
    #     type_list = ["html", "css", "js"]
    #     content_sizes = {}
    #     for file in glob.glob(os.path.join(self.dir_path, "*")):
    #         file_type = os.path.splitext(file)[-1][1:]  # 获取文件扩展名
    #         if file_type not in type_list:
    #             continue
    #         file_name = os.path.basename(file)
    #         content_sizes[file_type] = os.path.getsize(file)
    #     return content_sizes

    # 读取文件填入content，返回每种文件的数量
    @catch_exceptions
    @typechecked
    def load_files(self) -> dict[str, dict]:
        file_types = ["html", "css", "js"]
        files_content: dict[str, list[dict[str, str]]] = {}
        files_meta: dict[str, dict] = {}
        url_list = []
        for file_type in file_types:
            folder_path = os.path.join(self.dir_path, file_type)
            files_meta[file_type] = {"count": 0, "meta": []}
            files_content[file_type] = []
            # 检查文件夹是否存在
            if not os.path.exists(folder_path):
                GLOBAL_LOGGER.error(f"文件夹 {folder_path} 不存在")
                continue
                # raise FileNotFoundError(f"文件夹 {folder_path} 不存在")

            for filename in os.listdir(folder_path):
                # if filename.endswith((".html", ".css", ".js")):  # 根据需要的文件类型过滤
                if filename.endswith(f".{file_type}"):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            content = file.read()
                            url_list.extend(extract_urls(content))
                            files_content[file_type].append(
                                {"filename": filename, "content": content}
                            )
                            files_meta[file_type]["count"] += 1
                            files_meta[file_type]["meta"].append(
                                {
                                    "filename": filename,
                                    "size": os.path.getsize(file_path),
                                }
                            )
                    except Exception as e:
                        GLOBAL_LOGGER.error(f"Error loading {file_path}: {e}")
            # 将所有URL添加到列表中
            url_list_set = list(set(url_list))
            files_content["url"] = url_list_set
            files_meta["url"] = {"count": len(url_list_set), "meta": url_list_set}

        self.content = files_content
        return files_meta

    @catch_exceptions
    @typechecked
    def create_metadata_yaml(self) -> dict:

        url = (
            self.extract_url_from_har()
            if self.har_processor
            else self.extract_url_from_meta()
        )

        files_meta = self.load_files()
        http_requests = (
            self.har_processor.extract_http_requests() if self.har_processor else {}
        )

        metadata = {
            "website": {
                "url": url,
                "crawled_at": http_requests["crawl_time"] if http_requests else "",
                "website_name": "ExampleSite",  # 可以根据实际情况修改
            },
            "content_info": files_meta,
            "http_requests": http_requests,
            "robots_protocol": "Disallow: /private/",  # 根据需要修改
            "sitemap": f"{url}/sitemap.xml",  # 假设sitemap在根目录
            "ssl_certificate": {
                "issuer": "Certificate Authority",  # 可以根据实际情况修改
                "validity": "2024-01-01 to 2025-01-01",  # 根据需要修改
            },
            "notes": "This is the initial crawl of the website for feature extraction.",
        }

        # 将结果写入YAML文件
        metadata_path = os.path.join(self.dir_path, "metadata.yaml")
        with open(metadata_path, "w", encoding="utf-8") as file:
            yaml.dump(metadata, file, allow_unicode=True, Dumper=SafeDumperWithOrder)
        return metadata


# def extract_crawled_time():
#     # 获取当前时间作为爬取时间
#     return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@catch_exceptions
def main():
    # 示例用法
    input_directory = "webpages/bilibili/"  # 修改为实际路径
    web_data = WebData(input_directory)
    web_data.aysnc_load_data()
    web_data.create_metadata_yaml()


if __name__ == "__main__":
    main()
