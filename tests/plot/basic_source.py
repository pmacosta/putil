# basic_source.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0611,R0201,R0204,W0212,W0232,W0612

# PyPI imports
from numpy import array
import pytest
# Putil imports
from putil.plot import BasicSource as FUT
from putil.test import AE, AI, APROP, AROPROP


###
# Global variables
###
RIVAR = array([1, 2, 3])
RDVAR = array([10, 20, 30])

###
# Test classes
###
class TestBasicSource(object):
    """ Tests for BasicSource """
    def test_str(self):
        """ Test that str behaves correctly """
        # Full set
        obj = str(FUT(RIVAR, RDVAR, indep_min=-10, indep_max=20.0))
        ref = (
            'Independent variable minimum: -10\n'
            'Independent variable maximum: 20.0\n'
            'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
            'Dependent variable: [ 10.0, 20.0, 30.0 ]'
        )
        assert obj == ref
        # indep_min not set
        obj = str(FUT(RIVAR, RDVAR, indep_max=20.0))
        ref = (
            'Independent variable minimum: -inf\n'
            'Independent variable maximum: 20.0\n'
            'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
            'Dependent variable: [ 10.0, 20.0, 30.0 ]'
        )
        assert obj == ref
        # indep_max not set
        obj = str(FUT(RIVAR, RDVAR, indep_min=-10))
        ref = (
            'Independent variable minimum: -10\n'
            'Independent variable maximum: +inf\n'
            'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
            'Dependent variable: [ 10.0, 20.0, 30.0 ]'
        )
        assert obj == ref
        # indep_min and indep_max not set
        obj = str(FUT(RIVAR, RDVAR))
        ref = (
            'Independent variable minimum: -inf\n'
            'Independent variable maximum: +inf\n'
            'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
            'Dependent variable: [ 10.0, 20.0, 30.0 ]'
        )
        assert obj == ref

    def test_complete(self):
        """ Test _complete property behavior """
        obj = FUT(RIVAR, RDVAR, indep_min=0, indep_max=50)
        obj._indep_var = None
        assert not obj._complete
        obj = FUT(RIVAR, RDVAR, indep_min=0, indep_max=50)
        assert obj._complete

    @pytest.mark.parametrize('indep_min', [1, 2.0])
    def test_indep_min(self, indep_min):
        """ Tests indep_min property behavior """
        # __init__ path
        FUT(RIVAR, RDVAR, indep_min=indep_min)
        # Managed attribute path
        obj = FUT(RIVAR, RDVAR)
        obj.indep_min = indep_min
        assert obj.indep_min == indep_min

    @pytest.mark.basic_source
    @pytest.mark.parametrize('indep_min', ['a', False])
    def test_indep_min_exceptions(self, indep_min):
        """ Tests indep_min property exceptions """
        # __init__ path
        AI(FUT, 'indep_min', RIVAR, RDVAR, indep_min=indep_min)
        obj = FUT(RIVAR, RDVAR)
        msg = 'Argument `indep_min` is not valid'
        APROP(obj, 'indep_min', indep_min, RuntimeError, msg)

    @pytest.mark.parametrize('indep_max', [1, 2.0])
    def test_indep_max(self, indep_max):
        """ Tests indep_max property behavior """
        # __init__ path
        FUT(RIVAR, RDVAR, indep_max=indep_max)
        # Managed attribute path
        obj = FUT(RIVAR, RDVAR)
        obj.indep_max = indep_max
        assert obj.indep_max == indep_max

    @pytest.mark.basic_source
    @pytest.mark.parametrize('indep_max', ['a', False])
    def test_indep_max_exceptions(self, indep_max):
        """ Tests indep_max property exceptions """
        # __init__ path
        AI(FUT, 'indep_max', RIVAR, RDVAR, indep_max=indep_max)
        # Managed attribute path
        obj = FUT(RIVAR, RDVAR)
        msg = 'Argument `indep_max` is not valid'
        APROP(obj, 'indep_max', indep_max, RuntimeError, msg)
        #with pytest.raises(RuntimeError) as excinfo:
        #    obj.indep_max = indep_max
        #assert GET_EXMSG(excinfo) == 'Argument `indep_max` is not valid'

    @pytest.mark.basic_source
    def test_indep_min_greater_than_indep_max_exceptions(self):
        """
        Test behavior when indep_min and indep_max are incongruous
        """
        # Assign indep_min first
        obj = FUT(RIVAR, RDVAR, indep_min=0.5)
        exmsg = 'Argument `indep_min` is greater than argument `indep_max`'
        APROP(obj, 'indep_max', 0, ValueError, exmsg)
        #with pytest.raises(ValueError) as excinfo:
        #    obj.indep_max = 0
        #assert GET_EXMSG(excinfo) == exmsg
        # Assign indep_max first
        obj = FUT(RIVAR, RDVAR)
        obj.indep_max = 40
        APROP(obj, 'indep_min', 50, ValueError, exmsg)
        #with pytest.raises(ValueError) as excinfo:
        #    obj.indep_min = 50
        #assert GET_EXMSG(excinfo) == exmsg

    def test_indep_var(self):
        """ Tests indep_var property behavior """
        # __init__ path
        indep_var1 = RIVAR
        indep_var2 = array([4.0, 5.0, 6.0])
        assert (FUT(indep_var1, RDVAR).indep_var == indep_var1).all()
        assert (FUT(indep_var2, RDVAR).indep_var == indep_var2).all()
        # Managed attribute path
        obj = FUT(indep_var=indep_var1, dep_var=RDVAR)
        obj.indep_var = indep_var2
        assert (obj.indep_var == indep_var2).all()

    @pytest.mark.basic_source
    @pytest.mark.parametrize(
        'indep_var', [None, 'a', array([1.0, 2.0, 0.0, 3.0]), []]
    )
    def test_indep_var_exceptions(self, indep_var):
        """ Tests indep_var property exceptions """
        # __init__ path
        AI(FUT, 'indep_var', indep_var, RDVAR)
        # Assign indep_min via attribute
        msg = (
            'Argument `indep_var` is empty after '
            '`indep_min`/`indep_max` range bounding'
        )
        obj = FUT(RIVAR, RDVAR)
        APROP(obj, 'indep_min', 45, ValueError, msg)
        # Assign indep_max via attribute
        obj = FUT(RIVAR, RDVAR)
        APROP(obj, 'indep_max', 0, ValueError, msg)
        # Assign both indep_min and indep_max via __init__ path
        AE(FUT, ValueError, msg, RIVAR, RDVAR, indep_min=4, indep_max=10)
        # Managed attribute path
        obj = FUT(RIVAR, RDVAR)
        # Wrong type
        assert (obj.indep_var == RIVAR).all()
        msg = 'Argument `indep_var` is not valid'
        APROP(obj, 'indep_var', indep_var, RuntimeError, msg)
        #with pytest.raises(RuntimeError) as excinfo:
        #    obj.indep_var = indep_var
        #assert GET_EXMSG(excinfo) == 'Argument `indep_var` is not valid'

    def test_dep_var(self):
        """ Tests dep_var property behavior """
        # __init__ path
        # Valid values, these should not raise any exception
        indep_var = array([10, 20, 30])
        dep_var1 = array([1, 2, 3])
        dep_var2 = array([4.0, 5.0, 6.0])
        assert (FUT(indep_var, dep_var1).dep_var == dep_var1).all()
        assert (FUT(indep_var, dep_var2).dep_var == dep_var2).all()
        # Managed attribute path
        obj = FUT(indep_var=indep_var, dep_var=dep_var1)
        obj.dep_var = dep_var1
        assert (obj.dep_var == dep_var1).all()
        obj.dep_var = dep_var2
        assert (obj.dep_var == dep_var2).all()

    @pytest.mark.basic_source
    @pytest.mark.parametrize('dep_var', [None, 'a', []])
    def test_dep_var_exceptions(self, dep_var):
        """ Tests dep_var property exceptions """
        # __init__ path
        msg = 'Argument `dep_var` is not valid'
        AI(FUT, 'dep_var', RIVAR, dep_var)
        # Managed attribute path
        obj = FUT(RIVAR, array([1, 2, 3]))
        APROP(obj, 'dep_var', dep_var, RuntimeError, msg)
        #with pytest.raises(RuntimeError) as excinfo:
        #    obj.dep_var = dep_var
        #assert GET_EXMSG(excinfo) == msg

    @pytest.mark.basic_source
    def test_indep_dep_var_not_same_number_of_elements_exceptions(self):
        """ Tests indep_var and dep_var vector congruency """
        msg = (
            'Arguments `indep_var` and `dep_var` '
            'must have the same number of elements'
        )
        # Both set at object creation
        AE(FUT, ValueError, msg, RDVAR, array([1, 2, 3, 4, 5, 6]), 30, 50)
        AE(FUT, ValueError, msg, RDVAR, array([1, 2]), 30, 50)
        # indep_var set first
        obj = FUT(
            indep_var=array([10, 20, 30, 40, 50, 60]),
            dep_var=array([1, 2, 3, 4, 5, 6]),
            indep_min=30,
            indep_max=50)
        APROP(obj, 'dep_var', array([100, 200, 300]), ValueError, msg)
        # dep_var set first
        obj = FUT(RDVAR, array([100, 200, 300]), indep_min=30, indep_max=50)
        APROP(obj, 'dep_var', array([10, 20, 30, 40, 50, 60]), ValueError, msg)

    @pytest.mark.basic_source
    @pytest.mark.parametrize(
        'prop', ['indep_min', 'indep_max', 'indep_var', 'dep_var']
    )
    def test_cannot_delete_attributes_exceptions(self, prop):
        """
        Test that del method raises an exception on all class attributes
        """
        AROPROP(FUT(RDVAR, array([100, 200, 300])), prop)
