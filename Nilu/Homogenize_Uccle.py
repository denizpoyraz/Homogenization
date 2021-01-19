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

allFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Uccle/Current/*rawcurrent.csv"))


list_data = []

for filename in allFiles:
    file = open(filename, 'r')
    date_tmp = filename.split('/')[9].split('_')[0].split("uc")[1]
    if (date_tmp == "080825") | (date_tmp == "080702") | (date_tmp == "080704") | (date_tmp == "190214"): continue

    # date = datetime.strptime(date_tmp, '%y%m%d%H%M')
    date = datetime.strptime(date_tmp, '%y%m%d')

    datef = date.strftime('%Y%m%d')
    print(datef)

    df = pd.read_csv(filename)
    # print(list(df))
    # , sep="\s *", engine="python", skiprows=2, names=columnStr)

    # to deal with data that is not complete
    if (len(df) < 300):
        #efile.write('length of df ' + datef  + '\n')
        continue

    df['Date'] = datef
    df['Datedt'] = pd.to_datetime(df['Date'], format='%Y%m%d').dt.date


    ##input variables for hom.
    df['Tpump'] = df['Tbox']
    df['Phip'] = 100 / df['PF']
    df['Eta'] = 1
    df['P'] = df['Pair']

    df['unc_Phip'] = 0
    df['unc_Tpump'] = 1

    Tlab = 20 + k
    ## calculation of I for the data before 2007
    # if datef < '20070101':
    #     df['I'] = (df['O3'] * 1000) / (0.43085 * (df['Tbox']) * df['PF']) + np.abs(df['iB0'])

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
    try:
        df['Tpump_cor'], df['dTpump_cor'] = pumptemp_corr(df, 'internalpump', 'Tpump', 'unc_Tpump', 'P', 'Tpump_cor',
                                                        'dTpump_cor')
    except ValueError:
        print('ValueError', datef)

    df['iBc'], df['unc_iB0'] = background_correction(df, df, 'iB0', 'iBc', 'unc_iB0')
    df['O3c'] = currenttopo3(df, 'I', 'Tpump_cor', 'iBc', 'Eta', 'Phip_cor', False, 'O3c')

    ## uncertainities
    df['dI'] = 0
    df.loc[df.I < 1,'dI'] = 0.01
    df.loc[df.I >= 1, 'dI'] = 0.01 * df.loc[df.I > 1, 'I']
    df['dIall'] = (df['dI']**2 + df['unc_iB0']**2)/(df['I'] - df['iB0'])**2
    # unc_eta = (DeltaEtac/Etac)**2
    df['dEta'] = 0.0013
    # final uncertainity on O3
    df['dO3'] = np.sqrt(df['dIall'] + df['dEta'] + df['dPhi_cor'] + df['dTpump_cor'])

    df.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Uccle/DQA/All/" + datef + "_all.csv")

    df['PF'] = df['Phip_cor']
    df['Tbox'] = df['Tpump_cor']
    df['iB0'] = df['iBc']
    df['O3'] = df['O3c']


    df = df.drop(['Tpump', 'unc_Tpump', 'Phip', 'unc_Phip', 'Eta', 'dPhip_meas', 'Phip_ground', 'unc_phix', 'unc_phipgr', 'dPhip_gr', 'PCF',
                  'dPCF', 'Phip_cor', 'dPhi_cor', 'deltat', 'unc_deltat', 'deltat_ppi', 'unc_deltat_ppi', 'Tpump_cor',
                  'dTpump_cor', 'iBc', 'unc_iB0', 'O3c', 'dIall', 'dEta'], axis=1)



    df.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Uccle/DQA/Corrected/" + datef + "_dqa.csv")
    list_data.append(df)

#efile.close()

# Merging all the data files to df
dfn = pd.concat(list_data, ignore_index=True)

dfn.to_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Uccle/UccleData_DQA.h5', key='df', mode='w')

