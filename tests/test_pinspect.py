# test_pinspect.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0611,F0401,R0201,R0903,R0913,R0915,W0104,W0212,W0232,W0612,W0613,W0621

# Standard library imports
from __future__ import print_function
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
import putil.test


###
# Helper functions
###
def compare_str_outputs(obj, ref_list):
    """
    Produce helpful output when reference output does not match actual output
    """
    ref_text = '\n'.join(ref_list)
    if str(obj) != ref_text:
        actual_list = str(obj).split('\n')
        for actual_line, ref_line in zip(actual_list, ref_list):
            if actual_line != ref_line:
                print(
                    '\033[{0}m{1}\033[0m <-> {2}'.format(
                        31, actual_line, ref_line
                    )
                )
            else:
                print(actual_line)
        print('---[Differing lines]---')
        for actual_line, ref_line in zip(actual_list, ref_list):
            if actual_line != ref_line:
                print('Actual line...: {0}'.format(actual_line))
                print('Reference line: {0}'.format(ref_line))
                break
        print('-----------------------')
        if len(actual_list) != len(ref_list):
            print(
                '{0} longer than {1}'.format(
                    (
                        'Actual'
                        if len(actual_list) > len(ref_list) else
                        'Reference'
                    ),
                    (
                        'reference'
                        if len(actual_list) > len(ref_list) else
                        'actual'
                    )
                )
            )
            print_list = (
                actual_list
                if len(actual_list) > len(ref_list) else
                ref_list
            )
            print(print_list[min([len(actual_list), len(ref_list)]):])
            print('-----------------------')
    return ref_text


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
        # by other unit tests
        _readlines(fname)
        # Trigger unrelated exception exception
        obj = _readlines
        with pytest.raises(RuntimeError) as excinfo:
            _readlines(fname, mopen1)
        assert putil.test.get_exmsg(excinfo) == 'Mock mopen1 function'
        # Trigger UnicodeDecodeError exception
        assert _readlines(fname, mopen2, MockOpenCls) == 'MockOpenCls'


def test_object_is_module():
    """ Test object_is_module() function """
    assert not putil.pinspect.is_object_module(5)
    assert putil.pinspect.is_object_module(sys.modules['putil.pinspect'])


def test_get_module_name():
    """ Test get_module_name() function """
    putil.test.assert_exception(
        putil.pinspect.get_module_name,
        {'module_obj':5},
        RuntimeError,
        'Argument `module_obj` is not valid'
    )
    mock_module_obj = types.ModuleType('mock_module_obj', 'Mock module')
    putil.test.assert_exception(
        putil.pinspect.get_module_name,
        {'module_obj':mock_module_obj},
        RuntimeError,
        'Module object `mock_module_obj` could not be found in loaded modules'
    )
    ref = 'putil.pinspect'
    assert putil.pinspect.get_module_name(sys.modules[ref]) == ref
    assert putil.pinspect.get_module_name(sys.modules['putil']) == 'putil'


