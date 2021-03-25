import requests
from bs4 import BeautifulSoup

# globals - noodle
noodle_url = "https://thelocalnoodle.com/page/"

# globals - campus
begin = 35088

campus_url = 'https://middleburycampus.com/'

# the two sitemaps which include articles from our desired date range
campus_categories = ['sports','news','local','opinion','arts-academics']

@dataclass
class Article:
    date: str
    headline: str
    link: str
    text: str

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
    maps = ['wp-sitemap-posts-post-7.xml','wp-sitemap-posts-post-8.xml']
    return fetch_articles_campus(maps)
