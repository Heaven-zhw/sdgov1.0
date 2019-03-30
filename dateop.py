#coding=utf-8
import datetime
import traceback
#返回date2与date1相差几天
def dateDelta(date1,date2):
    d2=datetime.datetime.strptime(date2,'%Y%m%d')
    d1=datetime.datetime.strptime(date1,'%Y%m%d')
    delta=d2-d1
    return delta.days
s="down1.do"
href="/sdxxgk/publi/message/down.do?id=039539"
print(href.find(s))
date1="2001-01-02"
date2="2000-01-06"
print(int(1e5))
try:
    ilist = [3, 5]
    ilist.insert(0,1)
    s1=str(ilist)
    print(s1)
    a=eval(s1)
    if date1>date2:
        #a=5/0
        raise Exception("error")

except:
    traceback.print_exc()
