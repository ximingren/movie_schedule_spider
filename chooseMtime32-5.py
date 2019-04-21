# coding:UTF-8
import csv
import datetime
import json
import os
import pandas as pd
import queue
import requests
import sys

requests.packages.urllib3.disable_warnings()


def crawl_cinema(args):
    city = args[0]
    cinema = args[1]
    search_date = args[2]
    cinemaFile = args[3]
    cityList = json.load(open('city.json', 'r', encoding='utf-8'))
    cityId = None
    for i in cityList['locations']['List']:
        if i['NameCn'] == city:
            cityId = i['Id']
    if cityId == None:
        print('输入的城市名称不存在')
        exit(1)
    res = requests.get(
        'http://m.mtime.cn/Service/callback.mi/Showtime/SearchVoice.api?keyword=%s&searchType=3&locationId=%s' % (
            cinema, cityId), verify=False)
    cinemaList = []
    if res.json()['locationCinemasCount'] == 0:
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

        for x in res.json()['locationCinemas']:
            url = 'http://m.mtime.cn/#!/theater/%s/%s/date/%s/' % (cityId, x['id'], search_date)
            cinemaList.append(x['name'] + "," + url + '\n')
        # f=open(cinemaFile, 'w',encoding='utf-8')
        f = open(cinemaFile, 'w', encoding='gbk')
        for c in cinemaList:
            f.write(c)
        f.close()
        print('保存影院数据成功,文件名为%s' % cinemaFile)


def crawl_showTimes(args):
    url = args[0]
    resultFile = args[1]
    index = url.split('/').index('date') - 1
    date_index = url.split('/').index('date') + 1
    search_date = url.split('/')[date_index]
    cinemaId = (url.split('/')[index])
    url = "https://ticket-api-m.mtime.cn/cinema/showtime.api?cinemaId=%s" % cinemaId
    res = requests.get(url, verify=False)
    data = res.json()
    showTimesList = []
    moviesName = {}
    moviesType = {}
    imageInfo = []
    if data['msg'] != '成功':
        print("抓取失败请稍候再试")
    else:
        cinema = data['data']['cinema']['name']
        movies = data['data']['movies']
        for m in movies:
            moviesName[m['movieId']] = m['title']
            moviesType[m['movieId']] = m['type']
            imgUrl = m['img']
            imageInfo.append({'title': m['title'], 'url': imgUrl, 'file': resultFile})

    showtimes = data['data']['showtimes']
    for s in showtimes:
        movieId = s['movieId']
        for i in s['list']:
            timeStamp = i['showDay']
            dateArray = datetime.datetime.fromtimestamp(timeStamp)

            if dateArray.date().strftime("%Y%m%d") == search_date:
                showTimesList.append(
                    {'播出日期': dateArray.date(), '播出时间': dateArray.time(), '影片名称': moviesName[movieId], '影厅名称': i['hall'],
                     '影片类型': moviesType[movieId], '影片样式': i['versionDesc'] + " " + i['language']})
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
        res = requests.get(imgUrl)
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
    field = ['播出日期', '播出时间', '影片名称', '影厅名称', '影片类型', '影片样式']
    argv = sys.argv[1:]
    if len(argv) == 4:
        crawl_cinema(argv)
    if len(argv) == 2:
        crawl_showTimes(argv)