import pandas as pd
from collections import Counter

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
