# exh.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Exception handling classes, methods, functions and constants
"""

import sys
import copy
import types
import inspect

import putil.check
import putil.misc
import putil.tree

class ExHandle(object):	#pylint: disable=R0902
	""" Exception handling class """
	def __init__(self, obj):
		if (not inspect.isclass(obj)) and (not hasattr(obj, '__call__')):
			raise TypeError('Argument `obj` is of the wrong type')
		self._trace_obj = obj
		self._trace_obj_name = '{0}.{1}'.format(obj.__module__, obj.__name__)
		self._trace_obj_props = dict([(member, obj_type(self._trace_obj, member)) for member in dir(self._trace_obj) if member[0] != '_']) if inspect.isclass(obj) else {obj.__name__:'meth'}
		self._trace_list, self._tobj, self._extable, self._module_functions_extable, self._cross_usage_extable, self._exoutput, self._exproptype = None, None, None, None, None, None, None
		self._ex_list = list()

	def __copy__(self):
		cobj = ExHandle(obj=copy.copy(self._trace_obj))
		cobj._trace_obj_name = copy.copy(self._trace_obj_name)	#pylint: disable=W0212
		cobj._trace_obj_props = copy.copy(self._trace_obj_props)	#pylint: disable=W0212
		cobj._trace_list = copy.copy(self._trace_list)	#pylint: disable=W0212
		cobj._tobj = copy.copy(self._tobj)	#pylint: disable=W0212
		cobj._extable = copy.copy(self._extable)	#pylint: disable=W0212
		cobj._module_functions_extable = copy.copy(self._module_functions_extable)	#pylint: disable=W0212
		cobj._cross_usage_extable = copy.copy(self._cross_usage_extable)	#pylint: disable=W0212
		cobj._exoutput = copy.copy(self._exoutput)	#pylint: disable=W0212
		cobj._ex_list = copy.copy(self._ex_list)	#pylint: disable=W0212
		return cobj

	def __deepcopy__(self, memodict=None):
		memodict = dict() if memodict is None else memodict
		cobj = ExHandle(obj=copy.deepcopy(self._trace_obj))
		cobj._trace_obj_name = copy.deepcopy(self._trace_obj_name, memodict)	#pylint: disable=W0212
		cobj._trace_obj_props = copy.deepcopy(self._trace_obj_props)	#pylint: disable=W0212
		cobj._trace_list = copy.deepcopy(self._trace_list, memodict)	#pylint: disable=W0212
		cobj._tobj = copy.deepcopy(self._tobj, memodict)	#pylint: disable=W0212
		cobj._extable = copy.deepcopy(self._extable, memodict)	#pylint: disable=W0212
		cobj._module_functions_extable = copy.deepcopy(self._module_functions_extable, memodict)	#pylint: disable=W0212
		cobj._cross_usage_extable = copy.deepcopy(self._cross_usage_extable, memodict)	#pylint: disable=W0212
		cobj._exoutput = copy.deepcopy(self._exoutput, memodict)	#pylint: disable=W0212
		cobj._ex_list = copy.deepcopy(self._ex_list, memodict)	#pylint: disable=W0212
		return cobj

	def __str__(self):
		ret = ['Name....: {0}\nFunction: {1}\nType....: {2}\nMessage.: {3}\nChecked.: {4}'.format(ex['name'], ex['function'], self._ex_type_str(ex['type']), ex['msg'], ex['checked']) for ex in self._ex_list]
		return '\n\n'.join(ret)

	def _build_ex_tree(self, no_print=True):
		""" Construct exception tree from trace """
		tree_data = self._tree_data()
		if not tree_data:
			raise RuntimeError('No trace information')
		self._tobj = putil.tree.Tree()
		if not no_print:
			print putil.misc.pcolor('Building tree', 'blue')
		self._tobj.add(tree_data)
		if not no_print:
			print str(self._tobj)

	def _change_ex_tree_root_node(self, no_print=True):
		""" Make class name of interest root node """
		node = self._tobj.root_name
		# Look for first occurance of trace object name in tree nodes
		# self._otbj.nodes returns all nodes _sorted_ alphabetically
		for node in self._tobj.nodes:
			if self._trace_obj_name in node:
				break
		else:
			raise RuntimeError('Class {0} not in tree'.format(self._trace_obj_name))
		if not no_print:
			print putil.misc.pcolor('Making {0} root'.format(node), 'blue')
		self._tobj.make_root(node)
		if not no_print:
			print str(self._tobj)
		return node

	def _collapse_ex_tree(self, no_print=True):
		""" Eliminates nodes without exception data """
		if not no_print:
			print putil.misc.pcolor('Collapsing tree', 'blue')
		self._tobj.collapse(self._tobj.root_name)
		if not no_print:
			print str(self._tobj)

	def _condense_ex_tree_exceptions(self, no_print):
		""" Condense exceptions to class methods nodes """
		if not no_print:
			print putil.misc.pcolor('Condensing exceptions to class methods and attributes', 'blue')
		self._extable = dict()
		children = self._tobj.get_children(self._tobj.root_name)
		if children:
			for child in children:
				exdesc_list = list()
				for name in self._tobj._get_subtree(child):	#pylint: disable=W0212
					exdesc_list += self._tobj.get_data(name)
				self._extable[child.replace(self._trace_obj_name+'.', '').split('.')[0].strip().replace('_set_', '')] = sorted(list(set(exdesc_list)))
		else:
			self._extable[self._tobj.root_name.replace(self._trace_obj_name+'.', '').split('.')[0].strip().replace('_set_', '')] = sorted(list(set(self._tobj.get_data(self._tobj.root_name))))

	def _create_ex_table_output(self, no_print=True):
		""" Create final exception table output """
		if not no_print:
			print putil.misc.pcolor('Creating final exception table output', 'blue')
		if not self._extable:
			raise RuntimeError('No exception table data')
		self._exoutput = list()
		for child in sorted(self._extable.keys()):
			self._exoutput.append('')
			self._exoutput.append('<START MEMBER> {0}'.format(child))
			if len(self._extable[child]) == 1:
				self._exoutput.append(':raises: {0}'.format(self._extable[child][0]))
			else:
				self._exoutput.append(':raises:')
				for exname in self._extable[child]:
					self._exoutput.append(' * {0}'.format(exname))
					if exname != self._extable[child][-1]:
						self._exoutput.append('')
			self._exoutput.append('<STOP MEMBER> {0}'.format(child))

	def _deduplicate_ex_table(self, no_print=True):
		""" Remove exceptions that could be in 'Same as [...]' entry or 'Same as [...] enties that have the same base exceptions """
		if not no_print:
			print putil.misc.pcolor('De-duplicate exception table', 'blue')
		# Remove exceptions that could be in 'Same as [...]' entry
		for key in self._extable:
			self._extable[key] = [member for member in self._extable[key] if member not in self._cross_usage_extable[key]]
		# Remove 'Same as [...]' entries that have the same exceptions
		for key in sorted(self._extable.keys()):
			bex_list = [member for member in self._extable[key] if member.find('Same as') == -1]
			sex_list = [member for member in self._extable[key] if member.find('Same as') == 0]
			csex = sex_list[:]
			for num1, sex1 in enumerate(csex):
				for num2, sex2 in enumerate(csex):
					if num2 > num1:
						sex1_key = sex1.split('.')[-1][:-1]
						sex2_key = sex2.split('.')[-1][:-1]
						if self._cross_usage_extable[sex1_key] == self._cross_usage_extable[sex2_key]:
							del sex_list[num2]
			# Homogenize 'Same as [...] structures to cases sucha as a 'Same as [...]' pointing to another 'Same as [...]'.
			# REMOVE print putil.misc.pcolor(str(self._cross_usage_extable), 'red')
			csex = sex_list[:]
			for num, sex2 in enumerate(sorted(csex)):
				for sex1 in sorted(self._cross_usage_extable.keys()):
					sex2_key = sex2.split('.')[-1][:-1]
					# REMOVE print sex1
					# REMOVE print sex2_key
					if self._cross_usage_extable[sex1] == self._cross_usage_extable[sex2_key]:
						# REMOVE print putil.misc.pcolor('Mach!', 'green')
						# REMOVE print 'Before: {0}'.format(sex_list[num])
						sex_list[num] = 'Same as :py:{0}:`{1}.{2}`'.format(self._trace_obj_props[sex1], self._trace_obj_name, sex1)
						# REMOVE print 'After: {0}'.format(sex_list[num])
						break
					# REMOVE print
			self._extable[key] = sorted(bex_list)+sorted(sex_list)

	def _detect_ex_tree_cross_usage(self, no_print=True):
		""" Replace exceptions from other class methods with 'Same as [...]' construct """
		if not no_print:
			print putil.misc.pcolor('Detecting cross-usage', 'blue')
		module = '.'.join(self._trace_obj_name.split('.')[:-1])
		children = self._tobj.get_children(self._tobj.root_name)
		self._module_functions_extable = dict()
		self._exproptype = dict()
		for child1 in sorted(children):
			grandchildren = sorted(self._tobj.get_children(child1)[:])
			for grandchild in grandchildren:
				for child2 in sorted(children)[::-1]:
					if child1 != child2:
						name_grandchild = grandchild[len(child1)+1:]
						name_child = child2
						name_module_function = module+'.'+(grandchild.split('.')[-1])
						fname = child2[:]
						# Method/attribute within class
						if name_child == name_grandchild:
							self._tobj.delete(grandchild)
							fname = (self._trace_obj_name+'.'+(fname.replace(self._trace_obj_name+'.', '').split('.')[0])).replace('_set_', '')
							self._tobj.add({'name':child1, 'data':'Same as :py:{0}:`{1}`'.format(self._trace_obj_props[fname.split('.')[-1]], fname)})
							break
						# Method/attribute/function within module
						elif grandchild.endswith(name_module_function):
							fname = (self._trace_obj_name+'.'+(fname.replace(self._trace_obj_name+'.', '').split('.')[0])).replace('_set_', '')
							self._tobj.add({'name':child1, 'data':'Same as :py:{0}:`{1}`'.format(self._trace_obj_props[fname.split('.')[-1]], name_module_function)})
							self._module_functions_extable[name_module_function] = self._tobj.get_data(grandchild)
							self._tobj.delete(grandchild)
							break
		if not no_print:
			print str(self._tobj)

	def _detect_top_level_equality(self, no_print=True):	#pylint: disable=R0912,R0914
		""" Replace exceptions that are the same (but not because of using antoerh method/attribute) 'Same as [...]' construct """
		if not no_print:
			print putil.misc.pcolor('Detecting top_level equality', 'blue')
		new_table = dict()
		for num1, key1 in enumerate(sorted(self._extable.keys())):
			for num2, key2 in enumerate(sorted(self._extable.keys())):
				# REMOVE print key1
				# REMOVE print key2
				# REMOVE print self._extable[key1]
				# REMOVE print self._extable[key2]
				if (num2 > num1) and (key2 not in new_table) and ((self._cross_usage_extable[key1] == self._cross_usage_extable[key2])):
					if key1 not in new_table:
						new_table[key1] = self._extable[key1]
					# REMOVE print 'Match!'
					new_table[key2] = ['* Same as :py:{0}:`{1}`'.format(obj_type(self._trace_obj, key1), self._trace_obj_name+'.'+key1)]
				# REMOVE print
			if key1 not in new_table:
				new_table[key1] = self._extable[key1]
		self._extable = new_table
		if not no_print:
			print str(self._tobj)


	def _eliminate_ex_tree_prefix(self, node, no_print=True):
		""" Remove prefix (usually main.__main__ or simmilar) from exception tree """
		# Find start of trace object name in root name and delete what comes before that
		index = node.find(self._trace_obj_name)
		if index != 0:
			prefix = node[:index-1]
			if not no_print:
				print putil.misc.pcolor('Removing prefix {0}'.format(prefix), 'blue')
			self._tobj.remove_prefix(prefix)
		if not no_print:
			print str(self._tobj)

	def _expand_same_ex_list(self, data, module_function_ex, start=False, indent=''):
		""" Create exception list where the 'Same as [...]' entries have been replaced for the exceptions in the method/attribute they point to """
		#REMOVE print indent+'Got data {0}'.format(data)
		#REMOVE print indent+'Got start {0}'.format(start)
		ret = [ex_member for ex_member in data if ex_member.find('Same as') == -1] if not start else list()
		sex_members = [ex_member.split('.')[-1][:-1] if self._trace_obj_name.split('.')[-1] in ex_member else ex_member[ex_member.find('`')+1:-1] for ex_member in data if ex_member.find('Same as') != -1]
		#REMOVE print indent+'sex_member: {0}'.format(sex_members)
		#REMOVE print indent+'initial ret: {0}'.format(ret)
		for member in sex_members:
			#REMOVE print indent+'Expanding {0}'.format(member)
			ret += (self._extable[member] if member.find('.') == -1 else module_function_ex[member])
		ret = sorted(list(set(ret)))
		#REMOVE print indent+'after sex_member expansion ret: {0}'.format(ret)
		if sex_members:
			#REMOVE print indent+'Recurring...'
			ret = self._expand_same_ex_list(ret[:], module_function_ex, start=False, indent=indent+(3*' '))
		ret = sorted(list(set(ret)))
		#REMOVE print indent+'after recursion ret: {0}'.format(ret)
		#REMOVE print indent+'Returning...'
		return ret

	def _ex_type_str(self, extype):	#pylint: disable-msg=R0201
		""" Returns a string corresponding to the exception type """
		return str(extype)[str(extype).rfind('.')+1:str(extype).rfind("'")]

	def _flatten_ex_tree(self, no_print=True):
		""" Flatten exception tree around class name hierarchy nodes """
		if not no_print:
			print putil.misc.pcolor('Flattening hierarchy', 'blue')
		obj_hierarchy = self._trace_obj_name.split('.')
		sub_trees = ['.'.join(obj_hierarchy[:num]) for num in range(len(obj_hierarchy), 0, -1)]	# List of hiearchical nodes from leaf to root of trace object name, i.e. ['a.b.c', 'a.b', 'a']
		for sub_tree in sub_trees:
			if not no_print:
				print '\tFlattening on {0}'.format(sub_tree)
			for node in self._tobj.nodes:
				if node.endswith('.{0}'.format(sub_tree)):
					self._tobj.flatten_subtree(node)
		if not no_print:
			print str(self._tobj)

	def _format_msg(self, msg, edata):	#pylint: disable=R0201
		""" Substitute parameters in exception message """
		edata = edata if isinstance(edata, list) else [edata]
		for field in edata:
			if 'field' not in field:
				raise ValueError('Key `field` not in field definition')
			if 'value' not in field:
				raise ValueError('Key `value` not in field definition')
			if '*[{0}]*'.format(field['field']) not in msg:
				raise RuntimeError('Field {0} not in exception message'.format(field['field']))
			msg = msg.replace('*[{0}]*'.format(field['field']), field['value'])
		return msg

	def _generate_cross_usage_table(self, no_print=True):
		""" Recursively expand 'Same as [...] entries """
		if not no_print:
			print putil.misc.pcolor('Generating cross-usage expanded exception table', 'blue')
		self._cross_usage_extable = dict()
		for key in self._extable:
			# REMOVE if key == 'get_node_children':
			# REMOVE 	print key
			self._cross_usage_extable[key] = self._expand_same_ex_list(self._extable[key], self._module_functions_extable, start=True)
			# REMOVE if key == 'get_node_children':
			# REMOVE 	print self._cross_usage_extable[key]
			# REMOVE 	print
			# REMOVE print

	def _prune_ex_tree(self, no_print=True):
		""" Prune tree (delete trace object methods/attributes that have no exceptions """
		if not no_print:
			print putil.misc.pcolor('Prunning tree', 'blue')
		children = self._tobj.get_children(self._tobj.root_name)
		for child in children:
			if not self._tobj.get_data(child):
				self._tobj.delete(child)
		if not no_print:
			print str(self._tobj)

	def _ptable(self, name):	#pylint: disable=C0111
		data = self._tobj.get_data(name)
		ret = 'Node: {0}\n{1}\n\n'.format(name, '\n'.join(sorted(data))) if data else ''
		for child in self._tobj.get_children(name):
			ret += self._ptable(child)
		return ret

	def _tree_data(self):	#pylint: disable-msg=R0201
		""" Returns a list of dictionaries suitable to be used with putil.tree module """
		return [{'name':ex['function'], 'data':'{0} ({1})'.format(self._ex_type_str(ex['type']), ex['msg'])} for ex in self._ex_list]

	def _sort_ex_table_members(self, no_print):
		""" Sort exceptions with 'Same as [...]' at the end, and both 'sections' sorted alphabetically """
		if not no_print:
			print putil.misc.pcolor('Sorting exception table members', 'blue')
		for key in self._extable:
			data = self._extable[key]
			bex = [exname for exname in data if 'Same as' not in exname]
			sex = [exname for exname in data if 'Same as' in exname]
			self._extable[key] = sorted(list(set(bex)))+sorted(list(set(sex)))

	def build_ex_tree(self, no_print=True):	#pylint: disable=R0912,R0914,R0915
		""" Builds exception tree """
		self._build_ex_tree(no_print)
		self._collapse_ex_tree(no_print)
		new_root_node = self._change_ex_tree_root_node(no_print)
		self._eliminate_ex_tree_prefix(new_root_node, no_print)
		self._flatten_ex_tree(no_print)
		self._prune_ex_tree(no_print)
		self._detect_ex_tree_cross_usage(no_print)	# As a function of a combination of other methods/attributes or functions
		self._condense_ex_tree_exceptions(no_print)
		self._print_ex_table(no_print, 'After condense')
		self._sort_ex_table_members(no_print)
		self._print_ex_table(no_print, 'After sort')
		self._generate_cross_usage_table(no_print)
		self._deduplicate_ex_table(no_print)
		self._print_ex_table(no_print)
		self._generate_cross_usage_table(no_print)
		self._detect_top_level_equality(no_print)
		self._create_ex_table_output(no_print)

	def _print_ex_table(self, no_print=True, msg=''):
		""" Prints exception table (for debugging purposes) """
		if not no_print:
			print 'self._extable{0}:'.format(' ({0})'.format(msg) if msg else msg)
			for key in sorted(self._extable.keys()):
				print 'Member {0}: {1}\n'.format(key, self._extable[key])

	def ex_add(self, name, extype, exmsg):	#pylint: disable=R0913,R0914
		""" Add exception to database """
		func_name = self.get_func_name()
		self._ex_list.append({'name':self.get_ex_name(name), 'function':func_name, 'type':extype, 'msg':exmsg, 'checked':False})
		self._ex_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in self._ex_list)] # Remove duplicates

	def get_exception_by_name(self, name):
		""" Find exception object """
		exname = self.get_ex_name(name)
		for obj in self._ex_list:
			if obj['name'] == exname:
				return obj
		raise ValueError('Exception name {0} not found'.format(name))

	def get_ex_name(self, name):
		""" Returns hierarchical function name """
		func_name = self.get_func_name()
		return '{0}{1}{2}'.format(func_name, '.' if func_name is not None else '', name)

	def get_func_name(self):	#pylint: disable=R0201
		""" Get calling function name """
		# Stack frame is a tuple with the following items:
		# 0: the frame object
		# 1: the filename
		# 2: the line number of the current line
		# 3: the function name
		# 4: a list of lines of context from the source code
		# 5: the index of the current line within that list.
		frame_list = inspect.stack()
		func_name = ''
		flag = False
		for frame_obj, file_name, _, fname, fcontext, findex in frame_list:
			lcontext = frame_obj.f_locals
			gcontext = frame_obj.f_globals
			scontext = lcontext['self'] if 'self' in lcontext else None
			func_obj = lcontext[fname] if fname in lcontext else (gcontext[fname] if fname in gcontext else (getattr(scontext, fname) if ((scontext is not None) and (getattr(scontext, fname, -1) != -1)) else None))
			if (('wrapper' in fname) and ('check.py' in file_name)) or ('exh.py' in file_name) or ('check.py' in file_name) or ((file_name == '<string>') and (fcontext is None) and (findex is None) and flag):
				pass
			elif fname != '<module>':
				func_name = get_func_calling_hierarchy(frame_obj, func_obj)+('' if not func_name else '.')+func_name
				flag = True
		return func_name

	def get_sphinx_doc_for_member(self, member):
		""" Returns Sphinx-compatible exception list """
		if not self._exoutput:
			raise RuntimeError('No exception table data')
		ret = ['']	# Sphinx requires a new line after the previous section, otherwise a warning is generated
		block_on = False
		for line in self._exoutput:
			if block_on:
				block_on = False if line == '<STOP MEMBER> {0}'.format(member) else block_on
				if not block_on:
					break
				ret.append(line)
			block_on = True if (not block_on) and (line == '<START MEMBER> {0}'.format(member)) else block_on
		else:
			raise RuntimeError('Memmber {0} not found in exception table'.format(member))
		ret.append('\n')	# Sphinx requires a new line after the section, otherwise a warning is generated
		return '\n'.join(ret)

	def print_ex_table(self):
		""" Prints exception table """
		if not self._exoutput:
			raise RuntimeError('No exception table data')
		print
		for line in self._exoutput:
			print line

	def print_ex_tree(self):
		""" Prints exception tree """
		print str(self._tobj)

	def raise_exception(self, name, **kargs):
		""" Raise exception by name """
		if (len(kargs) == 1) and ('edata' not in kargs):
			raise RuntimeError('Illegal keyword argument passed to raise_exception')
		if len(kargs) > 1:
			raise RuntimeError('Illegal keyword argument{0} passed to raise_exception'.format('s' if len(kargs)-(1 if 'edata' in kargs else 0) > 1 else ''))
		obj = self.get_exception_by_name(name)
		if len(kargs):
			raise obj['type'](self._format_msg(obj['msg'], kargs['edata']))
		else:
			raise obj['type'](obj['msg'])

	def raise_exception_if(self, name, condition, **kargs):
		""" Raise exception by name if condition is true """
		if (len(kargs) == 1) and ('edata' not in kargs):
			raise RuntimeError('Illegal keyword argument passed to raise_exception')
		if len(kargs) > 1:
			raise RuntimeError('Illegal keyword argument{0} passed to raise_exception'.format('s' if len(kargs)-(1 if 'edata' in kargs else 0) > 1 else ''))
		if condition:
			self.raise_exception(name, **kargs)
		self.get_exception_by_name(name)['checked'] = True

