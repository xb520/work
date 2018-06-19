# from bs4 import BeautifulSoup

import requests
import re

# data = requests.get('https://www.lyngsat.com/packages/Sky-New-Zealand.html',headers=headers)
# print(data.text)
# soup = BeautifulSoup(data.text)
# #
f = open('dd.html','r',encoding='utf-8')

from lxml import etree
import pymysql


# with open('dd.html',"r",encoding='utf-8') as f:
#     f.read()
# print(f.read())

def conn_mysql():
    conn = pymysql.connect(
        # host='localhost',
        host='192.168.1.6',
        port=3306,
        user='root',
        passwd='root',
        # db='satellite',
        db ='aicms_512',
        charset='utf8'

    )

    return conn

def starting():
    conn = conn_mysql()
    cursor = conn.cursor()
    cursor.execute("select id,url from b_satellite")
    data = cursor.fetchall()
    for i in data:
        id = i[0]
        url = i[1]
        s = pop(url_path=url,id=id)

        for P_url in s:
            pop(P_url,id)

def pop(url_path,id):

    # 读取卫星表的值




    a = set()

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "www.lyngsat.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36",
    }

    data = requests.get(url = url_path, headers=headers)

    s = data.text

    package_html = etree.HTML(s)
    package = package_html.xpath('//td[5]/a/@href')

    for pack in package:
        a.add(pack)

    print(type(a))
    p = re.findall(r'<td rowspan.*?(?=<td rowspan)|<td rowspan.*?<\/table>',s,re.S)
    # package_url = []
    for i in p:


        #匹配每一个表格里的数据

        table = re.findall(r'<td rowspan.*?<\/tr>|<tr>.*?<\/tr>',i,re.S)
        # print(table,'>>>>>>>>>>>>>>>>>>>>>',y)
        for x in table:


            html = etree.HTML(x)

            title = html.xpath('//td/font[@face="Verdana"]/font/b/text()')
            # if not title:
            #     title = ''
            global Frequencys
            global Pol
            try:
                title = "".join(title)

                title = title.split()
                # print(title)
                Frequencys = int(title[0])

                Pol = title[1]

                if Pol == "H":

                    Pol = 0
                if Pol == "V":
                    Pol = 1
            except:
                title = ''




                #     print(Frequencys,Pol,)

            Channel = html.xpath('//td/font[@face="Arial"]/font/b/a/text()')
            Channel = ''.join(Channel)

            print(Channel)
            try:
                ApidSUM = html.xpath('//td[last()-1]/font[@face="Verdana"]/text()')
                ApidSUM = "".join(ApidSUM)
                ApidSUM = ApidSUM.split()
                Apid = ApidSUM[0]

                lang = ApidSUM[1]
            except:
                Apid = ''
                lang = ''


            # APid = Sum[0]
            # lang = Sum[1]
            print(Apid,'>>>>>>>',lang)

            Spid = html.xpath('//td[last()-3]/font[@face="Verdana"]/font/text()')
            Spid = ''.join(Spid)
            try:
                Spid = int(Spid)
            except:
                Spid = ''
            print(Spid)

            Source_updated = html.xpath('//td[last()]/font[@face="Verdana"]/text()')
            Source_updated = ''.join(Source_updated)
            print(Source_updated)

            Vpid = html.xpath('//td[last()-2]/font[@face="Verdana"]/text()')
            Vpid = ''.join(Vpid)
            print(Vpid)

            Encryption = html.xpath('//td[4]/font[@face="Verdana"]/text()')
            Encryption = ''.join(Encryption)
            print(Encryption)

            satalliteid = id

            url = html.xpath('//td/font[@face="Arial"]/font/b/a/@href')
            url = "".join(url)


            # package = html.xpath('//td[5]/a/@href/text()')
            # print(package)
            # package = ''.join(package)
            # package_url.append(package)

            open_mysql(Frequencys=Frequencys, Pol=Pol, Channel=Channel, satalliteid=satalliteid, Encryption=Encryption, Spid=Spid, Vpid=Vpid, Apid=Apid, lang=lang, Source_updated=Source_updated, url_path=url)

            # 插入数据库中





    return a
        # print(package_url)

