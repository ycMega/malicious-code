from bs4 import BeautifulSoup

from src.static_features.html import *


class DoubleDocuments(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "DoubleDocuments",
            "prophiler",
            "统计html，head，title，body tags的重复次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res, presence_of_double_documents = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": presence_of_double_documents,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "html.parser")

    # 计数器
    double_document_count = {"html": 0, "head": 0, "title": 0, "body": 0}

    # 计数。可以这样遍历dict？
    for tag in double_document_count:
        double_document_count[tag] = len(soup.find_all(tag))

    # 检测是否存在多个元素
    presence_of_double_documents = {
        k: v for k, v in double_document_count.items() if v > 1
    }

    return (
        sum(v - 1 for v in presence_of_double_documents.values()),
        presence_of_double_documents,
    )  # 返回重复次数


if __name__ == "__main__":
    # 测试示例
    html_content = """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Hello World</h1>
        </body>
        <head>
            <title>Another Title</title>
        </head>
        <body>
            <p>Another body content.</p>
        </body>
    </html>
    """
    double_documents = extract(html_content)
    if double_documents:
        print("Presence of double documents:")
        for element, count in double_documents.items():
            print(f"{element}: {count}")
    else:
        print("No double documents found.")
