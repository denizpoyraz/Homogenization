from pathlib import Path
from unittest import TestCase

from convert_ozonedata import compile_regexp, compile_column_names_regexp, get_header, get_data, \
    extract_constants_from_header


class TestOzoneDataConverter(TestCase):

    def setUp(self):
        self.files = [
            # Path.cwd() / 'data' / 'so191121.q12',
            # Path.cwd() / 'data' / 'uc181205.b11',
            Path.cwd() / 'data' / 'SO030507.Q12'

        ]

    def test_convert_ozonedata_runs(self):
        regexp = compile_regexp()
        column_names_regexp = compile_column_names_regexp()

        for file in self.files:
            header = get_header(file, regexp, column_names_regexp)
            df = get_data(file, header)
            constants = extract_constants_from_header(header.meta_data)

    def test_column_names(self):
        regexp = compile_regexp()
        column_names_regexp = compile_column_names_regexp()

        for file in self.files[0:1]:
            header = get_header(file, regexp, column_names_regexp)
            self.assertEqual(['Pressure at observation (hPa)', 'Time after launch (s)', 'Geopotential height (gmp)',
                              'Temperature (C)', 'Relative humidity (%)', 'Temperature inside styrofoam box (C)',
                              'Ozone partial pressure (mPa)', 'Horizontal wind direction (degrees)',
                              'Horizontal wind speed (m/s)'],
                             header.column_names[:9])
