# pcsv.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0105,W0611

import csv
import sys

import putil.exh
import putil.misc
import putil.pcontracts
from putil.ptypes import csv_data_filter, file_name, file_name_exists


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_pcsv
exobj = trace_ex_pcsv.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
@putil.pcontracts.contract(
    fname='file_name',
    data='list(list(str|int|float))',
    append=bool
)
def write(fname, data, append=True):
    r"""
    Writes data to a specified comma-separated values (CSV) file

    :param  fname:  Name of the comma-separated values file to be written
    :type   fname:  :ref:`FileName`
    :param  data:   Data to write to the file. Each item in this argument
     should contain a sub-list corresponding to a row of data; each item in the
     sub-lists should contain data corresponding to a particular column
    :type   data:   list
    :param  append: Flag that indicates whether data is added to an existing
     file (or a new file is created if it does not exist) (True), or whether
     data overwrites the file contents (if the file exists) or creates a new
     file if the file does not exists (False)
    :type   append: boolean

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.pcsv.write

    :raises:
     * OSError (File *[fname]* could not be created: *[reason]*)

     * RuntimeError (Argument \`append\` is not valid)

     * RuntimeError (Argument \`data\` is not valid)

     * RuntimeError (Argument \`fname\` is not valid)

     * ValueError (There is no data to save to file)

    .. [[[end]]]
    """
    _write_int(fname, data, append)


def _write_int(fname, data, append=True):
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
        with open(fname, mode) as file_handle: # pragma: no cover
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


def _tofloat(obj):
    """ Convert to float if object is a float string """
    if 'inf' in obj.lower().strip():
        return obj
    try:
        return int(obj)
    except ValueError:
        try:
            return float(obj)
        except ValueError:
            return obj


