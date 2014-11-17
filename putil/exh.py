# exh.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Exception handling classes, methods, functions and constants
"""

import sys
import copy
import types
import inspect
import operator

import putil.check
import putil.misc
import putil.tree

###
# Functions
###
def _get_callable_path(frame_obj, func_obj):
	""" Get full path of callable """
	comp = dict()
	# Most of this code refactored from pycallgraph/tracer.py of the Python Call Graph project (https://github.com/gak/pycallgraph/#python-call-graph)
	code = frame_obj.f_code
	scontext = frame_obj.f_locals.get('self', None)
	# Module name
	module = inspect.getmodule(code)
	comp['module'] = module.__name__ if module else (scontext.__module__ if scontext else sys.modules[func_obj.__module__].__name__)
	ret = [comp['module']]
	# Class name
	comp['class'] = scontext.__class__.__name__ if scontext else ''
	ret.append(comp['class'])
	# Function/method/attribute name
	func_name = code.co_name
	comp['function'] = '__main__' if func_name == '?' else (func_obj.__name__ if func_name == '' else func_name)
	ret.append(comp['function'])
	return '' if ret[:2] == ['', ''] else '.'.join(filter(None, ret)), comp	#pylint: disable=W0141


def _is_module(obj):
	""" Determines whether an object is a module or not """
	return hasattr(obj, '__name__') and (obj.__name__ in sys.modules)


def _make_modules_obj_list(obj):
	""" Creates a list of package modules """
	sub_module_obj_list = [sub_module_obj for sub_module_obj in _package_submodules(obj)]
	for sub_module_obj in sub_module_obj_list:
		sub_module_obj_list += _make_modules_obj_list(sub_module_obj)
	return list(set(sub_module_obj_list))


def _obj_type(obj, prop):
	""" Determines if prop is part of class obj, and if so if it is a member or an attribute """
	if not hasattr(obj, prop):
		return None
	return 'meth' if type(getattr(obj, prop)) == types.MethodType else 'attr'


def _package_submodules(module_obj):
	""" Generator of package sub-modules """
	top_module_name = module_obj.__name__.split('.')[0]
	for element_name in dir(module_obj):
		element_obj = getattr(module_obj, element_name)
		if (element_name[0] != '_') and hasattr(element_obj, '__name__') and (element_obj.__name__.split('.')[0] == top_module_name) and (element_obj.__name__ != top_module_name):
			yield element_obj


def _public_callables(obj):
	""" Generator of 'callable' (functions, methods or properties) objects in argument """
	for element_name in dir(obj):
		# Get only __init__ method of classes that have name
		# if (element_name == '__init__') or ((not (element_name.startswith('__') and element_name.endswith('__'))) and (not (element_name.startswith('_') and element_name.endswith('_')))):
		if (element_name == '__init__') or ((not (element_name.startswith('__') and element_name.endswith('__'))) and (not (element_name.startswith('_') and element_name.endswith('_')))):
			element_obj = getattr(obj, element_name)
			if (hasattr(element_obj, '__call__') or isinstance(element_obj, property)) and (not inspect.isclass(element_obj)) and (not _is_module(element_obj)):
				yield element_name, element_obj, (element_obj if not isinstance(element_obj, property) else obj)


###
# Classes
###
class ExHandle(object):	#pylint: disable=R0902
	"""
	Manages exceptions and optionally automatically generates exception documentation in with `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ mark-up

	:param	obj: Object to document exceptions for
	:type	obj: Class object or module-level object
	:rtype: :py:class:`putil.exh.ExHandle()` object

	:raises:
	 * TypeError (Argument `obj` is of the wrong type)

	 * ValueError (Hidden objects cannot be traced)
	"""
	def __init__(self, obj):
		if (not inspect.isclass(obj)) and (not hasattr(obj, '__call__')):
			raise TypeError('Argument `obj` is of the wrong type')
		if obj.__name__.startswith('_'):
			raise ValueError('Hidden objects cannot be traced')
		self._trace_obj = obj
		self._trace_obj_type = inspect.isclass(obj)
		self._trace_obj_name = '{0}.{1}'.format(obj.__module__, obj.__name__)
		self._callable_db = dict()
		self._module_db = list()
		self._trace_list, self._tobj, self._extable, self._module_functions_extable, self._cross_usage_extable, self._exoutput, self._clsattr = None, None, None, None, None, None, None
		self._ex_list = list()

	def __copy__(self):
		cobj = ExHandle(obj=copy.copy(self._trace_obj))
		cobj._trace_obj_type = copy.copy(self._trace_obj_type)	#pylint: disable=W0212
		cobj._trace_obj_name = copy.copy(self._trace_obj_name)	#pylint: disable=W0212
		cobj._callable_db = copy.copy(self._callable_db)	#pylint: disable=W0212
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
		cobj._trace_obj_type = copy.deepcopy(self._trace_obj_type)	#pylint: disable=W0212
		cobj._trace_obj_name = copy.deepcopy(self._trace_obj_name, memodict)	#pylint: disable=W0212
		cobj._callable_db = copy.deepcopy(self._callable_db)	#pylint: disable=W0212
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

	def _alias_attributes(self, no_print=True):	#pylint: disable=R0912,R0914
		""" Create attribute nodes in tree """
		if inspect.isclass(self._trace_obj):
			if not no_print:
				print putil.misc.pcolor('Aliasing attributes', 'blue')
			# Select properties of traced class or module/level function
			#for mkey, mval in self._callable_db.items():
			#	print '{0}: {1}'.format(mkey, mval)
			attr_list = [(mkey, mval['attr']) for mkey, mval in self._callable_db.items() if 'attr' in mval]
			for key, fattr_funcs in attr_list:
				if not no_print:
					print '   Detected attribute {0}'.format(key)
					for func in sorted(fattr_funcs.values()):
						print '      {0}'.format(func)
				for fkey, fname in fattr_funcs.items():
					mod_list = sorted([node for node in self._tobj.nodes if node.endswith(fname) or (node.find(fname+'.') != -1)])
					while mod_list:
						start_char = mod_list[0].find(fname) if mod_list[0].endswith(fname) else mod_list[0].find(fname+'.')
						stop_char = len(mod_list[0]) if mod_list[0].endswith(fname) else start_char+len(fname)
						name_to_replace = mod_list[0][start_char:stop_char] if mod_list[0].endswith(fname) else mod_list[0][start_char:stop_char]+'.'
						self._tobj._rename_node(mod_list[0], mod_list[0].replace(name_to_replace, '{0}[{1}]{2}'.format(key, fkey, '' if mod_list[0].endswith(fname) else '.')))	#pylint: disable=W0212
						self._callable_db['{0}[{1}]'.format(key, fkey)] = copy.deepcopy(self._callable_db[fname])
						mod_list = sorted([node for node in self._tobj.nodes if node.endswith(fname) or (node.find(fname+'.') != -1)])
			if attr_list:
				self._collapse_ex_tree(no_print=True)
		if not no_print:
			print str(self._tobj)

	def _build_ex_tree(self, no_print=True):
		""" Construct exception tree from trace """
		tree_data = self._tree_data()
		if not tree_data:
			raise RuntimeError('No trace information')
		self._tobj = putil.tree.Tree()
		if not no_print:
			print putil.misc.pcolor('Building tree', 'blue')
		self._tobj.add_nodes(tree_data)
		if not no_print:
			print str(self._tobj)

	def _callable_list(self, node):
		""" Returns list of callables from a exception call tree """
		ret = list()
		name = copy.deepcopy(node)
		while name:
			callable_name = self._get_obj_full_name(name)
			ret.append(callable_name)
			name = name[len(callable_name)+(1 if len(callable_name) < len(name) else 0):]
		return ret

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
		self._tobj.collapse_subtree(self._tobj.root_name)
		if not no_print:
			print str(self._tobj)

	def _create_ex_table(self, no_print=True):	#pylint: disable=R0914
		""" Creates exception table entry """
		if not no_print:
			print putil.misc.pcolor('Creating exception table', 'blue')
		self._extable = dict()
		# Create flat exception table for each trace class method/property or module-level function
		children = self._tobj._get_children(self._tobj.root_name)	#pylint: disable=W0212
		module_function = [self._tobj.root_name] if self._tobj._get_data(self._tobj.root_name) else list()	#pylint: disable=W0212
		for child in children+module_function:
			child_name = self._get_obj_full_name(child)
			self._extable[child_name] = dict()
			self._extable[child_name]['native_exceptions'] = sorted(list(set(self._tobj._get_data(child))))	#pylint: disable=W0212
			self._extable[child_name]['flat_exceptions'] = sorted(list(set([exdesc for name in self._tobj._get_subtree(child) for exdesc in self._tobj._get_data(name)])))	#pylint: disable=W0212
			self._extable[child_name]['cross_hierarchical_exceptions'] = list()
			self._extable[child_name]['cross_flat_exceptions'] = list()
			self._extable[child_name]['cross_names'] = list()
		# Create entries for package callables outside the namespace of trace class or module-level function
		pkg_call_list = [(grandchild, grandchild.replace(child+'.', '', 1)) for child in children for grandchild in self._tobj._get_children(child) if not grandchild.replace(child+'.', '', 1).startswith(self._tobj.root_name)]	#pylint: disable=W0212
		for child, child_call_name in pkg_call_list:
			child_name = self._get_obj_full_name(child_call_name)
			self._extable[child_name] = dict()
			self._extable[child_name]['native_exceptions'] = sorted(list(set(self._tobj._get_data(child))))	#pylint: disable=W0212
			self._extable[child_name]['flat_exceptions'] = sorted(list(set([exdesc for name in self._tobj._get_subtree(child) for exdesc in self._tobj._get_data(name)])))	#pylint: disable=W0212
			self._extable[child_name]['cross_hierarchical_exceptions'] = list()
			self._extable[child_name]['cross_flat_exceptions'] = list()
			self._extable[child_name]['cross_names'] = list()

	def _create_ex_table_output(self, no_print=True):	#pylint: disable=R0912
		""" Create final exception table output """
		if not no_print:
			print putil.misc.pcolor('Creating final exception table output', 'blue')
		if not self._extable:
			raise RuntimeError('No exception table data')
		# Remove exception table entries that are package members but not trace class method/properies or module-level function
		for child in sorted(self._extable.keys()):
			if not child.startswith(self._trace_obj_name):
				del self._extable[child]
		# Create output table proper
		self._exoutput = dict()
		min_child_name_hierarchy = len(self._trace_obj_name.split('.'))-(0 if self._trace_obj_type else 1)
		for child in sorted(self._extable.keys()):
			child_name = child.split('.')[min_child_name_hierarchy]
			exoutput = ['']
			exlist = self._extable[child]['native_exceptions']+self._extable[child]['cross_hierarchical_exceptions']
			if child_name.find('[') != -1:
				prop_name = child_name[:child_name.find('[')]
				for child2 in [member for member in sorted(self._extable.keys()) if member != child]:
					child2_name = child2.split('.')[min_child_name_hierarchy]
					if child2_name[:child2_name.find('[')] == prop_name:
						token = child_name[child_name.find('[')+1:child_name.find(']')]
						exoutput.append('When being {0}:'.format('set' if token == 'fset' else ('retrieved' if token == 'fget' else 'deleted')))
					break
				child_name = prop_name
			if len(exlist) == 1:
				exoutput.append(':raises: {0}'.format(exlist[0]))
				exoutput.append('')
			else:
				exoutput.append(':raises:')
				for exname in exlist:
					exoutput.append(' * {0}'.format(exname))
					exoutput.append('')
			if child_name in self._exoutput:
				self._exoutput[child_name] += exoutput
			else:
				self._exoutput[child_name] = exoutput

	def _deduplicate_ex_table(self, no_print=True):	#pylint: disable=R0912
		""" Remove exceptions that could be in 'Same as [...]' entry or 'Same as [...] enties that have the same base exceptions """
		if not no_print:
			print putil.misc.pcolor('De-duplicating native exceptions', 'blue')
		# Remove exceptions that could be in 'Same as [...]' entry
		for key in self._extable:
			self._extable[key]['native_exceptions'] = [exdesc for exdesc in self._extable[key]['native_exceptions'] if exdesc not in self._extable[key]['cross_flat_exceptions']]
		if not no_print:
			print putil.misc.pcolor('Homogenizing cross-exceptions', 'blue')
		# Remove 'Same as [...]' entries that have the same exceptions
		sorted_children = sorted(self._extable.keys())
		for child in sorted_children:
			sorted_cross_names = sorted(self._extable[child]['cross_names'])
			for key1 in [member for member in sorted_children[::-1] if member != child]:
				new_list = list()
				for key2 in sorted_cross_names:
					new_list.append(key1 if (key1 != key2) and (self._extable[key1]['flat_exceptions'] == self._extable[key2]['flat_exceptions']) else key2)
				sorted_cross_names = sorted(list(set(new_list[:])))
			self._extable[child]['cross_names'] = copy.deepcopy(sorted_cross_names)
			self._extable[child]['cross_hierarchical_exceptions'] = sorted(['Same as :py:{0}:`{1}`'.format(self._callable_db[cross_name]['type'], cross_name) for cross_name in sorted_cross_names])
		if not no_print:
			print putil.misc.pcolor('Removing cross-exception loops', 'blue')
		# Expand entries pointed by 'Same as [...]' that only have a 'Same as [...]' as exception
		sorted_children = sorted(self._extable.keys())
		for child in sorted_children:
			sorted_cross_names = sorted(self._extable[child]['cross_names'])
			for key1 in sorted_cross_names:
				if (not self._extable[key1]['native_exceptions']) and (len(self._extable[key1]['cross_names']) == 1):
					self._extable[key1]['native_exceptions'] = self._extable[key1]['flat_exceptions']
					self._extable[key1]['cross_names'] = list()
					self._extable[key1]['cross_flat_exceptions'] = list()
					self._extable[key1]['cross_hierarchical_exceptions'] = list()
		if not no_print:
			print putil.misc.pcolor('Detecting exception table', 'blue')
		# Detect trace class methods/properties or trace module-level functions that are identical
		changed_entries = list()
		for num1, key1 in enumerate(sorted_children):
			for key2 in [child for child in sorted_children[num1+1:] if child not in changed_entries]:
				if self._extable[key1]['flat_exceptions'] == self._extable[key2]['flat_exceptions']:
					self._extable[key2]['native_exceptions'] = list()
					self._extable[key2]['cross_names'] = [key1]
					self._extable[key2]['cross_hierarchical_exceptions'] = ['Same as :py:{0}:`{1}`'.format(self._callable_db[key1]['type'], key1.replace('_set_', ''))]
					self._extable[key2]['cross_flat_exceptions'] = copy.deepcopy(self._extable[key1]['flat_exceptions'])
					changed_entries.append(key2)

	def _detect_ex_tree_cross_usage(self, no_print=True):	#pylint: disable=R0912,R0914
		""" Replace exceptions from other class methods with 'Same as [...]' construct """
		if not no_print:
			print putil.misc.pcolor('Detecting cross-usage across sub-trees', 'blue')
		# Generate trace class method/attribute or module-level class function callable list
		trace_obj_callable_list = [self._get_obj_full_name(child) for child in sorted(self._tobj.get_children(self._tobj.root_name))]
		# Detect cross-usage
		for child in sorted(self._tobj.get_children(self._tobj.root_name)):
			child_name = self._get_obj_full_name(child)
			grandchildren = self._tobj.get_children(child)
			for grandchild in sorted(grandchildren):
				sub_tree = sorted(self._tobj.get_subtree(grandchild), reverse=True)	#pylint: disable=W0212
				for node in sub_tree:
					callable_list = self._callable_list(node)
					node_deleted = False
					for num, callable_name in enumerate(callable_list[1:]):# The first element is the child name/1st level method/attribute/function
						if callable_name in trace_obj_callable_list:
							self._extable[child_name]['cross_names'].append(callable_name)
							self._extable[child_name]['cross_hierarchical_exceptions'].append('Same as :py:{0}:`{1}`'.format(self._callable_db[callable_name]['type'], callable_name))
							# Find out highest hierarchy node that contains cross-callable (because of collapse and flattenging, the ndoe might have several hierarchy levels after cross-callable)
							del_node = None
							for del_node in ['.'.join(callable_list[:num1+2]) for num1 in range(num, len(callable_list)-1)]:
								if self._tobj.in_tree(del_node):
									break
							else:
								raise RuntimeError('Could not find cross-usage node to delete')
							self._tobj._delete_subtree(del_node)	#pylint: disable=W0212
							node_deleted = True
							break
					if node_deleted:
						break
			self._extable[child_name]['cross_names'] = sorted(list(set(self._extable[child_name]['cross_names'])))
			self._extable[child_name]['cross_hierarchical_exceptions'] = sorted(list(set(self._extable[child_name]['cross_hierarchical_exceptions'])))

		if not no_print:
			print str(self._tobj)
		if not no_print:
			print putil.misc.pcolor('Condensing private callables', 'blue')
		# Move all exceptions in private callable sub-tree to child
		for child in sorted(self._tobj._get_children(self._tobj.root_name)):	#pylint: disable=W0212
			child_name = self._get_obj_full_name(child)
			grandchildren = self._tobj._get_children(child)[:]	#pylint: disable=W0212
			for grandchild in grandchildren:
				call_name = self._get_obj_full_name(grandchild.replace(child+'.', '', 1))
				if call_name.split('.')[-1].startswith('_'):
					for subnode in self._tobj._get_subtree(grandchild):	#pylint: disable=W0212
						self._extable[child_name]['native_exceptions'] += self._tobj._get_data(subnode)	#pylint: disable=W0212
					self._extable[child_name]['native_exceptions'] = sorted(list(set(self._extable[child_name]['native_exceptions'])))
					self._tobj._delete_subtree(grandchild)	#pylint: disable=W0212
		if not no_print:
			print str(self._tobj)
		# Generate flat cross-usage exceptions
		for child in sorted(self._tobj._get_children(self._tobj.root_name)):	#pylint: disable=W0212
			child_name = self._get_obj_full_name(child)
			self._extable[child_name]['cross_flat_exceptions'] = \
				sorted(list(set([exdesc for cross_name in self._extable[child_name]['cross_names'] for exdesc in self._extable[cross_name]['flat_exceptions']])))
		if not no_print:
			print str(self._tobj)

	def _eliminate_ex_tree_prefix(self, node, no_print=True):
		""" Remove prefix (usually main.__main__ or simmilar) from exception tree """
		# Find start of trace object name in root name and delete what comes before that
		index = node.find(self._trace_obj_name)
		if index != 0:
			prefix = node[:index-1]
			new_root = node[index:]
			if not no_print:
				print putil.misc.pcolor('Removing prefix {0}'.format(prefix), 'blue')
			self._tobj.rename_node(self._tobj.root_name, new_root)
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
			ret += (self._extable[member]['hier_exceptions'] if member.find('.') == -1 else module_function_ex[member])
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

	def _get_callable_name(self):	#pylint: disable=R0201,R0914
		""" Get fully qualified calling function name """
		ret = list()
		# Filter stack to omit frames that are part of the exception handling module, argument validation, or top level (tracing) module
		# Stack frame -> (frame object [0], filename [1], line number of current line [2], function name [3], list of lines of context from source code [4], index of current line within list [5])
		# Class initializations appear as: filename = '<string>', function name = '__init__', list of lines of context from source code = None, index of current line within list = None
		fstack = [(fo, fn, (fin, fc, fi) == ('<string>', None, None)) for fo, fin, _, fn, fc, fi in inspect.stack() if self._valid_frame(fin, fn)]
		for fobj, func in [(fo, fn) for num, (fo, fn, flag) in reversed(list(enumerate(fstack))) if not (flag and num)]:
			func_obj = fobj.f_locals.get(func, fobj.f_globals.get(func, getattr(fobj.f_locals.get('self'), func, None) if 'self' in fobj.f_locals else None))
			fname, fdict = _get_callable_path(fobj, func_obj)
			ftype = 'attr' if any([hasattr(func_obj, attr) for attr in ['fset', 'fget', 'fdel']]) else 'meth'
			# Methods that return a function have an empty function object. Strategy in this case is to find out which enclosing module-level function or class method returns the function
			# by looking at the line numbers at which each enclosing callable starts, and comparing it with the callable line number
			if fname and (not func_obj):
				try:
					mod_obj = sys.modules[fdict['module']]
					container_obj = getattr(mod_obj, fdict['class'] if fdict['class'] else fdict['module'])
				except:
					raise RuntimeError('Could not get container object')
				lines_dict = dict()
				for element_name in dir(container_obj):
					func_obj = getattr(container_obj, element_name)
					if func_obj and getattr(func_obj, 'func_code', None):
						lines_dict[element_name] = func_obj.func_code.co_firstlineno
				sorted_lines_dict = sorted(lines_dict.items(), key=operator.itemgetter(1))
				func_name = [member for member, line_no in sorted_lines_dict if line_no < fobj.f_lineno][-1]
				fname = '.'.join(filter(None, [fdict['module'], fdict['class'], func_name, fdict['function']]))	#pylint: disable=W0141
			# If callable is an attribute, "trace" module(s) where attributes are to find
			if (fname not in self._callable_db) and (ftype == 'attr'):
				self._make_module_callables_list(sys.modules[func_obj.__module__])
			# Method in class
			elif (fname not in self._callable_db) and hasattr(func_obj, 'im_class'):
				cls_obj = func_obj.im_class
				self._make_module_callables_list(cls_obj, cls_obj.__name__)
			# Module-level function
			elif fname not in self._callable_db:
				self._callable_db[fname] = {'type':ftype, 'code':None if not hasattr(func_obj, 'func_code') else func_obj.func_code}
			ret.append(fname)
		return '.'.join(ret)

	def _get_obj_full_name(self, obj_name):
		""" Find name in package callable dictionary """
		obj_hierarchy = obj_name.split('.')
		obj_hierarchy_list = ['.'.join(obj_hierarchy[:num]) for num in range(len(obj_hierarchy), 0, -1)]
		# Search callable dictionary from object names from the highest number of hierarchy levels to the lowest
		for obj_hierarchy_name in obj_hierarchy_list:
			if obj_hierarchy_name in self._callable_db:
				return obj_hierarchy_name
		raise RuntimeError('Call {0} could not be found in package callable dictionary'.format(obj_name))

	def _get_obj_type(self, obj_name):
		""" Return object type (method, attribute, etc.) """
		return self._callable_db[self._get_obj_full_name(obj_name)]

	def _make_module_callables_list(self, obj, cls_name=''):	#pylint: disable=R0914
		""" Creates a list of callable functions at and below an object hierarchy """
		for call_name, call_obj, base_obj in _public_callables(obj):
			call_full_name = '{0}.{1}.{2}'.format((obj if call_name == '__init__' else base_obj).__module__, cls_name, call_name) if cls_name else '{0}.{1}'.format(base_obj.__module__, call_name)
			call_type = 'attr' if any([hasattr(call_obj, attr) for attr in ['fset', 'fget', 'fdel']]) else 'meth'
			self._callable_db[call_full_name] = {'type':call_type, 'code':None if not hasattr(call_obj, 'func_code') else call_obj.func_code}
			# Setter/getter/deleter object have no introspective way of finding out what class (if any) they belong to
			# Need to compare code objects with class or module memebers to find out cross-link
			if call_type == 'attr':
				attr_dict = dict()
				# Object may have property but be None if it does not have a getter, setter or deleter assigned to it
				attr_tuple = [(attrn, getattr(call_obj, attrn)) for attrn in ['fset', 'fget', 'fdel'] if hasattr(call_obj, attrn) and getattr(call_obj, attrn)]
				# Scan module objects if not done before
				for modname in [attr_obj.__module__ for _, attr_obj in attr_tuple if attr_obj.__module__ not in self._module_db]:
					self._module_db.append(modname)
					self._make_module_callables_list(sys.modules[modname])
				for attr, attr_obj in attr_tuple:
					attr_module = attr_obj.__module__
					# Compare code objects, only reliable way of finding out if function object is the same as class/module object
					for mkey, mvalue in [(mcall, mvalue) for mcall, mvalue in self._callable_db.items() if mcall.startswith(attr_module+'.') and self._callable_db[mcall].get('code', None)]:
						if mvalue['code'] == attr_obj.func_code:
							attr_dict[attr] = mkey
							break
				self._callable_db[call_full_name]['attr'] = attr_dict

	def _print_ex_table(self, no_print=True, msg=''):
		""" Prints exception table (for debugging purposes) """
		if not no_print:
			print 'self._extable{0}:'.format(' ({0})'.format(msg) if msg else msg)
			for key in sorted(self._extable.keys()):
				print 'Member {0} ({1}): {2}\n'.format(key, self._extable[key]['obj_name'], self._extable[key]['hier_exceptions'])

	def _print_extable_for_debug(self, no_print=True):
		""" Pretty prints exception table (mainly for debugging purposes) """
		if not no_print:
			for key in sorted(self._extable.keys()):
				print 'Member: {0}'.format(key)
				print 'Native exceptions:'
				self._print_extable_subkey(key, 'native_exceptions')
				print 'Flat exceptions:'
				self._print_extable_subkey(key, 'flat_exceptions')
				print 'Cross hierarchical exceptions:'
				self._print_extable_subkey(key, 'cross_hierarchical_exceptions')
				print 'Cross names:'
				self._print_extable_subkey(key, 'cross_names')
				print

	def _print_extable_subkey(self, key, subkey):
		""" Prints sub-key of exception table """
		indent = 3*' '
		if not self._extable[key][subkey]:
			print '{0}None'.format(indent)
		for member in self._extable[key][subkey]:
			print '{0}{1}'.format(indent, member)

	def _prune_ex_tree(self, no_print=True):
		""" Prune tree (delete trace object methods/attributes that have no exceptions """
		if not no_print:
			print putil.misc.pcolor('Prunning tree', 'blue')
		children = self._tobj._get_children(self._tobj.root_name)	#pylint: disable=W0212
		for child in children:
			if not self._tobj._get_data(child):	#pylint: disable=W0212
				self._tobj._delete_subtree(child)	#pylint: disable=W0212
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
			data = self._extable[key]['hier_exceptions']
			bex = [exname for exname in data if 'Same as' not in exname]
			sex = [exname for exname in data if 'Same as' in exname]
			self._extable[key]['hier_exceptions'] = sorted(list(set(bex)))+sorted(list(set(sex)))

	def _valid_frame(self, fin, fna):	#pylint: disable-msg=R0201
		""" Selects valid stack frame to process """
		return not (fin.endswith('/putil/exh.py') or fin.endswith('/putil/check.py') or (fna in ['<module>', '<lambda>', 'contracts_checker']))

	def build_ex_tree(self, no_print=True):	#pylint: disable=R0912,R0914,R0915
		""" Builds exception tree """
		# Collect exceptions in hierarchical call tree
		self._build_ex_tree(no_print)
		# Eliminate intermediate call nodes that have no exceptions associated with them
		self._collapse_ex_tree(no_print)
		# Make trace object class or module/level function root node of call tree
		new_root_node = self._change_ex_tree_root_node(no_print)
		# Eliminate prefix hierarchy that is an artifact of the tracing infrastructure
		self._eliminate_ex_tree_prefix(new_root_node, no_print)
		# Flatten hierarchy call on to trace class methods/properties or on to trace module-level function
		self._flatten_ex_tree(no_print)
		# Delete trace class methods/properties or trace module-level function that have/has no exceptions associated with them/it
		self._prune_ex_tree(no_print)
		# Add getter/setter/deleter exceptions to trace class properties (if needed)
		self._alias_attributes(no_print)
		# Create exception table
		self._create_ex_table(no_print)
		# Add exceptions of the form 'Same as [...]' to account for the fact that some trace class methods/attributes may use methods/properties/functions from the same package
		self._detect_ex_tree_cross_usage(no_print)
		# Remove exceptions of trace class methods/properties or trace module-level function that are in their 'Same as [...]' exception constructs
		# Replace identical trace class methods/properties or trace module-level functions with 'Same as [...]' exception constructs
		self._deduplicate_ex_table(no_print)
		# Create Sphinx-formatted output
		self._create_ex_table_output(no_print)

	def add_exception(self, name, extype, exmsg):	#pylint: disable=R0913,R0914
		""" Add exception to handler

		:param	name: Exception name. Has to be unique within the namespace, duplicates are eliminated
		:type	name: string
		:param	extype: Exception type. *Must* be derived from `Exception <https://docs.python.org/2/library/exceptions.html#exceptions.Exception>`_ class
		:type	name: Exception type object (i.e. RuntimeError, TypeError, etc.)
		:param	exmsg: Exception message
		:type	exmsg: string

		:raises:
		 * TypeError (Argument `exmsg` is of the wrong type)

		 * TypeError (Argument `extype` is of the wrong type)

		 * TypeError (Argument `name` is of the wrong type)
		"""
		if not isinstance(name, str):
			raise TypeError('Argument `name` is of the wrong type')
		if not str(extype).startswith("<type 'exceptions."):
			raise TypeError('Argument `extype` is of the wrong type')
		if not isinstance(exmsg, str):
			raise TypeError('Argument `exmsg` is of the wrong type')
		func_name = self._get_callable_name()
		self._ex_list.append({'name':self.get_ex_name(name), 'function':func_name, 'type':extype, 'msg':exmsg, 'checked':False})
		self._ex_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in self._ex_list)] # Remove duplicates

	def get_exception_by_name(self, name):
		""" Find exception object """
		exname = self.get_ex_name(name)
		for obj in self._ex_list:
			if obj['name'] == exname:
				return obj
		raise ValueError('Exception name {0} not found'.format(name))

	def get_ex_name(self, name):	#pylint: disable=R0201
		""" Returns hierarchical function name """
		func_name = self._get_callable_name()
		return '{0}{1}{2}'.format(func_name, '.' if func_name is not None else '', name)

	def get_sphinx_doc_for_member(self, member):
		""" Returns Sphinx-compatible exception list """
		if not self._exoutput:
			raise RuntimeError('No exception table data')
		return ('\n'.join(self._exoutput[member]))+'\n' if member in self._exoutput else ''

	def print_ex_table(self):
		""" Prints exception table """
		if not self._exoutput:
			raise RuntimeError('No exception table data')
		print
		for key in sorted(self._exoutput.keys()):
			print '\n<START MEMBER: {0}>\n{1}\n<STOP MEMBER: {0}\n'.format(key, '\n'.join(self._exoutput[key]))

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

