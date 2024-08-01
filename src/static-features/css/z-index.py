# import requests
import re

from bs4 import BeautifulSoup
from src.utils.css import extract_css_features


# z-index 数量
def extract_z_index_from_style(style_content):
    z_indices = []
    pattern = r"z-index:\s*(-?\d+)"
    matches = re.findall(pattern, style_content, re.IGNORECASE)
    for match in matches:
        z_indices.append(int(match))
    return z_indices


def calculate_score(html_content: str):
    soup = BeautifulSoup(html_content, "html.parser")
    suspicious_elements = []
    high_z_indices = []

    # 检查所有元素的 style 属性
    for element in soup.find_all(True):
        style = element.get("style", "")
        z_indices = extract_z_index_from_style(style)

        # 检查内联 z-index
        for z_index_value in z_indices:
            if z_index_value < 0:
                suspicious_elements.append(
                    (element.name, z_index_value, "Negative z-index")
                )
            elif z_index_value > 1000:
                suspicious_elements.append(
                    (element.name, z_index_value, "High z-index")
                )
            if z_index_value > 100:
                high_z_indices.append(z_index_value)

    # 检查 <style> 块中的 CSS
    for style_tag in soup.find_all("style"):
        z_indices = extract_z_index_from_style(style_tag.string or "")
        for z_index_value in z_indices:
            if z_index_value < 0:
                suspicious_elements.append(
                    ("Style Block", z_index_value, "Negative z-index")
                )
            elif z_index_value > 1000:
                suspicious_elements.append(
                    ("Style Block", z_index_value, "High z-index")
                )
            if z_index_value > 100:
                high_z_indices.append(z_index_value)

    # 检测不合理组合
    if len(high_z_indices) > 3:
        suspicious_elements.append(
            (
                "Multiple elements",
                "High z-index values",
                f"Count: {format(len(high_z_indices))}",
            )
        )

    return len(suspicious_elements), suspicious_elements
    # inline_styles, external_styles, element_styles = extract_css_features(html_content)
    # for inline_style in inline_styles:
    #     if "z-index" in inline_style:
    #         z_index_count += inline_style.count("z-index")
    # for element_style in element_styles:
    #     if element_style and "z-index" in element_style:
    #         z_index_count += element_style.count("z-index")
    # for css_url in external_styles:
    #     try:
    #         pass
    #         # response = requests.get(css_url, timeout=5)
    #         # response.raise_for_status()
    #         # css_content = response.text
    #         # if "z-index" in css_content:
    #         #     z_index_count += css_content.count("z-index")
    #     except Exception as e:
    #         print(f"Failed to fetch CSS file: {css_url}")
    #         print(e)
    # return z_index_count


# 示例用法
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Z-Index</title>
    <style>
        .box1 {
            width: 100px;
            height: 100px;
            background-color: red;
            position: absolute;
            z-index: -1; /* Element style z-index */
        }
        .box2 {
            width: 100px;
            height: 100px;
            background-color: blue;
            position: absolute;
            z-index: 2; /* Element style z-index */
        }
    </style>
</head>
<body>
    <div class="box1" style="z-index: 1000;">Box 1 (Inline z-index)</div>
    <div class="box2" style="z-index: 1;">Box 2 (Inline z-index)</div>
    <div style="position: relative; z-index: 0;">This is a lower stacking context.</div>
    <style>
        .high { z-index: 1500; }
        .negative { z-index: -1; }
    </style>
    <div style="z-index: 10;">Normal Z Index</div>
    <div class="high">High Z Index</div>
    <div class="negative">Negative Z Index</div>
    <div style="z-index: 200;">Another High Z Index</div>
    <div style="z-index: 300;">Yet Another High Z Index</div>
    <div style="z-index: 1200;">Another Extremely High Z Index</div>
</body>
</html>
"""
z_index_score, suspicious_elements = calculate_score(html_content)
print(f"suspicious z-index: {suspicious_elements}")
