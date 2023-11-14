import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

if __name__ == '__main__':
    """
    A simple analysis to print out the most common X words
    """

    # number of most common words to show
    k_words = 200

    summary_df = pd.read_csv('./data/summary.csv')
    summary_df = summary_df[summary_df['date'].notnull()]
    summary_df['date'] = pd.to_datetime(summary_df['date'])

    summary_df_since_7th = summary_df[summary_df['date'] > '2023-10-06']

    text = summary_df_since_7th['title_from_page'].values.tolist()

    combined = " ".join(text)

    data_set = combined
    split_it = data_set.split()
    Counters_found = Counter(split_it)

    most_occuring = Counters_found.most_common(k_words)
    most_occuring_df = pd.DataFrame(most_occuring, columns=['word', 'count'])

    most_occuring_df.to_csv('most_occuring.csv')

    summary_df['day'] = summary_df['date'].dt.to_period('D')
    word_bank = {
        'palestine_word_bank': ['Palestine', 'Palestinian', 'Palestinians'],
        'israel_word_bank': ['Israel', 'Israeli', 'Israelis', 'IDF', 'I.D.F.'],
        'hamas_word_bank': ['Hamas'],
        'gaza_word_bank': ['Gaza'],
    }

    for bank, items in word_bank.items():
        summary_df['contains_' + bank] = summary_df['title'].str.strip().str.lower().str.contains(
            '|'.join([x.lower().strip() for x in items]), regex=True)

    # we can remove the articles which are talking about palestine only in the context of rallies/pro palestine gatherings
    #summary_df = summary_df[~summary_df['title'].str.lower().str.contains('pro-')]

    articles_word_bank = summary_df.filter(regex='word_bank|day')
    articles_summary = articles_word_bank.groupby('day').sum().reset_index()

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))

    dates = articles_summary['day'].astype(str).values

    for column in articles_summary.columns:
        if 'day' not in column:
            ax.plot(dates, articles_summary[column].values, label=column)

    ax.legend()
