# coding:UTF-8
import csv
import datetime
import json
import os
from urllib.parse import urlparse

import pandas as pd
import queue
import requests
import sys

requests.packages.urllib3.disable_warnings()
headers={'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Mobile Safari/537.36',
         'Referer':'http://m.maoyan.com/shows/25906?$from=canary'}

def crawl_cinema(args):
    city = args[0]
    cinema = args[1]
    search_date = args[2]
    cinemaFile = args[3]
    cityList = json.load(open('maoyan_city.json', 'r', encoding='utf-8'))
    cityId = None
    cityId = cityList[city]
    if cityId == None:
        print('输入的城市名称不存在')
        exit(1)
    res = requests.get(
        'http://m.maoyan.com/ajax/search?kw=%s&cityId=%s&stype=2' % (
            datetime.datetime.now().date(), cityId), verify=False,headerr=headers)
    cinemaList = []
    if len(res.json()['cinemas']['list']) == 0:
        print('无搜索结果')
        # nyj增加
        os.remove(cinemaFile)
    else:

        # nyj20181112
        # if not os.path.exists(file + '.csv'):
        #    conditon = True

        # with open(file + '.csv', 'w', newline='',encoding='utf-8') as f:
        #    fieldnames = field
        #    writer = csv.DictWriter(f, fieldnames=fieldnames)
        # 如果不存在这个目录就创建
        # nyj20181112
        if not os.path.exists(os.path.dirname(cinemaFile)):
            os.makedirs(os.path.dirname(cinemaFile))
        for x in res.json()['cinemas']['list']:
            url = 'http://m.maoyan.com/shows/%s/' % (x['id'])
            cinemaList.append(x['nm'] + "," + url + '\n')
        # f=open(cinemaFile, 'w',encoding='utf-8')
        f = open(cinemaFile, 'w', encoding='gbk')
        for c in cinemaList:
            f.write(c)
        f.close()
        print('保存影院数据成功,文件名为%s' % cinemaFile)


def crawl_showTimes(args):
    url = args[0]
    resultFile = args[1]
    cinemaId = ''.join(filter(str.isdigit,url.split('/')))
    url = "http://m.maoyan.com/ajax/cinemaDetail?cinemaId=%s" % cinemaId
    res = requests.get(url, verify=False,headers=headers)
    data = res.json()
    showTimesList = []
    imageInfo = []
    movies = data['showData']['movies']
    for m in movies:
        moviesName = m['nm']
        moviesType= m['desc'].split('|')[1]
        imgUrl = m['img'].replace('w.h','123.234')
        imageInfo.append({'title': moviesName, 'url': imgUrl, 'file': resultFile})
        showtimes = m['shows']
        for s in showtimes:
            for i in s['plist']:
                date = i['dt']
                time=i['tm']
                # if dateArray.date().strftime("%Y%m%d") == search_date:
                showTimesList.append(
                        {'播出日期':date, '播出时间': time, '影片名称': moviesName, '影厅名称': i['th'],
                         '影片类型': moviesType, '影片样式': i['tp'] + " " + i['lang']})
    if (len(showTimesList)) == 0:
        print("当日无搜索结果")
        delete_img(resultFile)
    else:
        save_img(imageInfo)
    save_data(showTimesList, resultFile)
    csv_to_excel(resultFile)


def delete_img(resultFile):
    dirName = os.path.dirname(resultFile)
    if not dirName:
        dirName = os.getcwd()
    if not os.path.exists(dirName):
        os.mkdir(dirName)
    files = os.listdir(dirName)
    for file in files:
        if file.split('.')[1] == 'jpg':
            os.remove(dirName + '/' + file)


def save_img(imageInfo):
    for i in imageInfo:
        movieName = i['title']
        imgUrl = i['url']
        resultFile = i['file']
        res = requests.get(imgUrl,headers=headers)
        dirName = os.path.dirname(resultFile)
        if not dirName:
            dirName = os.getcwd()
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        with open(dirName + '/' + movieName + '.jpg', 'wb')as f:
            f.write(res.content)


def save_data(data_list, fileName):
    try:
        conditon = False
        file = fileName.split('.')[0]

        if not os.path.exists(file + '.csv'):
            conditon = True

        with open(file + '.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = field
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()

            for data in data_list:
                writer.writerow(data)
            if len(data_list) == 0:
                writer.writerow({'播出日期': "本日无结果"})
    except Exception as e:
        print('保存数据错误', e)
    else:
        print("保存数据成功,文件名为%s" % fileName)


def csv_to_excel(fileName):
    file = fileName.split('.')[0]
    data = pd.read_csv(file + '.csv', encoding='utf-8')
    data.to_excel(fileName, index=False, encoding='utf-8')


if __name__ == '__main__':
    # field = ['播出日期', '播出时间', '影片名称', '影厅名称', '影片类型', '影片样式']
    # argv = sys.argv[1:]
    # if len(argv) == 4:
    #     crawl_cinema(argv)
    # if len(argv) == 2:
    #     crawl_showTimes(argv)
    date=''