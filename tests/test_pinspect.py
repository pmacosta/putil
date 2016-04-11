# test_pinspect.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0611,F0401,R0201,R0903,R0913,R0915,W0104,W0212,W0232,W0612,W0613,W0621

# Standard library imports
from __future__ import print_function
from functools import partial
import copy
import os
import sys
import time
import types
# PyPI imports
import pytest
if sys.hexversion == 0x03000000:
    from putil.compat3 import _readlines
# Putil imports
import putil.pinspect
from putil.test import AE, AI, CS, GET_EXMSG, RE


###
# Helper functions
###
modfile = lambda x: sys.modules[x].__file__


###
# Tests for module functions
###
def test_private_props():
    """ Test private_props function behavior """
    obj = putil.pinspect.Callables()
    assert sorted(list(putil.pinspect.private_props(obj))) == [
        '_callables_db',
        '_class_names',
        '_fnames',
        '_module_names',
        '_modules_dict',
        '_reverse_callables_db'
    ]


if sys.hexversion == 0x03000000:
    def test_readlines():
        """ Test _readlines function behavior """
        def mopen1(fname, mode):
            raise RuntimeError('Mock mopen1 function')
        def mopen2(fname, mode):
            text = chr(40960) + 'abcd' + chr(1972)
            # Next line raises UnicodeDecodeError
            b'\x80abc'.decode("utf-8", "strict")
        class MockOpenCls(object):
            def __init__(self, fname, mode, encoding):
                pass
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_value, exc_tb):
                if exc_type is not None:
                    return False
            def readlines(self):
                return 'MockOpenCls'
        pkg_dir = os.path.abspath(os.path.dirname(__file__))
        fname = os.path.join(pkg_dir, 'test_misc.py')
        # This should not trigger an exception (functionality checked
        # by other unit tests)
        _readlines(fname)
        # Trigger unrelated exception exception
        obj = _readlines
        with pytest.raises(RuntimeError) as excinfo:
            _readlines(fname, mopen1)
        assert GET_EXMSG(excinfo) == 'Mock mopen1 function'
        # Trigger UnicodeDecodeError exception
        assert _readlines(fname, mopen2, MockOpenCls) == 'MockOpenCls'


def test_object_is_module():
    """ Test object_is_module() function """
    assert not putil.pinspect.is_object_module(5)
    assert putil.pinspect.is_object_module(sys.modules['putil.pinspect'])


def test_get_module_name():
    """ Test get_module_name() function """
    obj = putil.pinspect.get_module_name
    AI(obj, 'module_obj', module_obj=5)
    mock_module_obj = types.ModuleType('mock_module_obj', 'Mock module')
    exmsg = (
        'Module object `mock_module_obj` could not be found in loaded modules'
    )
    AE(obj, RE, exmsg, module_obj=mock_module_obj)
    ref = 'putil.pinspect'
    assert putil.pinspect.get_module_name(sys.modules[ref]) == ref
    assert putil.pinspect.get_module_name(sys.modules['putil']) == 'putil'


def test_get_module_name_from_fname():
    """ Test _get_module_name_from_fname() function """
    obj = putil.pinspect._get_module_name_from_fname
    AE(obj, RE, 'Module could not be found', fname='_not_a_module')
    assert obj(modfile('putil.pinspect')) == 'putil.pinspect'


def test_is_special_method():
    """ Test is_special_method() function """
    assert not putil.pinspect.is_special_method('func_name')
    assert not putil.pinspect.is_special_method('_func_name_')
    assert putil.pinspect.is_special_method('__func_name__')


