import argparse, re
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from pymongo import MongoClient, TEXT
from datetime import timedelta, datetime 
from fake_useragent import UserAgent

def login(driver,email,password):
    try:
        driver.get("https://www.facebook.com/")
        driver.find_element_by_xpath("//input[@id='email']").send_keys(email)
        driver.find_element_by_xpath("//input[@id='pass']").send_keys(password)
        driver.find_element_by_xpath("//input[starts-with(@id, 'u_0_')][@value='Entrar']").click()
    except Exception as e:
        print(e)
        return None
    return driver.title

def changePage(driver,page):
    try:
        driver.get(page)
    except Exception as e:
        print(e)
        return None
    return driver.title

def postMessageWithAttachment(driver,message,filepath):
    try:
        a = driver.find_element_by_xpath("//div[@data-testid='photo-video-button']")
        driver.execute_script("arguments[0].click();", a)
        sleep(3)
        driver.find_element_by_xpath("//input[@data-testid='media-attachment-add-photo']").send_keys(filepath)
        sleep(10)
        driver.find_element_by_xpath("//div[@data-testid='status-attachment-mentions-input']").send_keys(message)
        b = driver.find_element_by_xpath("//button[@data-testid='react-composer-post-button']")
        driver.execute_script("arguments[0].click();", b)
        sleep(3)
        try:
            driver.find_element_by_xpath("//button[@tabindex='0']").send_keys(Keys.ENTER)
        except Exception as e:
            print(e)
            None
    except Exception as e:
        print(e)
        return None
    return driver.title

def postMessage(driver,message):
    try:
        try:
            post_box=driver.find_element_by_xpath("//*[@name='xhpc_message']")
            post_box.click()
        except Exception as e:
            print(e)
            try:
                post_box=driver.find_element_by_xpath("//div[@data-testid='status-attachment-mentions-input']")
                post_box.click()
            except Exception as e:
                print(e)
                return None
        # driver.execute_script("arguments[0].click();", post_box)
        
        post_box.send_keys("[publicação automática]"+Keys.ENTER+Keys.ENTER+"#inteligenciaartificial"+Keys.ENTER+Keys.ENTER+message+Keys.ENTER+Keys.ENTER)
        sleep(10)
        # post_it=driver.find_element_by_xpath("//*[@id='u_0_1a']/div/div[6]/div/ul/li[2]/button")
        post_it = driver.find_element_by_xpath("//button[@data-testid='react-composer-post-button']")
        driver.execute_script("arguments[0].click();", post_it)        
        # post_it.click()
        sleep(10)
    except Exception as e:
        print(e)
        return None
    return driver.title
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Facebook Auto Publisher')
    parser.add_argument('email', help='Email address')
    parser.add_argument('password', help='Login password')
    
    args = parser.parse_args()

    client = MongoClient("mongodb://localhost:27017")
    db_fonte = client['news']
    db_destino = client['gerabelo']
    collection_fonte = db_fonte['news']
    collection_destino = db_destino['publicacoes']
    # collection_destino.create_index([('url', TEXTk8)], name='search_index', default_language='english')

    regx = re.compile("(intel)?.*(artificial).*(intel)?", re.IGNORECASE)
    news = collection_fonte.find({"text":regx})
    publicacoes = news.count()

    if publicacoes:
        print("publicacoes: ",publicacoes)
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        ua = UserAgent()
        userAgent = ua.random
        chrome_options.add_argument(f'user-agent={userAgent}')
        chrome_options.add_experimental_option("prefs",prefs)
        chrome_options.add_argument('log-level=3')
        driver = webdriver.Chrome(chrome_options=chrome_options)

        if login(driver,args.email,args.password):
            print("successfully logged in")
            for new in news:
                # if new.get("text"):
                #     candidato = re.search("(intel)?.*(artificial).*(intel)?",new.get("text"))
                #     if candidato:
                url = ""
                if "http" in new.get("href"):
                    url = new.get("href")
                else:
                    if "//" in new.get("href"):
                        url = new.get("href").replace("//","")
                    else:
                        if new.get("parent")[-1:] == "/" or new.get("href")[:1] == "/":
                            url = new.get("parent")+new.get("href")
                        else:
                            url = new.get("parent")+"/"+new.get("href")
                            
                ocorrencia = collection_destino.find({"$and":[{"url":url}]})
                if ocorrencia.count() == 0:
                    # print("url: ",url)
                    if postMessage(driver,url):
                        collection_destino.insert_one({"url":url,"createdAt":datetime.utcnow().strftime("%d/%m/%Y-%H:%M:%S")})                            
                        print("OK: ",url)
                        sleep(5)
                    else:
                        sleep(300)
                        if postMessage(driver,url):
                            collection_destino.insert_one({"url":url,"createdAt":datetime.utcnow().strftime("%d/%m/%Y-%H:%M:%S")})                            
                            print("OK #2: ",url)
                            sleep(5)
                        else:                                
                            print("ERROR: ",url)
        driver.stop_client()
        driver.quit()
    else:
        print("nada a publicar.")