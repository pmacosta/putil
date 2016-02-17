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
    cmp_vectors(obj.dep_vector, numpy.arccos(dep_vector))
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
    cmp_vectors(obj.dep_vector, numpy.arccosh(dep_vector))
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
    cmp_vectors(obj.dep_vector, numpy.arcsin(dep_vector))
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
    cmp_vectors(obj.dep_vector, numpy.arcsinh(dep_vector))
    assert obj.indep_name == 'asinh(obj)'
    assert obj.dep_units == ''


def test_atan():
    """ Test atan function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    obj = putil.eng.atan(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.arctan(dep_vector))
    assert obj.indep_name == 'atan(obj)'
    assert obj.dep_units == 'rad'


def test_atanh():
    """ Test atanh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    obj = putil.eng.atanh(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.arctanh(dep_vector))
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


def test_average():
    """ Test average function behavior """
    obj = std_obj(indep_name='obj', interp='CONTINUOUS', indep_scale='LINEAR')
    act = putil.eng.average(obj)
    cmp_vectors(act.dep_vector, numpy.array([6.0, 5.5, 5.0]))
    assert act.indep_name == 'average(obj)'
    assert act.dep_units == 'Volts'
    act = putil.eng.average(obj, indep_min=1.5)
    cmp_vectors(act.dep_vector, numpy.array([5.5, 5.25, 4.8333333333333]))
    act = putil.eng.average(obj, indep_max=2.5)
    cmp_vectors(act.dep_vector, numpy.array([6, 5.5, 5.166666666666]))
    act = putil.eng.average(obj, indep_min=1.5, indep_max=2.5)
    cmp_vectors(act.dep_vector, numpy.array([5.5, 5.25, 5.0]))


@pytest.mark.wave_functions
def test_bound_exceptions():
    """ Test exceptions of functions that have range bounding """
    obj = std_obj(indep_name='obj')
    items = [putil.eng.average]
    for item in items:
        putil.test.assert_exception(
            item,
            {'wave':obj, 'indep_min':'a'},
            RuntimeError,
            'Argument `indep_min` is not valid'
        )
        putil.test.assert_exception(
            item,
            {'wave':obj, 'indep_max':'a'},
            RuntimeError,
            'Argument `indep_max` is not valid'
        )
        putil.test.assert_exception(
            item,
            {'wave':obj, 'indep_min':1.5, 'indep_max':1},
            RuntimeError,
            'Incongruent `indep_min` and `indep_max` arguments'
        )
        putil.test.assert_exception(
            item,
            {'wave':obj, 'indep_min':0},
            RuntimeError,
            'Argument `indep_min` is not valid'
        )
        putil.test.assert_exception(
            item,
            {'wave':obj, 'indep_max':10},
            RuntimeError,
            'Argument `indep_max` is not valid'
        )


def test_ceil():
    """ Test ceil function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    obj = putil.eng.ceil(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.array([11.0, 2.0, 1.0]))
    assert obj.indep_name == 'ceil(obj)'
    assert obj.dep_units == 'Volts'


def test_cos():
    """ Test cos function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    obj = putil.eng.cos(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.cos(dep_vector))
    assert obj.indep_name == 'cos(obj)'
    assert obj.dep_units == ''


def test_cosh():
    """ Test cosh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    obj = putil.eng.cosh(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.cosh(dep_vector))
    assert obj.indep_name == 'cosh(obj)'
    assert obj.dep_units == ''


def test_db():
    """ Test db function behavior """
    dep_vector = numpy.array([10, 100, 1000])
    obj = putil.eng.db(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.array([20.0, 40.0, 60.0]))
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


def test_exp():
    """ Test exp function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    obj = putil.eng.exp(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.exp(dep_vector))
    assert obj.indep_name == 'exp(obj)'
    assert obj.dep_units == ''


