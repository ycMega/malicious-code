from bs4 import BeautifulSoup
from cssutils import CSSParser

# most of the tags that contain malicious sources, are put in the page as hidden tag


def calculate_score(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "lxml")
    # 查找隐藏元素的规则
    # hidden_classes = []
    # for rule in stylesheet:
    #     if rule.type == rule.STYLE_RULE:
    #         if (
    #             "display: none" in rule.style.cssText
    #             or "visibility: hidden" in rule.style.cssText
    #         ):
    #             selectors = rule.selectorText.split(",")
    #             hidden_classes.extend(selectors)
    # 定义可疑标签列表
    suspicious_tags = [
        "area",
        "img",
        "source",
        "sound",
        "video",
        "body",
        "applet",
        "object",
        "embed",
        "iframe",
        "frame",
        "frameset",
    ]
    hidden_script_patterns = [
        "style.visibility = 'hidden'",
        "style.display = 'none'",
        "setAttribute('visibility','hidden')",
        "setAttribute('display','none')",
        "setAttribute('width','0')",
        "setAttribute('height','0')",
        "attr('display', 'none')",
        "attr('visibility', 'hidden')",
        "attr('width', '0')",
        "attr('height', '0')",
    ]
    hidden_style_patterns = [
        "width: 0px",
        "height: 0px",
        "display: none",
        "visibility: hidden",
    ]

    # 提取可疑标签
    suspicious_elements = soup.find_all(suspicious_tags)

    # 提取script和style标签
    script_tags = soup.find_all("script")
    style_tags = soup.find_all("style")

    # 初始化计数器
    hidden_count = 0

    # 检测可疑标签和script标签内部HTML是否包含隐藏模式
    for tag in suspicious_elements + script_tags:
        print(f"tag:{tag}")
        for pattern in hidden_script_patterns:
            if pattern in tag.text:
                print(f"script pattern:{pattern}")
                hidden_count += 1
                # break  # 匹配到一个模式后，跳出内层循环

    # 检测style标签是否包含隐藏模式
    for style in style_tags:
        print(f"style tag:{style}")
        for pattern in hidden_style_patterns:
            if pattern in style.text:
                print(f"style pattern:{pattern}")
                hidden_count += 1
                # break  # 匹配到一个模式后，跳出内层循环

    return hidden_count


# 示例HTML内容
html_content = """
<html>
<head>
<style>
.hidden { width: 0px; }
.invisible { visibility: hidden; }
.none { display: none; }
</style>
</head>
<body>
<div class="hidden">Invisible Content</div>
<div class="invisible">Invisible Content</div>
<div class="none">Invisible Content</div>
<script>
document.getElementById("someId").style.visibility = 'hidden';
document.getElementById("anotherId").style.display = 'none';
</script>
</body>
</html>
"""

css_text = """
.hidden { display: none; }
.invisible { visibility: hidden; }
"""

# 解析CSS
css_parser = CSSParser()
stylesheet = css_parser.parseString(css_text)

# 调用函数
result = calculate_score(html_content)
print(result)
# hidden_elements = soup.find_all(
#     style=lambda value: value and "display:none" in value
# )
# score = len(hidden_elements)  #  * 20
# return score
