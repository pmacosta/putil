# pinspect.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import copy, funcsigs, inspect, os, re, sys, types

import putil.misc


###
# Functions
###
def _get_code_id(obj, file_name=None, offset=0):
	""" Return unique identity tuple to individualize callable object """
	if hasattr(obj, 'func_code') and (obj.func_code.co_filename != '<string>'):
		return (os.path.realpath(obj.func_code.co_filename), obj.func_code.co_firstlineno)
	elif file_name:
		return (file_name, obj.func_code.co_firstlineno+offset)


def _is_parg(arg):
	""" Returns True if arg argument is the name of a positional variable argument (i.e. *pargs) """
	return (len(arg) > 1) and (arg[0] == '*') and (arg[1] != '*')


def _is_kwarg(arg):
	""" Returns True if arg argument is the name of a keyword variable argument (i.e. **kwargs) """
	return (len(arg) > 2) and (arg[:2] == '**')


def _line_tokenizer(lines):	#pylint: disable=R0914,R0915
	""" Perform all matches on source file line """
	docstring_start_regexp_1 = re.compile(r'^.*r?""".*')
	docstring_start_regexp_2 = re.compile(r"^.*r?'''.*")
	single_line_docstring_regexp_1 = re.compile(r'^.*r?""".*""".*$')
	single_line_docstring_regexp_2 = re.compile(r"^.*r?'''.*'''.*$")
	class_regexp = re.compile(r'^(\s*)class\s*(\w+)\s*[\(|\:]')
	func_regexp = re.compile(r'^(\s*)def\s*(\w+)\s*\(')
	prop_regexp = re.compile(r'^(\s*)(\w+)\s*=\s*property\(')
	get_prop_regexp = re.compile(r'^(\s*)@(property|property\.getter)\s*$')
	set_prop_regexp = re.compile(r'^(\s*)@(\w+)\.setter\s*$')
	del_prop_regexp = re.compile(r'^(\s*)@(\w+)\.deleter\s*$')
	decorator_regexp = re.compile(r'^(\s*)@(.+)')
	import_regexp = re.compile(r'^(\s*)import\s+')
	from_regexp = re.compile(r'^(\s*)from\s+')
	multi_line_string, multi_line_string_line_num, cont_flag, cont_lines, cont_line_num = False, 0, False, [], 0
	num_lines = len(lines)-1
	for line_num, line in enumerate(lines, start=1):
		# Multi line docstring support. LINE ORDER IS IMPORTANT!!!
		docstring_start_1 = (docstring_start_regexp_1.match(line) != None) and (not single_line_docstring_regexp_1.match(line))
		docstring_start_2 = (docstring_start_regexp_2.match(line) != None) and (not single_line_docstring_regexp_2.match(line))
		docstring_start = docstring_start_1 or docstring_start_2
		if docstring_start_1:
			single_line_docstring_regexp = single_line_docstring_regexp_1
			delimiter = '"""'
		elif docstring_start_2:
			single_line_docstring_regexp = single_line_docstring_regexp_2
			delimiter = "'''"
		multi_line_string_line_num = line_num if (not multi_line_string) and docstring_start else multi_line_string_line_num
		#multi_line_string = docstring_start if not multi_line_string else multi_line_string
		multi_line_string = docstring_start if not multi_line_string else multi_line_string
		#
		if not multi_line_string:
			line = line.rstrip()
			cont_line_num = line_num if not cont_lines else cont_line_num
			if (line.endswith('\\') or line.endswith(',')) or cont_flag:
				cont_flag = line.endswith('\\') or line.endswith(',')
				line = line.strip() if cont_lines else line
				cont_lines.append(line[:-1] if cont_flag and line.endswith('\\') else line)
				if cont_flag:
					continue
			if cont_lines:
				line = ''.join(cont_lines)
				line_num = cont_line_num
				cont_lines = []
				cont_line_num = 0
			class_match = class_regexp.match(line)
			class_indent, class_name = class_match.groups() if class_match else (None, None)
			func_match = func_regexp.match(line)
			func_indent, func_name = func_match.groups() if func_match else (None, None)
			prop_match = prop_regexp.match(line)
			prop_indent, prop_name = prop_match.groups() if prop_match else (None, None)
			get_match, set_match, del_match = get_prop_regexp.match(line), set_prop_regexp.match(line), del_prop_regexp.match(line)
			decorator_match = decorator_regexp.match(line)
			import_match, from_match = import_regexp.match(line), from_regexp.match(line)
			namespace_indent, namespace_match = import_match.group(1) if import_match else (from_match.group(1) if from_match else None), import_match or from_match
			line_match = class_match or func_match or namespace_match or prop_match
			yield num_lines, line_num, line, line_match, class_match, class_indent, class_name, func_match, func_indent, func_name, prop_match, prop_indent, prop_name, get_match, set_match, del_match, decorator_match,\
				namespace_indent, namespace_match
		elif multi_line_string:
			multi_line_string = False if single_line_docstring_regexp.match(line) else (True if (line_num == multi_line_string_line_num) else (not (delimiter in line)))	#pylint: disable=C0325
			yield num_lines, line_num, line, False, False, 0, None, False, 0, None, False, 0, None, False, False, False, False, 0, False


