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
k = 273.15


##Uccle metadata
columnMeta = ['mDate', 'mRadioSondeNr', 'PF', 'iB0', 'iB1', 'CorrectionFactor', 'SondeNr', 'InterfaceNr', 'DateTime',
              'Datenf']

dfmeta = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/" + station + "/one_day/ECCprop.txt", sep=r"\t", engine="python",
                     skiprows=1, names=columnMeta)
dfmeta['DateTime'] = dfmeta['mDate'].apply(lambda x: pd.to_datetime(str(x), format='%Y%m%d%H'))
dfmeta['Datenf'] = dfmeta['DateTime'].apply(lambda x: x.strftime('%Y%m%d'))
# special data cleaning for metadata
dfmeta = dfmeta[dfmeta.Datenf >= '19970101']  # only for dates after 1997
dfmeta = dfmeta[dfmeta.iB0 > -1] # clean iB) values which are not realistic


allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/" + station + "/raw/970*")

columnString0 = "Time Height P T U Tbox O3 Winddir Windv"
columnString1 = "Time P T U Height O3 Tbox I Winddir Windv"
columnString2 = "Time P T U Height O3 Tbox I V Winddir Windv Lat Lon GPSHeightMSL Dewp AscRate"
columnString3 = "Time P T U Height O3 Tbox I V PumpCurrent Winddir Windv Lat Lon GPSHeightMSL Dewp AscRate"

# 0) one for data before 2007
# i) one for data before 15/04/2016
# ii) one for data between 10/06/2016 and 17/09/2016
# iii) one for data after 17/09/2016

list_data = []

for filename in allFiles:
    file = open(filename, 'r')
    date_tmp = filename.split('/')[8].split('raw.')[0]
    date = datetime.strptime(date_tmp, '%y%m%d%H%M')
    datef = date.strftime('%Y%m%d')
    print(filename, datef)

    if datef < '20070101':
        columnStr = columnString0.split(" ")
    if (datef > '20061231') & (datef < '20160416'):
        columnStr = columnString1.split(" ")
    # if (datef >= '20160416') & (datef < '20160610'):
    if (datef >= '20160610') & (datef < '20160917'):
        columnStr = columnString2.split(" ")
    if datef >= '20160917':
        columnStr = columnString3.split(" ")

    df = pd.read_csv(filename, sep="\s *", engine="python", skiprows=3, names=columnStr)

    df['Date'] = datef
    df['Datedt'] = pd.to_datetime(df['Date'], format='%Y%m%d').dt.date
    # print(df.at[df.first_valid_index(), 'Date'], df.at[df.first_valid_index(), 'Datedt'] )

    ind = df.first_valid_index()
    select_indices = list(np.where(dfmeta["Datenf"] == df.at[ind, 'Date']))[0]
    common = [i for i in select_indices if i in select_indices]
    mindex = common[0]
    print(mindex, type(mindex))
    df['PF'] = dfmeta.at[mindex, 'PF']
    df['iB0'] = dfmeta.loc[mindex, 'iB0']

    ##input variables for hom.
    df['Tpump'] = df['Tbox'] + k
    df['unc_Tpump'] = 1
    df['Phip'] = 100 / df['PF']
    df['unc_Phip'] = 0
    df['Eta'] = 1
    Tlab = 20 + k
    ## calculation of I for the data before 2007
    if datef < '20070101':
        df['I'] = (df['O3'] * 1000) / (0.43085 * (df['Tbox'] + k) * df['PF']) + np.abs(df['iB0'])

    #uncertainities
    #dPhip_meas = (deltaPhip_measured/Phip_measured)**2
    df['dPhip_meas'] = 0.0004

    ## DQA corrections
    # first ground correction then efficiency
    df['Phip_ground'], df['unc_phix'] = pf_groundcorrection(df, 'Phip', 'dPhip_meas', Tlab, 'unc_Phip', 'unc_Phip',
                                                            'Phip_ground', 'unc_phix')
    df['unc_phipgr'] = 0.004
    df['dPhip_gr'] = 0.02

    df['Phip_cor'], df['dPhi_cor'] = pf_efficiencycorrection(df, 'P', 'Phip_ground', 'dPhip_gr', 'komhyr_95', 'polyfit',
                                                            'Phip_cor', 'dPhi_cor')

    df['Tpump_cor'], df['dTpump_cor'] = pumptemp_corr(df, 'internalpump', 'Tpump', 'unc_Tpump', 'P', 'Tpump_cor',
                                                        'dTpump_cor')
    df['iBc'], df['unc_iB0'] = background_correction(df, dfmeta, 'iB0', 'iBc', 'unc_iB0')
    df['O3c'] = currenttopo3(df, 'I', 'Tpump_cor', 'iBc', 'Eta', 'Phip_cor', False, 'O3c')

    ## uncertainities
    df['dI'] = 0
    df.loc[df.I < 1,'dI'] = 0.01
    df.loc[df.I >= 1, 'dI'] = 0.01 * df.loc[df.I > 1, 'I']
    df['dIall'] = (df['dI']**2 + df['unc_iB0']**2)/(df['I'] - df['iB0'])**2
    # unc_eta = (DeltaEtac/Etac)**2
    df['dEta'] = 0.0013
    # unc_phipground = (DeltaPhipGround/PhipGround)**2
    # df['dPhig'] = 0.000400
    # # dPhip = (DeltaPhip / Phip) ** 2
    # df['dPhip'] = df['dPhig'] + df['unc_eff']

    df['dO3'] = np.sqrt(df['dIall'] + df['dEta'] + df['dPhi_cor'] + df['dTpump_cor'])

    df.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/DQA/All/" + datef + "_all.csv")

    df['PF'] = df['Phip_cor']
    df['Tbox'] = df['Tpump_cor']
    df['iB0'] = df['iBc']
    df['O3'] = df['O3c']

    # print(list(df))

    df = df.drop(['Tpump', 'unc_Tpump', 'Phip', 'unc_Phip', 'Eta', 'dPhip_meas', 'Phip_ground', 'unc_phix', 'unc_phipgr', 'dPhip_gr', 'PCF',
                  'dPCF', 'Phip_cor', 'dPhi_cor', 'deltat', 'unc_deltat', 'deltat_ppi', 'unc_deltat_ppi', 'Tpump_cor', 'dTpump_cor', 'iBc', 'unc_iB0', 'O3c', 'dIall', 'dEta'], axis=1)

    df.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/DQA/Corrected/" + datef + "_dqa.csv")

    # print(list(df))

    ## uncertanities need to implemented

    list_data.append(df)

# Merging all the data files to df
dfn = pd.concat(list_data, ignore_index=True)

dfn.to_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleData_DQA.h5', key='df', mode='w')

dfmeta.to_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleMetaData.csv')