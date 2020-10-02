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

def PO3toCurrent(o3, tpump, ib, etac, phip, boolother):
    '''
    :param o3 partial ozone pressure of the sonde
    :param tpumo: pump temperature
    :param ib: background current
    :param etac: conversion efficiency
    :param phip: gas volume flow rate in cm3^3/s
    :param boolother: a boolean for if any other correction is applied
    :return: Current obtained from PO3
    '''
    if(boolother == False):
        current = 0.043085 * etac * phip/tpump  + ib

    ## husband check type hinting
    ## read pep8 python husband :/

    return current


def conversion_alpha(Pair, SolVolume):
    ''''
    Pair: Pressure of the air
    SolVolume: volume of the cathode solution in mls
    ( i might also need to add the year)
    '''

    if SolVolume == 2.5:
        if (Pair > 100) and (Pair < 1050): alpha_o3 = 1.0044 - 4.4 * 10**-5 * Pair
        if Pair <= 100: alpha_o3 = 1.00
    if (SolVolume == 3.0) and (Pair < 1050): alpha_o3 = 1.0

    unc_alpha = 0.01

    return alpha_o3, unc_alpha


def conversion_stoichemtry(Pair, SondeSSTone, SondeSSTtwo):
    '''
    :param Pair: Pressure of the air
    :param SondeSSTone: an array of the Sonde type and SST i.e: ['SPC', '0.5'] that was in use
    :param SondeSSTtwo: an array of the Sonde type and SST to be changed to i.e: ['SP', '1.0']
    :return: r and uncertainity on r which are transfer functions and taken from Table 3 from the guideline
    '''

    # if SondeSSTone == SondeSSTtwo: r = 1
    if (SondeSSTone == ['SPC', 0.5]) and (SondeSSTtwo == ['SPC', 1.0]):
        if Pair >= 30: r = 0.96
        if Pair < 30: r = 0.90 + 0.041 * np.log10(Pair)
    if (SondeSSTone == ['ENSCI', 1.0]) and (SondeSSTtwo == ['ENSCI', 0.5]):
        if Pair >= 30: r = 0.96
        if Pair < 30: r = 0.90 + 0.041 * np.log10(Pair)
    if (SondeSSTone == ['ENSCI', 1.0]) and (SondeSSTtwo == ['SPC', 1.0]):
        if Pair >= 50: r = 0.96
        if Pair < 50: r = 0.764 + 0.133 * np.log10(Pair)
    if (SondeSSTone == ['SPC', 0.5]) and (SondeSSTtwo == ['ENSCI', 0.5]):
        if Pair >= 50: r = 0.96
        if Pair < 50: r = 0.764 + 0.133 * np.log10(Pair)

    unc_r = 0.05

    return r, unc_r

def conversion_efficiency(alpha, alpha_unc, rstoich, rstoich_err, boolSSTchange):
    '''

    :param alpha: absorption efficiency obtained by conversion_alpha
    :param alpha_unc: absorption efficiency unc. obtained by conversion_alpha
    :param rstoich: transfer functions obtained by conversion_stoichemtry
    :param rstoich_err: transfer functions unc. obtained by conversion_stoichemtry
    :param boolSSTchange: if there is a need for tranfer functions of the conversion_stoichemtry, if there was a change
    in SST or Sonde Tyoe
    :return: total efficiency of the conversion etac_c and its uncertainity Eq. 4 from the guideline
    '''

    stoich = 1
    stoich_unc = 0.03
    eta_c = alpha * stoich
    unc_eta = eta_c * np.sqrt((alpha_unc/alpha) ** 2 + (stoich_unc/stoich)**2)

    if boolSSTchange:
        eta_c = alpha * stoich
        unc_eta = eta_c * np.sqrt((alpha_unc / alpha)**2 + (stoich_unc / stoich)**2 + (rstoich_err/rstoich)**2)

    return eta_c, unc_eta
