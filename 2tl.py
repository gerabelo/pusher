import argparse
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep

def login(driver,email,password):
    try:
        driver.get("https://www.facebook.com/")
        driver.find_element_by_xpath("//input[@id='email']").send_keys(email)
        driver.find_element_by_xpath("//input[@id='pass']").send_keys(password)
        driver.find_element_by_xpath("//input[starts-with(@id, 'u_0_')][@value='Entrar']").click()
    finally:
        return driver.title
    return None

def postMessage(driver,message,delay):
    try:
        post_box=driver.find_element_by_xpath("//*[@name='xhpc_message']")
        post_box.click()
        post_box.send_keys(message)
        sleep(delay)
        post_it=driver.find_element_by_xpath("//*[@id='u_0_1a']/div/div[6]/div/ul/li[2]/button")
        post_it.click()
    finally:
        return driver.title
    return None
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Facebook Auto Publisher')
    parser.add_argument('email', help='Email address')
    parser.add_argument('password', help='Login password')
    parser.add_argument('message', help='Message')
    parser.add_argument('delay', help='Delay')

    args = parser.parse_args()

    driver = webdriver.Chrome()
    if login(driver,args.email,args.password):
        print("successfully logged in")
        if postMessage(driver,args.message,args.delay):
            print("the message was delivered!")
            driver.stop_client()
            driver.quit()