import random
import urllib
import re
from string import punctuation

from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
import time
import datetime as dt

from scraper.base_scraper import Scraper


class BBCScraper(Scraper):

    def _load_url(self, url, browser=None):
        """
        """

        if not browser:
            browser = self.browser

        browser.get(url)

        wait = WebDriverWait(browser, 10)

    def return_entities(self, base_url, article_handler, browser=None, name='div', find_params={"type": "article"}, params=None):
        '''
        '''

        results = []

        if not browser:
            browser = self.browser

        if params:
            base_url = base_url + '?' + urllib.parse.urlencode(params)

        self._load_url(base_url)

        data = browser.page_source

        web_bs = bs(data, "lxml")

        articles = web_bs.find_all(name, find_params)

        for article in articles:
            results.append(article_handler(article))

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

    def return_entities_from_livefeed(self, base_url, feed, browser=None,
                                      sleep=random.randint(1800.0, 2400.0) / 1000.0):
        results = []

        def _return_article_info(article):

            def _return_text(element):

                sentences = []

                def _process_sentence(sentence):
                    if sentence.isspace() or sentence == '\n' or sentence == '':
                        return
                    sentence = sentence.strip().replace('\n', '').replace('\\', '')
                    if len(sentence) > 0:
                        if sentence[-1] not in punctuation:
                            sentence += '.'
                    return sentence

                for t in element.contents:
                    # print(t.name, '\n')
                    if t.name == "figure":
                        for e in t:
                            if e.name == 'figcaption':
                                sentences.append(_process_sentence(e.get_text().strip()))
                        continue
                    if t.name == "blockquote":
                        ps = t.find_all('p')
                        for _p in ps:
                            found_text = _p.get_text().split('\n')
                            for sent in found_text:
                                sentences.append(_process_sentence(sent))
                    elif t.name in ['p', 'ul', 'li']:
                        found_text = t.get_text().split('\n')
                        for sent in found_text:
                            _ps = _process_sentence(sent)
                            if _ps is not None:
                                sentences.append(_ps)
                return sentences

            try:
                date = article.find("span", {"class": "qa-post-auto-meta"}).text
                date = dt.datetime.strptime(date, "%H:%M %d %b")
                date = date.replace(year=2023)
                date = date.strftime("%Y-%m-%d %H:%M")
            except AttributeError:
                date = ''

            title = article.find("header", {"class": re.compile("lx-stream-post__header*")}).text
            text = _return_text(article.find("div", {"class": re.compile("lx-stream-post-body")}))

            return {
                "date": date,
                "title": title,
                "text": text,
            }

        if not browser:
            browser = self.browser

        feed_url = base_url + "/" + feed

        n_pages = self._return_page_count(feed_url, browser, element="span", class_type="lx-pagination*")

        for _p in tqdm(range(1, int(n_pages) + 1)):
            _url = feed_url+"/page/"+str(_p)
            page_results = self.return_entities(_url, article_handler=_return_article_info, name="li", find_params={"class": "lx-stream__post-container"})
            time.sleep(sleep)

            results += [dict(r, **{'url':_url}) for r in page_results]

        return results

    def return_entities_from_topic(self, base_url, topic, browser=None, sleep=random.randint(1800.0, 2400.0) / 1000.0):

        results = []

        def _return_article_info(article):
            try:
                title, link = article.find('span').text, article.find('a', {"href": True})['href']
                if re.match('^[0-9]{2}\:[0-9]{2}.*', title):
                    regex = re.compile('.*Headline*')
                    title, link = article.find('span', {"class": regex}).text, article.find('a', {"href": True})['href']
                return {
                    'title': title,
                    'link': link,
                }
            except IndexError:
                print("Failed to find title or link.")
            except AttributeError:
                print("Failed to find title.")

        if not browser:
            browser = self.browser

        topic_url = base_url + "/" + topic

        n_pages = self._return_page_count(topic_url, browser)

        for _p in tqdm(range(1, int(n_pages) + 1)):
            page_results = self.return_entities(topic_url, article_handler=_return_article_info, params={"page": _p})
            time.sleep(sleep)

            results += page_results

        return results
