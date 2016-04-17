# wave_functions.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import copy
import math
# PyPI imports
import numpy
import pytest
# Putil imports
import putil.eng
from putil.test import AE, AI
from .support import cmp_vectors, std_obj


###
# Helper functions
###
def strict_compare_waves(dep_vector=None, rfunc=None, rdesc=None,
    dep_units=None, nobj=None, indep_vector=None):
    """ Strictly compare waveform objects """
    # pylint: disable=R0913
    obj = rfunc(
        std_obj(
            indep_name='obj', indep_vector=indep_vector, dep_vector=dep_vector
        )
    )
    ref = std_obj(
        indep_name='{0}(obj)'.format(rdesc),
        indep_vector=indep_vector,
        dep_vector=(
            copy.copy(obj.dep_vector)
            if dep_vector is None else (
                nobj if isinstance(nobj, numpy.ndarray) else nobj(dep_vector)
            )
        ),
        dep_units=dep_units
    )
    assert obj == ref
    assert obj.indep_name == ref.indep_name


###
# Test functions
###
def test_acos():
    """ Test acos function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    strict_compare_waves(
        dep_vector, putil.eng.acos, 'acos', 'rad', numpy.arccos
    )


@pytest.mark.wave_functions
def test_acos_exceptions():
    """ Test acos function exceptions """
    dep_vector = numpy.array([-1.01, 0.98, 0.5])
    obj_a = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    dep_vector = numpy.array([1.01, 0.98, 0.5])
    obj_b = std_obj(indep_name='obj_b', dep_vector=dep_vector)
    for item in [obj_a, obj_b]:
        AE(putil.eng.acos, ValueError, 'Math domain error', item)


def test_acosh():
    """ Test acosh function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    strict_compare_waves(
        dep_vector, putil.eng.acosh, 'acosh', '', numpy.arccosh
    )


@pytest.mark.wave_functions
def test_acosh_exceptions():
    """ Test acosh function exceptions """
    dep_vector = numpy.array([0.99, 0.98, 0.5])
    obj = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    AE(putil.eng.acosh, ValueError, 'Math domain error', obj)


def test_asin():
    """ Test asin function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    strict_compare_waves(
        dep_vector, putil.eng.asin, 'asin', 'rad', numpy.arcsin
    )


@pytest.mark.wave_functions
def test_asin_exceptions():
    """ Test asin function exceptions """
    dep_vector = numpy.array([-1.01, 0.98, 0.5])
    obj_a = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    dep_vector = numpy.array([1.01, 0.98, 0.5])
    obj_b = std_obj(indep_name='obj_b', dep_vector=dep_vector)
    for item in [obj_a, obj_b]:
        AE(putil.eng.asin, ValueError, 'Math domain error', item)


def test_asinh():
    """ Test asinh function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    strict_compare_waves(
        dep_vector, putil.eng.asinh, 'asinh', '', numpy.arcsinh
    )


def test_atan():
    """ Test atan function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    strict_compare_waves(
        dep_vector, putil.eng.atan, 'atan', 'rad', numpy.arctan
    )


def test_atanh():
    """ Test atanh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    strict_compare_waves(
        dep_vector, putil.eng.atanh, 'atanh', '', numpy.arctanh
    )


@pytest.mark.wave_functions
def test_atanh_exceptions():
    """ Test atanh function exceptions """
    dep_vector = numpy.array([-1.01, 0.98, 0.5])
    obj_a = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    dep_vector = numpy.array([1.01, 0.98, 0.5])
    obj_b = std_obj(indep_name='obj_b', dep_vector=dep_vector)
    for item in [obj_a, obj_b]:
        AE(putil.eng.atanh, ValueError, 'Math domain error', item)


def test_average():
    """ Test average function behavior """
    obj = std_obj(indep_name='obj', interp='CONTINUOUS', indep_scale='LINEAR')
    act = putil.eng.average(obj)
    ref = std_obj(
        indep_name='average(obj)',
        dep_vector=numpy.array([6.0, 5.5, 5.0]),
        dep_units='Volts',
        interp='CONTINUOUS',
        indep_scale='LINEAR'
    )
    assert act == ref
    assert act.indep_name == ref.indep_name
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
    items = [
        putil.eng.average, putil.eng.derivative, putil.eng.integral,
        putil.eng.nintegral, putil.eng.nmax, putil.eng.nmin,
    ]
    for item in items:
        AI(item, 'indep_min', wave=obj, indep_min='a')
        AI(item, 'indep_max', wave=obj, indep_max='a')
        msg = 'Incongruent `indep_min` and `indep_max` arguments'
        AE(item, RuntimeError, msg, wave=obj, indep_min=1.5, indep_max=1)
        AI(item, 'indep_min', wave=obj, indep_min=0)
        AI(item, 'indep_max', wave=obj, indep_max=10)


