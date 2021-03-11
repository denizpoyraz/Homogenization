from dataclasses import dataclass
import re
import pandas as pd
from typing import List, Dict
from pathlib import Path

from utils import get_arguments

path = '/home/poyraden/Analysis/Homogenization_Analysis/Files/NDACC/ftp.cpc.ncep.noaa.gov/ndacc/station/sodanky/ames/o3sonde'


station = 'Sodankyl'

@dataclass
class Header:
    lines: int
    column_names: List[str]
    meta_data: Dict[str, float]


def convert_ozonedata(files: List[Path]) -> None:
    """Convert ozone data to hdf and csv files"""

    # Compile regular expressions
    regexp = compile_regexp()
    # regexp_den = compile_regexp_deniz()

    column_names_regexp = compile_column_names_regexp()

    # print(sorted(files))
    files = sorted(files)
    size = (len(files))
    datelist = [0]*size

    j = 0
    for file in files:
        print('file',file)
        tmp = file.name.split(".b")[0][2:8]
        fileout = file

        datelist[j] = tmp
        print(j)
        if(j > 0) and (j < (size-1)):
            if (datelist[j] == datelist[j-1]):
                # print(file)
                tmp = files[j].name.split(".b")[0] + "_2nd." + files[j].name.split(".")[1]
                fileout = str(files[j].parent) + "/" + tmp
                fileout = Path(fileout)
                print('zero', fileout)

        j = j+1

        with open(file, 'r', encoding='ISO-8859-1') as rfile:
            data = rfile.read()
        if len(data) < 1000: continue
        if file.name == 'le170517.b11' or file.name == 'le200903.b11' or file.name == 'nm030612.b11' or file.name == 'SO040714.Q12'\
                or file.name == 'so081203.q12': continue
        header = get_header(file, regexp, column_names_regexp)

        df = get_data(file, header)
        # Write data to hdf and metadata to csv
        constants = extract_constants_from_header(header.meta_data)
        dfm = extract_constants_from_header(header.meta_data)
        print('one',fileout)
        # pd.Series(constants).to_csv(file.with_suffix('.csv'), header=False)
        filename = str(fileout)
        print('two',filename)

        filenamecsv = filename.split(".b")[-2] + ('_md.csv')
        filenamehdf = filename.split(".b")[-2] + ('_md.hdf')
        # #
        # print(filenamehdf)
        pd.Series(constants).to_csv(filenamecsv, header=False)
        pd.Series(constants).to_hdf(filenamehdf, key = 'df')
        # print('fileout', fileout)
        df.to_hdf(fileout.with_suffix('.hdf'), key='df')
        df.to_csv(fileout.with_suffix('.csv'))



def get_header(p: Path, regexp, column_names_regexp) -> Header:
    """Return data contained in the header of the file"""
    with open(p, 'r', encoding='ISO-8859-1') as file:
        data = file.read()


    column_names = column_names_regexp.findall(data)
    match = regexp.search(data)
    position_data = match.span(2)[0]
    header_lines = data[0:position_data].count("\n")
    meta_data = match.groups()[0]

    return Header(header_lines, column_names, meta_data)


def get_data(file: Path, header: Header) -> pd.DataFrame:
    return (pd.read_csv(file,
                        delim_whitespace=True,
                        skiprows=header.lines,
                        names=header.column_names)
            ).dropna(axis=1)


def compile_column_names_regexp() -> re.Pattern:
    return re.compile(r'''
        ^[^\n]*\([^\s@]+\)
        ''', re.VERBOSE|re.MULTILINE)


def compile_regexp() -> re.Pattern:
    return re.compile(r'''
        ^[z\s]{2,}\n                        # z characters
        ([\s\S]+?)                          # Metadata
        (^[-\d\.\s]{1000,}$)                # Numbers separated by whitespace only
        ''', re.VERBOSE|re.MULTILINE)


def extract_constants_from_header(text: str) -> Dict[str, float]:
    pattern = re.compile(r'''
        (^[\s\S]+?)
        ^\d[\s\S]+?
        (^                                    # Numbers separated by whitespace only
          \s*\d{3}                             # Line starts with spaces (optional) then 3 digits (pressure levels)
          [^\n]                        # should not be a new line after 3 digits
          [-\d\.\s]{10,}
          [\s\S]*
        $)      
        ''', re.VERBOSE|re.MULTILINE)
    variables, values = pattern.search(text).groups()
    variables = variables.split("\n")
    variables = [v for v in variables if len(v) > 0]
    # print(len(variables), variables)
    values = values.split('\n')
    cleaned_values = []
    for v in values:
        # Remove leading spaces
        v = v.lstrip('File').lstrip()
        # print(v)
        if len(v) == 0:
            continue
        # don't split text values (contains any letter that is not E used in exponential numbers)
        if re.search('(?!e)(?!E)[a-zA-Z]', v):
            cleaned_values.append(v)
        else:
            cleaned_values.extend(v.split())
    constants = dict(zip(variables, cleaned_values))
    # df = pd.DataFrame([cleaned_values], columns=variables)
    return constants


if __name__ == "__main__":
    # Get the input files from the arguments
    files = get_arguments()
    convert_ozonedata(files)