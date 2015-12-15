# write.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0105,W0611

# Standard library imports
import csv
import os
import platform
import sys
# Putil imports
import putil.exh
import putil.pcontracts
from putil.ptypes import file_name


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_pcsv_write
exobj = trace_ex_pcsv_write.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
def _write_int(fname, data, append=True):
    """ Write data to CSV file with validation """
    # pylint: disable=W0705
    _exh = putil.exh.get_or_create_exh_obj()
    _exh.add_exception(
        exname='data_is_empty',
        extype=ValueError,
        exmsg='There is no data to save to file'
    )
    _exh.add_exception(
        exname='file_could_not_be_created_io',
        extype=OSError,
        exmsg='File *[fname]* could not be created: *[reason]*'
    )
    _exh.add_exception(
        exname='file_could_not_be_created_os',
        extype=OSError,
        exmsg='File *[fname]* could not be created: *[reason]*'
    )
    _exh.raise_exception_if(
        exname='data_is_empty',
        condition=(
            (len(data) == 0) or
            ((len(data) == 1) and (len(data[0]) == 0))
        )
    )
    try:
        putil.misc.make_dir(fname)
        mode = 'w' if append is False else 'a'
        if sys.hexversion < 0x03000000: # pragma: no cover, no branch
            with open(fname, mode) as file_handle:
                csv.writer(file_handle, delimiter=',').writerows(data)
        else: # pragma: no cover
            with open(fname, mode, newline='') as file_handle:
                csv.writer(file_handle, delimiter=',').writerows(data)
    except IOError as eobj:
        _exh.raise_exception_if(
            exname='file_could_not_be_created_io',
            condition=True,
            edata=[
                {'field':'fname', 'value':fname},
                {'field':'reason', 'value':eobj.strerror}
            ]
        )
    except OSError as eobj: # pragma: no cover
        _exh.raise_exception_if(
            exname='file_could_not_be_created_os',
            condition=True,
            edata=[
                {'field':'fname', 'value':fname},
                {'field':'reason', 'value':eobj.strerror}
            ]
        )


@putil.pcontracts.contract(
    fname='file_name', data='list(list(str|int|float|None))', append=bool
)
def write(fname, data, append=True):
    r"""
    Writes data to a specified comma-separated values (CSV) file

    :param fname: Name of the comma-separated values file to be written
    :type  fname: :ref:`FileName`

    :param data: Data to write to the file. Each item in this argument
                 should contain a sub-list corresponding to a row of data;
                 each item in the sub-lists should contain data corresponding
                 to a particular column
    :type  data: list

    :param append: Flag that indicates whether data is added to an existing
                   file (or a new file is created if it does not exist) (True),
                   or whether data overwrites the file contents (if the file
                   exists) or creates a new file if the file does not exists
                   (False)
    :type  append: boolean

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.pcsv.write.write

    :raises:
     * OSError (File *[fname]* could not be created: *[reason]*)

     * RuntimeError (Argument \`append\` is not valid)

     * RuntimeError (Argument \`data\` is not valid)

     * RuntimeError (Argument \`fname\` is not valid)

     * ValueError (There is no data to save to file)

    .. [[[end]]]
    """
    _write_int(fname, data, append)
