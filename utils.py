import argparse
import sys
from pathlib import Path
from typing import List


def get_arguments() -> List[Path]:
    """Get input file or directory from the command line argument,
    and create a list of input files"""

    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help='input docx file or directory')
    args = parser.parse_args()

    # Check input
    cwd = Path.cwd()
    input_path = cwd / args.input
    if input_path.is_file():
        if not is_ozone_data_file(input_path):
            print("Input file is not an ozone datafile, exiting.")
            sys.exit()
    elif not input_path.is_dir():
        print("Input is not a file or directory, exiting.")
        sys.exit()

    # Create list of files
    files = []
    if input_path.is_file():
        files.append(input_path)
    else:
        for f in input_path.glob('*'):
            if is_ozone_data_file(f):
                files.append(f)
    return files


def is_ozone_data_file(p: Path) -> bool:
    """Check if path looks like a correct input file"""
    return (p.is_file()) and (len(p.name) == 12) and (p.suffix not in ['.csv', '.hdf', '.b16','.b08'])
