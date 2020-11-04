import numpy as np
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

pval = np.array([1000, 200, 100, 50, 30, 20, 10, 7, 5, 3])

komhyr_86 = np.array([1, 1.007, 1.018, 1.022, 1.032, 1.055, 1.070, 1.092, 1.124]) #ECC Komhyr
komhyr_95 = np.array([1, 1.007, 1.018, 1.029, 1.041, 1.066, 1.087, 1.124, 1,241]) #ECC Komhyr
john_02 = np.array([1, 1.035, 1.052, 1.072, 1.088, 1.145, 1.200, 1.1260, 1]) #ECC Johnson
sbrecht_98 = np.array([1, 1.027, 1.075, 1.108, 1.150, 1.280, 1.5, 1.8, 1]) #BM Steinbrecht
kob_66 = np.array([1, 1.02, 1.04, 1.07, 1.11, 1.25, 1.4, 1.66, 1]) #Kobayashi

RS41_cor = np.array([1.171, 1.131, 1.092, 1.055, 1.032, 1.022, 1.015, 1.011, 1.008, 1.006, 1.004,1.000])
RS41_pval = np.array([2.0, 3.0, 5.0, 10.0, 20.0, 30.0, 50.0, 100.0, 200.0, 300.0, 500.0, 1000.0])

RS41_cor = np.flipud(RS41_cor)
RS41_pval = np.flipud(RS41_pval)

def po3tocurrent(df, o3, pair,  tpump, ib, etac, phip, pumpcorrectiontag, boolcorrection):
    '''
    :param df: dataframe
    :param o3: partial ozone pressure of the sonde
    :param pair:pressure of the air
    :param tpumo: pump temperature
    :param ib: background current, question: which one?
    :param etac: conversion efficiency
    :param phip: gas volume flow rate in cm3^3/s
    :param pumpcorrectiontag: pump flow correction factor applied depending on ecc type
    :param boolcorrection: a boolean for if any other correction is applied
    :return: Current obtained from PO3
    '''

    current = [0.0]*len(df)

    for k in range(len(df)):

        pump_corr = np.zeros(len(RS41_pval))

        if pumpcorrectiontag == 'RS41':
            for j in range(len(RS41_pval) - 1):
                # print('corr',k, j,  df.at[k, pair], RS41_pval[j], RS41_pval[j+1],  RS41_cor[j])
                if(df.at[k, pair] < RS41_pval[j]) & (df.at[k, pair] >= RS41_pval[j+1]):
                    # if (df.at[k, 'Pair'] >= Pval[p + 1]) & (df.at[k, 'Pair'] < Pval[p]):
                    pump_corr[j] = RS41_cor[j]
                    if (boolcorrection == False):
                        if df.at[k, o3] == 0:
                            current[k] = 0.0
                        else:
                            current[k] = (df.at[k, o3] * df.at[k, etac] * df.at[k, phip]) / (
                                        pump_corr[j] * (df.at[k, tpump] + 273) * 0.043085) + df.at[k, ib]


        else:
            for i in range(len(pval)-1):
                if(df[pair] < pval[i]) & (df[pair] >= pval[i+1]):
                    if pumpcorrectiontag == 'komhyr_86': pump_corr = komhyr_86[i]
                    if pumpcorrectiontag == 'komhyr_95': pump_corr = komhyr_95[i]
                    if pumpcorrectiontag == 'john_02': pump_corr = john_02[i]
                    if pumpcorrectiontag == 'sbrecht_98': pump_corr = sbrecht_98[i]
                    if pumpcorrectiontag == 'kob_66': pump_corr = kob_66[i]
                    if (boolcorrection == False):
                        if df.at[k, o3] == 0:
                            current[k] = 0.0
                        else:
                            current[k] = (df.at[k, o3] * df.at[k, etac] * df.at[k, phip]) / (pump_corr * (df.at[k, tpump]+273) * 0.043085) + df.at[k, ib]



        # dfr['Ic2'] = (dfr['O3'] * 1000) / (0.43085 * (dfr['Tbox'] + 273.15) * dfr['PF']) + dfr['iB0']

        # df.at[k, 'PO3_OPM'] * df.at[k, 'PFcor'] * JMA[p] / (df.at[k, 'TPext'] * 0.043085)

    ## husband check type hinting
    ## read pep8 python husband :/
    print('max', np.nanmax(current))

    return current


def conversion_absorption(pair, solvolume):
    ''''
    pair: Pressure of the air
    solvolume: volume of the cathode solution in mls
    ( i might also need to add the year)
    '''
    for k in range(len(pair)):

        if solvolume == 2.5:
            if (pair[k] > 100) and (pair[k] < 1050): alpha_o3 = 1.0044 - 4.4 * 10 ** -5 * pair[k]
            if pair[k] <= 100: alpha_o3 = 1.00
        if (solvolume == 3.0) and (pair[k] < 1050): alpha_o3 = 1.0

    unc_alpha = 0.01

    return alpha_o3, unc_alpha


