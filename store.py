#coding=utf-8
import pymysql
import traceback

#----------------数据库配置---------------------------------
host="10.245.144.96"          #数据库地址
user="user"                   #用户名
passwd="123456"               #密码
charset="utf8"                #字符编码
database="sdgov2"             #数据库
urlTable="infourl"            #存信息链接的数据表表名
contentTable="infocontent"    #存信息内容法数据表表名

#----------------Mysql操作---------------------------------
#存链接
def saveUrls(hreflist):  # tagname在此默认与table名称相同
    try:
        conn = pymysql.connect(host=host, user=user, password=passwd, db=database, charset=charset)
        cur = conn.cursor()
        sql = "INSERT ignore INTO {} (url,flag,department,pubdate,gaintime) " \
              "VALUE(%s,%s,%s,str_to_date(%s,'%%Y-%%m-%%d'),%s)".format(urlTable)  # 用(%d,%s)会报错，pymysql的自身bug
        print(sql)

        for item in hreflist:
            cur.execute(sql, item)
        conn.commit()
        print("URL存储成功！")
    except Exception as e:
        print("存储URL时出错！")
        print(e)
        conn.rollback()
    finally:
        conn.close()

#读取当前数据库中数据的最新日期
def readLatest():
    try:
        urllist = []
        conn = pymysql.connect(host=host, user=user, password=passwd, db=database, charset=charset)
        cur = conn.cursor()

        sql = "select date_format(pubdate, '%Y-%m-%d') from {} " \
              "order by pubdate desc limit 1".format(urlTable)
        # print(sql)
        cur.execute(sql)
        result = cur.fetchone()
        conn.close()
        #print(result)
        return result
    except:
        print("读取URL时数据库错误!")
        # traceback.print_exc()
        conn.close()
        return 1

#从链接数据表里读取指定数目的未爬取过的链接
def readUrls(count=1000):
    try:
        urllist = []
        conn = pymysql.connect(host=host, user=user, password=passwd, db=database, charset=charset)
        cur = conn.cursor()

        sql = "select id,url from {} where flag=0 limit ".format(urlTable) + str(count)
        # print(sql)
        cur.execute(sql)
        results = cur.fetchall()
        #print(results) #元组类型
        #for item in results:
        #   urllist.append(list(item))
        #print(urllist)
        conn.close()
        print(len(results))
        return results
    except:
        print("读取URL时数据库错误!")
        # traceback.print_exc()
        conn.close()
        return 1

#存内容并更新爬取完成标志位
def saveContent(id,result):
    try:
        conn = pymysql.connect(host=host, user=user, password=passwd, db=database, charset=charset)
        cur = conn.cursor()
        result.insert(0,id)
        #print(result)
        sql1="INSERT ignore INTO {} " \
             "(id,title,department,themeclass,serveclass,dispatchtime,pubtime,infotext,filesurl,filesname,gaintime) " \
             "VALUE(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(contentTable)
        cur.execute(sql1, result)
        conn.commit()

        #更新标志位为已经爬取成功
        sql2="update {} set flag=1 where id=%s".format(urlTable)
        cur.execute(sql2,id)
        conn.commit()

        print("网页信息存储成功！")
    except Exception as e:
        print("存储网页信息时出错！")
        #print(e)
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

#更新标志位为信息格式错误
def updateErrorFlag(id):
    try:
        conn = pymysql.connect(host=host, user=user, password=passwd, db=database, charset=charset)
        cur = conn.cursor()
        sql = "update {} set flag=2 where id=%s".format(urlTable)
        cur.execute(sql, id)
        conn.commit()

        print("flag更新成功！")
    except Exception as e:
        print("flag更新时出错！")
        print(e)
        conn.rollback()
    finally:
        conn.close()
'''
if __name__=='__main__':
    readUrls()



# 获取总条数
def readUrlNum(tagname):
    try:
        urllist = []
        conn = pymysql.connect(host=host, user=user, password=passwd, db=database, charset=charset)
        cur = conn.cursor()
        sql = "select count(1) from " + tagname
        cur.execute(sql)
        num = cur.fetchone()
        conn.close()
        return int(num[0])

    except:
        print("读取URL数量时数据库错误!")
        traceback.print_exc()
        conn.close()
        return []

'''
if __name__ =='__main__':
    #result=['2019年山东省文化和旅游厅 所属事业单位公开招聘工作人员考察体检公示', '山东省文化和旅游厅', '文化、广电、新闻出版', '全部', '2019-03-26 00:00:00', '2019-03-26 18:47:58', '根据省人社厅《关于2019年省属事业单位公开招聘工作人员有关问题的通知》要求，2019年省文化和旅游厅所属省文化艺术学校、省艺术研究院等2个事业单位公开招聘工作人员考试工作已经结束。根据省人社厅规定：“面试结束后，按笔试成绩和面试成绩各占50％的比例，百分制计算应聘人员考试总成绩。同一招聘岗位应聘人员出现总成绩并列的，按笔试成绩由高分到低分确定进入考察范围人选”，“按照招聘岗位，根据应聘人员考试总成绩，由高分到低分不高于1:1.5的比例，确定进入考察范围人选，组织考察。对考察合格人员，按照招聘人数1:1的比例确定进入体检范围人选。”现将参加等额考察体检人员及进入递补考察体检范围人员情况公示如下：\n\n\n参加等额考察体检人员名单\n序号\n招聘单位\n名称\n岗位名称\n姓名\n准考证号\n笔试成绩\n面试成绩\n总成绩\n1\n山东省文化艺术学校\n英语教师\n张莹\n201902002\n81.50\n90.00\n85.75\n2\n工艺美术教师\n崔爽\n201902007\n90.50\n89.00\n89.75\n3\n山东省艺术研究院\n影视制作与剪辑\n孟傲\n201901033\n92.50\n91.60\n92.05\n4\n会计\n王辉\n201901028\n79.00\n79.60\n79.30\n\n\n\n\n\n进入递补考察体检范围人员名单\n序号\n招聘单位\n名称\n岗位名称\n姓名\n考生编号\n笔试成绩\n面试成绩\n总成绩\n1\n山东省文化艺术学校\n英语教师\n徐朋焕\n201902006\n79.00\n79.00\n79.00\n2\n工艺美术教师\n刘瑞新\n201902008\n87.50\n75.00\n81.25\n3\n山东省艺术研究院\n影视制作与剪辑\n高菲\n201901036\n87.00\n64.00\n75.50\n4\n会计\n张孝爽\n201901012\n72.00\n69.60\n70.80\n\n\n公示期：2019年3月26日-4月1日\n联系电话：0531-86568852 86568826\n\n山东省文化和旅游厅\n2019年3月26日\n', '[]', '[]', '2019-03-26 21:33:52']
    #saveContent(1,result)
    print(readLatest())