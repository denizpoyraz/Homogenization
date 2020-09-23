import csv
import numpy as np
from io import StringIO
from woudc_extcsv import load
import pandas as pd
import glob


allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Praha/2020*csv")

list_data = []
list_mdata = []
list_udata = []

dfm = pd.DataFrame()

fi = 0

for filename in allFiles:

    print(filename)

    extcsv_to = load(filename)

    # access all tables
    tables = extcsv_to.sections.keys()

    ## first copy the profile data and delete this from the keys to save the metadata. For Praha data it is 'PORFILE',
    # watch out that this naming may change from station to station
    profile_keys = extcsv_to.sections['PROFILE'].keys()
    Profile = extcsv_to.sections['PROFILE']['_raw']
    Profile_uncertainity = extcsv_to.sections['PROFILE_UNCERTAINTY']['_raw']

    ## this sections are the ozone profile data
    del extcsv_to.sections['PROFILE']
    del extcsv_to.sections['PROFILE_UNCERTAINTY']

    msize = len(tables)

    for i in range(msize):
        dict = list(tables)[i]
        keys = extcsv_to.sections[dict].keys()
        ksize = len(keys)
        for j in range(1, ksize):
            mstr = dict
            kstr = list(keys)[j]
            if kstr == '_raw': kstr = ""
            astr = mstr + '_' + kstr
            find = dfm.first_valid_index()
            # print(fi, " , " , mstr, " , ", kstr , " , ", extcsv_to.sections[dict][list(keys)[j]])
            dfm.at[fi, astr] = extcsv_to.sections[dict][list(keys)[j]]

    list_mdata.append(dfm)
    #
    dfprofile = StringIO(Profile)
    df = pd.read_csv(dfprofile)
    df['Date'] = dfm.at[fi, 'TIMESTAMP_Date']
    df['Station'] = dfm.at[fi, 'DATA_GENERATION_Agency']

    fi = fi + 1
    list_data.append(df)
    #
    dfprofile_uncertainity = StringIO(Profile_uncertainity)
    df_uncer = pd.read_csv(dfprofile_uncertainity)
    list_udata.append(df_uncer)

dff = pd.concat(list_data,ignore_index=True)
dfu = pd.concat(list_udata,ignore_index=True)
dfmf = pd.concat(list_mdata,ignore_index=True)

dff.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Praha_2020.csv")
dfu.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Praha_2020_unc.csv")
dfmf.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Praha_2020_metadata.csv")
