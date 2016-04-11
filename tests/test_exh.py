
# test_exh.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,C0413,E0611,F0401,R0201,R0204,R0903,R0912
# pylint: disable=R0914,R0915,W0108,W0122,W0123,W0212,W0612,W0631,W0640

# Standard library imports
from __future__ import print_function
import collections
import copy
import os
import re
import sys
from itertools import product
if sys.hexversion >= 0x03000000:
    import unittest.mock as mock
# PyPI imports
import pytest
if sys.hexversion < 0x03000000:
    import mock
# Putil imports
import putil.eng
import putil.exh
import putil.misc
import putil.pcontracts
from putil.test import AE, AI, AROPROP, CLDICTS, GET_EXMSG
TEST_DIR = os.path.realpath(os.path.dirname(__file__))
SUPPORT_DIR = os.path.join(TEST_DIR, 'support')
sys.path.append(SUPPORT_DIR)
import exh_support_module_1
import exh_support_module_2

if sys.hexversion > 0x03000000:
    def exec_function(source, filename, global_map):
        """ A wrapper around exec() """
        exec(compile(source, filename, 'exec'), global_map)
else:
    # From https://stackoverflow.com/questions/12809234/
    # is-it-possible-to-call-exec-so-that-its-compatible-with-
    # both-python-3-and-pytho
    # "OK, this is pretty gross. In Py2, exec was a statement, but that will
    # be a syntax error if we try to put it in a Py3 file, even if it isn't
    # executed.  So hide it inside an evaluated string literal instead."
    eval(compile("""\
def exec_function(source, filename, global_map):
    exec compile(source, filename, "exec") in global_map
""",
    '<exec_function>', 'exec'
    ))


###
# Global variables
###
CTNAME = 'tests.test_exh.TestExHandle'
PENG_FNAME = sys.modules['putil.eng'].__file__

###
# Helper functions
###
sarg = lambda msg: 'Argument `{0}` is not valid'.format(msg)


###
# Test functions
###
def test_add():
    """ Test add function behavior """
    obj = putil.exh.addex
    # Exceptions
    AI(obj, 'extype', 5, 'Message')
    AI(obj, 'exmsg', RuntimeError, 2.0)
    AI(obj, 'condition', RuntimeError, 'Message', 1)
    AI(obj, 'edata', RuntimeError, 'Message', False, 5)
    inst1 = obj(IOError, 'First exception')
    inst2 = obj(TypeError, 'My exception')
    inst3 = obj(RuntimeError, 'Third exception')
    inst2(False)
    AE(inst2, TypeError, 'My exception', True)
    inst4 = obj(IOError, 'Invalid *[name]*')
    inst4(False)
    AE(inst4, IOError, 'Invalid arg', True, [{'field':'name', 'value':'arg'}])
    obj(TypeError, 'My exception', False)
    with pytest.raises(TypeError) as excinfo:
        obj(TypeError, 'My exception', True)
    assert GET_EXMSG(excinfo) == 'My exception'
    edata = [{'field':'name', 'value':'arg'}]
    obj(IOError, 'Invalid *[name]*', False, edata)
    with pytest.raises(IOError) as excinfo:
        obj(IOError, 'Invalid *[name]*', True, edata)
    assert GET_EXMSG(excinfo) == 'Invalid arg'

def test_add_ai():
    """ Test add_ai function behavior """
    obj = putil.exh.addai
    # Exceptions
    AI(obj, 'argname', 5)
    AI(obj, 'condition', 'name', 1)
    inst1 = obj('value')
    inst2 = obj('fname')
    inst3 = obj('kwarg')
    inst2(False)
    AE(inst2, RuntimeError, 'Argument `fname` is not valid', True)
    obj('arg', False)
    with pytest.raises(RuntimeError) as excinfo:
        obj('arg', True)
    assert GET_EXMSG(excinfo) == 'Argument `arg` is not valid'

def test_star_exh_obj():
    """ Test [get|set|del]_exh_obj() function behavior """
    AI(putil.exh.set_exh_obj, 'obj', obj=5)
    # set_exh_obj function
    exobj = putil.exh.ExHandle()
    putil.exh.set_exh_obj(exobj)
    assert id(putil.exh.get_exh_obj()) == id(exobj)
    # del_exh_obj function
    putil.exh.del_exh_obj()
    assert putil.exh.get_exh_obj() is None
    # Test that nothing happens if del_exh_obj is called when there
    # is no global object handler set
    putil.exh.del_exh_obj()
    new_exh_obj = putil.exh.get_or_create_exh_obj()
    assert id(new_exh_obj) != id(exobj)
    assert not new_exh_obj._full_cname
    # If there is a global exception handler the arguments passed
    # should not have any effect
    assert id(putil.exh.get_or_create_exh_obj(True)) == id(new_exh_obj)
    assert not new_exh_obj._full_cname
    # Test passed arguments are correctly assigned
    putil.exh.del_exh_obj()
    new_exh_obj = putil.exh.get_or_create_exh_obj(True)
    assert new_exh_obj._full_cname
    putil.exh.del_exh_obj()
    # get_or_create_exh_obj function
    obj = putil.exh.get_or_create_exh_obj
    AI(obj, 'full_cname', full_cname=5)
    AI(obj, 'exclude', exclude=5)
    AI(obj, 'callables_fname', callables_fname=True)
    args = {'callables_fname':'_not_a_file_'}
    msg = 'File _not_a_file_ could not be found'
    AE(obj, OSError, msg, **args)
    # exclude parameter
    pobj = putil.pinspect.Callables([PENG_FNAME])
    new_exh_obj = putil.exh.get_or_create_exh_obj(exclude=['putil.eng'])
    new_exh_obj._exclude = ['putil.eng']
    putil.exh.del_exh_obj()
    # callables_fname parameter
    with putil.misc.TmpFile() as fname:
        pobj.save(fname)
        new_exh_obj = putil.exh.get_or_create_exh_obj(callables_fname=fname)
        assert pobj == new_exh_obj._callables_obj
    putil.exh.del_exh_obj()


