from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)

db = client['work']

vacancy_new = db.vacancy_new

# 'https://hh.ru/search/vacancy?area=78&text=python&from=suggest_post&page=0&hhtmFrom=vacancy_search_list'
main_url = 'https://hh.ru'
id = 1
vacancy = 'python'
page = 0
all_vacancies = []
params = {'area': 78,
          'text': vacancy,
          'from': 'suggest_post',
          'page': page,
          'hhtmFrom': 'vacancy_search_list'}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/102.0.5005.61 Safari/537.36'}
response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)
soup = bs(response.text, 'html.parser')
try:
    last_page = int(soup.find_all('span', {'data-qa': 'pager-page'})[-1].text)
except:
    last_page = 1

for i in range(last_page):
    vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})
    for vacancy in vacancies:

        vacancy_info = {}
        vacancy_id = id
        vacancy_info['_id'] = vacancy_id
        id += 1

        vacancy_start = vacancy.find('a', {'data-qa': "vacancy-serp__vacancy-title"})
        vacancy_name = vacancy_start.text
        vacancy_info['Вакансия'] = vacancy_name

        vacancy_href = vacancy_start['href']
        vacancy_info['Ссылка на вакансию'] = vacancy_href

        vacancy_info['Сайт'] = 'HH.ru'
        vacancy_salary = vacancy.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"})
        if vacancy_salary is None:
            min_salary = None
            max_salary = None
            currency = None
        else:
            vacancy_salary = vacancy_salary.text
            if vacancy_salary.startswith('от'):
                min_salary = int("".join([s for s in vacancy_salary.split() if s.isdigit()]))
                max_salary = None
                currency = vacancy_salary.split()[-1]

            elif vacancy_salary.startswith('до'):
                min_salary = None
                max_salary = int("".join([s for s in vacancy_salary.split() if s.isdigit()]))
                currency = vacancy_salary.split()[-1]

            else:
                min_salary = int("".join([s for s in vacancy_salary.split('–')[0] if s.isdigit()]))
                max_salary = int("".join([s for s in vacancy_salary.split('–')[1] if s.isdigit()]))
                currency = vacancy_salary.split()[-1]
            vacancy_info['От'] = min_salary
            vacancy_info['До'] = max_salary
            vacancy_info['Денежная единица'] = currency

            all_vacancies.append(vacancy_info)

    params['page'] += 1
    response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)


# Вывод вакансий, у которых не повторяются _id
def id():
    for y in all_vacancies:
        try:
            vacancy_new.insert_one(y)
        except dke:
            print(f'Документ с id = {y["_id"]} уже существует в базе')


id()


for i in vacancy_new.find({}):
    pprint(i)


# Вывод вакансий, где зп "От" больше 90000 "До" больше или равняется 145000
# def vacancy_salary():
#     for z in vacancy_new.find({'От': {'$gt': 90000}, 'До': {'$gte': 145000}}):
#         pprint(z)
#
#
# vacancy_salary()

# Удаление коллекции из БД
# db.drop_collection('vacancy_new')
