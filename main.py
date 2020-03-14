from selenium import webdriver
from lxml import html
import json


def get_page_html_element(url, driver):
    driver.get(url)
    return html.fromstring(driver.page_source)


def get_articles_meta(driver, base_url):
    articles = []
    for page in range(1, 2):
        html_element = get_page_html_element(
            f"{base_url}/articles?searchType=journalSearch&sort=PubDate&page={page}",
            driver
        )
        articles_links = html_element.xpath(
            "//a[@itemprop='url' and @data-test='title-link']/@href"
        )
        for link in articles_links:
            html_element = get_page_html_element(base_url + link, driver)
            articles.append(
                {
                    "url": base_url + link,
                    "title": "".join(
                        html_element.xpath(
                            "//h1[@data-test='article-title']/descendant::text()"
                        )
                    ),
                    "category": "".join(
                        html_element.xpath(
                            "//li[@data-test='article-category']/descendant::text()"
                        )
                    ),
                    "pub_date": "".join(
                        html_element.xpath(
                            "//time[@itemprop='datePublished']/@datetime"
                        )
                    ),
                    "authors": html_element.xpath("//ul[@data-test='authors-list']/li/span[1]/a/text()"),
                    "keywords": html_element.xpath("//ul[@class='c-article-subject-list']/li/span/text()"),
                    "text": parse_article_for_text(html_element),
                    "figures": parse_article_for_figures(html_element)
                }
            )
    return articles


def parse_article_for_text(html_element):
    result = {}
    section: html.HtmlElement
    for section in html_element.xpath("//article/section"):
        sect_header = "".join(section.xpath("div/h2/descendant::text()"))
        result[sect_header] = "".join(section.xpath("div/div/descendant::text()"))
    return result


def parse_article_for_figures(html_element):
    result = []
    for figure in html_element.xpath("//figure"):
       result.append({
            "caption": "".join(figure.xpath("figcaption/descendant::text()")),
            "img_link": figure.xpath("descendant::a/@href"),
            "picture_src": figure.xpath("descendant::picture/img/src")
       })
    return result

if __name__ == '__main__':
    base_url = "https://journalofbigdata.springeropen.com"
    with webdriver.Firefox() as driver:
        articles = get_articles_meta(driver, base_url)
        with open("articles-info.json", 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2)
