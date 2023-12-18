import json
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

        :param url:
        :param browser:
        :return:
        """

        if not browser:
            browser = self.browser

        browser.get(url)

        wait = WebDriverWait(browser, 10)

    def _return_page_source(self, base_url, browser=None, params=None):
        """

        :param base_url:
        :param browser:
        :param params:
        :return:
        """

        if not browser:
            browser = self.browser

        if params:
            base_url = base_url + '?' + urllib.parse.urlencode(params)

        self._load_url(base_url)

        data = browser.page_source

        return data

    def return_entities(self, base_url, article_handler, browser=None, name='div', find_params={"type": "article"}, params=None):
        """

        :param base_url:
        :param article_handler:
        :param browser:
        :param name:
        :param find_params:
        :param params:
        :return:
        """

        results = []

        data = self._return_page_source(base_url, browser=browser, params=params)

        web_bs = bs(data, "lxml")

        articles = web_bs.find_all(name, find_params)

        for article in articles:
            results.append(article_handler(article))

        return results

    def _return_page_count(self, url, browser=None, element="li", class_type='.*PageButtonListItem.*'):
        """

        :param url:
        :param browser:
        :param element:
        :param class_type:
        :return:
        """
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
        """

        :param base_url:
        :param feed:
        :param browser:
        :param sleep:
        :return:
        """
        results = []

        def _return_article_info(page_source, page):
            web_bs = bs(page_source, "lxml")
            script_source = [script for script in web_bs.find_all('script') if feed in script.text and 'lx-nitro/pageNumber/{}/'.format(page) in script.text]

            page_blogs = []

            if not script_source:
                return page_blogs

            if len(script_source) > 1:
                print("ERROR: found more than one matching source.")
                return page_blogs

            script_source = script_source[0].text

            function_source = script_source[script_source.find('{') + 1:script_source.rfind('}')]
            json_source = function_source[function_source.find('{'):function_source.rfind('}') + 1]
            json_page = json.loads(json_source)

            def recurse_children(d, child="children", sentences=None):
                if sentences is None:
                    sentences = []
                if 'text' in d:
                    sentences.append(d['text'])
                if child in d:
                    if not d[child]:
                        return sentences
                    else:
                        for child in d[child]:
                            if 'name' in child:
                                if child['name'] == 'caption':
                                    continue
                            recurse_children(child, child="children", sentences=sentences)

                return sentences

            def check_sentence_punctuation(sentence: str):
                sentence = sentence.strip()
                if len(sentence) > 0:
                    if sentence[-1] not in punctuation:
                        sentence += '.'
                    sentence.replace('\n',' ')
                return sentence

            for entry in json_page['body']['results']:

                body = entry['body']
                post_sentences, visual_captions, image_captions = [], [], []

                title = ''
                if 'title' in entry:
                    title = check_sentence_punctuation(entry['title'])
                date = entry['lastPublished'].split("T")[0]

                for entity in body:
                    if entity['name'] == 'image':
                        if 'caption' in entity:
                            image_captions.append(check_sentence_punctuation(entity['caption']))
                    elif entity['name'] == 'video':
                        try:
                            visual_captions.append(check_sentence_punctuation(entity['synopses']['short']))
                        except KeyError:
                            continue
                    elif entity['name'] == 'paragraph':
                        post_sentences += [check_sentence_punctuation(' '.join([s.strip() for s in recurse_children(entity)]))]
                    elif entity['name'] == 'list':
                        for list_item in entity['children']:
                            post_sentences += [
                                check_sentence_punctuation(' '.join([s.strip() for s in recurse_children(list_item)]))]
                    elif entity['name'] == 'quote':
                        post_sentences += [check_sentence_punctuation(s) for s in recurse_children(entity)]
                    else:
                        print("Found element type which we don't support: {}.".format(entity['name']))

                page_blogs.append(
                    {
                        "date": date,
                        "title": title,
                        "text": [s.replace("\n", " ") for s in post_sentences],
                        "image_captions": [s.replace("\n", " ") for s in image_captions],
                        "video_captions": [s.replace("\n", " ") for s in visual_captions],
                        "type": entity["name"],
                    }
                )
            return page_blogs

        if not browser:
            browser = self.browser

        feed_url = base_url + "/" + feed

        n_pages = self._return_page_count(feed_url, browser, element="span", class_type="lx-pagination*")

        for _p in tqdm(range(1, int(n_pages) + 1)):
            _url = feed_url+"/page/"+str(_p)
            page_source = self._return_page_source(_url)
            page_results = _return_article_info(page_source, _p)
            time.sleep(sleep)

            results += [dict(r, **{'url':_url}) for r in page_results]

        return results

    def return_entities_from_topic(self, base_url, topic, browser=None, sleep=random.randint(1800.0, 2400.0) / 1000.0):
        """

        :param base_url:
        :param topic:
        :param browser:
        :param sleep:
        :return:
        """

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
