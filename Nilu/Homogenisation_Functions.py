import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import datetime

## General guidelines for Homogenisation of O3S-Data
# P03 = 0.043085 T_pump ( I_M - I_B) / (eta_c * Phi_p)
# T_pump " pump temperature in Kelvin
# I_M: ECC current in microA
# I_B background current
# eta_c: conersion efficiency
# Phi_p: gas volume flow rate in cm3^3/s

pval = np.array([1100, 200, 100, 50, 30, 20, 10, 7, 5, 3])


komhyr_86 = np.array([1, 1, 1.007, 1.018, 1.022, 1.032, 1.055, 1.070, 1.092, 1.124])  # SP Komhyr
komhyr_95 = np.array([1,1,  1.007, 1.018, 1.029, 1.041, 1.066, 1.087, 1.124, 1.241])  # ECC Komhyr
john_02 = np.array([1, 1.035, 1.052, 1.072, 1.088, 1.145, 1.200, 1.1260, 1])  # ECC Johnson
sbrecht_98 = np.array([1, 1.027, 1.075, 1.108, 1.150, 1.280, 1.5, 1.8, 1])  # BM Steinbrecht
kob_66 = np.array([1, 1.02, 1.04, 1.07, 1.11, 1.25, 1.4, 1.66, 1])  # Kobayashi

# SensorType = 'SPC-6A'
VecP_ECC6A =    [    0,     2,     3,      5,    10,    20,    30,    50,   100,   200,   300,   500, 1000, 1100]
VecC_ECC6A_25 = [ 1.16,  1.16, 1.124,  1.087, 1.054, 1.033, 1.024, 1.015, 1.010, 1.007, 1.005, 1.002,    1,    1]
VecC_ECC6A_30 = [ 1.171, 1.171, 1.131, 1.092, 1.055, 1.032, 1.022, 1.015, 1.011, 1.008, 1.006, 1.004,    1,    1]

komhyr_86_unc = np.array([0,0, 0.005, 0.006, 0.008, 0.009, 0.010, 0.012, 0.014, 0.025])  # SP Komhyr
komhyr_95_unc = np.array([0,0, 0.005, 0.005, 0.008, 0.012, 0.023, 0.024, 0.024, 0.043])  # ECC Komhyr
john_02_unc = np.array([0, 0.011, 0.012, 0.015, 0.018, 0.020, 0.025, 0.030, 0.0])  # ECC Johnson
sbrecht_98_unc = np.array([0, 0.004, 0.006, 0.007, 0.011, 0.020, 0.1, 0.2, 0.0])  # BM Steinbrecht
kob_66_unc = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])  # Kobayashi

RS41_cor = np.array([1.171, 1.131, 1.092, 1.055, 1.032, 1.022, 1.015, 1.011, 1.008, 1.006, 1.004, 1.000])
RS41_pval = np.array([2.0, 3.0, 5.0, 10.0, 20.0, 30.0, 50.0, 100.0, 200.0, 300.0, 500.0, 1000.0])

RS41_cor = np.flipud(RS41_cor)
RS41_pval = np.flipud(RS41_pval)

k = 273.15

def func_ptoi(df, po3, tpump, etac, phip, ib):
    i = po3 * etac * phip / 0.043085 + ib
    return i

def organize_metadata(dfm):

    dfm['rhlab'] = dfm['Relative humidity in laboratory during sonde flow rate calibration'].astype('float')
    dfm['plab'] = dfm['Background surface pressure (hPa)'].astype('float')
    dfm['tlab'] = dfm['Temperature in laboratory during sonde flow rate calibration'].astype('float')

    dfm = dfm[(dfm.tlab < 30) & (dfm.tlab > 10)]

    return dfm


def calculate_cph(dfmeta):

    dfmeta['x'] = ((7.5 * dfmeta['tlab']) / (dfmeta['tlab'] + 237.3)) + 0.7858
    dfmeta['psaturated'] = 10 ** (dfmeta['x'])
    dfmeta['cph'] = (1 - dfmeta['rhlab']/100) \
                    * dfmeta['psaturated']/dfmeta['plab']

    dfmeta['cpl'] = 2/(dfmeta['tlab'] + k)

    # print('cph', dfmeta.at[10,'cph'])


    return dfmeta


