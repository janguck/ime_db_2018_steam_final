from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime, timedelta
import pickle
from sqlalchemy import exc
import json
import sqlalchemy
import os
from models import *

def get_db_information():
    config = read_config()
    return """mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8""".format(config['db_id'],config['db_password'],config['host'],config['port'],config['db_name'])

def create_db():
    config = read_config()
    
    try:
        engine = sqlalchemy.create_engine(get_db_information())
        default_database_uri = os.path.join(os.path.dirname(str(engine.engine.url)), 'mysql')
        engine_default = sqlalchemy.create_engine(default_database_uri)
        engine_default.connect()
        engine_default.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET = utf8 DEFAULT COLLATE utf8_general_ci".format(config['db_name']))
        engine.execute("USE {}".format(config['db_name']))
        Base.metadata.create_all(engine)
        
    except exc.IntegrityError:
        print("already exists")
        
#def insert_db(db):
    
    
    
def read_config(directory="data/config.json"):
    with open(directory, "r") as config_json:
        config = json.load(config_json)
    return config

def setting_selenium():
    path_to_chromedriver = 'driver/chromedriver'
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox") 
    driver = webdriver.Chrome(executable_path=path_to_chromedriver, chrome_options=options)
    return driver

def main_hompage_get(driver=None,url='https://steamdb.info/sales/'):
    driver.get(url)
    time.sleep(5)
    driver.implicitly_wait(20)
    print(driver.page_source)
    driver.find_element_by_xpath("//select/option[@value='-1']").click()
    return driver

def parsing_date(text):
    if text == None:
        return None
    else:
        return text.split("T")[0]

def get_detail_sales_url(selenium=None):
    detail_sale = selenium.find_elements_by_class_name('b')
    return [i.get_attribute('href') for i in detail_sale]

def detail_sales_url_crawler(detail_sale_url=None,selenium=None):
    total_result = []
    column_name = ""
    before_name_changer = ["Store Name"]
    after_name_changer = ["Name"]
    before_id_changer = ["Sub ID"]
    after_id_changer = ["App ID"]
    publisher_column = ["Publisher"]
    developer_column = ["Developer"]
    publisher_collect = []
    developer_collect = []

    for url in detail_sale_url:
        print(url)
        selenium.get(url)
        time.sleep(1.5)
        instance_information = selenium.find_elements_by_css_selector("table.table-bordered.table-hover.table-dark tbody tr td")
        instance_result = {}
        for i in range(len(instance_information)):
            if i % 2 == 0:
                if instance_information[i].text in before_name_changer:
                    column_name = after_name_changer[0]
                elif instance_information[i].text in before_id_changer:
                    column_name = after_id_changer[0]
                else:
                    column_name = instance_information[i].text
            else:
                if column_name in publisher_column:
                    publisher_collect.append(instance_information[i].text)
                if column_name in developer_column:
                    developer_collect.append(instance_information[i].text)
                instance_result[column_name] = instance_information[i].text   
        total_result.append(instance_result)
    return total_result, publisher_collect, developer_collect#, selenium

def main_homepage_crawler(total_result=None,selenium=None):
    #selenium = main_hompage_get(driver=selenium)
    main_column_name = ["App Name","Price","Rating","Discount Rate","Start Date","End Date","Release Date"] 
    idx = 0
    for games in selenium.find_elements_by_css_selector('tbody tr'):
        main_homepage_information = games.find_elements_by_tag_name('td')
        total_result[idx][main_column_name[0]] = main_homepage_information[2].text 
        total_result[idx][main_column_name[1]] =  round(float(main_homepage_information[4].text.replace("$","")) / ((100 - int(main_homepage_information[3].text.replace("-","").replace("%","")))/100),2)
        total_result[idx][main_column_name[2]] =  None if main_homepage_information[5].text == '-' else float(main_homepage_information[5].text.replace("%",""))
        total_result[idx][main_column_name[3]] =  int(main_homepage_information[3].text.replace("-","").replace("%",""))
        total_result[idx][main_column_name[4]] =  parsing_date(main_homepage_information[7].get_attribute("title"))
        total_result[idx][main_column_name[5]] =  parsing_date(main_homepage_information[6].get_attribute("title"))
        total_result[idx][main_column_name[6]] =  parsing_date(main_homepage_information[8].get_attribute("title"))
        idx += 1
    return total_result

def write_pickle(filename,data):
    with open('data/{}.pickle'.format(filename), 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def read_pickle(filename):
    with open('data/{}.pickle'.format(filename), 'rb') as handle:
        return pickle.load(handle)
    
    


    