def open_mysql(Frequencys, Pol, Channel, satalliteid, Encryption, Spid, Vpid, Apid, lang, Source_updated, url_path):

    # conn = pymysql.connect(
    #     host='localhost',
    #     port=3306,
    #     user='root',
    #     passwd='root',
    #     db='satellite',
    #     charset='utf8'
    #
    # )
    #
    # 更新数据
    conn = conn_mysql()
    cursor = conn.cursor()

    # cursor.execute('select * from b_tvchannel where %d+10<freq="%d"<%d+10 and sid="%s" and satelliteid=%d;'%(Frequencys,Frequencys,Frequencys,Spid,satalliteid))
    cursor.execute('select * from b_tvchannel where freq between %d and %d and sid="%s" and satelliteid=%d;'%(Frequencys-10, Frequencys+10, Spid,satalliteid))

    data = cursor.fetchall()
    # print(data,"]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]")
    if Channel and Spid:
        if data:
            for i in data:


                sql = 'update b_tvchannel set freq="%s", pol="%s", channel="%s",encryption="%s",vpid="%s",apid="%s",lang="%s",source_updated="%s",url="%s" where id=%d;'%(Frequencys,Pol,Channel,Encryption,Vpid,Apid,lang,Source_updated,url_path,i[0])
                # print(sql,"????????????????????????????????????????????????????????????????????????")
                try:
                    print("更新数据中")
                    cursor.execute(sql)
                    conn.commit()

                except:
                    print("更新数据出错")
                    # conn.rollback()
                    cursor.close()
                    conn.close()

        else:


            sql = 'insert into b_tvchannel(freq,pol,channel,satelliteid,encryption,sid,vpid,apid,lang,source_updated,url) values ("%s",' \
                  '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s");' % (
                  Frequencys, Pol, Channel, satalliteid, Encryption, Spid, Vpid, Apid, lang, Source_updated, url_path)



            print("插入数据")
            try:
                cursor.execute(sql)
                conn.commit()
            except:
                print("插入出错")
                conn.rollback()

                cursor.close()
                conn.close()
    else:
        cursor.close()
        conn.close()
        return 1
    #

    # title = "".join(title)
    # title = title.split()
    #
    # Frequencys = title[0]
    # Pol = title[1]
    #
    # Channel = html.xpath('//td/font[@face="Arial"]/font/b/a/text()')
    # satalliteid = ""
    # ApidSUM = html.xpath('//td[last()-1]/font[@face="Verdana"]/text()')
    # # ApidSUM = "".join(ApidSUM)
    # # ApidSUM = ApidSUM.split()
    # # Apid = ApidSUM[0]
    # # lang = ApidSUM[1]
    # pacjk = html.xpath('//td[5]/a/@href/text()')
    # Spid = html.xpath('//td[last()-3]/font[@face="Verdana"]/font/text()')
    # if Spid == "":
    #     Spid = 'no'
    # Source_updated = html.xpath('//td[last()]/font[@face="Verdana"]/text()')
    # Vpid = html.xpath('//td[last()-2]/font[@face="Verdana"]/text()')
    # # print(Frequencys, '>>>>>>>>>', Pol,'>>>>>>>',Channel,ApidSUM,pacjk,'>>>>>>>>>>',Spid,'>>>>>>>>>',Vpid,Source_updated)
    # y = y + 1
    # # print(i,'>>>>>>>>>>>>>>>>>>>>>>>>>>%s'%y)
    # # for j,k in zip(Channel,Spid):
    # #     print('节目名称:',j +':''对应的spid:',Spid)
    # # for j, k in zip(html.xpath('//td[5]/a/@href/text()'),html.xpath('//td[last()-3]/font[@face="Verdana"]/font/text()')):
    # #     print('nihai')
    # #     print('节目名称:', j + ':''+对应的spid:', k)
    # values = [''.join(col.replace('\xa0','')) for col in Spid]
    #
    # # info = dict(zip(Channel,values))
    # print(Channel)



if __name__ == '__main__':
    # s = pop(url_path='https://www.lyngsat.com/Optus-D1.html')

    # for P_url in s:
    #     pop(P_url)
    starting()







#  # # print(soup.tr)