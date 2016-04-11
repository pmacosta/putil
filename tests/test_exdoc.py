# -*- coding: utf-8 -*-
# test_exdoc.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0411,E0012,E0611,F0401,R0201,R0903,W0104,W0212,W0612,W0613,W0621

# Standard library imports
from __future__ import print_function
import imp
import copy
import os
import sys
if sys.hexversion >= 0x03000000:
    import importlib
    import unittest.mock as mock
if sys.hexversion < 0x03000000:
    import __builtin__
else:
    import builtins as __builtin__
# PyPI imports
import pytest
if sys.hexversion < 0x03000000:
    import mock
# Putil imports
import putil.exdoc
import putil.exh
import putil.misc
from putil.test import AE, AI, AROPROP, CS, GET_EXMSG
import tests.support.exdoc_support_module_1
import tests.support.exdoc_support_module_3
import tests.support.exdoc_support_module_4
import tests.support.exdoc_support_module_5


###
# Global variables
###
TEST_DIR = os.path.realpath(os.path.dirname(__file__))
SEQ = [
    (os.path.join(TEST_DIR, 'support', 'exdoc_support_module_1.py+{0}'), 99),
    (os.path.join(TEST_DIR, 'support', 'exdoc_support_module_1.py+{0}'), 197),
    (os.path.join(TEST_DIR, 'support', 'exdoc_support_module_4.py+{0}'), 23),
    (os.path.join(TEST_DIR, 'support', 'exdoc_support_module_1.py+{0}'), 1000)
]


###
# Fixtures
###
@pytest.fixture
def exdocobj():
    """ Trace support module class """
    if putil.exh.get_exh_obj():
        putil.exh.del_exh_obj()
    def multi_level_write():
        """
        Test that multiple calls to the same function with different hierarchy
        levels get correctly aggregated
        """
        tests.support.exdoc_support_module_1.write(True)
    with putil.exdoc.ExDocCxt(_no_print=True, exclude=['_pytest']) as exdobj:
        obj = tests.support.exdoc_support_module_1.ExceptionAutoDocClass(10)
        obj.add(5)
        obj.subtract(3)
        obj.divide(5.2)
        obj.multiply(5.2)
        obj.value1 = 11
        obj.value1
        obj.value2 = 33
        obj.value2
        obj.value3 = 77
        obj.value3
        del obj.value3
        obj.temp = 10
        obj.temp
        del obj.temp
        tests.support.exdoc_support_module_1.write()
        multi_level_write()
        tests.support.exdoc_support_module_1.read()
        tests.support.exdoc_support_module_1.probe()
    return exdobj


@pytest.fixture
def exdocobj_raised():
    """ Trace support module class with raised argument """
    if putil.exh.get_exh_obj():
        putil.exh.del_exh_obj()
    with putil.exdoc.ExDocCxt(_no_print=True, exclude=['_pytest']) as exdobj:
        tests.support.exdoc_support_module_5.float_func(43.0)
        try:
            tests.support.exdoc_support_module_5.float_func(-5.0)
        except ValueError:
            pass
    return exdobj


@pytest.fixture
def exdocobj_single():
    """ Trace support module that only has one callable """
    if putil.exh.get_exh_obj():
        putil.exh.del_exh_obj()
    with putil.exdoc.ExDocCxt(_no_print=True) as exdoc_single_obj:
        tests.support.exdoc_support_module_4.func('John')
    return exdoc_single_obj


@pytest.fixture
def simple_exobj():
    """ Create simple exception handler for miscellaneous property tests """
    # pylint: disable=R0914
    exobj = putil.exh.ExHandle(True)
    def func1():
        exobj.add_exception(
            'first_exception', TypeError, 'This is the first exception'
        )
    func1()
    return exobj


###
# Helper functions
###
def mock_getframe(num):
    return MockGetFrame()


def trace_error_class():
    """ Trace classes that use the same getter function """
    if putil.exh.get_exh_obj():
        putil.exh.del_exh_obj()
    putil.exh.set_exh_obj(putil.exh.ExHandle(True))
    obj = tests.support.exdoc_support_module_3.Class1()
    obj.value1


###
# Helper classes
###
class MockFCode(object):
    def __init__(self):
        text, line_no = SEQ.pop(0)
        self.co_filename = text.format(line_no)


