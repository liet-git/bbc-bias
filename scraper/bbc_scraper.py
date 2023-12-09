import random
import urllib
import re

from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
import time

from scraper.base_scraper import Scraper


class BBCScraper(Scraper):

    def _load_url(self, url, browser=None):
        """
        """

        if not browser:
            browser = self.browser

        browser.get(url)

        wait = WebDriverWait(browser, 10)

    def return_entities(self, base_url, browser=None, kind='article', params=None):
        '''
        '''

        results = {}

        if not browser:
            browser = self.browser

        if params:
            base_url = base_url + '?' + urllib.parse.urlencode(params)

        self._load_url(base_url)

        data = browser.page_source

        web_bs = bs(data, "lxml")

        articles = web_bs.find_all("div", {"type": kind})

        for article in articles:
            try:
                title, link = article.find('span').text, article.find('a', {"href": True})['href']
                if re.match('^[0-9]{2}\:[0-9]{2}.*', title):
                    regex = re.compile('.*Headline*')
                    title, link = article.find('span', {"class": regex}).text, article.find('a', {"href": True})['href']
                results[title] = link
            except IndexError:
                print("Failed to find title or link.")
            except AttributeError:
                print("Failed to find title.")

        return results

    def _return_page_count(self, url, browser=None, element="li", class_type='.*PageButtonListItem.*'):
        if not browser:
            browser = self.browser

        self._load_url(url)

        base_bs = bs(browser.page_source, "lxml")

        regex = re.compile(class_type)
        list_pages = base_bs.find_all(element, {"class": regex})

        if not list_pages:
            return None

        return list_pages[-1].text.strip()

    def return_entities_from_topic(self, base_url, topic, browser=None, sleep=random.randint(1800.0, 2400.0) / 1000.0):

        results = {}

        if not browser:
            browser = self.browser

        topic_url = base_url + "/" + topic

        n_pages = self._return_page_count(topic_url, browser)

        for _p in tqdm(range(1, int(n_pages) + 1)):
            page_results = self.return_entities(topic_url, params={"page": _p})
            time.sleep(sleep)

            results = {**results, **page_results}

        return results
