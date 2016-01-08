# plot_example_3.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410,R0903

import putil.misc, putil.pcsv

def cwrite(fobj, data):
    fobj.write(data)

def write_csv_file(file_handle):
    cwrite(file_handle, 'Col1,Col2\n')
    cwrite(file_handle, '0E-12,10\n')
    cwrite(file_handle, '1E-12,0\n')
    cwrite(file_handle, '2E-12,20\n')
    cwrite(file_handle, '3E-12,-10\n')
    cwrite(file_handle, '4E-12,30\n')

# indep_var is a Numpy vector, in this example time,
# in seconds. dep_var is a Numpy vector
def proc_func1(indep_var, dep_var):
    # Scale time to pico-seconds
    indep_var = indep_var/1e-12
    # Remove offset
    dep_var = dep_var-dep_var[0]
    return indep_var, dep_var

def create_csv_source():
    with putil.misc.TmpFile(write_csv_file) as fname:
        obj = putil.plot.CsvSource(
            fname=fname,
            indep_col_label='Col1',
            dep_col_label='Col2',
            indep_min=2E-12,
            fproc=proc_func1
        )
    return obj
