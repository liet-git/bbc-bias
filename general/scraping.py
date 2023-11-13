import pandas as pd

import json

from scraper.bbc_scraper import BBCScraper
from selenium.webdriver.chrome.service import Service
from general.general import load_json, save_json, generate_summary_csv, get_article_info


def scrape_topics(all_topics:json, base_url: str):

    chrome = Service("/home/jan/.wdm/drivers/chromedriver/linux64/118.0.5993.70/chromedriver-linux64/chromedriver")
    scraper = BBCScraper(service=chrome)
    scraper.initialise_browser()

    # collect all the articles from different topics - keep in mind we ignire live topics (which are big)
    for topic, topic_url in all_topics.items():
        topic_data = scraper.return_entities_from_topic(
            base_url=base_url, topic=topic_url)
        topic_name = topic.lower().replace(" ", "_")
        save_json('./data/metadata/' + topic_name + ".json", topic_data)


def load_full_article_data(directory: str):
    # load all titles, links and topics
    titles, links, topics = generate_summary_csv(directory)

    df = pd.DataFrame(
        {
            "title": titles,
            "href": links,
            "topic": topics
        }
    )

    # collect full article info
    df = df.apply(get_article_info, axis=1)

    # articles can be in multiple topics
    df.drop_duplicates('href', keep='first', inplac=True)

    return df


if __name__ == '__main__':

    all_topics_json = load_json('./data/topics.json')
    base_url_topic = 'https://www.bbc.co.uk/news/topics'

    scrape_topics(all_topics_json, base_url_topic)

    summary_df = load_full_article_data('./data/metadata/')

    summary_df.to_csv('./data/summary.csv')