class MockGetFrame(object):
    def __init__(self):
        self.f_code = MockFCode()


###
# Test classes
###
class TestExDocCxt(object):
    """ Tests for ExDocCxt class """
    def test_init(self):
        """ Test constructor behavior """
        # Helper functions
        def check_ctx1(name=None, kwargs=None):
            exmsg = 'Argument `{0}` is not valid'.format(name)
            with pytest.raises(RuntimeError) as excinfo:
                with putil.exdoc.ExDocCxt(**kwargs):
                    putil.misc.pcolor('a', 'red')
            assert GET_EXMSG(excinfo) == exmsg
        def check_ctx2(name=None, kwargs=None):
            exmsg = 'Argument `in_callables_fname` is not valid'
            with pytest.raises(RuntimeError) as excinfo:
                with putil.exdoc.ExDocCxt(**kwargs):
                    func0()
            assert GET_EXMSG(excinfo) == exmsg
        # Function to use for tests
        def func0():
            exobj = putil.exh.get_or_create_exh_obj(
                full_cname=True, exclude=['_pytest']
            )
            exobj.add_exception(
                'first_exception', TypeError, 'This is the first exception'
            )
        if putil.exh.get_exh_obj():
            putil.exh.del_exh_obj()
        with pytest.raises(OSError) as excinfo:
            with putil.exdoc.ExDocCxt(_no_print=True):
                raise OSError('This is bad')
        assert GET_EXMSG(excinfo) == 'This is bad'
        assert putil.exh.get_exh_obj() is None
        #
        check_ctx1('_no_print', dict(_no_print='a'))
        check_ctx1('exclude', dict(exclude=5))
        #
        for item in [5, 'test\0']:
            check_ctx1('pickle_fname', dict(pickle_fname=item))
        #
        with putil.misc.TmpFile() as fname:
            with putil.exdoc.ExDocCxt(pickle_fname=fname):
                func0()
            assert os.path.isfile(fname)
        #
        for item in [5, 'test\0']:
            check_ctx1('in_callables_fname', dict(in_callables_fname=item))
        #
        with pytest.raises(OSError) as excinfo:
            with putil.exdoc.ExDocCxt(in_callables_fname='_not_a_file_'):
                func0()
        assert GET_EXMSG(excinfo) == 'File _not_a_file_ could not be found'
        #
        for item in [5, 'test\0']:
            check_ctx1('out_callables_fname', dict(out_callables_fname=item))

    def test_multiple(self):
        """ Test multiple-CPU tracing behavior """
        def func1():
            exobj = putil.exh.get_or_create_exh_obj(
                full_cname=True, exclude=['_pytest']
            )
            exobj.add_exception(
                'first_exception', TypeError, 'This is the first exception'
            )
        def test_trace():
            cobj = putil.exdoc.ExDocCxt
            with cobj(_no_print=True, exclude=['_pytest']) as tobj:
                tests.support.exdoc_support_module_4.func('John')
                obj1 = copy.copy(putil.exh.get_exh_obj())
                putil.exh.del_exh_obj()
                putil.exh.get_or_create_exh_obj(
                    full_cname=True, exclude=['_pytest']
                )
                func1()
                obj2 = copy.copy(putil.exh.get_exh_obj())
                setattr(__builtin__, '_EXH_LIST', [obj1, obj2])
            assert tobj._exh_obj == obj1+obj2
            assert not hasattr(__builtin__, '_EXH_LIST')
            assert not hasattr(__builtin__, '_EXDOC_FULL_CNAME')
            assert not hasattr(__builtin__, '_EXDOC_EXCLUDE')
        # Test without prior exception handler
        putil.exh.del_exh_obj()
        test_trace()
        assert not hasattr(__builtin__, '_EXH')
        # Test with prior exception handler
        from putil.eng import peng
        putil.exh.get_or_create_exh_obj()
        peng(3.125, 1)
        prev_exhobj = copy.copy(putil.exh.get_exh_obj())
        test_trace()
        assert prev_exhobj == putil.exh.get_exh_obj()

    def test_save_callables(self):
        """ Test traced modules information storage """
        putil.exh.del_exh_obj()
        cobj = putil.exdoc.ExDocCxt
        with putil.misc.TmpFile() as fname:
            out_callables_fname = fname
            with cobj(out_callables_fname=out_callables_fname) as tobj:
                tests.support.exdoc_support_module_4.func('John')
            pobj1 = putil.pinspect.Callables()
            pobj1.load(out_callables_fname)
        fname = sys.modules['tests.support.exdoc_support_module_4'].__file__
        pobj2 = putil.pinspect.Callables([__file__, fname])
        assert pobj1 == pobj2


