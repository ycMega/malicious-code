import os

from ana_html import analyze_html
from ana_js import analyze_js
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
                    total_scores = analyze_html(html_file_path)
                    print(total_scores)

                elif web_file.endswith(".js"):
                    js_file_path = os.path.join(web_dir_path, web_file)
                    print(f"Analyzing JS file: {js_file_path}")
                    total_scores = analyze_js(js_file_path)
                    print(total_scores)
                else:
                    print(f"Skipping file: {web_file}")
                    continue
                form_pandas(total_scores, web_dir_path, web_file, "csv")
        else:
            print(f"Skipping: {web_file}")
