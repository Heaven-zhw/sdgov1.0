#coding="utf-8"
from urlcrawl import get_all,get_new
from store import readLatest
from bs4 import BeautifulSoup
from basic import getHTMLText
import requests
import datetime
import time
import traceback
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate',
            'Connection':'keep-alive',
            'Upgrade-Insecure-Requests':'1',
            'Pragma':'no-cache',
            'Cache-Control':'no-cache',

        }

spiderUrl="http://www.shandong.gov.cn/sdxxgk/nest/xxgk/list.do?pagenos="
#get_all(spiderUrl,1,25)

#返回date2与date1相差几天,%Y-%m-%d格式
def dateDelta(date1,date2):
    d2=datetime.datetime.strptime(date2,'%Y-%m-%d')
    d1=datetime.datetime.strptime(date1,'%Y-%m-%d')
    delta=d2-d1
    return delta.days


#查找给定日期的信息在网页的哪一页,采用二分查找思想，返回最后一个不小于该日期的页码值
#注意与常见二分查找的区别，URL中的数字是页码值，为索引值mid+1
def findPageNum(targetDate,totalPageNum):
    left = 0
    right = int(totalPageNum)
    while left < right:
        mid = left + (right - left) // 2
        viewHref=spiderUrl+str(mid+1)
        print('第',mid+1,'页')
        #获取当前页面最近的和最远的日期
        try:
            html = getHTMLText(viewHref, headers)
            if html == -1:
                return -1

            soup = BeautifulSoup(html, 'lxml')
            firstDate = soup.find(attrs={'class': 'list-st'}).getText()
            lastDate = soup.findAll(attrs={'class': 'list-st'})[-1].getText()
            time.sleep(1)
        except:
            return -1

        if targetDate > firstDate:  # (fisrtDate,MAX)
            right = mid
        elif targetDate > lastDate:  # (lastDate，fisrtDate]
            return mid + 1
        else:  # (MIN,lastDate]
            left = mid + 1

    return left




if __name__=='__main__':

    day=0
    while True:
        day=day+1
        print("------------------现在是第",day,"天----------------")
        time.sleep(10)
        try:
            #从数据库中读取当前已有的最新日期
            dbLatestDate=readLatest()
            #print("The num is:",findPageNum("2018-09-13",8598))

            if dbLatestDate==None :
                #localLatestDate="1970-01-01"
                localLatestDate = "2017-01-01"
            elif dbLatestDate==1:
                print("日期读取错误")
                raise Exception("日期读取错误")
            else:
                localLatestDate=str(dbLatestDate[0])
                print(localLatestDate)

            firstHref=spiderUrl+str(1)
            #获取网站最新的信息日期和信息总页数

            html=getHTMLText(firstHref,headers)
            if html==-1:
                raise Exception("获取网站最新的信息日期和信息总页数错误")
            time.sleep(2)

            soup = BeautifulSoup(html, 'lxml')
            webLatestDate = soup.find(attrs={'class': 'list-st'}).getText()
            #lastdate = soup.findAll(attrs={'class': 'list-st'})[-1].getText()
            # <span class="simple_pgTotalPage">8598</span>
            totalPageNum = int(soup.find('span', attrs={'class': 'simple_pgTotalPage'}).getText())

            print(webLatestDate,totalPageNum)

            #如果大于2个月没有爬取，查找库中最新的日期在哪一页，从第一页到那一页多线程爬取
            if dateDelta(localLatestDate,webLatestDate)>60:
                beginPageNum=findPageNum(localLatestDate,totalPageNum)
                if beginPageNum<0:
                    print("起始页码错误")
                    raise Exception("起始页码错误")
                get_all(spiderUrl,1,beginPageNum)
            else:#否则采用递增式单线程爬取
                get_new(spiderUrl,localLatestDate)
        except:
            traceback.print_exc()
            pass

        print("------------------第", day, "天完成----------------")
        time.sleep(86000)

print(dateDelta('2019-03-25','2017-01-01'))

