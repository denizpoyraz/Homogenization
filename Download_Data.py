import csv
import urllib
import requests
import pandas as pd

## this code takes a csv file that has the urls of the each data day, and downloads the corresponding url csv file

df = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/woudc-DataURLFileList_Praha_All.csv", low_memory=False)

size = len(df)


for i in range(size):
    url = df.at[i, 'url']

    name = str(url.split("/")[-1].split(".")[0]) + '.csv'
    # print(name, type(name))
    year = name[0:4]
    # print(year)
    if (year == '2020') | (year == '1996'):

        req = requests.get(url)

        url_content = req.content

        csv_file = open('../Files/Praha/'+name, 'wb')

        csv_file.write(url_content)

        csv_file.close()