###
# Test for classes
###
class TestCallables(object):
    """ Test for Callables """
    def test_check_intersection(self):
        """ Test _check_intersection method behavior """
        obj1 = putil.pinspect.Callables()
        obj1._callables_db = {'call1':1, 'call2':2}
        obj2 = putil.pinspect.Callables()
        obj2._callables_db = {'call1':1, 'call2':'a'}
        exmsg = 'Conflicting information between objects'
        obj = obj1._check_intersection
        AE(obj, RE, exmsg, other=obj2)
        obj1._callables_db = {'call1':1, 'call2':['a', 'c']}
        obj2._callables_db = {'call1':1, 'call2':['a', 'b']}
        AE(obj, RE, exmsg, other=obj2)
        obj1._callables_db = {'call1':1, 'call2':{'a':'b'}}
        obj2._callables_db = {'call1':1, 'call2':{'a':'c'}}
        AE(obj, RE, exmsg, other=obj2)
        obj1._callables_db = {'call1':1, 'call2':'a'}
        obj2._callables_db = {'call1':1, 'call2':'c'}
        AE(obj, RE, exmsg, other=obj2)
        obj1._callables_db = {'call1':1, 'call2':'a'}
        obj2._callables_db = {'call1':1, 'call2':'a'}
        assert obj1._check_intersection(obj2) is None

    def test_init_exceptions(self):
        """ Test constructor exceptions """
        obj = putil.pinspect.Callables
        for item in [5, [5]]:
            AI(obj, 'fnames', fnames=item)
        exmsg = 'File _not_a_file_ could not be found'
        AE(obj, OSError, exmsg, fnames=['_not_a_file_'])

    def test_add(self):
        """ Test __add__ __radd__ method behavior """
        obj1 = putil.pinspect.Callables()
        obj1._callables_db = {'call1':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}}
        obj1._reverse_callables_db = {'rc1':'5', 'rc2':'7'}
        obj1._modules_dict = {
            'key1':{'entry':'alpha'}, 'key2':{'entry':'beta'}
        }
        obj1._fnames = {'hello':0}
        obj1._module_names = ['this', 'is']
        obj1._class_names = ['once', 'upon']
        #
        obj2 = putil.pinspect.Callables()
        obj2._callables_db = {
            'call3':{'a':10, 'b':100}, 'call4':{'a':200, 'b':300}
        }
        obj2._reverse_callables_db = {'rc3':'0', 'rc4':'1'}
        obj2._modules_dict = {'key3':{'entry':'pi'}, 'key4':{'entry':'gamma'}}
        obj2._fnames = {'world':1}
        obj2._module_names = ['a', 'test']
        obj2._class_names = ['a', 'time']
        #
        obj1._callables_db = {'call3':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}}
        with pytest.raises(RuntimeError) as excinfo:
            obj1+obj2
        assert GET_EXMSG(excinfo) == 'Conflicting information between objects'
        obj1._callables_db = {'call1':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}}
        #
        obj2._reverse_callables_db = {'rc3':'5', 'rc2':'-1'}
        with pytest.raises(RuntimeError) as excinfo:
            obj1+obj2
        assert GET_EXMSG(excinfo) == 'Conflicting information between objects'
        obj2._reverse_callables_db = {'rc3':'0', 'rc4':'-1'}
        #
        obj2._modules_dict = {'key1':{'entry':'pi'}, 'key4':{'entry':'gamma'}}
        with pytest.raises(RuntimeError) as excinfo:
            obj1+obj2
        assert GET_EXMSG(excinfo) == 'Conflicting information between objects'
        obj2._modules_dict = {'key3':{'entry':'pi'}, 'key4':{'entry':'gamma'}}
        # Test when intersection is the same
        obj2._modules_dict = {
            'key1':{'entry':'alpha'}, 'key4':{'entry':'gamma'}
        }
        obj1+obj2
        obj2._modules_dict = {'key3':{'entry':'pi'}, 'key4':{'entry':'gamma'}}
        #
        sobj = obj1+obj2
        scomp = lambda x, y: sorted(x) == sorted(y)
        ref = {
            'call1':{'a':5, 'b':6},
            'call2':{'a':7, 'b':8},
            'call3':{'a':10, 'b':100},
            'call4':{'a':200, 'b':300}
        }
        assert scomp(sobj._callables_db, ref)
        ref = {'rc1':'5', 'rc2':'7', 'rc3':'0', 'rc4':'-1'}
        assert scomp(sobj._reverse_callables_db, ref)
        ref = {
            'key1':{'entry':'alpha'},
            'key2':{'entry':'beta'},
            'key3':{'entry':'pi'},
            'key4':{'entry':'gamma'}
        }
        assert scomp(sobj._modules_dict, ref)
        assert scomp(sobj._fnames, {'hello':0, 'world':1})
        assert scomp(sobj._module_names, ['this', 'is', 'a', 'test'])
        assert scomp(sobj._class_names, ['once', 'upon', 'a', 'time'])
        #
        obj1 += obj2
        ref = {
            'call1':{'a':5, 'b':6},
            'call2':{'a':7, 'b':8},
            'call3':{'a':10, 'b':100},
            'call4':{'a':200, 'b':300}
        }
        assert scomp(obj1._callables_db, ref)
        ref = {'rc1':'5', 'rc2':'7', 'rc3':'0', 'rc4':'-1'}
        assert scomp(obj1._reverse_callables_db, ref)
        ref = {
            'key1':{'entry':'alpha'},
            'key2':{'entry':'beta'},
            'key3':{'entry':'pi'},
            'key4':{'entry':'gamma'}
        }
        assert scomp(obj1._modules_dict, ref)
        assert scomp(obj1._fnames, {'hello':0, 'world':1})
        assert scomp(obj1._module_names, ['this', 'is', 'a', 'test'])
        assert scomp(obj1._class_names, ['once', 'upon', 'a', 'time'])

    def test_copy(self):
        """ Test __copy__ method behavior """
        sobj = putil.pinspect.Callables()
        import tests.support.pinspect_support_module_1
        sobj.trace([modfile('tests.support.pinspect_support_module_1')])
        dobj = copy.copy(sobj)
        assert sobj._module_names == dobj._module_names
        assert id(sobj._module_names) != id(dobj._module_names)
        assert sobj._class_names == dobj._class_names
        assert id(sobj._class_names) != id(dobj._class_names)
        assert sobj._callables_db == dobj._callables_db
        assert id(sobj._callables_db) != id(dobj._callables_db)
        assert sobj._reverse_callables_db == dobj._reverse_callables_db
        assert id(sobj._reverse_callables_db) != id(dobj._reverse_callables_db)

    def test_eq(self):
        """ Test __eq__ method behavior """
        obj1 = putil.pinspect.Callables()
        obj2 = putil.pinspect.Callables()
        obj3 = putil.pinspect.Callables()
        import tests.support.pinspect_support_module_1
        import tests.support.pinspect_support_module_2
        mname = 'tests.support.pinspect_support_module_1'
        obj1.trace([modfile(mname)])
        obj2.trace([modfile(mname)])
        obj3.trace([modfile('putil.test')])
        assert (obj1 == obj2) and (obj1 != obj3)
        assert obj1 != 5

    def test_repr(self):
        """ Test __repr__ method behavior """
        get_name = lambda x: modfile(x).replace('.pyc', '.py')
        import tests.support.exdoc_support_module_1
        file1 = get_name('tests.support.exdoc_support_module_1')
        file2 = get_name('tests.support.exdoc_support_module_2')
        xobj = putil.pinspect.Callables([file2])
        xobj.trace([file1])
        ref = "putil.pinspect.Callables([{0}, {1}])".format(
            repr(file1), repr(file2)
        )
        assert repr(xobj) == ref

    def test_str_empty(self):
        """ Test __str__ magic method when object is empty """
        obj = putil.pinspect.Callables()
        assert str(obj) == ''

    def test_refresh(self):
        """ Test refresh method behavior """
        ref = modfile('putil.test')
        src = os.path.join(os.path.dirname(ref), 'pit.py')
        with open(src, 'w') as fobj:
            fobj.write(
                'class MyClass(object):\n'
                '    pass\n'
                'def func1():\n'
                '    pass\n'
            )
        import putil.pit
        obj = putil.pinspect.Callables([ref, src])
        tmod = obj._fnames[src]
        obj.trace([src])
        assert obj._fnames[src] == tmod
        rtext = (
            'Modules:\n'
            '   putil.pit\n'
            '   putil.test\n'
            'Classes:\n'
            '   putil.pit.MyClass\n'
            'putil.pit.MyClass: class (1-2)\n'
            'putil.pit.func1: func (3-4)\n'
            'putil.test._get_fargs: func (32-67)\n'
            'putil.test._pcolor: func (68-82)\n'
            'putil.test.assert_arg_invalid: func (83-115)\n'
            'putil.test.assert_exception: func (116-199)\n'
            'putil.test._invalid_frame: func (200-206)\n'
            'putil.test.assert_prop: func (207-246)\n'
            'putil.test.assert_ro_prop: func (247-266)\n'
            'putil.test.compare_strings: func (267-356)\n'
            'putil.test.compare_strings.colorize_lines: func (296-307)\n'
            'putil.test.compare_strings.print_non_diff: func (308-312)\n'
            'putil.test.compare_strings.print_diff: func (313-321)\n'
            'putil.test.comp_list_of_dicts: func (357-371)\n'
            'putil.test.exception_type_str: func (372-389)\n'
            'putil.test.get_exmsg: func (390-404)'
        )
        CS(str(obj), rtext)
        ftime = int(os.path.getmtime(src))
        while int(time.time()) <= ftime:
            time.sleep(0.1)
        os.remove(src)
        content = 'def my_func():\n    pass'
        with open(src, 'w') as fobj:
            fobj.write(content)
        obj.refresh()
        assert obj._fnames[src] != tmod
        rtext = (
            'Modules:\n'
            '   putil.pit\n'
            '   putil.test\n'
            'putil.pit.my_func: func (1-2)\n'
            'putil.test._get_fargs: func (32-67)\n'
            'putil.test._pcolor: func (68-82)\n'
            'putil.test.assert_arg_invalid: func (83-115)\n'
            'putil.test.assert_exception: func (116-199)\n'
            'putil.test._invalid_frame: func (200-206)\n'
            'putil.test.assert_prop: func (207-246)\n'
            'putil.test.assert_ro_prop: func (247-266)\n'
            'putil.test.compare_strings: func (267-356)\n'
            'putil.test.compare_strings.colorize_lines: func (296-307)\n'
            'putil.test.compare_strings.print_non_diff: func (308-312)\n'
            'putil.test.compare_strings.print_diff: func (313-321)\n'
            'putil.test.comp_list_of_dicts: func (357-371)\n'
            'putil.test.exception_type_str: func (372-389)\n'
            'putil.test.get_exmsg: func (390-404)'
        )
        CS(str(obj), rtext)
        ## Test malformed JSON file
        obj = putil.pinspect.Callables()
        json_src = os.path.join(os.path.dirname(ref), 'pit.json')
        json_txt = (
            '{{\n'
            '    "_callables_db": {{\n'
            '        "putil.pit.my_func": {{\n'
            '            "code_id": [\n'
            '                "{pyfile}",\n'
            '                1\n'
            '            ],\n'
            '            "last_lineno": 2,\n'
            '            "name": "putil.pit.my_func",\n'
            '            "type": "func"\n'
            '        }}\n'
            '    }},\n'
            '    "_class_names": [],\n'
            '    "_fnames": {{\n'
            '        "{pyfile}": {{\n'
            '            "classes": [],\n'
            '            "date": 1,\n'
            '            "name": "putil.pit"\n'
            '        }}\n'
            '    }},\n'
            '    "_module_names": [\n'
            '        "putil.pit"\n'
            '    ],\n'
            '    "_modules_dict": {{\n'
            '        "putil.pit": [\n'
            '            {{\n'
            '                "code_id": [\n'
            '                    "{pyfile}",\n'
            '                    1\n'
            '                ],\n'
            '                "last_lineno": 2,\n'
            '                "name": "putil.pit.my_func",\n'
            '                "type": "func"\n'
            '            }}\n'
            '        ]\n'
            '    }},\n'
            '    "_reverse_callables_db": {{\n'
            '        "(\'{pyfile}\', 1)": "putil.pit.my_func",\n'
            '        "(\'{pyfile}\', 10)": "putil.pit.my_func"\n'
            '    }}\n'
            '}}\n'
        )
        with open(json_src, 'w') as fobj:
            fobj.write(json_txt.format(pyfile=src.replace('\\', '/')))
        obj.load(json_src)
        obj.refresh()
        os.remove(json_src)
        os.remove(src)

    def test_load_save(self):
        """ Test load and save methods behavior """
        # pylint: disable=R0914
        import putil.pcsv
        import tests.support.exdoc_support_module_1
        # Empty object
        obj1 = putil.pinspect.Callables()
        with putil.misc.TmpFile() as fname:
            obj1.save(fname)
            obj2 = putil.pinspect.Callables()
            obj2.load(fname)
        assert obj1 == obj2
        # 1 module trace
        mname = 'putil.pcsv.csv_file'
        cname = '{0}.CsvFile'.format(mname)
        obj1 = putil.pinspect.Callables([modfile(mname)])
        with putil.misc.TmpFile() as fname:
            obj1.save(fname)
            obj2 = putil.pinspect.Callables()
            assert not bool(obj2)
            obj2.load(fname)
        assert obj1 == obj2
        # Test merging of traced and file-based module information
        mname1 = 'putil.pcsv.csv_file'
        obj1 = putil.pinspect.Callables([modfile(mname1)])
        mname2 = 'tests.support.exdoc_support_module_1'
        obj2 = putil.pinspect.Callables([modfile(mname2)])
        with putil.misc.TmpFile() as fname1:
            with putil.misc.TmpFile() as fname2:
                obj1.save(fname1)
                obj2.save(fname2)
                obj3 = putil.pinspect.Callables(
                    [modfile(mname1), modfile(mname2)]
                )
                obj4 = putil.pinspect.Callables()
                obj4.load(fname2)
                obj4.load(fname1)
        assert obj3 == obj4

    def test_load_exceptions(self):
        """ Test load method exceptions """
        obj = putil.pinspect.Callables()
        for item in [True, 5]:
            AI(obj.load, 'callables_fname', callables_fname=item)
        exmsg = 'File _not_a_file_ could not be found'
        AE(obj.load, OSError, exmsg, callables_fname='_not_a_file_')

    def test_save_exceptions(self):
        """ Test save method exceptions """
        obj = putil.pinspect.Callables()
        for item in [True, 5]:
            AI(obj.save, 'callables_fname', callables_fname=item)

    def test_trace(self):
        """ Test trace method behavior """
        import putil.pcsv
        mname = 'putil.pcsv.csv_file'
        cname = '{0}.CsvFile'.format(mname)
        xobj = putil.pinspect.Callables([modfile(mname)])
        ref = []
        ref.append('Modules:')
        ref.append('   {0}'.format(mname))
        ref.append('Classes:')
        ref.append('   {0}'.format(cname))
        ref.append('{0}._homogenize_data_filter: func (44-66)'.format(mname))
        ref.append('{0}._tofloat: func (67-82)'.format(mname))
        ref.append('{0}: class (83-958)'.format(cname))
        ref.append('{0}.__init__: meth (134-207)'.format(cname))
        ref.append('{0}.__eq__: meth (208-242)'.format(cname))
        ref.append('{0}.__repr__: meth (243-276)'.format(cname))
        ref.append('{0}.__str__: meth (277-321)'.format(cname))
        ref.append('{0}._format_rfilter: meth (322-338)'.format(cname))
        ref.append('{0}._gen_col_index: meth (339-351)'.format(cname))
        ref.append('{0}._get_cfilter: meth (352-354)'.format(cname))
        ref.append('{0}._get_dfilter: meth (355-357)'.format(cname))
        ref.append('{0}._get_rfilter: meth (358-360)'.format(cname))
        ref.append('{0}._reset_dfilter_int: meth (361-366)'.format(cname))
        ref.append('{0}._in_header: meth (367-401)'.format(cname))
        ref.append('{0}._set_cfilter: meth (402-406)'.format(cname))
        ref.append('{0}._set_dfilter: meth (407-412)'.format(cname))
        ref.append('{0}._set_rfilter: meth (413-417)'.format(cname))
        ref.append('{0}._add_dfilter_int: meth (418-460)'.format(cname))
        ref.append('{0}._apply_filter: meth (461-493)'.format(cname))
        ref.append('{0}._set_has_header: meth (494-497)'.format(cname))
        ref.append('{0}._validate_frow: meth (498-503)'.format(cname))
        ref.append('{0}._validate_rfilter: meth (504-537)'.format(cname))
        ref.append('{0}.add_dfilter: meth (538-561)'.format(cname))
        ref.append('{0}.cols: meth (562-581)'.format(cname))
        ref.append('{0}.data: meth (582-610)'.format(cname))
        ref.append('{0}.dsort: meth (611-663)'.format(cname))
        ref.append('{0}.header: meth (664-695)'.format(cname))
        ref.append('{0}.replace: meth (696-766)'.format(cname))
        ref.append('{0}.reset_dfilter: meth (767-784)'.format(cname))
        ref.append('{0}.rows: meth (785-804)'.format(cname))
        ref.append('{0}.write: meth (805-887)'.format(cname))
        ref.append('{0}.cfilter: prop (888-910)'.format(cname))
        ref.append('{0}.dfilter: prop (911-934)'.format(cname))
        ref.append('{0}.rfilter: prop (935-958)'.format(cname))
        ref_txt = '\n'.join(ref)
        actual_txt = str(xobj)
        CS(actual_txt, ref_txt)
        #
        import tests.support.exdoc_support_module_1
        mname = 'tests.support.exdoc_support_module_1'
        xobj = putil.pinspect.Callables([modfile(mname)])
        ref = []
        cname = '{0}.ExceptionAutoDocClass'.format(mname)
        ref.append('Modules:')
        ref.append('   {0}'.format(mname))
        ref.append('Classes:')
        ref.append('   {0}'.format(cname))
        ref.append('   {0}.MyClass'.format(mname))
        ref.append('{0}._validate_arguments: func (17-31)'.format(mname))
        ref.append('{0}._write: func (32-36)'.format(mname))
        ref.append('{0}.write: func (37-50)'.format(mname))
        ref.append('{0}.read: func (51-62)'.format(mname))
        ref.append('{0}.probe: func (63-74)'.format(mname))
        ref.append('{0}.dummy_decorator1: func (75-79)'.format(mname))
        ref.append('{0}.dummy_decorator2: func (80-91)'.format(mname))
        ref.append('{0}.dummy_decorator2.wrapper: func (86-88)'.format(mname))
        ref.append('{0}.mlmdfunc: func (92-108)'.format(mname))
        ref.append('{0}: class (109-251)'.format(cname))
        ref.append('{0}.__init__: meth (112-124)'.format(cname))
        ref.append('{0}._del_value3: meth (125-132)'.format(cname))
        ref.append('{0}._get_value3: meth (133-141)'.format(cname))
        ref.append('{0}._set_value1: meth (142-152)'.format(cname))
        ref.append('{0}._set_value2: meth (153-166)'.format(cname))
        ref.append('{0}._set_value3: meth (167-177)'.format(cname))
        ref.append('{0}.add: meth (178-184)'.format(cname))
        ref.append('{0}.subtract: meth (185-191)'.format(cname))
        ref.append('{0}.multiply: meth (192-204)'.format(cname))
        ref.append('{0}.divide: meth (205-214)'.format(cname))
        ref.append('{0}.temp(getter): meth (215-219)'.format(cname))
        ref.append('{0}.temp(setter): meth (220-225)'.format(cname))
        ref.append('{0}.temp(deleter): meth (226-231)'.format(cname))
        ref.append('{0}.value1: prop (232-240)'.format(cname))
        ref.append('{0}.value2: prop (241-246)'.format(cname))
        ref.append('{0}.value3: prop (247-248)'.format(cname))
        ref.append('{0}.value4: prop (249-251)'.format(cname))
        ref.append('{0}.my_func: func (252-254)'.format(mname))
        ref.append('{0}.MyClass: class (255-259)'.format(mname))
        ref.append('{0}.MyClass.value: prop (259)'.format(mname))
        ref_txt = '\n'.join(ref)
        actual_txt = str(xobj)
        CS(actual_txt, ref_txt)
        #
        import tests.test_exdoc
        mname = 'tests.test_exdoc'
        xobj = putil.pinspect.Callables([modfile(mname)])
        cname1 = '{0}.TestExDocCxt'.format(mname)
        cname2 = '{0}.TestExDoc'.format(mname)
        mename1 = '{0}.test_multiple'.format(cname1)
        mename2 = '{0}.test_build_ex_tree'.format(cname2)
        meroot = '{0}.test_get_sphinx'.format(cname2)
        ref = []
        ref.append('Modules:')
        ref.append('   tests.test_exdoc')
        ref.append('Classes:')
        ref.append('   tests.test_exdoc.MockFCode')
        ref.append('   tests.test_exdoc.MockGetFrame')
        ref.append('   tests.test_exdoc.TestExDoc')
        ref.append('   tests.test_exdoc.TestExDocCxt')
        ref.append('tests.test_exdoc.exdocobj: func (50-83)')
        ref.append('tests.test_exdoc.exdocobj.multi_level_write: func (55-60)')
        ref.append('tests.test_exdoc.exdocobj_raised: func (84-97)')
        ref.append('tests.test_exdoc.exdocobj_single: func (98-107)')
        ref.append('tests.test_exdoc.simple_exobj: func (108-123)')
        ref.append('tests.test_exdoc.simple_exobj.func1: func (113-116)')
        ref.append('tests.test_exdoc.mock_getframe: func (124-127)')
        ref.append('tests.test_exdoc.trace_error_class: func (128-139)')
        ref.append('tests.test_exdoc.MockFCode: class (140-145)')
        ref.append('tests.test_exdoc.MockFCode.__init__: meth (141-145)')
        ref.append('tests.test_exdoc.MockGetFrame: class (146-153)')
        ref.append('tests.test_exdoc.MockGetFrame.__init__: meth (147-153)')
        ref.append('{0}: class (154-263)'.format(cname1))
        ref.append('{0}.test_init: meth (156-208)'.format(cname1))
        ref.append('{0}.test_init.check_ctx1: func (159-164)'.format(cname1))
        ref.append('{0}.test_init.check_ctx2: func (165-171)'.format(cname1))
        ref.append('{0}.test_init.func0: func (172-178)'.format(cname1))
        ref.append('{0}: meth (209-245)'.format(mename1))
        ref.append('{0}.func1: func (211-217)'.format(mename1))
        ref.append('{0}.test_trace: func (218-234)'.format(mename1))
        ref.append('{0}.test_save_callables: meth (246-263)'.format(cname1))
        ref.append('{0}: class (264-698)'.format(cname2))
        ref.append('{0}.test_init: meth (266-282)'.format(cname2))
        ref.append('{0}.test_copy: meth (283-296)'.format(cname2))
        ref.append('{0}: meth (297-395)'.format(mename2))
        ref.append('{0}.func1: func (304-307)'.format(mename2))
        ref.append('{0}.mock_add_nodes1: func (309-310)'.format(mename2))
        ref.append('{0}.mock_add_nodes2: func (311-312)'.format(mename2))
        ref.append('{0}.mock_add_nodes3: func (313-314)'.format(mename2))
        ref.append('{0}.test_depth: meth (396-403)'.format(cname2))
        ref.append('{0}.test_exclude: meth (404-411)'.format(cname2))
        ref.append('{0}_autodoc: meth (412-439)'.format(meroot))
        ref.append('{0}_doc: meth (440-698)'.format(meroot))
        ref_txt = '\n'.join(ref)
        actual_txt = str(xobj)
        CS(actual_txt, ref_txt)
        #
        import tests.support.pinspect_support_module_4
        mname = 'tests.support.pinspect_support_module_4'
        xobj = putil.pinspect.Callables([modfile(mname)])
        ref = []
        fname = '{0}.another_property_action_enclosing_function'.format(mname)
        ref.append('Modules:')
        ref.append('   {0}'.format(mname))
        ref.append('{0}: func (16-24)'.format(fname))
        ref.append('{0}.fget: func (21-23)'.format(fname))
        ref_txt = '\n'.join(ref)
        actual_txt = str(xobj)
        CS(actual_txt, ref_txt)
        # Test re-tries, should produce no action and raise no exception
        xobj = putil.pinspect.Callables([modfile(mname)])
        import tests.support.pinspect_support_module_10
        mname = 'tests.support.pinspect_support_module_10'
        xobj = putil.pinspect.Callables([modfile(mname)])
        ref = []
        cname = '{0}.AClass'.format(mname)
        ref.append('Modules:')
        ref.append('   {0}'.format(mname))
        ref.append('Classes:')
        ref.append('   {0}'.format(cname))
        ref.append('   {0}.method1.SubClass'.format(cname))
        ref.append('{0}: class (6-28)'.format(cname))
        ref.append('{0}.method1: meth (12-25)'.format(cname))
        ref.append('{0}.method1.func1: func (15-18)'.format(cname))
        ref.append('{0}.method1.SubClass: class (20-23)'.format(cname))
        ref.append('{0}.method1.SubClass.__init__: meth (22-23)'.format(cname))
        ref.append('{0}.method2: meth (26-28)'.format(cname))
        ref_txt = '\n'.join(ref)
        actual_txt = str(xobj)
        CS(actual_txt, ref_txt)


    def test_callables_db(self):
        """ Test callables_db property """
        import tests.support.pinspect_support_module_4
        mname = 'tests.support.pinspect_support_module_4'
        xobj = putil.pinspect.Callables([modfile(mname)])
        pkg_dir = os.path.dirname(__file__)
        ref = {
            'tests.support.pinspect_support_module_4.'
            'another_property_action_enclosing_function': {
                'code_id': (
                    os.path.join(
                        pkg_dir,
                        'support',
                        'pinspect_support_module_4.py'
                    ), 16
                ),
                'last_lineno': 21,
                'name': 'pinspect_support_module_4.'
                        'another_property_action_enclosing_function',
                'type': 'func'
            },
            'tests.support.pinspect_support_module_4.'
            'another_property_action_enclosing_function.fget': {
                'code_id': (
                    os.path.join(
                        pkg_dir,
                        'support',
                        'pinspect_support_module_4.py'
                    ), 18
                ),
                'last_lineno': 20,
                'name': 'pinspect_support_module_4.'
                        'another_property_action_enclosing_function.fget',
                'type': 'func'
            }
        }
        assert sorted(xobj.callables_db) == sorted(ref)
        ref = {
            (
                os.path.join(
                    pkg_dir,
                    'support',
                    'pinspect_support_module_4.py'
                ),
                16
            ): (
                'pinspect_support_module_4.'
                'another_property_action_enclosing_function'
               ),
            (
                os.path.join(
                    pkg_dir,
                    'support',
                    'pinspect_support_module_4.py'
                ),
                21
            ): (
                'pinspect_support_module_4.'
                'another_property_action_enclosing_function.fget'
            )
        }
        assert sorted(xobj.reverse_callables_db) == sorted(ref)

    def test_get_callable_from_line(self):
        """ Test get_callable_from_line() function """
        xobj = putil.pinspect.Callables()
        import tests.support.pinspect_support_module_4
        fname = modfile('tests.support.pinspect_support_module_4')
        ref = ('tests.support.pinspect_support_module_4.'
              'another_property_action_enclosing_function')
        assert xobj.get_callable_from_line(fname, 16) == ref
        xobj = putil.pinspect.Callables([fname])
        ref = ('tests.support.pinspect_support_module_4.'
              'another_property_action_enclosing_function')
        assert xobj.get_callable_from_line(fname, 16) == ref
        ref = ('tests.support.pinspect_support_module_4.'
              'another_property_action_enclosing_function')
        assert xobj.get_callable_from_line(fname, 17) == ref
        ref = ('tests.support.pinspect_support_module_4.'
              'another_property_action_enclosing_function')
        assert xobj.get_callable_from_line(fname, 24) == ref
        ref = ('tests.support.pinspect_support_module_4.'
              'another_property_action_enclosing_function.fget')
        assert xobj.get_callable_from_line(fname, 21) == ref
        ref = ('tests.support.pinspect_support_module_4.'
              'another_property_action_enclosing_function.fget')
        assert xobj.get_callable_from_line(fname, 22) == ref
        ref = ('tests.support.pinspect_support_module_4.'
              'another_property_action_enclosing_function.fget')
        assert xobj.get_callable_from_line(fname, 23) == ref
        ref = 'tests.support.pinspect_support_module_4'
        assert xobj.get_callable_from_line(fname, 100) == ref


