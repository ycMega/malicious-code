# import requests
import re

from bs4 import BeautifulSoup
from src.utils.css import css_rules_listing, extract_css_features


# z-index 数量
def extract_z_index_from_style(style_content):
    z_indices = []
    pattern = r"z-index:\s*(-?\d+)"
    matches = re.findall(pattern, style_content, re.IGNORECASE)
    for match in matches:
        z_indices.append(int(match))
    return z_indices


def calculate_score(css_list: list):
    # soup = BeautifulSoup(html_content, "html.parser")
    suspicious_elements = []
    high_z_indices = []
    for css_style in css_list:
        print(f"css style:{css_style}")
        # 提取元素的 name 属性
        name_match = re.search(r"(\w+)\s*{", css_style)
        element_name = name_match.group(1) if name_match else "unknown"

        # 检查 z-index 属性
        z_index_match = re.search(r"z-index\s*:\s*(-?\d+)", css_style)
        if z_index_match:
            z_index_value = int(z_index_match.group(1))
            # 根据 z-index 值调整得分
            if z_index_value > 1000:
                suspicious_elements.append(
                    (element_name, z_index_value, "High z-index")
                )
            elif z_index_value > 100:
                high_z_indices.append(z_index_value)
            elif z_index_value < 0:
                suspicious_elements.append(
                    (element_name, z_index_value, "Negative z-index")
                )
    if len(high_z_indices) > 3:
        suspicious_elements.append(
            (
                "Multiple elements",
                "High z-index values",
                f"Count: {format(len(high_z_indices))}",
            )
        )

    # # 检查所有元素的 style 属性
    # for element in soup.find_all(True):
    #     style = element.get("style", "")
    #     z_indices = extract_z_index_from_style(style)

    #     # 检查内联 z-index
    #     for z_index_value in z_indices:
    #         if z_index_value < 0:
    #             suspicious_elements.append(
    #                 (element.name, z_index_value, "Negative z-index")
    #             )
    #         elif z_index_value > 1000:
    #             suspicious_elements.append(
    #                 (element.name, z_index_value, "High z-index")
    #             )
    #         if z_index_value > 100:
    #             high_z_indices.append(z_index_value)

    # # 检查 <style> 块中的 CSS
    # for style_tag in soup.find_all("style"):
    #     z_indices = extract_z_index_from_style(style_tag.string or "")
    #     for z_index_value in z_indices:
    #         if z_index_value < 0:
    #             suspicious_elements.append(
    #                 ("Style Block", z_index_value, "Negative z-index")
    #             )
    #         elif z_index_value > 1000:
    #             suspicious_elements.append(
    #                 ("Style Block", z_index_value, "High z-index")
    #             )
    #         if z_index_value > 100:
    #             high_z_indices.append(z_index_value)

    return len(suspicious_elements), suspicious_elements


# 示例用法
if __name__ == "__main__":
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
    css_content = """
    body {
        font-family: 'Arial', sans-serif;
    }
    .header {
        z-index: 10;
        position: relative;
    }
    .footer {
        z-index: 5;
        position: relative;
    }
    .sidebar {
        z-index: 1001;
        position: absolute;
    }
    .modal {
        z-index: 2000;
        position: fixed;
    }
    .hidden-element {
        z-index: -1;
        position: absolute;
    }
    .high-z-index-1 {
        z-index: 150;
        position: relative;
    }
    .high-z-index-2 {
        z-index: 200;
        position: relative;
    }
    .high-z-index-3 {
        z-index: 300;
        position: relative;
    }
    .high-z-index-4 {
        z-index: 400;
        position: relative;
    }
    """
    css_test_list = extract_css_features(html_content) + css_rules_listing(css_content)
    z_index_score, suspicious_elements = calculate_score(css_test_list)
    print(f"suspicious z-index count = {z_index_score}: {suspicious_elements}")
