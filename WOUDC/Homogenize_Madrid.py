import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

from Homogenisation_Functions import po3tocurrent, conversion_absorption, conversion_efficiency, background_correction

## WOUDC data file
df = pd.read_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/DF_Madrid_All.csv")
# df['O3PartialPressure'] = df['O3PartialPressure'].str.replace(':', '')
df.loc[(df['O3PartialPressure'] == '4:.090'), 'O3PartialPressure'] = '4.090'
df['O3PartialPressure'] = df['O3PartialPressure'].astype(float)
# df['imc'] = 0


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
dfme = dfme.fillna(dfme.mean())

## dates which are in excel date and not in woudc data and vice versa
extra_enw = [item for item in excel_date if item not in woudc_date] #in excel list but not in woudc
extra_wne = [item for item in woudc_date if item not in excel_date] # in woudc but not in excel list

print('dfme', list(dfme))
print('dfm', list(dfm))
print('df', list(df))

## now use df date to use each corresponding ib0 values
datelist = np.array(dfme.Datef2.tolist())

list_data = []

dft = {}
for d in range(len(datelist)):

    dft[d] = df[df.Date == datelist[d]]
    dft[d] = dft[d].reset_index()
    dfmet = dfme[dfme.Datef2 == datelist[d]]
    ##conversion efficiency
    dft[d]['alpha_o3'], dft[d]['alpha_unc'] = conversion_absorption(dft[d], 'Pressure', 3.0)
    dft[d]['etac_tmp'] = 1
    dft[d]['ib2_tmp'] = np.float(dfmet.at[dfmet.first_valid_index(), 'iB2'])
    dft[d]['phip'] = 100 / pf

    dft[d]['IMc'] = po3tocurrent(dft[d], 'O3PartialPressure', 'Pressure', 'SampleTemperature', 'ib2_tmp', 'etac_tmp', 'phip', 'RS41', False,'IMc')

    dft[d]['ib2'], dft[d]['unc_ib2'] = background_correction(dft[d],'ib2_tmp')
    dft[d]['etac'], dft[d]['unc_eta'] = conversion_efficiency(dft[d], 'alpha_o3', 'alpha_unc', 1, 1, False)


    # dft[d]['etac'] = 1
    pf = (dfmet.at[dfmet.first_valid_index(), 'PF'])
    dft[d]['phip'] = 100 / pf

    # dft[d]['IMc'] = po3tocurrent(dft[d], 'O3PartialPressure', 'Pressure', 'SampleTemperature', 'ib2', 'etac', 'phip', 'RS41', False,'IMc')

    list_data.append(dft[d])
    #  end of the allfiles loop    #

# Merging all the data files to df
dfn = pd.concat(list_data, ignore_index=True)


# po3tocurrent(df, o3, pair,  tpump, ib, etac, phip, pumpcorrectiontag, boolcorrection)

print('end list', list(dfn))

dfn.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/DF_Madrid_All_Homogonized.csv")
#
#
# df.to_cs()