def test_floor():
    """ Test floor function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    obj = putil.eng.floor(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.array([10.0, 1.0, 1.0]))
    assert obj.indep_name == 'floor(obj)'
    assert obj.dep_units == 'Volts'


@pytest.mark.wave_functions
def test_funcs_exceptions():
    """ Test argument wave not valid exception """
    items = [
        putil.eng.acos, putil.eng.acosh, putil.eng.asin, putil.eng.asinh,
        putil.eng.atan, putil.eng.atanh, putil.eng.average, putil.eng.ceil,
        putil.eng.cos, putil.eng.cosh, putil.eng.db, putil.eng.exp,
        putil.eng.floor, putil.eng.imag, putil.eng.log, putil.eng.log10,
        putil.eng.phase, putil.eng.sin, putil.eng.sinh, putil.eng.sqrt,
        putil.eng.tan, putil.eng.tanh, putil.eng.wcomplex, putil.eng.wfloat,
        putil.eng.wint, putil.eng.wround
    ]
    for item in items:
        putil.test.assert_exception(
            item, {'wave':'a'}, RuntimeError, 'Argument `wave` is not valid'
        )


def test_imag():
    """ Test imag function behavior """
    dep_vector = numpy.array([10.41, 1+3j, 10-0.5j])
    obj = putil.eng.imag(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.array([0, 3, -0.5]))
    assert obj.indep_name == 'imag(obj)'
    assert obj.dep_units == 'Volts'


def test_log():
    """ Test log function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    obj = putil.eng.log(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.log(dep_vector))
    assert obj.indep_name == 'log(obj)'
    assert obj.dep_units == ''


def test_log10():
    """ Test log function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    obj = putil.eng.log10(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.log10(dep_vector))
    assert obj.indep_name == 'log10(obj)'
    assert obj.dep_units == ''


@pytest.mark.wave_functions
def test_log_exceptions():
    """ Test log and log10 function exceptions """
    dep_vector = numpy.array([0, 0.98, 0.5])
    obj = std_obj(indep_name='obj', dep_vector=dep_vector)
    items = [putil.eng.log, putil.eng.log10]
    for item in items:
        putil.test.assert_exception(
            item, {'wave':obj}, ValueError, 'Math domain error'
        )


def test_phase():
    """ Test phase function behavior """
    indep_vector = numpy.arange(1, 12, 1)
    dep_vector = numpy.exp(complex(0, 1)*math.pi*numpy.arange(0.25, 3, 0.25))
    obj = putil.eng.phase(
        std_obj(
            indep_name='obj', indep_vector=indep_vector, dep_vector=dep_vector
        ),
        unwrap=False
    )
    ref = math.pi*numpy.array(
        [0.25, 0.5, 0.75, 1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75]
    )
    cmp_vectors(obj.dep_vector, ref)
    assert obj.indep_name == 'phase(obj)'
    assert obj.dep_units == 'rad'
    obj = putil.eng.phase(
        std_obj(
            indep_name='obj', indep_vector=indep_vector, dep_vector=dep_vector
        ),
    )
    ref = math.pi*numpy.arange(0.25, 3, 0.25)
    cmp_vectors(obj.dep_vector, ref)
    obj = putil.eng.phase(
        std_obj(
            indep_name='obj', indep_vector=indep_vector, dep_vector=dep_vector
        ),
        unwrap=True
    )
    cmp_vectors(obj.dep_vector, ref)
    obj = putil.eng.phase(
        std_obj(
            indep_name='obj', indep_vector=indep_vector, dep_vector=dep_vector
        ),
        unwrap=True,
        rad=False
    )
    cmp_vectors(obj.dep_vector, numpy.arange(45, 534, 45))


@pytest.mark.wave_functions
def test_phase_exceptions():
    """ Test phase function exceptions """
    obj = std_obj('obj')
    items = ['a', 5.0, (1, 2)]
    for item in items:
        putil.test.assert_exception(
            putil.eng.phase,
            {'wave':obj, 'unwrap':item},
            RuntimeError, 'Argument `unwrap` is not valid'
        )
        putil.test.assert_exception(
            putil.eng.phase,
            {'wave':obj, 'rad':item},
            RuntimeError, 'Argument `rad` is not valid'
        )


def test_sin():
    """ Test sin function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    obj = putil.eng.sin(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.sin(dep_vector))
    assert obj.indep_name == 'sin(obj)'
    assert obj.dep_units == ''


