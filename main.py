from selenium import webdriver
from selenium.common import exceptions
from lxml import html
import json


def get_page_html_element(url, driver):
    driver.get(url)
    return html.fromstring(driver.page_source)


def parse_articles(driver, base_url):
    articles = []
    #driver.find_element_by_xpath()
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
                    "pub_history": get_publication_history(html_element),
                    "authors": get_authors_info(html_element),
                    "keywords": html_element.xpath("//ul[@class='c-article-subject-list']/li/span/text()"),
                    "doi": html_element.find(".//meta[@name='DOI']").get("content"),
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


def get_publication_history(html_element: html.HtmlElement):
    result = {}
    items = html_element.findall(
        ".//ul[@data-test='publication-history']/li[@class='c-bibliographic-information__list-item']"
    )
    result["received"] = items[0].find(".//time").get("datetime")
    result["accepted"] = items[1].find(".//time").get("datetime")
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
            "img_link": link.get("href") if link is not None else None,
            "picture_src": src.get("src") if src is not None else None
        })
    return result


if __name__ == '__main__':
    base_url = "https://journalofbigdata.springeropen.com"
    with webdriver.Firefox() as driver:
        articles = parse_articles(driver, base_url)
        with open("src/articles-info.json", 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2)