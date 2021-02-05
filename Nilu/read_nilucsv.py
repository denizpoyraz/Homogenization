import pandas as pd
import glob
import math
import numpy as np
from re import search
from datetime import datetime


__MissingData__ = -32768.0
K = 273.15
station = 'Sodankyl'
# station = 'Uccle'

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
            df_out['iB2'] = df2.at[df2.first_valid_index(), bkg]

            # if(float(df2.at[df2.first_valid_index(), bkg]) > 0.1):
            #     # efile.write("background: " + str(df2.at[df2.first_valid_index(), bkg]) + filename  + '\n')
            #     print('background', df2.at[df2.first_valid_index(), bkg], filename)
            #     df_out['iB2'] = 0.03

        if (search('Background', list2[j])) and (search('before', list2[j])) and (search('exposed', list2[j])) :
            bkg = list2[j]
            df_out['iB0'] = df2.at[df2.first_valid_index(), bkg]

            # if(float(df2.at[df2.first_valid_index(), bkg]) > 0.1):
            #     print('background', df2.at[df2.first_valid_index(), bkg], filename)
            #     df_out['iB0'] = 0.03

        if ((search('Sensor', list2[j])) and (search('air', list2[j])) and (search('flow', list2[j]))) and \
               not(search('calibrator', list2[j])):
            pumpt = list2[j]
            df_out['PF'] = df2.at[df2.first_valid_index(), pumpt]

            if (float(df2.at[df2.first_valid_index(), pumpt]) < 20) | (float(df2.at[df2.first_valid_index(), pumpt]) > 40):
                # efile.write("PF: " + str(df2.at[df2.first_valid_index(), pumpt]) + filename  + '\n')
                df_out['PF'] = 29

        if (search('Ozone', list2[j])) and (search('sensor', list2[j])):
            sensor = list2[j]
            df_out['SensorType'] = df2.at[df2.first_valid_index(), sensor]

        if not((search('Ozone', list2[j])) and (search('sensor', list2[j]))) and (search('Serial number of ECC', list2[j])) :
            serial = list2[j]
            df_out['SerialECC'] = df2.at[df2.first_valid_index(), serial]
            if (df2.at[df2.first_valid_index(), serial][0] == "z") | (df2.at[df2.first_valid_index(), serial][0] == "Z")\
                    | (df2.at[df2.first_valid_index(), serial][1] == "Z") | (df2.at[df2.first_valid_index(), serial][1] == "z"):
                df_out['SensorType'] = 'DMT-Z'
            if (df2.at[df2.first_valid_index(), serial][0] == "4"): df_out['SensorType'] = 'SPC-4A'
            if (df2.at[df2.first_valid_index(), serial][0] == "5"): df_out['SensorType'] = 'SPC-5A'
            if (df2.at[df2.first_valid_index(), serial][0] == "6"): df_out['SensorType'] = 'SPC-6A'


        if (search('Background', list2[j])) and (search('surface pressure', list2[j])):
            pground = list2[j]
            df_out['Pground'] = df2.at[df2.first_valid_index(), pground]
            if (float(df2.at[df2.first_valid_index(), pground]) > 1090) | (
                    float(df2.at[df2.first_valid_index(), pground]) < 900):
                # efile.write("Pground: " + str(df2.at[df2.first_valid_index(), 'Background surface pressure (hPa)']) + filename + '\n')
                df_out['Pground'] = 1000

        if (search('Amount', list2[j])) and (search('cathode', list2[j])):
            cathodesol = list2[j]
            df_out['SolutionVolume'] = df2.at[df2.first_valid_index(), cathodesol]

        if (search('Concentration', list2[j])) and (search('cathode', list2[j])):
            cathodecon = list2[j]
            df_out['SolutionConcentration'] = df2.at[df2.first_valid_index(), cathodecon]

        if (search('Place', list2[j])) and (search('box', list2[j])) and (search('measurement', list2[j])):
            pt_location = list2[j]
            df_out['PumpTempLoc'] = df2.at[df2.first_valid_index(), pt_location]

        if (search('Temperature', list2[j])) and (search('laboratory', list2[j])) and (search('during', list2[j])) and (search('sonde', list2[j])) :
            t_lab = list2[j]
            df_out['TLab'] = df2.at[df2.first_valid_index(), t_lab]

        if (search('Relative humidity', list2[j])) and (search('laboratory', list2[j])) and (search('during', list2[j])) and (search('sonde', list2[j])) :
            u_lab = list2[j]
            df_out['ULab'] = df2.at[df2.first_valid_index(), u_lab]

        if (search('Pump', list2[j])) and (search('correction', list2[j])) and (
        search('table', list2[j])):
            pump_table = list2[j]
            df_out['PumpTable'] = df2.at[df2.first_valid_index(), pump_table]

    df_out['Pair'] = df1['Pressure at observation (hPa)']
    df_out['O3'] = df1['Ozone partial pressure (mPa)']
    df_out['T'] = df1['Temperature (C)']
    df_out['U'] = df1['Relative humidity (%)']
    df_out['PF'] = df_out['PF'].astype('float')
    df_out['iB0'] = df_out['iB0'].astype('float')
    df_out['iB2'] = df_out['iB2'].astype('float')
    df_out['Cef'] = 1

    return df_out


