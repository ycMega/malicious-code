import re

from bs4 import BeautifulSoup


def remove_css_comments(css_content):
    # 移除 /**/ 包裹的注释
    comment_pattern = re.compile(r"/\*.*?\*/", re.DOTALL)
    return comment_pattern.sub("", css_content)


def remove_html_comments(html_content):
    # 移除 <!-- --> 包裹的注释
    comment_pattern = re.compile(r"<!--.*?-->", re.DOTALL)
    return comment_pattern.sub("", html_content)


def css_rules_listing(css_content):
    # 移除注释
    css_content = remove_css_comments(css_content)

    # 匹配各种可能的选择器开头，并匹配整个规则块
    # css_rule_pattern = re.compile(r"([a-zA-Z.#*[\]:>+~][^{]+)\{([^}]+)\}")
    css_rule_pattern = re.compile(r"([^{]+?)\{([^}]*)\}")
    css_rules = css_rule_pattern.findall(css_content)

    # 将匹配到的 CSS 规则存储在一个列表中
    rules = [
        f"{rule[0].strip()}" + "{" + f"{rule[1].strip()}" + "}" for rule in css_rules
    ]

    return rules


def extract_css_features(html_content):
    html_content = remove_html_comments(html_content)
    # 提取 <style> 标签中的 CSS
    # css_rule_pattern = re.compile(r"([^{]+)\{([^}]+)\}")
    css_rule_pattern = re.compile(
        r"(@[^{]+|[^{]+)\{([^}]+)\}", re.DOTALL
    )  # dotall处理多行CSS规则
    style_tag_pattern = re.compile(
        r"<style.*?>(.*?)</style>", re.DOTALL | re.IGNORECASE
    )
    tag_list = style_tag_pattern.findall(html_content)
    tag_rule_list = []
    for tag in tag_list:
        matches = css_rule_pattern.findall(tag)
        tag_rule_list.extend(matches)

    style_tag_list = [
        rule[0].strip() + "{" + rule[1].strip() + "}"
        for rule in tag_rule_list  # strip是必要的吗
    ]

    # 提取 style 属性中的内联 CSS
    # r'style=("([^"]*)"|\'([^\']*)\')'
    # 注意善用捕获组！括号不能随便打！\1对应的是捕获组！
    style_attr_pattern = re.compile(
        r'style=(["\'])(.*?)\1', re.DOTALL | re.IGNORECASE
    )  # r'style=(["\'])(.*?)\1'
    attr_list = [attr[1] for attr in style_attr_pattern.findall(html_content)]
    # print(f"html content:{html_content}, attr list:{attr_list}")

    # 提取 <link> 标签中的外部 CSS 文件
    link_tag_pattern = re.compile(r'<link.*?href=["\'](.*?\.css)["\']', re.IGNORECASE)
    link_tag_css = link_tag_pattern.findall(html_content)  # 暂不考虑

    # 合并所有提取的样式
    res_list = style_tag_list + attr_list
    return res_list

    # # 提取内联CSS
    # inline_styles = []
    # for style in soup.find_all("style"):
    #     inline_styles.append(style.string)

    # # 提取外部CSS链接
    # external_styles = []
    # for link in soup.find_all("link", rel="stylesheet"):
    #     external_styles.append(link["href"])

    # # 提取所有元素的CSS样式
    # css_features = []
    # for element in soup.find_all(True):  # True表示所有标签
    #     styles = element.get("style")
    #     if styles:
    #         css_features.append(styles)
    #         # css_features[element.name] = styles

    # return inline_styles, external_styles, css_features


if __name__ == "__main__":
    # 示例用法
    html_content = """
    <div style="color: blue; font-size: 14px;">
        <p style="font-weight: bold;">Hello, World!</p>
        <script type="text/javascript">
            // 一些JavaScript代码
            var style = "background-color: yellow;";
        </script>
        <span style="text-decoration: underline; color: red;">Test</span>
        <span style="border: 1px solid #000; font-family: 'Times New Roman', Times, serif;">Special characters.</span>
    </div>
    <div style="display: flex;">
        <div style="flex: 1;">Flex item 1</div>
        <div style="flex: 2; color: blue;">Flex item 2</div>
    </div>
    """
    css_raw = """
    /* 样式规则 1 */
    body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
    }

    /* 样式规则 2 */
    h1 {
        color: #333;
        font-size: 24px;
        text-align: center;
    }

    /* 样式规则 3 */
    p {
        color: #666;
        line-height: 1.5;
        margin: 10px 0;
    }

    /* 样式规则 4 */
    a {
        color: blue;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    /* 样式规则 5 */
    .container {
        width: 80%;
        margin: 0 auto;
        padding: 20px;
        background-color: #f4f4f4;
    }/* 样式规则 6 */
    #header {
        background-color: #333;
        color: white;
        padding: 10px 0;
        text-align: center;
    }

    /* 样式规则 7 */
    .navbar {
        display: flex;
        justify-content: space-around;
        background-color: #444;
    }

    .navbar a {
        color: white;
        padding: 10px;
    }

    .navbar a:hover {
        background-color: #555;
    }
    """
    css_list = extract_css_features(html_content)
    ori_css_list = css_rules_listing(css_raw)
    print(f"css list len={len(css_list)}:", css_list)
    print("ori css list len=", len(ori_css_list), ori_css_list)