def test_ceil():
    """ Test ceil function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    strict_compare_waves(
        dep_vector, putil.eng.ceil, 'ceil', 'Volts', numpy.ceil
    )


def test_cos():
    """ Test cos function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    strict_compare_waves(
        dep_vector, putil.eng.cos, 'cos', '', numpy.cos
    )


def test_cosh():
    """ Test cosh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    strict_compare_waves(
        dep_vector, putil.eng.cosh, 'cosh', '', numpy.cosh
    )


def test_db():
    """ Test db function behavior """
    dep_vector = numpy.array([10, 100, 1000])
    strict_compare_waves(
        dep_vector, putil.eng.db, 'db', 'dB', numpy.array([20.0, 40.0, 60.0])
    )


@pytest.mark.wave_functions
def test_db_exceptions():
    """ Test db function exceptions """
    dep_vector = numpy.array([0, 0.98, 0.5])
    obj = std_obj(indep_name='obj', dep_vector=dep_vector)
    AE(putil.eng.db, ValueError, 'Math domain error', obj)


def test_derivative():
    """ Test derivative method behavior """
    indep_vector = numpy.array([1, 2.5, 3, 4.75])
    dep_vector = numpy.array([6, 5, 5.5, 1])
    strict_compare_waves(
        dep_vector,
        putil.eng.derivative,
        'derivative',
        'Volts/Sec',
        numpy.array(
            [
                -0.66666666666,
                -0.66666666666,
                1.0,
                -2.5714285714
            ]
        ),
        indep_vector,
    )


def test_exp():
    """ Test exp function behavior """
    strict_compare_waves(None, putil.eng.exp, 'exp', '', numpy.exp)


def test_floor():
    """ Test floor function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    strict_compare_waves(
        dep_vector, putil.eng.floor, 'floor', 'Volts', numpy.floor
    )


@pytest.mark.wave_functions
def test_funcs_exceptions():
    """ Test argument wave not valid exception """
    items = [
        putil.eng.acos, putil.eng.acosh, putil.eng.asin, putil.eng.asinh,
        putil.eng.atan, putil.eng.atanh, putil.eng.average, putil.eng.ceil,
        putil.eng.cos, putil.eng.cosh, putil.eng.db, putil.eng.derivative,
        putil.eng.exp, putil.eng.floor, putil.eng.imag, putil.eng.integral,
        putil.eng.log, putil.eng.log10, putil.eng.nintegral, putil.eng.nmax,
        putil.eng.nmin, putil.eng.phase, putil.eng.round, putil.eng.sin,
        putil.eng.sinh, putil.eng.sqrt, putil.eng.tan, putil.eng.tanh,
        putil.eng.wcomplex, putil.eng.wfloat, putil.eng.wint
    ]
    for item in items:
        AI(item, 'wave', 'a')


def test_imag():
    """ Test imag function behavior """
    dep_vector = numpy.array([10.41, 1+3j, 10-0.5j])
    strict_compare_waves(
        dep_vector, putil.eng.imag, 'imag', 'Volts', numpy.imag
    )


def test_integral():
    """ Test integral and nintegral methods behavior """
    indep_vector = numpy.array([1, 2.5, 3, 4.75])
    dep_vector = numpy.array([6, 5, 5.5, 1])
    strict_compare_waves(
        dep_vector,
        putil.eng.integral,
        'integral',
        'Volts*Sec',
        numpy.array([0.0, 8.25, 10.875, 16.5625]),
        indep_vector
    )
    obj = std_obj('obj', indep_vector, dep_vector)
    act = putil.eng.integral(obj)
    cmp_vectors(
        numpy.array([act.dep_vector[-1]]),
        numpy.array([putil.eng.nintegral(obj)])
    )


