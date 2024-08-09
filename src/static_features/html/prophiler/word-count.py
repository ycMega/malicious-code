from collections import Counter

from src.static_features.html import *


class WordCountHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "WordCountHTML",
            "prophiler",
            "不含tag（包含tag的内容）的词数。词可能按照空格或斜线分隔",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res, words_count = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    # 访问所有标签
    reserved = []
    for tag in soup.find_all(True):
        attrs = " ".join(
            [f'{attr}="{tag[attr]}"' for attr in tag.attrs if attr != "style"]
        )
        if attrs:
            reserved.append(attrs)

        # 提取标签内的文本内容，使用strip()避免提取空白字符
        if tag.string and tag.string.strip():
            reserved.append(tag.string.strip())

        # 清除已经访问的标签内容，避免重复。extract保留后代，decompose不保留后代
        tag.extract()

    text = " ".join(reserved)
    # 统计词数
    # 使用正则表达式分割单词，保留标点符号
    words_with_punctuation = re.findall(r"\b\w+\b|\S", text)

    # 统计单词数量，忽略标点符号
    words = [word for word in words_with_punctuation if word.isalnum()]
    word_count = Counter(words)
    # words = re.findall(r"\b\w+\b", text)
    # print(f"words count={word_count}: {words}")
    total_words = word_count.total()

    return total_words, word_count


if __name__ == "__main__":
    # 示例 HTML/CSS/JS 内容
    example_content = """
    <html>
        <head>
            <style>
                body { font-size: 16px; }
            </style>
            <script>
                console.log("Hello, world!");
            </script>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a sample paragraph.</p>
            <img src="https://www.example.com/image.jpg" alt="Example Image">
            <div>This is a div element.</div>
        </body>
    </html>
    """

    # 运行统计
    total_words, words_count = extract(example_content)
    print(f"Total Words: {total_words}, words count={words_count}")