def o3tocurrent(dft):
    # o3(mPa) = 4.3087 * 10e-4 * (i - ibg) * tp * t * cef * cref
    # tp: pump temp. in K, t: pumping time for 100 ml of air in seconds, cef: correction due to reduced ambient pressure for pump
    # cref: additional correction factor
    # i = o3 / (4.3087 * 10e-4 * tp * t * cef * cref ) + ibg

    # ensci = (dft.SensorType == 'DMT-Z') | (dft.SensorType == 'ECC6Z')
    # spc = dft.SensorType == 'SPC-6A'

    sensortype = dft.at[dft.first_valid_index(), 'SensorType']

    spctag4A = (search('SPC', sensortype)) or (search('4A', sensortype))
    if spctag4A: dft['SensorType'] = 'SPC-4A'
    spctag5A = (search('SPC', sensortype)) or (search('5A', sensortype))
    if spctag5A: dft['SensorType'] = 'SPC-5A'
    spctag6A = (search('SPC', sensortype)) or (search('6A', sensortype))
    if spctag6A: dft['SensorType'] = 'SPC-6A'

    enscitag = (search('DMT-Z', sensortype)) or (search('Z', sensortype)) or (search('ECC6Z', sensortype)) or (
        search('_Z', sensortype))
    if enscitag: dft['SensorType'] = 'DMT-Z'

    ensci = (dft.SensorType == 'DMT-Z')
    spc = (dft.SensorType == 'SPC') | (dft.SensorType == 'SPC-4A') | (dft.SensorType == 'SPC-5A') | (dft.SensorType == 'SPC-6A')

    dft['Cef'] = ComputeCef(dft)
    cref = 1
    dft['ibg'] = 0
    dft['Pcor'] = 0

    dft.loc[ensci, 'ibg'] = dft.loc[ensci,'iB2']
    dft.loc[spc,'ibg'] = ComputeIBG(dft[spc])

    dft.loc[ensci,'I'] = dft.loc[ensci,'O3'] / \
                                       (4.3087 * 10**(-4) * dft.loc[ensci,'Tbox'] * dft.loc[ensci, 'PF'] * dft.loc[ensci,'Cef'] * cref) + dft.loc[ensci,'ibg']
    dft.loc[spc, 'I'] = dft.loc[spc, 'O3'] / \
                          (4.3087 * 10 ** (-4) * dft.loc[spc, 'Tbox'] * dft.loc[spc, 'PF'] * dft.loc[
                              spc, 'Cef'] * cref) + dft.loc[spc, 'ibg']


    return dft