def test_sinh():
    """ Test sinh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    obj = putil.eng.sinh(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.sinh(dep_vector))
    assert obj.indep_name == 'sinh(obj)'
    assert obj.dep_units == ''


def test_sqrt():
    """ Test sqrt function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    obj = putil.eng.sqrt(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.sqrt(dep_vector))
    assert obj.indep_name == 'sqrt(obj)'
    assert obj.dep_units == 'Volts**0.5'


def test_tan():
    """ Test tan function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    obj = putil.eng.tan(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.tan(dep_vector))
    assert obj.indep_name == 'tan(obj)'
    assert obj.dep_units == ''


def test_tanh():
    """ Test tanh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    obj = putil.eng.tanh(std_obj(indep_name='obj', dep_vector=dep_vector))
    cmp_vectors(obj.dep_vector, numpy.tanh(dep_vector))
    assert obj.indep_name == 'tanh(obj)'
    assert obj.dep_units == ''


def test_wcomplex():
    """ Test wcomplex method behavior """
    obj_a = putil.eng.Waveform(
        indep_vector=numpy.array([1, 2]),
        dep_vector=numpy.array([3, 4]),
        indep_name='obj_b'
    )
    obj_b = putil.eng.wcomplex(obj_a)
    cmp_vectors(obj_b.dep_vector, numpy.array([3+0j, 4+0j]))
    assert obj_b.dep_vector.dtype.name.startswith('complex')


def test_wfloat():
    """ Test wfloat method behavior """
    obj_a = std_obj('obj_a')
    obj_b = putil.eng.wfloat(obj_a)
    cmp_vectors(obj_b.dep_vector, numpy.array([6.0, 5.0, 4.0]))
    assert obj_b.dep_vector.dtype.name.startswith('float')


@pytest.mark.wave_functions
def test_wfloat_exceptions():
    """ Test wfloat function exceptions """
    dep_vector = numpy.array([0.99, 1+3j, 0.5])
    obj = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    putil.test.assert_exception(
        putil.eng.wfloat,
        {'wave':obj},
        TypeError,
        'Cannot convert complex to float'
    )


def test_wint():
    """ Test wint method behavior """
    obj_a = std_obj('obj_a', dep_vector=numpy.array([5.5, 1.3, 3.4]))
    assert (putil.eng.wint(obj_a).dep_vector == numpy.array([5, 1, 3])).all()


@pytest.mark.wave_functions
def test_wint_exceptions():
    """ Test wint function exceptions """
    dep_vector = numpy.array([0.99, 1+3j, 0.5])
    obj = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    putil.test.assert_exception(
        putil.eng.wint,
        {'wave':obj},
        TypeError,
        'Cannot convert complex to integer'
    )


def test_wround():
    """ Test wround method behavior """
    obj_a = std_obj('obj_a', dep_vector=numpy.array([5.4, 1.6, 0]))
    cmp_vectors(putil.eng.wround(obj_a).dep_vector, numpy.array([5, 2, 0]))
    obj_a = std_obj('obj_a', dep_vector=numpy.array([5.47, 1.61, 0]))
    cmp_vectors(
        putil.eng.wround(obj_a, decimals=1).dep_vector,
        numpy.array([5.5, 1.6, 0.0])
    )


@pytest.mark.wave_functions
def test_wround_exceptions():
    """ Test wround function exceptions """
    obj = std_obj(indep_name='obj')
    items = [-1, -0.0001, 'a', 3.5]
    for item in items:
        putil.test.assert_exception(
            putil.eng.wround,
            {'wave':obj, 'decimals':item},
            RuntimeError,
            'Argument `decimals` is not valid'
        )
