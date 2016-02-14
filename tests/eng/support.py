# support.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0113,C0122,E1127,R0201,W0212

# Standard library imports
from __future__ import print_function
# PyPI imports
import numpy
# Putil imports
import putil.eng
from putil.eng.constants import FP_ATOL, FP_RTOL


###
# Global variables
###
FP_PREC = 1E-10


###
# Functions
###
def cmp_vectors(vector_a, vector_b):
    """ Compare two floating point vectors to a given precision """
    flag = numpy.all(numpy.isclose(vector_a, vector_b, FP_RTOL, FP_ATOL))
    if not flag:
        print('\nVectors do not match:')
        print('Vector A: {0}'.format(vector_a))
        print('Vector B: {0}'.format(vector_b))
    return flag


def std_obj(indep_name, indep_vector=None, dep_vector=None,
    interp='STAIRCASE', dep_units='Volts'):
    """ Return a waveform with fixed parameters and given name """
    indep_vector = (
        numpy.array([1, 2, 3])
        if indep_vector is None else
        indep_vector
    )
    dep_vector = (
        numpy.array([6, 5, 4])
        if dep_vector is None else
        dep_vector
    )
    return putil.eng.Waveform(
        indep_vector=indep_vector,
        dep_vector=dep_vector,
        indep_name=indep_name,
        indep_scale='LOG',
        dep_scale='LINEAR',
        indep_units='Sec',
        dep_units=dep_units,
        interp=interp
    )