def test_log():
    """ Test log function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    strict_compare_waves(
        dep_vector, putil.eng.log, 'log', '', numpy.log
    )


def test_log10():
    """ Test log function behavior """
    dep_vector = numpy.array([10.41, 1.98, 1.0])
    strict_compare_waves(
        dep_vector, putil.eng.log10, 'log10', '', numpy.log10
    )


@pytest.mark.wave_functions
def test_log_exceptions():
    """ Test log and log10 function exceptions """
    dep_vector = numpy.array([0, 0.98, 0.5])
    obj = std_obj(indep_name='obj', dep_vector=dep_vector)
    items = [putil.eng.log, putil.eng.log10]
    for item in items:
        AE(item, ValueError, 'Math domain error', obj)


def test_nmax():
    """ Test nmax method behavior """
    obj = std_obj('obj', indep_scale='LINEAR', interp='CONTINUOUS')
    assert putil.eng.nmax(obj) == 6
    assert putil.eng.nmax(obj, 1.5) == 5.5


def test_nmin():
    """ Test nmax method behavior """
    obj = std_obj('obj', indep_scale='LINEAR', interp='CONTINUOUS')
    assert putil.eng.nmin(obj) == 4
    assert putil.eng.nmin(obj, indep_max=2.5) == 4.5


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
    cmp_vectors(obj.indep_vector, indep_vector)
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
        AI(putil.eng.phase, 'unwrap', wave=obj, unwrap=item)
        AI(putil.eng.phase, 'rad', wave=obj, rad=item)


def test_round():
    """ Test wround method behavior """
    obj_a = std_obj('obj', dep_vector=numpy.array([5.4, 1.6, 0]))
    ref = std_obj('round(obj, 0)', dep_vector=numpy.array([5, 2, 0]))
    act = putil.eng.round(obj_a)
    assert ref == act
    assert ref.indep_name == act.indep_name
    obj_b = std_obj('obj', dep_vector=numpy.array([5.47, 1.61, 0]))
    ref = std_obj('round(obj, 1)', dep_vector=numpy.array([5.5, 1.6, 0.0]))
    act = putil.eng.round(obj_b, 1)
    assert ref == act
    assert ref.indep_name == act.indep_name


@pytest.mark.wave_functions
def test_round_exceptions():
    """ Test wround function exceptions """
    obj = std_obj(indep_name='obj')
    items = [-1, -0.0001, 'a', 3.5]
    for item in items:
        AI(putil.eng.round, 'decimals', wave=obj, decimals=item)


def test_sin():
    """ Test sin function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    strict_compare_waves(
        dep_vector, putil.eng.sin, 'sin', '', numpy.sin
    )


def test_sinh():
    """ Test sinh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    strict_compare_waves(
        dep_vector, putil.eng.sinh, 'sinh', '', numpy.sinh
    )



def test_sqrt():
    """ Test sqrt function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    strict_compare_waves(
        dep_vector, putil.eng.sqrt, 'sqrt', 'Volts**0.5', numpy.sqrt
    )


def test_tan():
    """ Test tan function behavior """
    dep_vector = numpy.array([1.1, 1.98, 1.5])
    strict_compare_waves(
        dep_vector, putil.eng.tan, 'tan', '', numpy.tan
    )


def test_tanh():
    """ Test tanh function behavior """
    dep_vector = numpy.array([0.1, 0.98, 0.5])
    strict_compare_waves(
        dep_vector, putil.eng.tanh, 'tanh', '', numpy.tanh
    )


def test_wcomplex():
    """ Test wcomplex method behavior """
    obj_a = std_obj(
        indep_name='obj_a',
        dep_vector=numpy.array([3, 4, 5]),
    )
    obj_b = putil.eng.wcomplex(obj_a)
    ref = std_obj(
        indep_name='ref',
        dep_vector=numpy.array([3+0j, 4+0j, 5+0j]),
    )
    assert obj_b == ref
    assert obj_b.dep_vector.dtype.name.startswith('complex')


def test_wfloat():
    """ Test wfloat method behavior """
    obj_a = std_obj('obj_a')
    obj_b = putil.eng.wfloat(obj_a)
    ref = std_obj(
        indep_name='ref',
        dep_vector=numpy.array([6.0, 5.0, 4.0]),
    )
    assert obj_b == ref
    assert obj_b.dep_vector.dtype.name.startswith('float')


@pytest.mark.wave_functions
def test_wfloat_exceptions():
    """ Test wfloat function exceptions """
    dep_vector = numpy.array([0.99, 1+3j, 0.5])
    obj = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    AE(putil.eng.wfloat, TypeError, 'Cannot convert complex to float', obj)


def test_wint():
    """ Test wint method behavior """
    obj_a = std_obj('obj_a', dep_vector=numpy.array([5.5, 1.3, 3.4]))
    obj_b = putil.eng.wint(obj_a)
    ref = std_obj(
        indep_name='ref', dep_vector=numpy.array([5, 1, 3]),
    )
    assert obj_b == ref
    assert obj_b.dep_vector.dtype.name.startswith('int')


@pytest.mark.wave_functions
def test_wint_exceptions():
    """ Test wint function exceptions """
    dep_vector = numpy.array([0.99, 1+3j, 0.5])
    obj = std_obj(indep_name='obj_a', dep_vector=dep_vector)
    AE(putil.eng.wint, TypeError, 'Cannot convert complex to integer', obj)
