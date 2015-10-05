# merge.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

import pytest
import tempfile

import putil.pcsv
import putil.test
from tests.pcsv.files import (
    write_cols_not_unique,
    write_file,
    write_file_empty,
    write_input_file,
    write_replacement_file
)


###
# Test functions
###
def test_merge():
    """ Test merge function behavior """
    # In place replacement
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(fname1, fname2)
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert (
        obj.header()
        ==
        ['Ctrl', 'Ref', 'Data1', 'Data2', 'H1', 'H2', 'H3', 'H4']
    )
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]
    # Filter one column
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(
                fname1, fname2, 'Ref', 'H2')
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ref', 'H2']
    assert obj.data() == [
        [10, 2],
        [20, 6],
        [30, 10]
    ]
    # Filter two columns
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(
                fname1, fname2, ['Ref', 'Data1'], ['H2', 'H4'])
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ref', 'Data1', 'H2', 'H4']
    assert obj.data() == [
        [10, 20, 2, 4],
        [20, 40, 6, 8],
        [30, 300, 10, 12]
    ]
    # Filter row and columns
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(
                fname1,
                fname2,
                (['Ref', 'Data1'], {'Ctrl':['nom', 'low']}),
                (['H2', 'H4'], {'H3':7})
            )
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ref', 'Data1', 'H2', 'H4']
    assert obj.data() == [
        [10, 20, 6, 8],
        [30, 300, None, None]
    ]
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(
                fname1=fname1,
                fname2=fname2,
                dfilter1=(['Ref', 'Data1'], {'Ctrl':['nom', 'low']}),
                dfilter2=['H2', 'H4'],
            )
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ref', 'Data1', 'H2', 'H4']
    assert obj.data() == [
        [10, 20, 2, 4],
        [30, 300, 6, 8],
        [None, None, 10, 12]
    ]

    # Output header when file1 has no headers
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(fname1, fname2, has_header1=False)
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert (
        obj.header()
        ==
        [
            'Column 1', 'Column 2', 'Column 3', 'Column 4',
            'H1', 'H2', 'H3', 'H4'
        ]
    )
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]
    # Output header when file2 has no headers
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(fname1, fname2, has_header2=False)
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert (
        obj.header()
        ==
        [
            'Ctrl', 'Ref', 'Data1', 'Data2',
            'Column 5', 'Column 6', 'Column 7', 'Column 8'
        ]
    )
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]
    # # Output header when neither file1 nor file2 have headers
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(
                fname1, fname2, has_header1=False, has_header2=False
            )
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=False)
    assert obj.header() == [0, 1, 2, 3, 4, 5, 6, 7]
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]
    # Output header given
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(
                fname1,
                fname2,
                has_header1=False,
                has_header2=False,
                ocols=['D{}'.format(num) for num in range(0, 8)]
            )
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert (
        obj.header()
        ==
        ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
    )
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]
    # Save to a different file
    with tempfile.NamedTemporaryFile() as fwobj:
        ofname = fwobj.name
        with putil.misc.TmpFile(write_input_file) as fname1:
            with putil.misc.TmpFile(write_replacement_file) as fname2:
                putil.pcsv.merge(fname1, fname2, ofname=ofname)
            obj = putil.pcsv.CsvFile(fname=ofname, has_header=True)
    assert (
        obj.header()
        ==
        ['Ctrl', 'Ref', 'Data1', 'Data2', 'H1', 'H2', 'H3', 'H4']
    )
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]


