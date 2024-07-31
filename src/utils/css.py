from bs4 import BeautifulSoup


def extract_css_features(html_content: str):
    # 发送请求获取网页内容
    soup = BeautifulSoup(html_content, "lxml")

    # 提取内联CSS
    inline_styles = []
    for style in soup.find_all("style"):
        inline_styles.append(style.string)

    # 提取外部CSS链接
    external_styles = []
    for link in soup.find_all("link", rel="stylesheet"):
        external_styles.append(link["href"])

    # 提取所有元素的CSS样式
    css_features = []
    for element in soup.find_all(True):  # True表示所有标签
        styles = element.get("style")
        if styles:
            css_features.append(styles)
            # css_features[element.name] = styles

    return inline_styles, external_styles, css_features


if __name__ == "__main__":
    # 示例用法
    url = "http://example.com"  # 替换为目标网页的URL
    css_features = extract_css_features(url)
    print(css_features)
