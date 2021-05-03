"""
This is our text scraping library for

TWITTER:
Two tasks needed for data collection:
1. run a search algorithm (BFS probably) on some starting user to find a list of middlebury
twitter users.

NOTE: (1) won't work anymore as twint cannot get a user's follower/following information.
This is behind a login screen now. Backup plan is to use the twitter dev portal, get MiddMood's
followers as a list of strings, and feed it into the twint scraper

2. input a list of users and a date range, retrieve all tweets posted by users across this period.
"""

from tqdm import tqdm
import os
import json
import sys
from itertools import chain

# twitter scraping dependencies
import twint
from typing import List, Any, Dict, Tuple
import tweepy
from time import sleep

# news scraping dependencies
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


global data_dir
data_dir = "./data"


# put .env variables as context -- eventually update this to work on a
# non-development environment
if os.environ.get("IS_HEROKU") == None:
    from dotenv import load_dotenv
    load_dotenv()

consumer_key = os.environ.get("TWITTER_KEY")
consumer_secret = os.environ.get("TWITTER_SECRET")
access_key = os.environ.get("TWITTER_ACCESS")
access_secret = os.environ.get("TWITTER_ACCESS_SECRET")


def get_user_list(friends_filename: str = "friends.txt") -> List:
    """
    Connect to twitter's api, scroll through everyone followed by my account,
    and append their handles to my list.
    """
    users: List = []
    # two cases for running this function --
    # either there is a list already or there is not
    f_path = os.path.join(data_dir, friends_filename)
    if os.path.exists(f_path): # if the friends list is here already... just load it up

        with open(f_path, 'r') as fp:
            users = [line.strip() for line in fp.readlines()]


    else: # if NOT, let's ask for our following list using the twitter api
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)

        for friend in tweepy.Cursor(api.friends).items():
            sleep(1)
            #print(friend.screen_name)
            users.append(friend.screen_name)

        # and then write the friends.txt file
        with open(f_path,'w') as fp: # O_CREAT || O_WRONLY
            [fp.write("{}\n".format(u)) for u in users]

    return users


def user_scrape(users: List, outfile: str, limit: int, since: str) -> None:
    """
    Scrape all tweets created by a list of users, beginning at some date, and write
    all contents into a file.
    """
    assert(len(users)>0)

    # put params into configuration object
    c = twint.Config()
    c.Hide_output = True
    c.Limit = limit
    c.Language = "en"
    c.Output = os.path.join(data_dir, outfile)
    c.Store_csv = True
    c.Since = since

    for u in tqdm(users, total=294):
        # and run the search for each username
        sleep(2.5)
        try:
            #print("scanning tweets from user {}".format(u))
            c.Username = u
            twint.run.Search(c)
        except:
            continue


"""
Here are all the campus and noodle scraping functions:

scrape_all accepts a 'since' datetime parameter and runs
    fetch_all_campus
    and
    fetch_all_noodle
"""

# so the functions here return headlines as headline/link pairs
# I want a list of articles

# globals - noodle
noodle_url = "https://thelocalnoodle.com/page/"

# globals - campus
begin = 53741 # 47710 is roughly the end of 2019
campus_url = 'https://middleburycampus.com/'

# the two sitemaps which include articles from our desired date range
campus_categories = ['sports','news','local','opinion','arts-academics']

def get_headlines_noodle(page: str) -> List:
    headlines = []

    r = requests.get(page)
    html_doc = r.content

    soup = BeautifulSoup( html_doc , 'html.parser')
    # for each entry that I find
    for e in soup.find_all("h1", {"class": "entry-title"}):
        # get the text and put it into a list
        link_elem = e.find_all('a', href=True)
        link = link_elem[0]['href']
        headlines.append((e.text,link))

    return headlines

def fetch_all_noodle() -> List:
    # get all noodle headlines from their wordpress site
    noodle_headlines = []
    for i in range(1,15): # there are 15 pages presently
        url_i = noodle_url + str(i) + "/"
        noodle_headlines += get_headlines_noodle(url_i)

    return noodle_headlines


