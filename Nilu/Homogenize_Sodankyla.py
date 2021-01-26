import pandas as pd
import numpy as np
import re
from re import search
import glob
from datetime import datetime

from Homogenisation_Functions import po3tocurrent, absorption_efficiency, conversion_efficiency, background_correction, \
    pumptemp_corr, pf_efficiencycorrection, currenttopo3, pf_groundcorrection

station = 'Sodankyl'
k = 273.15

allFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/Current/*rawcurrent.csv"))


list_data = []

for filename in allFiles:

    file = open(filename, 'r')
    date_tmp = filename.split('/')[9].split('_')[0][2:8]

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

    print(list(df))

    df['alpha_o3'], df['unc_alpha_o3'] =  absorption_efficiency(df, 'Pair', 'SolutionVolume')
    ## stoichemtry mostly ENSCI 0.5, therefore tune the other sonde stype (if not ensci 0.5) to ensci 0.5


