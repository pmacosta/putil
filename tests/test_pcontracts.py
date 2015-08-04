# test_pcontracts.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E1121,W0212,W0232,W0611,W0612,W0613

import contracts
import copy
import functools
import pytest
import sys

import putil.exh
import putil.pcontracts
import putil.test


###
# Helper functions
###
def decfunc(func):
    """" Decorator function to test _create_argument_value_pairs function """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function that creates the argument dictionary and returns a
        ret_func, which in turn just returns the argument passed. This is for
        testing only, obviously in an actual environment the decorator would
        return the original (called) function with the passed arguments
        """
        return ret_func(
            putil.pcontracts._create_argument_value_pairs(
                func, *args, **kwargs
            )
        )
    return wrapper


def ret_func(par):
    """ Returns the passed argument """
    return par


def sample_func_global():
    """ Global test function to test get_exdesc function behavior """
    tmp_global = putil.pcontracts.get_exdesc()
    return tmp_global


###
# Test functions
###
def test_get_replacement_token():
    """ Test _get_replacement_token function behavior """
    assert (
        putil.pcontracts._get_replacement_token(
            'Argument `*[argument_name]*` could not be found'
        )
        ==
        'argument_name'
    )
    assert (
        putil.pcontracts._get_replacement_token(
            'Argument `*file_name*` could not be found'
        )
        is
        None
    )


def test_format_arg():
    """ Test _format_arg function behavior """
    fobj = putil.pcontracts._format_arg
    assert (
        fobj('Message')
        ==
        {'msg':'Message', 'type':RuntimeError}
    )
    assert (
        fobj(OSError)
        ==
        {
            'msg':'Argument `*[argument_name]*` is not valid',
            'type':OSError
        }
    )
    assert (
        fobj((ValueError, 'Description 1'))
        ==
        {'msg':'Description 1', 'type':ValueError}
    )
    assert (
        fobj(('Description 2', TypeError))
        ==
        {'msg':'Description 2', 'type':TypeError}
    )


def test_format_arg_exceptions():
    """ Test _format_arg function exceptions """
    items = [
        '',
        [RuntimeError, ''],
        ['', RuntimeError],
        [''],
    ]
    for item in items:
        putil.test.assert_exception(
            putil.pcontracts._format_arg,
            {'arg':item},
            ValueError,
            'Empty custom contract exception message'
        )
    items = [
        set([RuntimeError, 'Message']),
        [],
        (RuntimeError, 'Message', 3),
        [3],
        ['a', 3],
        [3, 'a'],
        [ValueError, 3],
        [3, ValueError]
    ]
    for item in items:
        putil.test.assert_exception(
            putil.pcontracts._format_arg,
            {'arg':item},
            TypeError,
            'Illegal custom contract exception definition'
        )


def test_isexception():
    """ Test _isexception function behavior """
    assert not putil.pcontracts._isexception(str)
    assert not putil.pcontracts._isexception(3)
    assert putil.pcontracts._isexception(RuntimeError)


def test_parse_new_contract_args():
    """ Test _parse_new_contract_args function behavior """
    fobj = putil.pcontracts._parse_new_contract_args
    # Validate *args
    with pytest.raises(TypeError) as excinfo:
        fobj('Desc1', file_not_found='Desc2')
    assert (
        putil.test.get_exmsg(excinfo) ==
        'Illegal custom contract exception definition'
    )
    with pytest.raises(TypeError) as excinfo:
        fobj('Desc1', 'Desc2')
    assert (
        putil.test.get_exmsg(excinfo) ==
        'Illegal custom contract exception definition'
    )
    with pytest.raises(TypeError) as excinfo:
        fobj(5)
    assert (
        putil.test.get_exmsg(excinfo)
        ==
        'Illegal custom contract exception definition'
    )
    # Normal behavior
    assert (
        fobj()
        ==
        [
            {
                'name':'argument_invalid',
                'msg':'Argument `*[argument_name]*` is not valid',
                'type':RuntimeError
            }
        ]
    )
    assert (
        fobj('Desc')
        ==
        [
            {
                'name':'default',
                'msg':'Desc',
                'type':RuntimeError
            }
        ]
    )
    assert (
        fobj(OSError)
        ==
        [
            {
                'name':'default',
                'msg':'Argument `*[argument_name]*` is not valid',
                'type':OSError
            }
        ]
    )
    assert (
        fobj(('a', ))
        ==
        [{'name':'default', 'msg':'a', 'type':RuntimeError}]
    )
    assert (
        fobj((OSError, ))
        ==
        [
            {
                'name':'default',
                'msg':'Argument `*[argument_name]*` is not valid',
                'type':OSError
            }
        ]
    )
    assert (
        fobj([TypeError, 'bcd'])
        ==
        [
            {
                'name':'default',
                'msg':'bcd',
                'type':TypeError
            }
        ]
    )
    assert (
        fobj(['xyz', ValueError])
        ==
        [
            {
                'name':'default',
                'msg':'xyz',
                'type':ValueError
            }
        ]
    )
    assert putil.test.comp_list_of_dicts(
        fobj(
            mycontract=('xyz', ValueError),
            othercontract=('abc', OSError)
        ),
        [
            {'name':'othercontract', 'msg':'abc', 'type':OSError},
            {'name':'mycontract', 'msg':'xyz', 'type':ValueError}
        ]
    )
    # Validate **kwargs
    putil.test.assert_exception(
        fobj,
        {'a':45},
        TypeError,
        'Illegal custom contract exception definition'
    )
    ref = [
        {'name':'char', 'msg':'Desc1', 'type':RuntimeError},
        {'name':'other', 'msg':'a', 'type':ValueError}
    ]
    assert putil.test.comp_list_of_dicts(
        ref,
        fobj(char='Desc1', other=['a', ValueError])
    )


def test_register_custom_contracts():
    """ Test _register_custom_contracts function behavior """
    original_custom_contracts = copy.deepcopy(
        putil.pcontracts._CUSTOM_CONTRACTS
    )
    fobj = putil.pcontracts._register_custom_contracts
    ftest = putil.test.assert_exception
    key1 = 'contract_name'
    key2 = 'contract_exceptions'
    # Test data validation
    ftest(
        fobj,
        {key1:5, key2:{}},
        TypeError,
        'Argument `contract_name` is of the wrong type'
    )
    ftest(
        fobj,
        {key1:'test', key2:5},
        TypeError, 'Argument `contract_exceptions` is of the wrong type'
    )
    ftest(
        fobj,
        {key1:'test', key2:{'msg':'b', 'key':'hole'}},
        TypeError, 'Contract exception definition is of the wrong type'
    )
    ftest(
        fobj,
        {key1:'test', key2:[{5:'b'}]},
        TypeError, 'Contract exception definition is of the wrong type'
    )
    ftest(
        fobj,
        {key1:'test', key2:[{'a':'b'}]},
        TypeError, 'Contract exception definition is of the wrong type'
    )
    ftest(
        fobj,
        {key1:'test', key2:[{'name':'a', 'msg':'b', 'x':RuntimeError}]},
        TypeError, 'Contract exception definition is of the wrong type'
    )
    ftest(
        fobj,
        {key1:'test', key2:[{'name':5, 'msg':'b', 'type':RuntimeError}]},
        TypeError, 'Contract exception definition is of the wrong type'
    )
    ftest(
        fobj,
        {key1:'test', key2:[{'name':'a', 'msg':5, 'type':RuntimeError}]},
        TypeError, 'Contract exception definition is of the wrong type'
    )
    ftest(
        fobj,
        {key1:'test', key2:[{'name':'a', 'msg':'b', 'type':5}]},
        TypeError, 'Contract exception definition is of the wrong type'
    )
    ftest(
        fobj,
        {
            key1:'test',
            key2:[{'name':'a', 'msg':'b'}, {'name':'a', 'msg':'c',}]
        },
        ValueError, 'Contract exception names are not unique'
    )
    ftest(
        fobj,
        {
            key1:'test',
            key2:[
                {'name':'a', 'msg':'desc'}, {'name':'b', 'msg':'desc',}
            ]
        },
        ValueError, 'Contract exception messages are not unique'
    )
    ftest(
        fobj,
        {
            key1:'test',
            key2:[
                {'name':'x', 'msg':'I am *[spartacus]*'},
                {'name':'y', 'msg':'A move is *[spartacus]*',}
            ]
        },
        ValueError,
        'Multiple replacement fields to be substituted by argument value'
    )
    putil.pcontracts._register_custom_contracts(
        contract_name='test1',
        contract_exceptions=[{'name':'a', 'msg':'desc'}]
    )
    putil.test.assert_exception(
        fobj,
        {
            'contract_name':'test1',
            'contract_exceptions':[{'name':'a', 'msg':'other desc'}]
        },
        RuntimeError,
        'Attempt to redefine custom contract `test1`'
    )
    # Test homogenization of exception definitions
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    fobj('test_contract1', 'my description')
    assert (
        putil.pcontracts._CUSTOM_CONTRACTS
        ==
        {
            'test_contract1':{
                'default':{
                    'num':0,
                    'msg':'my description',
                    'type':RuntimeError,
                    'field':None
                }
            }
        }
    )
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    fobj(
        'test_contract2',
        [
            {'name':'mex1', 'msg':'msg1', 'type':ValueError},
            {'name':'mex2', 'msg':'msg2 *[token_name]* hello world'}
        ]
    )
    assert (
        putil.pcontracts._CUSTOM_CONTRACTS
        ==
        {
            'test_contract2':{
                'mex1':{
                    'num':0,
                    'msg':'msg1',
                    'type':ValueError,
                    'field':None
                },
                'mex2':{
                    'num':1,
                    'msg':'msg2 *[token_name]* hello world',
                    'type':RuntimeError,
                    'field':'token_name'}
            }
        }
    )
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    fobj('test_contract3', [{'name':'mex1', 'msg':'msg1', 'type':ValueError}])
    fobj(
        'test_contract4',
        [{'name':'mex2', 'msg':'msg2 *[token_name]* hello world'}]
    )
    assert (
        putil.pcontracts._CUSTOM_CONTRACTS
        ==
        {
            'test_contract3': {
                'mex1':
                    {
                        'num':0,
                        'msg':'msg1',
                        'type':ValueError,
                        'field':None
                    }
            },
            'test_contract4':{
                'mex2':
                    {
                        'num':0,
                        'msg':'msg2 *[token_name]* hello world',
                        'type':RuntimeError,
                        'field':'token_name'
                    }
            }
        }
    )
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    fobj('test_contract5', {'name':'mex5', 'msg':'msg5', 'type':ValueError})
    assert (
        putil.pcontracts._CUSTOM_CONTRACTS
        ==
        {
            'test_contract5':{
                'mex5':{
                    'num':0,
                    'msg':'msg5',
                    'type':ValueError,
                    'field':None
                }
            }
        }
    )
    #putil.pcontracts._CUSTOM_CONTRACTS = dict()
    putil.pcontracts._CUSTOM_CONTRACTS = copy.deepcopy(
        original_custom_contracts
    )


def test_contract():
    """ Test contract decorator behavior """
    # pylint: disable=R0912,R0914
    original_custom_contracts = copy.deepcopy(
        putil.pcontracts._CUSTOM_CONTRACTS
    )
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    @putil.pcontracts.new_contract('Illegal number: *[number]*')
    def not_zero(number):
        exdesc = putil.pcontracts.get_exdesc()
        if number == 0:
            raise ValueError(exdesc)
        return True
    @putil.pcontracts.new_contract(
        wrong_file_name='The argument *[argument_name]* is wrong',
        file_not_found=(OSError, 'File name `*[file_name]*` not found')
    )
    def file_name_valid(name):
        exdesc = putil.pcontracts.get_exdesc()
        if name == 'a':
            raise ValueError(exdesc['wrong_file_name'])
        if name == 'b':
            raise ValueError(exdesc['file_not_found'])
        return True
    @putil.pcontracts.contract(number='int|float')
    def func1(number):
        return number
    @putil.pcontracts.contract(number='not_zero')
    def func2(number):
        if number == 1:
            raise TypeError('Unfathomable')
        return number
    @putil.pcontracts.contract(fname='str,file_name_valid', flag=bool)
    def func3(fname, fnumber, flag=False):
        return fname, fnumber
    @putil.pcontracts.new_contract('Illegal number: unity')
    def not_one(number):
        exdesc = putil.pcontracts.get_exdesc()
        if number == 1:
            raise ValueError(exdesc)
        return True
    @putil.pcontracts.contract(fname='not_a_valid_contract')
    def func6(fname):
        return fname
    putil.test.assert_exception(
        func1,
        {'number':'a string'},
        RuntimeError,
        'Argument `number` is not valid'
    )
    putil.test.assert_exception(
        func2,
        {'number':0},
        RuntimeError,
        'Illegal number: 0')
    putil.test.assert_exception(
        func2,
        {'number':1},
        TypeError,
        'Unfathomable'
    )
    putil.test.assert_exception(
        func3,
        {'fname':'a', 'fnumber':5, 'flag':False},
        RuntimeError,
        'The argument fname is wrong'
    )
    putil.test.assert_exception(
        func3,
        {'fname':'b', 'fnumber':5, 'flag':False},
        OSError,
        'File name `b` not found'
    )
    putil.test.assert_exception(
        func3,
        {'fname':'zzz', 'fnumber':5, 'flag':45},
        RuntimeError,
        'Argument `flag` is not valid'
    )
    with pytest.raises(TypeError) as excinfo:
        func2(2, 5, 10)
    ref = (
        'func2() takes exactly 1 argument (3 given)'
        if sys.version_info.major == 2 else
        'func2() takes 1 positional argument but 3 were given'
    )
    assert putil.test.get_exmsg(excinfo) == ref
    assert func1(5) == 5
    assert func2(10) == 10
    assert func3('hello', 'world', False) == ('hello', 'world')
    putil.exh.set_exh_obj(putil.exh.ExHandle())
    @putil.pcontracts.contract(fname='str,file_name_valid')
    def func4(fname, fnumber):
        return fname, fnumber
    @putil.pcontracts.contract(num='float|not_one', flag=bool, fudge='str|int')
    def func5(num, flag=True, fudge=5):
        return num
    # Register exceptions
    func4('x', 5)
    func5(0)
    exdict = putil.exh.get_exh_obj()._ex_dict
    pexlist = list()
    for exkey, exitem in exdict.items():
        pexlist.append(
            {
                'name':exkey[
                    exkey.rfind(
                        putil.exh.get_exh_obj()._callables_separator
                    )+1:
                ],
                'type':exitem['type'],
                'msg':exitem['msg']
            }
        )
    ref = [
        {
            'name':'contract_func5_flag_0',
            'type':RuntimeError, 'msg':'Argument `flag` is not valid'
        },
        {
            'name':'contract_func5_fudge_0',
            'type':RuntimeError,
            'msg':'Argument `fudge` is not valid'
        },
        {
            'name':'contract_func5_num_0',
            'type':RuntimeError,
            'msg':'Illegal number: unity'
        },
        {
            'name':'contract_func4_fname_0',
            'type':OSError,
            'msg':'File name `*[file_name]*` not found'
        },
        {
            'name':'contract_func4_fname_1',
            'type':RuntimeError,
            'msg':'The argument fname is wrong'
        }
    ]
    assert putil.test.comp_list_of_dicts(pexlist, ref)
    putil.test.assert_exception(
        func4,
        {'fname':'a', 'fnumber':5},
        RuntimeError,
        'The argument fname is wrong'
    )
    putil.test.assert_exception(
        func4,
        {'fname':'b', 'fnumber':5},
        OSError,
        'File name `b` not found'
    )
    putil.test.assert_exception(
        func5,
        {'num':1},
        RuntimeError,
        'Illegal number: unity'
    )
    putil.test.assert_exception(
        func5,
        {'num':1.0, 'flag':45},
        RuntimeError,
        'Argument `flag` is not valid'
    )
    putil.test.assert_exception(
        func5,
        {'num':1.0, 'fudge':1.0},
        RuntimeError,
        'Argument `fudge` is not valid'
    )
    putil.exh.del_exh_obj()
    putil.test.assert_exception(
        func6,
        {'fname':5},
        contracts.interface.ContractSyntaxError,
        ''
    )
    putil.pcontracts._CUSTOM_CONTRACTS = copy.deepcopy(
        original_custom_contracts
    )


def test_enable_disable_contracts():
    """
    Test wrappers around disable_all, enable_all and
    all_disabled functions behavior
    """
    @putil.pcontracts.contract(number=int)
    def func(number):
        return number
    assert not putil.pcontracts.all_disabled()
    putil.test.assert_exception(
        func,
        {'number':None},
        RuntimeError,
        'Argument `number` is not valid'
    )
    putil.pcontracts.disable_all()
    assert putil.pcontracts.all_disabled()
    # Contracts are disabled, no exception should be raised
    assert func(['a', 'b']) == ['a', 'b']
    putil.pcontracts.enable_all()
    assert not putil.pcontracts.all_disabled()
    putil.test.assert_exception(
        func,
        {'number':None},
        RuntimeError,
        'Argument `number` is not valid'
    )


def test_get_exdesc():
    """ Test get_exdesc function behavior """
    def sample_func_local():
        """ Local test function to test get_exdesc function behavior """
        tmp_local = putil.pcontracts.get_exdesc()
        return tmp_local
    sample_func_local.exdesc = 'Test local function property'
    sample_func_global.exdesc = 'Test global function property'
    assert sample_func_local() == 'Test local function property'
    assert sample_func_global() == 'Test global function property'
    del globals()['sample_func_global']
    putil.test.assert_exception(
        putil.pcontracts.get_exdesc,
        {},
        RuntimeError,
        'Function object could not be found for function `assert_exception`'
    )


def test_new_contract():
    """ Tests for new_contract decorator behavior """
    original_custom_contracts = copy.deepcopy(
        putil.pcontracts._CUSTOM_CONTRACTS
    )
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    @putil.pcontracts.new_contract()
    def func1(name1):
        return name1, putil.pcontracts.get_exdesc()
    ref = (
        'a',
        '[START CONTRACT MSG: func1]Argument `*[argument_name]*` '
        'is not valid[STOP CONTRACT MSG]'
    )
    assert func1('a') == ref
    ref = {
        'func1':{
            'argument_invalid':{
                'num':0,
                'msg':'Argument `*[argument_name]*` is not valid',
                'type':RuntimeError,
                'field':'argument_name'
            }
        }
    }
    assert putil.pcontracts._CUSTOM_CONTRACTS == ref
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    @putil.pcontracts.new_contract('Simple message')
    def func2(name2):
        return name2, putil.pcontracts.get_exdesc()
    ref = (
        'bc',
        '[START CONTRACT MSG: func2]Simple message[STOP CONTRACT MSG]'
    )
    assert func2('bc') == ref
    ref = {
        'func2':{
            'default':{
                'num':0,
                'msg':'Simple message',
                'type':RuntimeError,
                'field':None
            }
        }
    }
    assert putil.pcontracts._CUSTOM_CONTRACTS == ref
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    @putil.pcontracts.new_contract(
        ex1='Medium message',
        ex2=('Complex *[data]*', TypeError)
    )
    def func3(name3):
        return name3, putil.pcontracts.get_exdesc()
    ref = (
        'def',
        {
            'ex1':(
                '[START CONTRACT MSG: func3]'
                'Medium message'
                '[STOP CONTRACT MSG]'
            ),
            'ex2':(
                '[START CONTRACT MSG: func3]'
                'Complex *[data]*'
                '[STOP CONTRACT MSG]'
            )
        }
    )
    assert func3('def') == ref
    ref = {
        'func3':{
            'ex1':{
                'num':0,
                'msg':'Medium message',
                'type':RuntimeError,
                'field':None
            },
            'ex2':{
                'num':1,
                'msg':'Complex *[data]*',
                'type':TypeError,
                'field':'data'
            }
        }
    }
    assert putil.pcontracts._CUSTOM_CONTRACTS == ref
    putil.pcontracts._CUSTOM_CONTRACTS = copy.deepcopy(
        original_custom_contracts
    )


###
# Test classes
###
class TestCreateArgumentValuePairs(object):
    """ Tests for _create_argument_value_pairs function behavior """
    # pylint: disable=E1123,E1124,R0201,R0913
    def test_all_positional_arguments(self):
        """
        Test that function behaves properly when all arguments
        are positional arguments
        """
        @decfunc
        def orig_func_all_positional_arguments(ppar1, ppar2, ppar3):
            pass
        ref = {'ppar1':1, 'ppar2':2, 'ppar3':3}
        assert orig_func_all_positional_arguments(1, 2, 3) == ref

    def test_all_keyword_arguments(self):
        """
        Test that function behaves properly when all arguments are
        keyword arguments
        """
        @decfunc
        def orig_func_all_keyword_arguments(kpar1, kpar2, kpar3):
            pass
        ref = {'kpar1':1, 'kpar2':2, 'kpar3':3}
        assert (
            orig_func_all_keyword_arguments(kpar3=3, kpar2=2, kpar1=1)
            ==
            ref
        )

    def test_positional_and_keyword_arguments(self):
        """
        Test that function behaves properly when arguments are a mix of
        positional and keywords arguments
        """
        @decfunc
        def orig_func_positional_and_keyword_arguments(
            ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3
        ):
            pass
        ref = {
            'ppar1':10,
            'ppar2':20,
            'ppar3':30,
            'kpar1':[1, 2],
            'kpar2':1.5,
            'kpar3':'x'
        }
        assert (
            orig_func_positional_and_keyword_arguments(
                10, 20, 30, kpar2=1.5, kpar3='x', kpar1=[1, 2]
            )
            ==
            ref
        )

    def test_no_arguments(self):
        """
        Test that function behaves properly when there are no
        arguments passed
        """
        @decfunc
        def orig_func_no_arguments():
            pass
        assert orig_func_no_arguments() == {}

    def test_more_positional_arguments_passed_than_defined(self):
        """
        Test that function behaves properly when there are more arguments
        passed by position than in the function definition
        """
        @decfunc
        def orig_func(ppar1):
            pass
        assert orig_func(1, 2, 3) == {}

    def test_more_keyword_arguments_passed_than_defined(self):
        """
        Test that function behaves properly when there are more arguments
        passed by keyword than in the function definition
        """
        @decfunc
        def orig_func(kpar1=0, kpar2=2):
            pass
        assert orig_func(kpar1=1, kpar2=2, kpar3=3) == {}

    def test_argument_passed_by_position_and_keyword(self):
        """
        Test that function behaves properly when there are arguments passed
        both by position and keyword
        """
        @decfunc
        def orig_func(ppar1, ppar2, kpar1=1, kpar2=2):
            pass
        assert orig_func(1, 2, ppar1=5) == {}

    def test_default_arguments(self):
        """
        Test that function behaves properly when omitting keyword arguments
        that have defaults
        """
        @decfunc
        def orig_func(ppar1, ppar2, kpar1='a', kpar2=2):
            pass
        ref = {'ppar1':1, 'ppar2':2, 'kpar1':'a', 'kpar2':20}
        assert orig_func(1, 2, kpar2=20) == ref
