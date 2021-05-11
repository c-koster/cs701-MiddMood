#%% import file

import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('../../first_scrape.csv', usecols= ['date', 'username','tweet', 'Positive', 'Negative', 'Relax', 'Stress'])

#%% raw boxplot

print(df.head())
box = df.boxplot(column= ['Positive', 'Negative'], by='date')
plt.show()

#%% get rid of neutral  text (positive = 1, negative = -1)

filter_pos = df["Positive"] != 1
filter_neg = df["Negative"] != -1
filter_relax = df["Relax"] != 1
filter_stress = df["Stress"] != -1


filtered = df[((filter_pos & filter_neg) & (filter_relax & filter_stress))]
print(filtered.head())

#box = filtered.boxplot(column= ['Positive', 'Negative'], by='date')

#not interesting because integer values
#plt.show()

# %% plot mean scores by date
filtered.groupby('date')['Positive', 'Negative', 'Relax', 'Stress'].mean().plot()

# %% adjust to fit graph better
# def adjust_pos(n):
#     return n-2

# def adjust_neg(n):
#     return n+2

def add(n,m):
    return n+m

# filtered['Positive_adjusted']=filtered.apply(lambda row: adjust_pos(row.Positive), axis = 1)
# filtered['Negative_adjusted']=filtered.apply(lambda row: adjust_neg(row.Negative), axis = 1)
# filtered.groupby('date')['Positive_adjusted', 'Negative_adjusted'].mean().plot()

filtered['Senti_Sum']=filtered.apply(lambda row: add(row.Positive, row.Negative), axis = 1)
filtered['Tensi_Sum']=filtered.apply(lambda row: add(row.Relax, row.Stress), axis = 1)
filtered.groupby('date')['Senti_Sum', 'Tensi_Sum'].mean().plot()


# %%
thelwall=pd.DataFrame(filtered.groupby('date')['Senti_Sum', 'Tensi_Sum'].mean())
print(thelwall.head())
thelwall.to_json(path_or_buf='../../filtered.json')

# %%
