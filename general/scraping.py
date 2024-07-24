import pandas as pd
import glob
import json
from datetime import datetime
from tqdm import tqdm
import argparse

from scraper.bbc_scraper import BBCScraper
from selenium.webdriver.chrome.service import Service
from general import load_json, save_json, return_article_dataset, get_article_info


def scrape_livefeed(live_feeds: json, base_url: str):
    """

    :param live_feeds:
    :param base_url:
    :return:
    """
    chrome = Service()
    scraper = BBCScraper(service=chrome)
    scraper.initialise_browser()

    for livefeed, livefeed_url in live_feeds.items():
        livefeed_data = scraper.return_entities_from_livefeed(
            base_url=base_url, feed=livefeed_url)

        livefeed_name = livefeed.lower().replace(" ", "_")

        save_json('../data/metadata/livefeeds/' + livefeed_name + ".json", livefeed_data, append=False)


def scrape_topics(all_topics: json, base_url: str, ignore: bool = True):
    """
    Scrape topics based on json file

    :param all_topics: json file of topics to scrape
    :param base_url: base_url to scrape from
    :param ignore: a dataframe of existing articles to not rescrape
    :return:
    """
    chrome = Service()
    scraper = BBCScraper(service=chrome)
    scraper.initialise_browser()

    # collect all the articles from different topics - keep in mind we ignire live topics (which are big)
    for topic, topic_url in all_topics.items():
        topic_data = scraper.return_entities_from_topic(
            base_url=base_url, topic=topic_url)

        topic_name = topic.lower().replace(" ", "_")

        existing_topic_data = {}
        if ignore:
            existing_topic_data = load_json('../data/metadata/topics/' + topic_name + ".json")

        for article in topic_data:
            if article['title'] not in existing_topic_data.keys():
                existing_topic_data[article['title']] = article['link']

        save_json('../data/metadata/topics/' + topic_name + ".json", existing_topic_data, append=False)


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
    df['url'] = 'http://bbc.co.uk' + df['href']
    df = df.progress_apply(get_article_info, axis=1)

    return df


def process_articles(directory: str = '../data/metadata/topics/'):
    """
    Function to take directory of scraped json file and output a csv with all the information
    It can also take into account an existing usmmary file

    :param directory:
    :return:
    """

    latest_summary_path = glob.glob("../data/summary_*_articles.csv")
    latest_summary = None

    if latest_summary_path:
        latest_summary = pd.read_csv(latest_summary_path[0])

    # this can then be run to collect full info (i.e. date + full text + inner article title which can be different)
    summary_df = load_full_article_data(directory, existing_summary=latest_summary)

    if latest_summary is not None:
        summary_df = pd.concat([latest_summary, summary_df])

    today_date = datetime.today().strftime('%Y%m%d')

    # save scraped output to summary file
    summary_df.to_csv('../data/summary_' + today_date + '_articles.csv', index=False)


def process_livefeeds(directory: str = '../data/metadata/livefeeds/'):
    """

    :param directory:
    :return:
    """

    titles, dates, links, texts, image_captions, video_captions = [], [], [], [], [], []

    for f_name in glob.glob(directory + '*.json'):
        with open(f_name, 'r') as j:

            lf = json.loads(j.read())

            import re

            for art in lf:
                titles.append(art['title'])
                dates.append(art['date'])
                links.append(art['url'])
                texts.append([re.sub("\\\\", "", t) for t in art['text']])
                image_captions.append(art['image_captions'])
                video_captions.append(art['video_captions'])

    df = pd.DataFrame(
        {
            "title": titles,
            "url": links,
            "date": dates,
            "body_text": texts,
            "image_captions": image_captions,
            "video_captions": video_captions,
        }
    )

    # combine all text sources into one field
    df['text'] = df['body_text'] + df['image_captions'] + df['video_captions']

    # get todays date
    today_date = datetime.today().strftime('%Y%m%d')

    # save scraped output to summary file
    df.to_csv('../data/summary_' + today_date + '_livefeeds.csv', index=False)


def scrape_articles(topic_json: str = '../data/topics.json', ignore=False):
    """

    :param topic_json:
    :param ignore:
    :return:
    """
    # load all BBC topics we want to scrape from a json file
    all_topics_json = load_json(topic_json)
    base_url_topic = 'https://www.bbc.co.uk/news/topics'

    scrape_topics(all_topics_json, base_url_topic, ignore=ignore)


def scrape_search(search_term: str):
    """

    :param search_term:
    :return:
    """
    base_url_topic = 'https://www.bbc.co.uk/search'

    chrome = Service()
    scraper = BBCScraper(service=chrome)
    scraper.initialise_browser()

    search_data = scraper.return_entities_from_search(base_url_topic, search_term)

    search_name = search_term.lower().replace(" ", "_")

    save_json('../data/metadata/search/' + search_name + ".json", search_data, append=False)


def process_searches(directory: str = '../data/metadata/search/'):
    """

    :param directory:
    :return:
    """

    titles, links, searches = [], [], []

    for f_name in glob.glob(directory + '*.json'):
        with open(f_name, 'r') as j:

            lf = json.loads(j.read())

            for art in lf:
                titles.append(art['title'])
                links.append(art['link'])
                searches.append(f_name.split("/")[-1].split(".")[0])

    df = pd.DataFrame(
        {
            "title": titles,
            "url": links,
            "search": searches,
        }
    )

    # articles can be in multiple topics
    df = df.groupby(['title', 'url'])['search'].apply(lambda x: ','.join(x)).reset_index()

    # collect full article info
    tqdm.pandas()
    df = df.progress_apply(get_article_info, axis=1)

    # get todays date
    today_date = datetime.today().strftime('%Y%m%d')

    # save scraped output to summary file
    df.to_csv('../data/summary_' + today_date + '_searches.csv', index=False)


def scrape_livefeeds(livefeed_json: str = '../data/livefeeds.json'):
    """

    :param livefeed_json:
    :return:
    """
    # load live feed json
    all_livefeed_json = load_json(livefeed_json)
    base_url_livefeed = 'https://www.bbc.com/news/live/'

    # collect all base article data, ignoring existing scraped articles
    scrape_livefeed(all_livefeed_json, base_url_livefeed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape and process BBC articles.')

    parser.add_argument('-s', '--scrape', action='store_true', help='Scrape a topic or livefeed.')
    parser.add_argument('-p', '--process', action='store_true', help='Process a list of scraped topics or livefeeds.')

    parser.add_argument('--scrape-from', '--scrape-from', default='../data/', type=str,
                        help='Location of json folder for topics or livefeed.')
    parser.add_argument('--json-directory', '--jsondirectory', default='../data/metadata/', type=str,
                        help='Location of json folder with scraped jsons.')

    parser.add_argument('-article', action='store_true', help='Whether to scrape/process articles.')
    parser.add_argument('-livefeed', action='store_true', help='Whether to scrape/process livefeeds.')

    args = vars(parser.parse_args())

    scrape_from = args['scrape_from']
    scraped_jsons = args['json_directory']

    handle_articles = args['article']
    handle_livefeeds = args['livefeed']

    if args['scrape']:
        if handle_articles:
            scrape_articles(scrape_from + 'topics.json')
        if handle_livefeeds:
            scrape_livefeeds(scrape_from + 'livefeeds,json')

    if args['process']:
        if handle_articles:
            process_articles(scraped_jsons + 'topics/')
        if handle_livefeeds:
            process_livefeeds(scraped_jsons + 'livefeeds/')