def get_func_calling_hierarchy(frame_obj, func_obj):
	""" Get class name of decorated function """
	# Most of this code from pycallgraph/tracer.py of the Python Call Graph project (https://github.com/gak/pycallgraph/#python-call-graph)
	ret = list()
	code = frame_obj.f_code
	# Work out the module name
	module = inspect.getmodule(code)
	module_name = ''
	if module:
		module_name = module.__name__
	else:
		if 'self' in frame_obj.f_locals:
			module_name = frame_obj.f_locals['self'].__module__
		else:
			module_name = sys.modules[func_obj.__module__].__name__
	ret.append(module_name)
	# Work out the class name
	try:
		class_name = frame_obj.f_locals['self'].__class__.__name__
		ret.append(class_name)
	except (KeyError, AttributeError):
		class_name = ''
	# Work out the current function or method
	func_name = code.co_name.strip()
	if func_name == '?':
		func_name = '__main__'
	if func_name == '':
		func_name = func_obj.__name__
	ret.append(func_name)
	return '' if (module_name.strip() == '') and (class_name.strip() == '') else '.'.join(ret)

def obj_type(obj, prop):
	""" Determines if prop is part of class obj, and if so if it is a member or an attribute """
	if not hasattr(obj, prop):
		return None
	return 'meth' if type(getattr(obj, prop)) == types.MethodType else 'attr'