def pf_groundcorrection(df, phim, unc_phim, tlab, plab, rhlab):
    """
    :param df:
    :param phim:
    :param unc_phip:
    :param tlab:
    :param plab:
    :param rhlab:
    :return:
    """

    df['x'] = ((7.5 * df['TLab']) / (df['TLab'] + 237.3)) + 0.7858
    df['psaturated'] = 10 ** (df['x'])
    df['cph'] = (1 - df['ULab'] / 100) \
                    * df['psaturated'] / df['Pground']

    df['tlabK'] = df[tlab] + k
    df['cPL'] = 2/df['tlabK']
    cPH = 0 ## for now
    unc_cPL = df.at[df.first_valid_index(),'unc_cpl']
    unc_cPH = df.at[df.first_valid_index(),'unc_cph']

    df['Phip_ground'] = (1 + df['cPL'] - df['cph']) * df[phim]
    df['unc_Phip_ground'] = df['Phip_ground'] * np.sqrt((0.02)**2 + (unc_cPL)**2 + (unc_cPH)**2)

    return df['Phip_ground'], df['unc_Phip_ground']


def VecInterpolate(XValues, YValues, unc_YValues, dft, Pair, LOG):

    dft['Cef'] = 0

    i = 1
    # ilast = len(YValues) - 1
    # return last value if xval out of xvalues range
    # y = float(YValues[ilast])

    dft = dft.reset_index()

    for k in range(len(dft)):

        for i in range(len(XValues)-1):
            # just check that value is in between xvalues
            if (XValues[i] >= dft.at[k, Pair] >= XValues[i + 1]):

                x1 = float(XValues[i])
                x2 = float(XValues[i+1])
                # print('k', k,x1,x2)
                if LOG == 1:
                    x = math.log(x)
                    x1 = math.log(x1)
                    x2 = math.log(x2)
                y1 = float(YValues[i])
                y2 = float(YValues[i+1])
                # print(k,y1,y2)

                unc_y1 = float(unc_YValues[i])
                unc_y2 = float(unc_YValues[i + 1])
                dft.at[k,'Cpf'] = y1 + (dft.at[k,Pair] - x1) * (y2 - y1) / (x2 - x1)
                dft.at[k,'unc_Cpf'] = unc_y1 + (dft.at[k,Pair] - x1) * (unc_y2 - unc_y1) / (x2 - x1)
                # print(k, dft.at[k,'Cpf'] )


    return dft['Cpf'], dft['unc_Cpf']


def pumpflow_efficiency(df, pair,  pumpcorrectiontag, effmethod ):

    if effmethod == 'polyfit':

        if pumpcorrectiontag == 'komhyr_95':
            df['Cpf'] = 2.17322861 - 3.686021555 * np.log10(df[pair]) + 5.105113826 * (
                np.log10(df[pair])) ** 2 - 3.741595297 * (np.log10(df[pair])) ** 3 + 1.496863681 * (
                            np.log10(df[pair])) ** 4 - \
                        0.3086952232 * (np.log10(df[pair])) ** 5 + 0.02569158956 * (np.log10(df[pair])) ** 6
            df['unc_Cpf'] = 0.07403603165 - 0.08532895578 * np.log10(df[pair]) + 0.03463984997 * (
                np.log10(df[pair])) ** 2 - 0.00462582698 * (np.log10(df[pair])) ** 3


    if effmethod == 'table_interpolate':

        if pumpcorrectiontag == 'komhyr_86':
            df['Cpf'], df['unc_Cpf'] = VecInterpolate(pval, komhyr_86, komhyr_86_unc,  df, pair, 0)

        if pumpcorrectiontag == 'komhyr_95':
            df['Cpf'], df['unc_Cpf'] = VecInterpolate(pval, komhyr_95, komhyr_95_unc,  df, pair, 0)

    return df['Cpf'], df['unc_Cpf']

def return_phipcor(df,phip_grd, unc_phip_grd, cpf, unc_cpf):

    df['Phip_cor'] = df[phip_grd]/df[cpf]

    df['unc_Phip_cor'] = df['Phip_cor'] * np.sqrt( df[unc_phip_grd]**2/df[phip_grd]**2 + df[unc_cpf]**2/df[cpf]**2 )

    return df['Phip_cor'], df['unc_Phip_cor']



