import csv
import numpy as np
from io import StringIO
from woudc_extcsv import load, WOUDCExtCSVReaderError
import pandas as pd
import glob

station = 'Madrid'
efile = open("errorfile_" + station + ".txt", "w")


# allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/" + station + "/19960219*csv")
allFiles = glob.glob("/home/poyraden/Analysis/Homogenization_Analysis/Files/" + station + "/CSV/*.csv")

list_data = []
list_udata = []
dfm = pd.DataFrame()
fi = 0


for filename in allFiles:

    print(filename)
    # try except is applied for the cases when there is formatting error: WOUDCExtCSVReaderError
    try:
        extcsv_to = load(filename)
        # access all tables
        tables = extcsv_to.sections.keys()
        ## first copy the profile data and delete this from the keys to save the metadata. For Praha data it is 'PORFILE',
        # watch out that this naming may change from station to station
        profile_keys = extcsv_to.sections['PROFILE'].keys()
        Profile = extcsv_to.sections['PROFILE']['_raw']
        del extcsv_to.sections['PROFILE']
        # Profile_uncertainity = extcsv_to.sections['PROFILE_UNCERTAINTY']['_raw']

    except WOUDCExtCSVReaderError:
        efile.write(filename  + '\n')
        tables = [0]

    ## this sections are the ozone profile data
    # del extcsv_to.sections['PROFILE_UNCERTAINTY']

    msize = len(tables)

    if msize == 1: continue

    for i in range(msize):
        dict = list(tables)[i]
        keys = extcsv_to.sections[dict].keys()
        ksize = len(keys)
        if ksize == 1:
            test = extcsv_to.sections[dict]['_raw']
            test_df = pd.read_csv(StringIO(test))
            tsize = len(test_df.columns)
            for t in range(tsize):
                cstr = test_df.columns.tolist()
                if(len(test_df) > 0):
                    dfm.at[fi, cstr[t]] = test_df.at[test_df.first_valid_index(),cstr[t]]
                if(len(test_df) == 0): continue

        for j in range(1, ksize):
            mstr = dict
            kstr = list(keys)[j]
            if kstr == '_raw': kstr = ""
            astr = mstr + '_' + kstr
            # print(fi, " , " , mstr, " , ", kstr , " , ", extcsv_to.sections[dict][list(keys)[j]])
            dfm.at[fi, astr] = extcsv_to.sections[dict][list(keys)[j]]

    #changes in the operation procedure
    # check this information from the data-sheets provided by the station
    # to be implemented by hand
###
    # dfm.at[fi,'SondeTypeChange'] = False
    # dfm.at[fi,'SSTChange'] = False
    # dfm.at[fi,'BkgCurrentChange'] = 'iB2toiB0_2003'
    # dfm.at[fi,'BkgCurrentCorrectionChange'] = 'AltDeptoConstant_2003'
    # dfm.at[fi,'PumpTempLocationChange'] = 'BoxtoHole_19970131'
    # dfm.at[fi,'PumpFlowMeasChange'] = False
    # dfm.at[fi,'PumpFlowEfficiencyChange'] = False
    # dfm.at[fi,'TONChange'] = 'DobsontoBrewer_2000'
    # dfm.at[fi,'RSChange'] = True
###

    dfprofile = StringIO(Profile)
    df = pd.read_csv(dfprofile)
    df['Date'] = dfm.at[fi, 'TIMESTAMP_Date']
    df['Station'] = dfm.at[fi, 'DATA_GENERATION_Agency']
    list_data.append(df)

    fi = fi + 1
    #
    # dfprofile_uncertainity = StringIO(Profile_uncertainity)
    # df_uncer = pd.read_csv(dfprofile_uncertainity)
    # list_udata.append(df_uncer)

efile.close()

dff = pd.concat(list_data,ignore_index=True)
# dfu = pd.concat(list_udata,ignore_index=True)

dff.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/DF_" + station + "_All.csv")
# dfu.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/DF_" + station + "_1996_unc.csv")
dfm.to_csv("/home/poyraden/Analysis/Homogenization_Analysis/Files/DF_" + station + "_All_metadata.csv")
