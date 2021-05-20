"""
This is our library for automated data processing and scoring for tweets and news.

INPUT:
we take as input the two outfiles from the text scraping libraryself.

- a tweets csv file
- a news articles jsonl file
- a 'tuning parameter' for our evaluation function, which determines our sensitivity to
neutrally-rated words.

OUTPUT:
A text file of dictionary objects, in which each line corresponds with one day's
text and happiness score.
"""
# killer combo -- collections.Counter and CountVectorizer
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer



from nltk.tokenize import TweetTokenizer
from nltk import pos_tag, word_tokenize, ne_chunk
# pos tag is a
# our lord and savior --
tweet_tokenizer = TweetTokenizer(strip_handles=True)


# python but fancier
from tqdm import tqdm
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


import sys
import csv
import math
import os
import json
from datetime import date, timedelta


# manage file paths up here -- everything goes into a data folder called 'data'
data_dir = "./data"
csv_filename = "tweets_out.csv"
news_filename = "news_out.txt"
dodds_filename = "dodds.txt"
badwords_filename = "badwords.txt"
out_filename = "fur_hirona.txt"

from wordcloud import STOPWORDS
STOPWORDS = set(STOPWORDS)
STOPWORDS = STOPWORDS | set(['t','co','http','https'])
# https is really trending huh
with open(os.path.join(data_dir, badwords_filename)) as fp:
    for line in fp:
        l = line.replace("\n","").split(" ")
        if len(l) == 1:
            STOPWORDS.add(l[0])


filepath_n = os.path.join(data_dir, news_filename)
filepath_t = os.path.join(data_dir, csv_filename)
filepath_dodds = os.path.join(data_dir, dodds_filename)
filepath_out = os.path.join(data_dir, out_filename)


# ASSERT: WE HAVE ALL THE FILES IN THE DATA DIR THAT WE NEED
assert(os.path.exists(filepath_n))
assert(os.path.exists(filepath_t))
assert(os.path.exists(filepath_dodds))


# convenience functions --
def date_range(d0: date,d1: date) -> List:
    """ give me a range of days """
    return [d0+timedelta(days=i) for i in range((d1-d0).days)]

def get_word_index(DIAL: int=2) -> Dict:
    """ Load the dodds/mturk word bank into a dictionary for quick lookups"""
    word_hash = {}

    with open(filepath_dodds,'r') as wordfile:
        # Combine the lines in the list into a string
        content = wordfile.readlines()
        content = content[4:] # idc about headers
        for word_info in content:
            w = word_info.split()
            word = w[0]
            word_score = float(w[2])
            if abs(5 - word_score) > DIAL:
                word_hash[word] = word_score # add it to the dict
    return word_hash


@dataclass
class TextData:
    name: str
    corpus: str
    counts: Optional[Dict[str,int]] = None
    score: Optional[float] = None
    pos: Optional[Dict[str,int]] = None

    def add_to(self,text: str) -> None: # convenience method
        self.corpus = self.corpus + " " + text + " "

    def add_pos(self,name: str) -> None: # another convenience method
        if self.pos == None:
            self.pos = {}
        self.pos[name] = self.pos.get(name, 0) + 1


    def to_dict(self) -> Dict:
        """
        This method creates a list of all the words in a string, and returns them all
        as counts in a dictionary.
        example:
            text_to_words("Hello hello world!") == ["hello", "hello", "world"]
            {"hello": 2, "world": 1}
        """
        word_features = CountVectorizer(
            strip_accents="unicode",
            lowercase=True,
            ngram_range=(1, 1),
        )
        text_to_words = word_features.build_analyzer()

        words = Counter() # special dict which makes it easy to count things

        corpus_iter = text_to_words(self.corpus)
        # string -> list of lowercase words with no punctuation
        for word in corpus_iter:
            if word not in STOPWORDS:
                words[word] +=1

        return words # return the dict

    def to_jsonl(self) -> str:
        self.score = self.dodds_word_score() # first compute the score
        try:
            merged_dict = {**self.counts, **self.pos}
        except TypeError:
            merged_dict = self.counts

        dict_out = {
            "date": self.name,
            "score": self.score,
            "words": merged_dict,
        }

        return json.dumps(dict_out)


    def dodds_word_score(self,word_scores=get_word_index()):
        """
        Perform a dodds-grading scheme on a corpus/bag of words.
        """
        self.counts = self.to_dict()

        h_avg = 0
        words_tot = 0
        for w in self.counts.items():
            word = w[0]
            freq = w[1]

            if word in word_scores.keys():
                h_avg += word_scores[word] * freq
                words_tot += freq

        # SAFE MEAN -- if there were no examples we should predict the mean
        if words_tot == 0:
            return 5.0

        val = h_avg / words_tot # round me to the 100's place before returning
        return math.ceil(val * 100) / 100