def is_module(obj):
	""" Determines whether an object is a module or not """
	return hasattr(obj, '__name__') and (obj.__name__ in sys.modules)

def public_callables(obj):
	""" Generator of 'callable' (functions, methods or properties) objects in argument """
	for element_name in dir(obj):
		if (not (element_name.startswith('__') and element_name.endswith('__'))) and (not (element_name.startswith('_') and element_name.endswith('_'))):
			element_obj = getattr(obj, element_name)
			if (hasattr(element_obj, '__call__') or isinstance(element_obj, property)) and (not inspect.isclass(element_obj)) and (not is_module(element_obj)):
				yield element_name, element_obj, (element_obj if not isinstance(element_obj, property) else obj)

def _make_module_callables_list(obj, cls_name=''):
	""" Creates a list of callable functions at and below an object hierarchy """
	top_level_module = (obj.__name__ if obj.__name__ in sys.modules else obj.__module__).split('.')[0]
	# Callables in object
	callable_dict = dict()
	for call_name, call_obj, base_obj in public_callables(obj):
		call_full_name = '{0}.{1}'.format(base_obj.__module__, call_name) if not cls_name else '{0}.{1}.{2}'.format(base_obj.__module__, cls_name, call_name)
		call_type = 'meth' if type(call_obj) == types.MethodType else 'attr'
		callable_dict[call_full_name] = call_type
	# Sub-classes in object within package
	for element_name in dir(obj):
		element_obj = getattr(obj, element_name)
		if inspect.isclass(element_obj) and (element_obj.__module__.split('.')[0] == top_level_module):
			callable_dict = dict(callable_dict.items()+_make_module_callables_list(element_obj, element_obj.__name__).items())
	return callable_dict

