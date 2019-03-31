#coding=utf-8
import time
#----------------------------日志记录---------------------
#链接页面的URL是随时间滚动的，记录某时刻爬取错误的链接页面只是
#为了记录爬取不成功的数量，不会对其进行再次爬取，因此允许重复，不必对内容去重
#爬取URL的界面如果加载错误，记录
def logUrlConnectError(viewHref):
    #URL页面由于随时间滚动，日志也要记录一下时间
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    with open('error_url_connect.txt', 'a+') as f:
        f.write(str(viewHref)+" "+str(nowtime))
        f.write('\n')
#爬取URL的界面如果内容格式错误，记录
def logUrlFormError(viewHref):
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    with open('error_url_form.txt', 'a+') as f:
        f.write(str(viewHref) + " " + str(nowtime))
        f.write('\n')

#对信息内容页面的日志内容，需要去重处理
#爬取信息内容界面如果连接错误，记录
def logContentConnectError(viewHref):
    with open('error_content_connect.txt', 'a+') as f:
        hreflist = f.read().splitlines()
        if viewHref not in hreflist:
            f.write(str(viewHref))
            f.write('\n')

# 爬取信息内容界面如果内容格式错误，记录
def logContentFormError(viewHref):
    with open('error_content_form.txt', 'a+') as f:
        hreflist = f.read().splitlines()
        if viewHref not in hreflist:
            f.write(str(viewHref))
            f.write('\n')


#读取爬URL错误的记录
def readErrorUrl():
    datelist=[]
    with open('error_url_connect.txt','r') as f:
        datelist=f.read().splitlines()

    return datelist
#重新爬取成功，删除log
def deleteErrorUrl(viewHref):
    with open('error_url_connect.txt', 'r+') as f:
        hreflist = f.read().splitlines()
        #文件指针指向开头并删除所有记录
        f.seek(0)
        f.truncate()
        if viewHref not in hreflist:
            f.write(str(viewHref))
            f.write('\n')