def _private_props(obj):
	""" Generator to yield private properties of object """
	private_prop_regexp = re.compile('_[^_]+')
	for obj_name in [obj_name for obj_name in dir(obj) if private_prop_regexp.match(obj_name) and (not callable(getattr(obj, obj_name))) and ('regexp' not in obj_name)]:
		yield obj_name


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
	if root_obj not in modules_list:
		modules_list.append(root_obj)
	for module_obj, module_name in [(getattr(root_obj, module_name), module_name) for module_name in dir(root_obj)]:
		if is_object_module(module_obj) and hasattr(module_obj, '__file__') and os.path.split(getattr(module_obj, '__file__'))[0].startswith(root_dir) and (module_name not in modules_traced):
			modules_traced, modules_list = loaded_package_modules(module_obj, (root_dir, modules_traced, modules_list))
	return (modules_traced, modules_list) if recursive else modules_list


def _replace_tabs(text):
	""" Section 2.1.8 Indentation of Python 2.7.9 documentation:
	First, tabs are replaced (from left to right) by one to eight spaces such that the total number of characters up to and including the replacement is a multiple of eight (this is intended to be the same rule as used by Unix).
	A form feed character may be present at the start of the line; it will be ignored for the indentation calculations above. Form feed characters occurring elsewhere in the leading whitespace have an undefined effect
	(for instance, they may reset the space count to zero)
	"""
	return -1 if text == None else text.lstrip('\f').expandtabs()


