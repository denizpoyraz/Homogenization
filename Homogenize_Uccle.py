import csv
import numpy as np
from io import StringIO
from woudc_extcsv import load, WOUDCExtCSVReaderError
import pandas as pd
import glob

station = 'Uccle'

allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/" + station + "/raw/*raw.txt")

list_data = []

columnString = "Time P T U Height O3 Tbox I Winddir Windv"
columnStr = columnString.split(" ")


for filename in allFiles:

    df = pd.read_csv(filename, sep = "\s *", engine="python", skiprows=1, names=columnStr)

    list_data.append(df)

df = pd.concat(list_data,ignore_index=True)



df.to_csv("/home/poyraden/Analysis/Uccle_Deconvolution/Files/UccleData.csv")