###
# Test classes
###
class TestExDoc(object):
    """ Tests for ExDoc class """
    def test_init(self, simple_exobj):
        """ Test constructor behavior """
        obj = putil.exdoc.ExDoc
        AI(obj, 'exh_obj', exh_obj=5, _no_print=False)
        AI(obj, 'depth', exh_obj=simple_exobj, depth='hello')
        AI(obj, 'depth', exh_obj=simple_exobj, depth=-1)
        AI(obj, 'exclude', exh_obj=simple_exobj, exclude=-1)
        AI(obj, 'exclude', exh_obj=simple_exobj, exclude=['hello', 3])
        exmsg = (
            'Object of argument `exh_obj` does not '
            'have any exception trace information'
        )
        args = {'exh_obj':putil.exh.ExHandle(True), '_no_print':False}
        AE(obj, ValueError, exmsg, **args)
        AI(obj, '_no_print', exh_obj=simple_exobj, _no_print=5)
        putil.exdoc.ExDoc(simple_exobj, depth=1, exclude=[])

    def test_copy(self, exdocobj):
        """ Test __copy__ method behavior """
        exdocobj.exclude = ['a', 'b', 'c']
        nobj = copy.copy(exdocobj)
        assert id(nobj) != id(exdocobj)
        assert nobj._depth == exdocobj._depth
        assert nobj._exclude == exdocobj._exclude
        assert id(nobj._exclude) != id(exdocobj._exclude)
        assert nobj._no_print == exdocobj._no_print
        assert id(nobj._exh_obj) != id(exdocobj._exh_obj)
        assert id(nobj._tobj) != id(exdocobj._tobj)
        assert nobj._module_obj_db == exdocobj._module_obj_db
        assert id(nobj._module_obj_db) != id(exdocobj._module_obj_db)

    def test_build_ex_tree(self, exdocobj):
        """ Test _build_ex_tree method behavior """
        with pytest.raises(RuntimeError) as excinfo:
            with putil.exdoc.ExDocCxt():
                pass
        assert GET_EXMSG(excinfo) == 'Exceptions database is empty'
        exobj1 = putil.exh.ExHandle(full_cname=True)
        def func1():
            exobj1.add_exception(
                'first_exception', TypeError, 'This is the first exception'
            )
        func1()
        def mock_add_nodes1(self):
            raise ValueError('Illegal node name: _node_')
        def mock_add_nodes2(self):
            raise ValueError('General exception #1')
        def mock_add_nodes3(self):
            raise OSError('General exception #2')
        ref = (
            'tests.test_exdoc.exdocobj\n'
            '├mod.ExceptionAutoDocClass.__init__ (*)\n'
            '│├putil.tree.Tree.__init__ (*)\n'
            '│└putil.tree.Tree.add_nodes (*)\n'
            '│ └putil.tree.Tree._validate_nodes_with_data (*)\n'
            '├mod.ExceptionAutoDocClass.divide (*)\n'
            '├mod.ExceptionAutoDocClass.multiply (*)\n'
            '├mod.ExceptionAutoDocClass.temp(setter) (*)\n'
            '├mod.ExceptionAutoDocClass.value1(getter) (*)\n'
            '├mod.ExceptionAutoDocClass.value1(setter) (*)\n'
            '├mod.ExceptionAutoDocClass.value2(setter) (*)\n'
            '├mod.ExceptionAutoDocClass.value3(deleter) (*)\n'
            '├mod.ExceptionAutoDocClass.value3(getter) (*)\n'
            '├mod.ExceptionAutoDocClass.value3(setter) (*)\n'
            '├mod.probe (*)\n'
            '├mod.read (*)\n'
            '├mod.write (*)\n'
            '└tests.test_exdoc.exdocobj.multi_level_write\n'
            ' └mod.write (*)\n'
            '  └mod._write\n'
            '   └mod._validate_arguments (*)'
        )
        ref = ref.replace('mod.', 'tests.support.exdoc_support_module_1.')
        CS(str(exdocobj._tobj), ref)
        trace_error_class()
        sfunc = 'putil.tree.Tree.add_nodes'
        with mock.patch(sfunc, side_effect=mock_add_nodes1):
            AE(
                putil.exdoc.ExDoc, RuntimeError,
                'Exceptions do not have a common callable',
                exh_obj=exobj1, _no_print=True,
            )
        with mock.patch(sfunc, side_effect=mock_add_nodes2):
            AE(
                putil.exdoc.ExDoc, ValueError, 'General exception #1',
                exh_obj=exobj1, _no_print=True,
            )
        with mock.patch(sfunc, side_effect=mock_add_nodes3):
            AE(
                putil.exdoc.ExDoc, OSError, 'General exception #2',
                exh_obj=exobj1, _no_print=True
            )
        # Create exception tree where branching is right at root node
        exobj = putil.exh.ExHandle()
        exobj._ex_dict = {
            12345: {
                (RuntimeError, 'Exception 1'): {
                    'function':['root/leaf1'],
                    'raised': [False],
                    'name':'root/leaf1'
                }
            },
            67899:{
                (OSError, 'Exception 2'): {
                    'function':['root.leaf2'],
                    'raised': [False],
                    'name':'root/leaf2'
                }
            }
        }
        exobj._callables_obj._callables_db = {
            'root':{
                'type':'func', 'code_id':('file', 50), 'attr':None, 'link':[]
            },
            'leaf1':{
                'type':'func', 'code_id':('file', 50), 'attr':None, 'link':[]
            },
            'leaf2':{
                'type':'func', 'code_id':('file', 60), 'attr':None, 'link':[]
            },
        }
        exdocobj = putil.exdoc.ExDoc(exobj, _no_print=True, _empty=True)
        exdocobj._build_ex_tree()
        ref = (
            'root\n'
            '├leaf1 (*)\n'
            '└leaf2 (*)'
        )
        putil.test.compare_strings(str(exdocobj._tobj), ref)

    def test_depth(self, simple_exobj):
        """ Test depth property behavior """
        obj = putil.exdoc.ExDoc(simple_exobj, _no_print=True)
        assert obj.depth is None
        obj.depth = 5
        assert obj.depth == 5
        AROPROP(obj, 'depth')

    def test_exclude(self, simple_exobj):
        """ Test exclude property behavior """
        obj = putil.exdoc.ExDoc(simple_exobj, _no_print=True)
        assert obj.exclude is None
        obj.exclude = ['a', 'b']
        assert obj.exclude == ['a', 'b']
        AROPROP(obj, 'exclude')

    def test_get_sphinx_autodoc(self, exdocobj, exdocobj_single):
        """ Test get_sphinx_autodoc method behavior """
        mobj = sys.modules['putil.exdoc']
        delattr(mobj, 'sys')
        del sys.modules['sys']
        if sys.hexversion < 0x03000000:
            nsys = imp.load_module('sys_patched', *imp.find_module('sys'))
        else:
            nsys = importlib.import_module('sys')
        setattr(mobj, 'sys', nsys)
        sfunc = 'putil.exdoc.sys._getframe'
        with mock.patch(sfunc, side_effect=mock_getframe):
            tstr = exdocobj.get_sphinx_autodoc()
            assert tstr == ''
            tstr = exdocobj.get_sphinx_autodoc()
            CS(tstr,
                '.. Auto-generated exceptions documentation for\n'
                '.. tests.support.exdoc_support_module_1.'
                'ExceptionAutoDocClass.multiply\n\n'
                ':raises: ValueError (Overflow)\n\n'
            )
            tstr = exdocobj_single.get_sphinx_autodoc()
            CS(tstr,
                '.. Auto-generated exceptions documentation for\n'
                '.. tests.support.exdoc_support_module_4.func\n\n'
                ':raises: TypeError (Argument \\`name\\` is not valid)\n\n'
            )

    def test_get_sphinx_doc(self, exdocobj, exdocobj_raised):
        """ Test get_sphinx_doc method behavior """
        # pylint: disable=R0915
        obj = exdocobj.get_sphinx_doc
        exmsg = 'Callable not found in exception list: _not_found_'
        AE(obj, RuntimeError, exmsg, name='_not_found_', error=True)
        AI(obj, 'depth', name='callable', depth='hello')
        AI(obj, 'depth', name='callable', depth=-1)
        AI(obj, 'exclude', name='callable', exclude=-1)
        AI(obj, 'exclude', name='callable', exclude=['hello', 3])
        AI(obj, 'width', name='callable', width=1.0)
        AI(obj, 'width', name='callable', width=5)
        AI(obj, 'error', name='callable', error=5)
        AI(obj, 'raised', name='callable', raised=5)
        AI(obj, 'raised', name='callable', no_comment=5)
        minwidth = putil.exdoc._MINWIDTH
        assert obj('_not_found_') == ''
        root = 'tests.support.exdoc_support_module_1.'
        assert obj(root+'read', raised=True) == ''
        CS(obj(root+'read'),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.read\n'
            '\n'
            ':raises: TypeError (Cannot call read)\n'
            '\n'
        )
        assert obj(root+'read', raised=True, no_comment=True) == ''
        CS(obj(root+'read', no_comment=True),
            '\n'
            ':raises: TypeError (Cannot call read)\n'
            '\n'
        )
        putil.exdoc._MINWIDTH = 16
        CS(obj(root+'read', width=16),
            '.. Auto-\n'
            '.. generated\n'
            '.. exceptions\n'
            '.. documentation\n'
            '.. for tests.sup\n'
            '.. port.exdoc_su\n'
            '.. pport_module_\n'
            '.. 1.read\n'
            '\n'
            ':raises:\n'
            ' TypeError\n'
            ' (Cannot call\n'
            ' read)\n'
            '\n'
        )
        putil.exdoc._MINWIDTH = minwidth
        CS(obj(root+'write'),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.write'
            '\n\n:raises:\n * TypeError (Argument is not valid)'
            '\n\n * TypeError (Cannot call write)\n\n'
        )
        putil.exdoc._MINWIDTH = 16
        CS(obj(root+'write', width=16),
            '.. Auto-\n'
            '.. generated\n'
            '.. exceptions\n'
            '.. documentation\n'
            '.. for tests.sup\n'
            '.. port.exdoc_su\n'
            '.. pport_module_\n'
            '.. 1.write\n'
            '\n'
            ':raises:\n'
            ' * TypeError\n'
            '   (Argument is\n'
            '   not valid)\n'
            '\n'
            ' * TypeError\n'
            '   (Cannot call\n'
            '   write)\n'
            '\n'
        )
        putil.exdoc._MINWIDTH = minwidth
        CS(obj(root+'write', depth=1),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.write'
            '\n\n:raises: TypeError (Cannot call write)\n\n'
        )
        CS(obj(root+'ExceptionAutoDocClass.__init__', depth=1),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
            '__init__\n\n:raises:\n'
            ' * RuntimeError '
            '(Argument \\`node_separator\\` is not valid)\n\n '
            '* RuntimeError (Argument \\`value1\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value2\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value3\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value4\\` is not valid)\n\n'
            ' * ValueError (Illegal node name: *[node_name]*)\n\n'
        )
        CS(obj(root+'ExceptionAutoDocClass.__init__', depth=0),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
            '__init__\n\n'
            ':raises:\n'
            ' * RuntimeError (Argument \\`value1\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value2\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value3\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value4\\` is not valid)\n\n'
        )
        CS(obj(root+'ExceptionAutoDocClass.__init__', exclude=['putil.tree']),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
            '__init__\n\n'
            ':raises:\n'
            ' * RuntimeError (Argument \\`value1\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value2\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value3\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value4\\` is not valid)\n\n'
        )
        tstr = obj(
            root+'ExceptionAutoDocClass.__init__',
            exclude=['add_nodes', '_validate_nodes_with_data']
        )
        CS(tstr,
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
            '__init__\n\n'
            ':raises:\n'
            ' * RuntimeError (Argument \\`node_separator\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value1\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value2\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value3\\` is not valid)\n\n'
            ' * RuntimeError (Argument \\`value4\\` is not valid)\n\n'
        )
        CS(obj(root+'ExceptionAutoDocClass.value3'),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
            'value3\n\n'
            ':raises:\n'
            ' * When assigned\n\n'
            '   * TypeError (Argument \\`value3\\` is not valid)\n\n'
            ' * When deleted\n\n'
            '   * TypeError (Cannot delete value3)\n\n'
            ' * When retrieved\n\n'
            '   * TypeError (Cannot get value3)\n\n'
        )
        putil.exdoc._MINWIDTH = 16
        CS(obj(root+'ExceptionAutoDocClass.value3', width=16),
            '.. Auto-\n'
            '.. generated\n'
            '.. exceptions\n'
            '.. documentation\n'
            '.. for tests.sup\n'
            '.. port.exdoc_su\n'
            '.. pport_module_\n'
            '.. 1.ExceptionAu\n'
            '.. toDocClass.va\n'
            '.. lue3\n'
            '\n'
            ':raises:\n'
            ' * When assigned\n'
            '\n'
            '   * TypeError\n'
            '     (Argument\n'
            '     \\`value3\\`\n'
            '     is not\n'
            '     valid)\n'
            '\n'
            ' * When deleted\n'
            '\n'
            '   * TypeError\n'
            '     (Cannot\n'
            '     delete\n'
            '     value3)\n'
            '\n'
            ' * When retrieved\n'
            '\n'
            '   * TypeError\n'
            '     (Cannot get\n'
            '     value3)\n'
            '\n'
        )
        putil.exdoc._MINWIDTH = minwidth
        CS(obj(root+'ExceptionAutoDocClass.temp'),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
            'temp\n\n'
            ':raises: (when assigned) RuntimeError (Argument \\`value\\`'
            ' is not\n'
            ' valid)\n\n'
        )
        putil.exdoc._MINWIDTH = 16
        CS(obj(root+'ExceptionAutoDocClass.temp', width=16),
            '.. Auto-\n'
            '.. generated\n'
            '.. exceptions\n'
            '.. documentation\n'
            '.. for tests.sup\n'
            '.. port.exdoc_su\n'
            '.. pport_module_\n'
            '.. 1.ExceptionAu\n'
            '.. toDocClass.te\n'
            '.. mp\n'
            '\n'
            ':raises: (when\n'
            ' assigned)\n'
            ' RuntimeError\n'
            ' (Argument\n'
            ' \\`value\\` is\n'
            ' not valid)\n'
            '\n'
        )
        putil.exdoc._MINWIDTH = minwidth
        CS(obj(root+'ExceptionAutoDocClass.value2'),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
            'value2\n\n'
            ':raises: (when assigned)\n\n'
            ' * OSError (Argument \\`value2\\` is not a file)\n\n'
            ' * TypeError (Argument \\`value2\\` is not valid)\n\n'
        )
        putil.exdoc._MINWIDTH = 16
        CS(obj(root+'ExceptionAutoDocClass.value2', width=16),
            '.. Auto-\n'
            '.. generated\n'
            '.. exceptions\n'
            '.. documentation\n'
            '.. for tests.sup\n'
            '.. port.exdoc_su\n'
            '.. pport_module_\n'
            '.. 1.ExceptionAu\n'
            '.. toDocClass.va\n'
            '.. lue2\n'
            '\n'
            ':raises: (when assigned)\n'
            '\n'
            ' * OSError\n'
            '   (Argument\n'
            '   \\`value2\\` is\n'
            '   not a file)\n'
            '\n'
            ' * TypeError\n'
            '   (Argument\n'
            '   \\`value2\\` is\n'
            '   not valid)\n'
            '\n'
        )
        putil.exdoc._MINWIDTH = minwidth
        # Test raised argument behaves as expected
        obj = exdocobj_raised.get_sphinx_doc
        root = 'tests.support.exdoc_support_module_5.'
        CS(obj(root+'float_func'),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_5.float_func\n\n'
            ':raises:\n'
            ' * TypeError (Argument \\`arg\\` is not valid)\n\n'
            ' * ValueError (Argument \\`arg\\` is illegal)\n\n'
        )
        CS(obj(root+'float_func', raised=True),
            '.. Auto-generated exceptions documentation for\n'
            '.. tests.support.exdoc_support_module_5.float_func\n\n'
            ':raises: ValueError (Argument \\`arg\\` is illegal)\n\n'
        )
