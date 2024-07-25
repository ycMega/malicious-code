from bs4 import BeautifulSoup

# The noframes tag is a fallback tag for browsers that do not support frames,
# but usually attackers put their infected elements in this tag


def calculate_score(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "lxml")
    suspicious_count = 0
    # 查找所有noframes标签
    noframes_tags = soup.find_all("noframes")
    for noframe in noframes_tags:
        # 检查是否存在a标签且其scr（AI任务应该是href）属性长度大于150字符
        a_tags = noframe.find_all("a")
        for a in a_tags:
            if "href" in a.attrs and len(a["href"]) > 150:
                suspicious_count += 1
                break  # 找到一个符合条件的即可，避免重复计数

        # 检查是否存在meta标签且为refresh形式，只有http-equiv="refresh"用于页面重定向或自动刷新？
        meta_tags = noframe.find_all("meta")
        for meta in meta_tags:
            if "http-equiv" in meta.attrs and meta["http-equiv"].lower() == "refresh":
                suspicious_count += 1
                break  # 找到一个符合条件的即可，避免重复计数

    return suspicious_count


if __name__ == "__main__":
    html_content = f"""
    <frameset><frame src="http://MalSite.com"></frameset>
    <noframes>
    <!--Attack1-->
    <a href="http://MalSite.com{"a"*150}">Prize</a>
    <!--Attack2-->
    <meta http-equiv="refresh" content="5; url=http://MalSite.com">
    </noframes>
    """
    print(f"noframe count:{calculate_score(html_content)}")
