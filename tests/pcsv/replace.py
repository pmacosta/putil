# replace.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

# PyPI imports
import pytest
# Putil imports
import putil.misc
import putil.pcsv
import putil.test
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
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['a'],
                    'rfname':rfname,
                    'rdfilter':['b']
                },
                OSError,
                'File _dummy_file_ could not be found'
            )
            for item in file_items:
                ifname = item if not file_toggle else real_file
                rfname = real_file if not file_toggle else item
                putil.test.assert_exception(
                    putil.pcsv.replace,
                    {
                        'ifname':ifname,
                        'idfilter':['a'],
                        'rfname':rfname,
                        'rdfilter':['b']
                    },
                    RuntimeError,
                    'Argument `*[{0}]*` is not valid'.format(
                        'ifname' if not file_toggle else 'rfname'
                    )
                )
        with putil.misc.TmpFile(write_file_empty) as empty_file:
            with putil.misc.TmpFile(write_file) as real_file:
                ifname = empty_file if not file_toggle else real_file
                rfname = real_file if not file_toggle else empty_file
                putil.test.assert_exception(
                    putil.pcsv.replace,
                    {
                        'ifname':ifname,
                        'idfilter':['Ctrl'],
                        'rfname':rfname,
                        'rdfilter':['Ctrl']
                    },
                    RuntimeError,
                    r'File (.+) is empty'
                )
        with putil.misc.TmpFile(write_cols_not_unique) as nuniq_file:
            with putil.misc.TmpFile(write_file) as real_file:
                ifname = nuniq_file if not file_toggle else real_file
                rfname = real_file if not file_toggle else nuniq_file
                putil.test.assert_exception(
                    putil.pcsv.replace,
                    {
                        'ifname':ifname,
                        'idfilter':['Ctrl'],
                        'rfname':rfname,
                        'rdfilter':['Ctrl']
                    },
                    RuntimeError,
                    'Column headers are not unique in file (.+)'
                )
        # Filter-related exceptions
        with putil.misc.TmpFile(write_file) as ifname:
            with putil.misc.TmpFile(write_file) as rfname:
                for item in dfilter_items:
                    idfilter = item if not file_toggle else ['Ctrl']
                    rdfilter = ['Ctrl'] if not file_toggle else item
                    putil.test.assert_exception(
                        putil.pcsv.replace,
                        {
                            'ifname':ifname,
                            'idfilter':idfilter,
                            'rfname':rfname,
                            'rdfilter':rdfilter
                        },
                        RuntimeError,
                        'Argument `{0}` is not valid'.format(
                            'idfilter' if not file_toggle else 'rdfilter'
                        )
                    )
                item = (['Ctrl'], {'aaa':5})
                idfilter = item if not file_toggle else ['Ctrl']
                rdfilter = ['Ctrl'] if not file_toggle else item
                putil.test.assert_exception(
                    putil.pcsv.replace,
                    {
                        'ifname':ifname,
                        'idfilter':idfilter,
                        'rfname':rfname,
                        'rdfilter':rdfilter
                    },
                    ValueError,
                    'Column aaa not found'
                )
                # Columns-related exceptions
                idfilter = ['NoCol'] if not file_toggle else ['Ref']
                rdfilter = ['Ref'] if not file_toggle else ['NoCol']
                putil.test.assert_exception(
                    putil.pcsv.replace,
                    {
                        'ifname':ifname,
                        'idfilter':idfilter,
                        'rfname':rfname,
                        'rdfilter':rdfilter
                    },
                    ValueError,
                    'Column NoCol not found'
                )
                idfilter = ['0'] if not file_toggle else ['Ref']
                rdfilter = ['Ref'] if not file_toggle else ['0']
                putil.test.assert_exception(
                    putil.pcsv.replace,
                    {
                        'ifname':ifname,
                        'ihas_header':file_toggle,
                        'idfilter':idfilter,
                        'rfname':rfname,
                        'rdfilter':rdfilter,
                        'rhas_header':not file_toggle,
                    },
                    RuntimeError,
                    'Invalid column specification'
                )
    with putil.misc.TmpFile(write_file) as ifname:
        with putil.misc.TmpFile(write_file) as rfname:
            # Invalid row_start
            for item in ['a', True, -1]:
                for par in ['ifrow', 'rfrow']:
                    putil.test.assert_exception(
                        putil.pcsv.replace,
                        {
                            'ifname':ifname,
                            'idfilter':['Ctrl'],
                            'rfname':rfname,
                            'rdfilter':['Ctrl'],
                            par:item,
                        },
                        RuntimeError,
                        'Argument `{0}` is not valid'.format(par)
                    )
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['Ctrl'],
                    'rfname':rfname,
                    'rdfilter':['Ctrl'],
                    'ifrow':200,
                },
                RuntimeError,
                'File {0} has no valid data'.format(ifname)
            )
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['Ctrl'],
                    'rfname':rfname,
                    'rdfilter':['Ctrl'],
                    'rfrow':200,
                },
                RuntimeError,
                'File {0} has no valid data'.format(rfname)
            )
            # Column numbers are different
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['Ctrl'],
                    'rfname':rfname,
                    'rdfilter':['Ctrl', 'Ref'],
                },
                RuntimeError,
                'Number of input and replacement columns are different'
            )
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['Ctrl'],
                    'rfname':rfname,
                    'rdfilter':['Ref'],
                    'ocols':['a', 'b', 'c']
                },
                RuntimeError,
                'Number of input and output columns are different'
            )
    # Output file exceptions
    with putil.misc.TmpFile(write_file) as ifname:
        with putil.misc.TmpFile(write_file) as rfname:
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['Ctrl'],
                    'rfname':rfname,
                    'rdfilter':['Ref'],
                    'ofname':7
                },
                RuntimeError,
                'Argument `ofname` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['Ctrl'],
                    'rfname':rfname,
                    'rdfilter':['Ref'],
                    'ofname':'a_file\0'
                },
                RuntimeError,
                'Argument `ofname` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['Ctrl'],
                    'rfname':rfname,
                    'rdfilter':['Ref'],
                    'ofname':'some_file.csv',
                    'ocols':7
                },
                RuntimeError,
                'Argument `ocols` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['Ctrl'],
                    'rfname':rfname,
                    'rdfilter':['Ref'],
                    'ofname':'some_file.csv',
                    'ocols':['a', 'b', 5]
                },
                RuntimeError,
                'Argument `ocols` is not valid'
            )
    # Number of rows do not match
    with putil.misc.TmpFile(write_file) as ifname:
        with putil.misc.TmpFile(write_str_cols_file) as rfname:
            putil.test.assert_exception(
                putil.pcsv.replace,
                {
                    'ifname':ifname,
                    'idfilter':['Ctrl'],
                    'rfname':rfname,
                    'rdfilter':['Ref']
                },
                ValueError,
                'Number of rows mismatch between input and replacement data'
            )
