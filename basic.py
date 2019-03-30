import time
import requests
import traceback

def getHTMLText(href,header):
    # 重复尝试10次，第10次失败后才返回错误
    for i in range(10):
        try:
            r = requests.get(href, timeout=30, headers=header)

            if r.encoding == 'ISO-8859-1':
                encodings = requests.utils.get_encodings_from_content(r.text)
                if encodings:
                    encoding = encodings[0]
                else:
                    encoding = r.apparent_encoding
                # encode_content = req.content.decode(encoding, 'replace').encode('utf-8', 'replace')
                global encode_content
                encode_content = r.content.decode(encoding, 'replace')  # 如果设置为replace，则会用?取代非法字符；
                html = encode_content
            else:
                html = r.text
        except:
            if i>=9:
                # 连接错误 logUrlConnectError
                traceback.print_exc()
                return -1
            else:
                print("第",i+2,"次尝试",href)
                time.sleep(0.5)
        else:
            time.sleep(0.1)
            return html

if __name__ =='__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    print(getHTMLText("http://www.shandong.gov.cn/sdxxgk/publi/message/detail.do?identifier=ml_0302-04-2018-000163",headers))