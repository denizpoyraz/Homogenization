import csv
import numpy as np
from io import StringIO
from woudc_extcsv import load, WOUDCExtCSVReaderError
import pandas as pd
import glob

df = pd.read_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Uccle/UccleDataRaw.csv')

datelist = np.array(df.Datenf.tolist())

list_data = []
dft = {}

for d in range(len(datelist)):

    dft[d] = df[df.Date == datelist[d]]
    dft[d] = dft[d].reset_index()

