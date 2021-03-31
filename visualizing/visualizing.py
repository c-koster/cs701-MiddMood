#%% import file

import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('../../first_scrape.csv', usecols= ['date', 'username','tweet', 'Positive', 'Negative'])

#%% raw boxplot

print(df.head())
box = df.boxplot(column= ['Positive', 'Negative'], by='date')
plt.show()

#%% get rid of neutral  text (positive = 1, negative = -1)

filter_pos = df["Positive"] != 1
filter_neg = df["Negative"] != -1

filtered = df[filter_pos & filter_neg]
print(filtered.head())

box = filtered.boxplot(column= ['Positive', 'Negative'], by='date')

#not interesting because integer values
plt.show()

# %% plot mean scores by date
filtered.groupby('date')['Positive', 'Negative'].mean().plot()

# %% adjust to fit graph better
def adjust_pos(n):
    return n-2

def adjust_neg(n):
    return n+2

filtered['Positive_adjusted']=filtered.apply(lambda row: adjust_pos(row.Positive), axis = 1)
filtered['Negative_adjusted']=filtered.apply(lambda row: adjust_neg(row.Negative), axis = 1)
filtered.groupby('date')['Positive_adjusted', 'Negative_adjusted'].mean().plot()