def get_corpus(data_src: str) -> TextData:
    """
    Sometimes you want a text corpus of words all jumbled together so you can
    make a bag of words later with count vectorizer. Simple way to scrape text.
    """
    corpus = ""
    if data_src == "TWEETS":
        with open(filepath_t) as fp:
            # get all my tweets to a single string
            csv_reader = csv.DictReader(fp)
            for row in csv_reader:
                u=row["tweet"]
                corpus = corpus + " " + u
        return TextData(data_src,corpus.replace(r'[^\s\w]',''))

    if data_src == "NEWS":
        with open(filepath_n) as fp:
            for line in fp:
                # append all the article text to a single string
                doc = json.loads(line)
                u=doc['title'] + doc['text']
                corpus = corpus + " " + u
        return TextData(data_src,corpus.replace(r'[^\s\w]','')) # then clean and return it

    else: # other data sources -- h
        return TextData("IDK","")


def get_text_by_day(d0: date, d1: date):
    """
    Create a dictionary with keys for each day in the range [d0, d1). Then
    sort/group all our text into these date buckets.
    """
    group_by_day = {}

    for day in date_range(d0,d1):
        key = str(day)
        group_by_day[key] = TextData("{}".format(key),"")

    with open(filepath_t) as fp:
        csv_reader = csv.DictReader(fp)

        for row in csv_reader: # TWEETS
            try:
                day = row["date"] # row["date"] may or may not exist with a limited date range
                text = row["tweet"]

                # now do a text_cleaning step -- us the twet tokenizer for nltk in a list comprehension
                text_clean = ' '.join([i for i in tweet_tokenizer.tokenize(text) if "https" not in i])
                # the just making sure the https://t.co/{ link } doesn't get parsed and added
                group_by_day[day].add_to(text_clean)

            except KeyError: # the date wasn't in our range... keep going
                continue

    with open(filepath_n) as fp: # NEWS
        for line in tqdm(fp,total=778): # 
            try: # try to load the article into this day's TextData object
                doc = json.loads(line)
                day = doc["date"][:10]

                tokenized_article = word_tokenize(doc["text"])
                tagged = pos_tag(tokenized_article)
                trees = ne_chunk(tagged, binary=True)
                for tree in trees:
                    if (hasattr(tree, 'label') and len(tree)>1):

                        entity = ' '.join([child[0].lower() for child in tree])
                        group_by_day[day].add_pos(entity)

                group_by_day[day].add_to(doc["title"])

                # clean before adding it to the text corp

                group_by_day[day].add_to(doc["text"])

            except KeyError: # as above
                continue

    return group_by_day


if __name__ == "__main__":

    # declare defaults
    date_end = date.today()
    date_start = date_end - timedelta(days=7)


    # get your dates from sys.argv
    if len(sys.argv) > 1: # unless someone input a different date in the command line

        try:
            date_start = date.fromisoformat(sys.argv[1])

            if len(sys.argv) == 3:
                date_end = date.fromisoformat(sys.argv[2])

        except ValueError:
            print("Bad datetime string!")
            print("usage: python3 {} <start_date: yyyy-mm-dd> <(end_date): yyyy-mm-dd>".format(sys.argv[0]))
            exit(-1)

    # construct get-text-by-day dictionary
    dates = get_text_by_day(date_start,date_end)

    # write me to some file in a place that hirona can read from
    with open(filepath_out,"w") as outfile:
        for i in dates.values():
            print(i.to_jsonl(),file=outfile)
            # using a textdata method to convert each 'day' into a jsonlines
