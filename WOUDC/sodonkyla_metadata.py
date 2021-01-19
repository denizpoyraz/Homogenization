import numpy as np
import pandas as pd

columnString = "Filename LaunchTime SerialNumber FlowRate BkgCurrent"
columnStr = columnString.split(" ")

dfmeta = pd.read_excel("/home/poyraden/Analysis/Homogenization_Analysis/O3S-DQA2/Sodankyla_FMI/table.xls", skiprows = 1,names=columnStr)

# dfmeta['Date'] = \
print(str(dfmeta.at[0,'Filename']).split('.')[0][2:])
      # ).split('.')[2:])