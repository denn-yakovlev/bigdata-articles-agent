from selenium import webdriver
from selenium.common import exceptions
from lxml import html
import json


def get_page_html_element(url, driver):
    driver.get(url)
    return html.fromstring(driver.page_source)


def get_articles_meta(driver, base_url):
    articles = []
    for page in range(1, 7):
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
                    "authors": get_authors_info(html_element),
                    "keywords": html_element.xpath("//ul[@class='c-article-subject-list']/li/span/text()"),
                    "text": get_text(html_element),
                    "figures": get_figures_info(html_element)
                }
            )
    return articles


def get_authors_info(html_element):
    result = []
    for author in html_element.xpath("//ul[@data-test='authors-list']/li[@itemprop='author']"):
        name = author.xpath("span[1]/a/text()")[0]
        driver.find_element_by_link_text(name).click()
        try:
            link = driver.find_element_by_class_name("c-article-orcid").get_attribute("href")
        except exceptions.NoSuchElementException:
            link = None
        result.append({
            "name": name,
            "link": link
        })
    return result


def get_text(html_element):
    result = {}
    section: html.HtmlElement
    for section in html_element.xpath("//article/section"):
        sect_header = "".join(section.xpath("div/h2/descendant::text()"))
        result[sect_header] = "".join(section.xpath("div/div/descendant::text()"))
    return result


def get_figures_info(html_element):
    result = []
    figure: html.HtmlElement
    for figure in html_element.xpath("//article//figure"):
        caption = "".join(figure.xpath(".//figcaption//descendant::text()"))
        link = figure.find(".//a")
        src = figure.find(".//picture//img")
        result.append({
            "caption": caption,
            "img_link": link.get("href") if link != None else None,
            "picture_src": src.get("src") if src != None else None
        })
    return result


if __name__ == '__main__':
    base_url = "https://journalofbigdata.springeropen.com"
    with webdriver.Firefox() as driver:
        articles = get_articles_meta(driver, base_url)
        with open("articles-info.json", 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2)