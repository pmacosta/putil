# test_pinspect.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,F0401,R0201,R0903,R0913,R0915,W0104,W0212,W0232,W0612,W0613

from __future__ import print_function
import copy
import os
import pytest
import sys
import types

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
    def test_callables_errors(self):
        """ Test callables __init__ (and trace() function) data validation """
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

    def test_repr(self):
        """ Test __repr__() function """
        import tests.support.exdoc_support_module_1
        file1 = sys.modules[
            'tests.support.exdoc_support_module_1'
        ].__file__.replace('.pyc', '.py')
        file2 = sys.modules[
            'tests.support.exdoc_support_module_2'
        ].__file__.replace('.pyc', '.py')
        xobj = putil.pinspect.Callables([file2])
        xobj.trace([file1])
        ref = "putil.pinspect.Callables(['{0}', '{1}'])".format(file1, file2)
        assert repr(xobj) == ref

    def test_add(self):
        """ Test __add__() and __radd__() functions """
        obj1 = putil.pinspect.Callables()
        obj1._callables_db = {'call1':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}}
        obj1._reverse_callables_db = {'rc1':'5', 'rc2':'7'}
        obj1._modules_dict = {
            'key1':{'entry':'alpha'}, 'key2':{'entry':'beta'}
        }
        obj1._fnames = ['hello']
        obj1._module_names = ['this', 'is']
        obj1._class_names = ['once', 'upon']
        #
        obj2 = putil.pinspect.Callables()
        obj2._callables_db = {
            'call3':{'a':10, 'b':100}, 'call4':{'a':200, 'b':300}
        }
        obj2._reverse_callables_db = {'rc3':'0', 'rc4':'1'}
        obj2._modules_dict = {'key3':{'entry':'pi'}, 'key4':{'entry':'gamma'}}
        obj2._fnames = ['world']
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
        assert sorted(sobj._fnames) == sorted(['hello', 'world'])
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
        assert sorted(obj1._fnames) == sorted(['hello', 'world'])
        assert (
            sorted(obj1._module_names) == sorted(['this', 'is', 'a', 'test'])
        )
        assert (
            sorted(obj1._class_names) == sorted(['once', 'upon', 'a', 'time'])
        )

    def test_callables_works(self):
        # pylint: disable=W0621
        import putil.pcsv
        mname = 'putil.pcsv.csv_file'
        cname = '{}.CsvFile'.format(mname)
        xobj = putil.pinspect.Callables(
            [sys.modules[mname].__file__]
        )
        ref = list()
        ref.append('Modules:')
        ref.append('   {}'.format(mname))
        ref.append('Classes:')
        ref.append('   {}'.format(cname))
        ref.append('{}._homogenize_data_filter: func (40-62)'.format(mname))
        ref.append('{}._tofloat: func (63-78)'.format(mname))
        ref.append('{}: class (79-1006)'.format(cname))
        ref.append('{}.__init__: meth (127-208)'.format(cname))
        ref.append('{}.__eq__: meth (209-241)'.format(cname))
        ref.append('{}.__repr__: meth (242-276)'.format(cname))
        ref.append('{}.__str__: meth (277-322)'.format(cname))
        ref.append('{}._format_rfilter: meth (323-339)'.format(cname))
        ref.append('{}._gen_col_index: meth (340-352)'.format(cname))
        ref.append('{}._get_cfilter: meth (353-355)'.format(cname))
        ref.append('{}._get_dfilter: meth (356-358)'.format(cname))
        ref.append('{}._get_rfilter: meth (359-361)'.format(cname))
        ref.append('{}._reset_dfilter_int: meth (362-367)'.format(cname))
        ref.append('{}._in_header: meth (368-420)'.format(cname))
        ref.append('{}._set_cfilter: meth (421-425)'.format(cname))
        ref.append('{}._set_dfilter: meth (426-431)'.format(cname))
        ref.append('{}._set_rfilter: meth (432-436)'.format(cname))
        ref.append('{}._add_dfilter_int: meth (437-479)'.format(cname))
        ref.append('{}._apply_filter: meth (480-509)'.format(cname))
        ref.append('{}._set_has_header: meth (510-513)'.format(cname))
        ref.append('{}._validate_rfilter: meth (514-559)'.format(cname))
        ref.append('{}.add_dfilter: meth (560-583)'.format(cname))
        ref.append('{}.cols: meth (584-603)'.format(cname))
        ref.append('{}.data: meth (604-625)'.format(cname))
        ref.append('{}.dsort: meth (626-678)'.format(cname))
        ref.append('{}.header: meth (679-710)'.format(cname))
        ref.append('{}.replace: meth (711-805)'.format(cname))
        ref.append('{}.reset_dfilter: meth (806-823)'.format(cname))
        ref.append('{}.rows: meth (824-843)'.format(cname))
        ref.append('{}.write: meth (844-929)'.format(cname))
        ref.append('{}.cfilter: prop (930-954)'.format(cname))
        ref.append('{}.dfilter: prop (955-980)'.format(cname))
        ref.append('{}.rfilter: prop (981-1006)'.format(cname))
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
        ref.append('tests.test_exdoc.exdocobj: func (45-78)')
        ref.append('tests.test_exdoc.exdocobj.multi_level_write: func (50-55)')
        ref.append('tests.test_exdoc.exdocobj_raised: func (79-92)')
        ref.append('tests.test_exdoc.exdocobj_single: func (93-102)')
        ref.append('tests.test_exdoc.simple_exobj: func (103-120)')
        ref.append('tests.test_exdoc.simple_exobj.func1: func (108-113)')
        ref.append('tests.test_exdoc.mock_getframe: func (121-124)')
        ref.append('tests.test_exdoc.trace_error_class: func (125-136)')
        ref.append('tests.test_exdoc.MockFCode: class (137-142)')
        ref.append('tests.test_exdoc.MockFCode.__init__: meth (138-142)')
        ref.append('tests.test_exdoc.MockGetFrame: class (143-150)')
        ref.append('tests.test_exdoc.MockGetFrame.__init__: meth (144-150)')
        ref.append('tests.test_exdoc.TestExDocCxt: class (151-258)')
        ref.append('tests.test_exdoc.TestExDocCxt.test_init: meth (153-213)')
        ref.append(
            'tests.test_exdoc.TestExDocCxt.test_init.func0: '
            'func (155-164)'
        )
        ref.append(
            'tests.test_exdoc.TestExDocCxt.test_multiple: '
            'meth (214-258)'
        )
        ref.append(
            'tests.test_exdoc.TestExDocCxt.test_multiple.func1: '
            'func (216-225)'
        )
        ref.append(
            'tests.test_exdoc.TestExDocCxt.test_multiple.test_trace: '
            'func (226-243)'
        )
        ref.append('tests.test_exdoc.TestExDoc: class (259-850)')
        ref.append('tests.test_exdoc.TestExDoc.test_init: meth (261-310)')
        ref.append('tests.test_exdoc.TestExDoc.test_copy: meth (311-324)')
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree: '
            'meth (325-432)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree.func1: '
            'func (332-337)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree.mock_add_nodes1: '
            'func (339-340)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree.mock_add_nodes2: '
            'func (341-342)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_build_ex_tree.mock_add_nodes3: '
            'func (343-344)'
        )
        ref.append('tests.test_exdoc.TestExDoc.test_depth: meth (433-442)')
        ref.append('tests.test_exdoc.TestExDoc.test_exclude: meth (443-452)')
        ref.append(
            'tests.test_exdoc.TestExDoc.test_get_sphinx_autodoc: '
            'meth (453-480)'
        )
        ref.append(
            'tests.test_exdoc.TestExDoc.test_get_sphinx_doc: '
            'meth (481-850)'
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

    def test_empty_str(self):
        """ Test __str__() magic method when object is empty """
        obj = putil.pinspect.Callables()
        assert str(obj) == ''

    def test_copy(self):
        """ Test __copy__() magic method """
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
        """ Test __eq__() magic method """
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
        assert 5 != obj1

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