@pytest.mark.parametrize(
    'arg, ref', [
        (RuntimeError, 'RuntimeError'),
        (OSError, 'OSError')
    ]
)
def test_ex_type_str(arg, ref):
    """ test _ex_type_str() function behavior """
    assert putil.exh._ex_type_str(arg) == ref


class TestExHandle(object):
    """ Tests for ExHandle class """
    def test_init(self):
        """ Test constructor behavior """
        # Exceptions
        obj = putil.exh.ExHandle
        AI(obj, 'full_cname', full_cname=5)
        AI(obj, 'exclude', exclude=5)
        AI(obj, 'exclude', exclude=['p', 'a', 5, 'c'])
        AI(obj, 'callables_fname', callables_fname=True)
        arg = {'exclude':['sys', '_not_a_module_']}
        msg = 'Source for module _not_a_module_ could not be found'
        AE(obj, ValueError, msg, **arg)
        arg = {'callables_fname':'_not_an_existing_file_'}
        msg = 'File _not_an_existing_file_ could not be found'
        # Functionality
        exobj = putil.exh.ExHandle()
        assert not exobj._full_cname
        assert exobj._exclude is None
        assert exobj._exclude_list == []
        exobj = putil.exh.ExHandle(False, [])
        assert not exobj._full_cname
        assert exobj._exclude == []
        assert exobj._exclude_list == []
        exobj = putil.exh.ExHandle(True, None)
        assert exobj._full_cname
        assert exobj._exclude is None
        assert exobj._exclude_list == []
        exobj = putil.exh.ExHandle(exclude=['putil.exh'])
        assert exobj._exclude == ['putil.exh']
        assert exobj._exclude_list == [
            sys.modules['putil.exh'].__file__.replace('.pyc', '.py')
        ]
        pobj = putil.pinspect.Callables([PENG_FNAME])
        with putil.misc.TmpFile() as fname:
            pobj.save(fname)
            exobj = putil.exh.ExHandle(callables_fname=fname)
        assert pobj == exobj._callables_obj

    @pytest.mark.parametrize(
        'args, extype, exname', [
            ((5, RuntimeError, 'Message'), RuntimeError, sarg('exname')),
            (('34', RuntimeError, 'Message'), RuntimeError, sarg('exname')),
            (('exception', 5, 'Message'), RuntimeError, sarg('extype')),
            (('exception', RuntimeError, True), RuntimeError, sarg('exmsg'))
        ]
    )
    @pytest.mark.parametrize('full_cname', [True, False])
    def test_add_exception_exceptions(self, full_cname, args, extype, exname):
        """ Test add_exception() method exceptions """
        obj = putil.exh.ExHandle(full_cname).add_exception
        AE(obj, extype, exname, *args)
        # These should not raise an exception
        obj = putil.exh.ExHandle(full_cname)
        obj.add_exception(exname='name1', extype=RuntimeError, exmsg='desc1')
        obj.add_exception(exname='name2', extype=TypeError, exmsg='desc2')

    def test_add_exception(self):
        """ Test add_exception() function behavior """
        # pylint: disable=E0602,W0613
        # Functions that are going to be traced
        def func1():
            aobj('first_exception', TypeError, dmsg('first'))
            print("Hello")
        def prop_decorator(func):
            return func
        @putil.pcontracts.contract(text=str)
        @prop_decorator
        def func2(text):
            aobj('second_exception', ValueError, dmsg('second'))
            aobj('third_exception', OSError, dmsg('third'))
            print(text)
        class Class1(object):
            def __init__(self, exobj):
                self._value = None
                self._aobj = exobj.add_exception
            @property
            def value3(self):
                self._aobj('getter_exception', TypeError, pmsg('Get'))
                return self._value
            @value3.setter
            @putil.pcontracts.contract(value=int)
            def value3(self, value):
                self._aobj('setter_exception', TypeError, pmsg('Set'))
                self._value = value
            @value3.deleter
            def value3(self):
                self._aobj('deleter_exception', TypeError, pmsg('Delete'))
                print('Cannot delete attribute')
            def _get_value4_int(self):
                self._aobj('dummy_exception', OSError, 'Bypass exception')
                return self._value
            def _get_value4(self):
                return self._get_value4_int()
            value4 = property(_get_value4)
        def func7():
            aobj(emsg(7), TypeError, mmsg(7))
        def func8():
            aobj(emsg(8), TypeError, mmsg(8))
        def func9():
            aobj(emsg(9), TypeError, mmsg(9))
        def func10():
            aobj(emsg(10), TypeError, mmsg(10))
        def func11():
            aobj(emsg(11), TypeError, mmsg(11))
        def func12():
            aobj(emsg(12), TypeError, mmsg(12))
        def func13():
            aobj(emsg(13), TypeError, mmsg(13))
        def func14():
            aobj(emsg(14), TypeError, mmsg(14))
        # Add a function via exec
        iftxt = (
            "def func15(exobj):"
            "   aobj(emsg(15), TypeError, mmsg(15))"
        )
        gmap = locals()
        exec_function(iftxt, '<exec_function>', gmap)
        func15 = gmap['func15']
        # Helper functions
        dmsg = lambda msg: 'This is the {0} exception'.format(msg)
        emsg = lambda num: 'total_exception_{0}'.format(num)
        mmsg = lambda num: 'Total exception #{0}'.format(num)
        pmsg = lambda msg: '{0} function exception'.format(msg)
        root = CTNAME+'.test_add_exception'
        # Assertions
        exobj = putil.exh.ExHandle(
            full_cname=True, exclude=['_pytest', 'tests.test_exh']
        )
        assert exobj.exceptions_db == []
        # Generate all possible combinations of full_cname and exclude options
        #                       full_cname     exclude
        combinations = product([True, False], [None, ['_pytest', 'execnet']])
        for full_cname, exclude in combinations:
            exobj = putil.exh.ExHandle(full_cname=full_cname, exclude=exclude)
            aobj = exobj.add_exception
            # Trace functions
            dobj = Class1(exobj)
            dobj.value3 = 5
            print(dobj.value3)
            del dobj.value3
            cdb = exobj._ex_dict
            func1()
            func2("world")
            func7()
            func8()
            func9()
            func10()
            func11()
            func12()
            func13()
            func14()
            func15(exobj)
            exh_support_module_1.func16(exobj)
            # Define references
            cpath = lambda msg: 'Class1.value3({0})'.format(msg)
            fkeys = [
                'first_exception', 'second_exception', 'third_exception',
                'setter_exception', 'getter_exception', 'deleter_exception',
                emsg(7), emsg(8), emsg(9), emsg(10), emsg(11), emsg(12),
                emsg(13), emsg(14), emsg(15), emsg(16), 'dummy_exception'
            ]
            fnames = [
                'func1', 'func2', 'func2',
                cpath('setter'), cpath('getter'), cpath('deleter'),
                'func7', 'func8', 'func9', 'func10', 'func11', 'func12',
                'func13', 'func14', '', '/exh_support_module_1.func16',
                'Class1.value4(getter)',
            ]
            if full_cname and exclude:
                template = root+'/'+CTNAME+'.'
                func_name = 'test_add_exception.'
                fnames = (
                    [template+func_name+item for item in fnames[0:14]]+
                    [root, root+'/exh_support_module_1.func16']+
                    [template+func_name+item for item in fnames[-1]]
                )
            fexh = [TypeError, ValueError, OSError]+13*[TypeError]+[OSError]
            fdesc = [
                dmsg('first'), dmsg('second'), dmsg('third'),
                pmsg('Set'), pmsg('Get'), pmsg('Delete'),
                mmsg(7), mmsg(8), mmsg(9), mmsg(10), mmsg(11), mmsg(12),
                mmsg(13), mmsg(14), mmsg(15), mmsg(16), 'Bypass exception'
            ]
            # Test that exceptions have been added correctly to handler
            assert cdb
            cdb = exobj._flatten_ex_dict()
            for exname in cdb:
                erec = cdb[exname]
                iobj = zip(fnames, fexh, fdesc)
                match_dict = dict(
                    [(key, value) for key, value in zip(fkeys, iobj)]
                )
                for key, ttuple in match_dict.items():
                    if re.compile(r'\d+/'+key).match(exname):
                        break
                else:
                    raise RuntimeError('Callable not found')
                if full_cname and exclude:
                    assert erec['function'][0] == exobj.encode_call(ttuple[0])
                else:
                    if not full_cname:
                        assert erec['function'][0] is None
                    else:
                        assert re.compile(('.+/{0}'+ttuple[0]).format(root))
                assert erec['type'] == ttuple[1]
                assert erec['msg'] == ttuple[2]
            # Test that function IDs are unique
            mdict = collections.defaultdict(lambda: [])
            for exname in cdb:
                func_id = exname.split('/')[0]
                mdict[exname] = mdict[exname].append(func_id)
            exlist = []
            for exname, value in mdict.items():
                if value and match(exname) and (len(set(value)) != len(value)):
                    raise RuntimeError('Functions do not have unique IDs')
                exlist = exlist+value if value else exlist
            assert len(set(exlist)) == len(exlist)
            # Test that exec code gets correctly flagged
            frobj = sys._getframe(0)
            gcf = exobj._get_callable_full_name
            for item in [func15, None]:
                assert gcf(frobj, '<module>', item) == 'dynamic'
            # Test what happens when top of stack is reached
            exobj = putil.exh.ExHandle(full_cname=True, exclude=['_pytest'])
            obj = exobj.add_exception
            def func_f():
                obj(emsg('F'), TypeError, mmsg('F'))
            def mock_get_frame(num):
                if num < 4:
                    return frobj
                raise ValueError('Top of the stack')
            frobj = sys._getframe(0)
            cname = 'putil.exh.sys._getframe'
            with mock.patch(cname, side_effect=mock_get_frame):
                func_f()
            ecb = exobj._flatten_ex_dict()
            exname = list(ecb.keys())[0]
            erec = ecb[exname]
            ref = sorted(
                {
                    'function': [root+'/'+root+'/'+root+'/'+root],
                    'type':TypeError,
                    'msg':mmsg('F'),
                    'raised': [False]
                }.items()
            )
            assert re.compile(r'\d+/'+emsg('F')).match(exname)
            erec['function'] = [
                exobj.decode_call(call) for call in erec['function']
            ]
            assert sorted(erec.items()) == ref
        ###
        # Test property search
        ###
        exobj = putil.exh.ExHandle(
            full_cname=True, exclude=['_pytest', 'tests.test_exh']
        )
        cobj = exh_support_module_2.MyClass(exobj)
        cobj.value = 5
        cdb = cobj._exhobj._flatten_ex_dict()
        assert len(list(cdb.keys())) == 1
        key = list(cdb.keys())[0]
        item = cdb[key]
        assert cobj._exhobj.decode_call(item['function'][0]).endswith(
            'exh_support_module_2.MyClass.value(setter)'
        )
        assert item['msg'] == 'Illegal value'
        ###
        # Test exclude: test without exclusion and with exclusion,
        # the function name should be 'None'
        ###
        # Test with function that has a contract decorator
        putil.exh.set_exh_obj(
            putil.exh.ExHandle(full_cname=True, exclude=['_pytest'])
        )
        _ = putil.eng.peng(15, 3, False)
        cdb = putil.exh.get_exh_obj()._flatten_ex_dict()
        for item in cdb.values():
            assert item['function'][0]
        putil.exh.set_exh_obj(
            putil.exh.ExHandle(
                full_cname=True, exclude=['_pytest', 'putil.eng']
            )
        )
        _ = putil.eng.peng(15, 3, False)
        cdb = putil.exh.get_exh_obj()._flatten_ex_dict()
        for item in cdb.values():
            assert not item['function'][0]
        # Test with function that has an exception in body
        import tests.support.exh_support_module_1
        putil.exh.set_exh_obj(
            putil.exh.ExHandle(full_cname=True, exclude=['_pytest'])
        )
        tests.support.exh_support_module_1.simple_exception()
        cdb = putil.exh.get_exh_obj()._flatten_ex_dict()
        for item in cdb.values():
            assert item['function'][0]
        putil.exh.set_exh_obj(
            putil.exh.ExHandle(
                full_cname=True,
                exclude=['_pytest', 'tests.support.exh_support_module_1']
            )
        )
        tests.support.exh_support_module_1.simple_exception()
        cdb = putil.exh.get_exh_obj()._flatten_ex_dict()
        for item in cdb.values():
            assert not item['function'][0]

    def test_raise_exception_if_exceptions(self):
        """ Test raise_exception_if method exceptions """
        # pylint: disable=W0702
        # Helper functions
        def check_rec(mname, extype, exmsg):
            assert erec['function'].endswith('{0}'.format(mname))
            assert erec['type'] == extype
            assert erec['msg'] == exmsg
            assert erec['raised']
        def check_str(exobj, slist, llist):
            root = CTNAME+'.test_raise_exception_if_exceptions'
            ref = [
                '{0}/{0}.func_top/{0}.func_mid/{0}.func_base'.format(root),
                '{0}/{0}.func_base'.format(root),
                '{0}/{0}.func_mid/{0}.func_base'.format(root)
            ]
            pb = lambda x, nflip: x if nflip else (not x)
            alist = ['*' if item else '' for item in llist]
            cdb_int = exobj._flatten_ex_dict()
            entry = cdb_int[list(cdb_int.keys())[0]]
            entry = cdb_int[list(cdb_int.keys())[0]]
            assert (
                [exobj.decode_call(item) for item in entry['function']] == ref
            )
            assert entry['raised'] == llist
            stxt = str(exobj).split('\n')[3:]
            plist = [item.endswith(' [raised]') for item in stxt]
            assert all([pb(item, sitem) for item, sitem in zip(plist, slist)])
            db = exobj.exceptions_db
            exmsg = 'RuntimeError (Invalid condition)'
            for num in range(0, 3):
                assert db[num]['data'] == exmsg+alist[num]
            for num, fname in zip(range(0, 3), ref):
                assert db[num]['name'] == fname
        # Tests
        obj = putil.exh.ExHandle()
        def func3(cond1=False, cond2=False, cond3=False, cond4=False):
            exobj = putil.exh.ExHandle()
            items = (
                (RuntimeError, 'This is an exception'),
                (OSError, 'This is an exception with a *[fname]* field')
            )
            for num, (extype, exmsg) in enumerate(items):
                exobj.add_exception('my_exception'+str(num+1), extype, exmsg)
            exobj.raise_exception_if('my_exception1', cond1, edata=None)
            edata = {'field':'fname', 'value':'my_file.txt'}
            exobj.raise_exception_if('my_exception2', cond2, edata=edata)
            if cond3:
                exobj.raise_exception_if('my_exception3', False)
            edata = {'field':'not_a_field', 'value':'my_file.txt'}
            exobj.raise_exception_if('my_exception2', cond4, edata=edata)
            return exobj
        robj = obj.raise_exception_if
        AI(robj, 'exname', exname=5, condition=False)
        AI(robj, 'condition', exname='my_exception', condition=5)
        items = [
            354,
            {'field':'my_field'},
            {'field':3, 'value':5},
            {'value':5},
            [{'field':'my_field1', 'value':5}, {'field':'my_field'}],
            [{'field':'my_field1', 'value':5}, {'field':3, 'value':5}],
            [{'field':'my_field1', 'value':5}, {'value':5}]
        ]
        for item in items:
            AI(robj, 'edata', 'my_exception', False, item)
        AE(func3, RuntimeError, 'This is an exception', True, False)
        exmsg = 'This is an exception with a my_file.txt field'
        AE(func3, OSError, exmsg, cond2=True)
        exmsg = 'Exception name my_exception3 not found'
        AE(func3, ValueError, exmsg, cond3=True)
        exmsg = 'Field not_a_field not in exception message'
        AE(func3, RuntimeError, exmsg, cond4=True)
        # Test that edata=None works
        exobj = func3()
        cdb = exobj._flatten_ex_dict()
        if not cdb:
            pytest.fail('_ex_dict empty')
        for exname, erec in cdb.items():
            mname = 'test_exh.test_raise_exception.func3'
            if exname.endswith('/{0}.my_exception1'.format(mname)):
                check_rec(mname, RuntimeError, 'This is an exception')
            if exname.endswith('/{0}.my_exception2'.format(mname)):
                msg = 'This is an exception with a *[fname]* field'
                check_rec(mname, OSError, msg)
        exobj = putil.exh.ExHandle(full_cname=True)
        def func_base(exobj, cond):
            """ Test raised field """
            exobj.add_exception(
                'multi_path_exception', RuntimeError, 'Invalid condition'
            )
            exobj.raise_exception_if(
                exname='multi_path_exception', condition=cond
            )
        def func_mid(exobj, cond):
            """ Add multi-path to exception object """
            func_base(exobj, cond)
        def func_top(exobj, cond):
            """ Add another multi-path to exception object """
            func_mid(exobj, cond)
        # Mangle "natural" order to test __str__, which
        # sorts the function names
        func_top(exobj, False)
        func_base(exobj, False)
        func_mid(exobj, False)
        fpointers = [func_mid, func_top, func_base]
        slist = [[False, True, False], [False, True, True], [True, True, True]]
        llist = [[False, False, True], [True, False, True], [True, True, True]]
        for fpointer, sitem, litem in zip(fpointers, slist, llist):
            try:
                fpointer(exobj, True)
            except:
                pass
            check_str(exobj, sitem, litem)

    def test_exceptions_db(self):
        """ Test _exceptions_db property behavior """
        for full_cname in [True, False]:
            # Functions definitions
            def func4(exobj):
                exobj.add_exception(
                    'my_exception1', RuntimeError, 'This is exception #1'
                )
            def func5(exobj):
                exobj.add_exception(
                    'my_exception2',
                    ValueError,
                    'This is exception #2, *[result]*'
                )
                exobj.add_exception(
                    'my_exception3', TypeError, 'This is exception #3'
                )
            exobj = putil.exh.ExHandle(full_cname)
            func4(exobj)
            func5(exobj)
            # Actual tests
            # Test that property cannot be deleted
            AROPROP(exobj, 'exceptions_db')
            # Test contents
            tdata_in = exobj.exceptions_db
            if (not tdata_in) or (len(tdata_in) != 3):
                pytest.fail('Erroneous exceptions database')
            tdata_out = list()
            regtext1 = r'[\w|\W]+/'+CTNAME+'.test_exceptions_db.func4'
            regtext2 = r'[\w|\W]+/'+CTNAME+'.test_exceptions_db.func5'
            regtext3 = r'\d+/my_exception[2-3]'
            cname = CTNAME+'.test_exceptions_db'
            for erec in tdata_in:
                name = None
                if full_cname:
                    if re.compile(regtext1).match(erec['name']):
                        name = '{0}.func4'.format(cname)
                    elif re.compile(regtext2).match(erec['name']):
                        name = '{0}.func5'.format(cname)
                else:
                    if re.compile(r'\d+/my_exception1').match(erec['name']):
                        name = '{0}.func4'.format(cname)
                    elif re.compile(regtext3).match(erec['name']):
                        name = '{0}.func5'.format(cname)
                if not name:
                    pytest.fail('Exception not found')
                tdata_out.append({'name':name, 'data':erec['data']})
            ref = [
                    {
                        'name':'{0}.func4'.format(cname),
                        'data':'RuntimeError (This is exception #1)'
                    },
                    {
                        'name':'{0}.func5'.format(cname),
                        'data':'ValueError (This is exception #2, *[result]*)'
                    },
                    {
                        'name':'{0}.func5'.format(cname),
                        'data':'TypeError (This is exception #3)'
                    }
            ]
            assert CLDICTS(tdata_out, ref)

    def test_save_callables(self):
        """ Test save_callables method behavior """
        obj1 = putil.pinspect.Callables([PENG_FNAME])
        with putil.misc.TmpFile() as fname1:
            with putil.misc.TmpFile() as fname2:
                callables_fname1 = fname1
                callables_fname2 = fname2
                obj1.save(callables_fname1)
                obj2 = putil.exh.ExHandle(callables_fname=callables_fname1)
                obj2.save_callables(callables_fname2)
                obj3 = putil.pinspect.Callables()
                obj3.load(callables_fname2)
        assert obj1 == obj3

    def test_save_callables_exceptions(self):
        """ Test save_callables method exceptions """
        obj = putil.exh.ExHandle()
        AI(obj.save_callables, 'callables_fname', True)

    def test_callables_db(self):
        """ Test callables_db property behavior """
        # Function definitions
        def func6(exobj):
            exobj.add_exception(
                'my_exception', RuntimeError, 'This is an exception'
            )
            return exobj
        # Actual tests
        exobj = func6(putil.exh.ExHandle())
        # Actual contents of what is returned should be checked
        # in pinspect module
        assert exobj.callables_db is not None
        # Test that property cannot be deleted
        AROPROP(exobj, 'callables_db')

    def test_callables_separator(self):
        """ Test callables_separator property behavior """
        exobj = putil.exh.ExHandle()
        # Actual contents of what is returned should be checked in
        # pinspect module
        assert exobj.callables_separator == '/'
        # Test that property cannot be deleted
        AROPROP(exobj, 'callables_separator')

    def test_str(self):
        """ Test __str__ method behavior """
        for full_cname in [True, False]:
            # Functions definition
            def func7(exobj):
                exobj.add_exception(
                    'my_exception7', RuntimeError, 'This is exception #7'
                )
                exobj.raise_exception_if('my_exception7', False)
            def func8(exobj):
                exobj.add_exception(
                    'my_exception8',
                    ValueError,
                    'This is exception #8, *[fname]*'
                )
                exobj.add_exception(
                    'my_exception9', TypeError, 'This is exception #9'
                )
            exobj = putil.exh.ExHandle(full_cname)
            func7(exobj)
            func8(exobj)
            # Actual tests
            str_in = str(exobj).split('\n\n')
            str_out = list()
            cname = 'test_exh.TestExHandle.test_str'
            for str_element in str_in:
                str_list = str_element.split('\n')
                if str_list[0].endswith('/my_exception7'):
                    str_list[0] = (
                        'Name    : {0}.func7/my_exception7'.format(cname)
                    )
                elif str_list[0].endswith('/my_exception8'):
                    str_list[0] = (
                        'Name    : {0}.func8/my_exception8'.format(cname)
                    )
                elif str_list[0].endswith('/my_exception9'):
                    str_list[0] = (
                        'Name    : {0}.func8/my_exception9'.format(cname)
                    )
                if str_list[3].endswith('{0}.func7'.format(cname)):
                    str_list[3] = 'Function: {0}'.format(
                        '{0}.func7'.format(cname) if full_cname else 'None'
                    )
                elif str_list[3].endswith('{0}.func8'.format(cname)):
                    str_list[3] = 'Function: {0}'.format(
                        '{0}.func8'.format(cname) if full_cname else 'None'
                    )
                str_out.append('\n'.join(str_list))
            #
            str_check = list()
            str_check.append(
                'Name    : '+cname+'.func7/my_exception7\n'
                'Type    : RuntimeError\n'
                'Message : This is exception #7\n'
                'Function: {name}'.format(
                    name='{0}.func7'.format(cname) if full_cname else 'None'
                )
            )
            str_check.append(
                'Name    : '+cname+'.func8/my_exception8\n'
                'Type    : ValueError\n'
                'Message : This is exception #8, *[fname]*\n'
                'Function: {name}'.format(
                    name='{0}.func8'.format(cname) if full_cname else 'None'
                )
            )
            str_check.append(
                'Name    : '+cname+'.func8/my_exception9\n'
                'Type    : TypeError\n'
                'Message : This is exception #9\n'
                'Function: {name}'.format(
                    name='{0}.func8'.format(cname) if full_cname else 'None'
                )
            )
            if sorted(str_out) != sorted(str_check):
                print('\n\nActual output:\n{text}'.format(
                        text='\n'.join(sorted(str_out))
                    )
                )
                print('\n\nReference output\n{text}'.format(
                        text='\n'.join(sorted(str_check))
                    )
                )
            assert sorted(str_out) == sorted(str_check)

    def test_copy(self):
        """ Test __copy__ method behavior """
        # Functions definition
        def funca(exobj):
            exobj.add_exception(
                'my_exceptionA', RuntimeError, 'This is exception #A'
            )
        def funcb(exobj):
            exobj.add_exception(
                'my_exceptionB', ValueError, 'This is exception #B'
            )
            exobj.add_exception(
                'my_exceptionC', TypeError, 'This is exception #C'
            )
        class Clsc(object):
            def __init__(self, exobj):
                self._exobj = exobj
                self._value = None
            def _set_value(self, value):
                self._exobj.add_exception(
                    'my_exceptionD', OSError, 'This is exception #D'
                )
                self._value = value
            value = property(None, _set_value, None, doc='Value property')
        source_obj = putil.exh.ExHandle(full_cname=True)
        funca(source_obj)
        funcb(source_obj)
        obj = Clsc(source_obj)
        obj.value = 5
        # Actual tests
        dest_obj = copy.copy(source_obj)
        assert source_obj._ex_dict == dest_obj._ex_dict
        assert id(source_obj._ex_dict) != id(dest_obj._ex_dict)
        assert source_obj._callables_obj == dest_obj._callables_obj
        assert id(source_obj._callables_obj) != id(dest_obj._callables_obj)
        assert source_obj._clut == dest_obj._clut
        assert id(source_obj._clut) != id(dest_obj._clut)
        assert source_obj._full_cname == dest_obj._full_cname
        assert CLDICTS(source_obj.exceptions_db, dest_obj.exceptions_db)

    def test_multiple_paths_to_same_exception(self):
        """
        Test that different paths to a single exception definition do not
        overwrite each other
        """
        def exdef(obj):
            obj.add_exception(
                'my_exception', RuntimeError, 'This is the exception'
            )
        def funca(obj):
            exdef(obj)
        def funcb(obj):
            exdef(obj)
        exobj = putil.exh.ExHandle(full_cname=True)
        funca(exobj)
        funcb(exobj)
        exdb = sorted(exobj.exceptions_db, key=lambda item: item['name'])
        assert len(exdb) == 2
        assert exdb[0]['data'] == 'RuntimeError (This is the exception)'
        assert exdb[1]['data'] == 'RuntimeError (This is the exception)'
        cname = CTNAME+'.test_multiple_paths_to_same_exception'
        assert exdb[0]['name'].endswith(
            '{0}/{0}.funca/{0}.exdef'.format(cname)
        )
        assert exdb[1]['name'].endswith(
            '{0}/{0}.funcb/{0}.exdef'.format(cname)
        )
        str_in = putil.misc.flatten_list(
            [item.split('\n') for item in str(exobj).split('\n\n')]
        )
        fstring = cname+'/'+cname+'.func{0}/'+cname+'.exdef'
        assert str_in[0].endswith('/my_exception')
        assert str_in[1] == 'Type    : RuntimeError'
        assert str_in[2] == 'Message : This is the exception'
        assert str_in[3].startswith('Function: ')
        assert (
            str_in[3].endswith(fstring.format('a')) or
            str_in[3].endswith(fstring.format('b'))
        )
        assert str_in[4].startswith(' '*10)
        assert str_in[4].endswith(
            fstring.format(
                'a' if str_in[3].endswith(fstring.format('b')) else 'b'
            )
        )

    def test_add(self):
        """ Test __add__ method behavior """
        scomp = lambda a, b: bool(sorted(a) == sorted(b))
        def check_add(sobj):
            ex_dict_ref = {
                'call1':{'a':5, 'b':6},
                'call2':{'a':7, 'b':8},
                'call3':{'a':10, 'b':100},
                'call4':{'a':200, 'b':300}
            }
            c_ref = {'id1':5, 'ssid1':10, 'id2':3, 'ssid2':1}
            rcdb_ref = {'rc1':5, 'rc2':7, 'rc3':0, 'rc4':-1}
            mod_ref = {
                'key1':'alpha', 'key2':'beta', 'key3':'pi', 'key4':'gamma'
            }
            fnames_ref = {'hello':0, 'world':1}
            mlist_ref = ['this', 'is', 'a', 'test']
            cls_ref = ['once', 'upon', 'a', 'time']
            assert scomp(sobj._ex_dict, c_ref)
            cobj = sobj._callables_obj
            assert scomp(cobj._callables_db, ex_dict_ref)
            assert scomp(cobj._reverse_callables_db, rcdb_ref)
            assert scomp(cobj._modules_dict, mod_ref)
            assert scomp(cobj._fnames, fnames_ref)
            assert scomp(cobj._module_names, mlist_ref)
            assert scomp(cobj._class_names, cls_ref)
        def comp_objs(obj):
            ref = {
                CTNAME+'.test_add': '0',
                CTNAME+'.test_add.func1': '1',
                CTNAME+'.test_add.func2': '3',
                CTNAME+'.test_add.func3': '2'
            }
            assert obj._clut == ref
            nref = [
                'copy_exception_1',
                'copy_exception_2',
                'copy_exception_3',
                'contract:putil.eng.peng.frac_length_0',
                'contract:putil.eng.peng.number_0',
                'contract:putil.eng.peng.rjust_0',
            ]
            alist = [
                item.split(obj._callables_separator)[1]
                for item in obj._flatten_ex_dict()
            ]
            assert sorted(alist) == sorted(nref)
            for key, value in obj._flatten_ex_dict().items():
                name = key.split(obj._callables_separator)[1]
                if name == 'copy_exception_1':
                    assert value['function'] == ['0/1']
                elif name == 'copy_exception_2':
                    assert value['function'] == ['0/3']
                elif name == 'copy_exception_3':
                    assert value['function'] == ['0/2']
                else:
                    assert value['function'] == [None]
        # pylint: disable=W0104
        obj1 = putil.exh.ExHandle(_copy=True)
        obj1._ex_dict = {'id1':5, 'ssid1':10}
        obj1._callables_obj = putil.pinspect.Callables()
        obj1._callables_obj._callables_db = {
            'call1':{'a':5, 'b':6},
            'call2':{'a':7, 'b':8}
        }
        obj1._callables_obj._reverse_callables_db = {'rc1':5, 'rc2':7}
        obj1._callables_obj._modules_dict = {'key1':'alpha', 'key2':'beta'}
        obj1._callables_obj._fnames = {'hello':0}
        obj1._callables_obj._module_names = ['this', 'is']
        obj1._callables_obj._class_names = ['once', 'upon']
        #
        obj2 = putil.exh.ExHandle(_copy=True)
        obj2._ex_dict = {'id2':3, 'ssid2':1}
        obj2._callables_obj = putil.pinspect.Callables()
        obj2._callables_obj._callables_db = {
            'call3':{'a':10, 'b':100},
            'call4':{'a':200, 'b':300}
        }
        obj2._callables_obj._reverse_callables_db = {'rc3':0, 'rc4':-1}
        obj2._callables_obj._modules_dict = {'key3':'pi', 'key4':'gamma'}
        obj2._callables_obj._fnames = {'world':0}
        obj2._callables_obj._module_names = ['a', 'test']
        obj2._callables_obj._class_names = ['a', 'time']
        #
        check_add(obj1+obj2)
        obj1 += obj2
        check_add(obj1)
        # Incompatible types
        with pytest.raises(TypeError) as excinfo:
            obj1+5
        msg = 'Unsupported operand type(s) for +: putil.exh.ExHandle and int'
        assert GET_EXMSG(excinfo) == msg
        # Incompatible types
        with pytest.raises(TypeError) as excinfo:
            obj1 += 5
        assert GET_EXMSG(excinfo) == msg
        #
        obj2._full_cname = True
        with pytest.raises(RuntimeError) as excinfo:
            obj1+obj2
        msg = 'Incompatible exception handlers'
        assert GET_EXMSG(excinfo) == msg
        with pytest.raises(RuntimeError) as excinfo:
            obj1 += obj2
        assert GET_EXMSG(excinfo) == msg
        obj2._full_cname = False
        obj2._exclude = ['_pytest']
        with pytest.raises(RuntimeError) as excinfo:
            obj1+obj2
        assert GET_EXMSG(excinfo) == msg
        with pytest.raises(RuntimeError) as excinfo:
            obj1 += obj2
        assert GET_EXMSG(excinfo) == msg
        obj2._exclude = None
        # Test re-mapping of callables look-up table
        obj1 = putil.exh.ExHandle(full_cname=True, exclude=['putil.eng'])
        obj2 = putil.exh.ExHandle(full_cname=True, exclude=['putil.eng'])
        def func1(exhobj):
            exhobj.add_exception(
                'copy_exception_1', TypeError, 'Copy exception #1'
            )
        def func2(exhobj):
            exhobj.add_exception(
                'copy_exception_2', RuntimeError, 'Copy exception #2'
            )
        def func3(exhobj):
            exhobj.add_exception(
                'copy_exception_3', ValueError, 'Copy exception #3'
            )
            putil.exh.del_exh_obj()
            putil.exh.get_or_create_exh_obj(
                full_cname=True, exclude=['putil.eng']
            )
            putil.eng.peng(1, 3, False)
            exhobj += putil.exh.get_exh_obj()
            putil.exh.del_exh_obj()
        # Test __add__
        func1(obj1)
        func3(obj1)
        func1(obj2)
        func2(obj2)
        func3(obj2)
        obj1_ref = copy.copy(obj1)
        obj2_ref = copy.copy(obj2)
        assert obj1_ref == obj1
        assert obj2_ref == obj2
        obj3 = obj1+obj2
        assert obj1_ref == obj1
        assert obj2_ref == obj2
        comp_objs(obj3)
        # Test __iadd__
        obj1 = putil.exh.ExHandle(full_cname=True, exclude=['putil.eng'])
        obj2 = putil.exh.ExHandle(full_cname=True, exclude=['putil.eng'])
        func1(obj1)
        func3(obj1)
        func1(obj2)
        func2(obj2)
        func3(obj2)
        obj2_ref = copy.copy(obj2)
        assert obj2_ref == obj2
        obj1 += obj2
        assert obj2_ref == obj2
        comp_objs(obj1)

    def test_eq(self):
        """ Test __eq__ method behavior """
        putil.exh.get_or_create_exh_obj()
        # Trace some exceptions
        putil.eng.peng(100, 3, True)
        obj1 = putil.exh.get_exh_obj()
        obj2 = copy.copy(obj1)
        assert obj1 == obj2
        assert obj1 != 5

    def test_nonzero(self):
        """ Test __nonzero__ method behavior """
        exhobj = putil.exh.ExHandle()
        assert not exhobj
        def my_func(exhobj):
            exhobj.add_exception('test', RuntimeError, 'Message')
        my_func(exhobj)
        assert exhobj
