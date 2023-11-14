# Analysing the bias in BBC reporting of Palestine
The following code can be used to gather information from BBC articles regarding several topics (a form of grouping on the BBC website). These topics can be found in ```./data/topics.json```. 

## Set up and requirements
Simply clone the repoistory and run:
```pip3 install -r requirements.txt```

### Usage

To simply collect all articles, from all topics defined in the above json, run  ```scraping.py```. It is also possible to scrape individual articles/topics using the ```BBCArticle``` and ```BBCScraper``` class respectively.

## Analysis 

In ```summary.csv``` we have all the articles collected from the creation of the topic, until 2023-11-04, with the following columns:
* date: date of article
* href: reference to news/topic url part of whole url
* text: the span texts of the article, containing all the text in list format
* title: the title of the article as shown in the topic
* title_from_page: the title of the article as shown when loaded (can differ to above, often longer)
* topic: the topic this article was found in (can be multiple)
* url: full url to the article

The ```base_analysis.py``` contains a simple analysis looking at word count frequencies in the article titles, as well as plotting the mentions of Palestine/Israel/Gaza/Hamas with the following output (the following plot shows counts with articles containing mention of the 'pro-' string removed):

![alt text](./outputs/word_bank_mentions.png "Title")
