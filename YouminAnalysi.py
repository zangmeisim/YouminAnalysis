from bs4 import BeautifulSoup
from urllib.request import urlopen
import pyhdb
import datetime
import requests
import re
import datetime

def get_connect():   # 连接数据库信息
    conn_obj = pyhdb.connect(
        host='10.150.16.99',
        port = 30015,
        user = 'sapabap2',
        password = 'Sap_7890'
    )
    return conn_obj

def intohana_grandcat(conn,id,cate,site):
    cursor = conn.cursor()
    cursor.execute('insert into ZANG_TEST_GRANDCAT (GRANDCAT_ID,GRANDCAT_NAME,SITE,UPDATE_DATE) values(%s,%s,%s,%s)',(id,cate,site,current_date))

def intohana_game(conn,grand_id,grand_name,game_id,game_name,site):
    cursor = conn.cursor()
    cursor.execute('insert into ZANG_TEST_GAM (GRAND_ID,GRAND_NAME,GAME_ID,GAME_NAME,GAME_SITE,UPDATE_DATE) values(%s,%s,%s,%s,%s,%s) ',(grand_id,grand_name,game_id,game_name,site,current_date))
    updateSQL="insert into SAPABAP2.ZANG_TEST_GAM_NEW (select a.GRAND_ID,a.GRAND_NAME,a.GAME_ID,a.GAME_NAME,a.GAME_SITE,a.UPDATE_DATE from SAPABAP2.ZANG_TEST_GAM a where a.GAME_ID not in (select GAME_ID from SAPABAP2.ZANG_TEST_GAM_NEW)) "
    cursor.execute(updateSQL)


def intohana_blogdetail(conn,GRAND_ID,GAME_ID,GAME_NAME,BLOG_TYPE,BLOG_THEME,REPLY_NUM,
                        READ_NUM,CREATOR,CREATE_TIME,LAST_REPLIER,LAST_REPLY_TIME,UPDATE_TIME):
    cursor = conn.cursor()
    cursor.execute('insert into ZANG_TEST_BLOG_DETAIL (GRAND_ID,GAME_ID,GAME_NAME,BLOG_TYPE,BLOG_THEME,REPLY_NUM,READ_NUM,CREATOR,CREATE_TIME,LAST_REPLIER,LAST_REPLY_TIME,UPDATE_TIME) '
                   'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ',
                   (GRAND_ID,GAME_ID,GAME_NAME,BLOG_TYPE,BLOG_THEME,REPLY_NUM,
                        READ_NUM,CREATOR,CREATE_TIME,LAST_REPLIER,LAST_REPLY_TIME,UPDATE_TIME))

    updateSQL="insert into SAPABAP2.ZANG_TEST_BLOG_DETAIL_NEW (select GRAND_ID,GAME_ID,GAME_NAME,BLOG_TYPE,BLOG_THEME,REPLY_NUM,READ_NUM,CREATOR,CREATE_TIME,LAST_REPLIER,LAST_REPLY_TIME,UPDATE_TIME from SAPABAP2.ZANG_TEST_BLOG_DETAIL   where BLOG_THEME not in (select BLOG_THEME from SAPABAP2.ZANG_TEST_BLOG_DETAIL_NEW)) "
    cursor.execute(updateSQL)


def delete_grandcat(conn):
    cursor = conn.cursor()
    cursor.execute('truncate table ZANG_TEST_GRANDCAT')
    cursor.execute('truncate table ZANG_TEST_GAM')
    cursor.execute('truncate table ZANG_TEST_BLOG_DETAIL')



def check_contain_chinese(check_str):
    for ch in check_str:
         if u'\u4e00' <= ch <= u'\u9fff':
           return True
    return False


def getgrand(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}  # 设置头文件信息 #
    response = requests.get(url, headers=headers).content  # 提交requests get 请求
    soup = BeautifulSoup(response, "html.parser")  # 用Beautifulsoup 进行解析
    commid = soup.findAll('a', class_='xi2')
    for commid2 in commid[2:-1]: ##爬取论坛首页
        href=commid2.get("href")
        if len(href.split("-"))>=2 :
            id=href.split("-")[1]
            site=url+href
            print(site)
            cate=commid2.text
            if check_contain_chinese(cate) == True:
                response2 = requests.get(site, headers=headers).content  # 提交requests get 请求
                soup2= BeautifulSoup(response2, "html.parser")  # 用Beautifulsoup 进行解析
                catmid=soup2.findAll('dt')
                intohana_grandcat(conn, id, cate, site)
                # print(catmid)
                # print(cate)
                for catmid2 in catmid: ##爬取每个游戏类型首页
                    a=catmid2.findAll("a")[0]
                    href2=a.get("href")
                    gamename=a.text
                    # print(gamename)
                    if (len(href2.split("-"))>=2) & (href2[-4:]=="html") :
                        site2=url+href2
                        id2=href2.split("-")[1]

                #         print(a)
                #         print(id2)
                #         print(site2)
                        intohana_game(conn, id, cate, id2, gamename, site2)
                        getdetail(site2,conn,id,id2,gamename)  ## get detail of blog information



def getdetail(site,conn,GRAND_ID,GAME_ID,GAME_NAME):  ## get detail of blog information
    globals()
    type=''
    theme=''
    replynum=''
    readnum=''
    editor=''
    createdate=''
    lastreply=''
    lastreplydate=''

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}  # 设置头文件信息 #

    response3 = requests.get(site, headers=headers).content  # 提交requests get 请求
    soup3 = BeautifulSoup(response3, "html.parser")  # 用Beautifulsoup 进行解析
    gamemid = soup3.findAll('th', class_='new')
    td = soup3.findAll('td', class_='by')
    for tbody in soup3.findAll('tbody'):
        for tr in tbody.findAll('tr'):
            for new in tr.findAll('th', class_='new'):  ##get title
                em = new.find('em')
                if em:
                    type = em.text[1:-1]
                else:
                    type = ''
                theme = new.find('a', class_='s xst').text
                num = tr.find('td', class_='num')  ###get reply & read
                if num:
                    replynum = num.find('a').text
                    readnum = num.find('em').text
                else:
                    replynum='0'
                    readnum='0'
                # print(type, theme, replynum, readnum)
            by = tr.findAll('td', class_='by')  # get editor & date
            if by:
                for uby in by[:1]:  # get editor & date
                    createdate = uby.find('em').text
                    editor = uby.find('cite').text
                # print(editor,createdate)
                for uby in by[1:]:  # get editor & date
                    lastreply = uby.find('cite').text
                    lastreplydate = uby.find('em').text
                # print(editor, createdate, lastreply, lastreplydate)
                # print(lastreply, lastreplydate)
            intohana_blogdetail(conn,GRAND_ID,GAME_ID,GAME_NAME,type,theme,replynum,
                                readnum,editor,createdate,lastreply,lastreplydate,current_daytime)






if __name__ == '__main__':
    globals()
    conn = get_connect()
    current_date = datetime.datetime.now()
    current_daytime = current_date.strftime('%Y-%m-%d %H:%M:%S')
    url = 'http://bbs.3dmgame.com/'

    delete_grandcat(conn)
    getgrand(url)
    conn.commit()
    print('Update complted')
