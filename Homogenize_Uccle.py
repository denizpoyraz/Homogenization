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

from Homogenisation_Functions import po3tocurrent, conversion_absorption, conversion_efficiency, background_correction, \
    pumptemp_corr, pf_efficiencycorrection, currenttopo3, pf_groundcorrection

station = 'Uccle'

##Uccle metadata
columnMeta = ['mDate', 'mRadioSondeNr', 'PF', 'iB0', 'iB1', 'CorrectionFactor', 'SondeNr', 'InterfaceNr', 'DateTime',
              'Datenf']

dfmeta = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/" + station + "/one_day/ECCprop.txt", sep=r"\t", engine="python",
                     skiprows=1, names=columnMeta)
dfmeta['DateTime'] = dfmeta['mDate'].apply(lambda x: pd.to_datetime(str(x), format='%Y%m%d%H'))
dfmeta['Datenf'] = dfmeta['DateTime'].apply(lambda x: x.strftime('%Y%m%d'))


allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/" + station + "/raw/*raw.txt")

columnString1 = "Time P T U Height O3 Tbox I Winddir Windv"
columnString2 = "Time P T U Height O3 Tbox I V Winddir Windv Lat Lon GPSHeightMSL Dewp AscRate"
columnString3 = "Time P T U Height O3 Tbox I V PumpCurrent Winddir Windv Lat Lon GPSHeightMSL Dewp AscRate"

# i) one for data before 15/04/2016
# ii) one for data between 10/06/2016 and 17/09/2016
# iii) one for data after 17/09/2016

# columnStr = columnString.split(" ")

k = 273.15

list_data = []


for filename in allFiles:
    file = open(filename, 'r')
    date_tmp = filename.split('/')[8].split('raw.')[0]
    date = datetime.strptime(date_tmp, '%y%m%d%H%M')
    datef = date.strftime('%Y%m%d')

    if datef < '20160416':
        columnStr = columnString1.split(" ")
    # if (datef >= '20160416') & (datef < '20160610'):
    #     print(datef)
    if (datef >= '20160610') & (datef < '20160917'):
        columnStr = columnString2.split(" ")
    if datef >= '20160917':
        columnStr = columnString3.split(" ")

    df = pd.read_csv(filename, sep="\s *", engine="python", skiprows=1, names=columnStr)

    df['Date'] = datef

    ind = df.first_valid_index()
    select_indices = list(np.where(dfmeta["Datenf"] == df.at[ind, 'Date']))[0]
    common = [i for i in select_indices if i in select_indices]
    mindex = common[0]

    df['PF'] = dfmeta.loc[mindex, 'PF']
    df['iB0'] = dfmeta.loc[mindex, 'iB0']

    ##input variables for hom.
    df['Tpump'] = df['Tbox'] + k
    df['unc_Tpump'] = 1
    df['Phip'] = 100 / df['PF']
    df['unc_Phip'] = 0
    df['Eta'] = 1
    Tlab = 20 + k

    ## DQA corrections
    df['Phip_eff'], df['unc_eff'] = pf_efficiencycorrection(df, 'P', 'Phip', 'unc_Phip', 'komhyr_95', 'polyfit',
                                                            'Phip_eff', 'unc_eff')
    df['Phip_cor'], df['unc_phipcor'] = pf_groundcorrection(df, 'Phip_eff', 'unc_eff', Tlab, 'unc_Phip', 'unc_Phip',
                                                            'Phip_cor', 'unc_phipcor')
    # pf_groundcorrection(df, phim, unc_phim, tlab, plab, rhlab, out, unc_out)
    df['Tpump_cor'], df['unc_tpumpcor'] = pumptemp_corr(df, 'internalpump', 'Tpump', 'unc_Tpump', 'P', 'Tpump_cor',
                                                        'unc_tpumpcor')
    df['iBc'], df['unc_iBc'] = background_correction(df, 'iB0', 'iBc', 'unc_iBc')
    df['O3c'] = currenttopo3(df, 'I', 'Tpump_cor', 'iBc', 'Eta', 'Phip_cor', False, 'O3c')

    df.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/DQA/All/" + datef + "_all.csv")

    df['PF'] = df['Phip_cor']
    df['Tbox'] = df['Tpump_cor']
    df['iB0'] = df['iBc']
    df['O3'] = df['O3c']

    df = df.drop(['Tpump', 'unc_Tpump', 'Phip', 'unc_Phip', 'Eta', 'PCF', 'Phip_eff', 'unc_phipcor', 'unc_eff',
                  'Phip_cor', 'deltat', 'unc_deltat', 'deltat_ppi', 'unc_deltat_ppi', 'Tpump_cor', 'unc_tpumpcor',
                  'iBc', 'unc_iBc', 'O3c'], axis=1)

    df.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/DQA/Corrected/" + datef + "_dqa.csv")

    # print(list(df))

    ## uncertanities need to implemented

    list_data.append(df)

# Merging all the data files to df
dfn = pd.concat(list_data, ignore_index=True)

dfn.to_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleData_DQA.h5', key='df', mode='w')
