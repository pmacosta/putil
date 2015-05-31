# test_exh.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,F0401,R0903,R0915,W0212,W0612,W0640

import copy
import mock
import os
import pytest
import re
import sys
from itertools import product

import putil.eng
import putil.exh
import putil.misc
import putil.pcontracts
import putil.test
TEST_DIR = os.path.dirname(__file__)
SUPPORT_DIR = os.path.join(TEST_DIR, 'support')
sys.path.append(SUPPORT_DIR)
import exh_support_module_1

###
# Tests
###
def test_star_exh_obj():
	""" Test [get|set|del]_exh_obj() function """
	putil.test.assert_exception(
		putil.exh.set_exh_obj,
		{'obj':5},
		RuntimeError,
		'Argument `obj` is not valid'
	)
	exobj = putil.exh.ExHandle()
	putil.exh.set_exh_obj(exobj)
	assert id(putil.exh.get_exh_obj()) == id(exobj)
	putil.exh.del_exh_obj()
	assert putil.exh.get_exh_obj() is None
	# Test that nothing happens if del_exh_obj is called when there
	# is no global object handler set
	putil.exh.del_exh_obj()
	new_exh_obj = putil.exh.get_or_create_exh_obj()
	assert id(new_exh_obj) != id(exobj)
	assert not new_exh_obj._full_cname
	assert id(putil.exh.get_or_create_exh_obj(True)) == id(new_exh_obj)
	assert not new_exh_obj._full_cname
	putil.exh.del_exh_obj()
	new_exh_obj = putil.exh.get_or_create_exh_obj(True)
	assert new_exh_obj._full_cname
	putil.exh.del_exh_obj()
	putil.test.assert_exception(
		putil.exh.get_or_create_exh_obj,
		{'full_cname':5},
		RuntimeError,
		'Argument `full_cname` is not valid'
	)


def test_ex_type_str():
	""" test _ex_type_str() function """
	assert putil.exh._ex_type_str(RuntimeError) == 'RuntimeError'
	assert putil.exh._ex_type_str(IOError) == 'IOError'


def test_init_errors():
	""" Test __init__() method errors """
	putil.test.assert_exception(
		putil.exh.ExHandle,
		{'full_cname':5},
		RuntimeError,
		'Argument `full_cname` is not valid'
	)
	putil.test.assert_exception(
		putil.exh.ExHandle,
		{'exclude':5},
		RuntimeError,
		'Argument `exclude` is not valid'
	)
	putil.test.assert_exception(
		putil.exh.ExHandle,
		{'exclude':['p', 'a', 5, 'c']},
		RuntimeError,
		'Argument `exclude` is not valid'
	)
	putil.test.assert_exception(
		putil.exh.ExHandle,
		{'exclude':['sys', '_not_a_module_']},
		ValueError,
		'Source for module _not_a_module_ could not be found'
	)
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


def test_add_exception_errors():
	""" Test add_exception() function errors """
	for full_cname in [True, False]:
		obj = putil.exh.ExHandle(full_cname)
		putil.test.assert_exception(
			obj.add_exception,
			{'exname':5, 'extype':RuntimeError, 'exmsg':'Message'},
			RuntimeError,
			'Argument `exname` is not valid'
		)
		putil.test.assert_exception(
			obj.add_exception,
			{'exname':'exception', 'extype':5, 'exmsg':'Message'},
			RuntimeError,
			'Argument `extype` is not valid'
		)
		putil.test.assert_exception(
			obj.add_exception,
			{'exname':'exception', 'extype':RuntimeError, 'exmsg':True},
			RuntimeError,
			'Argument `exmsg` is not valid'
		)
		# These should not raise an exception
		obj = putil.exh.ExHandle(full_cname)
		obj.add_exception(
			exname='exception name',
			extype=RuntimeError,
			exmsg='exception message for exception #1'
		)
		obj.add_exception(
			exname='exception name',
			extype=TypeError,
			exmsg='exception message for exception #2'
		)


