# basic_source.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0201,W0212,W0232,W0612

# PyPI imports
import numpy
import pytest
# Putil imports
import putil.misc
import putil.plot
import putil.test


###
# Test classes
###
class TestBasicSource(object):
    """ Tests for BasicSource """
    def test_str(self):
        """ Test that str behaves correctly """
        # Full set
        obj = str(putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30]),
            indep_min=-10,
            indep_max=20.0)
        )
        ref = (
            'Independent variable minimum: -10\n'
            'Independent variable maximum: 20.0\n'
            'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
            'Dependent variable: [ 10.0, 20.0, 30.0 ]'
        )
        assert obj == ref
        # indep_min not set
        obj = str(putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30]),
            indep_max=20.0)
        )
        ref = (
            'Independent variable minimum: -inf\n'
            'Independent variable maximum: 20.0\n'
            'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
            'Dependent variable: [ 10.0, 20.0, 30.0 ]'
        )
        assert obj == ref
        # indep_max not set
        obj = str(putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30]),
            indep_min=-10)
        )
        ref = (
            'Independent variable minimum: -10\n'
            'Independent variable maximum: +inf\n'
            'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
            'Dependent variable: [ 10.0, 20.0, 30.0 ]'
        )
        assert obj == ref
        # indep_min and indep_max not set
        obj = str(putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30]))
        )
        ref = (
            'Independent variable minimum: -inf\n'
            'Independent variable maximum: +inf\n'
            'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
            'Dependent variable: [ 10.0, 20.0, 30.0 ]'
        )
        assert obj == ref

    def test_complete(self):
        """ Test _complete property behavior """
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([10, 20, 30]),
            dep_var=numpy.array([100, 200, 300]),
            indep_min=0,
            indep_max=50
        )
        obj._indep_var = None
        assert not obj._complete
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([10, 20, 30]),
            dep_var=numpy.array([100, 200, 300]),
            indep_min=0,
            indep_max=50
        )
        assert obj._complete

    def test_indep_min(self):
        """ Tests indep_min property behavior """
        # __init__ path
        items = [1, 2.0]
        for item in items:
            putil.plot.BasicSource(
                indep_var=numpy.array([1, 2, 3]),
                dep_var=numpy.array([10, 20, 30]),
                indep_min=item
            )
        # Managed attribute path
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30])
        )
        for item in items:
            obj.indep_min = item
            assert obj.indep_min == item

    @pytest.mark.basic_source
    def test_indep_min_exceptions(self):
        """ Tests indep_min property exceptions """
        # __init__ path
        items = ['a', False]
        for item in items:
            putil.test.assert_exception(
                putil.plot.BasicSource,
                {
                    'indep_var':numpy.array([1, 2, 3]),
                    'dep_var':numpy.array([10, 20, 30]),
                    'indep_min':item
                },
                RuntimeError,
                'Argument `indep_min` is not valid'
            )
        # Managed attribute path
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30])
        )
        for item in items:
            with pytest.raises(RuntimeError) as excinfo:
                obj.indep_min = item
            assert (
                putil.test.get_exmsg(excinfo)
                ==
                'Argument `indep_min` is not valid'
            )

    def test_indep_max(self):
        """ Tests indep_max property behavior """
        # __init__ path
        items = [1, 2.0]
        for item in items:
            putil.plot.BasicSource(
                indep_var=numpy.array([1, 2, 3]),
                dep_var=numpy.array([10, 20, 30]),
                indep_max=item
            )
        # Managed attribute path
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30])
        )
        for item in items:
            obj.indep_max = item
            assert obj.indep_max == item

    @pytest.mark.basic_source
    def test_indep_max_exceptions(self):
        """ Tests indep_max property exceptions """
        # __init__ path
        items = ['a', False]
        for item in items:
            putil.test.assert_exception(
                putil.plot.BasicSource,
                {
                    'indep_var':numpy.array([1, 2, 3]),
                    'dep_var':numpy.array([10, 20, 30]),
                    'indep_max':item
                },
                RuntimeError,
                'Argument `indep_max` is not valid'
            )
        # Managed attribute path
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30])
        )
        for item in items:
            with pytest.raises(RuntimeError) as excinfo:
                obj.indep_max = item
            assert (
                putil.test.get_exmsg(excinfo)
                ==
                'Argument `indep_max` is not valid'
            )

    @pytest.mark.basic_source
    def test_indep_min_greater_than_indep_max_exceptions(self):
        """
        Test behavior when indep_min and indep_max are incongruous
        """
        # Assign indep_min first
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30]),
            indep_min=0.5)
        with pytest.raises(ValueError) as excinfo:
            obj.indep_max = 0
        assert (
            putil.test.get_exmsg(excinfo)
            ==
            'Argument `indep_min` is greater than argument `indep_max`'
        )
        # Assign indep_max first
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30])
        )
        obj.indep_max = 40
        with pytest.raises(ValueError) as excinfo:
            obj.indep_min = 50
        assert (
            putil.test.get_exmsg(excinfo)
            ==
            'Argument `indep_min` is greater than argument `indep_max`'
        )

    def test_indep_var(self):
        """ Tests indep_var property behavior """
        # __init__ path
        indep_var1 = numpy.array([1, 2, 3])
        indep_var2 = numpy.array([4.0, 5.0, 6.0])
        dep_var = numpy.array([10, 20, 30])
        assert (
            putil.plot.BasicSource(
                indep_var=indep_var1, dep_var=dep_var
            ).indep_var == indep_var1
        ).all()
        assert (
            putil.plot.BasicSource(
                indep_var=indep_var2, dep_var=dep_var
            ).indep_var == indep_var2
        ).all()
        # Managed attribute path
        obj = putil.plot.BasicSource(indep_var=indep_var1, dep_var=dep_var)
        obj.indep_var = indep_var2
        assert (obj.indep_var == indep_var2).all()

    @pytest.mark.basic_source
    def test_indep_var_exceptions(self):
        """ Tests indep_var property exceptions """
        # __init__ path
        items = [
            None,
            'a',
            numpy.array([1.0, 2.0, 0.0, 3.0]),
            numpy.array([])
        ]
        for item in items:
            putil.test.assert_exception(
                putil.plot.BasicSource,
                {'indep_var':item, 'dep_var':numpy.array([10, 20, 30])},
                RuntimeError,
                'Argument `indep_var` is not valid'
            )
        # Assign indep_min via attribute
        msg = (
            'Argument `indep_var` is empty after '
            '`indep_min`/`indep_max` range bounding'
        )
        obj = putil.plot.BasicSource(
            numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30])
        )
        with pytest.raises(ValueError) as excinfo:
            obj.indep_min = 45
        assert putil.test.get_exmsg(excinfo) == msg
        # Assign indep_max via attribute
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30])
        )
        with pytest.raises(ValueError) as excinfo:
            obj.indep_max = 0
        assert putil.test.get_exmsg(excinfo) == msg
        # Assign both indep_min and indep_max via __init__ path
        putil.test.assert_exception(
            putil.plot.BasicSource,
            {
                'indep_var':numpy.array([1, 2, 3]),
                'dep_var':numpy.array([10, 20, 30]),
                'indep_min':4, 'indep_max':10
            },
            ValueError,
            msg
        )
        # Managed attribute path
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([10, 20, 30])
        )
        # Wrong type
        assert (obj.indep_var == numpy.array([1, 2, 3])).all()
        for item in items:
            with pytest.raises(RuntimeError) as excinfo:
                obj.indep_var = item
            assert (
                putil.test.get_exmsg(excinfo)
                ==
                'Argument `indep_var` is not valid'
            )

    def test_dep_var(self):
        """ Tests dep_var property behavior """
        # __init__ path
        # Valid values, these should not raise any exception
        indep_var = numpy.array([10, 20, 30])
        dep_var1 = numpy.array([1, 2, 3])
        dep_var2 = numpy.array([4.0, 5.0, 6.0])
        assert (
            putil.plot.BasicSource(
                indep_var=indep_var,
                dep_var=dep_var1
            ).dep_var == dep_var1
        ).all()
        assert (
            putil.plot.BasicSource(
                indep_var=indep_var,
                dep_var=dep_var2
            ).dep_var == dep_var2
        ).all()
        # Managed attribute path
        obj = putil.plot.BasicSource(indep_var=indep_var, dep_var=dep_var1)
        obj.dep_var = dep_var1
        assert (obj.dep_var == dep_var1).all()
        obj.dep_var = dep_var2
        assert (obj.dep_var == dep_var2).all()

    @pytest.mark.basic_source
    def test_dep_var_exceptions(self):
        """ Tests dep_var property exceptions """
        # __init__ path
        msg = 'Argument `dep_var` is not valid'
        items = [None, 'a', []]
        for item in items:
            putil.test.assert_exception(
                putil.plot.BasicSource,
                {'indep_var':numpy.array([1, 2, 3]), 'dep_var':item},
                RuntimeError,
                msg
            )
        # Managed attribute path
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3]),
            dep_var=numpy.array([1, 2, 3])
        )
        for item in items:
            with pytest.raises(RuntimeError) as excinfo:
                obj.dep_var = item
            assert putil.test.get_exmsg(excinfo) == msg

    @pytest.mark.basic_source
    def test_indep_dep_var_not_same_number_of_elements_exceptions(self):
        """ Tests indep_var and dep_var vector congruency """
        msg = (
            'Arguments `indep_var` and `dep_var` '
            'must have the same number of elements'
        )
        # Both set at object creation
        putil.test.assert_exception(
            putil.plot.BasicSource,
            {
                'indep_var':numpy.array([10, 20, 30]),
                'dep_var':numpy.array([1, 2, 3, 4, 5, 6]),
                'indep_min':30,
                'indep_max':50
            },
            ValueError,
            msg
        )
        putil.test.assert_exception(
            putil.plot.BasicSource,
            {
                'indep_var':numpy.array([10, 20, 30]),
                'dep_var':numpy.array([1, 2]),
                'indep_min':30,
                'indep_max':50
            },
            ValueError,
            msg
        )
        # indep_var set first
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([10, 20, 30, 40, 50, 60]),
            dep_var=numpy.array([1, 2, 3, 4, 5, 6]),
            indep_min=30,
            indep_max=50)
        with pytest.raises(ValueError) as excinfo:
            obj.dep_var = numpy.array([100, 200, 300])
        assert putil.test.get_exmsg(excinfo) == msg
        # dep_var set first
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([10, 20, 30]),
            dep_var=numpy.array([100, 200, 300]),
            indep_min=30,
            indep_max=50
        )
        with pytest.raises(ValueError) as excinfo:
            obj.indep_var = numpy.array([10, 20, 30, 40, 50, 60])
        assert putil.test.get_exmsg(excinfo) == msg

    @pytest.mark.basic_source
    def test_cannot_delete_attributes_exceptions(self):
        """
        Test that del method raises an exception on all class attributes
        """
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([10, 20, 30]),
            dep_var=numpy.array([100, 200, 300])
        )
        with pytest.raises(AttributeError) as excinfo:
            del obj.indep_min
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.indep_max
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.indep_var
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.dep_var
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
