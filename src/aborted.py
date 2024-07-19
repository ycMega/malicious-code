"""
this file is not used in the project
"""

import argparse
import html
import json
import os
import time

import requests
from bs4 import BeautifulSoup
from genericpath import isdir
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# 定义恶意行为检测规则
MALICIOUS_RULES = [
    {"type": "inline_js", "pattern": "<script>", "score": 5},
    {"type": "eval_function", "pattern": "eval\\(", "score": 10},
    {"type": "data_uri", "pattern": "data:", "score": 3},
    {"type": "remote_resource", "pattern": 'src="http://', "score": 2},
    # 添加更多规则...
]


# def check_malicious(soup: BeautifulSoup, rules: list) -> int:
#     score = 0
#     script_count = len(soup.find_all("script"))
#     src_count = len([tag for tag in soup.find_all(src=True)])
#     href_count = len([tag for tag in soup.find_all(href=True)])
#     for rule in rules:
#         pattern = rule["pattern"]
#         score += rule["score"] * content.count(pattern)
#     return score


# 实际上不都是js？
def save_js(soup: BeautifulSoup, path: str):
    # 查找并打印所有<script>标签的内容
    for script_tag in soup.find_all("script"):
        src = script_tag.get("src")
        if src:
            # 如果<script>标签有src属性，尝试获取并打印外部JS文件的内容
            if src.startswith("//"):
                src = "https:" + src
            js_response = requests.get(src, timeout=5)
            with open(
                f"path/{src.split('/')[-1]}", "w", encoding="utf-8"
            ) as f:  # 不需要.js后缀，因为原文件已经有后缀了？
                f.write(js_response.text)
        else:
            # 打印内联JavaScript代码
            with open(f"{path}/inline_js.txt", "a", encoding="utf-8") as f:
                f.write(script_tag.text)


def analyze_webpage(args: argparse.Namespace) -> int:
    try:
        url = args.url
        start_time = time.time()
        # page_source = get_full_page_content(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15"
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        }
        # with open("src/config.json", "r", encoding="utf-8") as f:
        #     config = json.load(f)
        # headers["cookie"] = config["cookie"]
        # response = requests.get(url, headers=headers, timeout=5)
        response = requests.get(url, timeout=5)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        print(soup.prettify())
        # save_js(soup, "webpages/bilibili")
        html_content = response.text
        with open("webpages/bilibili/bilibili.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        # print(f"response.text={html_content}")
        soup = BeautifulSoup(html_content, "html.parser")

        content = str(soup)
        # print(f"content={content}")
        scores = calculate_total_scores(soup, RULES_PATH)
        # score = check_malicious(content, MALICIOUS_RULES)
        print(f"Analyzed {url} in {time.time() - start_time:.2f}s")
        print(f"Scores: {scores}")
        return scores["total_score"]
    except requests.RequestException as e:
        print(f"Error fetching url {url}: {e}")
        return -1


# 使用示例

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze a webpage for malicious content"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://www.bilibili.com",
        help="The URL of the webpage to analyze.",
    )
    parser.add_argument(
        "-th",
        "--THRESHOLD",
        type=int,
        default=15,
        help="The threshold for malicious content detection.",
    )
    parser.add_argument(
        "-ti",
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout for the webpage request in seconds.",
    )

    args = parser.parse_args()
    print("args=", args)
    # url = "https://www.zhihu.com" #您当前请求存在异常，暂时限制本次访问 code=40362
    url = args.url
    score = analyze_webpage(args)
    print(f"Malicious score for {url}: {score}")

    # 根据分数设定阈值
    THRESHOLD = args.THRESHOLD
    if score > THRESHOLD:
        print("The webpage is potentially malicious.")
    else:
        print("The webpage is likely benign.")


def get_full_page_content(url):
    # 设置ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    # 访问网页
    driver.get(url)
    # 等待一段时间，让JavaScript内容加载完成
    time.sleep(5)  # 根据需要调整等待时间
    # 获取页面源代码
    page_source = driver.page_source
    # 关闭浏览器
    driver.quit()
    return page_source

    # # 提取特定的html标签，例如所有<a>
    # links = soup.find_all("a")
    # for link in links:
    #     print(link.get("href"))
    # # CSS通常位于<link>标签中，指向外部CSS文件，或者嵌入在<style>标签内：
    # css_links = soup.find_all("link", rel="stylesheet")
    # for css in css_links:
    #     print(css.get("href"))
    # embedded_css = soup.find_all("style")
    # for css in embedded_css:
    #     print(css.string)

    # # 其他媒体文件
    # images = soup.find_all("img")
    # for img in images:
    #     print(img.get("src"))
    # # 其他媒体文件，如GIFs，可以通过寻找特定的扩展名来过滤
    # media_files = soup.find_all("img", src=lambda src: src.endswith(".gif"))
    # for media in media_files:
    #     print(media.get("src"))
    # 检查网页中的恶意代码