def test_add_exception_works():
	""" Test add_exception() function works """
	# pylint: disable=E0602,R0201,R0912,R0914,W0122,W0613
	exobj = putil.exh.ExHandle(
		full_cname=True,
		exclude=['_pytest', 'tests.test_exh']
	)
	assert exobj.exceptions_db == []
	combinations = product([True, False], [None, ['_pytest', 'execnet']])
	for full_cname, exclude in combinations:
		exobj = putil.exh.ExHandle(full_cname=full_cname, exclude=exclude)
		def func1():
			exobj.add_exception(
				'first_exception',
				TypeError,
				'This is the first exception'
			)
			print "Hello"
		def prop_decorator(func):
			return func
		@putil.pcontracts.contract(text=str)
		@prop_decorator
		def func2(text):
			exobj.add_exception(
				'second_exception',
				ValueError,
				'This is the second exception'
			)
			exobj.add_exception(
				'third_exception',
				IOError,
				'This is the third exception'
			)
			print text
		class Class1(object):
			def __init__(self, exobj):
				self._value = None
				self._exobj = exobj
			@property
			def value3(self):
				self._exobj.add_exception(
					'getter_exception',
					TypeError,
					'Get function exception'
				)
				return self._value
			@value3.setter
			@putil.pcontracts.contract(value=int)
			def value3(self, value):
				self._exobj.add_exception(
					'setter_exception',
					TypeError,
					'Set function exception'
				)
				self._value = value
			@value3.deleter
			def value3(self):
				self._exobj.add_exception(
					'deleter_exception',
					TypeError,
					'Delete function exception'
				)
				print 'Cannot delete attribute'
			def _get_value4_int(self):
				self._exobj.add_exception(
					'dummy_exception',
					IOError,
					'Pass-through exception'
				)
				return self._value
			def _get_value4(self):
				return self._get_value4_int()
			value4 = property(_get_value4)
		def func7():
			exobj.add_exception('total_exception_7', TypeError, 'Total exception #7')
		def func8():
			exobj.add_exception('total_exception_8', TypeError, 'Total exception #8')
		def func9():
			exobj.add_exception('total_exception_9', TypeError, 'Total exception #9')
		def func10():
			exobj.add_exception('total_exception_10', TypeError, 'Total exception #10')
		def func11():
			exobj.add_exception('total_exception_11', TypeError, 'Total exception #11')
		def func12():
			exobj.add_exception('total_exception_12', TypeError, 'Total exception #12')
		def func13():
			exobj.add_exception('total_exception_13', TypeError, 'Total exception #13')
		def func14():
			exobj.add_exception('total_exception_14', TypeError, 'Total exception #14')
		exec compile(
			"def func15(exobj):"
			"	exobj.add_exception("
			"		'total_exception_15',"
			"		TypeError,"
			"		'Total exception #15'"
			"	)",
			'<exec_function>',
			'exec'
		) in locals()
		dobj = Class1(exobj)
		dobj.value3 = 5
		print dobj.value3
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
		if not cdb:
			assert False
		for exname in cdb:
			erec = cdb[exname]
			if full_cname and exclude:
				if re.compile(r'\d+/first_exception').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func1',
						TypeError,
						'This is the first exception'
					)
				elif re.compile(r'\d+/second_exception').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func2',
						ValueError,
						'This is the second exception'
					)
				elif re.compile(r'\d+/third_exception').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func2',
						IOError,
						'This is the third exception'
					)
				elif re.compile(r'\d+/setter_exception').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.Class1.value3(setter)',
						TypeError,
						'Set function exception'
					)
				elif re.compile(r'\d+/getter_exception').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.Class1.value3(getter)',
						TypeError,
						'Get function exception'
					)
				elif re.compile(r'\d+/deleter_exception').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.Class1.value3(deleter)',
						TypeError,
						'Delete function exception'
					)
				elif re.compile(r'\d+/total_exception_7').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func7',
						TypeError,
						'Total exception #7'
					)
				elif re.compile(r'\d+/total_exception_8').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func8',
						TypeError,
						'Total exception #8'
					)
				elif re.compile(r'\d+/total_exception_9').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func9',
						TypeError,
						'Total exception #9'
					)
				elif re.compile(r'\d+/total_exception_10').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func10',
						TypeError,
						'Total exception #10'
					)
				elif re.compile(r'\d+/total_exception_11').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func11',
						TypeError,
						'Total exception #11'
					)
				elif re.compile(r'\d+/total_exception_12').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func12',
						TypeError,
						'Total exception #12'
					)
				elif re.compile(r'\d+/total_exception_13').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func13',
						TypeError,
						'Total exception #13'
					)
				elif re.compile(r'\d+/total_exception_14').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.func14',
						TypeError,
						'Total exception #14'
					)
				elif re.compile(r'\d+/total_exception_15').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works',
						TypeError,
						'Total exception #15'
					)
				elif re.compile(r'\d+/total_exception_16').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/'
						'exh_support_module_1.func16',
						TypeError,
						'Total exception #16'
					)
				elif re.compile(r'\d+/dummy_exception').match(exname):
					ttuple = (
						'tests.test_exh.test_add_exception_works/tests.test_exh.'
						'test_add_exception_works.Class1.value4(getter)',
						IOError,
						'Pass-through exception'
					)
				else:
					assert False
				assert erec['function'][0] == ttuple[0]
				assert erec['type'] == ttuple[1]
				assert erec['msg'] == ttuple[2]
			else:
				if re.compile(r'\d+/first_exception').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func1',
						TypeError,
						'This is the first exception'
					)
				elif re.compile(r'\d+/second_exception').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func2',
						ValueError,
						'This is the second exception'
					)
				elif re.compile(r'\d+/third_exception').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func2',
						IOError,
						'This is the third exception'
					)
				elif re.compile(r'\d+/setter_exception').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.Class1.'
						r'value3\(setter\)',
						TypeError,
						'Set function exception'
					)
				elif re.compile(r'\d+/getter_exception').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.Class1.'
						r'value3\(getter\)',
						TypeError,
						'Get function exception'
					)
				elif re.compile(r'\d+/deleter_exception').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.Class1.'
						r'value3\(deleter\)',
						TypeError,
						'Delete function exception'
					)
				elif re.compile(r'\d+/total_exception_7').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func7',
						TypeError,
						'Total exception #7'
					)
				elif re.compile(r'\d+/total_exception_8').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func8',
						TypeError,
						'Total exception #8'
					)
				elif re.compile(r'\d+/total_exception_9').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func9',
						TypeError,
						'Total exception #9'
					)
				elif re.compile(r'\d+/total_exception_10').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func10',
						TypeError,
						'Total exception #10'
					)
				elif re.compile(r'\d+/total_exception_11').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func11',
						TypeError,
						'Total exception #11'
					)
				elif re.compile(r'\d+/total_exception_12').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func12',
						TypeError,
						'Total exception #12'
					)
				elif re.compile(r'\d+/total_exception_13').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func13',
						TypeError,
						'Total exception #13'
					)
				elif re.compile(r'\d+/total_exception_14').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.func14',
						TypeError,
						'Total exception #14'
					)
				elif re.compile(r'\d+/total_exception_15').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works',
						TypeError,
						'Total exception #15'
					)
				elif re.compile(r'\d+/total_exception_16').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works/'
						'exh_support_module_1.func16',
						TypeError,
						'Total exception #16'
					)
				elif re.compile(r'\d+/dummy_exception').match(exname):
					ttuple = (
						r'.+/tests.test_exh.test_add_exception_works.Class1.'
						r'value4\(getter\)',
						IOError,
						'Pass-through exception'
					)
				else:
					assert False
				if not full_cname:
					assert erec['function'][0] is None
				else:
					assert re.compile(ttuple[0])
				assert erec['type'] == ttuple[1]
				assert erec['msg'] == ttuple[2]
		# Test that function IDs are unique
		repeated_found = False
		exlist = []
		for exname in cdb:
			if ((exname.endswith('/second_exception') or
	            exname.endswith('/third_exception')) and
	           (not repeated_found)):
				func_id = exname.split('/')[0]
				repeated_found = True
				exlist.append(func_id)
			elif (exname.endswith('/second_exception') or
			     exname.endswith('/third_exception')):
				if exname.split('/')[0] != func_id:
					assert False
			else:
				exlist.append(exname.split('/')[0])
		assert len(set(exlist)) == len(exlist)
		# Test that exec code gets correctly flagged
		frobj = sys._getframe(0)
		assert exobj._get_callable_full_name(frobj, '<module>', None) == 'dynamic'
		# Test what happens when top of stack is reached
		exobj = putil.exh.ExHandle(full_cname=True, exclude=['_pytest'])
		def func_f():
			exobj.add_exception('total_exception_F', TypeError, 'Total exception #F')
		frobj = sys._getframe(0)
		def mock_get_frame(num):
			if num < 4:
				return frobj
			raise ValueError('Top of the stack')
		with mock.patch('putil.exh.sys._getframe', side_effect=mock_get_frame):
			func_f()
		ecb = exobj._ex_dict
		exname = ecb.keys()[0]
		erec = ecb[exname]
		ref = sorted(
				{
					'function': [
						'tests.test_exh.test_add_exception_works/'
						'tests.test_exh.test_add_exception_works/'
						'tests.test_exh.test_add_exception_works/'
						'tests.test_exh.test_add_exception_works'],
					'type':TypeError,
					'msg':'Total exception #F'
				}.items()
			  )
		assert re.compile(r'\d+/total_exception_F').match(exname)
		assert sorted(erec.items()) == ref
		# Test property search
		exobj = putil.exh.ExHandle(full_cname=True, exclude=['_pytest'])
		class MyClass(object):
			def __init__(self, exobj):
				exobj.add_exception('class_exception', OSError, 'Init exception')
		_ = MyClass(exobj)
		ecb = exobj._ex_dict
		exname = ecb.keys()[0]
		erec = ecb[exname]
		ref = sorted(
				{
					'function':[
						'tests.test_exh.test_add_exception_works/'
						'tests.test_exh.test_add_exception_works.MyClass.__init__'],
					'type':OSError,
					'msg':'Init exception'
				}.items()
			  )
		assert re.compile(r'\d+/class_exception').match(exname)
		assert sorted(erec.items()) == ref
	###
	# Test case where callable is dynamic and does not have a code ID
	###
	def mock_get_code_id_from_obj(obj):
		""" Return unique identity tuple to individualize callable object """
		return None
	assert putil.exh._get_code_id_from_obj(None) is None
	obj = putil.exh.ExHandle(True)
	exec 'def efunc(): pass' in locals()
	fobj = efunc
	patch_name = 'putil.exh._get_code_id_from_obj'
	patch_obj = mock_get_code_id_from_obj
	with mock.patch(patch_name, side_effect=patch_obj):
		frobj = sys._getframe(0)
		assert obj._get_callable_full_name(frobj, '<module>', fobj) == 'dynamic'
	###
	# Test exclude: test without exclusion and with exclusion,
	# the function name should be 'None'
	###
	# Test with function that has a contract decorator
	putil.exh.set_exh_obj(
		putil.exh.ExHandle(
			full_cname=True,
			exclude=['_pytest']
		)
	)
	_ = putil.eng.peng(15, 3, False)
	for item in putil.exh.get_exh_obj()._ex_dict.values():
		assert item['function'][0]
	putil.exh.set_exh_obj(
		putil.exh.ExHandle(
			full_cname=True,
			exclude=['_pytest', 'putil.eng']
		)
	)
	_ = putil.eng.peng(15, 3, False)
	for item in putil.exh.get_exh_obj()._ex_dict.values():
		assert not item['function'][0]
	# Test with function that has an exception in body
	import tests.support.exh_support_module_1
	putil.exh.set_exh_obj(
		putil.exh.ExHandle(
			full_cname=True,
			exclude=['_pytest']
		)
	)
	tests.support.exh_support_module_1.simple_exception()
	for item in putil.exh.get_exh_obj()._ex_dict.values():
		assert item['function'][0]
	putil.exh.set_exh_obj(
		putil.exh.ExHandle(
			full_cname=True,
			exclude=['_pytest',
			'tests.support.exh_support_module_1']
		)
	)
	tests.support.exh_support_module_1.simple_exception()
	for item in putil.exh.get_exh_obj()._ex_dict.values():
		assert not item['function'][0]


