# So far we've found that the dodds word score (linear evaluation metric) is not
# effectivee at scoring tweets. But it *might* be good on news articles, so I've
# worked out a text scraper to do this work for me.

# So what do we need to do next?

# 1. try out the dodds model on my news files

# 2. try out the BERT model on tweets, and devise some way of producing a summary
# statistic for a week's worth of tweets. Maybe based upon the ratio of positive
# and negative ones?

# 2b.

# 3. generate a jsonl object which will be easy for hirona to plot later.

# 4. do some research on 'trending topics', 'named entity recognition', etc...
# we want meaningful word cloud display

# 5. (on paper) make a story board for what the site layout should look like
import json
from datetime import date, timedelta
import csv

from experiment0 import word_bag, dodds_word_score, get_corpus

# convenience methods
def date_range(d0,d1):
    return [d0+timedelta(days=i) for i in range((d1-d0).days + 1)]


def get_text_by_day():

    group_by_day = {}

    for day in date_range(date(2021, 2, 21), date(2021, 4, 10)):
        group_by_day[str(day)] = ""

    with open("data/demo_scrape.csv") as fp:
        csv_reader = csv.DictReader(fp)

        for row in csv_reader:
            day = row["date"]
            text = row["tweet"]
            group_by_day[day] += text + " "

    with open("data/NEWS.txt") as fp:
        for line in fp:
            doc = json.loads(line)
            day = doc["date"][:10]
            group_by_day[day] += doc["title"] + " " + doc["text"] + " "

    return group_by_day

word_bag_range = get_text_by_day()

output = []
for key,val in word_bag_range.items():

    text_bag = word_bag(val)
    score = dodds_word_score(text_bag)
    d = {"date":key,"score":score,"words":text_bag}
    output.append(d)
    print(json.dumps(d))


exit(0)

corpus = get_corpus("NEWS")

# get my data -- run it against the news bank
w = word_bag(corpus)
score = dodds_word_score(w)

print("this week's news score: {:.2f}".format(score))


t_corpus = get_corpus("TWEETS")
tweets_bag = word_bag(t_corpus)
t_score = dodds_word_score(tweets_bag)


print("this week's tweet score: {:.2f}".format(t_score))
# get my


# ok at this point -- I want a "feature vector" for each week