###
# Classes
###
class Callables(object):	#pylint: disable=R0903,R0902
	r"""
	Generates a list of module callables (functions, classes, methods and class properties) and gets their attributes (callable type, file name, starting line number). Information from multiple modules can be stored in the
	callables database of the object by repeatedly calling :py:meth:`putil.pinspect.Callables.trace` with different module objects. A :py:class:`putil.pinspect.Callables` object retains knowledge of which modules have been traced
	so repeated calls to :py:meth:`putil.pinspect.Callables.trace` with the *same* module object will *not* result in module re-traces (and the consequent performance hit).

	Enclosed functions and classes are supported. Class property action functions (getter, deleter and setter) in a different module than the one in which the class is defined are also supported both in module classes as well
	as in enclosed classes. For the latter only property action functions for which the module in which they are defined is imported via ``import`` or ``from [module name] import [...]`` are supported.

	:param obj: Module object(s)
	:type	obj: object or iterable of objects
	:rtype: :py:class:`putil.pinspect.Callables` object
	:raises:
	 * RuntimeError (Argument \`obj\` is not valid)

	 * RuntimeError (Attribute \`*[attribute_name]*\` of property \`*[property_name]*\` not found in callable database)
	"""
	def __init__(self, obj=None):
		self._module_names, self._class_names, self._callables_db, self._reverse_callables_db, self._closure_class_obj_list = set(), set(), {}, {}, []
		self._whitespace_regexp = re.compile(r'^(\s*)(\w*)')
		self._namespece_regexp = re.compile(r"name '(\w+)' is not defined")
		if obj:
			self.trace(obj)

	def __copy__(self):
		cobj = Callables()
		for prop_name in _private_props(self):
			setattr(cobj, prop_name, copy.deepcopy(getattr(self, prop_name)))
		return cobj

	def __eq__(self, other):
		# _prop_dict is a class variable used to pass data between sub-functions in the trace operation, not material to determine if two objects are the same
		return all([sorted(getattr(self, attr)) == sorted(getattr(other, attr)) for attr in _private_props(self) if attr != '_prop_dict'])

	def __repr__(self):
		return 'putil.pinspect.Callables({0})'.format('[{0}]'.format(', '.join(["sys.modules['{0}']".format(module_name) for module_name in sorted(self._module_names)])) if self._module_names else '')

	def __str__(self):
		ret = list()
		ret.append('Modules:')
		for module_name in sorted(self._module_names):
			ret.append('   {0}'.format(module_name))
		ret.append('Classes:')
		for class_name in sorted(self._class_names):
			ret.append('   {0}'.format(class_name))
		for key in sorted(self._callables_db.keys()):
			ret.append('{0}: {1}{2}'.format(key, self._callables_db[key]['type'], ' ({0})'.format(self._callables_db[key]['code_id'][1]) if self._callables_db[key]['code_id'] else ''))
			if self._callables_db[key]['type'] == 'prop':
				for attr in sorted(self._callables_db[key]['attr']):
					ret.append('   {0}: {1}'.format(attr, self._callables_db[key]['attr'][attr]))
			elif self._callables_db[key].get('link', None):
				for link_dict in self._callables_db[key]['link']:
					ret.append('   {0} of: {1}'.format(link_dict['action'], link_dict['prop']))
		return '\n'.join(ret)

	def _get_callables_db(self):
		""" Getter for callables_db property """
		return self._callables_db

	def _get_closures(self, obj):	#pylint: disable=R0912,R0914,R0915
		"""
		Find closures within module.
		Implement a mini-parser, finding "@", "def" or "class" start of lines while keeping track of indentation levels
		Have to keep track of imports because technically class properties can be functions from other modules. Closure classes code is executed with recorded imports at top, a class object is created and then traced as "usual"
		"""
		# Read module file
		module_file_name = os.path.realpath('{0}.py'.format(os.path.splitext(obj.__file__)[0]))
		with open(module_file_name, 'rb') as file_obj:
			module_lines = file_obj.read().split('\n')
		# Initialize mini-parser variables
		indent_stack, import_stack, decorator_num, attr_name, closure_class, closure_class_list = [{'level':0, 'prefix':obj.__name__, 'type':'module'}], [{'level':0, 'type':'module', 'line':None}], None, '', False, []
		for num_lines, line_num, line, line_match, class_match, class_indent, class_name, func_match, func_indent, func_name, prop_match, prop_indent, prop_name, get_match, set_match, del_match, decorator_match,\
				namespace_indent, namespace_match in _line_tokenizer(module_lines):
			# To allow for nested decorators when a property is defined via a decorator, remember property decorator line and use that for the callable line number
			attr_name = attr_name if attr_name else '(getter)' if get_match else ('(setter)' if set_match else ('(deleter)' if del_match else ''))
			decorator_num = line_num if decorator_match and (decorator_num == None) else decorator_num
			element_num = decorator_num if decorator_num else line_num
			indent = len(_replace_tabs(class_indent if class_match else (func_indent if func_match else (prop_indent if prop_match else namespace_indent)))) if line_match else -1
			if namespace_match:
				while (indent < import_stack[-1]['level']) and (import_stack[-1]['type'] != 'module'):
					import_stack.pop()
				# Top-level imports are handled by including the whole module code before the extracted enclosed class, no need to add them to the enclosed class namespace
				if indent:	# Top-level imports are handled by including the whole module code before the extracted enclosed class, no need to add them to the enclosed class namespace
					import_stack.append({'level':indent, 'line':line.lstrip(), 'type':'not module'})
			elif class_match or func_match or prop_match:
				# Remove all blocks at the same level to find out the indentation "parent"
				deindent = False
				# Update callable stack
				while (indent <= indent_stack[-1]['level']) and (indent_stack[-1]['type'] != 'module'):
					deindent = True
					indent_stack.pop()
				# Update enclosed class namespace stack
				while (indent < import_stack[-1]['level']) and (import_stack[-1]['type'] != 'module'):
					import_stack.pop()
				if class_match:
					closure_class = indent_stack[-1]['type'] != 'module'
					if closure_class and deindent:
						self._process_enclosed_class(line, closure_class, closure_class_list, line_num, num_lines)
					full_class_name = '{0}.{1}'.format(indent_stack[-1]['prefix'], class_name)
					self._class_names.add(full_class_name)
					if closure_class:
						namespace_code = ['###', '# Start of enclosed class', '###']+[import_dict['line'] for import_dict in import_stack[1:]]
						eval_line = 'tvar = {0}'.format(class_name)
						closure_class_list.append({'file':module_file_name, 'name':full_class_name, 'code':[], 'namespace':module_lines+namespace_code, 'indent':indent, 'eval':eval_line, 'lineno':line_num})
					self._callables_db[full_class_name] = {'type':'class', 'code_id':(module_file_name, line_num), 'attr':None, 'link':[]}
					self._reverse_callables_db[(module_file_name, element_num)] = full_class_name
				element_full_name = '{0}.{1}{2}'.format(indent_stack[-1]['prefix'], prop_name if prop_match else (class_name if class_name else func_name), attr_name)
				if (prop_match or func_name) and (element_full_name not in self._callables_db):
					self._callables_db[element_full_name] = {'type':'prop' if prop_match else ('meth' if indent_stack[-1]['type'] == 'class' else 'func'), 'code_id':(module_file_name, element_num), 'attr':None, 'link':[]}
					self._reverse_callables_db[(module_file_name, element_num)] = element_full_name
				indent_stack.append({'level':indent, 'prefix':element_full_name, 'type':'class' if class_name else 'func'})
				# Reset property variables
				decorator_num, attr_name = None, ''
			closure_class = self._process_enclosed_class(line, closure_class, closure_class_list, line_num, num_lines)

	def _get_prop_components(self, prop_name, prop_obj, closure_file_name=None, closure_offset=0):
		""" Find getter, setter, deleter functions of a property """
		attr_dict = {}
		for attr_name, attr_obj in [(attr_name, getattr(prop_obj, attr_name)) for attr_name in ['fdel', 'fget', 'fset'] if hasattr(prop_obj, attr_name) and getattr(getattr(prop_obj, attr_name), '__call__', None)]:
			if attr_obj.__name__ == '<lambda>':
				func_name = '{0}.{1}_lambda'.format(prop_name, attr_name)
			else:
				if attr_obj.__module__  and (attr_obj.__module__ not in self._module_names):
					self._trace_module(sys.modules[attr_obj.__module__])
				# Get to the object of the actual, undecorated function
				while getattr(attr_obj, '__wrapped__', None):
					attr_obj = getattr(attr_obj, '__wrapped__')
				attr_code_id = _get_code_id(attr_obj, closure_file_name, closure_offset)
				if attr_code_id not in self._reverse_callables_db:
					#for name in sorted(self._callables_db.keys()):
					#	print '{0}: {1}'.format(name, self._callables_db[name])
					#print 'Attribute `{0}` of property `{1}` is a closure, do not know how to deal with it\ncode_id: {2}'.format(attr_name, prop_name, attr_code_id)
					raise RuntimeError('Attribute `{0}` of property `{1}` not found in callable database'.format(attr_name, prop_name))
				func_name = self._reverse_callables_db[attr_code_id]
				prop_dict = {'prop':prop_name, 'action':attr_name}
				if prop_dict not in self._callables_db[func_name]['link']:
					self._callables_db[func_name]['link'].append(prop_dict)
			attr_dict[attr_name] = func_name	#pylint: disable=W0631
		self._callables_db[prop_name]['attr'] = attr_dict if attr_dict else None

	def _get_reverse_callables_db(self):
		""" Getter for reverse_callables_db property """
		return self._reverse_callables_db

	def _process_enclosed_class(self, line, closure_class, closure_class_list, line_num, num_lines):	#pylint: disable=R0913
		""" Process enclosed class: finish code snippet or add lines to enclosed class """
		if closure_class:
			line = _replace_tabs(line)
			start_space, content = self._whitespace_regexp.match(line).groups()
			for class_dict in closure_class_list:
				start_space_length = len(start_space)
				if class_dict['code'] and ((content and ((start_space_length <= class_dict['indent']) or (start_space_length == 0))) or ((line_num == num_lines) and (start_space_length > class_dict['indent']))):
					if (line_num == num_lines) and (start_space_length > class_dict['indent']):
						class_dict['code'].append(line[class_dict['indent']:])
					class_dict['code'].append(class_dict['eval'])
					self._closure_class_obj_list.append({'code':'\n'.join(class_dict['namespace']+class_dict['code']), 'file':class_dict['file'], 'name':class_dict['name'], 'lineno':class_dict['lineno']-len(class_dict['namespace'])})
					closure_class_list.pop()
				else:
					# Remove base indentation from lines, as the code is going to be executed via exec, which would give an error if there is extra whitespace at the beginning of all lines
					class_dict['code'].append(line[class_dict['indent']:])
			closure_class = bool(closure_class_list)
		return closure_class

	def _trace_class(self, obj, closure_file_name=None, closure_name=None, closure_offset=0):
		""" Trace class properties, methods have already been added to database by mini-parser """
		class_name = closure_name if closure_name else '.'.join([obj.__module__, obj.__name__])
		self._class_names.add(class_name)	# Classes are only traced once because modules are only traced once, no need to check if they are already traced
		for prop_name, prop_obj in [('.'.join([class_name, prop_name]), prop_obj) for prop_name, prop_obj in inspect.getmembers(obj) if isinstance(prop_obj, property)]:
			if prop_name not in self._callables_db:
				self._callables_db[prop_name] = {'type':'prop', 'code_id':None, 'attr':None, 'link':[]}
			self._get_prop_components(prop_name, prop_obj, closure_file_name, closure_offset)	# Find out which callables re the setter/getter/deleter of properties

	def _trace_module(self, obj):	#pylint: disable=R0914
		""" Generate a list of object callables (internal function, no argument validation)"""
		if obj.__name__ not in self._module_names:
			self._module_names.add(obj.__name__)
			# Closures need to be recorded before class tracing because some class properties might use closures
			self._get_closures(obj)
			# "Standard" (non closure) class tracing
			for class_obj in [class_obj for _, class_obj in inspect.getmembers(obj) if inspect.isclass(class_obj)]:
				self._trace_class(class_obj)
			# Closure class tracing, exec creates tvar variable which contains an unbound object of the closure class
			for class_obj in self._closure_class_obj_list:
				# The namespace recreating is inherently brittle because the imports can be conditional on variables, which affects the importing dynamically at runtime.
				# The approach is to try with all the (potentially conditional) imports first and if there is an import error, remove the offending import and try again
				error = True
				lines_removed = 0
				while error:
					try:
						#print '----'
						#print class_obj['code']
						#print '----'
						exec class_obj['code'] in locals()	#pylint: disable=W0122
						error = False
					except ImportError as exobj:
						module_name = exobj.message.split(' ')[-1]	#pylint: disable=E1101
					except:
						raise
					if error:
						# Remove "offending" import
						new_code = []
						in_class = False
						lines = class_obj['code'].split('\n')
						for line in lines[lines.index('# Start of enclosed class'):]:
							in_class = line.startswith('class') if not in_class else in_class
							namespace_line = line.startswith('import ') or line.startswith('from ') if not in_class else False
							if namespace_line:
								tokens = re.findall(r'[\w\.]+', line)
								modules = tokens[1:] if tokens[0] == 'import' else [tokens[1]]
								if module_name in modules:
									lines_removed += 1
									continue
							new_code.append(line)
						class_obj['code'] = '\n'.join(new_code)
				self._trace_class(tvar, class_obj['file'], class_obj['name'], class_obj['lineno']-1+lines_removed)	#pylint: disable=E0602

	def trace(self, obj):
		r"""
		Generates a list of module callables (functions, classes, methods and class properties) and gets their attributes (callable type, file name, starting line number)

		:param obj: Module object(s)
		:type	obj: object or iterable of objects
		:raises:
		 * RuntimeError (Argument \`obj\` is not valid)

		 * RuntimeError (Attribute \`*[attribute_name]*\` of property \`*[property_name]*\` not found in callable database)

		"""
		if (obj == None) or (not (inspect.ismodule(obj) or putil.misc.isiterable(obj))):
			raise RuntimeError('Argument `obj` is not valid')
		for obj in obj if putil.misc.isiterable(obj) else [obj]:
			if not inspect.ismodule(obj):
				raise RuntimeError('Argument `obj` is not valid')
			self._trace_module(obj)

	# Managed attributes
	callables_db = property(_get_callables_db, None, None, doc='Module(s) callables database')
	"""
	Returns the callables database

	:rtype: dictionary

	The callable database is a dictionary that has the following structure:

	* **full callable name** *(string)* -- Dictionary key. Elements in the callable path are separated by periods (:code:`'.'`). For example, method :code:`my_method()` from class :code:`MyClass` from module :code:`my_module`
	  appears as :code:`'my_module.MyClass.my_method'`

	 * **callable properties** *(dictionary)* -- Dictionary value. The elements of this dictionary are:

	  * **type** *(string)* -- :code:`'class'` for classes, :code:`'meth'` for methods, :code:`'func'` for functions or :code:`'prop'` for properties

	  * **code_id** *(tuple or None)* -- None if **type** is :code:`'prop'`, otherwise a tuple with the following elements:

	    * **file name** *(string)* -- the first element contains the file name where the callable can be found

	    * **line number** *(integer)* -- the second element contains the line number in which the callable code starts (including decorators)

	  * **attr** *(dictionary or None)* -- None if **type** is :code:`'class'`, :code:`'meth'`, :code:`'func'`, otherwise a dictionary with the following elements:

	   * **fget** *(string or None)* -- Name of the getter function or method associated with the property (if any)

	   * **fset** *(string or None)* -- Name of the setter function or method associated with the property (if any)

	   * **fdel** *(string or None)* -- Name of the deleter function or method associated with the property (if any)

	  * **link** *(dictionary or None)* -- None if callable is not the getter, setter or deleter of a property, otherwise a dictionary with the following elements:

	   * **prop** *(string)* -- Property the callable is associated with

	   * **action** *(string)* -- Property action the callable performs, one of :code:`'fget'`, :code:`'fset'` or :code:`'fdel'`

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
