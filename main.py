from selenium import webdriver
from lxml import html
import json


def get_page_html_element(driver):
    return html.fromstring(driver.page_source)


def get_text(elems_list):
    return "".join(
        map(
            lambda el: el.text if isinstance(el, html.HtmlElement) else el,
            elems_list
        )
    )


def get_articles_meta(driver, base_url):
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
                {
                    "url": base_url + link,
                    "title": get_text(html_element.xpath("//h1[@data-test='article-title']/node()")),
                    "category": get_text(html_element.xpath("//li[@data-test='article-category']/node()")),
                    "pub_date": get_text(html_element.xpath("//time[@itemprop='datePublished']/@datetime")),
                    "authors": html_element.xpath("//ul[@data-test='authors-list']/li/span[1]/a/text()"),
                    "keywords": html_element.xpath("//ul[@class='c-article-subject-list']/li/span/text()")
                }
            )
    return articles


if __name__ == '__main__':
    base_url = "https://journalofbigdata.springeropen.com"
    with webdriver.Firefox() as driver:
        articles = get_articles_meta(driver, base_url)
        with open("articles-info.json", 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2)
