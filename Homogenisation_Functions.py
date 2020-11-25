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

pval = np.array([1030, 200, 100, 50, 30, 20, 10, 7, 5, 3])


komhyr_86 = np.array([1, 1.007, 1.018, 1.022, 1.032, 1.055, 1.070, 1.092, 1.124])  # SP Komhyr
komhyr_95 = np.array([1, 1.007, 1.018, 1.029, 1.041, 1.066, 1.087, 1.124, 1.241])  # ECC Komhyr
john_02 = np.array([1, 1.035, 1.052, 1.072, 1.088, 1.145, 1.200, 1.1260, 1])  # ECC Johnson
sbrecht_98 = np.array([1, 1.027, 1.075, 1.108, 1.150, 1.280, 1.5, 1.8, 1])  # BM Steinbrecht
kob_66 = np.array([1, 1.02, 1.04, 1.07, 1.11, 1.25, 1.4, 1.66, 1])  # Kobayashi

komhyr_86_unc = np.array([0, 0.005, 0.006, 0.008, 0.009, 0.010, 0.012, 0.014, 0.025])  # SP Komhyr
komhyr_95_unc = np.array([0, 0.005, 0.005, 0.008, 0.012, 0.023, 0.024, 0.024, 0.043])  # ECC Komhyr
john_02_unc = np.array([0, 0.011, 0.012, 0.015, 0.018, 0.020, 0.025, 0.030, 0.0])  # ECC Johnson
sbrecht_98_unc = np.array([0, 0.004, 0.006, 0.007, 0.011, 0.020, 0.1, 0.2, 0.0])  # BM Steinbrecht
kob_66_unc = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])  # Kobayashi

RS41_cor = np.array([1.171, 1.131, 1.092, 1.055, 1.032, 1.022, 1.015, 1.011, 1.008, 1.006, 1.004, 1.000])
RS41_pval = np.array([2.0, 3.0, 5.0, 10.0, 20.0, 30.0, 50.0, 100.0, 200.0, 300.0, 500.0, 1000.0])

RS41_cor = np.flipud(RS41_cor)
RS41_pval = np.flipud(RS41_pval)


def func_ptoi(df, po3, tpump, etac, phip, ib):
    i = po3 * etac * phip / 0.043085 + ib
    return i

def pf_groundcorrection(df, phim, unc_phim, tlab, plab, rhlab, out, unc_out):
    """
    :param df:
    :param phim:
    :param unc_phip:
    :param tlab:
    :param plab:
    :param rhlab:
    :param out:
    :param unc_out:
    :return:
    """
    cPL = 2/tlab
    cPH = 0 ## for now
    unc_cPL = 0
    unc_cPH = 0

    df[out] = (1 + cPL - cPH) * df[phim]
    df[unc_out] = df[out] * np.sqrt((df[unc_phim]/df[phim])**2 + (unc_cPL)**2 + (unc_cPH)**2)

    return df[out], df[unc_out]


def pf_efficiencycorrection(df, pair, phip, unc_phip, pumpcorrectiontag, out, unc_out):
    """
    :param df:
    :param pair:
    :param phip:
    :param pumpcorrectiontag:
    :return: df[phipcor], df[unc_phip]
    """

    if pumpcorrectiontag == 'RS41':
        for j in range(len(RS41_pval) - 1):
            filt = (df[pair] < RS41_pval[j]) & (df[pair] >= RS41_pval[j + 1])
            df.loc[filt,out] = df.loc[filt, phip] / RS41_cor[j]
            df.loc[filt, 'unc_phipcor'] = 0

    else:
        for i in range(len(pval) - 1):
            filt = (df[pair] < pval[i]) & (df[pair] >= pval[i + 1])

            if pumpcorrectiontag == 'komhyr_86':
                df.loc[filt,out] = df.loc[filt, phip] / komhyr_86[i]
                df.loc[filt, 'unc_phipcor'] = komhyr_86_unc[i]
            if pumpcorrectiontag == 'komhyr_95':
                print(i, 'komhyr 95', pval[i],  pval[i + 1],  komhyr_95[i])
                df.loc[filt,out] = df.loc[filt, phip] / komhyr_95[i]
                df.loc[filt, 'unc_phipcor'] = komhyr_95_unc[i]
            if pumpcorrectiontag == 'john_02':
                df.loc[filt,out] = df.loc[filt, phip] / john_02[i]
                df.loc[filt, 'unc_phipcor'] = john_02_unc[i]
            if pumpcorrectiontag == 'sbrecht_98':
                df.loc[filt,out] = df.loc[filt, phip] / sbrecht_98[i]
                df.loc[filt, 'unc_phipcor'] = sbrecht_98_unc[i]
            if pumpcorrectiontag == 'kob_66':
                df.loc[filt,out] = df.loc[filt, phip] / kob_66[i]
                df.loc[filt, 'unc_phipcor'] = kob_66_unc[i]

    df[unc_out] = df[phip] * np.sqrt((df[unc_phip] / df[phip]) ** 2 + (df['unc_phipcor'] / df[out]) ** 2)

    return df[out], df[out]


