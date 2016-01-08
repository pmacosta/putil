# pinspect_support_module_1.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0411,C0413,R0201,R0903,W0212,W0621

from __future__ import print_function
import sys
import putil.exh
import putil.pcontracts
import tests.support.pinspect_support_module_2


def module_enclosing_func(offset):
    """ Test function to see if module-level enclosures are detected """
    def module_closure_func(value):
        """ Actual closure function """
        return offset+value
    return module_closure_func


def class_enclosing_func():
    """ Test function to see if classes within enclosures are detected """
    import tests.support.pinspect_support_module_3
    class ClosureClass(object):
        r''' Actual closure class '''
        def __init__(self):
            """ Constructor method """
            self.obj = None

        def get_obj(self):
            """ Getter method """
            return self.obj

        def set_obj(self, obj):
            """
            Setter method
            """
            self.obj = obj

        def sub_enclosure_method(self):
            """ Test method to see if class of classes are detected """
            class SubClosureClass(object):
                """ Actual sub-closure class """
                def __init__(self):
                    """ Constructor method """
                    self.subobj = None
            return SubClosureClass

        mobj = sys.modules['tests.support.pinspect_support_module_2']
        obj = property(
            mobj.getter_func_for_closure_class,
            set_obj,
            tests.support.pinspect_support_module_3.deleter
        )

    return ClosureClass


class ClassWithPropertyDefinedViaLambdaAndEnclosure(object):
    """
    Class that used an inline function (lambda) to define one of the property
    functions and an enclosed function to define another
    """
    def __init__(self):
        self._clsvar = None

    clsvar = property(
        lambda self: self._clsvar+10,
        tests.support.pinspect_support_module_2.setter_enclosing_func(5),
        doc='Class variable property'
    )


def dummy_decorator(func):
    """
    Dummy property decorator, to test if chained decorators are handled
    correctly
    """
    return func


def simple_property_generator():
    """
    Function to test if properties done via enclosed functions are
    properly detected
    """
    def fget(self):
        """ Actual getter function """
        return self._value
    return property(fget)


class ClassWithPropertyDefinedViaFunction(object):
    """
    Class to test if properties defined via property function are
    handled correctly
    """
    def __init__(self):
        self._state = None

    @putil.pcontracts.contract(state=int)
    @dummy_decorator
    def _setter_func(self, state):
        """ Setter method with property defined via property() function """
        exobj = (putil.exh.get_exh_obj()
                if putil.exh.get_exh_obj() else
                putil.exh.ExHandle())
        exobj.add_exception(
            exname='dummy_exception_1',
            extype=ValueError,
            exmsg='Dummy message 1'
        )
        exobj.add_exception(
            exname='dummy_exception_2',
            extype=TypeError,
            exmsg='Dummy message 2'
        )
        self._state = state

    def _getter_func(self):
        """ Getter method with property defined via property() function """
        return self._state

    def _deleter_func(self):
        """ Deleter method with property defined via property() function """
        print('Cannot delete attribute')

    state = property(
        _getter_func,
        _setter_func,
        _deleter_func,
        doc='State attribute'
    )


import math


class ClassWithPropertyDefinedViaDecorators(object):
    """
    Class to test if properties defined via decorator functions are
    handled correctly
    """
    def __init__(self):
        self._value = None

    def __call__(self):
        self._value = 2*self._value if self._value else self._value

    @property
    def temp(self):
        """ Getter method defined with decorator """
        return math.sqrt(self._value)

    @temp.setter
    @putil.pcontracts.contract(value=int)
    def temp(self, value):
        """ Setter method defined with decorator """
        self._value = value

    @temp.deleter
    def temp(self):
        """ Deleter method defined with decorator """
        print('Cannot delete attribute')

    encprop = simple_property_generator()


import tests.support.pinspect_support_module_4


def class_namespace_test_enclosing_func():
    """ Test namespace support for enclosed class properties """
    class NamespaceTestClosureClass(object):
        r''' Actual class
        ''' #This is to test a comment after a multi-line docstring
        def __init__(self,
               value):
            _, _, _ = (5, \
                3,
                7)

            self._value = value

        nameprop = (tests.support.pinspect_support_module_4.
                   another_property_action_enclosing_function())

    return NamespaceTestClosureClass
