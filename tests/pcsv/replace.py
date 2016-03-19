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
from tests.pcsv.files import (
    write_cols_not_unique,
    write_file,
    write_file_empty,
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
    with putil.misc.TmpFile(write_input_file) as ifname:
        with putil.misc.TmpFile(write_replacement_file) as rfname:
            putil.pcsv.replace(ifname, ['Ref'], rfname, ['H4'])
            obj = putil.pcsv.CsvFile(fname=ifname)
            assert obj.header() == ['Ctrl', 'Ref', 'Data1', 'Data2']
            assert obj.data() == [
                ['nom', 4, 20, 30],
                ['high', 8, 40, 60],
                ['low', 12, 300, 3000],
            ]
    # Two-column replacement
    with putil.misc.TmpFile(write_input_file) as ifname:
        with putil.misc.TmpFile(write_replacement_file) as rfname:
            putil.pcsv.replace(
                ifname, ['Data2', 'Ref'], rfname, ['H2', 'H4']
            )
            obj = putil.pcsv.CsvFile(fname=ifname)
            assert obj.header() == ['Ctrl', 'Ref', 'Data1', 'Data2']
            assert obj.data() == [
                ['nom', 4, 20, 2],
                ['high', 8, 40, 6],
                ['low', 12, 300, 10],
            ]
    # Two-column replacement with new column names of output file
    # "In place" replacement
    with putil.misc.TmpFile(write_input_file) as ifname:
        with putil.misc.TmpFile(write_replacement_file) as rfname:
            putil.pcsv.replace(
                ifname,
                ['Data2', 'Ref'],
                rfname,
                ['H2', 'H4'],
                ocols=['New_A', 'New_B']
            )
            obj = putil.pcsv.CsvFile(fname=ifname)
            assert obj.header() == ['Ctrl', 'New_B', 'Data1', 'New_A']
            assert obj.data() == [
                ['nom', 4, 20, 2],
                ['high', 8, 40, 6],
                ['low', 12, 300, 10],
            ]
    # Two-column replacement with new column names of output file
    # Separate output file generated
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_input_file) as ifname:
            with putil.misc.TmpFile(write_replacement_file) as rfname:
                putil.pcsv.replace(
                    ifname,
                    ['Data2', 'Ref'],
                    rfname,
                    ['H3', 'H4'],
                    ofname=ofname,
                    ocols=['New_C', 'New_D']
                )
        obj = putil.pcsv.CsvFile(fname=ofname)
        assert obj.header() == ['Ctrl', 'New_D', 'Data1', 'New_C']
        assert obj.data() == [
            ['nom', 4, 20, 3],
            ['high', 8, 40, 7],
            ['low', 12, 300, 11],
        ]
    # Input and replacement files row filtering
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_input_file) as ifname:
            with putil.misc.TmpFile(write_replacement_file) as rfname:
                putil.pcsv.replace(
                    ifname,
                    (['Data2', 'Ref'], {'Ref':[10, 30]}),
                    rfname,
                    (['H3', 'H4'], {'H1':[1, 9]}),
                    ofname=ofname,
                    ocols=['New_C', 'New_D']
                )
        obj = putil.pcsv.CsvFile(fname=ofname)
        assert obj.header() == ['Ctrl', 'New_D', 'Data1', 'New_C']
        assert obj.data() == [
            ['nom', 4, 20, 3],
            ['high', 20, 40, 60],
            ['low', 12, 300, 11],
        ]
    # No header option
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_input_file) as ifname:
            with putil.misc.TmpFile(write_replacement_file) as rfname:
                putil.pcsv.replace(
                    ifname,
                    ([3, 1], {1:[10, 30]}),
                    rfname,
                    ([2, 3], {0:[1, 9]}),
                    ihas_header=False,
                    rhas_header=False,
                    ofname=ofname,
                    ocols=['New_C', 'New_D']
                )
        obj = putil.pcsv.CsvFile(fname=ofname, has_header=False)
        assert obj.header() == [0, 1, 2, 3]
        assert obj.data() == [
            ['nom', 4, 20, 3],
            ['high', 20, 40, 60],
            ['low', 12, 300, 11],
        ]
    # Starting row
    with putil.misc.TmpFile(write_input_file) as ifname:
        with putil.misc.TmpFile(write_replacement_file) as rfname:
            putil.pcsv.replace(
                ifname, ['Ref'], rfname, ['H4'], ifrow=3, rfrow=3)
            obj = putil.pcsv.CsvFile(fname=ifname)
            assert obj.header() == ['Ctrl', 'Ref', 'Data1', 'Data2']
            assert obj.data() == [
                ['high', 8, 40, 60],
                ['low', 12, 300, 3000],
            ]


