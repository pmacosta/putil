# pcsv.py	pylint:disable=C0111
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

import csv
import inspect

import putil.exh
import putil.misc
import putil.check

# Exception tracing initialization code
"""
[[[cog
import sys
import copy
import tempfile

import putil.exh
import putil.misc
import putil.pcsv

mod_obj = sys.modules['__main__']
def write_file(file_handle):	#pylint: disable=C0111
	file_handle.write('Ctrl,Ref,Result\n')
	file_handle.write('1,3,10\n')
	file_handle.write('1,4,20\n')
	file_handle.write('2,4,30\n')
	file_handle.write('2,5,40\n')
	file_handle.write('3,5,50\n')

# Trace CsvFile class
setattr(mod_obj, '_EXH', putil.exh.ExHandle(putil.pcsv.CsvFile))
exobj = getattr(mod_obj, '_EXH')
with putil.misc.TmpFile(write_file) as file_name:
	obj = putil.pcsv.CsvFile(file_name, dfilter={'Result':20})
obj.add_dfilter({'Result':20})
obj.dfilter = {'Result':20}
obj.data()
with tempfile.NamedTemporaryFile(delete=True) as fobj:
	obj.write(file_name=fobj.name, col=None, filtered=False, headers=True, append=False)
exobj.build_ex_tree(no_print=True)
exobj_csvfile = copy.deepcopy(exobj)

# Trace module functions
setattr(mod_obj, '_EXH', putil.exh.ExHandle(putil.pcsv.write))
exobj = getattr(mod_obj, '_EXH')
with tempfile.NamedTemporaryFile(delete=True) as fobj:
	putil.pcsv.write(file_name=fobj.name, data=[['Col1', 'Col2'], [1, 2], [3, 4]], append=False)
exobj.build_ex_tree(no_print=True)
exobj_funcs = copy.deepcopy(exobj)
]]]
[[[end]]]
"""	#pylint: disable=W0105

###
# DataFilter custom pseudo-type
###
class DataFilter(object):	#pylint: disable=R0903
	""" Data filter specification pseudo-type """
	def includes(self, test_obj):	#pylint: disable=R0201,W0613
		"""	Test that an object belongs to the pseudo-type """
		if not isinstance(test_obj, dict):
			return False
		for col_name in test_obj:
			if (not isinstance(test_obj[col_name], list)) and (not putil.misc.isnumber(test_obj[col_name])) and (not isinstance(test_obj[col_name], str)):
				return False
			if isinstance(test_obj[col_name], list):
				for element in test_obj[col_name]:
					if (not putil.misc.isnumber(element)) and (not isinstance(element, str)):
						return False
		return True

	def istype(self, test_obj):	#pylint: disable=R0201
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

	def exception(self, param_name):	#pylint: disable=R0201,W0613
		"""	Returns a suitable exception message """
		return {'type':TypeError, 'msg':'Argument `{0}` is of the wrong type'.format(param_name)}
putil.check.register_new_type(DataFilter, 'Comma-separated values file data filter')


