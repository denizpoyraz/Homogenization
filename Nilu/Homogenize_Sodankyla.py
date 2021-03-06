import pandas as pd
import numpy as np
import re
from re import search
import glob
from datetime import datetime
import time

from Nilu.Homogenisation_Functions import po3tocurrent, absorption_efficiency, stoichmetry_conversion, conversion_efficiency, \
    background_correction,pumptemp_corr, currenttopo3, pf_groundcorrection, organize_metadata, calculate_cph, pumpflow_efficiency, \
    return_phipcor, RS_pressurecorrection

# pf_efficiencycorrection

t0 = time.time()
print(t0)

station = 'Sodankyl'
k = 273.15

dfmeta = pd.read_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/All_metedata.hdf')

dfmeta = organize_metadata(dfmeta)

# part to calculate cph and its error
dfmeta = calculate_cph(dfmeta)
dfmeta['unc_cph'] = dfmeta['cph'].std()
dfmeta['unc_cpl'] = dfmeta['cpl'].std()

print('cph std', dfmeta['cph'].std(), 'cpl std', dfmeta['cpl'].std())
# print()
# cph_average = (dfmeta['cph'].max() + dfmeta['cph'].min())/2
# cph_unc = (dfmeta['cph'].max() - dfmeta['cph'].min())/2
#
# print(np.nanmean(dfmeta['cph']), np.nanmedian(dfmeta['cph']), dfmeta.cph.std(),   cph_average, cph_unc)

