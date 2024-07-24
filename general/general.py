import json
from glob import glob
import time
import random
import os

import requests.exceptions

from entities.bbc_article import BBCArticle


def save_json(file: str, data: json, append: bool = False):
    """
    Save json file

    :param append:
    :param file:
    :param data:
    :return:
    """
    if not os.path.isfile(file) or not append:
        with open(file, 'w', encoding='utf8') as json_file:
            json.dump(data, json_file, ensure_ascii=False)
    else:
        with open(file, encoding='utf8') as json_file:
            existing_data = json.load(json_file)

        existing_data = {**existing_data, **data}

        with open(file, 'w', encoding='utf8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False)


def load_json(file: str):
    """
    Load json file
    :param file:
    :return:
    """
    assert os.path.isfile(file), "File {} doesn't exist".format(file)

    with open(file) as f:
        json_file = json.load(f)
    return json_file


def return_article_dataset(directory: str):
    """
    Read directory of scraped json files and return all data
    :param directory:
    :return:
    """
    titles, links, topics = [], [], []

    for f_name in glob(directory + '/' + '*.json'):
        with open(f_name, 'r') as j:

            topic = json.loads(j.read())

            for title, link in topic.items():
                titles.append(title)
                links.append(link)
                topics.append(f_name.split("/")[-1].split(".")[0])

    return titles, links, topics


def get_article_info(row):
    url = row['url']

    row['date'] = ''
    row['title_from_page'] = ''
    row['text'] = ''

    if not url or url == '':
        return row

    try:
        article = BBCArticle(url)
    except (AttributeError, TypeError, requests.exceptions.ConnectionError):
        print("Failed to process article {}.".format(url))
        return row

    row['date'] = article.date
    row['title_from_page'] = article.title
    row['text'] = article.body

    time.sleep(random.randint(600.0, 800.0) / 1000.0)

    return row
