import time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common import ElementClickInterceptedException

client = MongoClient('localhost', 27017)

db = client['LettersDB']

letters_collection = db.letters

s = Service('./chromedriver.exe')
options = Options()
options.add_argument('start-maximized')

driver = webdriver.Chrome(service=s, options=options)

driver.get('https://mail.ru')
driver.implicitly_wait(10)

button = driver.find_element(By.XPATH,
                             "//button[@class='resplash-btn "
                             "resplash-btn_primary "
                             "resplash-btn_mailbox-big gfb__aifb-de8k2m']")
button.click()

iframe = driver.find_element(By.XPATH,
                             "//iframe[contains(@class,"
                             "'ag-popup__frame__layout__iframe')]")
driver.switch_to.frame(iframe)

input_data = driver.find_element(By.NAME, "username")
input_data.send_keys('study.ai_172@mail.ru')
input_data.send_keys(Keys.ENTER)

input_data = driver.find_element(By.NAME, "password")
input_data.send_keys('NextPassword172#')
input_data.send_keys(Keys.ENTER)

driver.switch_to.default_content()

letter = driver.find_element(By.XPATH,
                          "//div[@class='ReactVirtualized__Grid__innerScrollContainer']/a").click()

arrow = driver.find_element(By.XPATH,
                             "//div[@class='portal-menu-element "
                             "portal-menu-element_next "
                             "portal-menu-element_expanded "
                             "portal-menu-element_not-touch']/span")
is_disabled = arrow.get_attribute("disabled")

mail = {}
try:
    while is_disabled is None:
        send_from = driver.find_element(By.XPATH,
                                        "//div[@class='letter__author']/"
                                        "span[@class='letter-contact']").text
        send_date = driver.find_element(By.XPATH,
                                        "//div[@class='letter__author']/"
                                        "div[@class='letter__date']").text
        send_letter = driver.find_element(By.XPATH,
                                     "//div[@class='letter-body']").text
        mail["from"] = send_from
        mail["date"] = send_date
        mail["letter"] = send_letter
        arrow.click()
        time.sleep(1)
        letters_collection.insert_one(mail)
        mail = {}
except ElementClickInterceptedException:
    print("Готово!")
except DuplicateKeyError:
    print("Элемент с таким id уже существует")
