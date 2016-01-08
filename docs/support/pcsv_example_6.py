# pcsv_example_6.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410,W0104

import putil.misc, putil.pcsv

def main():
    ctx = putil.misc.TmpFile
    with ctx() as ifname:
        with ctx() as ofname:
            # Create input data file
            data = [
                ['Ctrl', 'Ref', 'Result'],
                [1, 3, 10],
                [1, 4, 20],
                [2, 4, 30],
                [2, 5, 40],
                [3, 5, 50]
            ]
            putil.pcsv.write(ifname, data, append=False)
            # Swap 'Ctrl' and 'Result' columns, duplicate
            # 'Ref' column at the end
            obj = putil.pcsv.CsvFile(
                fname=ifname,
                dfilter=['Result', 'Ref', 'Ctrl', 1],
            )
            assert obj.header(filtered=False) == ['Ctrl', 'Ref', 'Result']
            assert (
                obj.header(filtered=True)
                ==
                ['Result', 'Ref', 'Ctrl', 'Ref']
            )
            obj.write(
                ofname,
                header=['Result', 'Ref', 'Ctrl', 'Ref2'],
                filtered=True,
                append=False
            )
            # Verify that resulting file is correct
            ref_data = [
                [10, 3, 1, 3],
                [20, 4, 1, 4],
                [30, 4, 2, 4],
                [40, 5, 2, 5],
                [50, 5, 3, 5]
            ]
            obj = putil.pcsv.CsvFile(ofname, has_header=True)
            assert obj.header() == ['Result', 'Ref', 'Ctrl', 'Ref2']
            assert obj.data() == ref_data

if __name__ == '__main__':
    main()
