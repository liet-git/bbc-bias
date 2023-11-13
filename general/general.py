import json
from glob import glob
import time
import random

from entities.bbc_article import BBCArticle


def save_json(file: str, data: json):
    """
    Save json file

    :param file:
    :param data:
    :return:
    """
    with open(file, 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, ensure_ascii=False)


def load_json(file: str):
    """
    Load json file
    :param file:
    :return:
    """
    with open(file) as f:
        json_file = json.load(f)
    return json_file


def generate_summary_csv(directory: str):
    """
    Read directory of scraped json files and create csv summary
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
    href = row['url']
    href = "http://bbc.co.uk" + href

    try:
        article = BBCArticle(href)
    except AttributeError:
        print("Failed to process article {}.".format(href))
        row['date'] = ''
        row['title'] = ''
        row['text'] = ''
        return row

    row['date'] = article.date
    row['title_from_page'] = article.title
    row['text'] = article.body

    time.sleep(random.randint(800.0, 1400.0) / 1000.0)

    return row

