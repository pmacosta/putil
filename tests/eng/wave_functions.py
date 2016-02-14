# wave_functions.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# PyPI imports
import numpy
import pytest
# Putil imports
import putil.eng
import putil.test
from .support import cmp_vectors, std_obj


###
# Test functions
###
def test_acos():
    """ Test acos function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    obj = putil.eng.acos(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.arccos(dep_vector))
    assert obj.indep_name == 'acos(obj)'
    assert obj.dep_units == 'rad'


@pytest.mark.wave_functions
def test_acos_exceptions():
    """ Test acos function exceptions """
    putil.test.assert_exception(
        putil.eng.acos,
        {'wave':'a'},
        RuntimeError,
        'Argument `wave` is not valid'
    )
    dep_vector = numpy.array([-1.01, 0.98, 0.5])
    obj_a = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    dep_vector = numpy.array([1.01, 0.98, 0.5])
    obj_b = std_obj(indep_name='obj_b', dep_vector=dep_vector)
    for item in [obj_a, obj_b]:
        putil.test.assert_exception(
            putil.eng.acos, {'wave':item}, ValueError, 'Math domain error'
        )


def test_acosh():
    """ Test acosh function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    obj = putil.eng.acosh(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.arccosh(dep_vector))
    assert obj.indep_name == 'acosh(obj)'
    assert obj.dep_units == ''


@pytest.mark.wave_functions
def test_acosh_exceptions():
    """ Test acosh function exceptions """
    putil.test.assert_exception(
        putil.eng.acosh,
        {'wave':'a'},
        RuntimeError,
        'Argument `wave` is not valid'
    )
    dep_vector = numpy.array([0.99, 0.98, 0.5])
    obj = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    putil.test.assert_exception(
        putil.eng.acosh, {'wave':obj}, ValueError, 'Math domain error'
    )
