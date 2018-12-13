from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')
def re_search(request):
    import time
    search_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
    import pymysql
    cnn = pymysql.connect(host="localhost",user="root",password="9527",db='movie',charset="utf8")
    cursor = cnn.cursor()
    createTab = """CREATE TABLE IF NOT EXISTS movie_search(
            num_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            search_time VARCHAR(20) NULL,
            title  TEXT NULL,
            content  TEXT NULL
            )"""
    cursor.execute(createTab)
    # print('db success')
    import requests
    import json
    from bs4 import BeautifulSoup
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }
    movie = request.GET['text']
    # 测试https://v.qq.com/x/cover/dzn1zjs53yvpvij/d0027j8xpic.html
    try:
        if len(movie)>40:
            # print(len(movie))
            jiexi_url = 'http://app.baiyug.cn:2019/vip/index.php'
            # 按照格式
            para = {
                'url':movie,
            }
            # 按照格式
            headers ={
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.9',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Cookie':'Hm_lvt_ffcba8bba444f065b18b388402d00e95=1540042238,1540042245,1540045044,1540045044; Hm_lpvt_ffcba8bba444f065b18b388402d00e95=1540045046',
                'Host':'app.baiyug.cn:2019',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            }
            html = requests.get(jiexi_url,params=para,headers=headers)

            title = movie
            sql = "INSERT INTO `movie_search`(search_time,content,title) VALUES(%s,%s,%s)"
            cursor.execute(sql,(search_time,html.url,title))
            cnn.commit()
            content = [html.url]
            return render(request, 're_search.html',{ 'content':content,'title':'点击即可观看'})
        else:
            url = 'http://v1.yn-dove.cn/zy-'+movie+'-zwone.html?tl='+movie
            html = requests.get(url,headers=header)
            data_resource = json.loads(html.text)['show']
            URL = BeautifulSoup(data_resource,'lxml').find_all('a')
            text1 = []
            movie_name = []
            for i in URL:
                real_url = i.get('href')
                if real_url:
                    real_url1 = ('http://v1.yn-dove.cn'+real_url).replace('zyplays','zyplay')
                    movie_title = i.get('title')
                    html1 = requests.get(real_url1,headers=header)
                    data_resource1 = json.loads(html1.text)['show']
                    URL1 = BeautifulSoup(data_resource1,'lxml').find_all('a')
                    num = 1
                    for i in URL1:
                        real_url1 = i.get('href')
                        if real_url1.endswith('html') and num <= 1:
                            real = 'http://v1.yn-dove.cn/'+real_url1
                            num += 1
                            text1.append(real)
            content = text1[0]
            title = movie
            sql = "INSERT INTO `movie_search`(search_time,content,title) VALUES(%s,%s,%s)"
            cursor.execute(sql,(search_time,content,title))
            cnn.commit()
            return render(request, 're_search.html',{ 'content':text1,'title':movie})
    except Exception as e:
        #     ['http://v1.yn-dove.cn/jx-m3u8-aHR0cHM6Ly9sZXR2LmNvbS12LWxldHYuY29tLzIwMTgxMDA0Lzc0NzZfYTdlNmE4N2UvaW5kZXgubTN1OA.html', '江湖儿女BD']
        return HttpResponse('请重新搜索')


