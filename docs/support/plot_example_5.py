# plot_example_5.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410,E0611,F0401,R0903

import sys, putil.misc, putil.pcsv
if sys.hexversion < 0x03000000:
    from putil.compat2 import _write
else:
    from putil.compat3 import _write

def write_csv_file(file_handle):
    _write(file_handle, 'Col1,Col2\n')
    _write(file_handle, '0E-12,10\n')
    _write(file_handle, '1E-12,0\n')
    _write(file_handle, '2E-12,20\n')
    _write(file_handle, '3E-12,-10\n')
    _write(file_handle, '4E-12,30\n')

def proc_func2(indep_var, dep_var, par1, par2):
    return (indep_var/1E-12)+(2*par1), dep_var+sum(par2)

def create_csv_source():
    with putil.misc.TmpFile(write_csv_file) as fname:
        obj = putil.plot.CsvSource(
            fname=fname,
            indep_col_label='Col1',
            dep_col_label='Col2',
            fproc=proc_func2,
            fproc_eargs={'par1':5, 'par2':[1, 2, 3]}
        )
    return obj