##
# Tests for get_function_args()
###
class TestGetFunctionArgs(object):
    """ Tests for get_function_args function """
    def test_all_positional_arguments(self):
        """
        Test that function behaves properly when all arguments are positional
        arguments
        """
        def func(ppar1, ppar2, ppar3):
            pass
        obj = putil.pinspect.get_function_args
        assert obj(func) == ('ppar1', 'ppar2', 'ppar3')

    def test_all_keyword_arguments(self):
        """
        Test that function behaves properly when all arguments are keywords
        arguments
        """
        def func(kpar1=1, kpar2=2, kpar3=3):
            pass
        obj = putil.pinspect.get_function_args
        assert obj(func) == ('kpar1', 'kpar2', 'kpar3')

    def test_positional_and_keyword_arguments(self):
        """
        Test that function behaves properly when arguments are a mix of
        positional and keywords arguments
        """
        def func(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3, **kwargs):
            pass
        assert putil.pinspect.get_function_args(func) == (
            'ppar1', 'ppar2', 'ppar3', 'kpar1', 'kpar2', 'kpar3', '**kwargs'
        )
        assert putil.pinspect.get_function_args(func, no_varargs=True) == (
            'ppar1', 'ppar2', 'ppar3', 'kpar1', 'kpar2', 'kpar3'
        )

    def test_no_arguments(self):
        """
        Test that function behaves properly when there are no arguments
        passed
        """
        def func():
            pass
        assert putil.pinspect.get_function_args(func) == ()

    def test_no_self(self):
        """
        Test that function behaves properly when there are no arguments
        passed
        """
        class MyClass(object):
            def __init__(self, value, **kwargs):
                pass
        obj = partial(putil.pinspect.get_function_args, MyClass.__init__)
        assert obj() == ('self', 'value', '**kwargs')
        assert obj(no_self=True) == ('value', '**kwargs')
        assert obj(no_self=True, no_varargs=True) == ('value', )
        assert obj(no_varargs=True) == ('self', 'value')

    def test_nonzero(self):
        """ Test __nonzero__() function """
        obj = putil.pinspect.Callables()
        assert not obj
        obj.trace([modfile('putil.test')])
        assert obj
