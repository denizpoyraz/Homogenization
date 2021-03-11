import pandas as pd
import numpy as np
import re
from re import search
import glob
from datetime import datetime
import matplotlib.pyplot as plt

# from Homogenisation_Functions import po3tocurrent, absorption_efficiency, stoichemtry_conversion, conversion_efficiency, background_correction, \
#     pumptemp_corr, pf_efficiencycorrection, currenttopo3, pf_groundcorrection

station = 'Sodankyl'
k = 273.15

allFiles = sorted(glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/Current/*rawcurrent.csv"))

print(len(allFiles))

list_data = []
size = len(allFiles)
dates = np.zeros(size)

dfpl = pd.DataFrame()

i = 0
for filename in allFiles:

    file = open(filename, 'r')
    date_tmp = filename.split('/')[9].split('_')[0][2:8]
    # print(filename)
    date = datetime.strptime(date_tmp, '%y%m%d')
    # print(date)
    dfpl.at[i,'Date'] = date

    datef = date.strftime('%Y%m%d')
    # print(datef)
    df = pd.read_csv(filename)

    # print(datef)
    # if df.at[df.first_valid_index(),'iB0'] > 1: continue
    # if df.at[df.first_valid_index(),'iB2'] > 1: continue

    # if df.at[df.first_valid_index(),'TLab'] > 40: continue
    # if df.at[df.first_valid_index(),'TLab'] < 5: continue

    # if df.at[df.first_valid_index(),'iB2'] > 1: continue
    # Pground, TLab, ULab

    # dfpl.at[i,'iB0'] = df.at[df.first_valid_index(),'iB0']
    # dfpl.at[i,'iB2'] = df.at[df.first_valid_index(),'iB2']
    # dfpl.at[i,'PF'] = df.at[df.first_valid_index(),'PF']

    dfpl.at[i,'iB0'] = df.at[df.first_valid_index(),'ULab']
    dfpl.at[i,'iB2'] = df.at[df.first_valid_index(),'ULab']
    dfpl.at[i,'PF'] = df.at[df.first_valid_index(),'ULab']


    i = i+1

    # if i > 50: continue

# print('ib0', dfpl.iB0.median(), 'ib2', dfpl.iB2.median())
# print('ib0', dfpl.iB0.mean(), 'ib2', dfpl.iB2.mean())
# print('err', dfpl.iB0.mean() - dfpl.iB0.std(), dfpl.iB0.mean() + dfpl.iB0.std())

dfpl = dfpl.set_index('Date')

plt.close('all')
fig, ax = plt.subplots()

plt.fill_between(dfpl.index, dfpl.iB0.mean()-2 * dfpl.iB0.std(), dfpl.iB0.mean()+ 2 *dfpl.iB0.std(), facecolor='#1f77b4', alpha=.2, label = r"Mean$\pm$2sigma")

plt.plot(dfpl.index, dfpl.iB0,  label="ULab", linestyle = 'None', color = '#1f77b4',  marker="o", markersize = 3)
ax.axhline(y=dfpl.iB0.median(), color='grey', label = "Median ULab")
ax.axhline(y=dfpl.iB0.mean() + dfpl.iB0.std(), color='#1f77b4',linestyle='--', label = "Mean ULab + 1sigma")
ax.axhline(y=dfpl.iB0.mean(), color='#1f77b4', label = "Mean ULab")
ax.axhline(y=dfpl.iB0.mean() - dfpl.iB0.std(), color='#1f77b4',linestyle='--', label = "Mean ULab - 1sigma")


# plt.fill_between(dfpl.index, dfpl.iB2.mean()-2*dfpl.iB2.std(), dfpl.iB2.mean()+2*dfpl.iB2.std(), facecolor='#ff7f0e', alpha=.2,  label = r"Mean$\pm$2sigma")
#
# plt.plot(dfpl.index, dfpl.iB2, label="ULab", linestyle = 'None', color='#ff7f0e', marker="X", markersize = 3)
# ax.axhline(y=dfpl.iB2.median(), color='grey', label = "Median ULab")
#
# ax.axhline(y=dfpl.iB2.mean()+ dfpl.iB2.std(), color='#ff7f0e',linestyle='--', label = "Mean ULab + 1sigma")
# ax.axhline(y=dfpl.iB2.mean(), color='#ff7f0e', label = "Mean ULab")
# ax.axhline(y=dfpl.iB2.mean()- dfpl.iB2.std(), color='#ff7f0e',linestyle='--', label = "Mean ULab - 1sigma")
# #



# plt.fill_between(dfpl.index, dfpl.PF.mean()-2*dfpl.PF.std(), dfpl.PF.mean()+2*dfpl.PF.std(), facecolor='#1f77b4', alpha=.2, label = r"Mean$\pm$2sigma")
#
# plt.plot(dfpl.index, dfpl.PF,  label="PF", linestyle = 'None', color = '#1f77b4',  marker="o", markersize = 3)
# ax.axhline(y=dfpl.PF.median(), color='grey', label = "Median PF")
# ax.axhline(y=dfpl.PF.mean() + dfpl.PF.std(), color='#1f77b4',linestyle='--', label = "Mean PF + 1sigma")
#
# ax.axhline(y=dfpl.PF.mean(), color='#1f77b4', label = "Mean PF")
# ax.axhline(y=dfpl.PF.mean() - dfpl.PF.std(), color='#1f77b4',linestyle='--', label = "Mean PF - 1sigma")


plt.title('Sodankyla ULab values')
ax.legend(loc='best', frameon=True, fontsize='small')

plotname = 'ULab_timeseries'

plt.savefig('/home/poyraden/Analysis/Homogenization_Analysis/Plots/Sodankyl/' + plotname + '.pdf')
plt.savefig('/home/poyraden/Analysis/Homogenization_Analysis/Plots/Sodankyl/' + plotname + '.eps')
plt.savefig('/home/poyraden/Analysis/Homogenization_Analysis/Plots/Sodankyl/' + plotname + '.png')

plt.show()