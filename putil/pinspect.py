# pinspect.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
#pylint: disable=C0111,W0212

import ast, copy, funcsigs, os, re, sys, types

import putil.misc


###
# Functions
###
def _get_module_name_from_file_name(file_name):
	""" Get module name from module file name """
	for mobj in [item for item in sys.modules.values() if item and hasattr(item, '__file__')]:
		if mobj.__file__.replace('.pyc', '.py') == file_name.replace('.pyc', '.py'):
			module_name = mobj.__name__
			return module_name
	raise RuntimeError('Module could not be found')


def _is_parg(arg):
	""" Returns True if arg argument is the name of a positional variable argument (i.e. *pargs) """
	return (len(arg) > 1) and (arg[0] == '*') and (arg[1] != '*')


def _is_kwarg(arg):
	""" Returns True if arg argument is the name of a keyword variable argument (i.e. **kwargs) """
	return (len(arg) > 2) and (arg[:2] == '**')


def get_function_args(func, no_self=False, no_varargs=False):
	"""
	Returns a tuple of the function argument names in the order they are specified in the function signature

	:param	func: Function
	:type	func: function object
	:param	no_self: Flag that indicates whether the argument *self* should be included in the output (False) or not (True)
	:type	no_self: boolean
	:param	no_varargs: Flag that indicates whether keyword arguments should be included in the output (True) or not (False)
	:rtype: tuple

	For example:

		>>> class MyClass(object):
		...	def __init__(self, value, **kwargs):
		...		pass
		...
		>>> putil.pinspect.get_function_args(MyClass.__init__)
		('self', 'value', '**kwargs')
		>>> putil.pinspect.get_function_args(MyClass.__init__, no_self=True)
		('value', '**kwargs')
		>>> putil.pinspect.get_function_args(MyClass.__init__, no_self=True, no_varargs=True)
		('value', )
		>>> putil.pinspect.get_function_args(MyClass.__init__, no_varargs=True)
		('self', 'value')
	"""
	par_dict = funcsigs.signature(func).parameters
	args = ['{0}{1}'.format('*' if par_dict[par].kind == par_dict[par].VAR_POSITIONAL else ('**' if par_dict[par].kind == par_dict[par].VAR_KEYWORD else ''), par) for par in par_dict]
	self_filtered_args = args if not args else (args[1 if (args[0] == 'self') and no_self else 0:])
	varargs_filtered_args = tuple([arg for arg in self_filtered_args if (not no_varargs) or (no_varargs and (not _is_parg(arg)) and (not _is_kwarg(arg)))])
	return varargs_filtered_args


def get_module_name(module_obj):
	r"""
	Retrieves the module name from a module object

	:param	module_obj: Module object
	:type	module_obj: object
	:rtype: string
	:raises:
	 * RuntimeError (Argument \`module_obj\` is not valid)

	 * RuntimeError (Module object \`*[module_name]*\` could not be found in loaded modules)

	For example:

		>>> putil.pinspect.get_module_name(sys.modules['putil.pinspect'])
		'putil.pinspect'
	"""
	if not is_object_module(module_obj):
		raise RuntimeError('Argument `module_obj` is not valid')
	name = module_obj.__name__
	if name not in sys.modules:
		raise RuntimeError('Module object `{0}` could not be found in loaded modules'.format(name))
	return name


def get_package_name(module_obj):
	"""
	Finds loaded root package name of module object

	:param	module_obj: Module object
	:type	module_obj: object
	:rtype: string
	:raises: RuntimeError (Loaded package root could not be found)

	For example:

		>>> import putil.pinspect
		>>> putil.pinspect.get_package_name(sys.modules['putil.pinspect'])
		'putil'
	"""
	name = get_module_name(module_obj)
	obj_name_tokens = name.split('.')
	if len(obj_name_tokens) == 1:
		return name
	for module_name in ['.'.join(obj_name_tokens[:num+1]) for num in xrange(len(obj_name_tokens)-1)]:
		if module_name in sys.modules:
			return module_name
	raise RuntimeError('Loaded package root could not be found')


