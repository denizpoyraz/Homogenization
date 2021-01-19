# Homogenization
first steps of the homogenization code
#### add a section to download woudc reader libraries
### Step 1) Download csv files for each date from the WOUDC data-server
Download_Data.py
### Step 2) Read these csv files and covert them to main and meta data csv files (2 seperate files)
SondeCSV_reader.py
### meta step 2) if needed read additional meta-data file provided by station
Madrid_MetaData.py
### Step 3) Homogenize the data-set using the metadata from WOUDC and if existss from the station
Homogenize_Madrid.py