@putil.check.check_arguments({'file_name':putil.check.File(check_existance=False), 'data':putil.check.ArbitraryLengthList(list), 'append':bool})
def write(file_name, data, append=True):
	"""
	Write data to a specified comma-separated values (CSV) file

	:param	file_name:	File name of the comma-separated values file to be written
	:type	file_name:	string
	:param	data:	Data to write to file. Each item in **data** should contain a sub-list corresponding to a row of data; each item in the sub-lists should contain data corresponding to a \
	particular column
	:type	data:	list
	:param	append: Append data flag. If **append** is *True* data is added to **file_name** if it exits, otherwise a new file is created. If **append** is *False*, a new file is created, \
	(overwriting an existing file with the same name if such file exists)
	:type	append: boolean

	.. [[[cog cog.out(exobj_funcs.get_sphinx_doc_for_member('write')) ]]]

	:raises:
	 * IOError (File *[file_name]* could not be created: *[reason]*)

	 * IOError (File *[file_name]* could not be found)

	 * OSError (File *[file_name]* could not be created: *[reason]*)

	 * RuntimeError (File *[file_name]* could not be created: *[reason]*)

	 * TypeError (Argument `append` is of the wrong type)

	 * TypeError (Argument `data` is of the wrong type)

	 * TypeError (Argument `file_name` is of the wrong type)

	 * ValueError (There is no data to save to file)

	.. [[[end]]]
	"""
	root_module = inspect.stack()[-1][0]
	_exh = root_module.f_locals['_EXH'] if '_EXH' in root_module.f_locals else putil.exh.ExHandle(putil.pcsv.write)
	_exh.add_exception(name='data_is_empty', extype=ValueError, exmsg='There is no data to save to file')
	_exh.add_exception(name='file_could_not_be_created_io', extype=IOError, exmsg='File *[file_name]* could not be created: *[reason]*')
	_exh.add_exception(name='file_could_not_be_created_os', extype=OSError, exmsg='File *[file_name]* could not be created: *[reason]*')
	_exh.add_exception(name='file_could_not_be_created_runtime', extype=RuntimeError, exmsg='File *[file_name]* could not be created: *[reason]*')
	_exh.raise_exception_if(name='data_is_empty', condition=(len(data) == 0) or ((len(data) == 1) and (len(data[0]) == 0)))
	try:
		putil.misc.make_dir(file_name)
		file_handle = open(file_name, 'wb' if append is False else 'ab')
		csv_handle = csv.writer(file_handle, delimiter=',')
		for row in data:
			csv_handle.writerow(row)
		file_handle.close()
	except IOError as msg:
		_exh.raise_exception_if(name='file_could_not_be_created_io', condition=True, edata=[{'field':'file_name', 'value':file_name}, {'field':'reason', 'value':msg.strerror}])
	except OSError as msg:
		_exh.raise_exception_if(name='file_could_not_be_created_os', condition=True, edata=[{'field':'file_name', 'value':file_name}, {'field':'reason', 'value':msg.strerror}])
	except Exception as msg:	#pylint: disable=W0703
		_exh.raise_exception_if(name='file_could_not_be_created_runtime', condition=True, edata=[{'field':'file_name', 'value':file_name}, {'field':'reason', 'value':msg.strerror}])
	_exh.raise_exception_if(name='file_could_not_be_created_io', condition=False)
	_exh.raise_exception_if(name='file_could_not_be_created_os', condition=False)
	_exh.raise_exception_if(name='file_could_not_be_created_runtime', condition=False)


def _number_failsafe(obj):
	""" Convert to float if object is a float string """
	if 'inf' in obj.lower():
		return obj
	try:
		return int(obj)
	except:	#pylint: disable=W0702
		try:
			return float(obj)
		except:	#pylint: disable=W0702
			return obj


