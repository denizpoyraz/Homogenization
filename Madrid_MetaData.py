import numpy as np
import pandas as pd

dfmeta = pd.read_excel("/home/poyraden/Analysis/Homogenization_Analysis/Files/Madrid/Madrid_2005-2019_O3S-Parameters.xls")

dfmeta.to_csv('/home/poyraden/Analysis/Homogenization_Analysis/Files/Madrid/Madrid_2005-2019_MetaData.csv')