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
import typing
import os
from dotenv import load_dotenv


global data_dir
data_dir = "../data"




def get_user_list() -> list:
    """

    """

    return ["kfuentesgeorge","middlebury","middcampus"]


def user_scrape(users: list, outfile: str, limit: int, since: int) -> None:
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
        print("scanning tweets from user {}".format(u))
        c.Username = u
        twint.run.Search(c)


# I am not being imported -- test code goes here

if __name__ == '__main__':
    test_users = get_user_list()
    #exit(0) # stop here for now

    user_scrape(test_users, limit=100, outfile="test.csv", since="2021-03-06")
