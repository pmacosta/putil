# pcsv_example_4.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0104

import putil.pcsv, tempfile

def main():
    ctx = tempfile.NamedTemporaryFile
    with ctx() as fobj1, ctx() as fobj2, ctx() as ofobj:
        # Create first data file
        data1 = [
            [1, 9.99],
            [2, 10000],
            [3, 0.10]
        ]
        fname1 = fobj1.name
        putil.pcsv.write(fname1, data1, append=False)
        # Create second data file
        data2 = [
            ['Joe', 10, 'Sunday'],
            ['Sue', 20, 'Thursday'],
            ['Pat', 15, 'Tuesday']
        ]
        fname2 = fobj2.name
        putil.pcsv.write(fname2, data2, append=False)
        # Merge file1 and file2
        ofname = ofobj.name
        putil.pcsv.merge(
            fname1=fname1,
            has_header1=False,
            fname2=fname2,
            has_header2=False,
            ofname=ofname
        )
        # Verify that resulting file is correct
        ref_data = [
            [1, 9.99, 'Joe', 10, 'Sunday'],
            [2, 10000, 'Sue', 20, 'Thursday'],
            [3, 0.10, 'Pat', 15, 'Tuesday'],
        ]
        obj = putil.pcsv.CsvFile(ofname, has_header=False)
        assert obj.header() == list(range(0, 5))
        assert obj.data() == ref_data

if __name__ == '__main__':
    main()
