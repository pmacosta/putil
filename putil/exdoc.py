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
	:param	depth: Default hierarchy levels to include in the exceptions per callable
	:type	depth: non-negative integer
	:param	exclude: Default list of (potentially partial) module and callable names to exclude from exceptions per callable (see :py:attr:`putil.exdoc.ExDoc.exclude`)
	:type	exclude: list
	:rtype: :py:class:`putil.exdoc.ExDoc()` object
	:raises:
	 * TypeError (Argument `depth` is not valid)

	 * TypeError (Argument `exclude` is not valid)

	 * TypeError (Argument `exh_obj` is not valid)

	 * ValueError (Object of argument `exh_obj` does not have any exception trace information)
	"""
	def __init__(self, exh_obj, depth=None, exclude=None, _no_print=False, _step=None):
		if not isinstance(exh_obj, putil.exh.ExHandle):
			raise TypeError('Argument `exh_obj` is not valid')
		if not exh_obj.exceptions_db:
			raise ValueError('Object of argument `exh_obj` does not have any exception trace information')
		if not isinstance(_no_print, bool):
			raise TypeError('Argument `_no_print` is not valid')
		self._exh_obj = exh_obj
		self._callables_db = self._exh_obj.callables_db
		self._no_print = _no_print
		self._depth, self._exclude, self._trace_obj_type, self._trace_obj_name, self._trace_list, self._tobj, self._extable, self._cross_usage_extable, self._exoutput = 9*[None]
		self._set_depth(depth)
		self._set_exclude(exclude)
		self._build_ex_tree()
		#self._process_exceptions(_step)

	def __copy__(self):
		cobj = ExDoc(exh_obj=copy.copy(self._exh_obj), _no_print=self._no_print)
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
		cobj = ExDoc(exh_obj=copy.deepcopy(self._exh_obj), _no_print=self._no_print)
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
		unique_data = []
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
			unique_data.append(ditem)
		# Actually build tree
		self._tobj = putil.tree.Tree(sep)
		try:
			self._tobj.add_nodes(unique_data)
		except ValueError as eobj:
			if str(eobj).startswith('Illegal node name'):
				raise RuntimeError('Exceptions do not have a common callable')
			raise
		# Find closest root node to first branching
		node = self._tobj.root_name
		while len(self._tobj.get_children(node)) == 1:
			node = self._tobj.get_children(node)[0]
		if not self._tobj.is_root(node):
			self._tobj.make_root(node)
			self._tobj.delete_prefix(self._tobj.node_separator.join(node.split(self._tobj.node_separator)[:-1]))
		print str(self._tobj)
		self._print_ex_tree()

	def _callable_list(self, node):
		""" Returns list of callables from an exception call tree """
		ret = list()
		name = copy.deepcopy(node)
		while name:
			callable_name = self._get_obj_full_name(name)
			ret.append(callable_name)
			name = name[len(callable_name)+(1 if len(callable_name) < len(name) else 0):]
		return ret

	def _cprint(self, text, color=None):
		""" Conditionally print text depending on no_print state """
		if not self._no_print:
			print putil.misc.pcolor(text, 'white' if not color else color)

	def _create_ex_table(self):	#pylint: disable=R0914
		""" Creates exception table entry """
		self._cprint('Creating exception table', 'blue')
		sep = self._tobj.node_separator
		self._extable = dict()
		# Build exception table by searching all nodes in tree for:
		# a) First level nodes below root that have exception(s) attached to them
		# b) Second level nodes below root. These may or may not have exceptions attached to them, but there has be an exception attached to a node in their subtree
		#    otherwise the subtree would not exist. This second level below root is kept and typically shows as in the 'Same as [...] construct
		for node in [node for node in self._tobj.nodes if ((len(node.split(sep)) < 3) and self._tobj._get_data(node)) or (len(node.split(sep)) == 3)]:	#pylint: disable=W0212
			# The last callable in the node hierarchy is the one that generated the exception
			name = node.split(sep)[-1]
			if name not in self._extable:
				self._extable[name] = dict()
				self._extable[name]['native_exceptions'] = sorted(list(set(self._tobj._get_data(node))))	#pylint: disable=W0212
				self._extable[name]['flat_exceptions'] = sorted(list(set([exdesc for subnode in self._tobj._get_subtree(node) for exdesc in self._tobj._get_data(subnode)])))	#pylint: disable=W0212
				self._extable[name]['cross_hierarchical_exceptions'] = list()
				self._extable[name]['cross_flat_exceptions'] = list()
				self._extable[name]['cross_names'] = list()

	def _create_ex_table_output(self):	#pylint: disable=R0912
		""" Create final exception table output """
		if not self._no_print:
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
		if not self._no_print:
			print putil.misc.pcolor('De-duplicating native exceptions', 'blue')
		# Remove exceptions that could be in 'Same as [...]' entry
		for key in self._extable:
			self._extable[key]['native_exceptions'] = [exdesc for exdesc in self._extable[key]['native_exceptions'] if exdesc not in self._extable[key]['cross_flat_exceptions']]
		if not self._no_print:
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
		if not self._no_print:
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
		if not self._no_print:
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
		self._cprint('Detecting cross-usage across sub-trees', 'blue')
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
		if not self._no_print:
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
		if not self._no_print:
			print 'self._extable{0}:'.format(' ({0})'.format(msg) if msg else msg)
			for key in sorted(self._extable.keys()):
				print 'Member {0} ({1}): {2}\n'.format(key, self._extable[key]['obj_name'], self._extable[key]['hier_exceptions'])

	def _print_extable_for_debug(self):
		""" Pretty prints exception table (mainly for debugging purposes) """
		if not self._no_print:
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
		if not self._no_print:
			print str(self._tobj)

	def _process_exceptions(self, step):	#pylint: disable=R0912,R0914,R0915
		""" Builds exception tree """
		step = step if step != None else 18
		# Collect exceptions in hierarchical call tree
		if step >= 0:
			self._build_ex_tree()
		# Create exception table
		if step >= 1:
			self._create_ex_table()
		# Add exceptions of the form 'Same as [...]' to account for the fact that some trace class methods/attributes may use methods/properties/functions from the same package
		if step >= 2:
			self._detect_ex_tree_cross_usage()
		# Remove exceptions of trace class methods/properties or trace module-level function that are in their 'Same as [...]' exception constructs
		# Replace identical trace class methods/properties or trace module-level functions with 'Same as [...]' exception constructs
		if step >= 7:
			self._deduplicate_ex_table()
		# Create Sphinx-formatted output
		if step >= 8:
			self._create_ex_table_output()

	def _ptable(self, name):	#pylint: disable=C0111
		data = self._tobj.get_data(name)
		ret = 'Node: {0}\n{1}\n\n'.format(name, '\n'.join(sorted(data))) if data else ''
		for child in self._tobj.get_children(name):
			ret += self._ptable(child)
		return ret

	def _sort_ex_table_members(self):
		""" Sort exceptions with 'Same as [...]' at the end, and both 'sections' sorted alphabetically """
		if not self._no_print:
			print putil.misc.pcolor('Sorting exception table members', 'blue')
		for key in self._extable:
			data = self._extable[key]['hier_exceptions']
			bex = [exname for exname in data if 'Same as' not in exname]
			sex = [exname for exname in data if 'Same as' in exname]
			self._extable[key]['hier_exceptions'] = sorted(list(set(bex)))+sorted(list(set(sex)))

	def get_sphinx_doc(self, name, depth=None, exclude=None):	#pylint: disable=R0914
		"""
		Returns exception list marked up in `reStructuredText<http://sphinx-doc.org>`_

		:param	name: Name of the callable (method or function) to generate exception documentatio for
		:type	name: string
		:param	depth: Hierarchy levels to include in the exceptions list (overrides default **depth** argument)
		:type	depth: non-negative integer
		:param	exclude: List of (potentially partial) module and callable names to exclude from exceptions list  (overrides default **exclude** argument)
		:type	exclude: list
		:raises:
		 * RuntimeError (Callable not found in exception list: *[name]*)

		 * TypeError (Argument `depth` is not valid)

		 * TypeError (Argument `exclude` is not valid)
		"""
		if depth and ((not isinstance(depth, int)) or (isinstance(depth, int) and (depth < 0))):
			raise TypeError('Argument `depth` is not valid')
		if exclude and ((not isinstance(exclude, list)) or (isinstance(exclude, list) and any([not isinstance(item, str) for item in exclude]))):
			raise TypeError('Argument `exclude` is not valid')
		depth = self._depth if depth == None else depth
		exclude = self._exclude if not exclude else exclude
		try:
			callable_root = self._tobj.search_tree(name)[0]
		except:
			raise RuntimeError('Callable not found in exception list: {0}'.format(name))
		# Create exception table
		sep = self._tobj.node_separator
		exlist, exoutput = [], []
		root_hierarchy_level = callable_root.count(sep)
		for full_node, rebased_node in [(node, sep.join(node.split(sep)[root_hierarchy_level:])) for node in self._tobj.get_subtree(callable_root)]:	#pylint: disable=W0212
			data = self._tobj._get_data(full_node)	#pylint: disable=W0212
			if ((depth == None) or ((depth != None) and (rebased_node.count(sep) <= depth))) and ((not exclude) or (not any([item in rebased_node for item in exclude]))) and data:
				for exc in data:
					exlist.append(exc)
		# Format exceptions
		if exlist:
			exlist = sorted(exlist)
			if len(exlist) == 1:
				exoutput.append(':raises: {0}'.format(exlist[0]))
			else:
				exoutput.append(':raises:')
				for exname in exlist:
					exoutput.append(' * {0}'.format(exname))
			exoutput.append('')
		return ('\n'.join(exoutput))+'\n' if exoutput else ''

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

	def _get_depth(self):
		""" depth getter """
		return self._depth

	def _set_depth(self, depth):
		""" depth setter """
		if depth and ((not isinstance(depth, int)) or (isinstance(depth, int) and (depth < 0))):
			raise TypeError('Argument `depth` is not valid')
		self._depth = depth

	depth = property(_get_depth, _set_depth, None, doc='Call hierarchy depth')
	"""
	Default hierarchy levels to include in the exceptions per callable

	:rtype: non-negative integer
	:raises: TypeError (Argument `depth` is not valid)
	"""	#pylint: disable=W0105

	def _get_exclude(self):
		""" exclude getter """
		return self._exclude

	def _set_exclude(self, exclude):
		""" exclude setter """
		if exclude and ((not isinstance(exclude, list)) or (isinstance(exclude, list) and any([not isinstance(item, str) for item in exclude]))):
			raise TypeError('Argument `exclude` is not valid')
		self._exclude = exclude

	exclude = property(_get_exclude, _set_exclude, None, doc='Modules and callables to exclude')
	"""
	Default list of (potentially partial) module and callable names to exclude from exceptions per callable. For example, :code:`['putil.ex']` excludes all exceptions from modules :code:`putil.exh` and :code:`putil.exdoc`.
	In addition to these modules, :code:`['putil.ex', 'putil.eng.peng']` excludes exceptions from the function :code:`putil.eng.peng`.

	:rtype: list
	:raises: TypeError (Argument `exclude` is not valid)
	"""	#pylint: disable=W0105
