# sdgov1.0
爬取山东省政务公开的信息

# 程序流程

获取这类随时间滚动的信息，基本思路就是先从滚动页面爬取一定数量的URL存入数据库的链接表，再从库中取未爬取过内容的URL，访问并获取信息内容，存入数据库的内容表，同时更新爬取标志位为已完成。像这一类的滚动类信息还有通知公告，实时新闻等，其发布时间是一个关键要素。

基于此，本程序对山东省政务公开网站 （ http://www.shandong.gov.cn/sdxxgk/nest/xxgk/list.do ）进行自动化的获取，对于URL和链接都是每隔24小时可以进行新的一次爬取。

程序具体流程为：

获取URL：从数据库中读取当前最新一条记录的发布日期，如果没有数据（第一次运行）则为一个事先指定的日期，代表要获取这一天以后发布的信息，本程序中指定为2017-01-01，即获取2017年以后的政务公开信息。然后再从URL链接页面的第一页获取当前最新的日期，与从库中读的日期做比较，如果时间间隔比较大（要爬的页面较多）则采用多线程的方法爬取，如果间隔较小，就直接单线程按页序号依次递增爬取页面，直到页面最早一条信息的发布日期早于从库中读的日期为止，本程序这个日期间隔临界值设为60天。多线程爬取中，采用二分查找的思想，获取发布时间不晚于中从库中读的日期的最后一条信息所在的页码号，从这一页到第一页按页码由大到小把拼接完整的链接送入线程队列，再采用多线程的方式从线程队列中取得链接，进行URL等信息的爬取。


获取内容：每隔一天（86000秒）执行一次爬取流程，每次执行的内容为：读取一定数量的未爬取过的URL，不为空则放入线程队列，进行信息内容的爬取，为空则完成当天的爬取流程。程序中设定每天最多读取20次URL，每次读1000条记录。


# 文件说明

basic.py:获取页面HTML的基础函数

urlcrawl.py:爬取URL页面的具体方法

urldetect.py:爬取URL页面的入口

contentcrawl.py:爬取详细内容页面的具体方法

contentdetect.py:爬取详细内容页面的入口

store.py:直接与数据库相连的若干操作

mylog.py:多种日志记录函数

dateop.py:日期比较函数

createDB.sql:建立数据表的SQL语句

Onecontent1.0.py、Onecontent2.0.py:爬取单个内容页面的函数（未使用，已经嵌入contentcrawl中）

QQ截图:某次的出错信息，看看就好


# 使用说明

本程序使用Python3，Windows和Linux环境下均可运行。

1. 创建新的MySQL数据库，运行建立table的SQL代码

2. 安装相应的Python3的第三方库

3. 在store.py中修改数据库配置，在urldetect.py里可修改默认起始爬取日期（默认值为2017-01-01）

4. 运行urldetect.py，当有一定数量的url后再运行contentdetect.py，理论上程序可以一直运行着

# 页面内容提取过程

链接页面的提取很简单，由于格式固定，只要匹配上关键标签即可。

信息内容页面的提取稍微复杂一点。

首先，公开内容的基本信息在body顶部的table中，格式固定，很容易抓取到。

之后是正文的抓取，正文的标签大部分为`<div style="align-content: center;" >`，经过测试后发现少部分比较正式的文章正文标签为`<div ergodic="article" >`，还可能有别的种类的标签，可能需要进一步完善。正文内还可能有img图片标签，在此暂时不抓取。

对于附件信息，也可以找到对应的父标签，由于附件可能有多个，需要findAll提取，在此使用列表，直接把结果列表转为字符串存数据库里。


# 踩过的坑


1.爬URL的时候一开始没有在意，开了8线程，结果服务器短暂宕机，于是改为1线程。而爬信息内容时服务器情况好一些，开了2线程。还是建议尽量不要爬政府网站，有被查水表的风险


2.在网络情况不好时（如晚上8点以后），无论是爬链接还是爬内容，都会经常出现" Max retries exceeded with url "的错误，解决措施是增加延时，请求被拒绝时进行多次重试，参考 [https://segmentfault.com/a/1190000007480913?_ea=1359663](https://segmentfault.com/a/1190000007480913?_ea=1359663)



3.
`http://www.shandong.gov.cn/sdxxgk/publi/message/detail.do?identifier=ml_0302-04-2018-000163`

在这个链接中碰到了网页中带有 base64 编码的图片，再用apparent\_encoding程序直接卡住，因为图片比较大，保存下来要412.7KB，这么大的base64串apparent\_encoding几乎是解析不动的。解决方法是修改获取HTML页面内容的函数，不使用r.apparen\_encoding

附：
	三种方法获取网页编码：
	
	r.encoding从响应头中获取，响应头中没有编码，encoding则默认为ISO-8859-1
	
	r.apparent_encoding从内容中分析编码，利用了chardet，速度较慢
	
	requests.utils.get_encodings_from_content(r.text) 调用方法从html页面开头
	的charset获取，如<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">



4.

	textpat = re.compile(r'p|span|ul')
    texts = infobody.findAll(textpat)

用正则匹配p、span、ul标签时可能会有嵌套情况，如部分span标签出现在p标签之内，这样在用beautifulSoup的soup.getText()方法时，由于该方法是提取当前标签及其子标签所有文本的内容，部分文本会被提取两次，在此可以不提取span标签，不过可能损失一些信息。而lxml好像有只提取直接子标签文本和提取所有标签文本的内容两种方法，可以更改选择器。

正文文本出现的位置在各网页中有所不同，有的网页文字在infobody下的p标签内，有的在span标签内，还有的直接出现在infobody内，其实可以直接对infobody直接getText()，不过可能会有杂数据，目前采用的是直接在大标签下直接getText。


