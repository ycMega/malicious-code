import html

from bs4 import BeautifulSoup

# some HTML5 tags are capable of loading files in themselves


def calculate_score(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "lxml")
    tags_to_check = ["embed", "video", "audio", "track", "source"]
    external_or_long_src_count = 0
    hidden_tags_count = 0

    for tag_name in tags_to_check:
        for tag in soup.find_all(tag_name):
            # 检查src属性
            src = tag.get("src", "")
            if src.startswith(("http://", "https://")) or len(src) > 150:
                external_or_long_src_count += 1

            # 检查是否隐藏
            if tag_name in ["video", "audio"] and (
                tag.get("width") == "0" or tag.get("height") == "0"
            ):
                hidden_tags_count += 1
            elif tag_name in ["embed", "track", "source"] and tag.find_parent(
                "video", {"width": "0", "height": "0"}
            ):
                hidden_tags_count += 1

    return external_or_long_src_count + hidden_tags_count


# 示例HTML内容
html_content = """
<video width="0" height="0" controls>
<source src="www.evil.com/malicious.mp4" type="video/mp4"></video>
"""

res = calculate_score(html_content)
print(f"html5-tags count:{res}")
