import pandas as pd
import numpy as np
import re
from re import search
import glob
from datetime import datetime

from Homogenisation_Functions import po3tocurrent, absorption_efficiency, stoichemtry_conversion, conversion_efficiency, background_correction, \
    pumptemp_corr, pf_efficiencycorrection, currenttopo3, pf_groundcorrection

station = 'Sodankyl'
k = 273.15

allFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/Current/so06*rawcurrent.csv"))


list_data = []
size = len(allFiles)

datelist = [0]*size
j = 0
for filename in allFiles:

    file = open(filename, 'r')
    date_tmp = filename.split('/')[9].split('_')[0][2:8]

    print(filename)

    date = datetime.strptime(date_tmp, '%y%m%d')

    datef = date.strftime('%Y%m%d')
    datestr = str(datef)
    datelist[j] = datestr
    if (j > 0) and (j < (size - 1)):
        if (datelist[j] == datelist[j - 1]):
            datestr = str(datef) + "_2nd"
            print(datestr)

    j = j+1

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

    # print(list(df))
    if(df.at[df.first_valid_index(),'SensorType'] == 'DMT-Z') and (df.at[df.first_valid_index(),'SolutionConcentration'] == 10):
        print(df.at[df.first_valid_index(),'SensorType'], df.at[df.first_valid_index(),'SolutionConcentration'])
        print(datef)



    df['alpha_o3'], df['unc_alpha_o3'] =  absorption_efficiency(df, 'Pair', 'SolutionVolume')
    df['stoich'], df['unc_stoich'] = stoichemtry_conversion(df, 'Pair', df.at[df.first_valid_index(),'SensorType'],
                                                            df.at[df.first_valid_index(),'SolutionConcentration'], 'ENSCI05')
    df['eta_c'], df['unc_eta_c'] = conversion_efficiency(df, 'alpha_o3', 'unc_alpha_o3', 'stoich', 'unc_stoich')

    df.to_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/DQA/' + datestr + "_dqa.csv")