#
# def pf_efficiencycorrection(df, pair, phip, unc_phip, pumpcorrectiontag, effmethod, out, unc_out):
#     """
#     :param df:
#     :param pair:
#     :param phip:
#     :param pumpcorrectiontag:
#     :param effmethod:
#     :return: df[phipcor], df[unc_phip]
#
#     """
#
#     if effmethod == 'polyfit':
#
#         if pumpcorrectiontag == 'komhyr_95':
#
#             df['PCF'] = 2.17322861 - 3.686021555 * np.log10(df[pair]) + 5.105113826 * (
#                 np.log10(df[pair])) ** 2 - 3.741595297 * (np.log10(df[pair])) ** 3 + 1.496863681 * (np.log10(df[pair]))**4 - \
#                         0.3086952232 * (np.log10(df[pair])) ** 5 + 0.02569158956 * (np.log10(df[pair])) ** 6
#             df['dPCF'] = 0.07403603165-0.08532895578*np.log10(df[pair])+0.03463984997*(np.log10(df[pair]))**2 - 0.00462582698 *(np.log10(df[pair]))**3
#
#             df[out] = df[phip]/df['PCF']
#             # df['unc_phipcor'] = df['dPCF']**2/df['PCF']**2
#             df[unc_out] = df[unc_phip]**2 + df['dPCF']**2/df['PCF']**2
#
#     if effmethod == 'table_interpolate':
#
#         if pumpcorrectiontag == 'komhyr_86':
#             df['Cpf'] = VecInterpolate(pval, komhyr_86, df[pair], 0)
#                 df.loc[filt, 'unc_phipcor'] = 0
#
#
#     if effmethod == 'table':
#
#         if pumpcorrectiontag == 'RS41':
#             for j in range(len(RS41_pval) - 1):
#                 filt = (df[pair] < RS41_pval[j]) & (df[pair] >= RS41_pval[j + 1])
#                 df.loc[filt,out] = df.loc[filt, phip] / RS41_cor[j]
#                 df.loc[filt, 'unc_phipcor'] = 0
#
#         else:
#             for i in range(len(pval) - 1):
#                 filt = (df[pair] < pval[i]) & (df[pair] >= pval[i + 1])
#
#                 if pumpcorrectiontag == 'komhyr_86':
#                     df.loc[filt,out] = df.loc[filt, phip] / komhyr_86[i]
#                     df.loc[filt, 'unc_phipcor'] = komhyr_86_unc[i]
#                 if pumpcorrectiontag == 'komhyr_95':
#                     print(i, 'komhyr 95', pval[i],  pval[i + 1],  komhyr_95[i])
#                     df.loc[filt,out] = df.loc[filt, phip] / komhyr_95[i]
#                     df.loc[filt, 'unc_phipcor'] = komhyr_95_unc[i]
#                 if pumpcorrectiontag == 'john_02':
#                     df.loc[filt,out] = df.loc[filt, phip] / john_02[i]
#                     df.loc[filt, 'unc_phipcor'] = john_02_unc[i]
#                 if pumpcorrectiontag == 'sbrecht_98':
#                     df.loc[filt,out] = df.loc[filt, phip] / sbrecht_98[i]
#                     df.loc[filt, 'unc_phipcor'] = sbrecht_98_unc[i]
#                 if pumpcorrectiontag == 'kob_66':
#                     df.loc[filt,out] = df.loc[filt, phip] / kob_66[i]
#                     df.loc[filt, 'unc_phipcor'] = kob_66_unc[i]
#
#     # df[unc_out] = df[phip] * np.sqrt((df[unc_phip] / df[phip]) ** 2 + (df['unc_phipcor'] / df[out]) ** 2)
#
#     return df[out], df[unc_out]


def background_correction(df, dfmeta, ib,):
    """
    :param df:
    :param ib2:
    :return: df[ib]
    """

    df['iBc'] = 0
    df['unc_iBc'] = 0

    mean = np.mean(dfmeta[dfmeta[ib] < 0.1][ib])
    std = np.std(dfmeta[dfmeta[ib] < 0.1][ib])

    df.loc[(df[ib] > mean + 2 * std) | (df[ib] < mean - 2 * std), 'iBc'] = mean
    df.loc[(df[ib] <= mean + 2 * std) & (df[ib] >= mean - 2 * std), 'iBc'] = df.loc[(df[ib] <= mean + 2 * std) & (df[ib] >= mean - 2 * std), ib]

    df.loc[(df[ib] > mean + 2 * std) | (df[ib] < mean - 2 * std), 'unc_iBc'] = 2 * std
    df.loc[(df[ib] <= mean + 2 * std) & (df[ib] >= mean - 2 * std), 'unc_iBc'] = std

    return df['iBc'], df['unc_iBc']


