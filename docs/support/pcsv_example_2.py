# pcsv_example_2.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0104

import putil.pcsv, tempfile

def main():
    ctx = tempfile.NamedTemporaryFile
    with ctx() as ifobj, ctx() as rfobj, ctx() as ofobj:
        # Create first (input) data file
        input_data = [
            ['Item', 'Cost'],
            [1, 9.99],
            [2, 10000],
            [3, 0.10]
        ]
        ifname = ifobj.name
        putil.pcsv.write(ifname, input_data, append=False)
        # Create second (replacement) data file
        replacement_data = [
            ['Staff', 'Rate', 'Days'],
            ['Joe', 10, 'Sunday'],
            ['Sue', 20, 'Thursday'],
            ['Pat', 15, 'Tuesday']
        ]
        rfname = rfobj.name
        putil.pcsv.write(rfname, replacement_data, append=False)
        # Replace "Cost" column of input file with "Rate" column
        # of replacement file for "Items" 2 and 3 with "Staff" data
        # from Joe and Pat. Save resulting data to another file
        ofname = ofobj.name
        putil.pcsv.replace(
            ifname=ifname,
            idfilter=('Cost', {'Item':[1, 3]}),
            rfname=rfname,
            rdfilter=('Rate', {'Staff':['Joe', 'Pat']}),
            ofname=ofname
        )
        # Verify that resulting file is correct
        ref_data = [
            ['Item', 'Cost'],
            [1, 10],
            [2, 10000],
            [3, 15]
        ]
        obj = putil.pcsv.CsvFile(ofname)
        assert obj.header() == ref_data[0]
        assert obj.data() == ref_data[1:]

if __name__ == '__main__':
    main()