@pytest.mark.replace
def test_replace_function_exceptions():
    """ Test replace function exceptions """
    # pylint: disable=R0914
    obj = putil.pcsv.replace
    # Input file exceptions
    file_items = [5, 'some_file\0']
    dfilter_items = [
        True,
        ['a', True],
        (['Ctrl'], 'a'),
        (['Ctrl'], {}),
        ({5:True}, ['Ctrl']),
        ({'a':{'xx':2}}, ['Ctrl']),
        (['Ctrl'], {'a':[3, {'xx':2}]})
    ]
    for file_toggle in [False, True]:
        # File-related tests
        with putil.misc.TmpFile(write_file) as real_file:
            ifname = '_dummy_file_' if not file_toggle else real_file
            rfname = real_file if not file_toggle else '_dummy_file_'
            exmsg = 'File _dummy_file_ could not be found'
            AE(obj, OSError, exmsg, ifname, ['a'], rfname, ['b'])
            for item in file_items:
                ifname = item if not file_toggle else real_file
                rfname = real_file if not file_toggle else item
                par = 'ifname' if not file_toggle else 'rfname'
                AI(obj, par, ifname, ['a'], rfname, ['b'])
        dfilter = ['Ctrl']
        with putil.misc.TmpFile(write_file_empty) as empty_file:
            with putil.misc.TmpFile(write_file) as real_file:
                ifname = empty_file if not file_toggle else real_file
                rfname = real_file if not file_toggle else empty_file
                exmsg = r'File (.+) is empty'
                AE(obj, RE, exmsg, ifname, dfilter, rfname, dfilter)
        with putil.misc.TmpFile(write_cols_not_unique) as nuniq_file:
            with putil.misc.TmpFile(write_file) as real_file:
                ifname = nuniq_file if not file_toggle else real_file
                rfname = real_file if not file_toggle else nuniq_file
                exmsg = 'Column headers are not unique in file (.+)'
                AE(obj, RE, exmsg, ifname, dfilter, rfname, dfilter)
        # Filter-related exceptions
        with putil.misc.TmpFile(write_file) as ifname:
            with putil.misc.TmpFile(write_file) as rfname:
                for item in dfilter_items:
                    idfilter = item if not file_toggle else ['Ctrl']
                    rdfilter = ['Ctrl'] if not file_toggle else item
                    par = 'idfilter' if not file_toggle else 'rdfilter'
                    AI(obj, par, ifname, idfilter, rfname, rdfilter)
                item = (['Ctrl'], {'aaa':5})
                idfilter = item if not file_toggle else ['Ctrl']
                rdfilter = ['Ctrl'] if not file_toggle else item
                exmsg = 'Column aaa not found'
                AE(obj, ValueError, exmsg, ifname, idfilter, rfname, rdfilter)
                # Columns-related exceptions
                idfilter = ['NoCol'] if not file_toggle else ['Ref']
                rdfilter = ['Ref'] if not file_toggle else ['NoCol']
                exmsg = 'Column NoCol not found'
                AE(obj, ValueError, exmsg, ifname, idfilter, rfname, rdfilter)
                idfilter = ['0'] if not file_toggle else ['Ref']
                rdfilter = ['Ref'] if not file_toggle else ['0']
                exmsg = 'Invalid column specification'
                AE(
                    obj, RE, exmsg,
                    ifname, idfilter,
                    rfname, rdfilter,
                    ihas_header=file_toggle, rhas_header=not file_toggle
                )
    with putil.misc.TmpFile(write_file) as ifname:
        with putil.misc.TmpFile(write_file) as rfname:
            # Invalid row_start
            for item, par in product(['a', True, -1], ['ifrow', 'rfrow']):
                AI(obj, par, ifname, dfilter, rfname, dfilter, **{par:item})
            exmsg = 'File {0} has no valid data'.format(ifname)
            AE(obj, RE, exmsg, ifname, dfilter, rfname, dfilter, ifrow=200)
            exmsg = 'File {0} has no valid data'.format(rfname)
            AE(obj, RE, exmsg, ifname, dfilter, rfname, dfilter, rfrow=200)
            # Column numbers are different
            exmsg = 'Number of input and replacement columns are different'
            AE(obj, RE, exmsg, ifname, ['Ctrl'], rfname, ['Ctrl', 'Ref'])
            exmsg = 'Number of input and output columns are different'
            ocols = ['a', 'b', 'c']
            AE(obj, RE, exmsg, ifname, ['Ctrl'], rfname, ['Ref'], ocols=ocols)
    # Output file exceptions
    with putil.misc.TmpFile(write_file) as ifname:
        with putil.misc.TmpFile(write_file) as rfname:
            par = 'ofname'
            for item in [7, 'a_file\0']:
                AI(obj, par, ifname, dfilter, rfname, ['Ref'], ofname=item)
            fname = 'some_file.csv'
            for item in [7, ['a', 'b', 5]]:
                AI(
                    obj, 'ocols', ifname, dfilter, rfname, ['Ref'],
                    ofname=fname, ocols=item
                )
    # Number of rows do not match
    exmsg = 'Number of rows mismatch between input and replacement data'
    with putil.misc.TmpFile(write_file) as ifname:
        with putil.misc.TmpFile(write_str_cols_file) as rfname:
            AE(obj, ValueError, exmsg, ifname, dfilter, rfname, ['Ref'])
