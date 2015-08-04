# replace.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0105,W0611

import putil.pcontracts
from putil.ptypes import (
    csv_col_filter, csv_row_filter, file_name, file_name_exists
)
from .csv_file import CsvFile
from .write import write


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_pcsv_replace
exobj = trace_ex_pcsv_replace.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
@putil.pcontracts.contract(
    ifname='file_name_exists',
    idfilter='csv_data_filter',
    ihas_header=bool,
    rfname='file_name_exists',
    rdfilter='csv_data_filter',
    rhas_header=bool,
    ofname='None|file_name',
    ocols='None|list(str)'
)
def replace(
    ifname, idfilter, rfname, rdfilter,
    ihas_header=True, rhas_header=True,
    ofname=None, ocols=None):
    r"""
    Replaces data in one file with data from another file

    :param ifname: Name of the input comma-separated values file, the file
                   that contains the columns to be replaced
    :type  ifname: :ref:`FileNameExists`

    :param idfilter: Row and/or column filter for the input file
    :type  idfilter: :ref:`CsvDataFilter`

    :param rfname: Name of the replacement comma-separated values file, the
                   file that contains the replacement data
    :type  rfname: :ref:`FileNameExists`

    :param rdfilter: Row and/or column filter for the replacement file
    :type  rdfilter: :ref:`CsvDataFilter`

    :param ihas_header: Flag that indicates whether the input comma-separated
                        values file has column headers in its first line (True)
                        or not (False)
    :type  ihas_header: boolean

    :param rhas_header: Flag that indicates whether the replacement
                        comma-separated values file has column headers in its
                        first line (True) or not (False)
    :type  rhas_header: boolean

    :param ofname: Name of the output comma-separated values file, the file
                   that will contain the input file data but with some columns
                   replaced with data from the replacement file. If None the
                   input file is replaced "in place"
    :type  ofname: :ref:`FileName` or None

    :param ocols: Names of the replaced columns in the output comma-separated
                  values file. If None the column names in the input file are
                  used if **ihas_header** is True, otherwise no header is used
    :type  ocols: list or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.pcsv.replace.replace

    :raises:
     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`idfilter\` is not valid)

     * RuntimeError (Argument \`ifname\` is not valid)

     * RuntimeError (Argument \`ocols\` is not valid)

     * RuntimeError (Argument \`ofname\` is not valid)

     * RuntimeError (Argument \`rdfilter\` is not valid)

     * RuntimeError (Argument \`rfname\` is not valid)

     * RuntimeError (Column headers are not unique in file *[fname]*)

     * RuntimeError (File *[fname]* is empty)

     * RuntimeError (Invalid column specification)

     * RuntimeError (Number of input and output columns are different)

     * RuntimeError (Number of input and replacement columns are
       different)

     * ValueError (Column *[column_identifier]* not found)

     * ValueError (Number of rows mismatch between input and replacement
       data)

    .. [[[end]]]
    """
    # pylint: disable=R0913,R0914
    _exh = putil.exh.get_or_create_exh_obj()
    _exh.add_exception(
        exname='irmm',
        extype=RuntimeError,
        exmsg='Number of input and replacement columns are different'
    )
    _exh.add_exception(
        exname='iomm',
        extype=RuntimeError,
        exmsg='Number of input and output columns are different'
    )
    # Read and validate input data
    iobj = CsvFile(fname=ifname, dfilter=idfilter, has_header=ihas_header)
    # Read and validate replacement data
    robj = CsvFile(fname=rfname, dfilter=rdfilter, has_header=rhas_header)
    # Assign output data structure
    ofname = ifname if ofname is None else ofname
    icfilter = iobj.header() if iobj.cfilter is None else iobj.cfilter
    rcfilter = robj.header() if robj.cfilter is None else robj.cfilter
    ocols = icfilter if ocols is None else ocols
    # Miscellaneous data validation
    _exh.raise_exception_if(
        exname='irmm', condition=len(icfilter) != len(rcfilter)
    )
    _exh.raise_exception_if(
        exname='iomm', condition=len(icfilter) != len(ocols)
    )
    # Replace data
    iobj.replace(rdata=robj.data(filtered=True), filtered=True)
    iheader_upper = [
        item.upper()
        if isinstance(item, str) else item
        for item in iobj.header()
    ]
    icfilter_index = [
        iheader_upper.index(item.upper() if isinstance(item, str) else item)
        for item in icfilter
    ]
    # Create new header
    orow = []
    if ihas_header:
        for col_num, idata in enumerate(iobj.header()):
            orow.append(
                ocols[icfilter_index.index(col_num)]
                if col_num in icfilter_index else
                idata
            )
    # Write (new) file
    iobj.write(fname=ofname, header=orow if orow else False, append=False)
