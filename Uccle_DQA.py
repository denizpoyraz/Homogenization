import csv
import numpy as np
from io import StringIO
from woudc_extcsv import load, WOUDCExtCSVReaderError
import pandas as pd
import glob
from Homogenisation_Functions import po3tocurrent, conversion_absorption, conversion_efficiency, background_correction, \
    pumptemp_corr, pf_efficiencycorrection, currenttopo3, pf_groundcorrection

columnString = "Time P T U Height O3 Tbox I V PumpCurrent Winddir Windv Lat Lon GPSHeightMSL Dewp AscRate"
columnStr = columnString.split(" ")

df = pd.read_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/one_day/2011231129raw.txt', sep="\s *",
                 engine="python", skiprows=1, names=columnStr)

k = 273.15

df['PCF'] = 2.17322861-3.686021555*np.log10(df.P)+5.105113826*(np.log10(df.P))**2-3.741595297*(np.log10(df.P))**3+1.496863681*(np.log10(df.P))**4-\
      0.3086952232*(np.log10(df.P))**5+0.02569158956*(np.log10(df.P))**6

##input variables for hom.
df['Tpump'] = df['Tbox'] + k
df['unc_Tpump'] = 1
df['PF'] = 30.04
df['Phip'] = 100 / df['PF']
df['unc_Phip'] = 0

df['Phip_kom'] = df['Phip']/df['PCF']
df['Phip_komcpl'] = df['Phip'] * (1 + 2/293.15) / df['PCF']
# df['Phip_cpl'] = 100 / df['PF'] * (1 + 2 / 293)
# df['Phipc'] = 100 * df['PCF'] / df['PF'] * (1 + 2 / 293)

# df['Phip_komcpl'] = np.round(df['Phip_komcpl'],4)

df['Tlab'] = 20 + k

df['pf_kom'], df['unc_kom'] = pf_efficiencycorrection(df, 'P', 'Phip', 'unc_Phip', 'komhyr_95', 'pf_kom', 'unc_kom')
df['pfg'], df['unc_pfg'] = pf_groundcorrection(df, 'pf_kom', 'unc_kom', 20+k, 'unc_Phip', 'unc_Phip', 'pfg', 'unc_pfg')

df['unc_Phip'] = 0
df['Eta'] = 1
df['iB0'] = 0.004

## corrected variables
df['iBc'], df['unc_iBc'] = background_correction(df, 'iB0', 'iBc', 'unc_iBc')
df['Tpumpc'], df['unc_Tpumpc'] = pumptemp_corr(df, 'internalpump', 'Tpump', 'unc_Tpump', 'P', 'Tpumpc', 'unc_Tpumpc')
# df['Phipc'], df['unc_Phipc'] = pumpflow_correction(df, 'P', 'Phip', 'unc_Phip', 'komhyr_95', 'Phipc', 'unc_Phipc')
# df['O3c1'] = currenttopo3(df, 'I', 'Tpumpc', 'iBc', 'Eta', 'PF', False, 'O3c1')
df['O3c'] = currenttopo3(df, 'I', 'Tpumpc', 'iBc', 'Eta', 'Phip_komcpl', False, 'O3c')

# df['Ic1'] = po3tocurrent(df, 'O3', 'Tpumpc', 'iBc', 'Eta', 'PF', False, 'Ic1')
# df['Ic'] = po3tocurrent(df, 'O3', 'Tpumpc', 'iBc', 'Eta', 'Phipc', False, 'Ic2')

#
# df = df.drop(['U', 'Height', 'O3', 'Tbox', 'I',  'mRadioSondeNr', 'PF', 'iB0', 'iB1', 'CorrectionFactor', 'SondeNr',
#               'Tpump', 'unc_Tpump', 'Phip', 'unc_Phip','InterfaceNr', 'deltat', 'unc_deltat', 'deltat_ppi', 'unc_deltat_ppi',
#               'unc_phipcor'], axis = 1)

df = df.round(4)

print(list(df))

df.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/one_day/202011231129_1s_hom_two.csv")
