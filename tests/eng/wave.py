# wave.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0113,C0122,E0611,E1101,R0201,W0212

# Standard library imports
from __future__ import print_function
import copy
import math
import sys
# PyPI imports
import numpy
from numpy import array
import pytest
# Putil imports
import putil.eng
import putil.test
from putil.test import AE, AI, APROP, AROPROP, GET_EXMSG, compare_strings


###
# Global variables
###
FP_PREC = 1E-10


###
# Helper functions
###
def cmp_vectors(vector_a, vector_b):
    """ Compare two floating point vectors to a given precision """
    flag = (
        (numpy.abs(vector_a-vector_b) <= FP_PREC).all()
        if len(vector_a) == len(vector_b) else
        False
    )
    if not flag:
        print('\nVectors do not match:')
        print('Vector A: {0}'.format(vector_a))
        print('Vector B: {0}'.format(vector_b))
    return flag


def interp_iter():
    """ Test values for dependent axis interpolator """
    ystart = 3
    ystop = 5
    xinterp = 40
    xstop = 50
    xstart = 30
    yinterp = (
        ystart
        +
        ((ystop-ystart)/(math.log10(xstop)-math.log10(xstart)))
        *
        (math.log10(xinterp)-math.log10(xstart))
    )
    cases = [
        {
            'oiv':array([1, 2, 3, 4]),
            'odv':array([10, 20, 30, 40]),
            'niv':array([1, 1.5, 2, 2.25, 3, 3.75, 4]),
            'ndv':array([10, 15, 20, 22.5, 30, 37.5, 40]),
            'itf':'CONTINUOUS',
            'ids':'LINEAR',
        },
        {
            'oiv':array([1, 2, 3, 4]),
            'odv':array([10, 20, 30, 40]),
            'niv':array([1, 1.5, 2, 2.25, 3, 3.75, 4]),
            'ndv':array([10, 10, 20, 20, 30, 30, 40]),
            'itf':'STAIRCASE',
            'ids':'LINEAR',
        },
        {
            'oiv':array([1, 2, 3, 4]),
            'odv':array([10, 20, 30, 40]),
            'niv':array([1.5, 2, 2.25, 3, 3.75]),
            'ndv':array([10, 20, 20, 30, 30]),
            'itf':'STAIRCASE',
            'ids':'LINEAR',
        },
        {
            'oiv':array([10, 20, 30, 50]),
            'odv':array([1, 2, 3, 5]),
            'niv':array([10, 20, 30, 40, 50]),
            'ndv':array([1, 2, 3, yinterp, 5]),
            'itf':'CONTINUOUS',
            'ids':'LOG',
        },
        {
            'oiv':array([1, 3, 4]),
            'odv':array([1+1j, 3+3j, 4+4j]),
            'niv':array([1, 2, 3, 4]),
            'ndv':array([1+1j, 2+2j, 3+3j, 4+4j]),
            'itf':'CONTINUOUS',
            'ids':'LINEAR',
        },
        {
            'oiv':array([1, 3, 4]),
            'odv':array([1+1j, 3+3j, 4+4j]),
            'niv':array([1, 2, 3, 4]),
            'ndv':array([1+1j, 1+1j, 3+3j, 4+4j]),
            'itf':'STAIRCASE',
            'ids':'LINEAR',
        },
        {
            'oiv':array([10, 20, 30, 50]),
            'odv':array([1+1j, 2+2j, 3+3j, 5+5j]),
            'niv':array([10, 20, 30, 40, 50]),
            'ndv':array([1+1j, 2+2j, 3+3j, yinterp+(yinterp*1j), 5+5j]),
            'itf':'CONTINUOUS',
            'ids':'LOG',
        },
    ]
    for case in cases:
        yield case