@pytest.mark.merge
def test_merge_exceptions():
    """ Test merge function exceptions """
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
            fname1 = '_dummy_file_' if not file_toggle else real_file
            fname2 = real_file if not file_toggle else '_dummy_file_'
            putil.test.assert_exception(
                putil.pcsv.merge,
                {
                    'fname1':fname1,
                    'dfilter1':['a'],
                    'fname2':fname2,
                    'dfilter2':['b']
                },
                OSError,
                'File _dummy_file_ could not be found'
            )
            for item in file_items:
                fname1 = item if not file_toggle else real_file
                fname2 = real_file if not file_toggle else item
                putil.test.assert_exception(
                    putil.pcsv.merge,
                    {
                        'fname1':fname1,
                        'dfilter1':['a'],
                        'fname2':fname2,
                        'dfilter2':['b']
                    },
                    RuntimeError,
                    'Argument `*[{}]*` is not valid'.format(
                        'fname1' if not file_toggle else 'fname2'
                    )
                )
        with putil.misc.TmpFile(write_file_empty) as empty_file:
            with putil.misc.TmpFile(write_file) as real_file:
                fname1 = empty_file if not file_toggle else real_file
                fname2 = real_file if not file_toggle else empty_file
                putil.test.assert_exception(
                    putil.pcsv.merge,
                    {
                        'fname1':fname1,
                        'dfilter1':['Ctrl'],
                        'fname2':fname2,
                        'dfilter2':['Ctrl']
                    },
                    RuntimeError,
                    r'File (.+) is empty'
                )
        with putil.misc.TmpFile(write_cols_not_unique) as nuniq_file:
            with putil.misc.TmpFile(write_file) as real_file:
                fname1 = nuniq_file if not file_toggle else real_file
                fname2 = real_file if not file_toggle else nuniq_file
                putil.test.assert_exception(
                    putil.pcsv.merge,
                    {
                        'fname1':fname1,
                        'dfilter1':['Ctrl'],
                        'fname2':fname2,
                        'dfilter2':['Ctrl']
                    },
                    RuntimeError,
                    'Column headers are not unique in file (.+)'
                )
        # Filter-related exceptions
        with putil.misc.TmpFile(write_file) as fname1:
            with putil.misc.TmpFile(write_file) as fname2:
                for item in dfilter_items:
                    dfilter1 = item if not file_toggle else ['Ctrl']
                    dfilter2 = ['Ctrl'] if not file_toggle else item
                    putil.test.assert_exception(
                        putil.pcsv.merge,
                        {
                            'fname1':fname1,
                            'dfilter1':dfilter1,
                            'fname2':fname2,
                            'dfilter2':dfilter2
                        },
                        RuntimeError,
                        'Argument `{}` is not valid'.format(
                            'dfilter1' if not file_toggle else 'dfilter2'
                        )
                    )
                item = (['Ctrl'], {'aaa':5})
                dfilter1 = item if not file_toggle else ['Ctrl']
                dfilter2 = ['Ctrl'] if not file_toggle else item
                putil.test.assert_exception(
                    putil.pcsv.merge,
                    {
                        'fname1':fname1,
                        'dfilter1':dfilter1,
                        'fname2':fname2,
                        'dfilter2':dfilter2
                    },
                    ValueError,
                    'Column aaa not found'
                )
                # Columns-related exceptions
                dfilter1 = ['NoCol'] if not file_toggle else ['Ref']
                dfilter2 = ['Ref'] if not file_toggle else ['NoCol']
                putil.test.assert_exception(
                    putil.pcsv.merge,
                    {
                        'fname1':fname1,
                        'dfilter1':dfilter1,
                        'fname2':fname2,
                        'dfilter2':dfilter2
                    },
                    ValueError,
                    'Column NoCol not found'
                )
                dfilter1 = ['0'] if not file_toggle else ['Ref']
                dfilter2 = ['Ref'] if not file_toggle else ['0']
                putil.test.assert_exception(
                    putil.pcsv.merge,
                    {
                        'fname1':fname1,
                        'has_header1':file_toggle,
                        'dfilter1':dfilter1,
                        'fname2':fname2,
                        'dfilter2':dfilter2,
                        'has_header2':not file_toggle,
                    },
                    RuntimeError,
                    'Invalid column specification'
                )
    with putil.misc.TmpFile(write_file) as fname1:
        with putil.misc.TmpFile(write_file) as fname2:
            putil.test.assert_exception(
                putil.pcsv.merge,
                {
                    'fname1':fname1,
                    'dfilter1':['Ctrl'],
                    'fname2':fname2,
                    'dfilter2':['Ref'],
                    'ocols':['a', 'b', 'c']
                },
                RuntimeError,
                (
                    'Combined columns in data files and output '
                    'columns are different'
                )
            )
    # Output file exceptions
    with putil.misc.TmpFile(write_file) as fname1:
        with putil.misc.TmpFile(write_file) as fname2:
            putil.test.assert_exception(
                putil.pcsv.merge,
                {
                    'fname1':fname1,
                    'dfilter1':['Ctrl'],
                    'fname2':fname2,
                    'dfilter2':['Ref'],
                    'ofname':7
                },
                RuntimeError,
                'Argument `ofname` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.merge,
                {
                    'fname1':fname1,
                    'dfilter1':['Ctrl'],
                    'fname2':fname2,
                    'dfilter2':['Ref'],
                    'ofname':'a_file\0'
                },
                RuntimeError,
                'Argument `ofname` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.merge,
                {
                    'fname1':fname1,
                    'dfilter1':['Ctrl'],
                    'fname2':fname2,
                    'dfilter2':['Ref'],
                    'ofname':'some_file.csv',
                    'ocols':7
                },
                RuntimeError,
                'Argument `ocols` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.merge,
                {
                    'fname1':fname1,
                    'dfilter1':['Ctrl'],
                    'fname2':fname2,
                    'dfilter2':['Ref'],
                    'ofname':'some_file.csv',
                    'ocols':['a', 'b', 5]
                },
                RuntimeError,
                'Argument `ocols` is not valid'
            )
