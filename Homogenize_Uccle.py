import csv
import numpy as np
from io import StringIO
from woudc_extcsv import load, WOUDCExtCSVReaderError
import pandas as pd
import glob
from Homogenisation_Functions import po3tocurrent, conversion_absorption, conversion_efficiency, background_correction, \
    pumptemp_corr, pumpflow_correction, currenttopo3, po3tocurrent

# df = pd.read_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleDataRaw.csv', low_memory=False)
df = pd.read_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleDataRaw.h5')
# df = df[df.Datenf > 20180101]

# datelist = np.array(df.Date.tolist())

# columnString = "Time Height P T U Winddir Windv Tbox TrueTbox I PF O3 uncO3"
# columnStr = columnString.split(" ")


# print(list(df))
#
# ##input variables for hom.
# df['Tpump'] = df['Tbox'] + 273
# df['unc_Tpump'] = 1
# df['Phip'] = 100 / df['PF']
# df['unc_Phip'] = 0
# df['Eta'] = 1
#
# ## corrected variables
# df['iBc'], df['unc_iBc'] = background_correction(df, 'iB0', 'iBc', 'unc_iBc')
# df['Tpumpc'], df['unc_Tpumpc'] = pumptemp_corr(df, 'internalpump', 'Tpump', 'unc_Tpump', 'P', 'Tpumpc', 'unc_Tpumpc' )
# df['Phipc'], df['unc_Phipc'] = pumpflow_correction(df, 'P', 'Phip', 'unc_Phip', 'komhyr_95', 'Phipc', 'unc_Phipc')
# df['O3c'] = currenttopo3(df, 'I', 'Tpumpc', 'iBc', 'Eta', 'Phipc', False, 'O3c')
# df['Ic'] = po3tocurrent(df, 'O3', 'Tpumpc', 'iBc', 'Eta', 'Phipc', False, 'Ic')
#
#
# df = df.drop(['U', 'Height', 'O3', 'Tbox', 'I',  'mRadioSondeNr', 'PF', 'iB0', 'iB1', 'CorrectionFactor', 'SondeNr',
#               'Tpump', 'unc_Tpump', 'Phip', 'unc_Phip','InterfaceNr', 'deltat', 'unc_deltat', 'deltat_ppi', 'unc_deltat_ppi',
#               'unc_phipcor'], axis = 1)
#
# print(list(df))

# df.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/DF_Uccle_Homogonized.csv")
# df.to_hdf('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/DF_Uccle_Homogonized_2.h5', key='df', mode='w')
#


# po3tocurrent(df, o3, pair,  Tpump, ib, etac, phip, pumpcorrectiontag, boolcorrection)


# list_data = []
# dft = {}


# for d in range(len(datelist)):
#     df = df[df.Date == datelist[d]]
#     df = df.reset_index()
#
#     ##input variables for hom.
#     df['Tpump'] = df['Tbox'] + 273
#     df['unc_Tpump'] = 1
#     df['phip'] = 100 / df['PF']
#     df['unc_phip'] = 0
#     df['eta'] = 1
#
#     ## corrected variables
#     df['ibc'], df['unc_ibc'] = background_correction(df, 'iB0')
#
#     df['Tpumpc'], df['unc_Tpumpc'] = pumptemp_corr(df, 'internalpump', 'Tpump', 'unc_Tpump', 'P')
#     df['phipc'], df['unc_phipc'] = pumpflow_correction(df, 'P', 'phip', 'unc_phip', 'komhyr_95')
#
#     df['po3c'] = currenttopo3(df, 'I', 'Tpumpc', 'ibc', 'eta', 'phipc', False)
#     df['ic'] = po3tocurrent(df, 'po3c', 'Tpumpc', 'ibc', 'eta', 'phipc', False)
#
#     list_data.append(df)
#     #  end of the allfiles loop    #
#
# # Merging all the data files to df
# dfn = pd.concat(list_data, ignore_index=True)
#
# # po3tocurrent(df, o3, pair,  Tpump, ib, etac, phip, pumpcorrectiontag, boolcorrection)
# 
# print('end list', list(dfn))

