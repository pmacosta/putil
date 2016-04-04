# merge.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

# PyPI imports
import pytest
# Putil imports
import putil.pcsv
from putil.test import AE, RE
from tests.pcsv.fixtures import (
    common_exceptions,
    write_input_file,
    write_file,
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
    assert obj.header() == [
        'Ctrl', 'Ref', 'Data1', 'Data2', 'H1', 'H2', 'H3', 'H4'
    ]
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]
    # Filter one column
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(fname1, fname2, 'Ref', 'H2')
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ref', 'H2']
    assert obj.data() == [[10, 2], [20, 6], [30, 10]]
    # Filter two columns
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(fname1, fname2, ['Ref', 'Data1'], ['H2', 'H4'])
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ref', 'Data1', 'H2', 'H4']
    assert obj.data() == [[10, 20, 2, 4], [20, 40, 6, 8], [30, 300, 10, 12]]
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
    assert obj.data() == [[10, 20, 6, 8], [30, 300, None, None]]
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
        [10, 20, 2, 4], [30, 300, 6, 8], [None, None, 10, 12]
    ]

    # Output header when file1 has no headers
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(fname1, fname2, has_header1=False)
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == [
        'Column 1', 'Column 2', 'Column 3', 'Column 4', 'H1', 'H2', 'H3', 'H4'
    ]
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
    assert obj.header() == [
        'Ctrl', 'Ref', 'Data1', 'Data2',
        'Column 5', 'Column 6', 'Column 7', 'Column 8'
    ]
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]
    # Output header when neither file1 nor file2 have headers
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
                ocols=['D{0}'.format(num) for num in range(0, 8)]
            )
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]
    # Save to a different file
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_input_file) as fname1:
            with putil.misc.TmpFile(write_replacement_file) as fname2:
                putil.pcsv.merge(fname1, fname2, ofname=ofname)
            obj = putil.pcsv.CsvFile(fname=ofname, has_header=True)
    assert obj.header() == [
        'Ctrl', 'Ref', 'Data1', 'Data2', 'H1', 'H2', 'H3', 'H4'
    ]
    assert obj.data() == [
        ['nom', 10, 20, 30, 1, 2, 3, 4],
        ['high', 20, 40, 60, 5, 6, 7, 8],
        ['low', 30, 300, 3000, 9, 10, 11, 12]
    ]
    # Starting row
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.merge(fname1, fname2, frow1=3, frow2=4)
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == [
        'Ctrl', 'Ref', 'Data1', 'Data2', 'H1', 'H2', 'H3', 'H4'
    ]
    assert obj.data() == [
        ['high', 20, 40, 60, 9, 10, 11, 12],
        ['low', 30, 300, 3000, None, None, None, None]
    ]


@pytest.mark.merge
def test_merge_exceptions():
    """ Test merge function exceptions """
    # pylint: disable=R0914
    obj = putil.pcsv.merge
    common_exceptions(obj)
    with putil.misc.TmpFile(write_file) as fname1:
        with putil.misc.TmpFile(write_file) as fname2:
            exmsg = (
                'Combined columns in data files and output '
                'columns are different'
            )
            AE(
                obj, RE, exmsg,
                fname1, fname2, ['Ctrl'], ['Ref'], ocols=['a', 'b', 'c']
            )
