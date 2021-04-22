#%% USING NLTK
import nltk
import re
import json

from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
#%%

articles = []

with open("../../campus_text.jsonl",  'r', encoding='utf-8') as fp:
    for line in fp:
        p = re.compile('(?<!\\\\)\'')
        double_quotes = p.sub('\"', line)
        no_backslash = re.sub(r"\\xa0", u' ', double_quotes)
        info = json.loads(no_backslash)
        articles.append(info['text'])

# culton needs to json with double quotes
# configure beautifulsoup to strip
# clean_text = BeautifulSoup(raw_html, "lxml").get_text(strip=True)
# print clean_text

# %% pos tagging

def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

example = "I grew up on Lincoln and 19th in the Sunset District of San Francisco, where wisps of morning fog would tumble into the city at first light. The district is bounded by Golden Gate Park on one side and Ocean Beach on another. "
sent = preprocess(example)
print(sent)

# %% chunking
pattern = 'NP: {<DT>?<JJ>*<NN>}'

cp = nltk.RegexpParser(pattern)
cs = cp.parse(sent)
print(cs)

# %% IOB tagging

from nltk.chunk import conlltags2tree, tree2conlltags
from pprint import pprint
iob_tagged = tree2conlltags(cs)
pprint(iob_tagged)

# %% PRINT TREE WITH ENTITY

ne_tree = nltk.ne_chunk(pos_tag(word_tokenize(example)))
print(ne_tree)


#%% import
### trying the same thing with spacy
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp = spacy.load('en_core_web_sm')
# %%
sample = nlp(articles[3])
len(sample.ents)
# %%
labels = [x.label_ for x in sample.ents]
print(Counter(labels))

items = [x.text for x in sample.ents]
print(Counter(items).most_common(10))
# %%
#all of the entities in a list
entities = [x for x in sample.ents]
displacy.render(nlp(str(entities)), jupyter=True, style='ent')

#all of the entities formatted in sentences
sentences = [x for x in sample.ents]
displacy.render(nlp(str(sentences)), jupyter=True, style='ent')


# %% let's write some code that aggregates list of named entites and the counts
all_entities = []
for article in articles:
    processed = nlp(article)
    all_entities.extend([x.text for x in processed.ents])
    print("article processed")
Counter(all_entities).most_common(50)

# %%
