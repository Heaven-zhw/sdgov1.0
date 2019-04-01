#coding=utf-8

from bs4 import BeautifulSoup
import requests
import re
import time
import traceback
import queue
import threading
from mylog import logContentConnectError,logContentFormError
from store import saveContent,updateErrorFlag
from basic import getHTMLText
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
            viewHref_and_id=queue_href.get()
            viewHref = str(viewHref_and_id.split("WHZHW")[0])
            id=int(viewHref_and_id.split("WHZHW")[1])
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
                    saveContent(id,result)
                elif result == 1: #连接错误
                    logContentConnectError(viewHref)
                elif result==2: #格式错误
                    logContentFormError(viewHref)
                    updateErrorFlag(id)

                mutex_href_put.release()
            except:
                traceback.print_exc()
                print('shittttttttttttttttttt')
                mutex_href_put.release()
                mutex_href_get.acquire()
                continue
            mutex_href_get.acquire()
        mutex_href_get.release()

#爬取hrefList中的链接，传递的数量取决于detect模块
#由于url存储的是相对路径，需要传递spiderUrl补全
def get_all(spiderUrl,hrefList):
    # 定义链接队列/得到链接的锁/给予链接的锁为全局变量
    global queue_href, mutex_href_get, mutex_href_put
    queue_href = queue.Queue()
    threads = []
    # 线程数量
    num = 2
    mutex_href_get = threading.Lock()
    mutex_href_put = threading.Lock()

    #URL加入线程队列
    for k in hrefList:
        id=k[0]
        viewHref=spiderUrl+k[1]
        queue_href.put(viewHref+"WHZHW"+str(id))

    for i in range(0, num):
        threads.append(LookUp())

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def get_page(viewHref):
    time.sleep(1.5)
    print(viewHref)

    html= getHTMLText(viewHref,headers)
    if html==-1:
        return 1 #连接错误

    try:
        soup = BeautifulSoup(html, 'lxml')

        # 抓取公开内容基本信息
        table = soup.find('table')
        tds = table.findAll('td')

        # indexNo=tds[1].getText().strip()
        themeclass = tds[3].getText() #主题分类
        if type(themeclass) == str:
            themeclass = themeclass.strip()

        department = tds[5].getText() #发布机构
        if type(department) == str:
            department = department.strip()

        serveclass = tds[7].getText() #服务对象分类
        if type(serveclass) == str:
            serveclass = serveclass.strip()

        # docNo=tds[9].getText().strip()
        dispatchtime = tds[11].getText() #发文时间
        if type(dispatchtime) == str:
            dispatchtime = dispatchtime.strip()

        title = tds[13].getText() #文章标题
        if type(title) == str:
            title = title.strip()

        pubtime = tds[15].getText() #公开时间
        if type(pubtime) == str:
            pubtime = pubtime.strip()

        # 通过正文标签提取正文

        def getInfoByBody(soup, infobody, infotext):
            if infobody != None:
                #textpat = re.compile(r'p|span|ul') #span在p标签内文本会被提取提取两次
                textpat = re.compile(r'p|ul')
                texts = infobody.findAll(textpat)
                # 大部分情况都有p标签
                for item in texts:
                    if type(item.getText()) == str:
                        # 要去除不间断空白符和全角空白符
                        infotext = infotext + item.getText().replace(u'\u3000', u' ').replace(u'\xa0',
                                                                                              u' ').strip() + '\n'
                # print(infotext)
                # 针对没有p标签，正文直接在infobody中的情况
                if infotext == "":
                    if type(infobody.getText()) == str:
                        infotext = infotext + infobody.getText().replace(u'\u3000', u' ').replace(u'\xa0',
                                                                                                  u' ').strip()
            return infotext
        '''
        # 防止span标签被多次提取
        def getInfoByBody(soup, infobody, infotext):
            if infobody != None:
                if type(infobody.getText()) == str:
                    infotext = infotext + infobody.getText().replace(u'\u3000', u' ').replace(u'\xa0', u' ').strip()
            return infotext

        '''
        # 抓取正文内容
        infotext = ""
        infobody = soup.find('div', attrs={'style': 'align-content: center;'})
        # 最主要的标签
        infotext = getInfoByBody(soup, infobody, infotext)
        # 如果还没抓到正文，换标签
        if infotext == "":
            infobody = soup.find('div', attrs={'ergodic': 'article'})
            infotext = getInfoByBody(soup, infobody, infotext)

        # 抓取附件信息
        filesurl = []
        filesname = []

        filebody = soup.find('div', attrs={'class': 'chancolor'})
        if filebody != None:
            fileAtags = filebody.findAll('a')
            for item in fileAtags:
                fileurl = item.get('href')
                # 注意：有可能有html类型的链接
                if fileurl.find("down.do") != -1:
                    filename = item.getText()
                    filesurl.append(fileurl)
                    filesname.append(filename)
                    # print(filename)
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        result = [title, department, themeclass, serveclass, dispatchtime, pubtime, infotext, str(filesurl), str(filesname),
                  nowtime]

        #print(result)
        print(len(infotext))
        return result

    except:
        traceback.print_exc()
        return 2


if __name__=='__main__':
    get_page("http://www.shandong.gov.cn/sdxxgk/publi/message/detail.do?identifier=ml_0123-00-2019-000006")