def package_submodules(module_obj):
	""" Generator of package sub-modules """
	top_module_name = module_obj.__name__.split('.')[0]
	for element_name in dir(module_obj):
		element_obj = getattr(module_obj, element_name)
		if (element_name[0] != '_') and hasattr(element_obj, '__name__') and (element_obj.__name__.split('.')[0] == top_module_name) and (element_obj.__name__ != top_module_name):
			yield element_obj

def _make_modules_obj_list(obj):
	""" Creates a list of package modules """
	sub_module_obj_list = [sub_module_obj for sub_module_obj in package_submodules(obj)]
	for sub_module_obj in sub_module_obj_list:
		sub_module_obj_list += _make_modules_obj_list(sub_module_obj)
	return list(set(sub_module_obj_list))

def get_package_obj_type(obj):
	""" Scans package and determines method/attribute/function property for function or class member """
	try:
		obj_module_name = (obj.__name__ if obj.__name__ in sys.modules else obj.__module__)
	except:
		raise RuntimeError('Argument `obj` is of the wrong type')
	# Find top-level module
	top_module_name = obj_module_name.split('.')[0]
	top_module_obj = sys.modules[top_module_name]
	# Get packages modules
	sub_modules_obj_list = [top_module_obj]+_make_modules_obj_list(top_module_obj)
	callables_dict = dict()
	for sub_module_obj in sub_modules_obj_list:
		callables_dict = dict(callables_dict.items()+_make_module_callables_list(sub_module_obj).items())
	return callables_dict