def is_object_module(obj):
	"""
	Tests if the argument is a module object

	:param	obj: Object
	:type	obj: any
	:rtype: boolean
	"""
	return isinstance(obj, types.ModuleType)


def is_special_method(name):
	"""
	Tests if a callable name is a special Python method (has a :code:`'__'` prefix and suffix)

	:param	name: Callable name
	:type	name: string
	:rtype: boolean
	"""
	return name.startswith('__')


def loaded_package_modules(module_obj, _rarg=None):
	"""
	Generates a list of loaded package module objects from a module object belonging to a given package

	:param	module_obj: Module object
	:type	module_obj: object
	:rtype: list

	For example:

		>>> import matplotlib.compat.subprocess, pprint
		>>> pprint.pprint(putil.pinspect.loaded_package_modules(sys.modules['matplotlib.compat.subprocess']))
		[<module 'matplotlib' from '/usr/lib/python2.7/dist-packages/matplotlib/__init__.pyc'>,
		 <module 'matplotlib.cbook' from '/usr/lib/python2.7/dist-packages/matplotlib/cbook.pyc'>,
		 <module 'matplotlib.colors' from '/usr/lib/python2.7/dist-packages/matplotlib/colors.pyc'>,
		 <module 'matplotlib.compat' from '/usr/lib/python2.7/dist-packages/matplotlib/compat/__init__.pyc'>,
		 <module 'matplotlib.compat.subprocess' from '/usr/lib/python2.7/dist-packages/matplotlib/compat/subprocess.pyc'>,
		 <module 'matplotlib.fontconfig_pattern' from '/usr/lib/python2.7/dist-packages/matplotlib/fontconfig_pattern.pyc'>,
		 <module 'matplotlib.rcsetup' from '/usr/lib/python2.7/dist-packages/matplotlib/rcsetup.pyc'>]
	"""
	recursive = bool(_rarg)
	root_name = (get_module_name if recursive else get_package_name)(module_obj)
	root_obj = sys.modules.get(root_name, None)
	root_dir, modules_traced, modules_list = _rarg[0] if recursive else os.path.split(getattr(root_obj, '__file__'))[0], _rarg[1] if recursive else list(), _rarg[2] if recursive else list()
	modules_traced.append(root_name)
	modules_list.append(root_obj)
	for module_obj, module_name in [(getattr(root_obj, module_name), module_name) for module_name in dir(root_obj)]:
		if is_object_module(module_obj) and hasattr(module_obj, '__file__') and os.path.split(getattr(module_obj, '__file__'))[0].startswith(root_dir) and (module_name not in modules_traced):
			modules_traced, modules_list = loaded_package_modules(module_obj, (root_dir, modules_traced, modules_list))
	return (modules_traced, modules_list) if recursive else modules_list


