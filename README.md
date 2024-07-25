
## requirements
- python 3.10
- requirements.txt
- conda: pandas, deprecated, pyjsparser
<!-- - npm: esprima -->

## usage
- python src/main.py


## 思考
- 7.18：目前的实现是每个文件统计一个特征，并直接计算分数。后面可能设计为“多个规则”，每个规则涉及到多个特征，满足特定规则后再判断更深的规则。（规则是偏序的，且不一定要遍历所有规则）
- 7.19：对JS用JS的规则，

## 问题
1. 对HTML和JS的处理方法不同，需要单独判断，无法直接递归读取文件夹来处理？
2. 爬取的内容与ctrl+G看到的内容差异很大。比如缺少了很多link和内联JS。
3. 尝试使用scrapy？