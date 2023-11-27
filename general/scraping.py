import pandas as pd
import glob
import json
from datetime import datetime
from tqdm import tqdm

from scraper.bbc_scraper import BBCScraper
from selenium.webdriver.chrome.service import Service
from general import load_json, save_json, return_article_dataset, get_article_info


def scrape_topics(all_topics: json, base_url: str, ignore: bool = True):
    """
    Scrape topics based on json file

    :param all_topics: json file of topics to scrape
    :param base_url: base_url to scrape from
    :param ignore: a dataframe of existing articles to not rescrape
    :return:
    """
    chrome = Service("/home/jan/.wdm/drivers/chromedriver/linux64/118.0.5993.70/chromedriver-linux64/chromedriver")
    scraper = BBCScraper(service=chrome)
    scraper.initialise_browser()

    # collect all the articles from different topics - keep in mind we ignire live topics (which are big)
    for topic, topic_url in all_topics.items():
        topic_data = scraper.return_entities_from_topic(
            base_url=base_url, topic=topic_url)

        topic_name = topic.lower().replace(" ", "_")

        existing_topic_data = {}
        if ignore:
            existing_topic_data = load_json('../data/metadata/' + topic_name + ".json")

        for article, href in topic_data.items():
            if article not in existing_topic_data:
                existing_topic_data[article] = href

        save_json('../data/metadata/' + topic_name + ".json", existing_topic_data, append=False)


def load_full_article_data(directory: str, existing_summary: pd.DataFrame = None):
    """
    Takes an input general scraped csv file and loads the full article text
    This is done in 2 parts to speed up scraping from the high level page and only scape full text if needed

    :param existing_summary:
    :param directory:
    :return:
    """
    # load all titles, links and topics
    titles, links, topics = return_article_dataset(directory)

    df = pd.DataFrame(
        {
            "title": titles,
            "href": links,
            "topic": topics
        }
    )

    if existing_summary is not None:
        df = df[~df['href'].isin(existing_summary['href'].values)]

    # articles can be in multiple topics
    df = df.groupby(['title', 'href'])['topic'].apply(lambda x: ','.join(x)).reset_index()

    # collect full article info
    tqdm.pandas()
    df['url'] = 'http://bbc.co.uk'+df['href']
    df = df.progress_apply(get_article_info, axis=1)

    return df


if __name__ == '__main__':

    latest_summary_path = glob.glob("../data/summary*.csv")
    latest_summary = None

    if latest_summary_path:
        latest_summary = pd.read_csv(latest_summary_path[0])

    # load all BBC topics we want to scrape from a json file
    #all_topics_json = load_json('../data/topics.json')
    #base_url_topic = 'https://www.bbc.co.uk/news/topics'

    #topics_now = {"Israel-Gaza war": "c2vdnvdg6xxt"}

    # collect all base article data, ignoring existing scraped articles
    #scrape_topics(topics_now, base_url_topic, ignore=False)

    # this can then be run to collect full info (i.e. date + full text + inner article title which can be different)
    summary_df = load_full_article_data('../data/metadata/', existing_summary=latest_summary)

    if latest_summary is not None:
        summary_df = pd.concat([latest_summary, summary_df])

    today_date = datetime.today().strftime('%Y%m%d')

    # save scraped output to summary file
    summary_df.to_csv('../data/summary_' + today_date + '.csv')
