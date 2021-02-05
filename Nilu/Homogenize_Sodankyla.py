import pandas as pd
import numpy as np
import re
from re import search
import glob
from datetime import datetime

from Homogenisation_Functions import po3tocurrent, absorption_efficiency, stoichemtry_conversion, conversion_efficiency, background_correction, \
    pumptemp_corr, currenttopo3, pf_groundcorrection, organize_metadata, calculate_cph, pumpflow_efficiency
# pf_efficiencycorrection

station = 'Sodankyl'
k = 273.15

dfmeta = pd.read_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/All_metedata.hdf')

dfmeta = organize_metadata(dfmeta)

#part to calculate cph and its error
dfmeta = calculate_cph(dfmeta)
dfmeta['unc_cph'] = dfmeta['cph'].std()
dfmeta['unc_cpl'] = dfmeta['cpl'].std()

print('cph std', dfmeta['cph'].std(), 'cpl std', dfmeta['cpl'].std())
# print()
# cph_average = (dfmeta['cph'].max() + dfmeta['cph'].min())/2
# cph_unc = (dfmeta['cph'].max() - dfmeta['cph'].min())/2
#
# print(np.nanmean(dfmeta['cph']), np.nanmedian(dfmeta['cph']), dfmeta.cph.std(),   cph_average, cph_unc)

allFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/Current/*rawcurrent.csv"))


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
            # print(datestr)
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

    df['unc_Phip'] = 0.02
    df['unc_Tpump'] = 1
    df['unc_cph'] = dfmeta.at[dfmeta.first_valid_index(),'unc_cph']
    df['unc_cpl'] = dfmeta.at[dfmeta.first_valid_index(),'unc_cpl']

    # print(list(df))
    # if(df.at[df.first_valid_index(),'SensorType'] == 'DMT-Z') and (df.at[df.first_valid_index(),'SolutionConcentration'] == 10):
    #     print(df.at[df.first_valid_index(),'SensorType'], df.at[df.first_valid_index(),'SolutionConcentration'])
    #     print(datef)


    ##conversion efficiency
    df['alpha_o3'], df['unc_alpha_o3'] =  absorption_efficiency(df, 'Pair', 'SolutionVolume')
    df['stoich'], df['unc_stoich'] = stoichemtry_conversion(df, 'Pair', df.at[df.first_valid_index(),'SensorType'],
                                                            df.at[df.first_valid_index(),'SolutionConcentration'], 'ENSCI05')
    df['eta_c'], df['unc_eta_c'] = conversion_efficiency(df, 'alpha_o3', 'unc_alpha_o3', 'stoich', 'unc_stoich')
    # background correction
    df['iBc'], df['unc_iBc'] = background_correction(df, df, 'iB2')
    # pump temperature correction
    # try:
    #     if (df.at[df.first_valid_index(), 'PumpTempLoc'] != 'Pump hole'):
    #         print(df.at[df.first_valid_index(), 'PumpTempLoc'], df.at[df.first_valid_index(), 'SerialECC'], df.at[df.first_valid_index(), 'SensorType'])
    # except KeyError:
    #     print('KeyError', datef)
    # if (df.at[df.first_valid_index(),'PumpTempLoc'] == 'Pump hole') | (df.at[df.first_valid_index(),'PumpTempLoc'] == 'Pump hole'):
    #     boxlocation = 'internalpump'
    df['Tpump_cor'], df['unc_Tpump_cor'] = pumptemp_corr(df, 'internalpump', 'Tpump', 'unc_Tpump', 'P')
    #pump flow corrections
    # ground correction
    df['Phip_ground'], df['unc_Phip_ground'] = pf_groundcorrection(df, 'Phip', 'unc_Phip', 'TLab', 'Pground', 'ULab')
    #efficiency correction
    df['Cpf'], df['unc_Cpf'] = pumpflow_efficiency(df, 'P', 'komhyr_95', 'table_interpolate')

    df.to_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/DQA/' + datestr + "_dqa.csv")