def conversion_stoichemtry(pair, sondesstone, sondessttwo):
    '''
    :param pair: Pressure of the air
    :param sondesstone: an array of the Sonde type and SST i.e: ['SPC', '0.5'] that was in use
    :param sondessttwo: an array of the Sonde type and SST to be changed to i.e: ['SP', '1.0']
    :return: r and uncertainity on r which are transfer functions and taken from Table 3 from the guideline
    '''

    for k in range(len(pair)):

        # if sondesstone == sondessttwo: r = 1
        if (sondesstone == ['SPC', 0.5]) and (sondessttwo == ['SPC', 1.0]):
            if pair[k] >= 30: r = 0.96
            if pair[k] < 30: r = 0.90 + 0.041 * np.log10(pair[k])
        if (sondesstone == ['ENSCI', 1.0]) and (sondessttwo == ['ENSCI', 0.5]):
            if pair[k] >= 30: r = 0.96
            if pair[k] < 30: r = 0.90 + 0.041 * np.log10(pair[k])
        if (sondesstone == ['ENSCI', 1.0]) and (sondessttwo == ['SPC', 1.0]):
            if pair[k] >= 50: r = 0.96
            if pair[k] < 50: r = 0.764 + 0.133 * np.log10(pair[k])
        if (sondesstone == ['SPC', 0.5]) and (sondessttwo == ['ENSCI', 0.5]):
            if pair[k] >= 50: r = 0.96
            if pair[k] < 50: r = 0.764 + 0.133 * np.log10(pair[k])

    unc_r = 0.05

    return r, unc_r


def conversion_efficiency(alpha, alpha_unc, rstoich, rstoich_err, boolsstchange):
    '''

    :param alpha: absorption efficiency obtained by conversion_absorption
    :param alpha_unc: absorption efficiency unc. obtained by conversion_alpha
    :param rstoich: transfer functions obtained by conversion_stoichemtry
    :param rstoich_err: transfer functions unc. obtained by conversion_stoichemtry
    :param boolsstchange: if there is a need for tranfer functions of the conversion_stoichemtry, if there was a change
    in SST or Sonde Tyoe
    :return: total efficiency of the conversion etac_c and its uncertainity Eq. 4 from the guideline
    '''

    stoich = 1
    stoich_unc = 0.03
    eta_c = alpha * stoich
    unc_eta = eta_c * np.sqrt((alpha_unc / alpha) ** 2 + (stoich_unc / stoich) ** 2)

    if boolsstchange:
        eta_c = alpha * stoich
        unc_eta = eta_c * np.sqrt((alpha_unc / alpha) ** 2 + (stoich_unc / stoich) ** 2 + (rstoich_err / rstoich) ** 2)

    return eta_c, unc_eta


#############

# def po3tocurrent(o3, pair,  tpump, ib, etac, phip, pumpcorrectiontag, boolcorrection):
#     '''
#     :param o3: partial ozone pressure of the sonde
#     :param pair:pressure of the air
#     :param tpumo: pump temperature
#     :param ib: background current, question: which one?
#     :param etac: conversion efficiency
#     :param phip: gas volume flow rate in cm3^3/s
#     :param pumpcorrectiontag: pump flow correction factor applied depending on ecc type
#     :param boolcorrection: a boolean for if any other correction is applied
#     :return: Current obtained from PO3
#     '''
#
#     current = np.zeros(len(o3));
#
#     for k in range(len(o3)):
#
#         if pumpcorrectiontag == 'RS41':
#             for j in range(len(RS41_pval) - 1):
#                 pump_corr = RS41_cor[j]
#         else:
#             for i in range(len(pval)-1):
#                 if(pair[k] < pval[i]) & (pair[k] >= pval[i+1]):
#                     if pumpcorrectiontag == 'komhyr_86': pump_corr = komhyr_86[i]
#                     if pumpcorrectiontag == 'komhyr_95': pump_corr = komhyr_95[i]
#                     if pumpcorrectiontag == 'john_02': pump_corr = john_02[i]
#                     if pumpcorrectiontag == 'sbrecht_98': pump_corr = sbrecht_98[i]
#                     if pumpcorrectiontag == 'kob_66': pump_corr = kob_66[i]
#
#         if (boolcorrection == False):
#             current[k] = o3[k] * etac * phip  / (pump_corr * tpump * 0.043085) + ib
#
#         # df.at[k, 'PO3_OPM'] * df.at[k, 'PFcor'] * JMA[p] / (df.at[k, 'TPext'] * 0.043085)
#
#     ## husband check type hinting
#     ## read pep8 python husband :/
#
#     return current