def std_obj(indep_name, indep_vector=None, dep_vector=None,
    interp='STAIRCASE', dep_units='Volts'):
    """ Return a waveform with fixed parameters and given name """
    indep_vector = (
        array([1, 2, 3]) if indep_vector is None else indep_vector
    )
    dep_vector = (
        array([6, 5, 4]) if dep_vector is None else dep_vector
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


###
# Test functions
###
def test_get_indep_vector():
    """ Test _get_indep_vector method behavior """
    fut = putil.eng.wave._get_indep_vector
    obj_a = putil.eng.Waveform(
        array([1, 2, 3, 4]), array([10, 20, 30, 40]), 'obj_a'
    )
    obj_b = putil.eng.Waveform(
        array([1.5, 4, 5]), array([30, 40, 50]), 'obj_b'
    )
    assert cmp_vectors(fut(obj_a, obj_b), array([1.5, 2, 3, 4]))
    obj_a = putil.eng.Waveform(
        array([1.75, 2, 2.5, 4]), array([10, 20, 30, 40]), 'obj_a'
    )
    assert cmp_vectors(fut(obj_a, obj_b), array([1.75, 2, 2.5, 4]))
    obj_a = putil.eng.Waveform(
        array([3.5, 4.5, 6, 7]), array([10, 20, 30, 40]), 'obj_a'
    )
    assert cmp_vectors(fut(obj_a, obj_b), array([3.5, 4, 4.5, 5]))


def test_homogenize_waves():
    """ Test _homogenize_waves method behavior """
    # This function is a convenience function that bundles
    # the operations of _get_indep_vector and _interp_dep_vector
    # functions. The test below is not meant to be comprehensive,
    # merely to test if all parameters are passed correctly
    obj_a = putil.eng.Waveform(
        array([1, 2, 3, 4]), array([10, 20, 30, 40]), 'obj_a'
    )
    obj_b = putil.eng.Waveform(
        array([1, 1.5, 2, 2.25, 3, 3.75, 4]),
        array([100, 200, 300, 400, 500, 600, 700]),
        'obj_b'
    )
    fut = putil.eng.wave._homogenize_waves
    indep_vector, dep_vector_a, dep_vector_b = fut(obj_a, obj_b)
    assert cmp_vectors(
        indep_vector,
        array([1, 1.5, 2, 2.25, 3, 3.75, 4])
    )
    assert cmp_vectors(
        dep_vector_a,
        array([10, 15, 20, 22.5, 30, 37.5, 40]),
    )
    assert cmp_vectors(
        dep_vector_b,
        array([100, 200, 300, 400, 500, 600, 700])
    )


def test_interp_dep_vector():
    """ Test _interp_dep_vector method behavior """
    for case in interp_iter():
        obj = putil.eng.Waveform(
            indep_vector=case['oiv'],
            dep_vector=case['odv'],
            indep_name='obj_a',
            indep_scale=case['ids'],
            interp=case['itf']
        )
        assert cmp_vectors(
            putil.eng.wave._interp_dep_vector(obj, case['niv']), case['ndv']
        )


@pytest.mark.wave
def test_get_indep_vector_exceptions():
    """ Test _get_indep_vector method exceptions """
    obj_a = putil.eng.Waveform(
        array([1, 2, 3]), array([10, 20, 30]), 'obj_a'
    )
    obj_b = putil.eng.Waveform(
        array([3.1, 4, 5]), array([30, 40, 50]), 'obj_b'
    )
    msg = 'Independent variable ranges do not overlap'
    args = dict(wave_a=obj_a, wave_b=obj_b)
    AE(putil.eng.wave._get_indep_vector, RuntimeError, msg, **args)


###
# Test classes
###
class TestWaveform(object):
    """ Tests for Waveform class """
    # pylint: disable=R0903,R0904
    @pytest.mark.wave
    @pytest.mark.parametrize(
        'prop', [
            'indep_vector', 'dep_vector', 'indep_name', 'indep_scale',
            'dep_scale', 'indep_units', 'dep_units', 'interp', 'vectors'
        ]
    )
    def test_cannot_delete_attributes_exceptions(self, prop):
        """
        Test that del method raises an exception on all class attributes
        """
        obj = std_obj('test')
        AROPROP(obj, prop)

    def test_init(self):
        """ Test constructor behaviour """
        indep_vector = array([1, 2, 3])
        dep_vector = array([4, 5, 6])
        obj = putil.eng.Waveform(
            indep_vector,
            dep_vector,
            'test',
            'log',
            'linear',
            'amps',
            'time',
            'continuous'
        )
        assert (obj.indep_vector == indep_vector).all()
        assert (obj.dep_vector == dep_vector).all()
        assert obj.indep_name == 'test'
        assert obj.indep_scale == 'LOG'
        assert obj.dep_scale == 'LINEAR'
        assert obj.indep_units == 'amps'
        assert obj.dep_units == 'time'
        assert obj.interp == 'CONTINUOUS'
        obj.indep_name = 'some_name'
        assert obj.indep_name == 'some_name'
        obj.indep_scale = 'linear'
        assert obj.indep_scale == 'LINEAR'
        obj.dep_scale = 'Log'
        assert obj.dep_scale == 'LOG'
        obj.indep_units = 'Watts'
        assert obj.indep_units == 'Watts'
        obj.dep_units = 'meters'
        assert obj.dep_units == 'meters'
        obj.interp = 'STAIRcase'
        assert obj.interp == 'STAIRCASE'
        # Integer dependent variable vector
        obj.indep_vector = array([10, 20, 30])
        assert (obj.indep_vector == array([10, 20, 30])).all()
        obj.dep_vector = array([45, 2, 100])
        assert (obj.dep_vector == array([45, 2, 100])).all()
        # Float dependent variable vector
        obj.vectors = [(5, 1.1), (6, 1.2), (7, 1.3)]
        indep_vector, dep_vector = zip(*(obj.vectors))
        assert (array(indep_vector) == array([5, 6, 7])).all()
        assert (array(dep_vector) == array([1.1, 1.2, 1.3])).all()
        assert (obj.indep_vector == array([5, 6, 7])).all()
        assert (obj.dep_vector == array([1.1, 1.2, 1.3])).all()
        # Complex dependent variable vector
        obj.dep_vector = array([1+1j, 2+2j, 3+3j])
        assert (obj.dep_vector == array([1+1j, 2+2j, 3+3j])).all()

    @pytest.mark.wave
    def test_init_exceptions(self):
        """ Test constructor exceptions """
        items = [
            'a',
            array([]),
            array([10, 5, 3])
        ]
        for item in items:
            args = dict(
                indep_vector=item, dep_vector=array([]), indep_name='a'
            )
            AI(putil.eng.Waveform, 'indep_vector', **args)
        #
        items = ['a', array([])]
        for item in items:
            args = dict(
                indep_vector=array([1, 2]),
                dep_vector=item,
                indep_name='a'
            )
            AI(putil.eng.Waveform, 'dep_vector', **args)
        #
        args = dict(
            indep_vector=array([1, 2]),
            dep_vector=array([1, 2, 3]),
            indep_name='a'
        )
        msg = (
            'Independent and dependent vectors must '
            'have the same number of elements'
        )
        AE(putil.eng.Waveform, ValueError, msg, **args)
        #
        items = ['', True, array([]), 5]
        for item in items:
            args = dict(
                indep_vector=array([1, 2]),
                dep_vector=array([10, 20]),
                indep_name=item
            )
            AI(putil.eng.Waveform, 'indep_name', **args)
        items = [None, True, 'a', 5.0, []]
        for item in items:
            args = dict(
                indep_vector=array([1, 2]),
                dep_vector=array([10, 20]),
                indep_name='a',
                indep_scale=item
            )
            AI(putil.eng.Waveform, 'indep_scale', **args)
        for item in items:
            args = dict(
                indep_vector=array([1, 2]),
                dep_vector=array([10, 20]),
                indep_name='a',
                dep_scale=item
            )
            AI(putil.eng.Waveform, 'dep_scale', **args)
        items = [True, array([]), 5]
        for item in items:
            args = dict(
                indep_vector=array([1, 2]),
                dep_vector=array([10, 20]),
                indep_name='a',
                indep_units=item
            )
            AI(putil.eng.Waveform, 'indep_units', **args)
        for item in items:
            args = dict(
                indep_vector=array([1, 2]),
                dep_vector=array([10, 20]),
                indep_name='a',
                dep_units=item
            )
            AI(putil.eng.Waveform, 'dep_units', **args)
        items = [None, True, 'a', 5.0, []]
        for item in items:
            args = dict(
                indep_vector=array([1, 2]),
                dep_vector=array([10, 20]),
                indep_name='a',
                interp=item
            )
            AI(putil.eng.Waveform, 'interp', **args)
        obj = std_obj('obj')
        msg = (
            'Independent and dependent vectors must '
            'have the same number of elements'
        )
        APROP(obj, 'indep_vector', array([1, 2]), ValueError, msg)
        APROP(obj, 'dep_vector', array([1, 2]), ValueError, msg)
        msg = 'Argument `vectors` is not valid'
        items = [
            [(1, 0), (2, 2), ('a', 5)],
            [(1, 0), (2, 2), (5, 'a')],
            [(1, 0), (2, 2), (3, 4, 5)],
        ]
        for item in items:
            APROP(obj, 'vectors', item, RuntimeError, msg)

    def test_abs(self):
        """ Test __abs__ method behavior """
        indep_vector = array([1, 2, 3])
        dep_vector_a = array([4, -5, complex(1, math.sqrt(3))])
        obj_a = putil.eng.Waveform(indep_vector, dep_vector_a, 'obj_a')
        dep_vector_b = array([4, 5, 2])
        obj_b = putil.eng.Waveform(indep_vector, dep_vector_b, 'obj_b')
        obj_c = abs(obj_a)
        assert obj_c.indep_name == 'abs(obj_a)'
        assert obj_c == obj_b
        indep_vector = array([1, 2, 3])
        dep_vector_a = array([4, -5, 6])
        obj_a = putil.eng.Waveform(indep_vector, dep_vector_a, 'obj_a')
        dep_vector_b = array([4, 5, 6])
        obj_b = putil.eng.Waveform(indep_vector, dep_vector_b, 'obj_b')
        obj_c = abs(obj_a)
        assert obj_c.indep_name == 'abs(obj_a)'
        assert obj_c.dep_units == obj_a.dep_units
        assert obj_c == obj_b
        assert obj_c.dep_vector.dtype.name.startswith('int')

    def test_add(self):
        """ Test __add__ method behavior """
        # Float and integer dependent variable vector
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([8, -1, -4]))
        obj_c = std_obj('obj_c', dep_vector=array([14, 4, 0]))
        aobj = obj_a+obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a+obj_b'
        assert obj_c.dep_units == obj_a.dep_units
        assert ((5+obj_a).dep_vector == array([11, 10, 9])).all()
        assert ((obj_a+2).dep_vector == array([8, 7, 6])).all()
        obj_a += 2
        assert (obj_a.dep_vector == array([8, 7, 6])).all()
        # Complex dependent variable vector
        obj_a = std_obj(
            'obj_a',
            indep_vector=array([1, 2]),
            dep_vector=array([1+1j, 3+5j])
        )
        obj_b = std_obj(
            'obj_b',
            indep_vector=array([1, 2]),
            dep_vector=array([8, -1j])
        )
        obj_c = std_obj(
            'obj_c',
            indep_vector=array([1, 2]),
            dep_vector=array([9+1j, 3+4j])
        )
        aobj = obj_a+obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a+obj_b'
        assert (
            (5+obj_a).dep_vector == array([6+1j, 8+5j])
        ).all()
        assert (
            ((obj_a+7+1j).dep_vector == array([8+2j, 10+6j]))
        ).all()
        obj_a += 7+1j
        assert (obj_a.dep_vector == array([8+2j, 10+6j])).all()

    @pytest.mark.wave
    def test_add_exceptions(self):
        """ Test __add__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a + 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' + obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a + obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b + obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a + obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_and(self):
        """ Test __and__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([7, 1, 4]))
        obj_c = std_obj('obj_c', dep_vector=array([6, 1, 4]))
        aobj = obj_a & obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a&obj_b'
        assert aobj.dep_units == obj_a.dep_units
        assert ((2&obj_a).dep_vector == array([2, 0, 0])).all()
        assert ((obj_a&2).dep_vector == array([2, 0, 0])).all()
        obj_a &= 2
        assert (obj_a.dep_vector == array([2, 0, 0])).all()

    @pytest.mark.wave
    def test_and_exceptions(self):
        """ Test __and__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a & True
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = True & obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a & obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b & obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_b = std_obj('obj_b', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a & obj_b
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_b & obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a & 1+1j
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 1+1j & obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a & obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_bool(self):
        """ Test __bool__ and __nonzero__ methods behavior """
        indep_vector = array([1, 2, 3])
        dep_vector = array([4, 5, 6])
        obj = putil.eng.Waveform(indep_vector, dep_vector, 'obj')
        if obj:
            pass
        else:
            pytest.fail('__bool__ failed')
        dep_vector = numpy.zeros(3)
        obj = putil.eng.Waveform(indep_vector, dep_vector, 'obj')
        if obj:
            pytest.fail('__bool__ failed')
        dep_vector = array([1+1j, 2+2j, 3+3j])
        obj = putil.eng.Waveform(indep_vector, dep_vector, 'obj')
        if obj:
            pass
        else:
            pytest.fail('__bool__ failed')
        dep_vector = array(
            [0+0.000000000001j, 0.000000000001+0j, 0+0j]
        )
        obj = putil.eng.Waveform(indep_vector, dep_vector, 'obj')
        if obj:
            pytest.fail('__bool__ failed')

    def test_copy(self):
        """ Test __copy__ method behavior """
        obj_a = std_obj('test')
        indep_vector = obj_a.indep_vector
        dep_vector = obj_a.dep_vector
        obj_b = copy.copy(obj_a)
        assert (indep_vector == obj_a.indep_vector).all()
        assert (indep_vector == obj_b.indep_vector).all()
        assert (obj_a.indep_vector == obj_b.indep_vector).all()
        assert obj_a.indep_vector is not obj_b.indep_vector
        assert (dep_vector == obj_a.dep_vector).all()
        assert (dep_vector == obj_b.dep_vector).all()
        assert (obj_a.dep_vector == obj_b.dep_vector).all()
        assert obj_a.dep_vector is not obj_b.dep_vector
        assert obj_a.indep_name == 'test'
        assert obj_b.indep_name == 'test'
        assert obj_a.indep_name == obj_b.indep_name
        assert obj_a.indep_scale == 'LOG'
        assert obj_b.indep_scale == 'LOG'
        assert obj_a.indep_scale == obj_b.indep_scale
        assert obj_a.dep_scale == 'LINEAR'
        assert obj_b.dep_scale == 'LINEAR'
        assert obj_a.dep_scale == obj_b.dep_scale
        assert obj_a.indep_units == 'Sec'
        assert obj_b.indep_units == 'Sec'
        assert obj_a.indep_units == obj_b.indep_units
        assert obj_a.dep_units == 'Volts'
        assert obj_b.dep_units == 'Volts'
        assert obj_a.dep_units == obj_b.dep_units
        assert obj_a.interp == 'STAIRCASE'
        assert obj_b.interp == 'STAIRCASE'
        assert obj_a.interp == obj_b.interp

    def test_div(self):
        """ Test __div__ method behavior """
        # pylint: disable=R0915
        ref = array([0.8333333333333333333, 1.0, 1.25])
        if sys.hexversion < 0x03000000:
            # Integer division
            obj_a = std_obj('obj_a')
            obj_b = std_obj(
                'obj_b', dep_vector=array([8, -1, -4]), dep_units='A'
            )
            obj_c = std_obj(
                'obj_c',
                dep_vector=array([0, -5, -1]),
                dep_units='Volts/A'
            )
            aobj = obj_a/obj_b
            assert aobj == obj_c
            assert aobj.indep_name == 'obj_a/obj_b'
            assert ((5/obj_a).dep_vector == array([0, 1, 1])).all()
            assert (5/obj_a).dep_units == '1/Volts'
            assert ((obj_a/2).dep_vector == array([3, 2, 2])).all()
            assert (obj_a/2).dep_units == 'Volts'
            obj_a /= 2
            assert (obj_a.dep_vector == array([3, 2, 2])).all()
        else:
            # True division
            obj_a = std_obj('obj_a')
            obj_b = std_obj(
                'obj_b', dep_vector=array([8, -1, -4]), dep_units='A'
            )
            obj_c = std_obj(
                'obj_c',
                dep_vector=array([0.75, -5.0, -1.0]),
                dep_units='Volts/A'
            )
            aobj = obj_a/obj_b
            assert aobj == obj_c
            assert aobj.indep_name == 'obj_a/obj_b'
            assert ((5/obj_a).dep_vector == ref).all()
            assert (5/obj_a).dep_units == '1/Volts'
            assert ((obj_a/2).dep_vector == array([3.0, 2.5, 2.0])).all()
            assert (obj_a/2).dep_units == 'Volts'
            obj_a /= 2
            assert (obj_a.dep_vector == array([3.0, 2.5, 2.0])).all()
        # Floating point division
        obj_a = std_obj('obj_a')
        obj_b = std_obj(
            'obj_b', dep_vector=array([8.0, -1.0, -4.0]), dep_units='A'
        )
        obj_c = std_obj(
            'obj_c',
            dep_vector=array([0.75, -5.0, -1.0]), dep_units='Volts/A'
        )
        aobj = obj_a/obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a/obj_b'
        assert ((5.0/obj_a).dep_vector == ref).all()
        assert (5.0/obj_a).dep_units == '1/Volts'
        assert ((obj_a/2.0).dep_vector == array([3.0, 2.5, 2.0])).all()
        assert (obj_a/2.0).dep_units == 'Volts'
        obj_a /= 2.0
        assert (obj_a.dep_vector == array([3.0, 2.5, 2.0])).all()
        # Complex operands
        obj_a = std_obj('obj_a')
        obj_b = std_obj(
            'obj_b', dep_vector=array([10+20j, 5+5j, 6-2j]), dep_units='Ohms'
        )
        obj_c = std_obj(
            'obj_c',
            dep_vector=array([0.12-0.24j, 0.5-0.5j, 0.6+0.2j]),
            dep_units='Volts/Ohms'
        )
        aobj = obj_a/obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a/obj_b'
        ref = array([(1/6.0)+(1j/6.0), 0.2+0.2j, 0.25+0.25j])
        assert (((1+1j)/obj_a).dep_vector == ref).all()
        ref = array([0.6-0.3j, 0.5-0.25j, 0.4-0.2j])
        assert cmp_vectors((obj_a/(8+4j)).dep_vector, ref)
        obj_a /= 8+4j
        ref = array([0.6-0.3j, 0.5-0.25j, 0.4-0.2j])
        assert cmp_vectors(obj_a.dep_vector, ref)

    @pytest.mark.wave
    def test_div_exceptions(self):
        """ Test __div__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a / 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' / obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a / obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b / obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_eq_ne(self):
        """ Test __eq__ and __ne__ methods behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b')
        assert obj_a == obj_a
        assert obj_a == obj_b
        dep_vector = copy.copy(obj_b.dep_vector)
        obj_b = std_obj(
            'obj_b', dep_vector=dep_vector+(1E-16*array([1, 1, 1]))
        )
        assert obj_a == obj_b
        assert not obj_a != obj_b
        obj_b = std_obj(
            'obj_b', dep_vector=dep_vector+(1E-10*array([1, 1, 1]))
        )
        assert not obj_a == obj_b
        assert obj_a != obj_b
        obj_a = std_obj('obj_a', dep_vector=array([1, 2, 3]))
        obj_b = std_obj('obj_b', dep_vector=array([2, 1, 4]))
        assert not obj_a == obj_b
        assert obj_a != obj_b
        obj = putil.eng.Waveform(
            array([1, 2, 3]), array([5, 5, 5]), 'obj'
        )
        assert obj == 5
        assert obj != 6
        assert not obj == 'a'
        assert not 'a' == obj
        # Complex waveform
        obj_a = std_obj('obj_a', dep_vector=array([1+1j, 2+2j, 3+3j]))
        obj_b = std_obj('obj_b', dep_vector=array([1+1j, 2+2j, 3+3j]))
        assert obj_a == obj_b
        assert obj_b == obj_a
        obj_b.dep_vector += 1E-10
        assert not obj_a == obj_b
        assert obj_a != obj_b
        obj_b = std_obj(
            'obj_b',
            dep_vector=array(
                [1+1.00000000001j, 1+0.99999999999j, 1+1.00000000001j]
            )
        )
        assert obj_b == 1+1j
        assert obj_b != 1+2j
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_units='unknown')
        assert not obj_a == obj_b
        assert obj_a != obj_b

    def test_floordiv(self):
        """ Test __floordiv__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([8, -1, -4]), dep_units='C')
        obj_c = std_obj(
            'obj_c', dep_vector=array([0, -5, -1]), dep_units='Volts/C'
        )
        aobj = obj_a//obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a//obj_b'
        assert ((10//obj_a).dep_vector == array([1, 2, 2])).all()
        assert (10//obj_a).dep_units == '1/Volts'
        assert ((obj_a//2).dep_vector == array([3, 2, 2])).all()
        assert (obj_a//2).dep_units == 'Volts'
        obj_a //= 2
        assert (obj_a.dep_vector == array([3, 2, 2])).all()

    @pytest.mark.wave
    def test_floordiv_exceptions(self):
        """ Test __floordiv__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a // 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' // obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a // obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b // obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_a = std_obj('obj_a', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a // 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' // obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 5 // obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a // 5
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'

    def test_ge(self):
        """ Test __ge__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b')
        assert obj_a >= obj_b
        obj_b = std_obj('obj_b', dep_vector=array([1, 7, 1]))
        assert not obj_a >= obj_b
        obj_b = std_obj('obj_b', dep_vector=array([1, 4.99, 1]))
        assert obj_a >= obj_b
        obj_b = std_obj('obj_b', dep_vector=array([1, 5, 1]))
        assert obj_a >= obj_b
        assert obj_a >= 3
        assert not obj_a >= 6

    @pytest.mark.wave
    def test_ge_exceptions(self):
        """ Test __ge__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a >= 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a >= obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_a = std_obj('obj_a', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a >= 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' >= obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 5 >= obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a >= 5
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a >= obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_getitem(self):
        """ Test __getitem__ method behavior """
        obj_a = std_obj('obj_a')
        assert obj_a[0] == (1, 6)
        assert obj_a[-1] == (3, 4)
        assert obj_a[0:2] == [(1, 6), (2, 5)]

    def test_getitem_exceptions(self):
        """ Test __getitem__ method exceptions """
        # pylint: disable=E1127
        obj_a = std_obj('obj_a')
        with pytest.raises(IndexError) as excinfo:
            _ = obj_a[1:'a']
        exmsg1 = 'failed to coerce slice entry of type str to integer'
        exmsg2 = 'invalid slice'
        assert GET_EXMSG(excinfo) in [exmsg1, exmsg2]

    def test_gt(self):
        """ Test __gt__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b')
        assert not obj_a > obj_b
        obj_b = std_obj('obj_b', dep_vector=array([1, 7, 1]))
        assert not obj_a > obj_b
        obj_b = std_obj('obj_b', dep_vector=array([1, 4.99, 1]))
        assert obj_a > obj_b
        obj_b = std_obj('obj_b', dep_vector=array([1, 5, 1]))
        assert not obj_a > obj_b
        assert obj_a > 3
        assert not obj_a > 7

    @pytest.mark.wave
    def test_gt_exceptions(self):
        """ Test __gt__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a > 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a > obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_a = std_obj('obj_a', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a > 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' > obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 5 > obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a > 5
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a > obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_invert(self):
        """ Test __invert__ method behavior """
        ref = std_obj('ref')
        obj = ~ref
        assert obj.indep_name == '~ref'
        assert (obj.dep_vector == array([-7, -6, -5])).all()

    @pytest.mark.wave
    def test_invert_exceptions(self):
        """ Test __invert__ method exceptions """
        obj = std_obj('obj', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = ~obj
        assert GET_EXMSG(excinfo) == 'Complex operand not supported'

    def test_le(self):
        """ Test __le__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b')
        assert obj_a <= obj_b
        obj_b = std_obj('obj_b', dep_vector=array([7, 2, 7]))
        assert not obj_a <= obj_b
        obj_b = std_obj('obj_b', dep_vector=array([7, 5.01, 7]))
        assert obj_a <= obj_b
        obj_b = std_obj('obj_b', dep_vector=array([7, 5, 7]))
        assert obj_a <= obj_b
        assert obj_a <= 7
        assert not obj_a <= 4

    @pytest.mark.wave
    def test_le_exceptions(self):
        """ Test __le__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a <= 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a <= obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_a = std_obj('obj_a', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a <= 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' <= obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 5 <= obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a <= 5
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a <= obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_len(self):
        """ Test __len__ method behavior """
        indep_vector = array([1, 2, 3])
        dep_vector = array([4, 5, 6])
        obj = putil.eng.Waveform(indep_vector, dep_vector, 'obj')
        assert len(obj) == 3

    def test_lshift(self):
        """ Test __lshift__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([8, 1, 4]))
        obj_c = std_obj('obj_c', dep_vector=array([1536, 10, 64]))
        aobj = obj_a<<obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a<<obj_b'
        assert ((5<<obj_a).dep_vector == array([320, 160, 80])).all()
        assert ((obj_a<<2).dep_vector == array([24, 20, 16])).all()
        obj_a <<= 2
        assert (obj_a.dep_vector == array([24, 20, 16])).all()

    @pytest.mark.wave
    def test_lshift_exceptions(self):
        """ Test __lshift__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a << True
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = True << obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a << obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b << obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_b = std_obj('obj_b', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a << obj_b
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_b << obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a << 1+1j
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 1+1j << obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a << obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_lt(self):
        """ Test __lt__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b')
        assert not obj_a < obj_b
        obj_b = std_obj('obj_b', dep_vector=array([7, 2, 7]))
        assert not obj_a < obj_b
        obj_b = std_obj('obj_b', dep_vector=array([7, 5.01, 7]))
        assert obj_a < obj_b
        obj_b = std_obj('obj_b', dep_vector=array([7, 5, 7]))
        assert not obj_a < obj_b
        assert obj_a < 7
        assert not obj_a < 6

    @pytest.mark.wave
    def test_lt_exceptions(self):
        """ Test __lt__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a < 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a < obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_a = std_obj('obj_a', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a < 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' < obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 5 < obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a < 5
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a < obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_mod(self):
        """ Test __mod__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([8, -1, -4]))
        obj_c = std_obj('obj_c', dep_vector=array([6, 0, 0]))
        aobj = obj_a%obj_b
        assert aobj == obj_c
        assert aobj.indep_name == r'obj_a%obj_b'
        assert ((5%obj_a).dep_vector == array([5, 0, 1])).all()
        assert ((obj_a%2).dep_vector == array([0, 1, 0])).all()
        obj_a %= 2
        assert (obj_a.dep_vector == array([0, 1, 0])).all()

    @pytest.mark.wave
    def test_mod_exceptions(self):
        """ Test __mod__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a % True
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = True % obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a % obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b % obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_b = std_obj('obj_b', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a % obj_b
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_b % obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a % (1+1j)
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = (1+1j) % obj_a
        msg = (
            'Complex operands not supported'
            if sys.hexversion < 0x03000000 else
            "can't mod complex numbers."
        )
        assert GET_EXMSG(excinfo) == msg

    def test_mul(self):
        """ Test __mul__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([8, -1, -4]), dep_units='A')
        obj_c = std_obj(
            'obj_c', dep_vector=array([48, -5, -16]), dep_units='Volts*A'
        )
        aobj = obj_a*obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a*obj_b'
        assert ((5*obj_a).dep_vector == array([30, 25, 20])).all()
        assert (5*obj_a).dep_units == 'Volts'
        assert ((obj_a*2).dep_vector == array([12, 10, 8])).all()
        assert (obj_a*2).dep_units == 'Volts'
        obj_a *= 2
        assert (obj_a.dep_vector == array([12, 10, 8])).all()

    @pytest.mark.wave
    def test_mul_exceptions(self):
        """ Test __mul__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a * 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' * obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a * obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b * obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_neg(self):
        """ Test __neg__ method behavior """
        ref = std_obj('ref')
        obj = -ref
        assert obj.indep_name == '-ref'
        assert (obj.dep_vector == array([-6, -5, -4])).all()
        ref = std_obj('obj', dep_vector=array([1, 2+2j, 3+3j]))
        assert ((-ref).dep_vector == array([-1, -2-2j, -3-3j])).all()

    def test_or(self):
        """ Test __or__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([7, 1, 4]))
        obj_c = std_obj('obj_c', dep_vector=array([7, 5, 4]))
        aobj = obj_a | obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a|obj_b'
        assert ((2|obj_a).dep_vector == array([6, 7, 6])).all()
        assert ((obj_a|2).dep_vector == array([6, 7, 6])).all()
        obj_a |= 2
        assert (obj_a.dep_vector == array([6, 7, 6])).all()

    @pytest.mark.wave
    def test_or_exceptions(self):
        """ Test __or__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a | True
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = True | obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a | obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b | obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_b = std_obj('obj_b', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a | obj_b
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_b | obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a | 1+1j
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 1+1j | obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a | obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_pos(self):
        """ Test __pos__ method behavior """
        ref = std_obj('ref')
        obj = +ref
        assert ref is not obj
        assert ref == obj

    def test_pow(self):
        """ Test __pow__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([8, -1, -4]), dep_units='A')
        obj_c = std_obj(
            'obj_c', dep_vector=array([1679616, 0, 0]), dep_units='Volts**A'
        )
        aobj = obj_a**obj_b
        assert aobj == obj_c
        obj_a.dep_vector = obj_a.dep_vector.astype('float')
        obj_c = std_obj(
            'obj_c',
            dep_vector=array([1679616, 0.2, 0.00390625]),
            dep_units='Volts**A'
        )
        aobj = obj_a**obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a**obj_b'
        assert ((5**obj_a).dep_vector == array([15625, 3125, 625])).all()
        assert (5**obj_a).dep_units == '1**Volts'
        assert ((obj_a**2).dep_vector == array([36, 25, 16])).all()
        assert (obj_a**2).dep_units == 'Volts**2'
        obj_a **= 2
        assert (obj_a.dep_vector == array([36, 25, 16])).all()
        obj_a = std_obj('obj_a', dep_vector=array([1+1j, 2+2j, 3+3j]))
        obj_b = std_obj('obj_b', dep_vector=array([3+4j, 1+6j, 2]))
        obj_c = std_obj(
            'obj_c',
            dep_vector=array(
                [
                    -0.10081675027325637-0.06910517142735251j,
                    0.018754229185649937+0.017142783560861786j,
                    0+18j
                ]
            ),
            dep_units='Volts**Volts'
        )
        aobj = obj_a**obj_b
        assert aobj == obj_c

    @pytest.mark.wave
    def test_pow_exceptions(self):
        """ Test __pow__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a ** 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' ** obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a ** obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b ** obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_repr(self):
        """ Test __repr__ method behavior """
        obj = std_obj('test_waveform')
        ref = (
            "putil.eng.Waveform("
            "indep_vector=array([1, 2, 3]), "
            "dep_vector=array([6, 5, 4]), "
            "indep_name='test_waveform', "
            "indep_scale='LOG', "
            "dep_scale='LINEAR', "
            "indep_units='Sec', "
            "dep_units='Volts', "
            "interp='STAIRCASE')"
        )
        compare_strings(repr(obj), ref)

    def test_rshift(self):
        """ Test __rshift__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([1, 1, 1]))
        obj_c = std_obj('obj_c', dep_vector=array([3, 2, 2]))
        aobj = obj_a>>obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a>>obj_b'
        ref = array([258, 516, 1033])
        assert ((16536>>obj_a).dep_vector == ref).all()
        assert ((obj_a>>1).dep_vector == array([3, 2, 2])).all()
        obj_a >>= 1
        assert (obj_a.dep_vector == array([3, 2, 2])).all()

    @pytest.mark.wave
    def test_rshift_exceptions(self):
        """ Test __rshift__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a >> True
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = True >> obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a >> obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b >> obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_b = std_obj('obj_b', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a >> obj_b
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_b >> obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a >> 1+1j
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 1+1j >> obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a >> obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_str(self):
        """ Test __str__ method behavior """
        obj = putil.eng.Waveform(
            array([1, 2, 3]), array([4, 5, 6]), 'test_waveform_0'
        )
        ref = (
            'Waveform: test_waveform_0\n'
            'Independent variable: [ 1, 2, 3 ]\n'
            'Dependent variable: [ 4, 5, 6 ]\n'
            'Independent variable scale: LINEAR\n'
            'Dependent variable scale: LINEAR\n'
            'Independent variable units: (None)\n'
            'Dependent variable units: (None)\n'
            'Interpolating function: CONTINUOUS'
        )
        assert str(obj) == ref
        obj = std_obj('test_waveform_1')
        ref = (
            'Waveform: test_waveform_1\n'
            'Independent variable: [ 1, 2, 3 ]\n'
            'Dependent variable: [ 6, 5, 4 ]\n'
            'Independent variable scale: LOG\n'
            'Dependent variable scale: LINEAR\n'
            'Independent variable units: Sec\n'
            'Dependent variable units: Volts\n'
            'Interpolating function: STAIRCASE'
        )
        assert str(obj) == ref
        indep_vector = array(
            [
                1.23456789,
                2.45678901,
                3.45678901,
                4.56789012,
                5.67890123,
                6.78901234,
                7.89012345
            ]
        )
        dep_vector = array(
            [
                10.23456789,
                20.45678901,
                30.45678901,
                40.56789012,
                50.67890123,
                60.78901234,
                70.89012345
            ]
        )
        obj = putil.eng.Waveform(
            indep_vector=indep_vector,
            dep_vector=dep_vector,
            indep_name='test_waveform_2',
            indep_scale='LOG',
            dep_scale='LINEAR',
            indep_units='Sec',
            dep_units='Volts',
            interp='STAIRCASE'
        )
        ref = (
            'Waveform: test_waveform_2\n'
            'Independent variable: [ 1.23456789, 2.45678901, 3.45678901,\n'
            '                                        ...\n'
            '                        5.67890123, 6.78901234, 7.89012345 ]\n'
            'Dependent variable: [ 10.23456789, 20.45678901, 30.45678901,\n'
            '                                       ...\n'
            '                      50.67890123, 60.78901234, 70.89012345 ]\n'
            'Independent variable scale: LOG\n'
            'Dependent variable scale: LINEAR\n'
            'Independent variable units: Sec\n'
            'Dependent variable units: Volts\n'
            'Interpolating function: STAIRCASE'
        )
        assert str(obj) == ref

    def test_sub(self):
        """ Test __sub__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([8, -1, -4]))
        obj_c = std_obj('obj_c', dep_vector=array([-2, 6, 8]))
        aobj = obj_a-obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a-obj_b'
        assert ((5-obj_a).dep_vector == array([1, 0, -1])).all()
        assert ((obj_a-2).dep_vector == array([4, 3, 2])).all()
        obj_a -= 2
        assert (obj_a.dep_vector == array([4, 3, 2])).all()

    @pytest.mark.wave
    def test_sub_exceptions(self):
        """ Test __sub__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a - 'a'
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 'a' - obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a - obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b - obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'

    def test_xor(self):
        """ Test __xor__ method behavior """
        obj_a = std_obj('obj_a')
        obj_b = std_obj('obj_b', dep_vector=array([7, 1, 4]))
        obj_c = std_obj('obj_c', dep_vector=array([1, 4, 0]))
        aobj = obj_a ^ obj_b
        assert aobj == obj_c
        assert aobj.indep_name == 'obj_a^obj_b'
        assert ((2^obj_a).dep_vector == array([4, 7, 6])).all()
        assert ((obj_a^2).dep_vector == array([4, 7, 6])).all()
        obj_a ^= 2
        assert (obj_a.dep_vector == array([4, 7, 6])).all()

    @pytest.mark.wave
    def test_xor_exceptions(self):
        """ Test __xor__ method exceptions """
        obj_a = std_obj('obj_a')
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a ^ True
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = True ^ obj_a
        assert GET_EXMSG(excinfo) == 'Data type not supported'
        obj_b = std_obj('obj_b', interp='CONTINUOUS')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a ^ obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_b ^ obj_a
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
        obj_b = std_obj('obj_b', dep_vector=array([1+1j, 2+2j, 3+3j]))
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a ^ obj_b
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_b ^ obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = obj_a ^ 1+1j
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        with pytest.raises(TypeError) as excinfo:
            _ = 1+1j ^ obj_a
        assert GET_EXMSG(excinfo) == 'Complex operands not supported'
        obj_b = std_obj('obj_b', dep_units='unknown')
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj_a ^ obj_b
        assert GET_EXMSG(excinfo) == 'Waveforms are not compatible'
