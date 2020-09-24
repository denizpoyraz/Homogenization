import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime


## General guidelines for Homogenisation of O3S-Data
# Conversion efficiency eta_c = alpha_o3 * stoich_c
# conversion uncertainity

# def ozonesonde_pressure():




def conversion_alpha(Pair, SolVolume):
    ''''
    Pair: Pressure of the air
    SolVolume: volume of the cathode solution in mls
    ( i might also need to add the year)
    '''

    if SolVolume == 2.5:
        if (Pair > 100) and (Pair < 1050): alpha_o3 = 1.0044 - 4.4 *  10**-5 * Pair
        if Pair <= 100: alpha_o3 = 1.00
    if SolVolume == 3.0: alpha_o3 = 1.0

    unc_alpha = 0.01

    return alpha_o3, unc_alpha



def conversion_stoich(Pair, SondeSSTone, SondeSSTtwo):
    '''
    Pair: Pressure of the air
    SondeSSTone: an array of the Sonde type and SST i.e: ['SPC', '0.5'] that was in use
    SondeSSTtwo: an array of the Sonde type and SST to be changed to i.e: ['SP', '1.0']
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

    stoich = 1
    stoich_unc = 0.03
    eta_c = alpha * stoich

    unc_eta = eta_c * np.sqrt((alpha_unc/alpha) ** 2 + (stoich_unc/stoich)**2)


    if boolSSTchange:
        eta_c = alpha * stoich
        unc_eta = eta_c * np.sqrt((alpha_unc / alpha)**2 + (stoich_unc / stoich)**2 + (rstoich_err/rstoich)**2)

    return eta_c, unc_eta
