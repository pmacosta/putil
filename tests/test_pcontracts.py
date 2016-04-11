# test_pcontracts.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E1121,W0212,W0232,W0611,W0612,W0613

# Standard library imports
import copy
import functools
import sys
# PyPI imports
import contracts
import pytest
# Putil imports
import putil.exh
import putil.pcontracts
from putil.test import AE, AI, GET_EXMSG


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
    obj = putil.pcontracts._get_replacement_token
    ref = 'argument_name'
    assert obj('Argument `*[argument_name]*` could not be found') == ref
    assert obj('Argument `*file_name*` could not be found') is None


def test_format_arg():
    """ Test _format_arg function behavior """
    fobj = putil.pcontracts._format_arg
    assert fobj('Message') == {'msg':'Message', 'type':RuntimeError}
    assert fobj(OSError) == {
        'msg':'Argument `*[argument_name]*` is not valid', 'type':OSError
    }
    assert fobj((ValueError, 'Description 1')) == {
        'msg':'Description 1', 'type':ValueError
    }
    assert fobj(('Description 2', TypeError)) == {
        'msg':'Description 2', 'type':TypeError
    }


def test_format_arg_exceptions():
    """ Test _format_arg function exceptions """
    obj = putil.pcontracts._format_arg
    items = ['', [RuntimeError, ''], ['', RuntimeError], ['']]
    exmsg = 'Empty custom contract exception message'
    for item in items:
        AE(obj, ValueError, exmsg, arg=item)
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
    exmsg = 'Illegal custom contract exception definition'
    for item in items:
        AE(obj, TypeError, exmsg, arg=item)


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
    assert GET_EXMSG(excinfo) == 'Illegal custom contract exception definition'
    with pytest.raises(TypeError) as excinfo:
        fobj('Desc1', 'Desc2')
    assert GET_EXMSG(excinfo) == 'Illegal custom contract exception definition'
    with pytest.raises(TypeError) as excinfo:
        fobj(5)
    assert GET_EXMSG(excinfo) == 'Illegal custom contract exception definition'
    # Normal behavior
    assert fobj() == [
        {
            'name':'argument_invalid',
            'msg':'Argument `*[argument_name]*` is not valid',
            'type':RuntimeError
        }
    ]
    assert fobj('Desc') == [
        {
            'name':'default',
            'msg':'Desc',
            'type':RuntimeError
        }
    ]
    assert fobj(OSError) == [
        {
            'name':'default',
            'msg':'Argument `*[argument_name]*` is not valid',
            'type':OSError
        }
    ]
    assert fobj(('a', )) == [
        {'name':'default', 'msg':'a', 'type':RuntimeError}
    ]
    assert fobj((OSError, )) == [
        {
            'name':'default',
            'msg':'Argument `*[argument_name]*` is not valid',
            'type':OSError
        }
    ]
    assert fobj([TypeError, 'bcd']) == [
        {
            'name':'default', 'msg':'bcd', 'type':TypeError
        }
    ]
    assert fobj(['xyz', ValueError]) == [
        {
            'name':'default', 'msg':'xyz', 'type':ValueError
        }
    ]
    assert putil.test.comp_list_of_dicts(
        fobj(mycontract=('xyz', ValueError), othercontract=('abc', OSError)),
        [
            {'name':'othercontract', 'msg':'abc', 'type':OSError},
            {'name':'mycontract', 'msg':'xyz', 'type':ValueError}
        ]
    )
    # Validate **kwargs
    exmsg = 'Illegal custom contract exception definition'
    AE(fobj, TypeError, exmsg, a=45)
    ref = [
        {'name':'char', 'msg':'Desc1', 'type':RuntimeError},
        {'name':'other', 'msg':'a', 'type':ValueError}
    ]
    assert putil.test.comp_list_of_dicts(
        ref, fobj(char='Desc1', other=['a', ValueError])
    )