def po3tocurrent(df, po3, tpump, ib, etac, phip, boolcorrection, out):
    '''
    :param df: dataframe
    :param po3: partial ozone pressure of the sonde
    :param tpump: pump temperature
    :param ib: background current, question: which one?
    :param etac: conversion efficiency
    :param phip: gas volume flow rate in cm3^3/s
    :param boolcorrection: a boolean for if any other correction is applied
    :return: Current obtained from PO3
    '''

    if (boolcorrection == False):
        df.loc[(df[po3] == 0), out] = 0
        df[out] = (df[po3] * df[etac] * df[phip]) / (df[tpump] * 0.043085) + df[ib]

    return df[out]


def currenttopo3(df, im, tpump, ib, etac, phip, boolcorrection):
    '''
    :param df: dataframe
    :param po3: partial ozone pressure of the sonde
    :param pair:pressure of the air
    :param tpump: pump temperature
    :param ib: background current, question: which one?
    :param etac: conversion efficiency
    :param phip: gas volume flow rate in cm3^3/s
    :param boolcorrection: a boolean for if any other correction is applied
    :return: Current obtained from PO3
    '''

    if (boolcorrection == False):
        df.loc[(df[im] == 0), 'O3c'] = 0
        df['O3c'] = 0.043085 * df[tpump] / (df[etac] * df[phip]) * (df[im] - df[ib])

    return df['O3c']


def pumptemp_corr(df, boxlocation, temp, unc_temp, pair):
    '''
    :param df: dataframe
    :param boxlocation: location of the temperature measurement
    :param temp: temp. of the pump that was measured at boxlocation
    :param pressure: pressure of the air
    :return: the corrected base temperature of the pump
    '''
    df['Tpump_cor'] = 0
    df['unc_Tpump_cor'] = 0

    if boxlocation == 'box':  # case I in O3S-DQA guide
        df.loc[(df[pair] >= 40), 'deltat'] = 7.43 - 0.393 * np.log10(df.loc[(df[pair] >= 40), pair])
        df.loc[(df[pair] < 40) & (df[pair] > 6), 'deltat'] = 2.7 + 2.6 * np.log10(
            df.loc[(df[pair] < 40) & (df[pair] > 6), pair])
        df.loc[(df[pair] <= 6), 'deltat'] = 4.5
        df['unc_deltat'] = 1  # units in K

    if boxlocation == 'externalpump_taped':  # case III in O3S-DQA guide
        df.loc[(df[pair] > 70), 'deltat'] = 20.6 - 6.7 * np.log10(df.loc[(df[pair] > 70), pair])
        df.loc[(df[pair] > 70), 'unc_deltat'] = 3.9 - 1.13 * np.log10(df.loc[(df[pair] > 70), pair])
        df.loc[(df[pair] <= 70) & (df[pair] >= 15), 'deltat'] = 8.25
        df.loc[(df[pair] < 15) & (df[pair] >= 5), 'deltat'] = 3.25 - 4.25 * np.log10(
            df.loc[(df[pair] < 15) & (df[pair] >= 5), pair])
        df.loc[(df[pair] <= 70), 'unc_deltat'] = 0.3 + 1.13 * np.log10(df.loc[(df[pair] <= 70), pair])

    if boxlocation == 'externalpump_glued':  # case IV in O3S-DQA guide
        df.loc[(df[pair] > 40), 'deltat'] = 6.4 - 2.14 * np.log10(df.loc[(df[pair] > 40), pair])
        df.loc[(df[pair] <= 40) & (df[pair] >= 3), 'deltat'] = 3.0
        df['unc_deltat'] = 0.5  # units in K

    filt = df[pair] > 3

    if boxlocation == 'internalpump':  # case V in O3S-DQA guide
        df.loc[filt,'deltat'] = 0  # units in K
        df.loc[filt,'unc_deltat'] = 0  # units in K

    df.loc[(df[pair] > 3), 'deltat_ppi'] = 3.9 - 0.8 * np.log10(df.loc[(df[pair] > 3), pair])
    df.loc[(df[pair] > 3), 'unc_deltat_ppi'] = 0.5

    df.loc[filt, 'Tpump_cor'] = df.loc[filt, temp] + df.loc[filt, 'deltat'] + df.loc[filt, 'deltat_ppi']
    df.loc[filt, 'unc_Tpump_cor'] = (df.loc[filt, unc_temp] ** 2 / df.loc[filt, temp] ** 2) + \
                            (df.loc[filt, 'unc_deltat'] ** 2 / df.loc[filt, temp] ** 2)+ (df.loc[filt, 'unc_deltat_ppi'] ** 2 / df.loc[filt, temp] ** 2)
    # df.loc[filt, unc_out] = df.loc[filt, out] * np.sqrt(
    #     (df.loc[filt, unc_temp] ** 2 / df.loc[filt, temp] ** 2) +
    #     (df.loc[filt, 'unc_deltat'] ** 2 / df.loc[filt, temp] ** 2)
    #     + (df.loc[filt, 'unc_deltat_ppi'] ** 2 / df.loc[filt, temp] ** 2))

    df = df.drop(['deltat', 'unc_deltat', 'deltat_ppi', 'unc_deltat_ppi'], axis=1)

    return df.loc[filt,'Tpump_cor'], df.loc[filt,'unc_Tpump_cor']


