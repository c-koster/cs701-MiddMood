from collections import Counter

import csv
import pandas as pd
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS

from sklearn.feature_extraction.text import CountVectorizer

import operator
import json

stopwords = set(STOPWORDS)


CSV_PATH = "data/first_scrape.csv"

def user_tweet_skew():
    counts = Counter()

    with open(CSV_PATH) as fp:
        csv_reader = csv.DictReader(fp)
        for row in csv_reader:
            u=row["username"]
            counts[u] +=1

    df = pd.DataFrame.from_dict(counts,orient='index',columns=['tweets'])
    df['tweets'].hist(bins=100)
    plt.show()
    return


def cloud():
    tweets = pd.read_csv(CSV_PATH)
    #tweets = tweets[tweets['username'] != "bhrenton"]
    #tweets = tweets[tweets['username'] != ""]
    print(tweets['tweet'])

    wordcloud = WordCloud(
        background_color='white',
        stopwords=stopwords,
        max_words=200,
        max_font_size=40,
        random_state=45
    ).generate(str(tweets['tweet']))
    fig = plt.figure(1)
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()
    return


def get_corpus(data_src):
    """
    Sometimes you just want a text corpus of words all jumbled together so you can
    make a bag of words.
    """

    corpus = ""
    if data_src == "TWEETS":
        with open(CSV_PATH) as fp:
            csv_reader = csv.DictReader(fp)
            for row in csv_reader:
                u=row["tweet"]
                corpus = corpus + " " + u
        return corpus.replace(r'[^\s\w]','')
    if data_src == "NEWS":
        with open("scraping-libraries/NEWS.txt") as fp:
            for line in fp:
                print(line)
                doc = json.loads(line)
                u=doc['title'] + doc['text']
                corpus = corpus + " " + u
        return corpus.replace(r'[^\s\w]','')

    else:
        return False



def word_bag(corpus):

    word_features = CountVectorizer(
        strip_accents="unicode",
        lowercase=True,
        ngram_range=(1, 1),
    )
    text_to_words = word_features.build_analyzer()
    assert(text_to_words("Hello hello world!") == ["hello", "hello", "world"])


    words = Counter()

    corpus_iter = text_to_words(corpus)
    for word in corpus_iter:
        if word not in STOPWORDS:
            words[word] +=1

    return words


def get_word_index():
    word_hash = {}
    with open("data/dodds.txt",'r') as wordfile:
            # Combine the lines in the list into a string
            content = wordfile.readlines()
            content = content[4:]
            for word_info in content[:10]:
                w = word_info.split()
                word = w[0]
                word_score = w[2]
                word_hash[word] = word_score # add it to the dict
            #content = "".join(content)

    return word_hash



def dodds_word_score(corpus,word_scores):
    """
    Perform a dodds-grading scheme on a corpus/bag of words. Ignore (but record)
    middlebury-specific or twitter specific words which don't get spotted.
    """
    h_avg = 0
    words_tot = 0
    for w in corpus.items():
        word = w[0]
        freq = w[1]
        if w[0] in word_scores.keys():

            print(word,freq)





if __name__ == "__main__":
    # maybe useful to decide which experiment to run based on text input
    word_hash = get_word_index()
    c = get_corpus("NEWS")
    tweets_bag = word_bag(c)
    dodds_word_score(corpus=tweets_bag,word_scores=word_hash)
