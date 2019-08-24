import argparse, urllib.parse, random
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
        sleep(random.randint(5,int(delay)))
    except:
        return None
    return driver.title

def getGroupID(driver,delay):
    soup = BeautifulSoup(driver.find_element_by_tag_name('body').get_attribute("innerHTML"), 'html.parser')
    anchors = soup.find_all("a",{"data-endpoint":"/ajax/home/generic.php"})
    href = anchors[3].get('href')
    if href[:8] == '/groups/':
        for i,j in enumerate(href):
                if j == '/' and i > 8:
                    return href[8:i]

def getContactFromUserID(driver,user_id,delay):
    try:
        if changePage(driver,'https://www.facebook.com/'+user_id+'?sk=about&section=contact-info',args.delay):
            pagelet = driver.find_element_by_xpath("//div[@id='pagelet_timeline_medley_about']")
            data = pagelet.get_attribute("innerHTML")
            f = open("C:\\Users\\User\\jobs\\fbbot\\"+user_id+".txt","wb")
            f.write(data.encode("utf-8"))
            f.close()
    except Exception as e:
        print("error: ",e)
        return False
    return True
    
def getLocalMembers(driver,delay):
    # if changePage(driver,'https://www.facebook.com/groups/'+args.group+'/local_members/',args.delay):
        #rolar até o final
        last_height = driver.execute_script("return document.body.scrollHeight")
        sleep(1)
        print("redirected")
        delayed = False
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(random.randint(5,int(delay)))
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                if delayed:
                    break
                else:
                    delayed = True
                    sleep(random.randint(5,int(delay)*5))
            else:
                delayed = False
            last_height = new_height
        users_id = ''
        members = driver.find_elements_by_xpath("//div[starts-with(@id, 'recently_joined_')]")
        print("len(members): ",len(members))
        users = []
        for member in members:
            soup = BeautifulSoup(member.get_attribute("innerHTML"),'html.parser')
            # anchors = soup.find_all("a")
            # for c,anchor in enumerate(anchors):
                # if c%3 == 0 and c > 0:
            anchor = soup.find("a")
            ajaxify = anchor.get('ajaxify')
            if '_id' in ajaxify:
                for i,j in enumerate(ajaxify):
                    if j == '=' and i > 40:
                        user_id = ajaxify[(i+1):-16]
                        users_id += user_id+'\n'
                        users.append(user_id)
                        print("ajaxify[(i+1):-16]: ",ajaxify[(i+1):-16])
                        if getContactFromUserID(driver,user_id,delay):
                            print("user_id saved: ",user_id)
                        else:
                            print("user_id not saved: ",user_id)
                        break
        #     html_doc += str(member.get_attribute("innerHTML"))
        # f = open("C:\\Users\\User\\jobs\\fbbot\\"+args.group+".txt","wb")
        # f.write(html_doc.encode("utf-8"))
        # f.close()
        a = open("C:\\Users\\User\\jobs\\fbbot\\"+args.group+".txt",'wb')            
        a.write(users_id.encode("utf-8"))
        a.close()  
        # for user in users:      
        #     if getContactFromUserID(driver,user,delay):
        #         print("user_id saved: ",user)
        #     else:
        #         print("user_id not saved: ",user)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Facebook Auto Publisher')
    parser.add_argument('email', help='Email address')
    parser.add_argument('password', help='Login password')
    parser.add_argument('group', help='Group')
    parser.add_argument('delay', help='Delay')
    # parser.add_argument('depth', help='Depth')

    args = parser.parse_args()

    client = MongoClient("mongodb://localhost:27017")
    db = client['facebook']
    collection = db[args.group]

    chrome_options = webdriver.ChromeOptions()
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)

    if login(driver,args.email,args.password):
        print("successfully logged in")
        if changePage(driver,'https://www.facebook.com/groups/'+args.group+'/members/',args.delay):
            print("redirected!")
            sleep(random.randint(5,int(args.delay)))
            getLocalMembers(driver,args.delay)
    # driver.stop_client()
    # driver.close()