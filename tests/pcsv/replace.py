# replace.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

# Standard library imports
from itertools import product
# PyPI imports
import pytest
# Putil imports
import putil.misc
import putil.pcsv
from putil.test import AE, AI, RE
from tests.pcsv.fixtures import (
    common_exceptions,
    write_file,
    write_input_file,
    write_replacement_file,
    write_str_cols_file
)


###
# Test functions
###
def test_replace_function():
    """ Test replace function behavior """
    # One-column replacement
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.replace(fname1, fname2, ['Ref'], ['H4'])
            obj = putil.pcsv.CsvFile(fname=fname1)
            assert obj.header() == ['Ctrl', 'Ref', 'Data1', 'Data2']
            assert obj.data() == [
                ['nom', 4, 20, 30], ['high', 8, 40, 60], ['low', 12, 300, 3000]
            ]
    # Two-column replacement
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.replace(fname1, fname2, ['Data2', 'Ref'], ['H2', 'H4'])
            obj = putil.pcsv.CsvFile(fname=fname1)
            assert obj.header() == ['Ctrl', 'Ref', 'Data1', 'Data2']
            assert obj.data() == [
                ['nom', 4, 20, 2], ['high', 8, 40, 6], ['low', 12, 300, 10]
            ]
    # Two-column replacement with new column names of output file
    # "In place" replacement
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.replace(
                fname1, fname2,
                ['Data2', 'Ref'], ['H2', 'H4'],
                ocols=['New_A', 'New_B']
            )
            obj = putil.pcsv.CsvFile(fname=fname1)
            assert obj.header() == ['Ctrl', 'New_B', 'Data1', 'New_A']
            assert obj.data() == [
                ['nom', 4, 20, 2], ['high', 8, 40, 6], ['low', 12, 300, 10]
            ]
    # Two-column replacement with new column names of output file
    # Separate output file generated
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_input_file) as fname1:
            with putil.misc.TmpFile(write_replacement_file) as fname2:
                putil.pcsv.replace(
                    fname1, fname2,
                    ['Data2', 'Ref'], ['H3', 'H4'],
                    ofname=ofname, ocols=['New_C', 'New_D']
                )
        obj = putil.pcsv.CsvFile(fname=ofname)
        assert obj.header() == ['Ctrl', 'New_D', 'Data1', 'New_C']
        assert obj.data() == [
            ['nom', 4, 20, 3], ['high', 8, 40, 7], ['low', 12, 300, 11]
        ]
    # Input and replacement files row filtering
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_input_file) as fname1:
            with putil.misc.TmpFile(write_replacement_file) as fname2:
                putil.pcsv.replace(
                    fname1, fname2,
                    (['Data2', 'Ref'], {'Ref':[10, 30]}),
                    (['H3', 'H4'], {'H1':[1, 9]}),
                    ofname=ofname, ocols=['New_C', 'New_D']
                )
        obj = putil.pcsv.CsvFile(fname=ofname)
        assert obj.header() == ['Ctrl', 'New_D', 'Data1', 'New_C']
        assert obj.data() == [
            ['nom', 4, 20, 3], ['high', 20, 40, 60], ['low', 12, 300, 11]
        ]
    # No header option
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_input_file) as fname1:
            with putil.misc.TmpFile(write_replacement_file) as fname2:
                putil.pcsv.replace(
                    fname1, fname2,
                    ([3, 1], {1:[10, 30]}), ([2, 3], {0:[1, 9]}),
                    False, False,
                    ofname=ofname, ocols=['New_C', 'New_D']
                )
        obj = putil.pcsv.CsvFile(fname=ofname, has_header=False)
        assert obj.header() == [0, 1, 2, 3]
        assert obj.data() == [
            ['nom', 4, 20, 3], ['high', 20, 40, 60], ['low', 12, 300, 11]
        ]
    # Starting row
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.replace(
                fname1, fname2, ['Ref'], ['H4'], frow1=3, frow2=3
            )
            obj = putil.pcsv.CsvFile(fname=fname1)
            assert obj.header() == ['Ctrl', 'Ref', 'Data1', 'Data2']
            assert obj.data() == [['high', 8, 40, 60], ['low', 12, 300, 3000]]


@pytest.mark.replace
def test_replace_function_exceptions():
    """ Test replace function exceptions """
    # pylint: disable=R0914
    obj = putil.pcsv.replace
    common_exceptions(obj)
    dfilter = ['Ctrl']
    with putil.misc.TmpFile(write_file) as fname1:
        with putil.misc.TmpFile(write_file) as fname2:
            # Invalid row_start
            for item, par in product(['a', True, -1], ['frow1', 'frow2']):
                AI(obj, par, fname1, fname2, dfilter, dfilter, **{par:item})
            exmsg = 'File {0} has no valid data'.format(fname1)
            AE(obj, RE, exmsg, fname1, fname2, dfilter, dfilter, frow1=200)
            exmsg = 'File {0} has no valid data'.format(fname2)
            AE(obj, RE, exmsg, fname1, fname2, dfilter, dfilter, frow2=200)
            # Column numbers are different
            exmsg = 'Number of input and replacement columns are different'
            AE(obj, RE, exmsg, fname1, fname2, ['Ctrl'], ['Ctrl', 'Ref'])
            exmsg = 'Number of input and output columns are different'
            ocols = ['a', 'b', 'c']
            AE(obj, RE, exmsg, fname1, fname2, ['Ctrl'], ['Ref'], ocols=ocols)
    # Number of rows do not match
    exmsg = 'Number of rows mismatch between input and replacement data'
    with putil.misc.TmpFile(write_file) as fname1:
        with putil.misc.TmpFile(write_str_cols_file) as fname2:
            AE(obj, ValueError, exmsg, fname1, fname2, dfilter, ['Ref'])
