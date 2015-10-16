# pcsv_example_3.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0104

import putil.pcsv, tempfile

def main():
    ctx = tempfile.NamedTemporaryFile
    with ctx() as fobj1:
        with ctx() as fobj2:
            with ctx() as ofobj:
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
                # Concatenate file1 and file2. Filter out
                # second column of file2
                ofname = ofobj.name
                putil.pcsv.concatenate(
                    fname1=fname1,
                    fname2=fname2,
                    has_header1=False,
                    has_header2=False,
                    dfilter2=[0, 2],
                    ofname=ofname,
                    ocols=['D1', 'D2']
                )
                # Verify that resulting file is correct
                ref_data = [
                    ['D1', 'D2'],
                    [1, 9.99],
                    [2, 10000],
                    [3, 0.10],
                    ['Joe', 'Sunday'],
                    ['Sue', 'Thursday'],
                    ['Pat', 'Tuesday']
                ]
                obj = putil.pcsv.CsvFile(ofname)
                assert obj.header() == ref_data[0]
                assert obj.data() == ref_data[1:]

if __name__ == '__main__':
    main()
