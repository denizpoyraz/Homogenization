import woudc_extcsv
from woudc_extcsv import Writer, WOUDCExtCSVReaderError, dump
from io import StringIO
from woudc_extcsv import load, WOUDCExtCSVReaderError
import pandas as pd
import glob


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


allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/Current/so160622*rawcurrent.hdf")

for filename in allFiles:

    print(filename)
    extcsv = woudc_extcsv.Writer(template=True)

    df = pd.read_hdf(filename)
    df = df[0:10]

    ps_field = 'iB0, iB2, SolutionVolume, SolutionConcentration, PumpFlowRate'
    df_names = 'iB0', 'iB2',  'SolutionVolume', 'SolutionConcentration', 'PF'
    # print(ps_field)
    preflight_summary = [df.at[df.first_valid_index(), i] for i in df_names ]
    # print(preflight_summary)

    preflight_summary = str(preflight_summary)[1:-1]
    extcsv.add_data('#PREFLIGHT_SUMMARY',   preflight_summary, field= ps_field)

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




