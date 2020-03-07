from lxml.html import HtmlElement
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from lxml import html
import time


def get_articles_links(driver, url):
    articles_links = []
    for page in range(1, 7):
        driver.get(url + f"?searchType=journalSearch&sort=PubDate&page={page}")
        html_element: HtmlElement = html.fromstring(driver.page_source)
        articles_links += html_element.xpath(
            "//a[@itemprop='url' and @data-test='title-link']/@href"
            )
    return articles_links


if __name__ == '__main__':
    base_url = r"https://journalofbigdata.springeropen.com"
    url = base_url + "/articles"
    with webdriver.Firefox() as driver:
        articles_links = get_articles_links(driver, url)
        time.sleep(3)