def test_raise_exception():
	""" Test raise_exception_if() function errors """
	obj = putil.exh.ExHandle()
	def func3(cond1=False, cond2=False, cond3=False, cond4=False):
		exobj = putil.exh.ExHandle()
		exobj.add_exception(
			'my_exception1',
			RuntimeError,
			'This is an exception'
		)
		exobj.add_exception(
			'my_exception2',
			IOError,
			'This is an exception with a *[fname]* field'
		)
		exobj.raise_exception_if(
			'my_exception1',
			cond1,
			edata=None
		)
		exobj.raise_exception_if(
			'my_exception2',
			cond2,
			edata={'field':'fname', 'value':'my_file.txt'}
		)
		if cond3:
			exobj.raise_exception_if('my_exception3', False)
		if cond4:
			exobj.raise_exception_if(
				'my_exception2',
				cond4,
				edata={'field':'not_a_field', 'value':'my_file.txt'}
			)
		return exobj
	putil.test.assert_exception(
		obj.raise_exception_if,
		{'exname':5, 'condition':False},
		RuntimeError,
		'Argument `exname` is not valid'
	)
	putil.test.assert_exception(
		obj.raise_exception_if,
		{'exname':'my_exception', 'condition':5},
		RuntimeError,
		'Argument `condition` is not valid'
	)
	putil.test.assert_exception(
		obj.raise_exception_if,
		{'exname':'my_exception', 'condition':False, 'edata':354},
		RuntimeError,
		'Argument `edata` is not valid'
	)
	putil.test.assert_exception(
		obj.raise_exception_if,
		{'exname':'my_exception', 'condition':False, 'edata':{'field':'my_field'}},
		RuntimeError,
		'Argument `edata` is not valid'
	)
	putil.test.assert_exception(
		obj.raise_exception_if,
		{'exname':'my_exception', 'condition':False, 'edata':{'field':3, 'value':5}},
		RuntimeError,
		'Argument `edata` is not valid'
	)
	putil.test.assert_exception(
		obj.raise_exception_if,
		{'exname':'my_exception', 'condition':False, 'edata':{'value':5}},
		RuntimeError,
		'Argument `edata` is not valid'
	)
	putil.test.assert_exception(
		obj.raise_exception_if,
		{
			'exname':'my_exception',
			'condition':False,
			'edata':[{'field':'my_field1', 'value':5}, {'field':'my_field'}]
		},
		RuntimeError,
		'Argument `edata` is not valid'
	)
	putil.test.assert_exception(
		obj.raise_exception_if,
		{
			'exname':'my_exception', 'condition':False,
			'edata':[{'field':'my_field1', 'value':5}, {'field':3, 'value':5}]
		},
		RuntimeError,
		'Argument `edata` is not valid'
	)
	putil.test.assert_exception(
		obj.raise_exception_if,
		{
			'exname':'my_exception',
			'condition':False,
			'edata':[{'field':'my_field1', 'value':5}, {'value':5}]
		},
		RuntimeError,
		'Argument `edata` is not valid'
	)
	putil.test.assert_exception(
		func3,
		{'cond1':True, 'cond2':False},
		RuntimeError,
		'This is an exception'
	)
	putil.test.assert_exception(
		func3,
		{'cond2':True},
		IOError,
		'This is an exception with a my_file.txt field'
	)
	putil.test.assert_exception(
		func3,
		{'cond3':True},
		ValueError,
		'Exception name my_exception3 not found'
	)
	putil.test.assert_exception(
		func3,
		{'cond4':True},
		RuntimeError,
		'Field not_a_field not in exception message'
	)
	exobj = func3()	# Test that edata=None works
	cdb = exobj._ex_dict
	if not cdb:
		assert False
	for exname, erec in cdb.items():
		if exname.endswith('/test_exh.test_raise_exception.func3.my_exception1'):
			assert erec['function'].endswith('test_exh.test_raise_exception.func3')
			assert erec['type'] == RuntimeError
			assert erec['msg'] == 'This is an exception'
		if exname.endswith('/test_exh.test_raise_exception.func3.my_exception2'):
			assert erec['function'].endswith('test_exh.test_raise_exception.func3')
			assert erec['type'] == IOError
			assert erec['msg'] == 'This is an exception with a *[fname]* field'


