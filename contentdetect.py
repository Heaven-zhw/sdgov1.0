#coding=utf-8
from contentcrawl import get_all
from store import readUrls
import time
spiderUrl="http://www.shandong.gov.cn"


if __name__ =='__main__':
    day=0
    while True:
        day = day + 1
        print("------------------现在是第", day, "天----------------")
        time.sleep(10)
        ncount=20 #限定一天最多调用get_all函数的次数

        while ncount>0:
            #实际上是Tuple类型
            hrefList=readUrls() #每次读一定数量的链接，默认1000
            #print(hrefList)
            if hrefList!=1:
                if(len(hrefList)>0):
                    get_all(spiderUrl,hrefList)
                    ncount=ncount-1
                else:
                    break
        print("------------------第", day, "天的爬取完成----------------")
        time.sleep(86000)