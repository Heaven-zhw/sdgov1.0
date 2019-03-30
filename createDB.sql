/*说明
1.表infourl:存储URL的信息
字段:
id:自增的ID号，主键
url:公开信息内容所在的URL，唯一索引
flag：内容是否爬取过的标识，未爬取过为0，成功爬取过为1，爬取内容有误为2
department:发布机构
pubdate:公开日期
gaintime:爬取时间

2.表infocontent:存储具体公开信息的内容
字段:
id:ID号，主键，与infourl的id保持一致
url:公开信息内容所在的URL，唯一索引
department:发布机构
title:文章标题
themeclass:主题分类
serclass:服务对象分类
dispatchtime:发布时间
pubtime:公开时间
infotext:正文内容
filesurl:附件的url（如果有），字符串类型的列表
filesname:附件名（如果有），字符串类型的列表
gaintime:爬取时间

*/


create table if not exists `infourl`(
    `id` int(16) auto_increment,
    `url` varchar(255) default null unique,
    `flag` char(2) default null,
    `department` varchar(30) default null,
    `pubdate` date,
    `gaintime` datetime,
		primary key(`id`)
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


create table if not exists `infocontent`(
    `id` int(16),
    `title` varchar(100) default null,
    `department` varchar(30) default null,
    `themeclass` varchar(50) default null,
    `serveclass` varchar(50) default null,
    `dispatchtime` datetime,
    `pubtime` datetime,
    `infotext` text default null,
    `filesurl` text default null,
    `filesname` text default null,
    `gaintime` datetime,
		primary key(`id`)
)ENGINE=InnoDB  DEFAULT CHARSET=utf8;

/*清空表后加上下面这句，自增的id从1开始*/
alter table infourl auto_increment=1
/*查询内容、附件都为空的文章信息*/
SELECT url,department from infourl where id in
	(SELECT id from infocontent WHERE infotext='' and filesurl='[]')