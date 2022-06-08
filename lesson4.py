import re
from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke

client = MongoClient('127.0.0.1', 27017)

db = client['news']

news = db.news

url = 'https://lenta.ru/'
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 '
                  'Safari/537.36'}

response = requests.get(url, headers=headers)

dom = html.fromstring(response.text)

items = dom.xpath("//a[@class='card-mini _topnews']")

list_items = []
for item in items:
    item_info = {}
    source = ['lenta.ru', 'moslenta.ru']
    name = item.xpath(".//div/span//text()")
    link = item.xpath("./@href")
    publication_time = item.xpath(".//div/div/time//text()")

    # _id формировала исходя из ссылки на новость, извлекла уникальные строковые данные(так как числовых данных в ссылке
    # не было совсем), каждый символ преобразовала к числу с помощью ord и сделала этот номер уникальным.
    # Разделила новости Мосленты и Ленты. Для каждого источника своя ссылка
    if link[0].find("https://moslenta.ru") != -1:
        item_info['source'] = source[1]
        item_info['link'] = link[0]
        news_id = re.split('/', link[0])[5][:-4]
        news_ord = [str(ord(x)) for x in news_id]
        k = "".join(news_ord)
        item_info['_id'] = int(k[:18])

    else:
        item_info['source'] = source[0]
        item_info['link'] = 'https://lenta.ru' + link[0]
        news_id = re.split('/', link[0])[5]
        news_ord = [str(ord(x)) for x in news_id]
        k = "".join(news_ord)
        item_info['_id'] = int(k[:18])

    item_info['name'] = name[0]
    item_info['publication_time'] = publication_time[0]
    list_items.append(item_info)

for y in list_items:
    try:
        news.insert_one(y)
    except dke:
        print(f'Документ с id = {y["_id"]} уже существует в базе')
for b in news.find({}):
    pprint(b)
# db.drop_collection('news')
