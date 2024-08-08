
## requirements
- python 3.10
- requirements.txt
- conda: pandas, deprecated, aiofiles, loguru #pyjsparser
<!-- - npm: esprima -->

## usage
- python src/main.py


## 思考
- 7.18：目前的实现是每个文件统计一个特征，并直接计算分数。后面可能设计为“多个规则”，每个规则涉及到多个特征，满足特定规则后再判断更深的规则。（规则是偏序的，且不一定要遍历所有规则）
- 7.19：对JS用JS的规则，
- 7.31：HTML和CSS的对应关系不明，但至少可以单独检测。最好把之前关于CSS的规则单独提取出来？

## 问题
1. 对HTML和JS的处理方法不同，需要单独判断，无法直接递归读取文件夹来处理？
2. 爬取的内容与ctrl+G看到的内容差异很大。比如缺少了很多link和内联JS。

### Malicious URL Detection using Machine Learning: A Survey
#### HTML-survey19
1. 平均单词长度
    恶意内容指示：较长的单词可能指示复杂或加密的恶意代码。
    可读性评估：帮助判断文本的可读性，恶意网页通常会使用复杂的术语。

2. 总单词数
    内容丰富性：总单词数可以反映网页内容的丰富程度，恶意网页往往内容较少。
    爬虫检测：低单词数可能表明该网页是生成的或不真实。

3. 不同单词数
    多样性分析：较高的不同单词数表示文本多样性，通常与正常内容相关。
    重复内容检测：低不同单词数可能暗示内容重复，增加恶意性质的可能性。

4. 每行单词数
    格式化判断：每行单词数可以反映页面的格式和布局，异常的排版可能是恶意设计的迹象。
    可读性影响：过多或过少的单词数可能影响读者的体验，恶意页面通常会故意设计以混淆用户。
- 此外还提到了NULL字符数量、字符串拼接函数、不对称HTML标签、外部脚本链接、超链接（a）、不可见对象数量、iframe（总数和零大小）、行数、小区域元素数、可疑内容元素数、不符合常规位置或结构的元素数量、双文档检测、版本变化检测
#### JS-survey19
1. 常用 JavaScript 函数的使用计数：
    eval()
    unescape()
    escape()
    link()
    exec()
    search()

2. 关键字与单词的比例：
3. 长字符串数量：
4. 解码例程的存在：
5. shell 代码存在的概率：
6. 直接字符串赋值的数量：
7. DOM 修改函数的数量：
8. 事件绑定的数量：
9. 可疑对象名称的数量：
10. 可疑字符串的数量：
11. "iframe" 字符串的数量：
12. 可疑字符串标签的数量：
#### Other Content-based Features.
active X对象频率
DOM文本中的身份与关键字
对比观察到的身份和潜在模仿的身份，评估其一致性
网站目录结构分析（似乎是检测vulnerable before turning malicious?）
#### context features
最近出现了一种研究方向，专注于获取 URL 的上下文特征，即该 URL 被分享的背景信息。[103] 利用从分享 URL 的推文中提取的上下文信息。[185] 使用点击流数据对短网址进行恶意与否的分类。[31] 提出了基于转发的特征来对抗恶意转发网址。[30] 提出了另一种特征方向，专注于在社交媒体上分享的 URL，旨在通过分析分享和点击这些 URL 的用户行为来识别恶意性质。这些特征正式称为“`基于发布的特征`”和“`基于点击的特征`”。[6] 通过系统分类上下文特征来处理此问题，包括内容相关特征（推文的词汇和统计属性）、推文上下文特征（时间、相关性和用户提及）以及社交特征（关注、粉丝、位置、推文、转发和喜欢的数量）。
#### popularity features
- 应用统计技术来检测恶意 URL 的早期方法之一，旨在以概率方式识别特定手工设计特征的重要性。这些特征包括：基于页面的特征（页面排名、质量等）、基于域的特征（在白名单域表中的存在）、基于类型的特征（混淆类型）和基于词的特征（如“确认”、“银行”等关键字的存在）。
- [178] 同时使用基于 URL 和基于内容的特征，并记录初始 URL、着陆 URL 和重定向链。此外，他们记录弹出窗口的数量和插件的行为，这些通常被垃圾邮件发送者使用。
- [40] 提出了新类别特征的使用：链接流行度和网络特征。链接流行度基于来自其他网页的入站链接进行评分。这些信息来自不同的搜索引擎。为了使这些特征的使用对操控具有鲁棒性，他们还提出了某些度量标准以验证链接的质量。他们还使用了一个度量标准来检测垃圾邮件到垃圾邮件的 URL 链接。在他们的研究中，这些特征与词汇特征、基于内容的特征和基于主机的特征结合使用。
- [55] 通过跟踪 URL 在 Facebook 和 Twitter 上的公共分享次数，使用了 URL 的社交声誉特征。其他研究将重定向链的信息纳入重定向图中，以提供检测恶意 URL 的洞察[99, 170]。
- [49, 120] 使用搜索引擎查询数据来挖掘词相关性测量。