import pandas as pd
import numpy as np
import re
import glob
import math
from math import log
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from matplotlib.offsetbox import AnchoredText
from math import log
from datetime import time
from datetime import datetime
from scipy import signal
from scipy.interpolate import interp1d

station = 'Uccle'

allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/" + station + "/raw/*raw.txt")

list_data = []

columnString = "Time P T U Height O3 Tbox I Winddir Windv"
columnStr = columnString.split(" ")

columnMeta  = ['mDate', 'mRadioSondeNr', 'PF', 'iB0', 'iB1', 'CorrectionFactor', 'SondeNr', 'InterfaceNr','DateTime','Datenf']

dfmeta = pd.read_csv("/home/poyraden/Analysis/Uccle_Deconvolution/Files/ECCprop.txt", sep = r"\t" , engine="python",skiprows=1, names=columnMeta)
dfmeta['DateTime'] = dfmeta['mDate'].apply(lambda x: pd.to_datetime(str(x), format='%Y%m%d%H'))
dfmeta['Datenf'] = dfmeta['DateTime'].apply(lambda x: x.strftime('%Y%m%d'))



for filename in allFiles:
#for filename in file_test:
    file = open(filename,'r')
    date_tmp = filename.split('/')[8].split('raw.')[0]
    # print(date_tmp)
    date = datetime.strptime(date_tmp, '%y%m%d%H%M')
    datef = date.strftime('%Y%m%d')
    # print(datef)
    # print(date.year, date.month, date.day, date.hour, date.minute)
    year = date.year
    month = date.month
    day = date.day
    hour = date.hour
    # print(date_tmp.strftime('%y%m%d%h'))
## yymmddhh
    # file.readline()

    df = pd.read_csv(filename, sep = "\s *", engine="python", skiprows=1, names=columnStr)

    df = df.join(pd.DataFrame(
        [[datef]],
        index=df.index,
        # columns=['Date', 'Year', 'Month', 'Day', 'Hour']
        columns = ['Date']))

    ind = df.first_valid_index()
    select_indices = list(np.where(dfmeta["Datenf"] == df.at[ind,'Date']))[0]
    common = [i for i in select_indices if i in select_indices]
    index_common = common[0]

    list_md = dfmeta.iloc[index_common, :].tolist()

    df = df.join(pd.DataFrame(
            [list_md],
            index = df.index,
            columns=columnMeta
        ))

    # print(list(df))

    df = df.drop(['Winddir', 'Windv','mDate',  'DateTime', 'Datenf'], axis = 1)

# df for all uccle data
    list_data.append(df)

# Merging all the data files to df
dfn = pd.concat(list_data,ignore_index=True)

# dfn.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleDataRaw.csv")
dfn.to_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleDataRaw.h5', key='df', mode='w')
dfmeta.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/ECCmetadata.csv")


# ### read DQA data
#
#
# allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/bofur/O3S-DQA/*dat")
#
# print('one')
#
# list_data = []
#
# columnString = "Time Height P T U Winddir Windv Tbox TrueTbox Icor x O3cor y"
# columnStr = columnString.split(" ")
#
# for filename in allFiles:
# #for filename in file_test:
#     file = open(filename,'r')
#     date_tmp = filename.split('/')[9].split('.dat')[0]
#     # print(date_tmp)
#     try:
#         date = datetime.strptime(date_tmp, '%Y%m%d%H%M')
#     except ValueError:
#         date = datetime.strptime(date_tmp, '%y%m%d%H%M')
#
#     datef = date.strftime('%Y%m%d')
#     # print(datef)
#     # print(date.year, date.month, date.day, date.hour, date.minute)
#     year = date.year
#     month = date.month
#     day = date.day
#     hour = date.hour
#
#     df = pd.read_csv(filename, sep = "\s *", engine="python", skiprows=1, names=columnStr)
#
#     df = df.join(pd.DataFrame(
#         [[datef, year, month, day, hour]],
#         index=df.index,
#         columns=['Date', 'Year', 'Month', 'Day', 'Hour']
#     ))
#
#     list_data.append(df)
# #
# # # Merging all the data files to df
# dfn = pd.concat(list_data,ignore_index=True)
# #
# dfn.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleDataDQA.csv")
# dfn.to_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleDataDQA.h5', key='df', mode='w')