###
# Classes
###
class CsvFile(object):
    r"""
    Processes comma-separated values (CSV) files

    :param  fname:  Name of the comma-separated values file to read
    :type   fname:  :ref:`FileNameExists`
    :param  dfilter:    Data filter
    :type   dfilter:    :ref:`CsvDataFilter`
    :rtype: :py:class:`putil.pcsv.CsvFile` object

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.pcsv.CsvFile.__init__

    :raises:
     * OSError (File \`*[file_name]*\` could not be found)

     * RuntimeError (Argument \`dfilter\` is not valid)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (Column headers are not unique)

     * RuntimeError (File *[fname]* has no valid data)

     * RuntimeError (File *[fname]* is empty)

     * ValueError (Argument \`dfilter\` is empty)

     * ValueError (Column *[column_name]* not found in header)

    .. [[[end]]]
    """
    # pylint: disable=W0631
    @putil.pcontracts.contract(
        fname='file_name_exists',
        dfilter='csv_data_filter'
    )
    def __init__(self, fname, dfilter=None):
        self._header = None
        self._header_upper = None
        self._data = None
        self._fdata = None
        self._dfilter = None
        self._exh = None
        # Register exceptions
        self._exh = putil.exh.get_or_create_exh_obj()
        self._exh.add_exception(
            exname='file_empty',
            extype=RuntimeError,
            exmsg='File *[fname]* is empty'
        )
        self._exh.add_exception(
            exname='column_headers_not_unique',
            extype=RuntimeError,
            exmsg='Column headers are not unique'
        )
        self._exh.add_exception(
            exname='file_has_no_valid_data',
            extype=RuntimeError,
            exmsg='File *[fname]* has no valid data'
        )
        # Read data
        with open(fname, 'rU') as file_handle:
            self._raw_data = [row for row in csv.reader(file_handle)]
        # Process header
        self._exh.raise_exception_if(
            exname='file_empty',
            condition=len(self._raw_data) == 0,
            edata={'field':'fname', 'value':fname}
        )
        self._header = self._raw_data[0]
        self._header_upper = [col.upper() for col in self.header]
        self._exh.raise_exception_if(
            exname='column_headers_not_unique',
            condition=len(set(self._header_upper)) != len(self._header_upper)
        )
        # Find start of data row
        for num, row in enumerate(self._raw_data[1:]):
            if any([putil.misc.isnumber(_tofloat(col)) for col in row]):
                break
        else:
            self._exh.raise_exception_if(
                exname='file_has_no_valid_data',
                condition=True,
                edata={'field':'fname', 'value':fname}
            )
        # Set up class properties
        self._data = [
            [
                None
                if col.strip() == '' else
                _tofloat(col)
                for col in row
            ]
            for row in self._raw_data[num+1:]
        ]
        self.reset_dfilter()
        # dfilter already validated, can use internal function,
        # not API end-point
        self._set_dfilter_int(dfilter)

    def _validate_dfilter(self, dfilter):
        """ Validate that all columns in filter are in header """
        if dfilter is not None:
            for key in dfilter:
                self._in_header(key)
                dfilter[key] = ([dfilter[key]]
                               if isinstance(dfilter[key], str) else
                               dfilter[key])

    def _get_dfilter(self):
        return self._dfilter

    @putil.pcontracts.contract(dfilter='csv_data_filter')
    def _set_dfilter(self, dfilter):
        self._set_dfilter_int(dfilter)

    def _set_dfilter_int(self, dfilter):
        if dfilter is not None:
            # Filter data
            self._validate_dfilter(dfilter)
            df_tuples = [
                (
                    self._header_upper.index(key.upper()),
                    [value]
                    if not putil.misc.isiterable(value) else
                    [item for item in value]
                )
                for key, value in dfilter.items()
            ]
            self._fdata = [
                row for row in self._data
                if all([row[col_num] in col_value
                for col_num, col_value in df_tuples])
            ]
        self._dfilter = dfilter

    @putil.pcontracts.contract(dfilter='csv_data_filter')
    def add_dfilter(self, dfilter):
        r"""
        Adds more data filter(s) to the existing filter(s). Data is added to
        the current filter for a particular column if that column was already
        filtered, duplicate filter values are eliminated.

        :param  dfilter:    Data filter
         specification
        :type   dfilter:    :ref:`CsvDataFilter`

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.CsvFile.add_dfilter

        :raises:
         * RuntimeError (Argument \`dfilter\` is not valid)

         * ValueError (Argument \`dfilter\` is empty)

         * ValueError (Column *[column_name]* not found in header)

        .. [[[end]]]
        """
        self._validate_dfilter(dfilter)
        if (dfilter is None) or (self._dfilter is None):
            self._dfilter = dfilter
        else:
            for key in dfilter:
                if key in self._dfilter:
                    self._dfilter[key] = list(set((
                        self._dfilter[key]
                        if isinstance(self._dfilter[key], list) else
                        [self._dfilter[key]]) + (dfilter[key]
                        if isinstance(dfilter[key], list) else [dfilter[key]])
                    ))
                else:
                    self._dfilter[key] = dfilter[key]
        self._set_dfilter_int(self._dfilter)

    def _get_header(self):
        return self._header

    @putil.pcontracts.contract(col='None|str|list(str)', filtered=bool)
    def data(self, col=None, filtered=False):
        r"""
         Returns (filtered) file data. The returned object is a list, each item
         is a sub-list corresponding to a row of data; each item in the
         sub-lists contains data corresponding to a particular column

        :param  col:    Column(s) to extract from (filtered) data. If no column
         specification is given (or the argument is None) all columns are
         returned
        :type   col:    string, list of strings or None
        :param  filtered: Flag that indicates whether the raw (original) data
         should be returned (False) or whether filtered data should be
         returned (True)
        :type   filtered: boolean
        :rtype: list

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for putil.pcsv.CsvFile.data

        :raises:
         * RuntimeError (Argument \`col\` is not valid)

         * RuntimeError (Argument \`filtered\` is not valid)

         * ValueError (Column *[column_name]* not found in header)

        .. [[[end]]]
        """
        self._in_header(col)
        return ((self._data if not filtered else self._fdata)
               if col is None else
               self._core_data(
                   (self._data if not filtered else self._fdata),
                   col
               ))

    def reset_dfilter(self):
        """ Reset (clears) the data filter """
        self._fdata = self._data[:]
        self._dfilter = None

    @putil.pcontracts.contract(
            fname='file_name',
            col='None|str|list(str)',
            filtered=bool,
            headers=bool,
            append=bool
    )
    def write(self, fname, col=None, filtered=False,
              headers=True, append=True):
        r"""
        Writes (processed) data to a specified comma-separated values (CSV)
        file

        :param  fname:  Name of the comma-separated values file to be
         written
        :type   fname:  :ref:`FileName`
        :param  col:    Column(s) to write to file. If no column specification
         is given (or the argument is None) all columns in the data are written
        :type   col:    string, list of strings or None
        :param  filtered: Flag that indicates whether the raw (original) data
         should be written (False) or whether filtered data should be
         written (True)
        :type   filtered: boolean
        :param  headers: Flag that indicates whether column headers should be
         written (True) or not (False)
        :type   headers: boolean
        :param  append: Flag that indicates whether data is added to an
         existing file (or a new file is created if it does not exist) (True),
         or whether data overwrites the file contents (if the file exists) or
         creates a new file if the file does not exists (False)
        :type   append: boolean

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.CsvFile.write

        :raises:
         * OSError (File *[fname]* could not be created: *[reason]*)

         * RuntimeError (Argument \`append\` is not valid)

         * RuntimeError (Argument \`col\` is not valid)

         * RuntimeError (Argument \`filtered\` is not valid)

         * RuntimeError (Argument \`fname\` is not valid)

         * RuntimeError (Argument \`headers\` is not valid)

         * ValueError (Column *[column_name]* not found in header)

         * ValueError (There is no data to save to file)

        .. [[[end]]]
        """
        # pylint: disable=R0913
        self._exh.add_exception(
            exname='write',
            extype=ValueError,
            exmsg='There is no data to save to file'
        )
        self._in_header(col)
        data = self.data(col=col, filtered=filtered)
        if headers:
            col = [col] if isinstance(col, str) else col
            header = (self.header
                     if col is None else
                     [
                         self.header[self._header_upper.index(element.upper())]
                        for element in col
                     ])
        self._exh.raise_exception_if(
            exname='write',
            condition=(
                (len(data) == 0) or ((len(data) == 1) and (len(data[0]) == 0))
            )
        )
        data = [["''" if col is None else col for col in row] for row in data]
        _write_int(fname, [header]+data if headers else data, append=append)

    def _in_header(self, col):
        """
        Validate column name(s) against the column names in the file header
        """
        self._exh.add_exception(
            exname='header_not_found',
            extype=ValueError,
            exmsg='Column *[column_name]* not found in header'
        )
        if col is not None:
            col_list = [col] if isinstance(col, str) else col
            for col in col_list:
                self._exh.raise_exception_if(
                    exname='header_not_found',
                    condition=col.upper() not in self._header_upper,
                    edata={'field':'column_name', 'value':col}
                )

    def _core_data(self, data, col=None):
        """ Extract columns from data """
        if isinstance(col, str):
            col_num = self._header_upper.index(col.upper())
            return [[row[col_num]] for row in data]
        else:   # isinstance(col, list):
            col_list = col[:]
            col_index_list = [
                self._header_upper.index(col.upper()) for col in col_list
            ]
            return [[row[index] for index in col_index_list] for row in data]

    # Managed attributes
    dfilter = property(
        _get_dfilter,
        _set_dfilter,
        doc='Data filter'
    )
    r"""
    Sets or returns the data filter

    :type:      :ref:`CsvDataFilter`
    :rtype:     :ref:`CsvDataFilter` or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.pcsv.CsvFile.dfilter

    :raises: (when assigned)

     * RuntimeError (Argument \`dfilter\` is not valid)

     * ValueError (Argument \`dfilter\` is empty)

     * ValueError (Column *[column_name]* not found in header)

    .. [[[end]]]
    """

    header = property(
        _get_header,
        doc='Comma-separated file (CSV) header'
    )
    """
    Returns the header of the comma-separated values file. Each list item is
    a column header

    :rtype: list of strings
    """