def get_text_noodle(article: Tuple) -> Dict:
    title = article[0]
    link = article[1]
    r = requests.get(link)
    html_doc = r.content
    soup = BeautifulSoup( html_doc , 'html.parser')
    text = ""
    content = soup.find_all("div",{"class": "entry-content"})[0]
    for p in content.find_all("p"):
        text = text + p.text

    date_text = soup.find_all("a",{"class": "entry-date"})[1].text
    date = datetime.strptime(date_text, '%B %d, %Y')

    return {'title':title,'text':text,'date':date,'link':link}


def get_text_campus(article: Tuple) -> Dict:

    # unpack the article tuple:
    # title will be over-written because my title parser for campus articles is unreliable
    link = article[1]

    r = requests.get(link)
    html_doc = r.content
    soup = BeautifulSoup( html_doc , 'html.parser')

    text = ""
    content = soup.find_all("span",{"class": "storycontent"})[0]
    for p in content.find_all("p"):
        text = text + p.text
    try:
        date_text = soup.find("span",{"class": "time-wrapper"}).text
        date = datetime.strptime(date_text, '%B %d, %Y') # this is still a datetime object
    except:
        return False
    title = soup.find("h1",{"class": "storyheadline"}).text

    return {'title':title,'text':text,'date':date,'link':link}


def fetch_articles_campus(maps: List) -> List:
    articles = []

    for m in maps: # for each sitemap linked
        r = requests.get(campus_url + m)
        soup = BeautifulSoup( r.content , 'html.parser')
        for e in soup.find_all("loc"):
            # e is an individual link

            # if this is a desired category in the right timeframe
            t = e.text[29:].split('/')
            if (int(t[0]) > begin) and (t[1] in campus_categories):
                headline = t[2].replace('-',' ')

                articles.append((headline,e.text))
                # save its (headline, url) to the articles list

    return articles

def fetch_all_campus() -> List:
    # now let's use the campus sitemap to get all of its headlines. the noodle started
    # in september of 2016, so let's start our scrape there.
    maps = ['wp-sitemap-posts-post-8.xml','wp-sitemap-posts-post-9.xml']
    return fetch_articles_campus(maps)


def scrape_all_news(since: datetime, outfile: str) -> None:

    f_dir = os.path.join(data_dir, outfile)

    # this gets us all headlines
    campus = fetch_all_campus()
    noodle = fetch_all_noodle()

    # this will look at each headline and pull text for us
    campus_texts_full = []
    for article_pair in campus:
        a = get_text_campus(article_pair)
        if a != False:
            campus_texts_full.append(a)

    noodle_texts_full = []
    for article_pair in noodle:
        noodle_texts_full.append(get_text_noodle(article_pair))

    # how to use the ternary op:
    # [on_true] if [expression] else [on_false]


    open_type = 'a' # append mode --
    if not os.path.exists(f_dir): # but if the file oesn't exist, write instead
        open_type = 'w'

    with open(f_dir, open_type) as fp:

        for a in chain(campus_texts_full, noodle_texts_full):
            if a['date'] > since:
                a['date'] = str(a['date'])
                fp.write("{}\n".format(json.dumps(a)))


# I am not being imported -- running code goes here
if __name__ == '__main__':

    #  make "date start" equal to one week ago... and run it
    date_start_dt = datetime.now() - timedelta(days=7)
    date_start = str(date_start_dt)[:10]

    if len(sys.argv) > 1: # unless someone input a different date in the command line
        try:
            date_start = sys.argv[1]
            date_start_dt = datetime.strptime(date_start, '%Y-%m-%d')
        except ValueError:
            print("Bad datetime string!")
            exit(-1)

    # run the twitter scrape
    users = get_user_list()
    user_scrape(users, limit=100, outfile="tweets_out.csv", since=date_start)
    # and the campus scrape
    scrape_all_news(since=date_start_dt,outfile="news_write_test.txt")
