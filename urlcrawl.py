#coding=utf-8
from bs4 import BeautifulSoup
import requests
import re
import time
import traceback
import queue
import threading
from basic import getHTMLText
from store import saveUrls
from mylog import logUrlConnectError,logUrlFormError
import datetime
start_url="http://www.shandong.gov.cn/sdxxgk/nest/xxgk/list.do?pagenos="

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



class LookUp(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global queue_href, mutex_href_get, mutex_href_put
        mutex_href_get.acquire()

        while queue_href.qsize() > 0:
            # 在线程池中取得链接
            viewHref = str(queue_href.get())
            mutex_href_get.release()

            # 调用get_page函数
            result = get_page(viewHref)
            print('1111111111111111111111111111111111111122222222222222')
            print(result)
            print('111' * 10)
            try:
                mutex_href_put.acquire()
                print(str(type(result)))
                if str(type(result)) == "<class 'list'>":
                    # 存储
                    print(len(result))
                    saveUrls(result)
                elif result == 1: #连接错误
                    logUrlConnectError(viewHref)
                elif result==2: #格式错误
                    logUrlFormError(viewHref)

                mutex_href_put.release()
            except:
                traceback.print_exc()
                print('shittttttttttttttttttt')
                mutex_href_put.release()
                mutex_href_get.acquire()
                continue
            mutex_href_get.acquire()
        mutex_href_get.release()

#爬取[start_page,end_page]范围内的
def get_all(spiderUrl,start_page,end_page):
    # 定义链接队列/得到链接的锁/给予链接的锁为全局变量
    global queue_href, mutex_href_get, mutex_href_put
    queue_href = queue.Queue()
    threads = []
    # 线程数量
    num = 1
    mutex_href_get = threading.Lock()
    mutex_href_put = threading.Lock()

    #URL倒序加入线程队列，以备网络连接失败后再启动还能继续从较早的日期爬取
    for k in range(int(end_page),int(start_page)-1,-
    1):
        queue_href.put(spiderUrl+str(k))

    for i in range(0, num):
        threads.append(LookUp())

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def get_page(viewHref):
    #"http://www.shandong.gov.cn/sdxxgk/nest/xxgk/list.do?pagenos={}".format(page)
    time.sleep(1.5)
    print(viewHref)
    #获取页面内容
    html=getHTMLText(viewHref,headers)
    if html==-1: #连接错误
        return 1

    try:
        soup = BeautifulSoup(html, 'lxml')

        table = soup.find('table')
        itemlist = table.findAll('tr')
        result = []

        for item in itemlist:
            url = item.find(attrs={'class': 'list-tit'}).a.get('href')
            department = item.find(attrs={'class': 'list-dw'}).getText()
            pubdate = item.find(attrs={'class': 'list-st'}).getText()
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            result.append([url, 0, department, pubdate, nowtime])
        return result
    except:
        #格式错误
        traceback.print_exc()
        return 2

#递增式爬取
def get_new(spiderUrl,localLatestDate):
    pageNum=1
    nowPageDate="1970-01-01" #初始化信息的发布日期
    errCount=0 #连接错误次数
    while errCount<=3: #错误次数超过三次，直接退出
        time.sleep(2)
        viewHref=spiderUrl+str(pageNum)
        result=get_page(viewHref)
        if str(type(result)) == "<class 'list'>":
            print(len(result))
            nowPageDate=result[-1][-2] #获取最后一条信息的发布日期
            print(nowPageDate)
            saveUrls(result)

            errCount = 0
            if nowPageDate<localLatestDate: #已经到本地最新的日期，停止爬
                break
            else:
                pageNum=pageNum+1 #继续爬下一页
        elif result == 1:  # 连接错误
            logUrlConnectError(viewHref)
            errCount = errCount + 1
        elif result == 2:  # 格式错误
            logUrlFormError(viewHref)
            errCount=0