def test_exceptions_db():
	""" Test _exceptions_db() property """
	for full_cname in [True, False]:
		# Functions definitions
		def func4(exobj):
			exobj.add_exception(
				'my_exception1',
				RuntimeError,
				'This is exception #1'
			)
		def func5(exobj):
			exobj.add_exception(
				'my_exception2',
				ValueError,
				'This is exception #2, *[result]*'
			)
			exobj.add_exception(
				'my_exception3',
				TypeError,
				'This is exception #3'
			)
		exobj = putil.exh.ExHandle(full_cname)
		func4(exobj)
		func5(exobj)
		# Actual tests
		# Test that property cannot be deleted
		with pytest.raises(AttributeError) as excinfo:
			del exobj.exceptions_db
		assert excinfo.value.message == "can't delete attribute"
		# Test contents
		tdata_in = exobj.exceptions_db
		if (not tdata_in) or (len(tdata_in) != 3):
			assert False
		tdata_out = list()
		regtext1 = r'[\w|\W]+/tests.test_exh.test_exceptions_db.func4'
		regtext2 = r'[\w|\W]+/tests.test_exh.test_exceptions_db.func5'
		for erec in tdata_in:
			name = None
			if full_cname:
				if re.compile(regtext1).match(erec['name']):
					name = 'tests.test_exh.test_exceptions_db.func4'
				elif re.compile(regtext2).match(erec['name']):
					name = 'tests.test_exh.test_exceptions_db.func5'
			else:
				if re.compile(r'\d+/my_exception1').match(erec['name']):
					name = 'tests.test_exh.test_exceptions_db.func4'
				elif re.compile(r'\d+/my_exception[2-3]').match(erec['name']):
					name = 'tests.test_exh.test_exceptions_db.func5'
			if not name:
				print 'NOT FOUND'
				assert False
			tdata_out.append({'name':name, 'data':erec['data']})
		ref = sorted([
				{
					'name':'tests.test_exh.test_exceptions_db.func4',
					'data':'RuntimeError (This is exception #1)'
				},
				{
					'name':'tests.test_exh.test_exceptions_db.func5',
					'data':'ValueError (This is exception #2, *[result]*)'
				},
				{
					'name':'tests.test_exh.test_exceptions_db.func5',
					'data':'TypeError (This is exception #3)'
				}
			  ])
		assert sorted(tdata_out) == ref


