# so the functions here return headlines as headline/link pairs
# I want a list of articles




import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import tqdm

# globals - noodle
noodle_url = "https://thelocalnoodle.com/page/"

# globals - campus
begin = 54164

campus_url = 'https://middleburycampus.com/'

# the two sitemaps which include articles from our desired date range
campus_categories = ['sports','news','local','opinion','arts-academics']

def get_headlines_noodle(page):
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

def fetch_all_noodle():
    # get all noodle headlines from their wordpress site
    noodle_headlines = []
    for i in range(1,15): # there are 15 pages presently
        url_i = noodle_url + str(i) + "/"
        noodle_headlines += get_headlines_noodle(url_i)

    return noodle_headlines


def get_text_noodle(article):
    title = article[0]
    link = article[1]
    r = requests.get(link)
    html_doc = r.content

    return


def get_text_campus(article):

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

    date_text = soup.find("span",{"class": "time-wrapper"}).text
    date = datetime.strptime(date_text, '%B %d, %Y') # this is still a datetime object

    title = soup.find("h1",{"class": "storyheadline"}).text

    return {'title':title,'text':text,'date':date,'link':link}


def fetch_articles_campus(maps):
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


def fetch_all_campus():
    # now let's use the campus sitemap to get all of its headlines. the noodle started
    # in september of 2016, so let's start our scrape there.
    maps = ['wp-sitemap-posts-post-8.xml']
    return fetch_articles_campus(maps)




if __name__ == "__main__":
    campus = fetch_all_campus()
    #noodle = fetch_all_noodle()

    campus_texts_full = []
    for article_pair in campus:
        campus_texts_full.append(get_text_campus(article_pair))
        #print(article_pair[0])


    seven_days_ago = datetime.now() - timedelta(days=7)
    for a in campus_texts_full:
        if a['date'] > seven_days_ago:
            a['date'] = str(a['date'])
            print(a)

    """
    noodle_texts_full = []
    for article_pair in noodle:
        noodle_texts_full.append(get_text_noodle(article_pair))
    """
    # eh just filter by date and dump it all to stdout ... ?
