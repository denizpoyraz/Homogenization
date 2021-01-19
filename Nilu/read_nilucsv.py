import pandas as pd
import glob
import math
import numpy as np
from re import search
from datetime import datetime


__MissingData__ = -32768.0
K = 273.15
station = 'Uccle'

# efile = open("errorfile_" + station + ".txt", "w")

# SensorType = 'SPC-6A'
VecP_ECC6A =    [    0,     2,     3,      5,    10,    20,    30,    50,   100,   200,   300,   500, 1000, 1100]
VecC_ECC6A_25 = [ 1.16,  1.16, 1.124,  1.087, 1.054, 1.033, 1.024, 1.015, 1.010, 1.007, 1.005, 1.002,    1,    1]
VecC_ECC6A_30 = [ 1.171, 1.171, 1.131, 1.092, 1.055, 1.032, 1.022, 1.015, 1.011, 1.008, 1.006, 1.004,    1,    1]

VecP_MAST = [     0,     3,     5,    10,    20,    30,    50,   100,   200,  1100]
VecC_MAST = [ 1.177, 1.177, 1.133, 1.088, 1.053, 1.037, 1.020, 1.004,     1,     1]

# SensorType = 'DMT-Z'
VecP_ECCZ = [   0,    3,     5,     7,    10,    15,    20,    30,    50,    70,    100,   150,   200, 1100]
VecC_ECCZ = [1.24, 1.24, 1.124, 1.087, 1.066, 1.048, 1.041, 1.029, 1.018, 1.013,  1.007, 1.002,     1,    1]



def o3tocurrent(df):
    # o3(mPa) = 4.3087 * 10e-4 * (i - ibg) * tp * t * cef * cref
    # tp: pump temp. in K, t: pumping time for 100 ml of air in seconds, cef: correction due to reduced ambient pressure for pump
    # cref: additional correction factor
    # i = o3 / (4.3087 * 10e-4 * tp * t * cef * cref ) + ibg

    ensci = (df.SensorType == 'DMT-Z') | (df.SensorType == 'ECC6Z')
    spc = df.SensorType == 'SPC-6A'

    df['Cef'] = ComputeCef(df)
    cref = 1
    df['ibg'] = 0

    df.loc[ensci, 'ibg'] = df.loc[ensci,'iB0']
    df.loc[ensci, 'CalibrationPressureCorrected'] = 1

    df.loc[spc, 'CalibrationPressureCorrected'] = ComputeCorP(df[spc], df.loc[spc, 'Pground'] )
    df.loc[spc, 'ibg'] = ComputeIBG(df[spc])
    # , 'CalibrationPressureCorrected'], df.loc[spc, 'Pair'], df.loc[spc, 'iB0'])
    df.loc[ensci,'I'] = df.loc[ensci,'O3'] / \
                                       (4.3087 * 10**(-4) * df.loc[ensci,'Tbox'] * df.loc[ensci, 'PF'] * df.loc[ensci,'Cef'] * cref) + df.loc[ensci,'ibg']


    return df

def ComputeCef(df):
    """ Computes pump efficiency correction factor based on pressure

        Arguments:
        Pressure -- air pressure [hPa]
    """
    spc = df.SensorType == 'SPC-6A'
    sol3 = df.SolutionVolume.astype(float) >= 2.75
    sol2 = df.SolutionVolume.astype(float) < 2.75
    ensci = (df.SensorType == 'DMT-Z') | (df.SensorType == 'ECC6Z')

    df.loc[(spc) & (sol3), 'Cef'] = \
        VecInterpolate(VecP_ECC6A, VecC_ECC6A_30, df.loc[(spc) & (sol3), 'Pair'], 0)
    df.loc[(spc) & (sol2), 'Cef'] = \
        VecInterpolate(VecP_ECC6A, VecC_ECC6A_25, df.loc[(spc) & (sol2),'Pair'], 0)
    df.loc[ensci,'Cef'] = VecInterpolate(VecP_ECCZ, VecC_ECCZ, df.loc[ensci,'Pair'], 0)

    return df.Cef


def VecInterpolate(XValues, YValues, dft, LOG):

    dft['Cef'] = 0

    i = 1
    ilast = len(XValues) - 1
    # return last value if xval out of xvalues range
    y = float(YValues[ilast])

    dft = dft.reset_index()

    for k in range(len(dft)):

        for i in range(len(XValues)-1):
            # just check that value is in between xvalues
            if (XValues[i] <= dft.at[k, 'Pair'] <= XValues[i + 1]):

                x1 = float(XValues[i])
                x2 = float(XValues[i+1])
                if LOG == 1:
                    x = math.log(x)
                    x1 = math.log(x1)
                    x2 = math.log(x2)

                y1 = float(YValues[i])
                y2 = float(YValues[i+1])
                dft.at[k,'Cef'] = y1 + (dft.at[k,'Pair'] - x1) * (y2 - y1) / (x2 - x1)
                dft.at[k,'y'] = y1 + (dft.at[k,'Pair'] - x1) * (y2 - y1) / (x2 - x1)
                # print(k, dft.at[k,'Pair'], y1 + (dft.at[k,'Pair'] - x1) * (y2 - y1) / (x2 - x1))

    return dft['Cef']

def ComputeIBG(df):
  """ Corrects background current value based on pressure

      Arguments:
      CalibrationPressureCorrected  -- corrected calibration pressure
                                      (with formula from function ComputeCorP)
      Pressure                      -- air pressure [hPa]
      iB0                            -- background current
  """
  df.Pcor = ComputeCorP(df, 'Pair') / ComputeCorP(df, 'Pground')
  df.IBG = df.Pcor*df.iB0

  return df.IBG


