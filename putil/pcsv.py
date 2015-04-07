# pcsv.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import csv, itertools, sys

import putil.exh, putil.misc, putil.pcontracts


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_pcsv
exobj = trace_ex_pcsv.trace_module(no_print=True)
]]]
[[[end]]]
"""	#pylint: disable=W0105


###
# DataFilter custom pseudo-type
###
@putil.pcontracts.new_contract(argument_invalid='Argument `*[argument_name]*` is not valid', argument_empty=(ValueError, 'Argument `*[argument_name]*` is empty'))
def csv_data_filter(obj):
	r"""
	Contract that validates if an object is a dictionary that represents a DataFilter pseudo-type object

	:param	obj: Object
	:type	obj: any
	:raises:
	 * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token \*[argument_name]\* is replaced by the *name* of the argument the contract is attached to

	 * ValueError (Argument \`*[argument_name]*\` is empty). The token \*[argument_name]\* is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	exdesc = putil.pcontracts.get_exdesc()
	if obj == None:
		return None
	if not isinstance(obj, dict):
		raise ValueError(exdesc['argument_invalid'])
	if not len(obj):
		raise ValueError(exdesc['argument_empty'])
	if any([not isinstance(col_name, str) for col_name in obj.iterkeys()]):
		raise ValueError(exdesc['argument_invalid'])
	for col_name in obj:
		if (not isinstance(obj[col_name], list)) and (not putil.misc.isnumber(obj[col_name])) and (not isinstance(obj[col_name], str)):
			raise ValueError(exdesc['argument_invalid'])
		if isinstance(obj[col_name], list):
			for element in obj[col_name]:
				if (not putil.misc.isnumber(element)) and (not isinstance(element, str)):
					raise ValueError(exdesc['argument_invalid'])


###
# Functions
###
@putil.pcontracts.contract(file_name='file_name', data='list(list(str|int|float))', append=bool)
def write(file_name, data, append=True):
	r"""
	Writes data to a specified comma-separated values (CSV) file

	:param	file_name:	File name of the comma-separated values file to be written
	:type	file_name:	string
	:param	data:	Data to write to file. Each item in **data** should contain a sub-list corresponding to a row of data; each item in the sub-lists should contain data corresponding to a
	 particular column
	:type	data:	list
	:param	append: Flag that indicates if data is added to an existing file (or a new file is created if it does not exist) (True), or if data overwrites the file contents (if the file exists) or creates a new file if the file
	 does not exists (False)
	:type	append: boolean

	.. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.pcsv.write

	:raises:
	 * IOError (File *[file_name]* could not be created: *[reason]*)

	 * OSError (File *[file_name]* could not be created: *[reason]*)

	 * RuntimeError (Argument \`append\` is not valid)

	 * RuntimeError (Argument \`data\` is not valid)

	 * RuntimeError (Argument \`file_name\` is not valid)

	 * RuntimeError (File *[file_name]* could not be created: *[reason]*)

	 * ValueError (There is no data to save to file)

	.. [[[end]]]
	"""
	_write_int(file_name, data, append)


def _write_int(file_name, data, append=True):
	_exh = putil.exh.get_or_create_exh_obj()
	_exh.add_exception(exname='data_is_empty', extype=ValueError, exmsg='There is no data to save to file')
	_exh.add_exception(exname='file_could_not_be_created_io', extype=IOError, exmsg='File *[file_name]* could not be created: *[reason]*')
	_exh.add_exception(exname='file_could_not_be_created_os', extype=OSError, exmsg='File *[file_name]* could not be created: *[reason]*')
	_exh.add_exception(exname='file_could_not_be_created_runtime', extype=RuntimeError, exmsg='File *[file_name]* could not be created: *[reason]*')
	_exh.raise_exception_if(exname='data_is_empty', condition=(len(data) == 0) or ((len(data) == 1) and (len(data[0]) == 0)))
	try:
		putil.misc.make_dir(file_name)
		file_handle = open(file_name, 'wb' if append is False else 'ab')
		csv_handle = csv.writer(file_handle, delimiter=',')
		for row in data:
			csv_handle.writerow(row)
		file_handle.close()
	except IOError as eobj:
		_exh.raise_exception_if(exname='file_could_not_be_created_io', condition=True, edata=[{'field':'file_name', 'value':file_name}, {'field':'reason', 'value':eobj.strerror}])
	except OSError as eobj:
		_exh.raise_exception_if(exname='file_could_not_be_created_os', condition=True, edata=[{'field':'file_name', 'value':file_name}, {'field':'reason', 'value':eobj.strerror}])
	except:	#pylint: disable=W0702
		_, exvalue, _ = sys.exc_info()
		msg = '{0}'.format(exvalue)
		_exh.raise_exception_if(exname='file_could_not_be_created_runtime', condition=True, edata=[{'field':'file_name', 'value':file_name}, {'field':'reason', 'value':msg}])
	_exh.raise_exception_if(exname='file_could_not_be_created_io', condition=False)
	_exh.raise_exception_if(exname='file_could_not_be_created_os', condition=False)
	_exh.raise_exception_if(exname='file_could_not_be_created_runtime', condition=False)


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

###
# Classes
###
class CsvFile(object):
	r"""
	Processes comma-separated values (CSV) files

	:param	file_name:	File name of the comma-separated values file to be read
	:type	file_name:	string
	:param	dfilter:	Data filter. See `DataFilter`_ pseudo-type specification
	:type	dfilter:	DataFilter
	:rtype:	:py:class:`putil.pcsv.CsvFile` object

	.. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.pcsv.CsvFile.__init__

	:raises:
	 * IOError (File \`*[file_name]*\` could not be found)

	 * RuntimeError (Argument \`dfilter\` is not valid)

	 * RuntimeError (Argument \`file_name\` is not valid)

	 * RuntimeError (Column headers are not unique)

	 * RuntimeError (File *[file_name]* has no valid data)

	 * RuntimeError (File *[file_name]* is empty)

	 * ValueError (Argument \`dfilter\` is empty)

	 * ValueError (Column *[column_name]* not found in header)

	.. [[[end]]]
	"""
	@putil.pcontracts.contract(file_name='file_name_exists', dfilter='csv_data_filter')
	def __init__(self, file_name, dfilter=None):
		self._header, self._header_upper, self._data, self._fdata, self._dfilter, self._exh = None, None, None, None, None, None
		# Register exceptions
		self._exh = putil.exh.get_or_create_exh_obj()
		self._exh.add_exception(exname='file_empty', extype=RuntimeError, exmsg='File *[file_name]* is empty')
		self._exh.add_exception(exname='column_headers_not_unique', extype=RuntimeError, exmsg='Column headers are not unique')
		self._exh.add_exception(exname='file_has_no_valid_data', extype=RuntimeError, exmsg='File *[file_name]* has no valid data')
		with open(file_name, 'rU') as file_handle:
			self._raw_data = [row for row in csv.reader(file_handle)]
		# Process header
		self._exh.raise_exception_if(exname='file_empty', condition=len(self._raw_data) == 0, edata={'field':'file_name', 'value':file_name})
		self._header = self._raw_data[0]
		self._header_upper = [col.upper() for col in self.header]
		self._exh.raise_exception_if(exname='column_headers_not_unique', condition=len(set(self._header_upper)) != len(self._header_upper))
		# Find start of data row
		num = -1
		for num, row in enumerate(self._raw_data[1:]):
			if any([putil.misc.isnumber(_number_failsafe(col)) for col in row]):
				break
		self._exh.raise_exception_if(exname='file_has_no_valid_data', condition=num == -1, edata={'field':'file_name', 'value':file_name})
		# Set up class properties
		self._data = [[None if col.strip() == '' else _number_failsafe(col) for col in row] for row in self._raw_data[num+1:]]
		self.reset_dfilter()
		self._set_dfilter_int(dfilter)	# dfilter already validated, can use internal function, not API end-point

	def _validate_dfilter(self, dfilter):
		""" Validate that all columns in filter are in header """
		if dfilter is not None:
			for key in dfilter:
				self._in_header(key)

	def _get_dfilter(self):	#pylint: disable=C0111
		return self._dfilter	#pylint: disable=W0212

	@putil.pcontracts.contract(dfilter='csv_data_filter')
	def _set_dfilter(self, dfilter):	#pylint: disable=C0111
		self._set_dfilter_int(dfilter)

	def _set_dfilter_int(self, dfilter):	#pylint: disable=C0111
		if dfilter is None:
			self._dfilter = None
		else:
			self._validate_dfilter(dfilter)
			col_nums = [self._header_upper.index(key.upper()) for key in dfilter]
			col_values = [[element] if not putil.misc.isiterable(element) else [value for value in element] for element in dfilter.values()]
			self._fdata = [row for row in self._data if all([row[col_num] in col_value for col_num, col_value in itertools.izip(col_nums, col_values)])]
			self._dfilter = dfilter

	@putil.pcontracts.contract(dfilter='csv_data_filter')
	def add_dfilter(self, dfilter):
		r"""
		Adds more data filter(s) to the existing filter(s). Data is added to the current filter for a particular column if that column was already filtered, duplicate filter values are eliminated.

		:param	dfilter:	Data filter. See `DataFilter`_ pseudo-type specification
		:type	dfilter:	DataFilter

		.. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.pcsv.CsvFile.add_dfilter

		:raises:
		 * RuntimeError (Argument \`dfilter\` is not valid)

		 * ValueError (Argument \`dfilter\` is empty)

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
		self._set_dfilter_int(self._dfilter)

	def _get_header(self):	#pylint: disable=C0111
		return self._header	#pylint: disable=W0212

	@putil.pcontracts.contract(col='None|str|list(str)', filtered=bool)
	def data(self, col=None, filtered=False):
		r"""
		 Returns (filtered) file data. The returned object is a list, each item is a sub-list corresponding to a row of data; each item in the sub-lists contains data corresponding to a \
		 particular column

		:param	col:	Column(s) to extract from filtered data. If no column specification is given (or the argument is None) all columns are returned
		:type	col:	string, list of strings or None
		:param	filtered: Flag that indicates whether the raw (original) data should be returned (False) or whether filtered data should be retuned (True)
		:type	filtered: boolean
		:rtype:	list

		.. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.pcsv.CsvFile.data

		:raises:
		 * RuntimeError (Argument \`col\` is not valid)

		 * RuntimeError (Argument \`filtered\` is not valid)

		 * ValueError (Column *[column_name]* not found in header)

		.. [[[end]]]
		"""
		self._in_header(col)
		return (self._data if not filtered else self._fdata) if col is None else self._core_data((self._data if not filtered else self._fdata), col)

	def reset_dfilter(self):
		""" Reset (clears) the data filter """
		self._fdata = self._data[:]
		self._dfilter = None

	@putil.pcontracts.contract(file_name='file_name', col='None|str|list(str)', filtered=bool, headers=bool, append=bool)
	def write(self, file_name, col=None, filtered=False, headers=True, append=True):	#pylint: disable=R0913
		r"""
		Writes (processed) data to a specified comma-separated values (CSV) file

		:param	file_name:	File name of the comma-separated values file to be written
		:type	file_name:	string
		:param	col:	Column(s) to write to file. If no column specification is given (or the argument is None) all columns in the data are written
		:type	col:	string, list of strings or None
		:param	filtered: Flag that indicates whether the raw (original) data should be written (False) or whether filtered data should be written (True)
		:type	filtered: boolean
		:param	headers: Flag that indicates whether column headers should be written (True) or not (False)
		:type	headers: boolean
		:param	append: Flag that indicates if data is added to an existing file (or a new file is created if it does not exist) (True), or if data overwrites the file contents (if the
		 file exists) or creates a new file if the file does not exists (False)
		:type	append: boolean

		.. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.pcsv.CsvFile.write

		:raises:
		 * IOError (File *[file_name]* could not be created: *[reason]*)

		 * OSError (File *[file_name]* could not be created: *[reason]*)

		 * RuntimeError (Argument \`append\` is not valid)

		 * RuntimeError (Argument \`col\` is not valid)

		 * RuntimeError (Argument \`file_name\` is not valid)

		 * RuntimeError (Argument \`filtered\` is not valid)

		 * RuntimeError (Argument \`headers\` is not valid)

		 * RuntimeError (File *[file_name]* could not be created: *[reason]*)

		 * ValueError (Column *[column_name]* not found in header)

		 * ValueError (There is no data to save to file)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='write', extype=ValueError, exmsg='There is no data to save to file')
		self._in_header(col)
		data = self.data(col=col, filtered=filtered)
		if headers:
			col = [col] if isinstance(col, str) else col
			header = self.header if col is None else [self.header[self._header_upper.index(element.upper())] for element in col]
		self._exh.raise_exception_if(exname='write', condition=(len(data) == 0) or ((len(data) == 1) and (len(data[0]) == 0)))
		data = [["''" if col is None else col for col in row] for row in data]
		_write_int(file_name, [header]+data if headers else data, append=append)

	def _in_header(self, col):
		""" Validate column name(s) against the column names in the file header """
		self._exh.add_exception(exname='header_not_found', extype=ValueError, exmsg='Column *[column_name]* not found in header')
		if col is not None:
			col_list = [col] if isinstance(col, str) else col
			for col in col_list:
				self._exh.raise_exception_if(exname='header_not_found', condition=col.upper() not in self._header_upper, edata={'field':'column_name', 'value':col})

	def _core_data(self, data, col=None):
		""" Extract columns from data """
		if isinstance(col, str):
			col_num = self._header_upper.index(col.upper())
			return [[row[col_num]] for row in data]
		else:	# isinstance(col, list):
			col_list = col[:]
			col_index_list = [self._header_upper.index(col.upper()) for col in col_list]
			return [[row[index] for index in col_index_list] for row in data]

	# Managed attributes
	dfilter = property(_get_dfilter, _set_dfilter, None, doc='Data filter')
	r"""
	Sets or returns the data filter

	:type:		DataFilter. See `DataFilter`_ pseudo-type specification
	:rtype:		DataFilter or None

	.. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.pcsv.CsvFile.dfilter

	:raises: (when assigned)

	 * RuntimeError (Argument \`dfilter\` is not valid)

	 * ValueError (Argument \`dfilter\` is empty)

	 * ValueError (Column *[column_name]* not found in header)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	header = property(_get_header, None, None, doc='Comma-separated file (CSV) header')
	"""
	Returns the header of the comma-separated values file. Each list item is a column header

	:rtype:	list of strings
	"""	#pylint: disable=W0105