def absorption_efficiency (df, pair, solvolume):
    '''
    :param df: dataframe
    :param pair: air pressure column
    :param solvolume: volume of the cathode solution in mls
    :return: absorption efficeincy and its uncertainity
    '''
    df['unc_alpha_o3'] = 0.01
    df['alpha_o3'] = 1


    if solvolume == 2.5:
        df.loc[(df[pair] > 100) & (df[pair] < 1050), 'alpha_o3'] = 1.0044 - 4.4 * 10 ** -5 * df.loc[(df[pair] > 100) & (df[pair] < 1050), pair]
        df.loc[(df[pair] <= 100), 'alpha_o3'] = 1.0
    if solvolume == 3.0:
        df.loc[(df[pair] <= 1050), 'alpha_o3'] = 1.0


    return df['alpha_o3'], df['unc_alpha_o3']


def stoichemtry_conversion(df, pair, sensortype, solutionconcentration, reference):
    '''
    :param pair: Pressure of the air
    :param sondesstone: an array of the Sonde type and SST i.e: ['SPC', '0.5'] that was in use
    :param sondessttwo: an array of the Sonde type and SST to be changed to i.e: ['SP', '1.0']
    :return: r and uncertainity on r which are transfer functions and taken from Table 3 from the guideline
    '''


    df['stoich'] = 0
    df['unc_stoich'] = 0.05

    if (reference == 'ENSCI05') & (sensortype == 'DMT-Z') & (solutionconcentration == 10):
        df.loc[df[pair] >= 30, 'stoich'] = 0.96
        df.loc[df[pair] < 30, 'stoich'] = 0.90 + 0.041 * np.log10(df[df[pair] < 30][pair])

    if (reference == 'ENSCI05') & (sensortype == 'DMT-Z') & (solutionconcentration == 5):
        df['stoich'] = 1
        df['unc_stoich'] = 0.03

    if (reference == 'ENSCI05') & (sensortype == 'SPC') & (solutionconcentration == 10):
        df['stoich'] = 1
        df['unc_stoich'] = 0.03

    # if (reference == 'SPC10') & (sensortype == 'SP') & (solutionconcentration == 5):
    #     df.loc[df[pair] >= 50, 'stoich'] = 0.96
    #     df.loc[df[pair] < 50, 'stoich'] = 0.764 + 0.133 * np.log10(df[df[pair] < 30])

    return df['stoich'], df['unc_stoich']


def conversion_efficiency(df, alpha_o3, alpha_unc_o3, stoich, stoich_unc):
    '''

    :param alpha: absorption efficiency obtained by conversion_absorption
    :param alpha_unc: absorption efficiency unc. obtained by conversion_alpha
    :param rstoich: transfer functions obtained by conversion_stoichemtry
    :param rstoich_err: transfer functions unc. obtained by conversion_stoichemtry
    :return: total efficiency of the conversion etac_c and its uncertainity Eq. 4 from the guideline
    '''

    df['eta_c'] = df[alpha_o3] * df[stoich]
    df['unc_eta'] = df['eta_c'] * np.sqrt((df[alpha_unc_o3] / df[alpha_o3]) ** 2 + (df[stoich_unc] / df[stoich]) ** 2)


    return df['eta_c'], df['unc_eta']
