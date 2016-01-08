# exdoc_support_module_1.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0613

import decorator

import putil.exh
import putil.tree
import putil.pcontracts
import tests.support.exdoc_support_module_2


###
# Module functions
###
def _validate_arguments():
    """
    Internal argument validation, have exceptions defined after a
    chain of function calls
    """
    exobj = (putil.exh.get_exh_obj()
            if putil.exh.get_exh_obj() else
            putil.exh.ExHandle())
    exobj.add_exception(
        exname='illegal_argument',
        extype=TypeError,
        exmsg='Argument is not valid'
    )


def _write():
    """ Internal pass-through function """
    _validate_arguments()


def write(validate=False):
    """ Module level function #1 """
    exobj = (putil.exh.get_exh_obj()
            if putil.exh.get_exh_obj() else
            putil.exh.ExHandle())
    exobj.add_exception(
        exname='illegal_write_call',
        extype=TypeError,
        exmsg='Cannot call write'
    )
    if validate:
        _write()


def read():
    """ Module level function #2 """
    exobj = (putil.exh.get_exh_obj()
            if putil.exh.get_exh_obj() else
            putil.exh.ExHandle())
    exobj.add_exception(
        exname='illegal_read_call',
        extype=TypeError,
        exmsg='Cannot call read'
    )


def probe():
    """ Module level function #3 """
    exobj = (putil.exh.get_exh_obj()
            if putil.exh.get_exh_obj() else
            putil.exh.ExHandle())
    exobj.add_exception(
        exname='illegal_probe_call',
        extype=TypeError,
        exmsg='Cannot call probe'
    )


def dummy_decorator1(func):
    """ Dummy property decorator """
    return func


def dummy_decorator2(**dargs):
    """
    Decorator with multiple parameters, suitable to test
    handling of multiple decorators whose instantiation takes multiple
    lines
    """
    @decorator.decorator
    def wrapper(func, *args, **kwargs):
        return func
    return wrapper


@putil.pcontracts.contract(
    value1=int,
    value2=int,
    value3=int,
    value4=int
)
@dummy_decorator2(
    darg1=False,
    darg2=True
)
def mlmdfunc(arg1, arg2, arg3):
    pass


###
# Classes
###
class ExceptionAutoDocClass(object):
    """ Class to automatically generate exception documentation for """
    # pylint: disable=R0902,W0212
    @putil.pcontracts.contract(value1=int, value2=int, value3=int, value4=int)
    @dummy_decorator1
    def __init__(self, value1=0, value2=0, value3=0, value4=0):
        self._exobj = (putil.exh.get_exh_obj()
                      if putil.exh.get_exh_obj() else
                      putil.exh.ExHandle())
        tobj = putil.tree.Tree('.')
        tobj.add_nodes({'name':'a.b.c', 'data':list()})
        self._value1 = value1
        self._value2 = value2
        self._value3 = value3
        self._value4 = value4

    def _del_value3(self):
        """ Deleter method for property defined via function """
        self._exobj.add_exception(
            exname='illegal_value3',
            extype=TypeError,
            exmsg='Cannot delete value3'
        )

    def _get_value3(self):
        """ Getter method for property defined via function """
        self._exobj.add_exception(
            exname='illegal_value3',
            extype=TypeError,
            exmsg='Cannot get value3'
        )
        return self._value3

    def _set_value1(self, value):
        """
        Setter method for property with getter defined via enclosed function
        """
        self._exobj.add_exception(
            exname='illegal_value1',
            extype=TypeError,
            exmsg='Argument `value1` is not valid'
        )
        self._value1 = value

    def _set_value2(self, value):
        """ Setter method for property with getter defined via lambda """
        self._exobj.add_exception(
            exname='illegal_value2_1',
            extype=TypeError,
            exmsg='Argument `value2` is not valid'
        )
        self._exobj.add_exception(
            exname='illegal_value2_2',
            extype=OSError,
            exmsg='Argument `value2` is not a file'
        )
        self._value2 = value

    def _set_value3(self, value):
        """
        Setter method for property defined via function (multi-line docstring)
        """
        self._exobj.add_exception(
            exname='illegal_value3',
            extype=TypeError,
            exmsg='Argument `value3` is not valid'
        )
        self._value3 = value

    def add(self, operand):
        """
        Method #1 that should not appear in exception tree since it has no
        exceptions defined
        """
        self._value1 += operand

    def subtract(self, operand):
        """
        Method #2 that should not appear in exception tree since it has no
        exceptions defined
        """
        self._value1 -= operand

    def multiply(self, operand):
        """
        Sample method with defined exceptions in function body
        to auto-document
        """
        self._exobj.add_exception(
            exname='maximum_value',
            extype=ValueError,
            exmsg='Overflow'
        )
        self._value1 *= operand

    # Multi-line single decorator
    @putil.pcontracts.contract(
        divisor='int|float,>0'
    )
    def divide(self, divisor):
        """
        Sample method with defined exceptions in argument contract to
        auto-document
        """
        self._value1 = self._value1/float(divisor)

    @property
    def temp(self):
        """ Getter method defined with decorator """
        return self._value4

    @temp.setter
    @putil.pcontracts.contract(value=int)
    def temp(self, value):
        """ Setter method defined with decorator """
        self._value4 = value

    @temp.deleter
    def temp(self):
        """ Deleter method defined with decorator """
        pass

    # Multi-line property
    value1 = property(
        tests.support.exdoc_support_module_2.module_enclosing_func(10),
        _set_value1
    )
    """
    This is the docstring for the property value1
    (multi-line)
    """

    value2 = property(
        lambda self: self._value2+10,
        _set_value2
    )
    """ This is the docstring for the property value2 (single line) """

    value3 = property(_get_value3, _set_value3, _del_value3)

    value4 = property()

# Test that last property is closed correctly
def my_func():
    pass

class MyClass(object):
    """
    Class test if property as last line of file gets closed out correctly
    """
    value = property()
