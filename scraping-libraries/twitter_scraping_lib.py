"""
Two tasks needed for data collection:
1. run a search algorithm (BFS probably) on some starting user to find a list of middlebury
twitter users.

NOTE: (1) won't work anymore as twint cannot get a user's follower/following information.
This is behind a login screen now. Backup plan is to use the twitter dev portal, get MiddMood's
followers as a list of strings, and feed it into the twint scraper

2. input a list of users and a date range, retrieve all tweets posted by users across this period.
"""
import twint
from typing import List, Any
import os
from dotenv import load_dotenv
import tweepy
from time import sleep


global data_dir
data_dir = "../data"


# put .env variables as context -- eventually update this to work on a
# non-development environment
load_dotenv()

consumer_key = os.environ.get("TWITTER_KEY")
consumer_secret = os.environ.get("TWITTER_SECRET")
access_key = os.environ.get("TWITTER_ACCESS")
access_secret = os.environ.get("TWITTER_ACCESS_SECRET")


def get_user_list() -> List:
    """
    Connect to twitter's api, scroll through everyone followed by my account,
    and append their handles to my list.
    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    user_list = []

    for friend in tweepy.Cursor(api.friends).items():
        print(friend.screen_name)
        user_list.append(friend.screen_name)

    return user_list


def user_scrape(users: List, outfile: List, limit: int, since: int) -> None:
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

    for u in users:
        # and run the search for each username
        sleep(2.5)
        try:
            print("scanning tweets from user {}".format(u))
            c.Username = u
            twint.run.Search(c)
        except:
            continue


# I am not being imported -- test code or runnning code goes here
if __name__ == '__main__':
    #users = get_user_list()

    users = []
    with open("friends.txt", 'r') as infile:
        for line in infile:
            users.append(line.strip())

    user_scrape(users, limit=100, outfile="first_scrape.csv", since="2021-03-18")
