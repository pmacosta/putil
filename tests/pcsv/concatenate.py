# concatenate.py
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
    write_file,
    write_input_file,
    write_replacement_file
)


###
# Test functions
###
def test_concatenate():
    """ Test concatenate function behavior """
    # In place replacement
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.concatenate(fname1, fname2)
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ctrl', 'Ref', 'Data1', 'Data2']
    assert obj.data() == [
        ['nom', 10, 20, 30],
        ['high', 20, 40, 60],
        ['low', 30, 300, 3000],
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    # Filter one column
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.concatenate(fname1, fname2, 'Ref', 'H2')
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ref']
    assert obj.data() == [[10], [20], [30], [2], [6], [10]]
    # Filter two columns
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.concatenate(
                fname1, fname2, ['Ref', 'Data1'], ['H2', 'H4']
            )
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ref', 'Data1']
    assert obj.data() == [
        [10, 20], [20, 40], [30, 300], [2, 4], [6, 8], [10, 12]
    ]
    # Filter row and columns
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.concatenate(
                fname1,
                fname2,
                (['Ref', 'Data1'], {'Ctrl':['nom', 'low']}),
                (['H2', 'H4'], {'H3':7})
            )
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['Ref', 'Data1']
    assert obj.data() == [[10, 20], [30, 300], [6, 8]]
    # Output header when file1 has no headers
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.concatenate(fname1, fname2, has_header1=False)
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['H1', 'H2', 'H3', 'H4']
    assert obj.data() == [
        ['nom', 10, 20, 30],
        ['high', 20, 40, 60],
        ['low', 30, 300, 3000],
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    # Output header when neither file1 nor file2 have headers
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.concatenate(
                fname1, fname2, has_header1=False, has_header2=False
            )
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=False)
    assert obj.header() == [0, 1, 2, 3]
    assert obj.data() == [
        ['nom', 10, 20, 30],
        ['high', 20, 40, 60],
        ['low', 30, 300, 3000],
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    # Output header given
    with putil.misc.TmpFile(write_input_file) as fname1:
        with putil.misc.TmpFile(write_replacement_file) as fname2:
            putil.pcsv.concatenate(
                fname1,
                fname2,
                has_header1=False,
                has_header2=False,
                ocols=['D0', 'D1', 'D2', 'D3']
            )
        obj = putil.pcsv.CsvFile(fname=fname1, has_header=True)
    assert obj.header() == ['D0', 'D1', 'D2', 'D3']
    assert obj.data() == [
        ['nom', 10, 20, 30],
        ['high', 20, 40, 60],
        ['low', 30, 300, 3000],
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    # Save to a different file
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_input_file) as fname1:
            with putil.misc.TmpFile(write_replacement_file) as fname2:
                putil.pcsv.concatenate(fname1, fname2, ofname=ofname)
            obj = putil.pcsv.CsvFile(fname=ofname, has_header=True)
        assert obj.header() == ['Ctrl', 'Ref', 'Data1', 'Data2']
        assert obj.data() == [
            ['nom', 10, 20, 30],
            ['high', 20, 40, 60],
            ['low', 30, 300, 3000],
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12]
        ]
    # Starting row
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_input_file) as fname1:
            with putil.misc.TmpFile(write_replacement_file) as fname2:
                putil.pcsv.concatenate(
                    fname1, fname2, ofname=ofname, frow1=4, frow2=3)
            obj = putil.pcsv.CsvFile(fname=ofname, has_header=True)
        assert obj.data() == [
            ['low', 30, 300, 3000],
            [5, 6, 7, 8],
            [9, 10, 11, 12]
        ]


@pytest.mark.concatenate
def test_concatenate_exceptions():
    """ Test concatenate function exceptions """
    obj = putil.pcsv.concatenate
    common_exceptions(obj)
    with putil.misc.TmpFile(write_file) as fname1:
        with putil.misc.TmpFile(write_file) as fname2:
            # Column numbers are different
            exmsg = 'Files have different number of columns'
            AE(obj, RE, exmsg, fname1, fname2, ['Ctrl'], ['Ctrl', 'Ref'])
            exmsg = (
                'Number of columns in data files '
                'and output columns are different'
            )
            AE(
                obj, RE, exmsg, fname1, fname2, ['Ctrl'], ['Ctrl', 'Ref'],
                ocols=['a', 'b', 'c']
            )
