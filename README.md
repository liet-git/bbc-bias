# Overview

In the following repository, we aim to analyse the bias in BBC reporting on Palestine, through providing transparent and reproducible methods for both obtaining BBC posts (articles and livefeeds) as well as a process for analysising the casualty mentions within the text. We have applied this technique to data since October 7, 2023 (a combined total of more than 600 articles, and 4000 posts in livefeeds), to investigate and show the disparity in the Palestinian and Israeli mentions of death.

This analysis has been produced by Dana Najjar and Jan Lietava, with the original application and the NLP/annotation code, (credited within) [by Holly Jackson on NYT data](https://github.com/hollyjackson/casualty_mentions_nyt).

The pipeline of the study is as follows:
1. We obtain source articles and livefeed posts from the BBC website (selecting relevant topics and livefeeds). 
2. We preprocess the article data to be in the correct format, and use a natural language processing pipeline ([Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/)) to parse the grammatical structure of the sentences.
3. We use the results from the pre-processing step to identify sentences with mention of death, and **manually tag each one of them**, using the following categories: Palestinian, Israeli, none (neither) or both. Please note, none of the tagging is performed automatically.

We also provide the raw, annotated sentences, which can be found in `./nlp/fatality_counts/summary/`.

## 1. Source data

Posts from the BBC were obtained from two main sources:
1. Articles published to specific topics
2. Livefeed articles

Due to the terms of conditions, we do not include all the full, raw article data in the repository, but do provide the reference jsons for obtaining them directly.

To validate that our sample of scraped articles is representative of the majority of published work by the BBC (considering articles can be published outside of our selected topics/livefeeds) on the topic of Palestine since October 7, we also scraped articles using the search functionality, using several search terms (Palestine/Israel/Gaza). More than 90% of all articles found using the search were present in our dataset. 

### 1.1 Articles
Due to the limitations of the BBC search (limited to only 30 page results), we obtained articles through the use of topics. Topics are a BBC functionality that allows for articles to be posted related to 'themes' and have no time/number limit. We scraped data from the following 6 topics: 
* [Gaza](https://www.bbc.com/news/topics/cgv64vq5z82t)
* [Israel](https://www.bbc.com/news/topics/c302m85q5ljt)
* [Israel and the Palestinians](https://www.bbc.com/news/topics/c207p54m4rqt)
* [Israel-Gaza war](https://www.bbc.com/news/topics/c2vdnvdg6xxt)
* [Hamas](https://www.bbc.com/news/topics/cnx753jen5zt)
* [Palestinian Territories](https://www.bbc.com/news/topics/cdl8n2eder8t)

These are included in the ```./data/topics.json``` file. 

Between October 7, 2023 and December 2, 2023, we collected 672 articles. 

### 1.2 Livefeeds
Livefeeds are a format that allow for multiple, smaller, blog-style posts over a longer period of time (usually 1-3 days). We collected livefeeds that covered the period from October 7, 2023 to December 2, 2023. This was done through the livefeeds themselves (they generally link to the next continuation), but also through Google advanced search, which allowed us to find the results between specific dates, with a specific URL.

All the livefeeds that were used can be found in ```./data/livefeeds.json```. 

Between October 7, 2023 and December 2, 2023 we collected 4404 invididual posts from 29 livefeeds. 

## 2. Pre-processing

The python notebook in ```./nlp/preprocessing.ipynb``` provides the scripts and code for preparing the raw, article data into a format that is processable by the Stanford CoreNLP package. 

After pre-processing using the above, run the following (replacing ```path/to/``` with your specific path):

```
export CLASSPATH=$CLASSPATH:/path/to/stanford-corenlp-4.5.5/*:
java edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,depparse -filelist all-files.txt -outputFormat json -outputDirectory ./results
```

This will generate results files in the ```./nlp/results/``` directory for each article. 

## 3. Annotating the sentences

We use the same process as seen [here](https://github.com/hollyjackson/casualty_mentions_nyt#3-automated-and-manual-tagging), with the following text copied directly, with small modifications (highlighted in bold) where our method was different.

We use linguistic annotations from the Stanford CoreNLP preprocessing and extract sentences which contain mentions of death using a pre-compiled word bank. **However, we widen the "detection" by also including adjectives (rather than just verbs)**. The classification is identical, where each sentence is tagged as either Palestinian, Israeli, both (if the sentence contains multiple victims), or none (if the sentence is unrelated to Palestine and Israel, or if it occurred before October 7, 2023). 

The data is manually tagged according to the following general rules:

* The victim must be Palestinian or Israeli or the death otherwise occured in the West Bank, Gaza, or Israel ('48 lands)
* The mention cannot be speculative (i.e. "He may die") and must have already happened
* The mention must refer to a fatality event that has happened on or since 10/7
* Injuries do not count
  
There is also an option for 'Next', if the sentence contains insufficient details for classification. If the annotator selects 'Next', the sentence is shown in context with the three preceding and three following sentences. If there is still insufficient details, the annotator can select 'Next' one more time to display the entire text of the article, where 'none' can still be assigned if it is still uncertain. 

# Results

## Casualty mentions over time

## Word bank analysis

# Bias, sources of error and limitations

## Bias in machine learning methods

There are many studies highlighting the inherent bias (racist, Islamophobic, sexist, and other forms) present in machine learning models, and specifially natural language processing, which will also be present in the Stanford CoreNLP linguistic pipeline ([Jacskon, 2023](https://github.com/hollyjackson/casualty_mentions_nyt); Abid et al., 2021; Bolukbasi et al., 2016; Bordia and Bowman, 2019; Lu et al., 2020; Nadeem et al., 2020; Shearer et al., 2019; Sheng et al., 2019; Garimella et al., 2019). Hence, considering this structural, and inherent, anti-Palestinian bias in machine learning techniques, there may be further and deeper bias which we are not capturing. Furthermore, these biases are also present in the manual processes of annotation, which does also affect the resulting data (Lee, N.T., 2018).

Another source of error can be the disagreement, or lack of consistency, with annotation. To try and mitigate this, during annotation we made sure to overlap samples of the data between the two core annotators, and cross check the results, as well as having a third independent person annotate a random sample of the data for verification. 

## Limitations

In terms of limitations of the study:
* Due to the limited direct access to all historical BBC articles, our method does not necessarily capture all articles/posts published relating to Israel/Palestine since October 7, 2023. However, the size of our dataset (~5000 posts/articles) highlights a very large, representative sample. We also scraped different search terms from the BBC website directly, and found 90%+ of those articles present in our dataset between October 7 and December 2. 
* Since we use a manual word bank for part of the selection, there are references to death that we may not have detected. 
