import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

from Homogenisation_Functions import po3tocurrent

## WOUDC data file
df = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/DF_Madrid_All.csv")

## WOUDC metadata file
dfm = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/DF_Madrid_All_metadata.csv")
dfm = dfm.sort_values('TIMESTAMP_Date')
dfm = dfm.reset_index()

## Excel metadata
dfme = pd.read_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Madrid/Madrid_1992-2020_MetaData.csv')
## reduced dfme, because excel metada goes back to 1992, while WOUDC starts from 1994
dfme = dfme[dfme.Datef2 >= '1994-12-01']
dfme = dfme.reset_index()

# there are some duplicated dates in the excel file, that for the moment first duplicated one is taken
duplicated_dates = dfme[dfme['Datef2'].duplicated()].Datef2.tolist()
print(duplicated_dates)
dfme = dfme.drop_duplicates('Datef2')

excel_date = dfme.Datef2.tolist()
woudc_date = dfm.TIMESTAMP_Date.tolist()
common_dates = list(set(excel_date).intersection(set(woudc_date)))
dfme = dfme[dfme['Datef2'].isin(common_dates)]
dfm = dfm[dfm['TIMESTAMP_Date'].isin(common_dates)]

## dates which are in excel date and not in woudc data and vice versa
extra_enw = [item for item in excel_date if item not in woudc_date] #in excel list but not in woudc
extra_wne = [item for item in woudc_date if item not in excel_date] # in woudc but not in excel list

print('dfme', list(dfme))
print('dfm', list(dfm))
print('df', list(df))

## now use df date to use each corresponding ib0 values
datelist = np.array(dfme.Datef2.tolist())
print(datelist[0:5])

dft = df[df.Date == '1994-12-14']
dft = dft.reset_index()
dft['etac'] = 1.0
dfmet = dfme[dfme.Datef2 =='1994-12-14']
pf = dfmet.at[dfmet.first_valid_index(),'PF']
dft['phip'] = 100. / pf
print('main', dfmet.at[dfmet.first_valid_index(),'iB2'])
dft['ib']  = np.float(dfmet.at[dfmet.first_valid_index(),'iB2'])


dft['IMc'] = po3tocurrent(dft,'O3PartialPressure', 'Pressure', 'SampleTemperature', 'ib', 'etac', 'phip', 'RS41', False)

# for d in range(len(datelist)):
#
#     df[df.Date == datelist[d]]['ib'] = dfme[dfme.Datef2 == datelist[d]].iB2
#     df[df.Date == datelist[d]]['etac'] = 1
#     df[df.Date == datelist[d]]['phip'] = 100 / dfme[dfme.Datef2 == datelist[d]].PF
#
#     df[df.Date == datelist[d]]['IMc'] = po3tocurrent(df[df.Date == datelist[d]],'O3PartialPressure', 'Pressure', 'SampleTemperature', 'ib', 'etac', 'phip', 'RS41', False  )
#     # print(df[df.Date == datelist[d]]['IMc'])
#
#     dft = df[df.Date == datelist[d]]
#     print(datelist[d], dft.at(dft.first_valid_index(),'IMc'))
# # po3tocurrent(df, o3, pair,  tpump, ib, etac, phip, pumpcorrectiontag, boolcorrection)


# df.to_cs()