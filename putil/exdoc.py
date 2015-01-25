# exdoc.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import copy

import putil.exh
import putil.misc
import putil.tree


###
# Classes
###
class ExDoc(object):	#pylint: disable=R0902
	"""
	Generates exception documentation with `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ mark-up

	:param	exh_obj: Exception handler containing exception information for the callable(s) to be documented
	:type	exh_obj: :py:class:`putil.exh.ExHandle` object
	:param	no_print: Print step-by-step processing information (False) or not (True) flag
	:type	no_print: boolean
	:rtype: :py:class:`putil.exdoc.ExDoc()` object

	:raises:
	 * TypeError (Argument `exh_obj` is of the wrong type)

	 * TypeError (Argument `no_print` is of the wrong type)

	 * TypeError (Argument `trace_name` is of the wrong type)

	 * ValueError (Object of argument `exh_obj` does not have any exception trace information)
	"""
	def __init__(self, exh_obj, no_print=False, trace_name=None, _step=None):
		if not isinstance(exh_obj, putil.exh.ExHandle):
			raise TypeError('Argument `exh_obj` is not valid')
		if not exh_obj.exceptions_db:
			raise ValueError('Object of argument `exh_obj` does not have any exception trace information')
		if not isinstance(no_print, bool):
			raise TypeError('Argument `no_print` is not valid')
		if not isinstance(trace_name, str):
			raise TypeError('Argument `trace_name` is not valid')
		self._trace_name = trace_name
		self._exh_obj = exh_obj
		self._callables_db = self._exh_obj.callables_db
		self.no_print = no_print
		self._trace_obj_type, self._trace_obj_name, self._trace_list, self._tobj, self._extable, self._cross_usage_extable, self._exoutput = None, None, None, None, None, None, None
		self._process_exceptions(_step)

	def __copy__(self):
		cobj = ExDoc(exh_obj=copy.copy(self._exh_obj), no_print=self.no_print)
		cobj._trace_obj_type = copy.copy(self._trace_obj_type)	#pylint: disable=W0212
		cobj._trace_obj_name = copy.copy(self._trace_obj_name)	#pylint: disable=W0212
		cobj._callables_db = copy.copy(self._callables_db)	#pylint: disable=W0212
		cobj._trace_list = copy.copy(self._trace_list)	#pylint: disable=W0212
		cobj._tobj = copy.copy(self._tobj)	#pylint: disable=W0212
		cobj._extable = copy.copy(self._extable)	#pylint: disable=W0212
		cobj._cross_usage_extable = copy.copy(self._cross_usage_extable)	#pylint: disable=W0212
		cobj._exoutput = copy.copy(self._exoutput)	#pylint: disable=W0212
		return cobj

	def __deepcopy__(self, memodict=None):
		memodict = dict() if memodict is None else memodict
		cobj = ExDoc(exh_obj=copy.deepcopy(self._exh_obj), no_print=self.no_print)
		cobj._trace_obj_type = copy.deepcopy(self._trace_obj_type)	#pylint: disable=W0212
		cobj._trace_obj_name = copy.deepcopy(self._trace_obj_name, memodict)	#pylint: disable=W0212
		cobj._callables_db = copy.deepcopy(self._callables_db)	#pylint: disable=W0212
		cobj._trace_list = copy.deepcopy(self._trace_list, memodict)	#pylint: disable=W0212
		cobj._tobj = copy.deepcopy(self._tobj, memodict)	#pylint: disable=W0212
		cobj._extable = copy.deepcopy(self._extable, memodict)	#pylint: disable=W0212
		cobj._cross_usage_extable = copy.deepcopy(self._cross_usage_extable, memodict)	#pylint: disable=W0212
		cobj._exoutput = copy.deepcopy(self._exoutput, memodict)	#pylint: disable=W0212
		return cobj

	def _build_ex_tree(self):
		""" Construct exception tree from trace """
		self._cprint('Building tree', 'blue')
		# Load exception data into tree structure
		cdb = self._exh_obj.callables_db
		sep = self._exh_obj.callables_separator
		data = self._exh_obj.exceptions_db
		func_list, unique_data = list(), list()
		for ditem in data:
			# Detect setter/getter/deleter functions of properties and re-name them, faster to do it before tree is built
			#ditem['name'] = sep.join(['{0}[{1}]'.format(cdb[token]['link'][0]['prop'], cdb[token]['link'][0]['action']) if cdb[token]['link'] else token for token in ditem['name'].split(sep)])
			new_name_list = []
			for token in ditem['name'].split(sep):
				if cdb[token]['link'] and (len(cdb[token]['link']) > 1):
					raise RuntimeError('Functions performing actions for multiple properties not supported')
				elif cdb[token]['link']:
					new_name_list.append('{0}[{1}]'.format(cdb[token]['link'][0]['prop'], cdb[token]['link'][0]['action']))
				else:
					new_name_list.append(token)
			ditem['name'] = sep.join(new_name_list)
			# Remove prefix (cannot be done in previous step because technically the setter/getter/deleter of propeties can be in a different module) and only handle unique exceptions
			if ditem['name'].find(self._trace_name) != -1:
				ditem['name'] = ditem['name'][ditem['name'].find(self._trace_name):]
				if ditem['name'] not in func_list:
					func_list.append(ditem['name'])
					# Make trace name root node
					ditem['name'] = '{0}/{1}'.format(ditem['name'][:len(self._trace_name):], ditem['name'][len(self._trace_name)+1:])
					unique_data.append(ditem)
		# Actually build tree
		self._tobj = putil.tree.Tree(self._exh_obj.callables_separator)
		self._tobj.add_nodes(unique_data)
		self._print_ex_tree()

	def _callable_list(self, node):
		""" Returns list of callables from a exception call tree """
		ret = list()
		name = copy.deepcopy(node)
		while name:
			callable_name = self._get_obj_full_name(name)
			ret.append(callable_name)
			name = name[len(callable_name)+(1 if len(callable_name) < len(name) else 0):]
		return ret

	def _collapse_ex_tree(self):
		""" Eliminates nodes without exception data """
		if not self.no_print:
			print putil.misc.pcolor('Collapsing tree', 'blue')
		self._tobj.collapse_subtree(self._tobj.root_name)
		self._print_ex_tree()

	def _cprint(self, text, color=None):
		""" Conditionally print text depending on no_print state """
		if not self.no_print:
			print putil.misc.pcolor(text, 'white' if not color else color)

	def _create_ex_table(self):	#pylint: disable=R0914
		""" Creates exception table entry """
		if not self.no_print:
			print putil.misc.pcolor('Creating exception table', 'blue')
		self._extable = dict()
		# Build exception table by searching all nodes in tree for those who have exception(s) attached to them
		for node in [node for node in self._tobj.nodes if self._tobj._get_data(node)]:	#pylint: disable=W0212
			# The last callable in the node hierarchy is the one that generated the exception
			for token in [token for token in node.split(self._exh_obj.tokens_separator)[-1] if token not in self._extable]:
				self._extable[token] = dict()
				self._extable[token]['native_exceptions'] = sorted(list(set(self._tobj._get_data(token))))	#pylint: disable=W0212
				self._extable[token]['flat_exceptions'] = sorted(list(set([exdesc for name in self._tobj._get_subtree(token) for exdesc in self._tobj._get_data(name)])))	#pylint: disable=W0212
				self._extable[token]['cross_hierarchical_exceptions'] = list()
				self._extable[token]['cross_flat_exceptions'] = list()
				self._extable[token]['cross_names'] = list()

	def _create_ex_table_output(self):	#pylint: disable=R0912
		""" Create final exception table output """
		if not self.no_print:
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
			exlist = self._extable[child]['native_exceptions']+self._extable[child]['cross_hierarchical_exceptions'] if self._trace_obj_type else self._extable[child]['flat_exceptions']
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

	def _deduplicate_ex_table(self):	#pylint: disable=R0912
		""" Remove exceptions that could be in 'Same as [...]' entry or 'Same as [...] enties that have the same base exceptions """
		if not self.no_print:
			print putil.misc.pcolor('De-duplicating native exceptions', 'blue')
		# Remove exceptions that could be in 'Same as [...]' entry
		for key in self._extable:
			self._extable[key]['native_exceptions'] = [exdesc for exdesc in self._extable[key]['native_exceptions'] if exdesc not in self._extable[key]['cross_flat_exceptions']]
		if not self.no_print:
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
			self._extable[child]['cross_hierarchical_exceptions'] = sorted(['Same as :py:{0}:`{1}`'.format(self._callables_db[cross_name]['type'], cross_name) for cross_name in sorted_cross_names])
		if not self.no_print:
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
		if not self.no_print:
			print putil.misc.pcolor('Detecting exception table', 'blue')
		# Detect trace class methods/properties or trace module-level functions that are identical
		changed_entries = list()
		for num1, key1 in enumerate(sorted_children):
			for key2 in [child for child in sorted_children[num1+1:] if child not in changed_entries]:
				if self._extable[key1]['flat_exceptions'] == self._extable[key2]['flat_exceptions']:
					self._extable[key2]['native_exceptions'] = list()
					self._extable[key2]['cross_names'] = [key1]
					self._extable[key2]['cross_hierarchical_exceptions'] = ['Same as :py:{0}:`{1}`'.format(self._callables_db[key1]['type'], key1.replace('_set_', ''))]
					self._extable[key2]['cross_flat_exceptions'] = copy.deepcopy(self._extable[key1]['flat_exceptions'])
					changed_entries.append(key2)

	def _detect_ex_tree_cross_usage(self):	#pylint: disable=R0912,R0914
		""" Replace exceptions from other class methods with 'Same as [...]' construct """
		if not self.no_print:
			print putil.misc.pcolor('Detecting cross-usage across sub-trees', 'blue')
		# Generate trace class method/attribute or module-level class function callable list
		trace_obj_callable_list = [self._get_obj_full_name(child[len(self._tobj.root_name)+1:]) for child in sorted(self._tobj.get_children(self._tobj.root_name))]
		# Detect cross-usage
		for child in sorted(self._tobj.get_children(self._tobj.root_name)):
			child_name = self._get_obj_full_name(child[len(self._tobj.root_name)+1:])
			grandchildren = self._tobj.get_children(child)
			for grandchild in sorted(grandchildren):
				sub_tree = sorted(self._tobj.get_subtree(grandchild), reverse=True)	#pylint: disable=W0212
				for node in sub_tree:
					callable_list = self._callable_list(node)
					node_deleted = False
					for num, callable_name in enumerate(callable_list[1:]):# The first element is the child name/1st level method/attribute/function
						if callable_name in trace_obj_callable_list:
							self._extable[child_name]['cross_names'].append(callable_name)
							self._extable[child_name]['cross_hierarchical_exceptions'].append('Same as :py:{0}:`{1}`'.format(self._callables_db[callable_name]['type'], callable_name))
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

		self._print_ex_tree()
		if not self.no_print:
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
		self._print_ex_tree()
		# Generate flat cross-usage exceptions
		for child in sorted(self._tobj._get_children(self._tobj.root_name)):	#pylint: disable=W0212
			child_name = self._get_obj_full_name(child)
			self._extable[child_name]['cross_flat_exceptions'] = \
				sorted(list(set([exdesc for cross_name in self._extable[child_name]['cross_names'] for exdesc in self._extable[cross_name]['flat_exceptions']])))
		self._print_ex_tree()

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

	def _flatten_ex_tree(self):
		""" Flatten exception tree around class name hierarchy nodes """
		if not self.no_print:
			print putil.misc.pcolor('Flattening hierarchy', 'blue')
		obj_hierarchy = self._tobj.root_name.split('.')
		sub_trees = ['.'.join(obj_hierarchy[:num]) for num in range(len(obj_hierarchy), 0, -1)]	# List of hiearchical nodes from leaf to root of trace object name, i.e. ['a.b.c', 'a.b', 'a']
		for sub_tree in sub_trees:
			if not self.no_print:
				print '\tFlattening on {0}'.format(sub_tree)
			for node in self._tobj.nodes:
				if node.endswith('.{0}'.format(sub_tree)):
					self._tobj.flatten_subtree(node)
		self._print_ex_tree()

	def _get_obj_full_name(self, obj_name):
		""" Find name in package callable dictionary """
		obj_hierarchy = obj_name.split('.')
		obj_hierarchy_list = ['.'.join(obj_hierarchy[:num]) for num in range(len(obj_hierarchy), 0, -1)]
		# Search callable dictionary from object names from the highest number of hierarchy levels to the lowest
		for obj_hierarchy_name in obj_hierarchy_list:
			if obj_hierarchy_name in self._callables_db:
				return obj_hierarchy_name
		raise RuntimeError('Call {0} could not be found in package callable dictionary'.format(obj_name))

	def _get_obj_type(self, obj_name):
		""" Return object type (method, attribute, etc.) """
		return self._callables_db[self._get_obj_full_name(obj_name)]

	def _print_ex_table(self, msg=''):
		""" Prints exception table (for debugging purposes) """
		if not self.no_print:
			print 'self._extable{0}:'.format(' ({0})'.format(msg) if msg else msg)
			for key in sorted(self._extable.keys()):
				print 'Member {0} ({1}): {2}\n'.format(key, self._extable[key]['obj_name'], self._extable[key]['hier_exceptions'])

	def _print_extable_for_debug(self):
		""" Pretty prints exception table (mainly for debugging purposes) """
		if not self.no_print:
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

	def _print_ex_tree(self):
		""" Prints exception tree """
		if not self.no_print:
			print str(self._tobj)

	def _process_exceptions(self, step):	#pylint: disable=R0912,R0914,R0915
		""" Builds exception tree """
		step = step if step != None else 18
		# Collect exceptions in hierarchical call tree
		if step >= 0:
			self._build_ex_tree()
		# Eliminate intermediate call nodes that have no exceptions associated with them
		if step >= 1:
			self._collapse_ex_tree()
		# Flatten hierarchy call on to trace class methods/properties or on to trace module-level function
		#if step >= 2:
		#	self._flatten_ex_tree()
		# # Delete trace class methods/properties or trace module-level function that have/has no exceptions associated with them/it
		# if step >= 3:
		# 	self._prune_ex_tree()
		# # Add getter/setter/deleter exceptions to trace class properties (if needed)
		# if step >= 4:
		# 	self._alias_attributes()
		# Create exception table
		if step >= 5:
			self._create_ex_table()
		# Add exceptions of the form 'Same as [...]' to account for the fact that some trace class methods/attributes may use methods/properties/functions from the same package
		if step >= 6:
			self._detect_ex_tree_cross_usage()
		# Remove exceptions of trace class methods/properties or trace module-level function that are in their 'Same as [...]' exception constructs
		# Replace identical trace class methods/properties or trace module-level functions with 'Same as [...]' exception constructs
		if step >= 7:
			self._deduplicate_ex_table()
		# Create Sphinx-formatted output
		if step >= 8:
			self._create_ex_table_output()

	def _prune_ex_tree(self):
		""" Prune tree (delete trace object methods/attributes that have no exceptions """
		if not self.no_print:
			print putil.misc.pcolor('Prunning tree', 'blue')
		children = self._tobj._get_children(self._tobj.root_name)	#pylint: disable=W0212
		for child in children:
			if not self._tobj._get_data(child):	#pylint: disable=W0212
				self._tobj._delete_subtree(child)	#pylint: disable=W0212
		self._print_ex_tree()

	def _ptable(self, name):	#pylint: disable=C0111
		data = self._tobj.get_data(name)
		ret = 'Node: {0}\n{1}\n\n'.format(name, '\n'.join(sorted(data))) if data else ''
		for child in self._tobj.get_children(name):
			ret += self._ptable(child)
		return ret

	def _sort_ex_table_members(self):
		""" Sort exceptions with 'Same as [...]' at the end, and both 'sections' sorted alphabetically """
		if not self.no_print:
			print putil.misc.pcolor('Sorting exception table members', 'blue')
		for key in self._extable:
			data = self._extable[key]['hier_exceptions']
			bex = [exname for exname in data if 'Same as' not in exname]
			sex = [exname for exname in data if 'Same as' in exname]
			self._extable[key]['hier_exceptions'] = sorted(list(set(bex)))+sorted(list(set(sex)))

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
