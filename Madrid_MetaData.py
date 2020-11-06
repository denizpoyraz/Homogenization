import numpy as np
import pandas as pd

columnString = "Year DateTime O3ratio BrewO3 ResidO3 iB0 iB1 iB2 PF PumpT400hpa PumpT200hpa PumpT50hpa PumpT25hpa Psup O3STotal"
columnStr = columnString.split(" ")

dfmeta = pd.read_excel("/home/poyraden/Analysis/Homogenization_Analysis/Files/Madrid/Madrid_1992-2020__O3S-Madrid_Parameters.xls", skiprows = 1,names=columnStr)
# dfmeta = pd.read_excel("/home/poyraden/Analysis/Homogenization_Analysis/Files/Madrid/Madrid_2005-2019_O3S-Parameters.xls", sheet_name ='Parametros',
#                        header=None, names=columnStr )
# dfmeta = pd.read_excel("/home/poyraden/Analysis/Homogenization_Analysis/Files/Madrid/Madrid_2005-2019_O3S-Parameters.xls", sheet_name ='Parametros')

dfmeta['DateTime'] = dfmeta['DateTime'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d %H'))
dfmeta['Date'] = dfmeta['DateTime'].dt.strftime('%d/%m/%Y')
dfmeta['Datef2'] = dfmeta['DateTime'].dt.strftime('%Y-%m-%d')
dfmeta['iB2'] = dfmeta['iB2'].astype(float)
#
# for i in range(len(dfmeta)):
#     # dfmeta['iB2'] = dfmeta['iB2'].astype(float)
#     try:
#         dfmeta.at[i,'iB2'] = np.float(dfmeta.at[i,'iB2'])
#     except ValueError: print(i, dfmeta.at[i,'Datef2'], dfmeta.at[i,'iB2'])


# '2020-10-14'

dfmeta.to_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Madrid/Madrid_1992-2020_MetaData.csv')