allFiles = sorted(
    glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/Current/*rawcurrent.hdf"))

list_data = []
list_datall = []
size = len(allFiles)

datelist = [0] * size
j = 0

bool_rscorrection = True


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
    j = j + 1

    df = pd.read_hdf(filename)
    # print(list(df))
    # , sep="\s *", engine="python", skiprows=2, names=columnStr)

    # to deal with data that is not complete
    if (len(df) < 300):
        # efile.write('length of df ' + datef  + '\n')
        continue

    df['Date'] = datef
    df['Datedt'] = pd.to_datetime(df['Date'], format='%Y%m%d').dt.date

    # input variables for hom.
    df['Tpump'] = df['Tbox']
    df['Phip'] = 100 / df['PF']
    df['Eta'] = 1

    df['unc_Phip'] = 0.02
    df['unc_Tpump'] = 1
    df['unc_cph'] = dfmeta.at[dfmeta.first_valid_index(), 'unc_cph']
    df['unc_cpl'] = dfmeta.at[dfmeta.first_valid_index(), 'unc_cpl']

    #                                   #
    #      radiosonde RS80 correction   #
    #                                   #
    # if bool_rscorrection == 'True':
    try: rsmodel = df.at[df.first_valid_index(), 'RadiosondeModel']
    except KeyError: rsmodel = 'RS92'
    df['Crs'], df['unc_Crs'] = RS_pressurecorrection(df, 'Height', rsmodel)
    df['Pair'] = df['Pair'] - df['Crs']


    #                                   #
    #      conversion efficiency        #
    #                                   #
    df['alpha_o3'], df['unc_alpha_o3'] = absorption_efficiency(df, 'Pair', 'SolutionVolume')
    df['stoich'], df['unc_stoich'] = stoichmetry_conversion(df, 'Pair', df.at[df.first_valid_index(), 'SensorType'],
                                                            df.at[df.first_valid_index(), 'SolutionConcentration'], 'ENSCI05')
    df['eta_c'], df['unc_eta_c'] = conversion_efficiency(df, 'alpha_o3', 'unc_alpha_o3', 'stoich', 'unc_stoich')

    #                                   #
    #       background correction       #
    #                                   #
    df['iBc'], df['unc_iBc'] = background_correction(df, dfmeta, 'iB2')
    #                                   #
    #       pump temperature correction       #
    #                                   #
    df['Tpump_cor'], df['unc_Tpump_cor'] = pumptemp_corr(df, 'internalpump', 'Tpump', 'unc_Tpump', 'Pair')

    #                                   #
    #      pump flow corrections        #
    #                                   #
    # ground correction

    df['Phip_ground'], df['unc_Phip_ground'] = pf_groundcorrection(df, 'Phip', 'unc_Phip', 'TLab', 'Pground', 'ULab')

    # efficiency correction

    pumpflowtable = ''
    if df.at[df.first_valid_index(), 'SensorType'] == 'SPC': pumpflowtable = 'komhyr_86'
    if df.at[df.first_valid_index(), 'SensorType'] == 'DMT-Z': pumpflowtable = 'komhyr_95'
    df['Cpf'], df['unc_Cpf'] = pumpflow_efficiency(df, 'Pair', pumpflowtable, 'table_interpolate')
    df['Phip_cor'], df['unc_Phip_cor'] = return_phipcor(df, 'Phip_ground', 'unc_Phip_ground', 'Cpf', 'unc_Cpf')
    df['Phip_PF'] = df['Phip'] / df['Cpf']

    # all corrections
    df['O3c'] = currenttopo3(df, 'I', 'Tpump_cor', 'iBc', 'eta_c', 'Phip_cor', False)

    # one correction only
    # df['O3c'] = currenttopo3(df, 'I', 'Tpump_cor', 'iBc', 'eta_c', 'Phip_PF', False)
    # df['O3st'] = currenttopo3(df, 'I', 'Tpump', 'iB2', 'Eta', 'Phip', False)


    # uncertainities
    df['dI'] = 0
    df.loc[df.I < 1, 'dI'] = 0.01
    df.loc[df.I >= 1, 'dI'] = 0.01 * df.loc[df.I > 1, 'I']
    df['dIall'] = (df['dI'] ** 2 + df['unc_iBc'] ** 2) / (df['I'] - df['iB0']) ** 2
    # unc_eta = (DeltaEtac/Etac)**2
    df['dEta'] = (df['unc_eta_c'] / df['unc_eta_c']) ** 2
    df['dPhi_cor'] = (df['unc_Phip_cor'] / df['Phip_cor']) ** 2
    df['dTpump_cor'] = (df['unc_Tpump_cor'] / df['Tpump_cor']) ** 2
    if bool_rscorrection: df['dPrs'] = (df['unc_Crs']/df['Crs'])**2
    # final uncertainity on O3
    df['dO3'] = np.sqrt(df['dIall'] + df['dEta'] + df['dPhi_cor'] + df['dTpump_cor'])
    if bool_rscorrection: df['dO3'] = np.sqrt(df['dIall'] + df['dEta'] + df['dPhi_cor'] + df['dTpump_cor'] + df['dPrs'])

    df.to_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/DQA/All/' + datestr + "_all_dqa_rs92.csv")
    df.to_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/DQA/All/' + datestr + "_all_dqa_rs92.hdf", key = 'df')

    # list_data.append(df)


    df['PF'] = df['Phip_cor']
    df['Tbox'] = df['Tpump_cor']
    df['iB0'] = df['iBc']
    df['O3'] = df['O3c']

    df = df.drop(
        ['SolutionVolume', 'SolutionConcentration', 'Pground', 'TLab', 'ULab', 'PumpTable', 'SerialECC', 'SensorType',
         'Cef', 'ibg', 'Pcor', 'Datedt', 'Tpump', 'Phip', 'Eta', 'unc_Phip', 'unc_Tpump', 'unc_cph', 'unc_cpl',
         'unc_alpha_o3', 'alpha_o3', 'stoich', 'unc_stoich', 'eta_c', 'unc_eta', 'unc_eta_c', 'iBc', 'unc_iBc', 'Tpump_cor',
         'unc_Tpump_cor','deltat', 'unc_deltat', 'deltat_ppi', 'unc_deltat_ppi', 'x', 'psaturated', 'cph', 'tlabK', 'cPL',
         'Phip_ground', 'Cef', 'ibg', 'Pcor', 'unc_Phip_ground', 'Cpf', 'unc_Cpf', 'Phip_cor', 'unc_Phip_cor', 'O3c',
         'dIall', 'dEta', 'dPhi_cor', 'dTpump_cor', 'Crs', 'unc_Crs'], axis=1)
    # 'Crs', 'unc_Crs',

    # print(list(df))

    df.to_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/DQA/' + datestr + '_dqa_rs92.h5',
              key='df', mode='w')
    # df.to_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/DQA/' + datestr + "_corrected_dqa.csv")

#
# dff = pd.concat(list_data,ignore_index=True)
# hdfall = '/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/DQA/' + "Sodankyl_All_data.onlyBkg.hdf"
# dff.to_hdf(hdfall, key = 'df')

t1 = time.time()

print(t1)
print(t1-t0)