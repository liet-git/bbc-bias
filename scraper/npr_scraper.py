from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep 
from npr_links import article_links
import urllib
from bs4 import BeautifulSoup as bs
import csv

def get_articles_links() -> list:
    npr_url = "https://www.npr.org/series/1205445976/middle-east-crisis"
    driver = webdriver.Chrome()
    driver.get(npr_url)
    while True: 
        try:
            WebDriverWait(driver, 15)
            button = driver.find_element("xpath", "//button[contains(text(), 'Load more stories')]")
            button.click()    
        except Exception as e: 
            break

    elems = driver.find_elements("xpath", "//a[contains(@data-metrics, 'Click Story Title')]")    
    links = [elem.get_attribute('href') for elem in elems]
    return links


def get_text_from_articles():
    """
    Parse article text and write to csv
    """
    with open('npr_summary.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["link", "text"])
        for article_link in article_links:
            html = urllib.request.urlopen(article_link)
            content = html.read()
            parsed_html = bs(content, 'lxml')
            try:
                text = parsed_html.find("div", {"id": "storytext"})
                children = text.findChildren("p" , recursive=False)
                article_text = ""
                for x in children:
                    article_text += x.text
                writer.writerow([article_link, article_text])
            except Exception as e:
                print(e)
                print(article_link+" is not a story")
                continue

get_text_from_articles()
