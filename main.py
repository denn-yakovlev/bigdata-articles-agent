from selenium import webdriver
import time

if __name__ == '__main__':
    driver = webdriver.Firefox()
    url = r"https://journalofbigdata.springeropen.com/articles"
    driver.get(url)
    time.sleep(3)
    driver.close()