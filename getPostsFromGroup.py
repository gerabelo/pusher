import argparse, urllib.parse
from datetime import timedelta, datetime 
from pymongo import MongoClient
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup

def login(driver,email,password):
    try:
        driver.get("https://www.facebook.com/")
        driver.find_element_by_xpath("//input[@id='email']").send_keys(email)
        driver.find_element_by_xpath("//input[@id='pass']").send_keys(password)
        driver.find_element_by_xpath("//input[starts-with(@id, 'u_0_')][@value='Entrar']").click()
    except:
        return None
    return driver.title

def changePage(driver,page,delay):
    try:
        driver.get(page)
        sleep(int(delay))
    except:
        return None
    return driver.title

def getPosts(html_doc,delay):
    # print(html_doc)
    try:
        soup = BeautifulSoup(html_doc, 'html.parser')
        articles = soup.find_all("div",{"role":"article"}) #articles = driver.find_elements_by_xpath("//div[@role='article']")

        for article in articles:        
            links = article.find_all('a')
            post = article.find("div",{"data-testid":"post_message"})    
            for link in links:
                href = link.get('href')
                if href[:24] == 'https://l.facebook.com/l':
                    for i,j in enumerate(href):
                        if j == '&':
                            external_url = href[31:i]
                            break
                    text = link.get_text()
                    if len(text.split()) > 2:
                        try:
                            createdAt = article.select_one("abbr")["title"]                        
                            print('\n')
                            print(href)
                            print(text)
                            print(urllib.parse.unquote(external_url))
                            print(post.get_text())
                            print(createdAt)
                            print('\n')
                            collection.insert_one({"publicacao":str(article),"CollectedUTC":datetime.utcnow().strftime("%d/%m/%Y-%H%M%S"),"createdAt":createdAt})                    
                        except:
                            None                        
    except:
        return None
    # return len(articles)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Facebook Auto Publisher')
    parser.add_argument('email', help='Email address')
    parser.add_argument('password', help='Login password')
    parser.add_argument('group', help='Group')
    parser.add_argument('delay', help='Delay')

    args = parser.parse_args()

    client = MongoClient("mongodb://localhost:27017")
    db = client['facebook']
    collection = db[args.group]


    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    # driver = webdriver.Chrome()

    if login(driver,args.email,args.password):
        print("successfully logged in")
        if changePage(driver,'https://www.facebook.com/groups/'+args.group+'/',args.delay):
            last_height = driver.execute_script("return document.body.scrollHeight")
            print("redirected")
            while True:
                # remove_opaque = driver.find_element_by_xpath("//div[@id='mainContainer']")
                # driver.execute_script("arguments[0].click();", remove_opaque)
                # remove_opaque = driver.find_element_by_tag_name('body').click()
                getPosts(driver.find_element_by_tag_name('body').get_attribute("innerHTML"),args.delay)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(int(args.delay)*5)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height