import pandas as pd

import json

from scraper.bbc_scraper import BBCScraper
from selenium.webdriver.chrome.service import Service
from general import load_json, save_json, generate_summary_csv, get_article_info


def scrape_topics(all_topics: json, base_url: str):
    chrome = Service("/home/jan/.wdm/drivers/chromedriver/linux64/118.0.5993.70/chromedriver-linux64/chromedriver")
    scraper = BBCScraper(service=chrome)
    scraper.initialise_browser()

    # collect all the articles from different topics - keep in mind we ignire live topics (which are big)
    for topic, topic_url in all_topics.items():
        topic_data = scraper.return_entities_from_topic(
            base_url=base_url, topic=topic_url)
        topic_name = topic.lower().replace(" ", "_")
        save_json('../data/metadata/' + topic_name + ".json", topic_data)


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
    df = df.groupby(['title', 'href'])['topic'].apply(lambda x: ','.join(x)).reset_index()

    return df


if __name__ == '__main__':

    # load all BBC topics we want to scrape from a json file
    all_topics_json = load_json('../data/topics.json')
    base_url_topic = 'https://www.bbc.co.uk/news/topics'

    # collect all base article data
    scrape_topics(all_topics_json, base_url_topic)

    # this can then be run to collect full info (i.e. date + full text + inner article title which can be different)
    summary_df = load_full_article_data('../data/metadata/')

    # save scraped output to summary file
    summary_df.to_csv('../data/summary_20231114.csv')
