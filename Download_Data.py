import csv
import urllib
import requests
import pandas as pd

## this code takes a csv file that has the urls of the each data day, and downloads the corresponding url csv file
## First one needs to download data-file url list from https://woudc.org/data/explore.php?lang=en

df = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/woudc-DataURLFileList_Praha_All.csv", low_memory=False)
# df = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/woudc-DataURLFileList_Madrid_All.csv", low_memory=False)

pathout = 'Praha'

size = len(df)


for i in range(size):
    url = df.at[i, 'url']

    name = str(url.split("/")[-1].split(".")[0]) + '.csv'
    # print(name, type(name))
    year = name[0:4]
    # print(year)
    # for the moment only downloading some years 2020 and 1996
    # if (year == '2020') | (year == '1996'):

    req = requests.get(url)

    url_content = req.content

    csv_file = open('../Files/' + pathout + '/' + name, 'wb')

    csv_file.write(url_content)

    csv_file.close()



