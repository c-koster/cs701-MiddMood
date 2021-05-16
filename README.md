# MiddMood
By Culton Koster and Hirona Arai


## Project Contents
1. Text Scraping Library - Contains functions for scraping text data from our three sources.
2. Evaluation Library - Using the text files as input, this script produces daily scores and a list of weighted terms for a word-cloud.
3. Experiments - These experiment files contain some early and messy versions of our code.


## Deploy Instructions
1. ensure there is a /data file, which contains a copy of Dodds' word evaluations called dodds.txt (this can be found in the supplementary materials at this link https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0026752#pone.0026752.s001). The text scraping library will look for this file, and will also write scraped tweet and news to the data directory.
$ mkdir data
$ curl {dodds link - this is really long} > data/dodds.txt

2. Ensure that, in evals_lib.py, the output file points somewhere that the heroku app can access.

3. add the two files to the cronjob scheduler. In words, this means:
"At 01:00am on Sunday, scrape the past week's text."
“At 01:30am on Sunday, evaluate and recompile fur_hirona.txt to include the past 7 days of content.”

$ pwd
$ crontab -e

0 1 * * 0 python3 {pwd}/text_scraping_lib.py
30 1 * * 0 python3 {pwd}/evals_lib.py


## Link to our Site

https://www.middood.herokuapp.com
