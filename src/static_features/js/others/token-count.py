from collections import Counter

import deprecated
from numpy import deprecate

from src.static_features.js import *

# from src.static_features.js import *
from src.utils.utils import parse_js_code


class TokenCountJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "TokenCountJS",
            "others",
            "使用某种可能不完善的匹配模式，计算token的总数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        js_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_list:
            start_time = time.time()
            res = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# 统计ast中的token数量
@deprecated.deprecated(
    reason="This function is deprecated due to unstable performance of traversing the ast."
)
def count_tokens(ast):
    token_counts = Counter()

    def traverse(node, token_counts):
        if not hasattr(node, "type"):
            return
        # 统计节点类型
        token_counts[node.type] += 1
        # print(token_counts)
        # print(node.type)
        # 遍历节点的子节点
        # 必须要检查callable，否则即使hasattr(node, "items")也会报错 'NoneType' object is not callable
        if node is None or not callable(getattr(node, "items", None)):
            return
        for key, value in node.items():
            if isinstance(value, list):
                for item in value:
                    traverse(item, token_counts)
            else:
                traverse(
                    value, token_counts
                )  # 注意！类型不是dict而是esprima的某个类型（只是打印出来看着像dict）
            # elif isinstance(value, dict):
            #     traverse(value, token_counts)

        # if node.type in ["Literal", "Identifier"]:
        #     token_counts.update(node.type)
        # elif node.type == "TemplateLiteral":
        #     for elem in node.expressions:
        #         traverse(elem)
        #     for quasi in node.quasis:
        #         traverse(quasi)

    traverse(ast, token_counts)
    return token_counts


def extract(js_content: str):
    token_pattern = r"""
        "(?:\\.|[^"\\])*"         |  # 双引号字符串
        '(?:\\.|[^'\\])*'         |  # 单引号字符串
        `(?:\\.|[^`\\])*`         |  # 模板字符串
        \b(?:break|case|catch|class|const|continue|debugger|default|delete|do|else|export|extends|finally|for|function|if|import|in|instanceof|let|new|return|super|switch|this|throw|try|typeof|var|void|while|with|async|await)\b |  # 关键字
        [a-zA-Z_]\w*              |  # 标识符
        \d+\.\d+|\d+              |  # 数字
        [+\-*/=<>!&|]{1,2}        |  # 运算符
        [(){};,.]                 |  # 分隔符
        \s+                       |  # 空白字符
        [^\w\s]                   # 其他符号
    """

    tokens = re.findall(token_pattern, js_content, re.VERBOSE)
    # 过滤掉空白和无效字符
    tokens = [token for token in tokens if token.strip()]

    return len(tokens)
    # ast, error = parse_js_code(js_content)
    # if error:
    #     print(f"Error parsing code: {error}")
    #     # return -1
    # token_count = count_tokens(ast)
    # return sum(token_count.values()), token_count


if __name__ == "__main__":
    sample_js = """
    function add(a, b) {
        return a + b;
    }

    // 复杂函数声明
    function complexFunction(x, y) {
        let result = x * y;
        if (result > 10) {
            result = result / 2;
        } else {
            result = result + 10;
        }
        return result;
    }

    // 对象和数组
    const obj = {
        name: "John",
        age: 30,
        address: {
            city: "New York",
            zip: "10001"
        }
    };

    const arr = [1, 2, 3, 4, 5];

    // 循环和条件语句
    for (let i = 0; i < 10; i++) {
        if (i % 2 === 0) {
            console.log(i);
        }
    }

    // 类和方法
    class Person {
        constructor(name, age) {
            this.name = name;
            this.age = age;
        }

        greet() {
            console.log(`Hello, my name is ${this.name} and I am ${this.age} years old.`);
        }
    }

    const person = new Person("Alice", 25);
    person.greet();

    // 箭头函数
    const multiply = (a, b) => a * b;

    // 模块导入和导出
    import { foo, bar } from './module';

    export const baz = foo + bar;
    async function fetchData(url) {
        const response = fetch(url);
        const data = response.json();
        return data;
    }
    // 异步函数
    async function fetchData(url) {
        const response = fetch(url);
        const data = response.json();
        return data;
    }
    """
    token_count = extract(sample_js)
    print(f"token count:{token_count}")
    # sum_count, token_count = extract(sample_js)
    # print(f"Token count: {sum_count}, {token_count}")

    js = """
        // 简单函数声明
    
    """