def test_callables_db():
	""" Test callables_db property """
	# Function definitions
	def func6(exobj):
		exobj.add_exception('my_exception', RuntimeError, 'This is an exception')
		return exobj
	# Actual tests
	exobj = func6(putil.exh.ExHandle())
	# Actual contents of what is returned should be checked in pinspect module
	assert exobj.callables_db is not None
	# Test that property cannot be deleted
	with pytest.raises(AttributeError) as excinfo:
		del exobj.callables_db
	assert excinfo.value.message == "can't delete attribute"


def test_callables_separator():
	""" Test callables_separator property """
	exobj = putil.exh.ExHandle()
	# Actual contents of what is returned should be checked in pinspect module
	assert exobj.callables_separator == '/'
	# Test that property cannot be deleted
	with pytest.raises(AttributeError) as excinfo:
		del exobj.callables_separator
	assert excinfo.value.message == "can't delete attribute"


def test_str():
	""" Test str() function """
	for full_cname in [True, False]:
		# Functions definition
		def func7(exobj):
			exobj.add_exception(
				'my_exception7',
				RuntimeError,
				'This is exception #7'
			)
			exobj.raise_exception_if('my_exception7', False)
		def func8(exobj):
			exobj.add_exception(
				'my_exception8',
				ValueError,
				'This is exception #8, *[fname]*'
			)
			exobj.add_exception(
				'my_exception9',
				TypeError,
				'This is exception #9'
			)
		exobj = putil.exh.ExHandle(full_cname)
		func7(exobj)
		func8(exobj)
		# Actual tests
		str_in = str(exobj).split('\n\n')
		str_out = list()
		for str_element in str_in:
			str_list = str_element.split('\n')
			if str_list[0].endswith('/my_exception7'):
				str_list[0] = 'Name    : test_exh.test_str.func7/my_exception7'
			elif str_list[0].endswith('/my_exception8'):
				str_list[0] = 'Name    : test_exh.test_str.func8/my_exception8'
			elif str_list[0].endswith('/my_exception9'):
				str_list[0] = 'Name    : test_exh.test_str.func8/my_exception9'
			if str_list[1].endswith('test_exh.test_str.func7'):
				str_list[1] = 'Function: {0}'.format(
					'test_exh.test_str.func7' if full_cname else 'None'
				)
			elif str_list[1].endswith('test_exh.test_str.func8'):
				str_list[1] = 'Function: {0}'.format(
					'test_exh.test_str.func8' if full_cname else 'None'
				)
			str_out.append('\n'.join(str_list))
		#
		str_check = list()
		str_check.append(
			'Name    : test_exh.test_str.func7/my_exception7\n'
			'Function: '+('test_exh.test_str.func7' if full_cname else 'None')+'\n'
			'Type    : RuntimeError\n'
			'Message : This is exception #7'
		)
		str_check.append(
			'Name    : test_exh.test_str.func8/my_exception8\n'
			'Function: '+('test_exh.test_str.func8' if full_cname else 'None')+'\n'
			'Type    : ValueError\n'
			'Message : This is exception #8, *[fname]*'
		)
		str_check.append(
			'Name    : test_exh.test_str.func8/my_exception9\n'
			'Function: '+('test_exh.test_str.func8' if full_cname else 'None')+'\n'
			'Type    : TypeError\n'
			'Message : This is exception #9'
		)
		assert sorted(str_out) == sorted(str_check)


