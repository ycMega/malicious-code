from typing import List, Tuple
from urllib.parse import urlparse

from src.static_features.url import *


class SubDomainURL(URLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "url",
            "SubDomainURL",
            "prophiler",
            "URL是否包含子域：len(domain_parts) > 2",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        url_list = self.web_data.content["url"]
        info_dict = {}
        for h in url_list:
            start_time = time.time()
            res, domain_parts = extract(h)
            info_dict["all_urls"] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": domain_parts,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(url: str) -> Tuple[int, str]:
    """
    检查URL中是否包含子域，并返回结果。
    :param url: 要检查的URL
    :return: 子域存在与否（1或0）和匹配的特征列表
    """
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split(".")

    # 检查是否存在子域
    has_subdomain = 1 if len(domain_parts) > 2 else 0

    return has_subdomain, domain_parts


if __name__ == "__main__":
    # 示例URL
    urls = [
        "http://example.com",
        "http://www.example.com",
        "http://sub.example.com",
        "http://example.co.uk",
        "http://www.example.co.uk",
    ]

    # 检查每个URL中是否包含子域
    for url in urls:
        count, domain_parts = extract(url)
        print(
            f"URL: {url} - Subdomain Present: {count} - Matched Patterns: {domain_parts}"
        )