def test_register_custom_contracts():
    """ Test _register_custom_contracts function behavior """
    original_custom_contracts = copy.deepcopy(
        putil.pcontracts._CUSTOM_CONTRACTS
    )
    fobj = putil.pcontracts._register_custom_contracts
    key1 = 'contract_name'
    key2 = 'contract_exceptions'
    # Test data validation
    exmsg = 'Argument `contract_name` is of the wrong type'
    AE(fobj, TypeError, exmsg, **{key1:5, key2:{}})
    exmsg = 'Argument `contract_exceptions` is of the wrong type'
    AE(fobj, TypeError, exmsg, **{key1:'test', key2:5})
    exmsg = 'Contract exception definition is of the wrong type'
    AE(fobj, TypeError, exmsg, **{key1:'test', key2:{'msg':'b', 'key':'hole'}})
    AE(fobj, TypeError, exmsg, **{key1:'test', key2:[{5:'b'}]})
    AE(fobj, TypeError, exmsg, **{key1:'test', key2:[{'a':'b'}]})
    AE(
        fobj, TypeError, exmsg,
        **{key1:'test', key2:[{'name':'a', 'msg':'b', 'x':RuntimeError}]}
    )
    AE(
        fobj, TypeError, exmsg,
        **{key1:'test', key2:[{'name':5, 'msg':'b', 'type':RuntimeError}]}
    )
    AE(
        fobj, TypeError, exmsg,
        **{key1:'test', key2:[{'name':'a', 'msg':5, 'type':RuntimeError}]}
    )
    AE(
        fobj, TypeError, exmsg,
        **{key1:'test', key2:[{'name':'a', 'msg':'b', 'type':5}]}
    )
    exmsg = 'Contract exception names are not unique'
    AE(
        fobj, ValueError, exmsg,
        **{
            key1:'test',
            key2:[{'name':'a', 'msg':'b'}, {'name':'a', 'msg':'c',}]
        }
    )
    exmsg = 'Contract exception messages are not unique'
    AE(
        fobj, ValueError, exmsg,
        **{
            key1:'test',
            key2:[
                {'name':'a', 'msg':'desc'}, {'name':'b', 'msg':'desc',}
            ]
        }
    )
    exmsg = 'Multiple replacement fields to be substituted by argument value'
    AE(
        fobj, ValueError, exmsg,
        **{
            key1:'test',
            key2:[
                {'name':'x', 'msg':'I am *[spartacus]*'},
                {'name':'y', 'msg':'A move is *[spartacus]*',}
            ]
        }
    )
    putil.pcontracts._register_custom_contracts(
        contract_name='test1', contract_exceptions=[{'name':'a', 'msg':'desc'}]
    )
    exmsg = 'Attempt to redefine custom contract `test1`'
    AE(
        fobj, RuntimeError, exmsg,
        **{key1:'test1', key2:[{'name':'a', 'msg':'other desc'}]}
    )
    # Test homogenization of exception definitions
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    fobj('test_contract1', 'my description')
    assert putil.pcontracts._CUSTOM_CONTRACTS == {
        'test_contract1':{
            'default':{
                'num':0,
                'msg':'my description',
                'type':RuntimeError,
                'field':None
            }
        }
    }
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    fobj(
        'test_contract2',
        [
            {'name':'mex1', 'msg':'msg1', 'type':ValueError},
            {'name':'mex2', 'msg':'msg2 *[token_name]* hello world'}
        ]
    )
    assert putil.pcontracts._CUSTOM_CONTRACTS == {
        'test_contract2':{
            'mex1':{'num':0, 'msg':'msg1', 'type':ValueError, 'field':None},
            'mex2':{
                'num':1,
                'msg':'msg2 *[token_name]* hello world',
                'type':RuntimeError,
                'field':'token_name'}
        }
    }
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    fobj('test_contract3', [{'name':'mex1', 'msg':'msg1', 'type':ValueError}])
    fobj(
        'test_contract4',
        [{'name':'mex2', 'msg':'msg2 *[token_name]* hello world'}]
    )
    assert putil.pcontracts._CUSTOM_CONTRACTS == {
        'test_contract3': {
            'mex1':
                {'num':0, 'msg':'msg1', 'type':ValueError, 'field':None}
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
    putil.pcontracts._CUSTOM_CONTRACTS = dict()
    fobj('test_contract5', {'name':'mex5', 'msg':'msg5', 'type':ValueError})
    assert putil.pcontracts._CUSTOM_CONTRACTS == {
        'test_contract5':{
            'mex5':{'num':0, 'msg':'msg5', 'type':ValueError, 'field':None}
        }
    }
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
    @putil.pcontracts.contract(value=int)
    def func7(value):
        return value
    AI(func1, 'number', number='a string')
    AE(func2, RuntimeError, 'Illegal number: 0', number=0)
    AE(func2, TypeError, 'Unfathomable', number=1)
    exmsg = 'The argument fname is wrong'
    AE(func3, RuntimeError, exmsg, fname='a', fnumber=5, flag=False)
    exmsg = 'File name `b` not found'
    AE(func3, OSError, exmsg, fname='b', fnumber=5, flag=False)
    exmsg = 'Argument `flag` is not valid'
    AE(func3, RuntimeError, exmsg, fname='zzz', fnumber=5, flag=45)
    with pytest.raises(TypeError) as excinfo:
        func2(2, 5, 10)
    ref = (
        'func2() takes exactly 1 argument (3 given)'
        if sys.hexversion < 0x03000000 else
        'func2() takes 1 positional argument but 3 were given'
    )
    assert GET_EXMSG(excinfo) == ref
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
    exdict = putil.exh.get_exh_obj()._flatten_ex_dict()
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
            'name':'contract:tests.test_pcontracts.func5.flag_0',
            'type':RuntimeError, 'msg':'Argument `flag` is not valid'
        },
        {
            'name':'contract:tests.test_pcontracts.func5.fudge_0',
            'type':RuntimeError,
            'msg':'Argument `fudge` is not valid'
        },
        {
            'name':'contract:tests.test_pcontracts.func5.num_0',
            'type':RuntimeError,
            'msg':'Illegal number: unity'
        },
        {
            'name':'contract:tests.test_pcontracts.func4.fname_0',
            'type':OSError,
            'msg':'File name `*[file_name]*` not found'
        },
        {
            'name':'contract:tests.test_pcontracts.func4.fname_1',
            'type':RuntimeError,
            'msg':'The argument fname is wrong'
        }
    ]
    assert putil.test.comp_list_of_dicts(pexlist, ref)
    exmsg = 'The argument fname is wrong'
    AE(func4, RuntimeError, exmsg, fname='a', fnumber=5)
    AE(func4, OSError, 'File name `b` not found', fname='b', fnumber=5)
    AE(func5, RuntimeError, 'Illegal number: unity', num=1)
    AI(func5, 'flag', num=1.0, flag=45)
    AI(func5, 'fudge', num=1.0, fudge=1.0)
    putil.exh.del_exh_obj()
    AE(func6, contracts.interface.ContractSyntaxError, '', fname=5)
    AI(func7, 'value', value='a')
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
    AI(func, 'number', number=None)
    putil.pcontracts.disable_all()
    assert putil.pcontracts.all_disabled()
    # Contracts are disabled, no exception should be raised
    assert func(['a', 'b']) == ['a', 'b']
    putil.pcontracts.enable_all()
    assert not putil.pcontracts.all_disabled()
    AI(func, 'number', number=None)


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
    exmsg = (
        'Function object could not be found for function `assert_exception`'
    )
    AE(putil.pcontracts.get_exdesc, RuntimeError, exmsg)


def test_new_contract():
    """ Tests for new_contract decorator behavior """
    # pylint: disable=R0204
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
        assert orig_func_all_keyword_arguments(kpar3=3, kpar2=2, kpar1=1) == {
            'kpar1':1, 'kpar2':2, 'kpar3':3
        }

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
        assert orig_func_positional_and_keyword_arguments(
            10, 20, 30, kpar2=1.5, kpar3='x', kpar1=[1, 2]
        ) == ref

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