def test_copy():
	""" Test __copy__() magic method """
	# Functions definition
	def funca(exobj):
		exobj.add_exception('my_exceptionA', RuntimeError, 'This is exception #A')
	def funcb(exobj):
		exobj.add_exception('my_exceptionB', ValueError, 'This is exception #B')
		exobj.add_exception('my_exceptionC', TypeError, 'This is exception #C')
	class Clsc(object):
		def __init__(self, exobj):
			self._exobj = exobj
			self._value = None
		def _set_value(self, value):
			self._exobj.add_exception('my_exceptionD', IOError, 'This is exception #D')
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
	assert source_obj._full_cname == dest_obj._full_cname
	assert sorted(source_obj.exceptions_db) == sorted(dest_obj.exceptions_db)


def test_multiple_paths_to_same_exception():
	"""
	Test that different paths to a single exception definition do not
	overwrite each other
	"""
	def exdef(obj):
		obj.add_exception('my_exception', RuntimeError, 'This is the exception')
	def funca(obj):
		exdef(obj)
	def funcb(obj):
		exdef(obj)
	exobj = putil.exh.ExHandle(full_cname=True)
	funca(exobj)
	funcb(exobj)
	exdb = sorted(exobj.exceptions_db)
	assert len(exdb) == 2
	assert exdb[0]['data'] == 'RuntimeError (This is the exception)'
	assert exdb[1]['data'] == 'RuntimeError (This is the exception)'
	assert exdb[0]['name'].endswith(
		'tests.test_exh.test_multiple_paths_to_same_exception/'
		'tests.test_exh.test_multiple_paths_to_same_exception.funca/'
		'tests.test_exh.test_multiple_paths_to_same_exception.exdef'
	)
	assert exdb[1]['name'].endswith(
		'tests.test_exh.test_multiple_paths_to_same_exception/'
		'tests.test_exh.test_multiple_paths_to_same_exception.funcb/'
		'tests.test_exh.test_multiple_paths_to_same_exception.exdef'
	)
	str_in = putil.misc.flatten_list([
		item.split('\n') for item in str(exobj).split('\n\n')
	])
	fstring = (
		'tests.test_exh.test_multiple_paths_to_same_exception/'
		'tests.test_exh.test_multiple_paths_to_same_exception.func{0}/'
		'tests.test_exh.test_multiple_paths_to_same_exception.exdef'
	)
	assert str_in[0].endswith('/my_exception')
	assert str_in[1].startswith('Function: ')
	assert (str_in[1].endswith(fstring.format('a')) or
		   str_in[1].endswith(fstring.format('b')))
	assert str_in[2].startswith('          ')
	assert str_in[2].endswith(fstring.format(
		'a' if str_in[1].endswith(fstring.format('b')) else 'b'
	))
	assert str_in[3] == 'Type    : RuntimeError'
	assert str_in[4] == 'Message : This is the exception'