def test_get_module_name_from_fname():
    """ Test _get_module_name_from_fname() function """
    putil.test.assert_exception(
        putil.pinspect._get_module_name_from_fname,
        {'fname':'_not_a_module'},
        RuntimeError,
        'Module could not be found'
    )
    ref = 'putil.pinspect'
    assert putil.pinspect._get_module_name_from_fname(
        sys.modules[ref].__file__
    ) == ref


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
        putil.test.assert_exception(
            obj1._check_intersection,
            {'other':obj2},
            RuntimeError,
            'Conflicting information between objects'
        )
        obj1._callables_db = {'call1':1, 'call2':['a', 'c']}
        obj2._callables_db = {'call1':1, 'call2':['a', 'b']}
        putil.test.assert_exception(
            obj1._check_intersection,
            {'other':obj2},
            RuntimeError,
            'Conflicting information between objects'
        )
        obj1._callables_db = {'call1':1, 'call2':{'a':'b'}}
        obj2._callables_db = {'call1':1, 'call2':{'a':'c'}}
        putil.test.assert_exception(
            obj1._check_intersection,
            {'other':obj2},
            RuntimeError,
            'Conflicting information between objects'
        )
        obj1._callables_db = {'call1':1, 'call2':'a'}
        obj2._callables_db = {'call1':1, 'call2':'c'}
        putil.test.assert_exception(
            obj1._check_intersection,
            {'other':obj2},
            RuntimeError,
            'Conflicting information between objects'
        )
        obj1._callables_db = {'call1':1, 'call2':'a'}
        obj2._callables_db = {'call1':1, 'call2':'a'}
        assert obj1._check_intersection(obj2) is None

    def test_init_exceptions(self):
        """ Test constructor exceptions """
        putil.test.assert_exception(
            putil.pinspect.Callables,
            {'fnames':5},
            RuntimeError,
            'Argument `fnames` is not valid'
        )
        putil.test.assert_exception(
            putil.pinspect.Callables,
            {'fnames':[5]},
            RuntimeError,
            'Argument `fnames` is not valid'
        )
        putil.test.assert_exception(
            putil.pinspect.Callables,
            {'fnames':['_not_a_file_']},
            OSError,
            'File _not_a_file_ could not be found'
        )

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
        assert (
            putil.test.get_exmsg(excinfo)
            ==
            'Conflicting information between objects'
        )
        obj1._callables_db = {'call1':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}}
        #
        obj2._reverse_callables_db = {'rc3':'5', 'rc2':'-1'}
        with pytest.raises(RuntimeError) as excinfo:
            obj1+obj2
        assert (
            putil.test.get_exmsg(excinfo)
            ==
            'Conflicting information between objects'
        )
        obj2._reverse_callables_db = {'rc3':'0', 'rc4':'-1'}
        #
        obj2._modules_dict = {'key1':{'entry':'pi'}, 'key4':{'entry':'gamma'}}
        with pytest.raises(RuntimeError) as excinfo:
            obj1+obj2
        assert (
            putil.test.get_exmsg(excinfo)
            ==
            'Conflicting information between objects'
        )
        obj2._modules_dict = {'key3':{'entry':'pi'}, 'key4':{'entry':'gamma'}}
        # Test when intersection is the same
        obj2._modules_dict = {
            'key1':{'entry':'alpha'}, 'key4':{'entry':'gamma'}
        }
        obj1+obj2
        obj2._modules_dict = {'key3':{'entry':'pi'}, 'key4':{'entry':'gamma'}}

        sobj = obj1+obj2
        assert (
            sorted(sobj._callables_db)
            ==
            sorted(
                {
                    'call1':{'a':5, 'b':6},
                    'call2':{'a':7, 'b':8},
                    'call3':{'a':10, 'b':100}, 'call4':{'a':200, 'b':300}
                }
            )
        )
        assert (
            sorted(sobj._reverse_callables_db)
            ==
            sorted(
                {
                    'rc1':'5',
                    'rc2':'7',
                    'rc3':'0',
                    'rc4':'-1'
                }
            )
        )
        assert (
            sorted(sobj._modules_dict)
            ==
            sorted(
                {
                    'key1':{'entry':'alpha'},
                    'key2':{'entry':'beta'},
                    'key3':{'entry':'pi'},
                    'key4':{'entry':'gamma'}
                }
            )
        )
        assert sorted(sobj._fnames) == sorted({'hello':0, 'world':1})
        assert (
            sorted(sobj._module_names) == sorted(['this', 'is', 'a', 'test'])
        )
        assert (
            sorted(sobj._class_names) == sorted(['once', 'upon', 'a', 'time'])
        )
        #
        obj1 += obj2
        assert (
            sorted(obj1._callables_db)
            ==
            sorted(
                {
                    'call1':{'a':5, 'b':6},
                    'call2':{'a':7, 'b':8},
                    'call3':{'a':10, 'b':100},
                    'call4':{'a':200, 'b':300}
                }
            )
        )
        assert (
            sorted(obj1._reverse_callables_db)
            ==
            sorted(
                {
                    'rc1':'5',
                    'rc2':'7',
                    'rc3':'0',
                    'rc4':'-1'
                }
            )
        )
        assert (
            sorted(obj1._modules_dict)
            ==
            sorted(
                {
                    'key1':{'entry':'alpha'},
                    'key2':{'entry':'beta'},
                    'key3':{'entry':'pi'},
                    'key4':{'entry':'gamma'}
                }
            )
        )
        assert sorted(obj1._fnames) == sorted({'hello':0, 'world':1})
        assert (
            sorted(obj1._module_names) == sorted(['this', 'is', 'a', 'test'])
        )
        assert (
            sorted(obj1._class_names) == sorted(['once', 'upon', 'a', 'time'])
        )

    def test_copy(self):
        """ Test __copy__ method behavior """
        source_obj = putil.pinspect.Callables()
        import tests.support.pinspect_support_module_1
        source_obj.trace(
            [sys.modules['tests.support.pinspect_support_module_1'].__file__]
        )
        dest_obj = copy.copy(source_obj)
        assert source_obj._module_names == dest_obj._module_names
        assert id(source_obj._module_names) != id(dest_obj._module_names)
        assert source_obj._class_names == dest_obj._class_names
        assert id(source_obj._class_names) != id(dest_obj._class_names)
        assert source_obj._callables_db == dest_obj._callables_db
        assert id(source_obj._callables_db) != id(dest_obj._callables_db)
        assert (
            source_obj._reverse_callables_db == dest_obj._reverse_callables_db
        )
        assert (id(source_obj._reverse_callables_db) !=
               id(dest_obj._reverse_callables_db))

    def test_eq(self):
        """ Test __eq__ method behavior """
        obj1 = putil.pinspect.Callables()
        obj2 = putil.pinspect.Callables()
        obj3 = putil.pinspect.Callables()
        import tests.support.pinspect_support_module_1
        import tests.support.pinspect_support_module_2
        obj1.trace(
            [sys.modules['tests.support.pinspect_support_module_1'].__file__]
        )
        obj2.trace(
            [sys.modules['tests.support.pinspect_support_module_1'].__file__]
        )
        obj3.trace([sys.modules['putil.test'].__file__])
        assert (obj1 == obj2) and (obj1 != obj3)
        assert obj1 != 5

    def test_repr(self):
        """ Test __repr__ method behavior """
        import tests.support.exdoc_support_module_1
        file1 = sys.modules[
            'tests.support.exdoc_support_module_1'
        ].__file__.replace('.pyc', '.py')
        file2 = sys.modules[
            'tests.support.exdoc_support_module_2'
        ].__file__.replace('.pyc', '.py')
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
        ref = sys.modules['putil.test'].__file__
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
            'putil.test.assert_exception: func (22-91)\n'
            'putil.test.comp_list_of_dicts: func (92-106)\n'
            'putil.test.exception_type_str: func (107-124)\n'
            'putil.test.get_exmsg: func (125-127)'
        )
        if str(obj) != rtext:
            print('Actual text:')
            print(obj)
            print('Reference text:')
            print(rtext)
        assert str(obj) == rtext
        os.remove(src)
        time.sleep(0.5)
        with open(src, 'w') as fobj:
            fobj.write('def my_func():\n    pass')
        obj.refresh()
        assert obj._fnames[src] != tmod
        rtext = (
            'Modules:\n'
            '   putil.pit\n'
            '   putil.test\n'
            'putil.pit.my_func: func (1-2)\n'
            'putil.test.assert_exception: func (22-91)\n'
            'putil.test.comp_list_of_dicts: func (92-106)\n'
            'putil.test.exception_type_str: func (107-124)\n'
            'putil.test.get_exmsg: func (125-127)'
        )
        if str(obj) != rtext:
            print('Actual text:')
            print(obj)
            print('Reference text:')
            print(rtext)
        assert str(obj) == rtext
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
        obj1 = putil.pinspect.Callables(
            [sys.modules[mname].__file__]
        )
        with putil.misc.TmpFile() as fname:
            obj1.save(fname)
            obj2 = putil.pinspect.Callables()
            assert not bool(obj2)
            obj2.load(fname)
        assert obj1 == obj2
        # Test merging of traced and file-based module information
        mname1 = 'putil.pcsv.csv_file'
        obj1 = putil.pinspect.Callables(
            [sys.modules[mname1].__file__]
        )
        mname2 = 'tests.support.exdoc_support_module_1'
        obj2 = putil.pinspect.Callables(
            [sys.modules[mname2].__file__]
        )
        with putil.misc.TmpFile() as fname1:
            with putil.misc.TmpFile() as fname2:
                obj1.save(fname1)
                obj2.save(fname2)
                obj3 = putil.pinspect.Callables(
                    [
                        sys.modules[mname1].__file__,
                        sys.modules[mname2].__file__
                    ]
                )
                obj4 = putil.pinspect.Callables()
                obj4.load(fname2)
                obj4.load(fname1)
        assert obj3 == obj4

    def test_load_exceptions(self):
        """ Test load method exceptions """
        obj = putil.pinspect.Callables()
        for item in [True, 5]:
            putil.test.assert_exception(
                obj.load,
                {'callables_fname':item},
                RuntimeError,
                'Argument `callables_fname` is not valid'
            )
        putil.test.assert_exception(
            obj.load,
            {'callables_fname':'_not_a_file_'},
            OSError,
            'File _not_a_file_ could not be found'
        )

    def test_save_exceptions(self):
        """ Test save method exceptions """
        obj = putil.pinspect.Callables()
        for item in [True, 5]:
            putil.test.assert_exception(
                obj.save,
                {'callables_fname':item},
                RuntimeError,
                'Argument `callables_fname` is not valid'
            )

    def test_trace(self):
        """ Test trace method behavior """
        import putil.pcsv
        mname = 'putil.pcsv.csv_file'
        cname = '{0}.CsvFile'.format(mname)
        xobj = putil.pinspect.Callables(
            [sys.modules[mname].__file__]
        )
        ref = list()
        ref.append('Modules:')
        ref.append('   {0}'.format(mname))
        ref.append('Classes:')
        ref.append('   {0}'.format(cname))
        ref.append('{0}._homogenize_data_filter: func (44-66)'.format(mname))
        ref.append('{0}._tofloat: func (67-82)'.format(mname))
        ref.append('{0}: class (83-1050)'.format(cname))
        ref.append('{0}.__init__: meth (134-231)'.format(cname))
        ref.append('{0}.__eq__: meth (232-266)'.format(cname))
        ref.append('{0}.__repr__: meth (267-304)'.format(cname))
        ref.append('{0}.__str__: meth (305-349)'.format(cname))
        ref.append('{0}._format_rfilter: meth (350-366)'.format(cname))
        ref.append('{0}._gen_col_index: meth (367-379)'.format(cname))
        ref.append('{0}._get_cfilter: meth (380-382)'.format(cname))
        ref.append('{0}._get_dfilter: meth (383-385)'.format(cname))
        ref.append('{0}._get_rfilter: meth (386-388)'.format(cname))
        ref.append('{0}._reset_dfilter_int: meth (389-394)'.format(cname))
        ref.append('{0}._in_header: meth (395-447)'.format(cname))
        ref.append('{0}._set_cfilter: meth (448-452)'.format(cname))
        ref.append('{0}._set_dfilter: meth (453-458)'.format(cname))
        ref.append('{0}._set_rfilter: meth (459-463)'.format(cname))
        ref.append('{0}._add_dfilter_int: meth (464-506)'.format(cname))
        ref.append('{0}._apply_filter: meth (507-536)'.format(cname))
        ref.append('{0}._set_has_header: meth (537-540)'.format(cname))
        ref.append('{0}._validate_frow: meth (541-556)'.format(cname))
        ref.append('{0}._validate_rfilter: meth (557-602)'.format(cname))
        ref.append('{0}.add_dfilter: meth (603-626)'.format(cname))
        ref.append('{0}.cols: meth (627-646)'.format(cname))
        ref.append('{0}.data: meth (647-668)'.format(cname))
        ref.append('{0}.dsort: meth (669-722)'.format(cname))
        ref.append('{0}.header: meth (723-754)'.format(cname))
        ref.append('{0}.replace: meth (755-849)'.format(cname))
        ref.append('{0}.reset_dfilter: meth (850-867)'.format(cname))
        ref.append('{0}.rows: meth (868-887)'.format(cname))
        ref.append('{0}.write: meth (888-973)'.format(cname))
        ref.append('{0}.cfilter: prop (974-998)'.format(cname))
        ref.append('{0}.dfilter: prop (999-1024)'.format(cname))
        ref.append('{0}.rfilter: prop (1025-1050)'.format(cname))
        ref_txt = '\n'.join(ref)
        actual_txt = str(xobj)
        if actual_txt != ref_txt:
            print('Actual text')
            print('-----------')
            print(actual_txt)
            print('Reference text')
            print('--------------')
            print(ref_txt)
        assert actual_txt == ref_txt

        import tests.support.exdoc_support_module_1
        xobj = putil.pinspect.Callables(
            [sys.modules['tests.support.exdoc_support_module_1'].__file__]
        )
        ref = list()
        ref.append('Modules:')
        ref.append('   tests.support.exdoc_support_module_1')
        ref.append('Classes:')
        ref.append('   tests.support.exdoc_support_module_1.'
                   'ExceptionAutoDocClass')
        ref.append('   tests.support.exdoc_support_module_1.'
                   'MyClass')
        ref.append('tests.support.exdoc_support_module_1._validate_arguments:'
                   ' func (17-31)')
        ref.append('tests.support.exdoc_support_module_1._write: func (32-36)')
        ref.append('tests.support.exdoc_support_module_1.write: func (37-50)')
        ref.append('tests.support.exdoc_support_module_1.read: func (51-62)')
        ref.append('tests.support.exdoc_support_module_1.probe: func (63-74)')
        ref.append('tests.support.exdoc_support_module_1.dummy_decorator1:'
                   ' func (75-79)')
        ref.append('tests.support.exdoc_support_module_1.dummy_decorator2:'
                   ' func (80-91)')
        ref.append('tests.support.exdoc_support_module_1.dummy_decorator2'
                   '.wrapper: func (86-88)')
        ref.append('tests.support.exdoc_support_module_1.mlmdfunc:'
                   ' func (92-108)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   ': class (109-251)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.__init__: meth (112-124)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '._del_value3: meth (125-132)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '._get_value3: meth (133-141)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '._set_value1: meth (142-152)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '._set_value2: meth (153-166)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '._set_value3: meth (167-177)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.add: meth (178-184)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.subtract: meth (185-191)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.multiply: meth (192-204)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.divide: meth (205-214)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.temp(getter): meth (215-219)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.temp(setter): meth (220-225)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.temp(deleter): meth (226-231)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.value1: prop (232-240)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.value2: prop (241-246)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.value3: prop (247-248)')
        ref.append('tests.support.exdoc_support_module_1.ExceptionAutoDocClass'
                   '.value4: prop (249-251)')
        ref.append('tests.support.exdoc_support_module_1.my_func: '
                   'func (252-254)')
        ref.append('tests.support.exdoc_support_module_1.MyClass'
                   ': class (255-259)')
        ref.append('tests.support.exdoc_support_module_1.MyClass'
                   '.value: prop (259)')
        ref_txt = '\n'.join(ref)
        actual_txt = str(xobj)
        if actual_txt != ref_txt:
            print('Actual text')
            print('-----------')
            print(actual_txt)
            print('Reference text')
            print('--------------')
            print(ref_txt)
        assert actual_txt == ref_txt
        import tests.test_exdoc
        xobj = putil.pinspect.Callables(
            [sys.modules['tests.test_exdoc'].__file__]
        )
        ref = list()
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
        ref.append('tests.test_exdoc.simple_exobj: func (108-125)')
        ref.append('tests.test_exdoc.simple_exobj.func1: func (113-118)')
        ref.append('tests.test_exdoc.mock_getframe: func (126-129)')
        ref.append('tests.test_exdoc.trace_error_class: func (130-141)')
        ref.append('tests.test_exdoc.MockFCode: class (142-147)')
        ref.append('tests.test_exdoc.MockFCode.__init__: meth (143-147)')
        ref.append('tests.test_exdoc.MockGetFrame: class (148-155)')
        ref.append('tests.test_exdoc.MockGetFrame.__init__: meth (149-155)')
        ref.append('tests.test_exdoc.TestExDocCxt: class (156-302)')
        ref.append('tests.test_exdoc.TestExDocCxt.test_init: meth (158-239)')
        ref.append(
            'tests.test_exdoc.TestExDocCxt.test_init.func0: func (160-169)'
        )
        ref.append(
            'tests.test_exdoc.TestExDocCxt.test_multiple: meth (240-280)'
        )
        ref.append(
            'tests.test_exdoc.TestExDocCxt.test_multiple.func1: func (242-251)'
        )
        ref.append(
            'tests.test_exdoc.TestExDocCxt.test_multiple.test_trace: '
            'func (252-269)'
        )
        ref.append(
            'tests.test_exdoc.TestExDocCxt.test_save_callables: meth (281-302)'
        )
        ref.append('tests.test_exdoc.TestExDoc: class (303-918)')
        ref.append('tests.test_exdoc.TestExDoc.test_init: meth (305-354)')
        ref.append('tests.test_exdoc.TestExDoc.test_copy: meth (355-368)')
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree: meth (369-476)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree.func1: '
            'func (376-381)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree.mock_add_nodes1: '
            'func (383-384)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree.mock_add_nodes2: '
            'func (385-386)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree.mock_add_nodes3: '
            'func (387-388)'
        )
        ref.append('tests.test_exdoc.TestExDoc.test_depth: meth (477-486)')
        ref.append('tests.test_exdoc.TestExDoc.test_exclude: meth (487-496)')
        ref.append(
            'tests.test_exdoc.TestExDoc.test_get_sphinx_autodoc: '
            'meth (497-524)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_get_sphinx_doc: meth (525-918)'
        )
        ref_txt = '\n'.join(ref)
        actual_txt = str(xobj)
        if actual_txt != ref_txt:
            print('Actual text')
            print('-----------')
            print(actual_txt)
            print('Reference text')
            print('--------------')
            print(ref_txt)
        assert actual_txt == ref_txt
        import tests.support.pinspect_support_module_4
        xobj = putil.pinspect.Callables(
            [sys.modules['tests.support.pinspect_support_module_4'].__file__]
        )
        ref = list()
        ref.append('Modules:')
        ref.append('   tests.support.pinspect_support_module_4')
        ref.append('tests.support.pinspect_support_module_4.'
                   'another_property_action_enclosing_function: func (16-24)'
        )
        ref.append('tests.support.pinspect_support_module_4.'
                   'another_property_action_enclosing_function.fget: '
                   'func (21-23)'
        )
        ref_txt = '\n'.join(ref)
        actual_txt = str(xobj)
        assert actual_txt == ref_txt
        # Test re-tries, should produce no action and raise no exception
        xobj.trace(
            [sys.modules['tests.support.pinspect_support_module_4'].__file__]
        )

    def test_callables_db(self):
        """ Test callables_db property """
        import tests.support.pinspect_support_module_4
        xobj = putil.pinspect.Callables(
            [sys.modules['tests.support.pinspect_support_module_4'].__file__]
        )
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
        fname = sys.modules['tests.support.pinspect_support_module_4'].__file__
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
            'ppar1',
            'ppar2',
            'ppar3',
            'kpar1',
            'kpar2',
            'kpar3',
            '**kwargs'
        )
        assert putil.pinspect.get_function_args(func, no_varargs=True) == (
            'ppar1',
            'ppar2',
            'ppar3',
            'kpar1',
            'kpar2',
            'kpar3'
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
        assert (
            putil.pinspect.get_function_args(MyClass.__init__)
            ==
            (
                'self',
                'value',
                '**kwargs'
            )
        )
        assert (
            putil.pinspect.get_function_args(
                MyClass.__init__,
                no_self=True
            )
            ==
            ('value', '**kwargs')
        )
        assert (
            putil.pinspect.get_function_args(
                MyClass.__init__,
                no_self=True,
                no_varargs=True
            )
            ==
            ('value', )
        )
        assert (
            putil.pinspect.get_function_args(
                MyClass.__init__,
                no_varargs=True
            )
            ==
            ('self', 'value')
        )

    def test_nonzero(self):
        """ Test __nonzero__() function """
        obj = putil.pinspect.Callables()
        assert not obj
        obj.trace([sys.modules['putil.test'].__file__])
        assert obj
