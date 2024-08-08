# 网页恶意代码检测系统
阎禹辰 david2002fx@163.com
## 一、环境配置
```cmd
conda create -n [env_name] python=3.10 deprecated loguru
pip install -r requirements.txt
```

## 二、使用方法
### （一）文件系统约定
#### 网页文件
需要将待检测的网页文件按以下规则组织为文件夹<web_dir>并放入文件夹`webpages`中：
- webpages/<web_dir>
    - html/{a.html, b.html...}
    - js/{c.js, d.js...}
    - css/{e.jss, f.jss...}
    - network.har
    - metadata.yaml
- 注意，network.har和metadata.yaml至少需要存在一个，用于传递网页的`url`给系统。系统在提取url时，会优先选择network.har的`["log"]["pages"][0]["title"]`字段，其次选择metadata的`["website"]["url"]`字段。
#### 特征提取脚本
- 可以将自主添加的特征提取脚本组织为文件夹<feature_dir>。
- 理论上，<feature_dir>`子树`下的所有`.py`文件（不包括__init__.py）都会被检查，文件中的规则提取器会被加载。
- 实际使用时，建议将<feature_dir>组织为html, css, js, url四个子文件夹。在html文件夹下添加提取html文件特征的脚本，并继承自HTMLExtractor，其他同理。
#### 规则检测脚本
- 可以将自主添加的特征提取脚本组织为文件夹<rule_dir>，与“特征提取”的原理相同。
### （二）运行系统
```cmd
python src/main.py [-d <web_dir>] [-f <feature_dir>] [-r <rule_dir>]
```
### （三）特征提取脚本规范
1. 特征提取器 `FeatureExtractor`类有四个子类HTMLExtractor, CSSExtractor, JSExtractor和URLExtractor。用户编写的特征提取器YourExtractor需要继承自四个类之一。
2. YourExtractor的属性`meta`需要被初始化为`ExtractorMeta`类的对象，记录提取特征类型（html/css/js/url）、提取器名称（不可重名，也不可与作者编写的内置提取器重名）、作者、提取器描述和版本。
3. YourExtractor的属性`web_data`包含网页的所有内容、url、目录等，会传入已经初始化的对象作为参数。
4. YourExtractor必须实现`extract()`方法，其中需要用到web_data中特定文件格式的数据，对特定类型的所有文件**分别统计**特征数量和信息，返回一个`FeatureExtractionResult`对象。
    - 注意`info_dict`的key应当是文件名，value dict中的“count”、“time”、“additional_info”三个字段都`必须存在`，其中"additional_info"字段的内容可自定义。
- 下面是一个规范的提取器：
```python
class BlendModeCSS(CSSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "css",
            "BlendModeCSS",
            "yyc",
            "可疑的混合模式mix-blend-mode的使用次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        css_list = self.web_data.content["css"] # 详见WebData类的格式
        info_dict = {}
        for css in css_list:
            start_time = time.time()
            input_list = css_rules_listing(css["content"])
            res, blend_mode_usage = extract(input_list) # 这里的extract()是模块内的一个函数，用于提取特征
            info_dict[css["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": blend_mode_usage,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)
```
### （四）规则检测脚本规范
1. 用户编写的规则检测器YourRule需要继承自`Rule`类。
2. 在`__init__()`函数中需要设定规则名称和描述。
3. feature_dict成员加载自特征提取结果文件<web_dir>/features.json，格式遵从OverallExtractionResult类的约定
4. 需要实现`analyze()`方法，返回`AnalysisResult`对象。注意res_dict的key是文件名，value dict中的“score”和“additional_info”字段`必须存在`，后者可自定义。
- 下面是一个规范的规则检测器：
```python
class WordLenCSS(Rule):
    def __init__(self, feature_dict):
        super().__init__(feature_dict, name="WordLenCSS")
        self.description = "the ratio of word count to char count in css"

    def analyze(self):
        info_dict = self.feature_dict["css"]["WordCountCSS"]
        res_dict = {}
        if not isinstance(info_dict, dict):
            print("Error: invalid css info in features.json-css-WordCountCSS")
            return None
        for filename, info in info_dict.items():
            css_word_count = info["count"]
            css_char_count = info["additional_info"]["CharCount"]
            ratio = css_char_count / css_word_count
            normal_ratio = 4
            score = (
                min(100, (1 - normal_ratio / ratio) * 100 + 20)
                if ratio > normal_ratio
                else 0
            )
            res_dict[filename] = {
                "score": score,
                "additional_info": {"description": self.description},
            }
        return AnalysisResult(self.name, res_dict)
```
## 三、系统结构设计
### （一）主要流程
1. 网页数据加载：加载<web_dir>的html，css，js文件，生成**WebData**对象，并在同目录下创建或补充metadata.yaml记录网页元数据。
2. 特征提取器加载：遍历默认的及用户指定的特征提取目录，提取其中符合条件的特征提取器。
3. 特征提取：遍历所有提取器，执行`extract()`方法，汇总结果到**OverallExtractionResult**对象，将结果以字典形式写入到<web_dir>/features.json和<web_dir>/features.csv。
4. 规则检测器加载：遍历默认的及用户指定的规则目录，提取其中符合条件的规则检测器。
5. 规则检测：遍历所有检测器，执行`analyze()`方法，汇总结果到**OverallAnalysisResult**对象，将结果以字典形式写入到<web_dir>/analysis_result.json和<web_dir>/analysis_result.csv。
- 全过程有日志输出到**logs/<web_dir>.log**。
### （二）模块设计 src/
#### io/
- 定义了加载网页文件的WebData等数据类，特征提取器及结果类，规则检测器及结果类。
- 在结果类中，定义了**写入和读取json文件**的接口。
#### static_features/
- 定义了默认的静态特征提取器。其中有部分特征还没有转化为约定的接口形式。
#### static_rules/
- 定义了默认的规则检测器。
#### unused/
- 包含了一个用于url分析的工具模块，但目前没有使用。
#### utils/
1. css.py包含了从html中**提取内嵌css**的extract_css_features()函数，以及将css文件内容**提取为css规则列表**的css_rules_listing()函数。
2. diff.py用于比较两个文件信息，可能用于未来的“时间对比特征检测”
3. utils.py包含各种路径`常量`和其他预定义常量，从html中提取url的工具函数。
#### modules.py
- 负责**加载**与**执行**特征提取与规则检测模块。（可以注意到这两个模块的结构和工作流程一致）
#### main.py
- 程序的入口，负责控制主要流程。
## 四、其他说明
### 关于未完成部分
1. URL的特征提取规则除了直接检测URL本身的suspicious_pattern外，涉及到注册信息、DNS等额外信息的检测还没有实现。
2. 有很多特征提取器逻辑编写完成但尚未转换为规定的接口。
3. 规则检测引擎尚未设计完全，目前需要遍历所有规则；如果修改为树状结构（为每个规则指定一个“分数-子规则列表”的对应关系）可能能提高检测效率。
    - src/io/rule.py的SuccRule类实现了增加与删除“分界点-子规则列表”的功能。
4. 规则引擎具体结构的设定需要训练数据和算法作为基础。可以考虑使用机器学习算法来学习每个规则的权值，也可以使用深度学习方法直接从文本中提取特征。可以考虑将AI与人类的理解结合。