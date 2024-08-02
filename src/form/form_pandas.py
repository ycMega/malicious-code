import os

import pandas as pd


def form_pandas(
    results: dict, path: str, name: str, format_choice: str = "csv"
) -> pd.DataFrame:
    # 将结果转换为 DataFrame
    # 将数据字典转换为列表，每个元素是一个键值对的元组
    # data_items = [(key, value) for key, value in results.items()]

    # 创建DataFrame，每行存储一个键值对
    # df = pd.DataFrame(data_items, columns=["Key", "Value"])
    print(f"form pandas: path={path}, name={name}, format_choice={format_choice}")

    index = ["Row1"]
    df = pd.DataFrame(results, index=index)
    # 使用 Styler 添加颜色对比
    # def highlight_rows(row):
    #     return [
    #         "background-color: yellow" if i % 2 == 0 else "background-color: lightblue"
    #         for i in range(len(row))
    #     ]

    # styled_df = df.style.apply(highlight_rows, axis=1)

    base_name, extension = os.path.splitext(name)
    # 根据指定的格式保存文件
    if format_choice == "csv":
        df.to_csv(os.path.join(path, f"{base_name}-{extension[1:]}.csv"), index=False)
    elif format_choice == "html":
        df.to_html(os.path.join(path, f"{base_name}-{extension[1:]}.html"), index=False)

    return df
