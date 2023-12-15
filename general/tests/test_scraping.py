import datetime as dt
from string import punctuation
import re

from scraper.bbc_scraper import BBCScraper
from selenium.webdriver.chrome.service import Service


def test_livefeed_scraper():
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

    # test url
    lf_url = "https://www.bbc.com/news/live//world-middle-east-67246761/page/1"

    chrome = Service()
    scraper = BBCScraper(service=chrome)
    scraper.initialise_browser()

    page_results = scraper.return_entities(lf_url, article_handler=_return_article_info, name="li",
                                           find_params={"class": "lx-stream__post-container"})

    expected = [
        '"We told everybody: support Israel. But you are not supporting Israel by supporting this war," insisted Jordan’s Deputy Prime Minister and Foreign Minister, Ayman Safadi when I asked him about the backing many western states, key allies of Jordan, are now giving to Israel’s military operations.',
        '“We recognise the pain of Israel on 7 October,” he said. But he added “you support Israel by supporting peace and only peace will bring support to every Palestinian and every Israeli.”',
        """Asked what Jordan was saying to its allies, including the United States, he said “we're telling everybody what they need to hear. And we're telling everybody that if this war continues, it's dragging the whole region into a regional war whose consequences will be devastating for everyone.”""",
        '“Violence will only make things worse,“ he added. “The amount of hatred that will come out of this amount of misery will not lead to peace.”',
    ]

    assert page_results[-3]['text'] == expected

    lf_url = "https://www.bbc.com/news/live//world-middle-east-67246761/page/3"

    page_results = scraper.return_entities(lf_url, article_handler=_return_article_info, name="li",
                                           find_params={"class": "lx-stream__post-container"})

    expected = [
        "As we’ve been reporting, connectivity is returning to Gaza today and we are slowly starting to hear back from people on the ground.",
        "WhatsApp messages that we sent on Friday night are finally showing two ticks, indicating that they have been received.",
        "One contact left a short message this morning letting us know that he is “OK”.",
        "Another, whose family had stayed in central Gaza for fear of being caught in a strike on the road if they travelled south, attempted to call after finally receiving our messages but the connection was too weak to speak.",
        "Internet monitoring service NetBlocks posted network data on X - formerly known as Twitter - showing that internet connectivity was being restored on Sunday.",
    ]

    assert page_results[-1]['text'] == expected

    lf_url = "https://www.bbc.com/news/live//world-middle-east-67246761/page/4"

    page_results = scraper.return_entities(lf_url, article_handler=_return_article_info, name="li",
                                           find_params={"class": "lx-stream__post-container"})

    expected = [
        "It's just gone 9.30 in Israel and Gaza. Here's a recap of the latest lines if you are just joining us:",
        'Phone and internet connectivity is being restored in Gaza after an outage that lasted for more than 24 hours.',
        "Israel's military operations in Gaza continued overnight, while Palestinian armed factions in Gaza fired more rockets into Israel.",
        'Netanyahu said in a televised address on Saturday that additional Israeli ground forces had gone into what he called "that stronghold of evil" - referring to Gaza - adding that commanders were now deployed "all over the Gaza Strip"',
        'He said that recovering the hostages was an "integral" part of the military\'s goals but that its top priority was to "abolish" Hamas.',
        'The International Committee of the Red Cross has called for an immediate de-escalation of the conflict, deploring the loss of life and what it said was an "intolerable level of suffering"',
        "Israel has been bombing Gaza since the 7 October Hamas attacks that killed 1,400 people and saw 229 people kidnapped as hostages. The Hamas-run health ministry in Gaza says more than 8,000 people have been killed by Israel's retaliatory attacks."
    ]

    assert page_results[0]['text'] == expected