###
# Classes
###
class Callables(object):	# pylint: disable=R0903
	r"""
	Generates a list of module callables (functions, classes, methods and class properties) and gets their attributes (callable type, file name, lines span). Information from multiple modules can be stored in the
	callables database of the object by repeatedly calling :py:meth:`putil.pinspect.Callables.trace` with different module objects. A :py:class:`putil.pinspect.Callables` object retains knowledge of which modules have been traced
	so repeated calls to :py:meth:`putil.pinspect.Callables.trace` with the *same* module object will *not* result in module re-traces (and the consequent performance hit).

	:param	file_names: File names containing the modules to trace
	:type	file_names: list
	:raises:
	 * IOError (File *[file_name]* could not be found)

	 * RuntimeError (Argument \`file_names\` is not valid)
	"""
	def __init__(self, file_names=None):
		self._callables_db, self._reverse_callables_db, self._modules_dict = {}, {}, {}
		self._file_names, self._module_names, self._class_names = [], [], []
		if file_names:
			self.trace(file_names)

	def __add__(self, other):
		"""
		Merges two objects.

		:raises: RuntimeError (Conflicting information between objects)

		For example:

			>>> import putil.eng, putil.exh, putil.pinspect, sys
			>>> obj1 = putil.pinspect.Callables([sys.modules['putil.exh'].__file__])
			>>> obj2 = putil.pinspect.Callables([sys.modules['putil.eng'].__file__])
			>>> obj3 = putil.pinspect.Callables([
			... sys.modules['putil.exh'].__file__,
			... sys.modules['putil.eng'].__file__,
			... ])
			>>> obj1 == obj3
			False
			>>> obj1 == obj2
			False
			>>> obj1+obj2 == obj3
			True

		"""
		self._check_intersection(other)
		robj = Callables()
		robj._callables_db = copy.deepcopy(self._callables_db)
		robj._callables_db.update(copy.deepcopy(other._callables_db))
		robj._reverse_callables_db = copy.deepcopy(self._reverse_callables_db)
		robj._reverse_callables_db.update(copy.deepcopy(other._reverse_callables_db))
		robj._modules_dict = copy.deepcopy(self._modules_dict)
		robj._modules_dict.update(copy.deepcopy(other._modules_dict))
		robj._module_names = list(set(self._module_names[:]+other._module_names[:]))
		robj._class_names = list(set(self._class_names[:]+other._class_names[:]))
		robj._file_names = list(set(self._file_names[:]+other._file_names[:]))
		return robj

	def __copy__(self):
		"""
		Copies object. For example:

			>>> import copy, putil.exh, putil.pinspect, sys
			>>> obj1 = putil.pinspect.Callables([sys.modules['putil.exh'].__file__])
			>>> obj2 = copy.copy(obj1)
			>>> obj1 == obj2
			True

		"""
		cobj = Callables()
		for prop_name in putil.misc._private_props(self):	#pylint: disable=W0212
			setattr(cobj, prop_name, copy.deepcopy(getattr(self, prop_name)))
		return cobj

	def __eq__(self, other):
		"""
		Tests object equality. For example:

			>>> import putil.eng, putil.exh, putil.pinspect, sys
			>>> obj1 = putil.pinspect.Callables([sys.modules['putil.exh'].__file__])
			>>> obj2 = putil.pinspect.Callables([sys.modules['putil.exh'].__file__])
			>>> obj3 = putil.pinspect.Callables([sys.modules['putil.eng'].__file__])
			>>> obj1 == obj2
			True
			>>> obj1 == obj3
			False
			>>> 5 == obj3
			False

		"""
		return isinstance(other, Callables) and all([sorted(getattr(self, attr)) == sorted(getattr(other, attr)) for attr in putil.misc._private_props(self)])	#pylint: disable=W0212

	def __iadd__(self, other):
		"""
		Merges an object into an existing object.

		:raises: RuntimeError (Conflicting information between objects)

		For example:

			>>> import putil.eng, putil.exh, putil.pinspect, sys
			>>> obj1 = putil.pinspect.Callables([sys.modules['putil.exh'].__file__])
			>>> obj2 = putil.pinspect.Callables([sys.modules['putil.eng'].__file__])
			>>> obj3 = putil.pinspect.Callables([
			... sys.modules['putil.exh'].__file__,
			... sys.modules['putil.eng'].__file__,
			... ])
			>>> obj1 == obj3
			False
			>>> obj1 == obj2
			False
			>>> obj1 += obj2
			>>> obj1 == obj3
			True

		"""

		self._check_intersection(other)
		self._callables_db.update(copy.deepcopy(other._callables_db))
		self._reverse_callables_db.update(copy.deepcopy(other._reverse_callables_db))
		self._modules_dict.update(copy.deepcopy(other._modules_dict))
		self._module_names = list(set(self._module_names+other._module_names[:]))
		self._class_names = list(set(self._class_names+other._class_names[:]))
		self._file_names = list(set(self._file_names+other._file_names[:]))
		return self

	def __repr__(self):
		"""
		Returns a string with the expression needed to re-create the object. For example:

			>>> import putil.exh, putil.pinspect, sys
			>>> obj1 = putil.pinspect.Callables([sys.modules['putil.exh'].__file__])
			>>> repr(obj1)
			"putil.pinspect.Callables(['putil/exh.py'])"
			>>> exec "obj2="+repr(obj1)
			>>> obj1 == obj2
			True

		"""
		return 'putil.pinspect.Callables({0})'.format(sorted(self._file_names))

	def __str__(self):
		"""
		Returns a string with a detailed description of the object's contents. For example:

			>>> import pinspect_example_1, putil.pinspect, sys
			>>> cobj = putil.pinspect.Callables([sys.modules['pinspect_example_1'].__file__])
			>>> print str(cobj)
			Modules:
			   pinspect_example_1
			Classes:
			   pinspect_example_1.my_func.MyClass
			pinspect_example_1.my_func: func (6-19)
			pinspect_example_1.my_func.MyClass: class (8-19)
			pinspect_example_1.my_func.MyClass.__init__: meth (14-15)
			pinspect_example_1.my_func.MyClass._get_value: meth (16-17)
			pinspect_example_1.my_func.MyClass.value: prop (18)
			pinspect_example_1.print_name: func (20-21)

		The numbers in parenthesis indicates the line number in which the callable starts and ends within the file it is defined in.
		"""
		ret = list()
		if self._module_names:
			ret.append('Modules:')
			for module_name in sorted(self._module_names):
				ret.append('   {0}'.format(module_name))
			if self._class_names:
				ret.append('Classes:')
				for class_name in sorted(self._class_names):
					ret.append('   {0}'.format(class_name))
			for entry in sorted(self._modules_dict):
				for value in sorted(self._modules_dict[entry], key=lambda x: x['code_id'][1]):
					start_line = value['code_id'][1]
					stop_line = value['last_lineno']
					line_text = ' ({0}-{1})'.format(start_line, stop_line) if start_line != stop_line else ' ({0})'.format(start_line)
					ret.append('{0}: {1}{2}'.format(value['name'], value['type'], line_text))
			return '\n'.join(ret)
		else:
			return ''

	def _check_intersection(self, other):
		""" Check that intersection of two objects is congruent, i.e. that they have identical information in the intersection """
		props = ['_callables_db', '_reverse_callables_db', '_modules_dict']
		for prop in props:
			self_dict = getattr(self, prop)
			other_dict = getattr(other, prop)
			keys_self = set(self_dict.keys())
			keys_other = set(other_dict.keys())
			intersection = keys_self & keys_other
			for key in intersection:
				if self_dict[key] != other_dict[key]:
					raise RuntimeError('Conflicting information between objects')

	def _get_callables_db(self):
		""" Getter for callables_db property """
		return self._callables_db

	def _get_reverse_callables_db(self):
		""" Getter for reverse_callables_db property """
		return self._reverse_callables_db

	def get_callable_from_line(self, module_file, lineno):
		""" Get the callable that the line number belongs to """
		module_name = _get_module_name_from_file_name(module_file)
		if module_name not in self._modules_dict:
			self.trace([module_file])
		ret = None
		for value in sorted(self._modules_dict[module_name], key=lambda x: x['code_id'][1]):
			if value['code_id'][1] <= lineno <= value['last_lineno']:
				ret = value['name']
			elif value['code_id'][1] > lineno:
				break
		return ret if ret else module_name

	def trace(self, file_names):
		r"""
		Generates a list of module callables (functions, classes, methods and class properties) and gets their attributes (callable type, file name, lines span)

		:param	file_names: File names containing the modules to trace
		:type	file_names: list
		:raises:
		 * IOError (File *[file_name]* could not be found)

		 * RuntimeError (Argument \`file_names\` is not valid)
		"""
		if file_names and ((not isinstance(file_names, list)) or (isinstance(file_names, list) and any([not isinstance(item, str) for item in file_names]))):
			raise RuntimeError('Argument `file_names` is not valid')
		for file_name in file_names:
			if not os.path.exists(file_name):
				raise IOError('File {0} could not be found'.format(file_name))
		file_names = [item.replace('.pyc', '.py') for item in file_names]
		for file_name in file_names:
			if file_name not in self._file_names:
				module_name = _get_module_name_from_file_name(file_name)
				with open(file_name, 'r') as fobj:
					lines = fobj.readlines()
				tree = ast.parse(''.join(lines))
				aobj = _AstTreeScanner(file_name, lines)
				aobj.visit(tree)
				fake_node = putil.misc.Bundle(lineno=len(lines)+1, col_offset=-1)
				aobj._close_callable(fake_node, force=True)
				self._class_names += aobj._class_names[:]
				self._module_names.append(module_name)
				for name, item in aobj._callables_db.items():
					self._callables_db[name] = item
				for name, item in aobj._reverse_callables_db.items():
					self._reverse_callables_db[name] = copy.deepcopy(item)
				# Split into modules
				self._modules_dict[module_name] = []
				for entry in [item for item in self._callables_db.values() if item['name'].startswith('{0}.'.format(module_name))]:
					self._modules_dict[module_name].append(entry)
		self._file_names = list(set(self._file_names+[item.replace('.pyc', '.py') for item in file_names]))

	callables_db = property(_get_callables_db, None, None, doc='Module(s) callables database')
	"""
	Returns the callables database

	:rtype: dictionary

	The callable database is a dictionary that has the following structure:

	* **full callable name** *(string)* -- Dictionary key. Elements in the callable path are separated by periods (:code:`'.'`). For example, method :code:`my_method()` from class :code:`MyClass` from module :code:`my_module`
	  appears as :code:`'my_module.MyClass.my_method'`

	 * **callable properties** *(dictionary)* -- Dictionary value. The elements of this dictionary are:

	  * **type** *(string)* -- :code:`'class'` for classes, :code:`'meth'` for methods, :code:`'func'` for functions or :code:`'prop'` for properties or class attributes

	  * **code_id** *(tuple or None)* -- A tuple with the following elements:

	    * **file name** *(string)* -- the first element contains the file name where the callable can be found

	    * **line number** *(integer)* -- the second element contains the line number in which the callable code starts (including decorators)

	  * **last_lineno** *(integer)* -- line number in which the callable code ends (including blank lines)
	"""
	reverse_callables_db = property(_get_reverse_callables_db, None, None, doc='Reverse module(s) callables database')
	"""
	Returns the reverse callables database

	:rtype: dictionary

	The reverse callable database is a dictionary that has the following structure:

	 * **callable id** *(tuple)* -- Dictionary key. Two-element tuple in which the first tuple element is the file name where the callable is defined and the second tuple element is the line number
	   where the callable definition starts

	 * **full callable name** *(string)* -- Dictionary value. Elements in the callable path are separated by periods (:code:`'.'`). For example, method :code:`my_method()` from class :code:`MyClass` from module :code:`my_module`
	   appears as :code:`'my_module.MyClass.my_method'`
	"""