class CsvFile(object):
	"""
	Process comma-separated values (CSV) files

	:param	file_name:	File name of the comma-separated values file to be read
	:type	file_name:	string
	:param	dfilter:	Data filter. See `DataFilter`_ pseudo-type specification
	:type	dfilter:	DataFilter
	:rtype:	:py:class:`putil.pcsv.CsvFile()` object

	.. [[[cog cog.out(exobj_csvfile.get_sphinx_doc_for_member('__init__')) ]]]

	:raises:
	 * IOError (File *[file_name]* could not be found)

	 * RuntimeError (Column headers are not unique)

	 * RuntimeError (File *[file_name]* has no valid data)

	 * RuntimeError (File *[file_name]* is empty)

	 * TypeError (Argument `file_name` is of the wrong type)

	 * Same as :py:meth:`putil.pcsv.CsvFile.add_dfilter`

	.. [[[end]]]
	"""
	@putil.check.check_arguments({'file_name':putil.check.File(check_existance=True), 'dfilter':putil.check.PolymorphicType([None, DataFilter()])})
	def __init__(self, file_name, dfilter=None):
		self._header, self._header_upper, self._data, self._fdata, self._dfilter, self._exh = None, None, None, None, None, None
		# Register exceptions
		root_module = inspect.stack()[-1][0]
		self._exh = root_module.f_locals['_EXH'] if '_EXH' in root_module.f_locals else putil.exh.ExHandle(putil.pcsv.CsvFile)
		self._exh.add_exception(name='file_not_found', extype=IOError, exmsg='File *[file_name]* could not be found')
		self._exh.add_exception(name='file_empty', extype=RuntimeError, exmsg='File *[file_name]* is empty')
		self._exh.add_exception(name='column_headers_not_unique', extype=RuntimeError, exmsg='Column headers are not unique')
		self._exh.add_exception(name='file_has_no_valid_data', extype=RuntimeError, exmsg='File *[file_name]* has no valid data')
		#
		self._exh.raise_exception_if(name='file_not_found', condition=False, edata={'field':'file_name', 'value':file_name})	# Check is actually done in the context manager, which is unreachable
		with open(file_name, 'rU') as file_handle:
			self._raw_data = [row for row in csv.reader(file_handle)]
		# Process header
		self._exh.raise_exception_if(name='file_empty', condition=len(self._raw_data) == 0, edata={'field':'file_name', 'value':file_name})
		self._header = self._raw_data[0]
		self._header_upper = [col.upper() for col in self.header]
		self._exh.raise_exception_if(name='column_headers_not_unique', condition=len(set(self._header_upper)) != len(self._header_upper))
		# Find start of data row
		num = -1
		for num, row in enumerate(self._raw_data[1:]):
			if any([putil.misc.isnumber(_number_failsafe(col)) for col in row]):
				break
		self._exh.raise_exception_if(name='file_has_no_valid_data', condition=num == -1, edata={'field':'file_name', 'value':file_name})
		# Set up class properties
		self._data = [[None if col.strip() == '' else _number_failsafe(col) for col in row] for row in self._raw_data[num+1:]]
		self.reset_dfilter()
		self._set_dfilter(dfilter)

	def _validate_dfilter(self, dfilter):
		""" Validate that all columns in filter are in header """
		self._exh.add_exception(name='dfilter_empty', extype=ValueError, exmsg='Argument `dfilter` is empty')
		if dfilter is not None:
			self._exh.raise_exception_if(name='dfilter_empty', condition=len(dfilter) == 0)
			for key in dfilter:
				self._in_header(key)

	def _get_dfilter(self):	#pylint: disable=C0111
		return self._dfilter	#pylint: disable=W0212

	@putil.check.check_argument(putil.check.PolymorphicType([None, DataFilter()]))
	def _set_dfilter(self, dfilter):	#pylint: disable=C0111
		if dfilter is None:
			self._dfilter = None
		else:
			self._validate_dfilter(dfilter)
			col_nums = [self._header_upper.index(key.upper()) for key in dfilter]
			col_values = [[element] if not putil.misc.isiterable(element) else [value for value in element] for element in dfilter.values()]
			self._fdata = [row for row in self._data if all([row[col_num] in col_value for col_num, col_value in zip(col_nums, col_values)])]
			self._dfilter = dfilter

	@putil.check.check_argument(DataFilter())
	def add_dfilter(self, dfilter):
		"""
		Add more data filter(s) to the existing filter(s). Data is added to the current filter for a particular column if that column was already filtered, duplicate filter values are eliminated.

		:param	dfilter:	Data filter. See `DataFilter`_ pseudo-type specification
		:type	dfilter:	DataFilter

		.. [[[cog cog.out(exobj_csvfile.get_sphinx_doc_for_member('add_dfilter')) ]]]

		:raises:
		 * TypeError (Argument `dfilter` is of the wrong type)

		 * ValueError (Argument `dfilter` is empty)

		 * ValueError (Column *[column_name]* not found in header)

		.. [[[end]]]
		"""
		self._validate_dfilter(dfilter)
		if dfilter is None:
			self._dfilter = dfilter
		elif self._dfilter is None:
			self._dfilter = dfilter
		else:
			for key in dfilter:
				if key in self._dfilter:
					self._dfilter[key] = list(set((self._dfilter[key] if isinstance(self._dfilter[key], list) else [self._dfilter[key]]) + (dfilter[key] if isinstance(dfilter[key], list) else [dfilter[key]])))
				else:
					self._dfilter[key] = dfilter[key]
		self._set_dfilter(self._dfilter)

	def _get_header(self):	#pylint: disable=C0111
		return self._header	#pylint: disable=W0212

	@putil.check.check_arguments({'col':putil.check.PolymorphicType([None, str, putil.check.ArbitraryLengthList(str)]), 'filtered':bool})
	def data(self, col=None, filtered=False):
		"""
		 Return (filtered) file data. The returned object is a list, each item is a sub-list corresponding to a row of data; each item in the sub-lists contains data corresponding to a \
		 particular column

		:param	col:	Column(s) to extract from filtered data. If no column specification is given (or **col** is *None*) all columns are returned
		:type	col:	string, list of strings or None
		:param	filtered: Raw or filtered data flag. If **filtered** is *True*, the filtered data is returned, if **filtered** is *False* the raw (original) file data is returned
		:type	filtered: boolean
		:rtype:	list

		.. [[[cog cog.out(exobj_csvfile.get_sphinx_doc_for_member('data')) ]]]

		:raises:
		 * TypeError (Argument `col` is of the wrong type)

		 * TypeError (Argument `filtered` is of the wrong type)

		 * ValueError (Column *[column_name]* not found in header)

		.. [[[end]]]
		"""
		self._in_header(col)
		return (self._data if not filtered else self._fdata) if col is None else self._core_data((self._data if not filtered else self._fdata), col)

	def reset_dfilter(self):
		""" Reset (clears) data filter """
		self._fdata = self._data[:]
		self._dfilter = None

	@putil.check.check_arguments({'file_name':putil.check.File(check_existance=False), 'col':putil.check.PolymorphicType([None, str, putil.check.ArbitraryLengthList(str)]), 'filtered':bool, 'headers':bool, 'append':bool})
	def write(self, file_name, col=None, filtered=False, headers=True, append=True):	#pylint: disable=R0913
		"""
		Write (processed) data to a specified comma-separated values (CSV) file

		:param	file_name:	File name of the comma-separated values file to be written
		:type	file_name:	string
		:param	col:	Column(s) to write to file. If no column specification is given (or **col** is *None*) all columns in data are written
		:type	col:	string, list of strings or None
		:param	filtered: Raw or filtered data flag. If **filtered** is *True*, the filtered data is written, if **filtered** is *False* the raw (original) file data is written
		:type	filtered: boolean
		:param	headers: Include headers flag. If **headers** is *True* headers and data are written, if **headers** is *False* only data is written
		:type	headers: boolean
		:param	append: Append data flag. If **append** is *True* data is added to **file_name** if it exits, otherwise a new file is created. If **append** is *False*, a new file is created, \
		(overwriting an existing file with the same name if such file exists)
		:type	append: boolean

		.. [[[cog cog.out(exobj_csvfile.get_sphinx_doc_for_member('write')) ]]]

		:raises:
		 * IOError (File *[file_name]* could not be found)

		 * TypeError (Argument `append` is of the wrong type)

		 * TypeError (Argument `file_name` is of the wrong type)

		 * TypeError (Argument `headers` is of the wrong type)

		 * ValueError (There is no data to save to file)

		 * Same as :py:meth:`putil.pcsv.CsvFile.data`

		.. [[[end]]]
		"""
		self._exh.add_exception(name='write', extype=ValueError, exmsg='There is no data to save to file')
		self._in_header(col)
		data = self.data(col=col, filtered=filtered)
		if headers:
			col = [col] if isinstance(col, str) else col
			header = self.header if col is None else [self.header[self._header_upper.index(element.upper())] for element in col]
		self._exh.raise_exception_if(name='write', condition=(len(data) == 0) or ((len(data) == 1) and (len(data[0]) == 0)))
		#if (len(data) == 0) or ((len(data) == 1) and (len(data[0]) == 0)):
		#	raise ValueError('There is no data to save to file')
		data = [["''" if col is None else col for col in row] for row in data]
		write(file_name, [header]+data if headers else data, append=append)

	def _in_header(self, col):
		""" Validate column name(s) against the column names in the file header """
		self._exh.add_exception(name='header_not_found', extype=ValueError, exmsg='Column *[column_name]* not found in header')
		if col is not None:
			col_list = [col] if isinstance(col, str) else col
			for col in col_list:
				self._exh.raise_exception_if(name='header_not_found', condition=col.upper() not in self._header_upper, edata={'field':'column_name', 'value':col})

	def _core_data(self, data, col=None):
		""" Extract columns from data """
		if isinstance(col, str):
			col_num = self._header_upper.index(col.upper())
			return [[row[col_num]] for row in data]
		elif isinstance(col, list):
			col_list = col[:]
			col_index_list = [self._header_upper.index(col.upper()) for col in col_list]
			return [[row[index] for index in col_index_list] for row in data]

	# Managed attributes
	dfilter = property(_get_dfilter, _set_dfilter, None, doc='Data filter')
	"""
	Set or return the data filter.

	:type:		DataFilter. See `DataFilter`_ pseudo-type specification
	:rtype:		DataFilter or None

	.. [[[cog cog.out(exobj_csvfile.get_sphinx_doc_for_member('dfilter')) ]]]

	:raises: Same as :py:meth:`putil.pcsv.CsvFile.add_dfilter`

	.. [[[end]]]
	"""	#pylint: disable=W0105

	header = property(_get_header, None, None, doc='Comma-separated file (CSV) header')
	"""
	Return the header of the comma-separated values file. Each list item is a column header

	:rtype:	list of strings
	"""	#pylint: disable=W0105

