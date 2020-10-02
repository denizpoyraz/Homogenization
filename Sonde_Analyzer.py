import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

df = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/DF_Praha_All.csv", low_memory=False)

dfm = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/DF_Praha_All_metadata.csv", low_memory=False)

print('DF ', list(df))
print('DF metada', list(dfm))

## start with the guidelines: with an example of Praha Data:

# Time series O3S-Parameters
# 1) Total ozone normalization: #FLIGHT_SUMMARY_CorrectionFactor# -> FLIGHT_SUMMARY_TotalO3 / FLIGHT_SUMMARY_SondeTotalO3
# 2) TOC by Brewer or Dobson: #FLIGHT_SUMMARY_TotalO3#
# 3) ROC above burst ?
# 4) Pump flow rate : #PumpFlowRate# , but what about the unit? is it PumpFlowRate or
# 5) Pump temperature in flight, SampleTemperature, and at launch and at Pair = 400, 200, 100, 50, 25hPa -> #SampleTemperature#

## example to clean NAN values
# result.loc[result['Ib0'].isnull(),'Ib0_is_NaN'] = 'Yes'
# result.loc[result['Ib0'].notnull(),'Ib0_is_NaN'] = 'No'

## conversion of pressure to Current
# what kind of corrections are available apart from the Pump Flow efficiency


# :param boolother: a boolean for if any other correction is applied

if(boolother == False):
    cur = 0.043085 * etac * phip/tpump  + ib