class _AstTreeScanner(ast.NodeVisitor):	#pylint: disable=R0902
	""" Get all callables from a given module """
	def __init__(self, file_name, lines):
		super(_AstTreeScanner, self).__init__()
		self._lines = lines
		self._wsregexp = re.compile(r'^(\s*).+')
		self._file_name = file_name.replace('.pyc', '.py')
		self._module = _get_module_name_from_file_name(file_name)
		self._indent_stack = [{'level':0, 'type':'module', 'prefix':'', 'full_name':None}]
		self._callables_db, self._reverse_callables_db = {}, {}
		self._class_names = []
		self._num_decorators = 0

	def _close_callable(self, node, force=False):
		""" Record last line number of callable """
		if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str) and (node.col_offset < 0):
			return
		try:
			lineno = node.lineno
		except:	#pylint: disable=W0702
			return
		if (not force) and self._callables_db:
			element_full_name = self._indent_stack[-1]['full_name']
			code_id = self._callables_db[element_full_name].get('code_id', None)
			if code_id and (lineno <= code_id[1]+self._num_decorators+1) and (self._indent_stack[-1]['type'] != 'prop'):
				return
		indent = self._get_indent(node)
		count = -1
		while count >= -len(self._indent_stack):
			element_full_name = self._indent_stack[count]['full_name']
			stack_indent = self._indent_stack[count]['level']
			if element_full_name and (not self._callables_db[element_full_name]['last_lineno']) and (force or (indent <= stack_indent) and (lineno-1 >= self._callables_db[element_full_name]['code_id'][1])):
				self._callables_db[element_full_name]['last_lineno'] = lineno-1
				self._num_decorators = 0
			if indent > stack_indent:
				break
			count -= 1

	def _get_indent(self, node):
		""" Get indentation level """
		lineno = node.lineno
		if lineno > len(self._lines):
			return -1
		wsindent = self._wsregexp.match(self._lines[lineno-1])
		return len(wsindent.group(1))

	def _in_class(self, node):
		""" Find if callable is function or method """
		indent = self._get_indent(node)
		for indent_dict in reversed(self._indent_stack):	# pragma: no branch
			if (indent_dict['level'] < indent) or (indent_dict['type'] == 'module'):
				return indent_dict['type'] == 'class'	# pylint: disable=W0631

	def _pop_indent_stack(self, node, node_type=None, action=None):
		indent = self._get_indent(node)
		while ((indent <= self._indent_stack[-1]['level']) and (self._indent_stack[-1]['type'] != 'module')) or (self._indent_stack[-1]['type'] == 'prop'):
			self._indent_stack.pop()
		name = (node.targets[0].id if hasattr(node.targets[0], 'id') else node.targets[0].value.id) if node_type == 'prop' else node.name
		element_full_name = '.'.join([self._module]+[indent_dict['prefix'] for indent_dict in self._indent_stack if indent_dict['type'] != 'module']+[name])+('({0})'.format(action) if action else '')
		self._indent_stack.append({'level':indent, 'prefix':name, 'type':node_type, 'full_name':element_full_name})
		return element_full_name

	def generic_visit(self, node):
		""" Generic node """
		self._close_callable(node)
		super(_AstTreeScanner, self).generic_visit(node)

	def visit_Assign(self, node):	#pylint: disable=C0103
		""" Assignment walker (to parse class properties defined via the property() function) """
		self._close_callable(node)
		# It may also be a class attribute that is not a property, record it anyway, no harm in doing so as it is not attached to a callable
		if self._in_class(node):
			element_full_name = self._pop_indent_stack(node, 'prop')
			code_id = (self._file_name, node.lineno)
			self._callables_db[element_full_name] = {'name':element_full_name, 'type':'prop', 'code_id':code_id, 'last_lineno':node.lineno}
			self._reverse_callables_db[code_id] = element_full_name
			# Get property actions
			super(_AstTreeScanner, self).generic_visit(node)

	def visit_ClassDef(self, node):	#pylint: disable=C0103
		""" Class walker """
		self._close_callable(node)
		element_full_name = self._pop_indent_stack(node, 'class')
		code_id = (self._file_name, node.lineno)
		self._class_names.append(element_full_name)
		self._callables_db[element_full_name] = {'name':element_full_name, 'type':'class', 'code_id':code_id, 'last_lineno':None}
		self._reverse_callables_db[code_id] = element_full_name
		self.generic_visit(node)

	def visit_FunctionDef(self, node):	#pylint: disable=C0103
		""" Function/method walker """
		self._close_callable(node)
		in_class = self._in_class(node)
		decorator_list = [dobj.id if hasattr(dobj, 'id') else dobj.attr for dobj in node.decorator_list if hasattr(dobj, 'id') or hasattr(dobj, 'attr')]
		self._num_decorators = len(decorator_list)
		action = 'getter' if 'property' in decorator_list else ('setter' if 'setter' in decorator_list else ('deleter' if 'deleter' in decorator_list else None))
		element_type = 'meth' if in_class else 'func'
		element_full_name = self._pop_indent_stack(node, element_type, action=action)
		code_id = (self._file_name, node.lineno)
		self._callables_db[element_full_name] = {'name':element_full_name, 'type':element_type, 'code_id':code_id, 'last_lineno':None}
		self._reverse_callables_db[code_id] = element_full_name
		self.generic_visit(node)
