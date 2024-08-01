import os

import pandas as pd

from analyze import analyze_content, analyze_html, analyze_js
from form.form_pandas import form_pandas

webpage_path = "./webpages"


if __name__ == "__main__":
    for web_file in os.listdir(webpage_path):
        web_dir_path = os.path.join(webpage_path, web_file)
        if os.path.isdir(web_dir_path):
            for web_file in os.listdir(web_dir_path):
                total_scores = {}
                if web_file.endswith(".html"):
                    html_file_path = os.path.join(web_dir_path, web_file)
                    print(f"Analyzing HTML file: {html_file_path}")
                    # total_scores = analyze_html(html_file_path)
                    total_scores = analyze_content(html_file_path, "html")
                    print(total_scores)

                elif web_file.endswith(".js"):
                    js_file_path = os.path.join(web_dir_path, web_file)
                    print(f"Analyzing JS file: {js_file_path}")
                    # total_scores = analyze_js(js_file_path)
                    total_scores = analyze_content(js_file_path, "js")
                    print(total_scores)
                elif web_file.endswith(".css"):
                    css_file_path = os.path.join(web_dir_path, web_file)
                    print(f"Analyzing CSS file: {css_file_path}")
                    total_scores = analyze_content(css_file_path, "css")
                else:
                    print(f"Skipping file: {web_file}")
                    continue
                form_pandas(total_scores, web_dir_path, web_file, "csv")
        else:
            print(f"Skipping: {web_file}")

    # CSV文件的路径
    csv_file_path = "webpages/bilibili/412-js.csv"

    # 读取CSV文件，这里header=None表示没有头部行，nrows=1读取第一行
    keys = pd.read_csv(csv_file_path, header=None, nrows=1).iloc[0].tolist()

    # 再次读取文件，这次从第二行开始读取数据
    df = pd.read_csv(csv_file_path, header=None, skiprows=1)

    # 重置列名
    df.columns = keys

    # 现在df应该是一个有正确列名和数据的DataFrame
    print(df)