def ComputeCorP(df, Pressure):

  A0 = 0.0012250380415
  A1 = 0.000124111475632
  A2 = -0.00000002687066130
  df.CorP = A0 + A1*df[Pressure] + A2*df[Pressure]*df[Pressure]

  return df.CorP

def organize_df(df1, df2):


    df_out = pd.DataFrame()
    # print(list(df2))
    list1 = list(df1)
    for i in range(len(list1)):
        if (search('Temperature', list1[i])) and (search('inside', list1[i])):
            pump_temp = list1[i]
            df_out['Tbox'] = df1[pump_temp] + K
        if (search('Time', list1[i])) and (search('after', list1[i])):
            time = list1[i]
            df_out['Time'] = df1[time]
        if (search('Geopotential', list1[i])) and (search('height', list1[i])):
            height = list1[i]
            df_out['Height'] = df1[height]

    list2 = list(df2)
    for j in range(len(list2)):
        if (search('Background', list2[j])) and (search('end', list2[j])) and (search('pre-flight', list2[j])) :
            bkg = list2[j]
            df_out['BgCurrent'] = df2.at[df2.first_valid_index(), bkg]
            df_out['iB0'] = df2.at[df2.first_valid_index(), bkg]
            if(float(df2.at[df2.first_valid_index(), bkg]) > 1):
                # efile.write("background: " + str(df2.at[df2.first_valid_index(), bkg]) + filename  + '\n')
                print('background', df2.at[df2.first_valid_index(), bkg], filename)
                df_out['BgCurrent'] = 0.03
                df_out['iB0'] = 0.03
        if ((search('Sensor', list2[j])) and (search('air', list2[j])) and (search('flow', list2[j]))) and \
               not(search('calibrator', list2[j])):
            pumpt = list2[j]
            df_out['PF'] = df2.at[df2.first_valid_index(), pumpt]

            if (float(df2.at[df2.first_valid_index(), pumpt]) < 25) | (float(df2.at[df2.first_valid_index(), pumpt]) > 35):
                # efile.write("PF: " + str(df2.at[df2.first_valid_index(), pumpt]) + filename  + '\n')
                print('PF', df2.at[df2.first_valid_index(), pumpt], filename)
                df_out['PF'] = 29

        if (search('Ozone', list2[j])) and (search('sensor', list2[j])) :
            sensor = list2[j]
            df_out['SensorType'] = df2.at[df2.first_valid_index(), sensor]
            print(df2.at[df2.first_valid_index(), sensor])

        if not(search('Ozone', list2[j])) and (search('sensor', list2[j])) :
            try:
                df_out['SensorType'] = df2.at[df2.first_valid_index(), 'Ozone sensor type']
            except KeyError:
                df_out['SensorType'] = 'DMT-Z'


    df_out['Pair'] = df1['Pressure at observation (hPa)']
    df_out['O3'] = df1['Ozone partial pressure (mPa)']
    # df_out['Time'] = df1['Time after launch (s)']
    df_out['T'] = df1['Temperature (C)']
    df_out['U'] = df1['Relative humidity (%)']
    # df_out['Height'] = df1['Geopotential height (gpm)']
    df_out['Pground'] = df2.at[df2.first_valid_index(),'Background surface pressure (hPa)']
    if (float(df2.at[df2.first_valid_index(),'Background surface pressure (hPa)']) > 1200) | (float(df2.at[df2.first_valid_index(),'Background surface pressure (hPa)']) <900):
        # efile.write("Pground: " + str(df2.at[df2.first_valid_index(), 'Background surface pressure (hPa)']) + filename + '\n')
        print('Pground', df2.at[df2.first_valid_index(), 'Background surface pressure (hPa)'] )
        df_out['Pground'] = 1000


    df_out['SolutionVolume'] = df2.at[df2.first_valid_index(), 'Amount of cathode solution (cm3)']
    df_out['PF'] = df_out['PF'].astype('float')
    df_out['iB0'] = df_out['iB0'].astype('float')
    df_out['Cef'] = 1

    # try:
    # df_out['SensorType'] = df2.at[df2.first_valid_index(), 'Ozone sensor type']
    # except KeyError:
    #     df_out['SensorType'] = 'DMT-Z'


    return df_out




##read datafiles
allFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/" + station + "/*.csv"))
metaFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/" + station + "/metadata/*_md.csv"))

for filename, metafile in zip(allFiles, metaFiles):

    name = filename.split(".")[-2].split("/")[-1].split("uc")[1]
    date = datetime.strptime(name, '%y%m%d')
    datef = date.strftime('%Y%m%d')

    # if datef < "20070514": continue

    dfd = pd.read_csv(filename)
    if(len(dfd) < 300): continue
    dfm = pd.read_csv(metafile, index_col=0, names=['Parameter', 'Value'])
    dfm = dfm.T

    # print(filename.split(".")[-2].split("/")[-1])
    if (name == "080825") | (name == "080702") | (name == "080704") | (name == "190214"): continue
    print(filename)

    dfl = pd.DataFrame()
    dfl = organize_df(dfd, dfm)

    dfl = o3tocurrent(dfl)

    rawname = filename.split(".")[-2].split("/")[-1] + "_rawcurrent.csv"
    pname = filename.split(".")[-2].split("uc")[0]

    dfl.to_csv(pname + '/Current/' + rawname)

# efile.close()




