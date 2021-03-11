import woudc_extcsv
from woudc_extcsv import Writer, WOUDCExtCSVReaderError, dump
from io import StringIO
from woudc_extcsv import load, WOUDCExtCSVReaderError
import pandas as pd
import glob
import numpy as np


#Table Name 	    Field (Column) Names (in order)
#PREFLIGHT_SUMMARY 	Ib0, ib1, ib2, SolutionType, SolutionVolume, PumpFlowRate, OzoneSondeResponseTime
#RADIOSONDE 	Manufacturer, Model, Number
#INTERFACE_CARD 	Manufacturer, Model, Number
#SAMPLING_METHOD 	TypeOzoneFreeAir, CorrectionWettingFlow, SurfaceOzone, DurationSurfaceOzoneExposure, LengthBG, WMOTropopausePressure, BurstOzonePressure, GroundEquipment, ProcessingSoftware
#PUMP_SETTINGS 	MotorCurrent, HeadPressure, VacuumPressure
#PUMP_CORRECTION 	Pressure, PumpCorrectionFactor
#FLIGHT_SUMMARY 	IntegratedO3, CorrectionCode, SondeTotalO3, NormalizationFactor, BackgroundCorrection, SampleTemperatureType
#OZONE_REFERENCE 	Name, Model, Number, Version, TotalO3, WLCode, ObsType, UTC_Mean
#PROFILE 	Duration, Pressure, O3PartialPressure, Temperature, WindSpeed, WindDirection, LevelCode, GPHeight, RelativeHumidity, SampleTemperature, SondeCurrent, PumpMotorCurrent, PumpMotorVoltage, Latitude, Longitude, Height
#PROFILE_UNCERTAINTY 	As in #PROFILE
#PRELAUNCH 	As in #PROFILE
#DESELECTED_DATA 	As in #PROFILE

# now read a metadata file or preapare a template to fill in the metadata
#     extcsv.add_data('CONTENT',   'WOUDC,Spectral,1.0,1', field='Class,Category,Level,Form')

def util_func(df, a):
    try:
        return df.at[df.first_valid_index(), a]
    except KeyError:
        return '9999'


allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/DQA/All/20201008*_all_dqa_rs80.hdf")

for filename in allFiles:

    print(filename)
    extcsv = woudc_extcsv.Writer(template=True)

    df = pd.read_hdf(filename)
    df = df[0:10]

    # PREFLIGHT_SUMMARY
    ps_field = 'iB0, iB2, SolutionVolume, SolutionConcentration, PumpFlowRate, OzoneSondeResponseTime'
    df_names = 'iB0', 'iB2',  'SolutionVolume', 'SolutionConcentration', 'PF', 'TimeResponse'
    preflight_summary = [util_func(df,i) for i in df_names]
    preflight_summary = str(preflight_summary)[1:-1]
    extcsv.add_data('PREFLIGHT_SUMMARY',   preflight_summary, field= ps_field)

    # RADIOSONDE
    rs_field = 'Manufacturer, Model, Number'
    df_names = 'RadiosondeModel', 'RadiosondeModel', 'RadiosondeSerial'
    rs_summary = [util_func(df,i) for i in df_names]
    rs_summary = str(rs_summary)[1:-1]
    extcsv.add_data('RADIOSONDE',   rs_summary, field= rs_field)

    # Interface
    int_field = 'Manufacturer, Model, Number'
    df_names = 'InterfaceModel', 'InterfaceModel', 'InterfaceSerial'
    int_summary = [util_func(df,i) for i in df_names]
    int_summary = str(int_summary)[1:-1]
    extcsv.add_data('INTERFACE',   int_summary, field= int_field)

    # SAMPLING_METHOD
    samp_field = 'TypeOzoneFreeAir, CorrectionWettingFlow, SurfaceOzone, DurationSurfaceOzoneExposure, LengthBG, ' \
                 'WMOTropopausePressure, BurstOzonePressure, GroundEquipment, ProcessingSoftware'
    df_names = 'TypeOzoneFreeAir', 'CorrectionWettingFlow', 'SurfaceOzone', 'DurationSurfaceOzoneExposure', 'LengthBG',  \
                 'WMOTropopausePressure', 'BurstOzonePressure', 'GroundEquipment', 'ProcessingSoftware'
    samp_summary = [util_func(df,i) for i in df_names]
    samp_summary = str(samp_summary)[1:-1]
    extcsv.add_data('SAMPLING_METHOD',   samp_summary, field= samp_field)

    # PUMP_SETTINGS
    pump_field = 'MotorCurrent, HeadPressure, VacuumPressure'
    df_names = 'MotorCurrent', 'HeadPressure', 'VacuumPressure'
    pump_summary = [util_func(df, i) for i in df_names]
    pump_summary = str(pump_summary)[1:-1]
    extcsv.add_data('PUMP_SETTINGS', pump_summary, field=pump_field)

    # PUMP_CORRECTION
    pval = np.array([1000, 100, 50, 30, 20, 10, 7, 5, 3])
    komhyr_86 = np.array([1, 1.007, 1.018, 1.022, 1.032, 1.055, 1.070, 1.092, 1.124])  # SP Komhyr
    komhyr_95 = np.array([1, 1.007, 1.018, 1.029, 1.041, 1.066, 1.087, 1.124, 1.241])  # ECC Komhyr
    corr = np.zeros(len(pval))
    if df.at[df.first_valid_index(),'SensorType'] == 'DMT-Z': corr = komhyr_95
    else: corr = komhyr_86
    correction = [str([x, y])[1:-1] for x, y in zip(pval[::-1], corr[::-1])]
    pumpcor_field = 'Pressure, Correction'
    # pumpcor_field = 'PumpPressure, PumpCorrectionFactor'
    for k in range(len(corr)):
        extcsv.add_data('#PUMP_CORRECTION',   correction[k], field= pumpcor_field)





    # PUMP_CORRECTION


    # FLIGHT_SUMMARY 	IntegratedO3, CorrectionCode, SondeTotalO3, NormalizationFactor, BackgroundCorrection,



    # PROFILE
    data_names = 'Duration, Height, Pressure, Temperature, Humidity, TemperatureSonde, O3PartialPressure, SondeCurrent'
    df_names = ['Time', 'Height','Pair', 'T', 'U',  'Tbox', 'O3',  'I']

    size = len(df)

    profile = [0] * size
    for k in range(size):
        profile[k] = df[df_names][k:k + 1].values[0]
        profile[k] = ",".join([str(i) for i in profile[k] if str(i)])
        extcsv.add_data('#PROFILE',   profile[k], field= data_names)



    out_name = '/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/WOUDC/' + str(df.at[df.first_valid_index(),'Date']) + '_testwoudc.csv'

    dump(extcsv, out_name)