def background_correction(df, ib, out, unc_out):
    """
    :param df:
    :param ib2:
    :return: df[ib]
    """
    median = np.median(df[df[ib] < 0.1][ib])
    std = np.std(df[df[ib] < 0.1][ib])

    df.loc[(df[ib] > median + 2 * std) | (df[ib] < median - 2 * std), out] = median
    df.loc[(df[ib] <= median + 2 * std) & (df[ib] >= median - 2 * std), out] = df.loc[(df[ib] <= median + 2 * std) & (df[ib] >= median - 2 * std), ib]

    df.loc[(df[ib] > median + 2 * std) | (df[ib] < median - 2 * std), unc_out] = 2 * std
    df.loc[(df[ib] <= median + 2 * std) & (df[ib] >= median - 2 * std), unc_out] = std

    return df[out], df[unc_out]


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


def currenttopo3(df, im, tpump, ib, etac, phip, boolcorrection, out):
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
        df.loc[(df[im] == 0), out] = 0
        df[out] = 0.043085 * df[tpump] / (df[etac] * df[phip]) * (df[im] - df[ib])

    return df[out]


def pumptemp_corr(df, boxlocation, temp, unc_temp, pair, out, unc_out):
    '''
    :param df: dataframe
    :param boxlocation: location of the temperature measurement
    :param temp: temp. of the pump that was measured at boxlocation
    :param pressure: pressure of the air
    :return: the corrected base temperature of the pump
    '''

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

    df.loc[filt, out] = df.loc[filt, temp] + df.loc[filt, 'deltat'] + df.loc[filt, 'deltat_ppi']
    df.loc[filt, unc_out] = df.loc[filt, out] * np.sqrt(
        (df.loc[filt, unc_temp] ** 2 / df.loc[filt, temp] ** 2) +
        (df.loc[filt, 'unc_deltat'] ** 2 / df.loc[filt, 'deltat'] ** 2)
        + (df.loc[filt, 'unc_deltat_ppi'] ** 2 / df.loc[filt, 'deltat_ppi'] ** 2))

    df = df.drop(['deltat', 'unc_deltat', 'deltat_ppi', 'unc_deltat_ppi'], axis=1)

    return df.loc[filt,out], df.loc[filt,unc_out]


def conversion_absorption(df, pair, solvolume):
    '''
    :param df: dataframe
    :param pair: air pressure column
    :param solvolume: volume of the cathode solution in mls
    :return: absorption efficeincy and its uncertainity
    '''

    if solvolume == 2.5:
        df.loc[(df[pair] > 100) & (df[pair] < 1050), 'alpha_o3'] = 1.0044 - 4.4 * 10 ** -5 * df[pair]
        df.loc[(df[pair] <= 100), 'alpha_o3'] = 1.0
    if solvolume == 3.0:
        df.loc[(df[pair] <= 1050), 'alpha_o3'] = 1.0
    df['unc_alpha'] = 0.01

    # for k in range(len(pair)):
    #
    #     if solvolume == 2.5:
    #         if (pair[k] > 100) and (pair[k] < 1050): alpha_o3 = 1.0044 - 4.4 * 10 ** -5 * pair[k]
    #         if pair[k] <= 100: alpha_o3 = 1.00
    #     if (solvolume == 3.0) and (pair[k] < 1050): alpha_o3 = 1.0

    return df['alpha_o3'], df['unc_alpha']


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


def conversion_efficiency(df, alpha_o3, alpha_unc, rstoich, rstoich_err, boolsstchange):
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
    df['eta_c'] = df[alpha_o3] * stoich
    df['unc_eta'] = df['eta_c'] * np.sqrt((df[alpha_unc] / df[alpha_o3]) ** 2 + (stoich_unc / stoich) ** 2)

    if boolsstchange:
        df['eta_c'] = df[alpha_o3] * stoich
        df['unc_eta'] = df['eta_c'] * np.sqrt(
            (alpha_unc / df[alpha_o3]) ** 2 + (stoich_unc / stoich) ** 2 + (rstoich_err / rstoich) ** 2)

    return df['eta_c'], df['unc_eta']