def test_add():
	""" Test __add__() function """
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
	obj1._callables_obj._fnames = ['hello']
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
	obj2._callables_obj._fnames = ['world']
	obj2._callables_obj._module_names = ['a', 'test']
	obj2._callables_obj._class_names = ['a', 'time']
	#
	sobj = obj1+obj2
	assert sorted(sobj._ex_dict) == sorted(
		{'id1':5, 'ssid1':10, 'id2':3, 'ssid2':1}
	)
	assert sorted(sobj._callables_obj._callables_db) == sorted({
		'call1':{'a':5, 'b':6},
		'call2':{'a':7, 'b':8},
		'call3':{'a':10, 'b':100},
		'call4':{'a':200, 'b':300}
	})
	assert sorted(sobj._callables_obj._reverse_callables_db) == sorted(
		{'rc1':5, 'rc2':7, 'rc3':0, 'rc4':-1}
	)
	assert sorted(sobj._callables_obj._modules_dict) == sorted(
		{'key1':'alpha', 'key2':'beta', 'key3':'pi', 'key4':'gamma'}
	)
	assert sorted(sobj._callables_obj._fnames) == sorted(['hello', 'world'])
	assert sorted(sobj._callables_obj._module_names) == sorted(
		['this', 'is', 'a', 'test']
	)
	assert sorted(sobj._callables_obj._class_names) == sorted(
		['once', 'upon', 'a', 'time']
	)
	#
	obj1 += obj2
	assert sorted(obj1._ex_dict) == sorted(
		{'id1':5, 'ssid1':10, 'id2':3, 'ssid2':1}
	)
	assert sorted(obj1._callables_obj._callables_db) == sorted({
		'call1':{'a':5, 'b':6},
		'call2':{'a':7, 'b':8},
		'call3':{'a':10, 'b':100},
		'call4':{'a':200, 'b':300}
	})
	assert sorted(obj1._callables_obj._reverse_callables_db) == sorted(
		{'rc1':5, 'rc2':7, 'rc3':0, 'rc4':-1}
	)
	assert sorted(obj1._callables_obj._modules_dict) == sorted(
		{'key1':'alpha', 'key2':'beta', 'key3':'pi', 'key4':'gamma'}
	)
	assert sorted(obj1._callables_obj._fnames) == sorted(['hello', 'world'])
	assert sorted(obj1._callables_obj._module_names) == sorted(
		['this', 'is', 'a', 'test']
	)
	assert sorted(obj1._callables_obj._class_names) == sorted(
		['once', 'upon', 'a', 'time']
	)
	#
	obj2._full_cname = True
	with pytest.raises(RuntimeError) as excinfo:
		obj1+obj2
	assert excinfo.value.message == 'Incompatible exception handlers'
	with pytest.raises(RuntimeError) as excinfo:
		obj1 += obj2
	assert excinfo.value.message == 'Incompatible exception handlers'
	obj2._full_cname = False

	obj2._exclude = ['_pytest']
	with pytest.raises(RuntimeError) as excinfo:
		obj1+obj2
	assert excinfo.value.message == 'Incompatible exception handlers'
	with pytest.raises(RuntimeError) as excinfo:
		obj1 += obj2
	assert excinfo.value.message == 'Incompatible exception handlers'
	obj2._exclude = None


def test_eq():
	""" Test __eq__() function """
	putil.exh.get_or_create_exh_obj()
	putil.eng.peng(100, 3, True) # Trace some exceptions
	obj1 = putil.exh.get_exh_obj()
	obj2 = copy.copy(obj1)
	assert obj1 == obj2
	assert 5 != obj1


def test_nonzero():
	""" Test __nonzero__() function """
	exhobj = putil.exh.ExHandle()
	assert not exhobj
	def my_func(exhobj):
		exhobj.add_exception('test', RuntimeError, 'Message')
	my_func(exhobj)
	assert exhobj
