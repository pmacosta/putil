# data_source2.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,W0105,W0212

import abc

import putil.exh


###
# Classes
###
class DataSource(object):
    """
    Abstract base class for data sources. The following example is a minimal
    implementation of a data source class:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('plot_example_2.py', cog)
    .. =]=
    .. code-block:: python

        # plot_example_2.py
        import putil.plot

        class MySource(putil.plot.DataSource, object):
            def __init__(self):
                super(MySource, self).__init__()

            def __str__(self):
                return super(MySource, self).__str__()

            def _set_dep_var(self, dep_var):
                super(MySource, self)._set_dep_var(dep_var)

            def _set_indep_var(self, indep_var):
                super(MySource, self)._set_indep_var(indep_var)

            dep_var = property(
                putil.plot.DataSource._get_dep_var, _set_dep_var
            )

            indep_var = property(
                putil.plot.DataSource._get_indep_var, _set_indep_var
            )

    .. =[=end=]=

    .. warning:: The abstract methods listed below need to be defined
                 in a child class

    """
    # pylint: disable=R0903,R0921
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self._exh = putil.exh.get_or_create_exh_obj()
        self._dep_var, self._indep_var = None, None

    def _get_dep_var(self):
        return self._dep_var

    def _get_indep_var(self):
        return self._indep_var

    @abc.abstractmethod
    def __str__(self):
        """
        Pretty prints the stored independent and dependent variables.
        For example:

        .. code-block:: python

            >>> from __future__ import print_function
            >>> import numpy, docs.support.plot_example_2
            >>> obj = docs.support.plot_example_2.MySource()
            >>> obj.indep_var = numpy.array([1, 2, 3])
            >>> obj.dep_var = numpy.array([-1, 1, -1])
            >>> print(obj)
            Independent variable: [ 1.0, 2.0, 3.0 ]
            Dependent variable: [ -1.0, 1.0, -1.0 ]
        """
        ret = ''
        ret += 'Independent variable: {0}\n'.format(putil.eng.pprint_vector(
            self.indep_var,
            width=50,
            indent=len('Independent variable: ')
        ))
        ret += 'Dependent variable: {0}'.format(putil.eng.pprint_vector(
            self.dep_var,
            width=50,
            indent=len('Dependent variable: ')
        ))
        return ret

    @abc.abstractmethod
    def _set_dep_var(self, dep_var):
        """
        Sets the dependent variable (casting to float type). For example:

        .. code-block:: python

            >>> import numpy, docs.support.plot_example_2
            >>> obj = docs.support.plot_example_2.MySource()
            >>> obj.dep_var = numpy.array([-1, 1, -1])
            >>> obj.dep_var
            array([-1.,  1., -1.])
        """
        self._dep_var = dep_var.astype(float)

    @abc.abstractmethod
    def _set_indep_var(self, indep_var):
        """
        Sets the independent variable (casting to float type). For example:

        .. code-block:: python

            >>> import numpy, docs.support.plot_example_2
            >>> obj = docs.support.plot_example_2.MySource()
            >>> obj.indep_var = numpy.array([1, 2, 3])
            >>> obj.indep_var
            array([ 1.,  2.,  3.])
        """
        self._indep_var = indep_var.astype(float)

    def _get_complete(self):
        """
        Returns True if object is fully specified, otherwise returns False
        """
        self._exh.add_exception(
            exname='num_elements',
            extype=ValueError,
            exmsg='Arguments `indep_var` and `dep_var` must have '
                  'the same number of elements'
        )
        self._exh.raise_exception_if(
            exname='num_elements',
            condition=(self._dep_var is not None) and
                      (self._indep_var is not None) and
                      (len(self._dep_var) != len(self._indep_var))
        )
        return (self.indep_var is not None) and (self.dep_var is not None)

    indep_var = abc.abstractproperty(
        _get_indep_var,
        _set_indep_var,
        doc='Independent variable Numpy vector'
    )

    dep_var = abc.abstractproperty(
        _get_dep_var,
        _set_dep_var,
        doc='Dependent variable Numpy vector'
    )

    _complete = property(
        _get_complete,
        doc='Flag that indicates whether the series '
            'is plottable (True) or not (False)'
    )
