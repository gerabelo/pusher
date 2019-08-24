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
from fake_useragent import UserAgent

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
        posts = soup.find_all("div",{"role":"article"})# posts = soup.find_all("div",id=lambda value: value and value.startswith("jumper_"))
        for post in posts:
            try:
                createdAt = post.select_one("abbr")["title"]                        
                collection.insert_one({"publicacao":str(post),"CollectedUTC":datetime.utcnow().strftime("%d/%m/%Y-%H:%M:%S"),"createdAt":createdAt})                    
            except:
                None
            try:
                links = post.find_all('a')
                for link in links:
                    href = link.get('href')
                    if href[:24] == 'https://l.facebook.com/l':
                        for i,j in enumerate(href):
                            if j == '&':
                                external_url = href[31:i]
                                break

                    print(link.get_text())
                    print(urllib.parse.unquote(external_url))

                post_message = post.find("div",{"data-testid":"post_message"})                    
                print(post_message.get_text())
                print(createdAt)
                print('\n')                
            except:
                None                        
    except:
        return None
    # return len(posts)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Facebook Auto Publisher')
    parser.add_argument('email', help='Email address')
    parser.add_argument('password', help='Login password')
    parser.add_argument('timeline', help='Time line')
    parser.add_argument('delay', help='Delay')
    parser.add_argument('depth', help='Depth')

    args = parser.parse_args()

    client = MongoClient("mongodb://localhost:27017")
    db = client['facebook']
    collection = db[args.timeline]

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')    
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument('log-level=3')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    # driver = webdriver.Chrome()

    delayed = False

    if login(driver,args.email,args.password):
        print("successfully logged in")
        if changePage(driver,'https://www.facebook.com/'+args.timeline,args.delay):
            last_height = driver.execute_script("return document.body.scrollHeight")
            print("redirected")
            i = 0
            while True:
                # remove_opaque = driver.find_element_by_xpath("//div[@id='mainContainer']")
                # driver.execute_script("arguments[0].click();", remove_opaque)
                # remove_opaque = driver.find_element_by_tag_name('body').click()
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(int(args.delay))
                new_height = driver.execute_script("return document.body.scrollHeight")
                if i == int(args.depth):
                    break
                if new_height == last_height:
                    if delayed:
                        break
                    else:
                        delayed = True
                        sleep(int(args.delay))
                else:
                    delayed = False
                last_height = new_height
                i += 1                
            getPosts(driver.find_element_by_id('timeline_tab_content').get_attribute("innerHTML"),args.delay) #getPosts(driver.find_element_by_tag_name('body').get_attribute("innerHTML"),args.delay)            
    driver.stop_client()
    driver.quit()