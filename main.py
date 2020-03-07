from lxml.html import HtmlElement
from selenium import webdriver
from lxml import html
from datetime import date, datetime
from typing import List
import json


class Article:
    url: str
    title: str
    category: str
    pub_date: str
    authors: List[str]
    keywords: List[str]

    def __init__(self, url, title, category, pub_date, authors, keywords):
        self.url = url
        self.title = title
        self.category = category
        self.pub_date = pub_date
        self.authors = authors
        self.keywords = keywords


def get_page_html_element(driver):
    html_element: HtmlElement = html.fromstring(driver.page_source)
    return html_element


def get_articles(driver, base_url):
    articles = []
    for page in range(1, 7):
        driver.get(f"{base_url}/articles?searchType=journalSearch&sort=PubDate&page={page}")
        html_element = get_page_html_element(driver)
        articles_links = html_element.xpath(
            "//a[@itemprop='url' and @data-test='title-link']/@href"
        )
        for link in articles_links:
            driver.get(base_url + link)
            html_element = get_page_html_element(driver)
            articles.append(
                Article(
                    url=base_url + link,
                    title=str(html_element.xpath("//h1[@data-test='article-title']/text()")[0]),
                    category=str(html_element.xpath("//li[@data-test='article-category']/text()")[0]),
                    pub_date=str(html_element.xpath("//time[@itemprop='datePublished']/@datetime")[0]),
                    authors=html_element.xpath("//ul[@data-test='authors-list']/li/span[1]/a/text()"),
                    keywords=html_element.xpath("//ul[@class='c-article-subject-list']/li/span/text()")
                )
            )
    return articles


def save_json(file_name, content):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2)


if __name__ == '__main__':
    base_url = "https://journalofbigdata.springeropen.com"
    with webdriver.Firefox() as driver:
        articles = get_articles(driver, base_url)
        save_json(
            "articles-info.json",
            list(
                map(
                    lambda obj: obj.__dict__,
                    articles
                )
            )
        )
        pass
