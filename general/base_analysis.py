import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def generate_most_occurring_words(filename):
    # number of most common words to show
    k_words = 200

    summary_df = pd.read_csv('../data/summary_20231113.csv')
    summary_df = summary_df[summary_df['date'].notnull()]
    summary_df['date'] = pd.to_datetime(summary_df['date'])

    summary_df_since_7th = summary_df[summary_df['date'] > '2023-10-06']

    text = summary_df_since_7th['title_from_page'].values.tolist()

    combined = " ".join(text)

    data_set = combined
    split_it = data_set.split()
    counters_found = Counter(split_it)

    most_occuring = counters_found.most_common(k_words)
    most_occuring_df = pd.DataFrame(most_occuring, columns=['word', 'count'])

    most_occuring_df.to_csv('../outputs/'+filename)

def create_word_bank_time_plot(filename):
    articles_7th = pd.read_csv('../bbc-bias/data/summary_20231007_to_20231113.csv')
    articles_7th['date'] = pd.to_datetime(articles_7th['date'])
    articles_7th['day'] = articles_7th['date'].dt.to_period('D')

    articles_word_bank = articles_7th.filter(regex='contains|week|day|date|title')
    articles_word_bank = articles_word_bank[articles_word_bank['date'] >= '2023-10-07']
    articles_summary = articles_word_bank.groupby(pd.Grouper(key='date', freq='W-Fri')).agg({
        'day': 'count',
        'contains_palestine_word_bank': 'sum',
        'contains_israel_word_bank': 'sum',
        'contains_hamas_word_bank': 'sum',
        'contains_gaza_word_bank': 'sum',
        'contains_palestine_protest_reference': 'sum',
    }).reset_index()

    # separate references to palestine outside of protest context to protest context
    articles_summary['contains_palestine_word_bank'] = articles_summary['contains_palestine_word_bank'] - \
                                                       articles_summary['contains_palestine_protest_reference']

    # normalise to percentage
    for column in articles_summary.columns:
        if 'contains' in column:
            articles_summary[column] = articles_summary[column] / articles_summary['day'] * 100.

    # fixing the weekly rolling grouping (so it starts on the 2022-10-07)
    articles_summary['start_date'] = articles_summary['date'] - pd.to_timedelta(6, unit='d')
    articles_summary['start_date'] = articles_summary['start_date'].dt.date

    renaming_dict = {
        'contains_palestine_word_bank': 'Mentions Palestine (non-protest) word bank',
        'contains_israel_word_bank': 'Mentions Israel word bank',
        'contains_hamas_word_bank': 'Mentions Hamas',
        'contains_gaza_word_bank': 'Mentions Gaza',
        'contains_palestine_protest_reference': 'Contains Palestine protest reference',
    }

    fig, ax = plt.subplots(figsize=(8, 6))

    dates = articles_summary['start_date']
    x = np.arange(len(dates))
    colors = {
        'contains_palestine_word_bank': 'yellow',
        'contains_palestine_protest_reference': 'orange',
        'contains_israel_word_bank': 'blue',
        'contains_hamas_word_bank': 'slategray',
        'contains_gaza_word_bank': 'violet',
    }

    ax.bar([0.5, 1.5, 2.5, 3.5, 4.5, 5.5], articles_summary.contains_palestine_word_bank,
           align='edge', width=0.2, color=colors['contains_palestine_word_bank'], edgecolor='black', linewidth=0.3,
           label=renaming_dict['contains_palestine_word_bank']),

    for i, column in enumerate(articles_summary.columns):
        i = i + 1
        if 'contains' in column:

            if 'palestine' in column:
                continue

            y = articles_summary[column]
            print(column, x + (0.2 * i))
            ax.bar(x + (0.2 * i), y, width=0.2, label=renaming_dict[column], color=colors[column], edgecolor='black',
                   linewidth=0.3)

    ax.bar([0.5, 1.5, 2.5, 3.5, 4.5, 5.5], articles_summary.contains_palestine_protest_reference,
           align='edge', width=0.2, color=colors['contains_palestine_protest_reference'],
           bottom=articles_summary.contains_palestine_word_bank,
           edgecolor='black', linewidth=0.3, label=renaming_dict['contains_palestine_protest_reference'])

    ax.set_xticklabels([''] + articles_summary['start_date'].values.tolist())

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 1.1])

    handles, labels = plt.gca().get_legend_handles_labels()
    order = [0, 4, 2, 3, 1]
    ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='upper center', handleheight=1,
              bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=False, ncol=4, prop={'size': 6.8})

    ax.set_xlabel('Week starting')
    ax.set_ylabel('% of all article titles which contain word/word bank item')

    ax.set_title("Proportion of BBC articles mentioning Palestine/Israel")

    plt.savefig('./outputs/'+filename, bbox_inches='tight', dpi=300)

if __name__ == '__main__':
    generate_most_occurring_words('most_occurring.csv')
    create_word_bank_time_plot('word_bank_mentions_20231007_to_20231113.png')
