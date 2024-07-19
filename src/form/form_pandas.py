import os

import pandas as pd


def form_pandas(
    results: dict, path: str, name: str, format_choice: str = "csv"
) -> pd.DataFrame:
    # 将结果转换为 DataFrame
    print(f"form pandas: path={path}, name={name}, format_choice={format_choice}")
    index = ["Row1"]
    df = pd.DataFrame(results, index=index)
    base_name, extension = os.path.splitext(name)
    # 根据指定的格式保存文件
    if format_choice == "csv":
        df.to_csv(os.path.join(path, f"{base_name}-{extension}.csv"), index=False)
    elif format_choice == "html":
        df.to_html(os.path.join(path, f"{base_name}-{extension}.html"), index=False)

    # print(df.to_string(index=False))

    return df
