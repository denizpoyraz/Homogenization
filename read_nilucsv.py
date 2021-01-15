import pandas as pd
import glob
import math
import numpy as np
from re import search



__MissingData__ = -32768.0
k = 273.15


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

    df['Cef'] = ComputeCef(df)
    cref = 1
    df['ibg'] = 0

    df[df.SensorType == 'DMT-Z']['ibg'] = df.I0
    # df[df.SensorType != 'DMT-Z'].CalibrationPressureCorrected = ComputeCorP(df[df.SensorType != 'DMT-Z'], 'Pground')
    # df[df.SensorType != 'DMT-Z'].ibg = \
    #     ComputeIBG(df[df.SensorType != 'DMT-Z'].CalibrationPressureCorrected, df[df.SensorType != 'DMT-Z'].Pair, df[df.SensorType != 'DMT-Z'].I0)



    df[df.SensorType == 'DMT-Z'].IO3 = df[df.SensorType == 'DMT-Z'].PO3 / \
                                       (4.3087 * 10e-4 * df[df.SensorType == 'DMT-Z'].PumpTemp *
                                        df[df.SensorType == 'DMT-Z'].PumpTime * df[df.SensorType == 'DMT-Z'].Cef * cref) + df[df.SensorType == 'DMT-Z']['ibg']


def ComputeCef(df):
    """ Computes pump efficiency correction factor based on pressure

        Arguments:
        Pressure -- air pressure [hPa]
    """

    # df[(df.SensorType == 'SPC-6A') & (df.SolutionVolume > 2.75)].Cef = \
    #     VecInterpolate(VecP_ECC6A, VecC_ECC6A_30, df[(df.SensorType == 'SPC-6A') & (df.SolutionVolume > 2.75)].Pair, 0)
    # df[(df.SensorType == 'SPC-6A') & (df.SolutionVolume < 2.75)].Cef = \
    #     VecInterpolate(VecP_ECC6A, VecC_ECC6A_25, df[(df.SensorType == 'SPC-6A') & (df.SolutionVolume < 2.75)].Pair, 0)
    df[df.SensorType == 'DMT-Z'].Cef = VecInterpolate(VecP_ECCZ, VecC_ECCZ, df[df.SensorType == 'DMT-Z'], 0)

    return df.Cef


def VecInterpolate(XValues, YValues, dft, LOG):

    i = 1
    ilast = len(XValues) - 1
    # return last value if xval out of xvalues range
    y = float(YValues[ilast])

    for k in range(len(dft)):

        while i <= ilast:
            # just check that value is in between xvalues
            if (XValues[i - 1] <= dft.at[k, 'Pair'] <= XValues[i]) or (XValues[i] <= dft.at[k, 'Pair'] <= XValues[i - 1]):

                # dft.x = float(dft.Pair)
                x1 = float(XValues[i - 1])
                x2 = float(XValues[i])
                if LOG == 1:
                    x = math.log(x)
                    x1 = math.log(x1)
                    x2 = math.log(x2)

                y1 = float(YValues[i - 1])
                y2 = float(YValues[i])
                dft.at[k,'Cef'] = y1 + (dft.at[k,'Pair'] - x1) * (y2 - y1) / (x2 - x1)
                dft.at[k,'y'] = y1 + (dft.at[k,'Pair'] - x1) * (y2 - y1) / (x2 - x1)

                break
            i += 1
    return dft.Cef

def ComputeIBG(df):
  """ Corrects background current value based on pressure

      Arguments:
      CalibrationPressureCorrected  -- corrected calibration pressure
                                      (with formula from function ComputeCorP)
      Pressure                      -- air pressure [hPa]
      I0                            -- background current
  """

  df.Pcor = ComputeCorP(df, 'Pair') / ComputeCorP(df, 'Pground')
  df.IBG = df.Pcor*df.I0
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
            df_out['PumpTemp'] = df1[pump_temp]

    list2 = list(df2)
    for j in range(len(list2)):
        if (search('Background', list2[j])) and (search('end', list2[j])) and (search('pre-flight', list2[j])) :
            bkg = list2[j]
        if ((search('Sensor', list2[j])) and (search('air', list2[j])) and (search('flow', list2[j]))) and \
               not(search('calibrator', list2[j])):
            pumpt = list2[j]

    try:
        df_out['Pair'] = df1['Pressure at observation (hPa)']
        df_out['PO3'] = df1['Ozone partial pressure (mPa)']
        df_out['Pground'] = df2['Background surface pressure (hPa)']
        df_out['SolutionVolume'] = df2['Amount of cathode solution (cm3)']
        df_out['BgCurrent'] = df2[bkg]
        df_out['I0'] = df2[bkg]
        df_out['PumpTemp'] = df1[pump_temp]
        df_out['PumpTime'] = df2[pumpt]
        df_out['SensorType'] = df2['Ozone sensor type']
        df_out['Cef'] = 1

    except KeyError:
        df_out['SensorType'] = 'DMT-Z'
        df_out['Cef'] = 1


    return df_out


    #or
    #df['BgCurrent'] = df1['Background sensor current before cell is exposed to ozone (microamperes)']
    


station = 'Uccle'

##read datafiles
allFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/" + station + "/*.csv"))
metaFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/" + station + "/metadata/*_md.csv"))

c=0
for filename, metafile in zip(allFiles, metaFiles):

    dfd = pd.read_csv(filename)
    if(len(dfd) < 300): continue
    dfm = pd.read_csv(metafile, index_col=0, names=['Parameter', 'Value'])
    dfm = dfm.T

    # print(filename.split(".")[-2].split("/")[-1])
    if filename.split(".")[-2].split("/")[-1] == "uc080825": continue
    print(filename)

    # 'Amount of cathode solution (cm3)',
    # 'Concentration of cathode solution (g/l)',
    # 'Sensor air flow rate (calibrator and ozonesonde pumps operating) (sec/100cm^3)', ##none uccle
    # 'Sensor air flow rate (ozonesonde pump only operating) (sec/100cm^3)',
    # 'Background sensor current before cell is exposed to ozone (microamperes)', ##none uccle
    # 'Background sensor current in the end of the pre-flight calibration (microamperes)'
    # 'Pump correction table',
    # 'Background current correction method',
    # 'Ozone sensor type'



    dfl = pd.DataFrame()
    dfl = organize_df(dfd, dfm)


    dfl['IO3'] = o3tocurrent(dfl)

    rawname = filename.split(".")[-2].split("/")[-1] + "_rawcurrent.csv"
    pname = filename.split(".")[-2].split("uc")[0]
    # print(pname, rawname)
    dfl.to_csv(pname + '/Current/' + rawname)



