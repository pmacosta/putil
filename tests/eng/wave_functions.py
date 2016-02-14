# wave_functions.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import math
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
    dep_vector = numpy.array([0.99, 0.98, 0.5])
    obj = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    putil.test.assert_exception(
        putil.eng.acosh, {'wave':obj}, ValueError, 'Math domain error'
    )


def test_asin():
    """ Test asin function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    obj = putil.eng.asin(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.arcsin(dep_vector))
    assert obj.indep_name == 'asin(obj)'
    assert obj.dep_units == 'rad'


@pytest.mark.wave_functions
def test_asin_exceptions():
    """ Test asin function exceptions """
    dep_vector = numpy.array([-1.01, 0.98, 0.5])
    obj_a = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    dep_vector = numpy.array([1.01, 0.98, 0.5])
    obj_b = std_obj(indep_name='obj_b', dep_vector=dep_vector)
    for item in [obj_a, obj_b]:
        putil.test.assert_exception(
            putil.eng.asin, {'wave':item}, ValueError, 'Math domain error'
        )


def test_asinh():
    """ Test asinh function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    obj = putil.eng.asinh(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.arcsinh(dep_vector))
    assert obj.indep_name == 'asinh(obj)'
    assert obj.dep_units == ''


def test_atan():
    """ Test atan function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    obj = putil.eng.atan(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.arctan(dep_vector))
    assert obj.indep_name == 'atan(obj)'
    assert obj.dep_units == 'rad'


def test_atanh():
    """ Test atanh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    obj = putil.eng.atanh(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.arctanh(dep_vector))
    assert obj.indep_name == 'atanh(obj)'
    assert obj.dep_units == ''


@pytest.mark.wave_functions
def test_atanh_exceptions():
    """ Test atanh function exceptions """
    dep_vector = numpy.array([-1.01, 0.98, 0.5])
    obj_a = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    dep_vector = numpy.array([1.01, 0.98, 0.5])
    obj_b = std_obj(indep_name='obj_b', dep_vector=dep_vector)
    for item in [obj_a, obj_b]:
        putil.test.assert_exception(
            putil.eng.atanh, {'wave':item}, ValueError, 'Math domain error'
        )


def test_ceil():
    """ Test ceil function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    obj = putil.eng.ceil(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.array([11.0, 2.0, 1.0]))
    assert obj.indep_name == 'ceil(obj)'
    assert obj.dep_units == 'Volts'


def test_cos():
    """ Test cos function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    obj = putil.eng.cos(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.cos(dep_vector))
    assert obj.indep_name == 'cos(obj)'
    assert obj.dep_units == ''


def test_cosh():
    """ Test cosh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    obj = putil.eng.cosh(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.cosh(dep_vector))
    assert obj.indep_name == 'cosh(obj)'
    assert obj.dep_units == ''


def test_db():
    """ Test db function behavior """
    dep_vector = numpy.array([10, 100, 1000])
    obj = putil.eng.db(std_obj(indep_name='obj', dep_vector=dep_vector))
    assert cmp_vectors(obj.dep_vector, numpy.array([20.0, 40.0, 60.0]))
    assert obj.indep_name == 'db(obj)'
    assert obj.dep_units == 'dB'


@pytest.mark.wave_functions
def test_db_exceptions():
    """ Test db function exceptions """
    dep_vector = numpy.array([0, 0.98, 0.5])
    obj = std_obj(indep_name='obj', dep_vector=dep_vector)
    putil.test.assert_exception(
        putil.eng.db, {'wave':obj}, ValueError, 'Math domain error'
    )


@pytest.mark.wave_functions
def test_funcs_exceptions():
    """ Test argument wave not valid exception for multiple functions """
    items = [
        putil.eng.acos, putil.eng.acosh, putil.eng.asin, putil.eng.asinh,
        putil.eng.atan, putil.eng.atanh, putil.eng.ceil,
        putil.eng.cos, putil.eng.cosh, putil.eng.db, putil.eng.to_complex,
        putil.eng.to_float, putil.eng.to_int
    ]
    for item in items:
        putil.test.assert_exception(
            item, {'wave':'a'}, RuntimeError, 'Argument `wave` is not valid'
        )


def test_to_complex():
    """ Test to_to_complex method behavior """
    obj_a = putil.eng.Waveform(
        indep_vector=numpy.array([1, 2]),
        dep_vector=numpy.array([3, 4]),
        indep_name='obj_b'
    )
    obj_b = putil.eng.to_complex(obj_a)
    assert cmp_vectors(obj_b.dep_vector, numpy.array([3+0j, 4+0j]))
    assert obj_b.dep_vector.dtype.name.startswith('complex')


def test_to_float():
    """ Test to_float method behavior """
    obj_a = std_obj('obj_a')
    obj_b = putil.eng.to_float(obj_a)
    assert cmp_vectors(obj_b.dep_vector, numpy.array([6.0, 5.0, 4.0]))
    assert obj_b.dep_vector.dtype.name.startswith('float')


@pytest.mark.wave_functions
def test_to_float_exceptions():
    """ Test to_float function exceptions """
    dep_vector = numpy.array([0.99, 1+3j, 0.5])
    obj = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    putil.test.assert_exception(
        putil.eng.to_float,
        {'wave':obj},
        TypeError,
        'Cannot convert complex to float'
    )


def test_to_int():
    """ Test to_int method behavior """
    obj_a = std_obj('obj_a', dep_vector=numpy.array([5.5, 1.3, 3.4]))
    assert (putil.eng.to_int(obj_a).dep_vector == numpy.array([5, 1, 3])).all()


@pytest.mark.wave_functions
def test_to_int_exceptions():
    """ Test to_int function exceptions """
    dep_vector = numpy.array([0.99, 1+3j, 0.5])
    obj = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    putil.test.assert_exception(
        putil.eng.to_int,
        {'wave':obj},
        TypeError,
        'Cannot convert complex to integer'
    )
