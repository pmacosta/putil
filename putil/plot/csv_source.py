# csv_source.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,E0602,W0105,W0212,W0611

import numpy
from collections import OrderedDict

import putil.exh
import putil.pcsv
from putil.pcsv import csv_data_filter
from .constants import PRECISION
from .functions import (DataSource, _check_increasing_real_numpy_vector,
                        _check_real_numpy_vector)


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
if sys.version_info.major == 2:
    import __builtin__
else:
    import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_plot_csv_source
exobj_plot = trace_ex_plot_csv_source.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Class
###
class CsvSource(DataSource):
    r"""
    Objects of this class hold a data set from a CSV file intended for
    plotting. The raw data from the file can be filtered and a callback
    function can be used for more general data pre-processing.

    :param  fname:              comma-separated values file name
    :type   fname:              :ref:`FileNameExists`
    :param  indep_col_label:    independent variable column label
    :type   indep_col_label:    case insensitive string
    :param  dep_col_label:      dependent variable column label
    :type   dep_col_label:      case insensitive string
    :param  dfilter:            data filter
     specification
    :type   dfilter:            :ref:`CsvDataFilter`
    :param  indep_min:          minimum independent variable value
    :type   indep_min:          :ref:`RealNum` *or None*
    :param  indep_max:          maximum independent variable value
    :type   indep_max:          :ref:`RealNum` *or None*
    :param  fproc:              data processing function
    :type   fproc:              :ref:`Function`
    :param  fproc_eargs:        data processing function extra arguments
    :type   fproc_eargs:        dictionary or None
    :rtype:                     :py:class:`putil.plot.CsvSource` object

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.__init__

    :raises:
     * OSError (File \`*[file_name]*\` could not be found)

     * RuntimeError (Argument \`col\` is not valid)

     * RuntimeError (Argument \`dep_col_label\` is not valid)

     * RuntimeError (Argument \`dep_var\` is not valid)

     * RuntimeError (Argument \`dfilter\` is not valid)

     * RuntimeError (Argument \`filtered\` is not valid)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (Argument \`fproc_eargs\` is not valid)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned an
       illegal number of values)

     * RuntimeError (Argument \`fproc\` is not valid)

     * RuntimeError (Argument \`indep_col_label\` is not valid)

     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`indep_var\` is not valid)

     * RuntimeError (Column headers are not unique)

     * RuntimeError (File *[fname]* has no valid data)

     * RuntimeError (File *[fname]* is empty)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value is
       not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Argument \`dfilter\` is empty)

     * ValueError (Argument \`fproc\` (function *[func_name]*) does not have
       at least 2 arguments)

     * ValueError (Argument \`indep_min\` is greater than argument
       \`indep_max\`)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

     * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the same
       number of elements)

     * ValueError (Column *[col_name]* (dependent column label) could not be
       found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* (independent column label) could not be
       found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* in data filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Column *[column_name]* not found in header)

     * ValueError (Extra argument \`*[arg_name]*\` not found in argument
       \`fproc\` (function *[func_name]*) definition)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """
    # pylint: disable=R0902,R0903,R0913
    def __init__(self, fname, indep_col_label, dep_col_label, dfilter=None,
                 indep_min=None, indep_max=None, fproc=None, fproc_eargs=None):
        # Private attributes
        super(CsvSource, self).__init__()
        self._exh = putil.exh.get_or_create_exh_obj()
        self._raw_indep_var, self._raw_dep_var = None, None
        self._min_indep_var_index, self._max_indep_var_index = None, None
        self._indep_var_indexes = None
        self._csv_obj, self._reverse_data = None, False
        # Public attributes
        self._indep_min, self._indep_max = None, None
        self._fname, self._dfilter, self._indep_col_label = None, None, None
        self._dep_col_label, self._fproc, self._fproc_eargs = None, None, None
        # Assignment of arguments to attributes
        self._set_fproc(fproc)
        self._set_fproc_eargs(fproc_eargs)
        self._set_dfilter(dfilter)
        self._set_indep_col_label(indep_col_label)
        self._set_dep_col_label(dep_col_label)
        self._set_indep_min(indep_min)
        self._set_indep_max(indep_max)
        self._set_fname(fname)

    def _get_fname(self):
        return self._fname

    @putil.pcontracts.contract(fname='file_name_exists')
    def _set_fname(self, fname):
        self._fname = fname
        self._csv_obj = putil.pcsv.CsvFile(fname)
        self._apply_dfilter()   # This also gets indep_var and dep_var from file
        self._process_data()

    def _get_dfilter(self):
        return self._dfilter

    @putil.pcontracts.contract(dfilter='csv_data_filter')
    def _set_dfilter(self, dfilter):
        # putil.pcsv is case insensitive and all caps
        self._dfilter = (dict([(key, value) for key, value in dfilter.items()])
                        if isinstance(dfilter, dict) else dfilter)
        self._apply_dfilter()
        self._process_data()

    def _get_indep_col_label(self):
        return self._indep_col_label

    @putil.pcontracts.contract(indep_col_label=str)
    def _set_indep_col_label(self, indep_col_label):
        self._indep_col_label = indep_col_label
        self._check_indep_col_label()
        self._apply_dfilter()
        self._process_data()

    def _get_dep_col_label(self):
        return self._dep_col_label

    @putil.pcontracts.contract(dep_col_label=str)
    def _set_dep_col_label(self, dep_col_label):
        self._dep_col_label = dep_col_label
        self._check_dep_col_label()
        self._apply_dfilter()
        self._process_data()

    @putil.pcontracts.contract(indep_var='increasing_real_numpy_vector')
    def _set_indep_var(self, indep_var):
        self._exh.add_exception(
            exname='same',
            extype=ValueError,
            exmsg='Arguments `indep_var` and `dep_var`'
                  ' must have the same number of elements'
        )
        self._exh.raise_exception_if(
            exname='same',
            condition=(indep_var is not None) and
                      (self._raw_dep_var is not None) and
                      (len(self._raw_dep_var) != len(indep_var)))
        self._raw_indep_var = putil.eng.round_mantissa(indep_var, PRECISION)
        # Apply minimum and maximum range bounding and assign it to
        # self._indep_var and thus this is what self.indep_var returns
        self._update_indep_var()
        self._update_dep_var()

    @putil.pcontracts.contract(dep_var='real_numpy_vector')
    def _set_dep_var(self, dep_var):
        self._exh.add_exception(
            exname='same',
            extype=ValueError,
            exmsg='Arguments `indep_var` and `dep_var`'
                  ' must have the same number of elements'
        )
        self._exh.raise_exception_if(
            exname='same',
            condition=(dep_var is not None) and
                      (self._raw_indep_var is not None) and
                      (len(self._raw_indep_var) != len(dep_var)))
        self._raw_dep_var = putil.eng.round_mantissa(dep_var, PRECISION)
        self._update_dep_var()

    def _get_indep_min(self):
        return self._indep_min

    @putil.pcontracts.contract(indep_min='real_num')
    def _set_indep_min(self, indep_min):
        self._exh.add_exception(
            exname='min_max',
            extype=ValueError,
            exmsg='Argument `indep_min` is greater than argument `indep_max`'
        )
        self._exh.raise_exception_if(
            exname='min_max',
            condition=(self.indep_max is not None) and
                      (indep_min is not None) and
                      (self.indep_max < indep_min)
        )
        self._indep_min = (putil.eng.round_mantissa(indep_min, PRECISION)
                          if not isinstance(indep_min, int) else
                          indep_min)
        # Apply minimum and maximum range bounding and assign it to
        # self._indep_var and thus this is what self.indep_var returns
        self._update_indep_var()
        self._update_dep_var()

    def _get_indep_max(self):
        return self._indep_max

    @putil.pcontracts.contract(indep_max='real_num')
    def _set_indep_max(self, indep_max):
        self._exh.add_exception(
            exname='min_max',
            extype=ValueError,
            exmsg='Argument `indep_min` is greater than argument `indep_max`'
        )
        self._exh.raise_exception_if(
            exname='min_max',
            condition=(self.indep_min is not None) and
                      (indep_max is not None) and
                      (indep_max < self.indep_min)
        )
        self._indep_max = (putil.eng.round_mantissa(indep_max, PRECISION)
                          if not isinstance(indep_max, int) else
                          indep_max)
        # Apply minimum and maximum range bounding and assign it to
        # self._indep_var and thus this is what self.indep_var returns
        self._update_indep_var()
        self._update_dep_var()

    def _update_indep_var(self):
        """
        Update independent variable according to its minimum and maximum limits
        """
        self._exh.add_exception(
            exname='empty',
            extype=ValueError,
            exmsg='Argument `indep_var` is empty after '
                  '`indep_min`/`indep_max` range bounding'
        )
        if self._raw_indep_var is not None:
            min_indexes = (self._raw_indep_var >=
                (self.indep_min if self.indep_min is not None else self._raw_indep_var[0])
            )
            max_indexes = (self._raw_indep_var <=
                (self.indep_max if self.indep_max is not None else self._raw_indep_var[-1])
            )
            self._indep_var_indexes = numpy.where(min_indexes & max_indexes)
            super(CsvSource, self)._set_indep_var(
                self._raw_indep_var[self._indep_var_indexes]
            )
            self._exh.raise_exception_if(
                exname='empty',
                condition=len(self.indep_var) == 0
            )

    def _update_dep_var(self):
        """
        Update dependent variable (if assigned) to match the independent
        variable range bounding
        """
        self._dep_var = self._raw_dep_var
        if (self._indep_var_indexes is not None) and (self._raw_dep_var is not None):
            super(CsvSource, self)._set_dep_var(
                self._raw_dep_var[self._indep_var_indexes]
            )

    def _get_fproc(self):
        return self._fproc

    @putil.pcontracts.contract(fproc='function')
    def _set_fproc(self, fproc):
        self._exh.add_exception(
            exname='min_args',
            extype=ValueError,
            exmsg='Argument `fproc` (function *[func_name]*) '
                  'does not have at least 2 arguments'
        )
        if fproc is not None:
            args = putil.pinspect.get_function_args(fproc)
            self._exh.raise_exception_if(
                exname='min_args',
                condition=(fproc is not None) and
                          (len(args) < 2) and
                          ('*args' not in args) and
                          ('**kwargs' not in args),
                edata={'field':'func_name', 'value':fproc.__name__}
            )
        self._fproc = fproc
        self._check_fproc_eargs()
        self._process_data()

    def _get_fproc_eargs(self):
        return self._fproc_eargs

    @putil.pcontracts.contract(fproc_eargs='None|dict')
    def _set_fproc_eargs(self, fproc_eargs):
        # Check that extra arguments to see if they are in the function definition
        self._fproc_eargs = fproc_eargs
        self._check_fproc_eargs()
        self._process_data()

    def _check_fproc_eargs(self):
        """
        Checks that the extra arguments are in the processing
        function definition
        """
        self._exh.add_exception(
            exname='extra_args',
            extype=ValueError,
            exmsg='Extra argument `*[arg_name]*` not found in argument '
                  '`fproc` (function *[func_name]*) definition'
        )
        if (self.fproc is not None) and (self.fproc_eargs is not None):
            args = putil.pinspect.get_function_args(self._fproc)
            for key in self.fproc_eargs:
                self._exh.raise_exception_if(
                    exname='extra_args',
                    condition=(key not in args) and
                              ('*args' not in args) and
                              ('**kwargs' not in args),
                    edata=[
                        {'field':'func_name', 'value':self.fproc.__name__},
                        {'field':'arg_name', 'value':key}
                    ]
                )

    def _check_indep_col_label(self):
        """
        Check that independent column label can be found in
        comma-separated file header
        """
        self._exh.add_exception(
            exname='label',
            extype=ValueError,
            exmsg='Column *[col_name]* (independent column label) could not'
                  ' be found in comma-separated file *[fname]* header'
        )
        self._exh.raise_exception_if(
            exname='label',
            condition=(self._csv_obj is not None) and
                      (self.indep_col_label is not None) and
                      (self.indep_col_label not in self._csv_obj.header),
            edata=[
                {'field':'col_name', 'value':self.indep_col_label},
                {'field':'fname', 'value':self.fname}
            ]
        )

    def _check_dep_col_label(self):
        """
        Check that dependent column label can be found in
        comma-separated file header
        """
        self._exh.add_exception(
            exname='label',
            extype=ValueError,
            exmsg='Column *[col_name]* (dependent column label) could not be'
                  ' found in comma-separated file *[fname]* header'
        )
        self._exh.raise_exception_if(
            exname='label',
            condition=(self._csv_obj is not None) and
                      (self.dep_col_label is not None) and
                      (self.dep_col_label not in self._csv_obj.header),
            edata=[
                {'field':'col_name', 'value':self.dep_col_label},
                {'field':'fname', 'value':self.fname}
            ]
        )

    def _check_dfilter(self):
        """
        Check that columns in filter specification can be found in
        comma-separated file header
        """
        self._exh.add_exception(
            exname='dfilter',
            extype=ValueError,
            exmsg='Column *[col_name]* in data filter not found '
                  'in comma-separated file *[fname]* header'
        )
        if (self._csv_obj is not None) and (self.dfilter is not None):
            for key in self.dfilter:
                self._exh.raise_exception_if(
                    exname='dfilter',
                    condition=key not in self._csv_obj.header,
                    edata=[
                        {'field':'col_name', 'value':key},
                        {'field':'fname', 'value':self.fname}
                    ]
                )

    def _apply_dfilter(self):
        """ Apply data filters to loaded data """
        self._check_dfilter()
        if ((self.dfilter is not None) and
            (len(self.dfilter) > 0) and
            (self._csv_obj is not None)):
            self._csv_obj.dfilter = self.dfilter
        elif self._csv_obj is not None:
            self._csv_obj.reset_dfilter()
        self._get_indep_var_from_file()
        self._get_dep_var_from_file()

    def _get_indep_var_from_file(self):
        """
        Retrieve independent data variable from comma-separated values file
        """
        self._exh.add_exception(
            exname='empty',
            extype=ValueError,
            exmsg='Filtered independent variable is empty'
        )
        if (self._csv_obj is not None) and (self.indep_col_label is not None):
            # When object is given all arguments at construction the column
            # label checking cannot happen at property assignment because file
            # data is not yet loaded
            self._check_indep_col_label()
            data = numpy.array([
                row[0] for row in self._csv_obj.data(
                    self.indep_col_label,
                    filtered=True
                )
            ])
            self._exh.raise_exception_if(
                exname='empty',
                condition=(len(data) == 0) or
                          bool(((data == [None]*len(data)).all()))
            )
            # Flip data if it is in descending order (affects interpolation)
            if max(numpy.diff(data)) < 0:
                self._reverse_data = True
                data = data[::-1]
            self._set_indep_var(data)

    def _get_dep_var_from_file(self):
        """
        Retrieve dependent data variable from comma-separated values file
        """
        self._exh.add_exception(
            exname='empty',
            extype=ValueError,
            exmsg='Filtered dependent variable is empty'
        )
        if (self._csv_obj is not None) and (self.dep_col_label is not None):
            # When object is given all arguments at construction the column
            # label checking cannot happen at property assignment because file
            # data is not yet loaded
            self._check_dep_col_label()
            data = numpy.array([
                row[0] for row in self._csv_obj.data(
                    self.dep_col_label,
                    filtered=True
                )
            ])
            self._exh.raise_exception_if(
                exname='empty',
                condition=(len(data) == 0) or
                          bool(((data == [None]*len(data)).all()))
            )
            self._set_dep_var(data[::-1] if self._reverse_data else data)

    def _process_data(self):
        """ Process data through call-back function """
        # pylint: disable=W0703
        self._exh.add_exception(
            exname='invalid_ret',
            extype=TypeError,
            exmsg='Argument `fproc` (function *[func_name]*) return value is not valid'
        )
        self._exh.add_exception(
            exname='illegal_ret',
            extype=RuntimeError,
            exmsg='Argument `fproc` (function *[func_name]*) '
                  'returned an illegal number of values'
        )
        self._exh.add_exception(
            exname='length',
            extype=ValueError,
            exmsg='Processed independent and dependent variables '
                  'are of different length'
        )
        self._exh.add_exception(
            exname='empty_indep_var',
            extype=ValueError,
            exmsg='Processed independent variable is empty'
        )
        self._exh.add_exception(
            exname='illegal_indep_var',
            extype=TypeError,
            exmsg='Processed independent variable is not valid'
        )
        self._exh.add_exception(
            exname='empty_dep_var',
            extype=ValueError,
            exmsg='Processed dependent variable is empty'
        )
        self._exh.add_exception(
            exname='illegal_dep_var',
            extype=TypeError,
            exmsg='Processed dependent variable is not valid'
        )
        self._exh.add_exception(
            exname='proc_fun_ex',
            extype=RuntimeError,
            exmsg='Processing function *[func_name]* raised an exception when '
                  'called with the following arguments:\n'
                  'indep_var: *[indep_var_value]*\n'
                  'dep_var: *[dep_var_value]*\n'
                  'fproc_eargs: *[fproc_eargs_value]*\n'
                  'Exception error: *[exception_error_message]*'
        )
        if ((self.fproc is not None) and
           (self.indep_var is not None) and
           (self.dep_var is not None)):
            try:
                ret = (self.fproc(self.indep_var, self.dep_var)
                      if self.fproc_eargs is None else
                      self.fproc(self.indep_var, self.dep_var, **self.fproc_eargs))
            except Exception as error_msg:
                if (self.fproc_eargs is None) or (not self.fproc_eargs):
                    eamsg = 'None'
                else:
                    eamsg = '\n'
                    for key, value in self.fproc_eargs.items():
                        eamsg += '   {0}: {1}\n'.format(key, value)
                    eamsg = eamsg.rstrip()
                self._exh.raise_exception_if(
                    exname='proc_fun_ex',
                    condition=True,
                    edata=[
                        {'field':'func_name', 'value':self.fproc.__name__},
                        {
                            'field':'indep_var_value',
                            'value':putil.eng.pprint_vector(
                                self.indep_var,
                                limit=10
                            )
                        },
                        {
                            'field':'dep_var_value',
                            'value':putil.eng.pprint_vector(
                                self.indep_var,
                                limit=10
                            )
                        },
                        {'field':'fproc_eargs_value', 'value':eamsg},
                        {'field':'exception_error_message', 'value':str(error_msg)}
                    ]
                )
            self._exh.raise_exception_if(
                exname='invalid_ret',
                condition=(not isinstance(ret, list)) and (not isinstance(ret, tuple)),
                edata={'field':'func_name', 'value':self.fproc.__name__}
            )
            self._exh.raise_exception_if(
                exname='illegal_ret',
                condition=len(ret) != 2,
                edata={'field':'func_name', 'value':self.fproc.__name__}
            )
            indep_var = ret[0]
            dep_var = ret[1]
            self._exh.raise_exception_if(
                exname='empty_indep_var',
                condition=isinstance(indep_var, type(numpy.array([]))) and
                          ((len(indep_var) == 0) or
                          bool(((indep_var == [None]*len(indep_var)).all())))
            )
            self._exh.raise_exception_if(
                exname='illegal_indep_var',
                condition=_check_increasing_real_numpy_vector(indep_var)
            )
            self._exh.raise_exception_if(
                exname='empty_dep_var',
                condition=isinstance(dep_var, type(numpy.array([]))) and
                          ((len(dep_var) == 0) or
                          bool(((dep_var == [None]*len(dep_var)).all())))
            )
            self._exh.raise_exception_if(
                exname='illegal_dep_var',
                condition=_check_real_numpy_vector(dep_var)
            )
            self._exh.raise_exception_if(
                exname='length',
                condition=len(indep_var) != len(dep_var)
            )
            # The processing function could potentially expand (say, via
            # interpolation) or shorten the data set length. To avoid errors
            # that dependent and independent variables have different number
            # of elements while setting the first processed variable (either
            # independent or dependent) both are "reset" to some dummy
            # value first
            self._raw_indep_var = None
            self._raw_dep_var = None
            self._indep_var_indexes = None
            self._set_indep_var(indep_var)
            self._set_dep_var(dep_var)

    def __str__(self):
        r"""
        Prints source information. For example:

        .. =[=cog
        .. import docs.support.incfile
        .. docs.support.incfile.incfile('plot_example_3.py', cog)
        .. =]=
        .. code-block:: python

            # plot_example_3.py
            import putil.misc, putil.pcsv, sys

            def cwrite(fobj, data):
                if sys.version_info.major == 2:
                    fobj.write(data)
                else:
                    fobj.write(bytes(data, 'ascii'))

            def write_csv_file(file_handle):
                cwrite(file_handle, 'Col1,Col2\n')
                cwrite(file_handle, '0E-12,10\n')
                cwrite(file_handle, '1E-12,0\n')
                cwrite(file_handle, '2E-12,20\n')
                cwrite(file_handle, '3E-12,-10\n')
                cwrite(file_handle, '4E-12,30\n')

            # indep_var is a Numpy vector, in this example  time,
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

        .. =[=end=]=

        .. code-block:: python

            >>> from __future__ import print_function
            >>> import docs.support.plot_example_3
            >>> obj = docs.support.plot_example_3.create_csv_source()
            >>> print(obj)  #doctest: +ELLIPSIS
            File name: ...
            Data filter: None
            Independent column label: Col1
            Dependent column label: Col2
            Processing function: proc_func1
            Processing function extra arguments: None
            Independent variable minimum: 2e-12
            Independent variable maximum: +inf
            Independent variable: [ 2.0, 3.0, 4.0 ]
            Dependent variable: [ 0.0, -30.0, 10.0 ]

        """
        ret = ''
        ret += 'File name: {0}\n'.format(self.fname)
        ret += 'Data filter: {0}\n'.format(
            self.dfilter if self.dfilter is None else ''
        )
        if self.dfilter is not None:
            odfilter = OrderedDict(sorted(self.dfilter.items(), key=lambda t: t[0]))
            for key, value in odfilter.items():
                ret += '   {0}: {1}\n'.format(key, value)
        ret += 'Independent column label: {0}\n'.format(self.indep_col_label)
        ret += 'Dependent column label: {0}\n'.format(self.dep_col_label)
        ret += 'Processing function: {0}\n'.format(
            'None' if self.fproc is None else self.fproc.__name__
        )
        ret += 'Processing function extra arguments: {0}\n'.format(
            self.fproc_eargs if self.fproc_eargs is None else ''
        )
        if self.fproc_eargs is not None:
            ofproc_eargs = OrderedDict(sorted(
                self.fproc_eargs.items(),
                key=lambda t: t[0]
            ))
            for key, value in ofproc_eargs.items():
                ret += '   {0}: {1}\n'.format(key, value)
        ret += 'Independent variable minimum: {0}\n'.format(
            '-inf' if self.indep_min is None else self.indep_min
        )
        ret += 'Independent variable maximum: {0}\n'.format(
            '+inf' if self.indep_max is None else self.indep_max
        )
        ret += super(CsvSource, self).__str__()
        return ret

    # Managed attributes
    dep_col_label = property(
        _get_dep_col_label,
        _set_dep_col_label,
        doc='Dependent column label (column name)'
    )
    r"""
    Gets or sets the dependent variable column label (column name)

    :type:  string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.dep_col_label

    :raises: (when assigned)

     * RuntimeError (Argument \`dep_col_label\` is not valid)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned an
       illegal number of values)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value is
       not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Column *[col_name]* (dependent column label) could not be
       found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* in data filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """

    # dep_var is read only
    dep_var = property(
        DataSource._get_dep_var,
        doc='Dependent variable Numpy vector (read only)'
    )
    """
    Gets the dependent variable Numpy vector
    """

    dfilter = property(_get_dfilter, _set_dfilter, doc='Data filter dictionary')
    r"""
    Gets or sets the data filter

    :type: :ref:`CsvDataFilter`

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.dfilter

    :raises: (when assigned)

     * RuntimeError (Argument \`dfilter\` is not valid)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned an
       illegal number of values)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value is
       not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Argument \`dfilter\` is empty)

     * ValueError (Column *[col_name]* in data filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """

    fname = property(
        _get_fname,
        _set_fname,
        doc='Comma-separated file name'
    )
    r"""
    Gets or sets the comma-separated values file from which data series is to
    be extracted. It is assumed that the first line of the file contains
    unique headers for each column

    :type:      string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.fname

    :raises: (when assigned)

     * OSError (File \`*[file_name]*\` could not be found)

     * RuntimeError (Argument \`col\` is not valid)

     * RuntimeError (Argument \`dep_var\` is not valid)

     * RuntimeError (Argument \`dfilter\` is not valid)

     * RuntimeError (Argument \`filtered\` is not valid)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned an
       illegal number of values)

     * RuntimeError (Argument \`indep_var\` is not valid)

     * RuntimeError (Column headers are not unique)

     * RuntimeError (File *[fname]* has no valid data)

     * RuntimeError (File *[fname]* is empty)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value is
       not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Argument \`dfilter\` is empty)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

     * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the same
       number of elements)

     * ValueError (Column *[col_name]* (dependent column label) could not be
       found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* (independent column label) could not be
       found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* in data filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Column *[column_name]* not found in header)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """

    fproc = property(
        _get_fproc,
        _set_fproc,
        doc='Processing function'
    )
    r"""
    Gets or sets the data processing function pointer. The processing function
    is useful for "light" data massaging, like scaling, unit conversion, etc.;
    it is called after the data has been retrieved from the comma-separated
    values file and the resulting filtered data set has been bounded
    (if applicable).

    The processing function is given two arguments, a Numpy vector containing
    the independent variable array (first argument) and a Numpy vector
    containing the dependent variable array (second argument).
    The expected return value is a two-item Numpy vector tuple, its first
    item being the processed independent variable array, and the second
    item being the processed dependent variable array. One valid processing
    function could be:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('plot_example_3.py', cog, '16-23')
    .. =]=
    .. code-block:: python

            cwrite(file_handle, '0E-12,10\n')
            cwrite(file_handle, '1E-12,0\n')
            cwrite(file_handle, '2E-12,20\n')
            cwrite(file_handle, '3E-12,-10\n')
            cwrite(file_handle, '4E-12,30\n')

        # indep_var is a Numpy vector, in this example  time,
        # in seconds. dep_var is a Numpy vector

    .. =[=end=]=

    :type: :ref:`Function`

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.fproc

    :raises: (when assigned)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned an
       illegal number of values)

     * RuntimeError (Argument \`fproc\` is not valid)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value is
       not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Argument \`fproc\` (function *[func_name]*) does not have
       at least 2 arguments)

     * ValueError (Extra argument \`*[arg_name]*\` not found in argument
       \`fproc\` (function *[func_name]*) definition)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """

    fproc_eargs = property(
        _get_fproc_eargs,
        _set_fproc_eargs,
        doc='Processing function extra argument dictionary'
    )
    # pylint: disable=W1401
    r"""
    Gets or sets the extra arguments for the data processing function. The
    arguments are specified by key-value pairs of a dictionary, for each
    dictionary element the dictionary key specifies the argument name and the
    dictionary value specifies the argument value. The extra parameters are
    passed by keyword so they must appear in the function definition explicitly
    or keyword variable argument collection must be used
    (:code:`**kwargs`, for example).

    :type:  dictionary, default is None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.fproc_eargs

    :raises: (when assigned)

     * RuntimeError (Argument \`fproc_eargs\` is not valid)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned an
       illegal number of values)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value is
       not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Extra argument \`*[arg_name]*\` not found in argument
       \`fproc\` (function *[func_name]*) definition)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]

    For example:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('plot_example_5.py', cog)
    .. =]=
    .. code-block:: python

        # plot_example_5.py
        import putil.misc, putil.pcsv, sys
        if sys.version_info.major == 2:
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

    .. =[=end=]=

    .. code-block:: python

        >>> from __future__ import print_function
        >>> import docs.support.plot_example_5
        >>> obj = docs.support.plot_example_5.create_csv_source()
        >>> print(obj)  #doctest: +ELLIPSIS
        File name: ...
        Data filter: None
        Independent column label: Col1
        Dependent column label: Col2
        Processing function: proc_func2
        Processing function extra arguments: None
        Independent variable minimum: -inf
        Independent variable maximum: +inf
        Independent variable: [ 10, 11, 12, 13, 14 ]
        Dependent variable: [ 16, 6, 26, -4, 36 ]

    """

    indep_col_label = property(
        _get_indep_col_label,
        _set_indep_col_label,
        doc='Independent column label (column name)'
    )
    r"""
    Gets or sets the independent variable column label (column name)

    :type:  string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.indep_col_label

    :raises: (when assigned)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned an
       illegal number of values)

     * RuntimeError (Argument \`indep_col_label\` is not valid)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value is
       not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Column *[col_name]* (independent column label) could not be
       found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* in data filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """

    indep_max = property(
        _get_indep_max,
        _set_indep_max,
        doc='Maximum of independent variable'
    )
    r"""
    Gets or sets the maximum independent variable limit

    :type: :ref:`RealNum`, default is None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.indep_max

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_max\` is not valid)

     * ValueError (Argument \`indep_min\` is greater than argument
       \`indep_max\`)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

    .. [[[end]]]
    """

    indep_min = property(
        _get_indep_min,
        _set_indep_min,
        doc='Minimum of independent variable'
    )
    r"""
    Gets or sets the minimum independent variable limit

    :type: :ref:`RealNum`, default is None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.indep_min

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * ValueError (Argument \`indep_min\` is greater than argument
       \`indep_max\`)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

    .. [[[end]]]
    """

    # indep_var is read only
    indep_var = property(
        DataSource._get_indep_var,
        doc='Independent variable Numpy vector (read only)'
    )
    """
    Gets the independent variable Numpy vector
    """