def ComputeCef(dft):
    """ Computes pump efficiency correction factor based on pressure

        Arguments:
        Pressure -- air pressure [hPa]
    """
    sensortype = dft.at[dft.first_valid_index(),'SensorType']

    # print('sensortype', sensortype)

    spctag = (search('SPC', sensortype)) or (search('6A', sensortype)) or (search('5A', sensortype)) or (search('4A', sensortype))
    if spctag: dft['SensorType'] = 'SPC'
    enscitag = (search('DMT-Z', sensortype)) or (search('Z', sensortype)) or (search('ECC6Z', sensortype)) or (search('_Z', sensortype))
    if enscitag: dft['SensorType'] = 'DMT-Z'

    sol3 = dft.SolutionVolume.astype(float) >= 2.75
    sol2 = dft.SolutionVolume.astype(float) < 2.75
    ensci = (dft.SensorType == 'DMT-Z')
    spc = (dft.SensorType == 'SPC')

    dft.loc[(spc) & (sol3), 'Cef'] = \
        VecInterpolate(VecP_ECC6A, VecC_ECC6A_30, dft.loc[(spc) & (sol3), 'Pair'], 0)
    dft.loc[(spc) & (sol2), 'Cef'] = \
        VecInterpolate(VecP_ECC6A, VecC_ECC6A_25, dft.loc[(spc) & (sol2),'Pair'], 0)
    dft.loc[ensci,'Cef'] = VecInterpolate(VecP_ECCZ, VecC_ECCZ, dft.loc[ensci,'Pair'], 0)

    return dft.Cef

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

def ComputeIBG(dft):
  """ Corrects background current value based on pressure

      Arguments:
      CalibrationPressureCorrected  -- corrected calibration pressure
                                      (with formula from function ComputeCorP)
      Pressure                      -- air pressure [hPa]
      iB0                            -- background current
  """
  dft.Pcor = ComputeCorP(dft, 'Pair') / ComputeCorP(dft, 'Pground')
  dft.ibg = dft.Pcor*dft.iB2

  return dft.ibg


def ComputeCorP(dft, Pressure):

  A0 = 0.0012250380415
  A1 = 0.000124111475632
  A2 = -0.00000002687066130
  dft.CorP = A0 + A1*dft[Pressure].astype('float') + A2*dft[Pressure].astype('float')*dft[Pressure].astype('float')

  return dft.CorP


##read datafiles
allFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/" + station + "/*.csv"))
metaFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/" + station + "/metadata/*_md.csv"))

list_data = []

for filename in (allFiles):

    name = filename.split(".")[-2].split("/")[-1][2:8]
    fname = filename.split(".")[-2].split("/")[-1]
    print(fname)

    metafile = '/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/metadata/' + fname + "_md.csv"
    # metafile = '/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Uccle/metadata/' + fname + "_md.csv"

    date = datetime.strptime(name, '%y%m%d')
    datef = date.strftime('%Y%m%d')

    # if datef < "20070514": continue

    dfd = pd.read_csv(filename)
    if(len(dfd) < 300): continue
    if len(dfd.columns) < 8: continue
    try:
        dfm = pd.read_csv(metafile, index_col=0, names=['Parameter', 'Value'])
        if (len(dfm)) < 15:
            print('skip this dataset for now, use the mean of everything later')
            continue
    except FileNotFoundError:
        print(metafile)
        continue

    dfm = dfm.T
    dfm['Date'] = datef

    # # print(filename.split(".")[-2].split("/")[-1])
    # # if (name == "080825") | (name == "080702") | (name == "080704") | (name == "190214"): continue
    # if (name == "021127") | (name == "080702") | (name == "080704") | (name == "190214"): continue
    #
    # # print('two', name)
    #
    # dfl = pd.DataFrame()
    # dfl = organize_df(dfd, dfm)
    # # print('three', name)
    # dfl = o3tocurrent(dfl)
    # # print('four', name)
    # if np.isnan(dfl.at[dfl.first_valid_index(),'I']): print(dfl.at[dfl.first_valid_index(),'SensorType'])
    #
    # rawname = filename.split(".")[-2].split("/")[-1] + "_rawcurrent.csv"
    # pname = filename.split(".")[-2].split("s")[0]
    pname = '/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/'
    # pname = '/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Uccle/'

    # print(rawname)
    #
    # dfl.to_csv(pname + '/Current/' + rawname)

    list_data.append(dfm)

# efile.close()


dff = pd.concat(list_data,ignore_index=True)
hdfall = pname + "All_metedata.hdf"

dff.to_hdf(hdfall, key = 'df')

