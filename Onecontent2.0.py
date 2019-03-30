#coding=utf-8
#增加了采集规则
from bs4 import BeautifulSoup
import requests
import re
import time
import traceback
import queue
import threading


def get_page(viewHref):
    time.sleep(1.5)
    print(viewHref)
    try:
        r = requests.get(viewHref, timeout=30, headers=headers)
        r.encoding = r.apparent_encoding
        html = r.text
    except:
        # 连接错误 logUrlConnectError
        traceback.print_exc()
        return 1

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
                textpat = re.compile(r'p|span|ul')
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
                        infotext = infotext + infobody.getText().replace(u'\u3000', u' ').replace(u'\xa0', u' ').strip()
            return infotext

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

        result = [title, department, themeclass, serveclass, dispatchtime,
                  pubtime, infotext, str(filesurl), str(filesname),nowtime]

        print(result)
        print(len(infotext))
        return result

    except:
        traceback.print_exc()
        return 2