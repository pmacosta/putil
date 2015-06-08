# exdoc.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0611,E1101,E1103,F0401,R0903,W0105,W0122,W0212,W0611,W0613

from __future__ import print_function
import bisect
import copy
import os
import sys
import textwrap
if sys.version_info.major == 2:	# pragma: no cover
	import __builtin__
	from putil.compat2 import _rwtb
else:	# pragma: no cover
	import builtins as __builtin__
	from putil.compat3 import _rwtb


import putil.exh
import putil.misc
import putil.tree

###
# Global variables
###
# Minimum width of the output lines, broken out as a global variable
# mainly to ease testing
_MINWIDTH = 40


###
# Functions
###
def _format_msg(text, width, indent=0, prefix=''):
	""" Replace newline characters \n with ``\n`` and wrap text as needed """
	text = repr(text).replace('`', '\\`').replace('\\n', ' ``\\n`` ')
	wrapped_text = textwrap.wrap(
		text,
		width,
		subsequent_indent=indent*' ' if not prefix else prefix
	)
	return ('\n'.join(wrapped_text))[1:-1].rstrip()


###
# Context managers
###
class ExDocCxt(object):
	r""" Context manager to simplify exception tracing; it sets up the
	tracing environment and returns a :py:class:`putil.exdoc.ExDoc`
	object that can the be used in the documentation string of each
	callable to extract the exceptions documentation with either
	:py:meth:`putil.exdoc.ExDoc.get_sphinx_doc` or
	:py:meth:`putil.exdoc.ExDoc.get_sphinx_autodoc`.

	:param	exclude: Module exclusion list. A particular callable in
	 an otherwise fully qualified name is omitted if it belongs to a
	 module in this list
	:type	exclude: list

	For example:

		>>> from __future__ import print_function
		>>> import putil.eng, putil.exdoc
		>>> with putil.exdoc.ExDocCxt() as exdoc_obj:
		...     value = putil.eng.peng(1e6, 3, False)
		>>> print(exdoc_obj.get_sphinx_doc('putil.eng.peng'))
		.. Auto-generated exceptions documentation for putil.eng.peng
		<BLANKLINE>
		:raises:
		 * RuntimeError (Argument \`frac_length\` is not valid)
		<BLANKLINE>
		 * RuntimeError (Argument \`number\` is not valid)
		<BLANKLINE>
		 * RuntimeError (Argument \`rjust\` is not valid)
		<BLANKLINE>
		<BLANKLINE>

	"""
	def __init__(self, _no_print=True, exclude=None):
		# Need to have an exception handler with full_cname=True and clean
		# the slate for the trace. If there is an existing handler copy it
		# to a temporary variable and copy it back/restore it upon exit
		self._existing_exhobj = None
		if putil.exh.get_exh_obj() is not None:
			self._existing_exhobj = copy.copy(putil.exh.get_exh_obj())
		putil.exh.set_exh_obj(putil.exh.ExHandle(full_cname=True, exclude=exclude))
		self._exdoc_obj = putil.exdoc.ExDoc(
			exh_obj=putil.exh.get_exh_obj(),
			_empty=True,
			_no_print=_no_print
		)
		setattr(__builtin__, '_EXDOC_EXCLUDE', exclude)
		setattr(__builtin__, '_EXDOC_FULL_CNAME', True)

	def __enter__(self):
		return self._exdoc_obj

	def __exit__(self, exc_type, exc_value, exc_tb):
		if exc_type is not None:
			putil.exh.del_exh_obj()
			return False
		if hasattr(__builtin__, '_EXH_LIST') and __builtin__._EXH_LIST:
			exhobj = copy.copy(__builtin__._EXH_LIST[0])
			for obj in __builtin__._EXH_LIST[1:]:
				exhobj += obj
			delattr(__builtin__, '_EXH_LIST')
		else:
			exhobj = putil.exh.get_exh_obj()
		delattr(__builtin__, '_EXDOC_EXCLUDE')
		delattr(__builtin__, '_EXDOC_FULL_CNAME')
		self._exdoc_obj._exh_obj = copy.copy(exhobj)
		putil.exh.del_exh_obj()	# Delete all traced exceptions
		self._exdoc_obj._build_ex_tree()
		self._exdoc_obj._build_module_db()
		putil.exh.del_exh_obj()	# Delete exceptions from exception tree building
		if self._existing_exhobj is not None:
			putil.exh.set_exh_obj(self._existing_exhobj)


###
# Classes
###
class ExDoc(object):
	"""
	Generates exception documentation with `reStructuredText
	<http://docutils.sourceforge.net/rst.html>`_ mark-up

	:param	exh_obj: Exception handler containing exception information
	 for the callable(s) to be documented
	:type	exh_obj: :py:class:`putil.exh.ExHandle` object
	:param	depth: Default hierarchy levels to include in the exceptions
	 per callable (see :py:attr:`putil.exdoc.ExDoc.depth`)
	:type	depth: non-negative integer
	:param	exclude: Default list of (potentially partial) module and
	 callable names to exclude from exceptions per callable (see
	 :py:attr:`putil.exdoc.ExDoc.exclude`)
	:type	exclude: list
	:rtype: :py:class:`putil.exdoc.ExDoc` object
	:raises:
	 * RuntimeError (Argument \\`depth\\` is not valid)

	 * RuntimeError (Argument \\`exclude\\` is not valid)

	 * RuntimeError (Argument \\`exh_obj\\` is not valid)

	 * RuntimeError (Exceptions database is empty)

	 * RuntimeError (Exceptions do not have a common callable)

	 * ValueError (Object of argument \\`exh_obj\\` does not have any
	   exception trace information)
	"""
	# pylint: disable=R0902
	def __init__(self, exh_obj, depth=None, exclude=None,
			     _empty=False, _no_print=False):
		if (not _empty) and (not isinstance(exh_obj, putil.exh.ExHandle)):
			raise RuntimeError('Argument `exh_obj` is not valid')
		if (not _empty) and (not exh_obj.exceptions_db):
			raise ValueError(
				'Object of argument `exh_obj` does not have any '
				'exception trace information'
			)
		if not isinstance(_no_print, bool):
			raise RuntimeError('Argument `_no_print` is not valid')
		self._module_obj_db = {}
		self._depth = None
		self._exclude = None
		self._tobj = None
		self._exh_obj = exh_obj
		self._no_print = _no_print
		self._set_depth(depth)
		self._set_exclude(exclude)
		if not _empty:
			self._build_ex_tree()
			self._build_module_db()

	def __copy__(self):
		cobj = ExDoc(
			exh_obj=None,
			depth=self.depth,
			exclude=self.exclude[:] if self.exclude else self.exclude,
			_empty=True,
			_no_print=self._no_print
		)
		cobj._exh_obj = copy.copy(self._exh_obj)
		cobj._tobj = copy.copy(self._tobj)
		cobj._module_obj_db = copy.deepcopy(self._module_obj_db)
		return cobj

	def _build_ex_tree(self):
		""" Construct exception tree from trace """
		# Load exception data into tree structure
		sep = self._exh_obj.callables_separator
		data = self._exh_obj.exceptions_db
		if not data:
			raise RuntimeError('Exceptions database is empty')
		# Add root node to exceptions, useful if tracing done through test
		# runner which is excluded from callable path
		for item in data:
			item['name'] = 'root{0}{1}'.format(sep, item['name'])
		self._tobj = putil.tree.Tree(sep)
		try:
			self._tobj.add_nodes(data)
		except ValueError as eobj:
			if str(eobj).startswith('Illegal node name'):
				raise RuntimeError('Exceptions do not have a common callable')
			raise
		# Find closest root node to first branching
		node = self._tobj.root_name
		while len(self._tobj.get_children(node)) == 1:
			node = self._tobj.get_children(node)[0]
		if not self._tobj.is_root(node):	# pragma: no branch
			self._tobj.make_root(node)
			nsep = self._tobj.node_separator
			prefix = nsep.join(node.split(self._tobj.node_separator)[:-1])
			self._tobj.delete_prefix(prefix)
		self._print_ex_tree()

	def _build_module_db(self):
		""" Build database of module callables sorted by line number """
		tdict = {}
		for callable_name, callable_dict in self._exh_obj.callables_db.items():
			fname, line_no = callable_dict['code_id']
			if fname not in tdict:
				tdict[fname] = list()
			if callable_dict['type'] == 'class':
				cname = '{0}.__init__'.format(callable_name)
			else:
				cname = callable_name
			tdict[fname].append({'name':cname, 'line':line_no})
		for fname in tdict.keys():
			self._module_obj_db[fname] = sorted(
				tdict[fname],
				key=lambda idict: idict['line']
			)

	def _get_depth(self):
		""" depth getter """
		return self._depth

	def _get_exclude(self):
		""" exclude getter """
		return self._exclude

	def _print_ex_tree(self):
		""" Prints exception tree """
		if not self._no_print:
			print(str(self._tobj).encode('utf-8'))

	def _set_depth(self, depth):
		""" Depth setter """
		if depth and ((not isinstance(depth, int)) or
		   (isinstance(depth, int) and (depth < 0))):
			raise RuntimeError('Argument `depth` is not valid')
		self._depth = depth

	def _set_exclude(self, exclude):
		""" exclude setter """
		if exclude and ((not isinstance(exclude, list)) or
		   (isinstance(exclude, list) and
		   any([not isinstance(item, str) for item in exclude]))):
			raise RuntimeError('Argument `exclude` is not valid')
		self._exclude = exclude

	def get_sphinx_autodoc(self, depth=None, exclude=None,
						   width=72, error=False):
		"""
		Returns an exception list marked up in `reStructuredText`_
		automatically determining callable name

		:param	depth: Hierarchy levels to include in the exceptions list
		 (overrides default **depth** argument; see
		 :py:attr:`putil.exdoc.ExDoc.depth`)
		:type	depth: non-negative integer
		:param	exclude: List of (potentially partial) module and callable
		 names to exclude from exceptions list  (overrides default
		 **exclude** argument, see :py:attr:`putil.exdoc.ExDoc.exclude`)
		:type	exclude: list
		:param	width: Maximum width of the lines of text (minimum 40)
		:type	width: integer
		:param	error: Flag that indicates whether an exception should be
		 raised if the callable is not found in the callables exceptions
		 database (True) or not (False)
		:type	error: boolean
		:raises:

		 * RuntimeError (Argument \\`depth\\` is not valid)

		 * RuntimeError (Argument \\`error\\` is not valid)

		 * RuntimeError (Argument \\`exclude\\` is not valid)

		 * RuntimeError (Argument \\`width\\` is not valid)

		 * RuntimeError (Callable not found in exception list: *[name]*)

		 * RuntimeError (Unable to determine callable name)
		"""
		# pylint: disable=R0201
		frame = sys._getframe(1)
		index = frame.f_code.co_filename.rfind('+')
		fname = os.path.abspath(frame.f_code.co_filename[:index])
		line_num = int(frame.f_code.co_filename[index+1:])
		module_db = self._module_obj_db[fname]
		names = [callable_dict['name'] for callable_dict in module_db]
		line_nums = [callable_dict['line'] for callable_dict in module_db]
		name = names[bisect.bisect(line_nums, line_num)-1]
		return self.get_sphinx_doc(
			name,
			depth=depth,
			exclude=exclude,
			width=width,
			error=error
		)

	def get_sphinx_doc(self, name, depth=None, exclude=None,
					   width=72, error=False):
		"""
		Returns an exception list marked up in `reStructuredText`_

		:param	name: Name of the callable (method, function or class
		 property) to generate exceptions documentation for
		:type	name: string
		:param	depth: Hierarchy levels to include in the exceptions
		 list (overrides default **depth** argument; see
		 :py:attr:`putil.exdoc.ExDoc.depth`)
		:type	depth: non-negative integer
		:param	exclude: List of (potentially partial) module and
		 callable names to exclude from exceptions list  (overrides
		 default **exclude** argument; see
		 :py:attr:`putil.exdoc.ExDoc.exclude`)
		:type	exclude: list
		:param	width: Maximum width of the lines of text (minimum 40)
		:type	width: integer
		:param	error: Flag that indicates whether an exception should
		 be raised if the callable is not found in the callables
		 exceptions database (True) or not (False)
		:type	error: boolean
		:raises:
		 * RuntimeError (Argument \\`depth\\` is not valid)

		 * RuntimeError (Argument \\`error\\` is not valid)

		 * RuntimeError (Argument \\`exclude\\` is not valid)

		 * RuntimeError (Argument \\`width\\` is not valid)

		 * RuntimeError (Callable not found in exception list: *[name]*)
		"""
		# pylint: disable=R0912,R0913,R0914,R0915
		if depth and ((not isinstance(depth, int)) or
		   (isinstance(depth, int) and (depth < 0))):
			raise RuntimeError('Argument `depth` is not valid')
		if exclude and ((not isinstance(exclude, list)) or
		   (isinstance(exclude, list) and
		   any([not isinstance(item, str) for item in exclude]))):
			raise RuntimeError('Argument `exclude` is not valid')
		if (not isinstance(width, int)) or (isinstance(width, int) and
		   (width < _MINWIDTH)):
			raise RuntimeError('Argument `width` is not valid')
		if not isinstance(error, bool):
			raise RuntimeError('Argument `error` is not valid')
		depth = self._depth if depth is None else depth
		exclude = self._exclude if not exclude else exclude
		callable_dict = {}
		prop = False
		# Try to find "regular" callable
		# The trace may have several calls to the same callable, capturing
		# potentially different exception or behaviors, thus capture them all
		instances = self._tobj.search_tree(name)
		if instances:
			callable_dict[name] = {'type':'regular', 'instances':instances}
		else:
			# Try to find property callable
			for action in ['getter', 'setter', 'deleter']:
				prop_name = '{0}({1})'.format(name, action)
				instances = self._tobj.search_tree(prop_name)
				if instances:
					callable_dict[prop_name] = {'type':action, 'instances':instances}
					prop = True
		if error and (not callable_dict):
			raise RuntimeError('Callable not found in exception list: {0}'.format(name))
		elif not callable_dict:
			return ''
		# Create exception table taking into account depth and exclude arguments
		sep = self._tobj.node_separator
		for name_dict in callable_dict.values():
			exlist = []
			for callable_root in name_dict['instances']:
				rlevel = callable_root[:callable_root.index(name)].count(sep)
				nodes = self._tobj.get_subtree(callable_root)
				tnodes = [(node, sep.join(node.split(sep)[rlevel:])) for node in nodes]
				for fnode, rnode in tnodes:
					data = self._tobj._get_data(fnode)
					if ((depth is None) or ((depth is not None) and
					   (rnode.count(sep) <= depth))) and ((not exclude) or
					   (not any([item in rnode for item in exclude]))) and data:
						for exc in data:
							exlist.append(exc)
			name_dict['exlist'] = list(set(exlist[:]))
		# Generate final output
		template = '.. Auto-generated exceptions documentation for {0}'
		exoutput = [_format_msg(template.format(name), width, prefix='.. ')]
		desc_dict = {
			'getter':'retrieved',
			'setter':'assigned',
			'deleter':'deleted'
		}
		if prop:
			if len(callable_dict) == 1:
				callable_root = list(callable_dict.keys())[0]
				action = callable_dict[callable_root]['type']
				desc = desc_dict[action]
				exlist = sorted(
					list(set(callable_dict[callable_root]['exlist']))
				)
				if len(exlist) == 1:
					template = ':raises: (when {0}) {1}'
					exoutput.extend(
						['\n{0}'.format(_format_msg(
								template.format(desc, exlist[0]),
								width,
								indent=1
						))]
					)
				else:
					exoutput.extend(
						['\n:raises: (when {0})\n'.format(desc)]+
						[' * {0}\n'.format(_format_msg(
							name,
							width,
							3)) for name in exlist]
					)
			else:
				exoutput.append('\n:raises:')
				for action in ['setter', 'deleter', 'getter']:
					desc = desc_dict[action]
					for callable_root in callable_dict:
						if callable_dict[callable_root]['type'] == action:
							exlist = sorted(list(set(callable_dict[callable_root]['exlist'])))
							exoutput.extend(
								[' * When {0}\n'.format(desc)]+
								['   * {0}\n'.format(_format_msg(
									name,
									width,
									5)) for name in exlist]
							)
		else:
			exlist = sorted(
				list(set(callable_dict[list(callable_dict.keys())[0]]['exlist']))
			)
			if len(exlist) == 1:
				exoutput.extend(
					['\n{0}'.format(_format_msg(
						':raises: {0}'.format(exlist[0]),
						width,
						indent=1))]
				)
			else:
				exoutput.extend(
					['\n:raises:']+
					[' * {0}\n'.format(_format_msg(name, width, 3)) for name in exlist]
				)
		exoutput[-1] = exoutput[-1].rstrip() + '\n\n'
		return ('\n'.join(exoutput)) if exoutput else ''

	depth = property(_get_depth, _set_depth, doc='Call hierarchy depth')
	"""
	Gets or sets the default hierarchy levels to include in the exceptions per
	callable. For example, a function :code:`my_func()` calls two other
	functions, :code:`get_data()` and :code:`process_data()`, and in turn
	:code:`get_data()` calls another function, :code:`open_socket()`. In this
	scenario, the calls hierarchy is::

			my_func            <- depth = 0
			├get_data          <- depth = 1
			│└open_socket      <- depth = 2
			└process_data      <- depth = 1

	Setting :code:`depth=0` means that only exceptions raised by
	:code:`my_func()` are going to be included in the documentation; Setting
	:code:`depth=1` means that only exceptions raised by :code:`my_func()`,
	:code:`get_data()` and :code:`process_data()` are going to be included in
	the documentation; and finally setting :code:`depth=2` (in this case it has
	the same effects as :code:`depth=None`) means that only exceptions raised
	by :code:`my_func()`, :code:`get_data()`, :code:`process_data()` and
	:code:`open_socket()` are going to be included in the documentation.

	:rtype: non-negative integer
	:raises: RuntimeError (Argument \\`depth\\` is not valid)
	"""

	exclude = property(
		_get_exclude,
		_set_exclude,
		doc='Modules and callables to exclude'
	)
	"""
	Gets or sets the default list of (potentially partial) module and callable
	names to exclude from exceptions per callable. For example,
	:code:`['putil.ex']` excludes all exceptions from modules :code:`putil.exh`
	and :code:`putil.exdoc` (it acts as :code:`r'putil.ex*'`).  In addition to
	these modules, :code:`['putil.ex', 'putil.eng.peng']` excludes exceptions
	from the function :code:`putil.eng.peng`.

	:rtype: list
	:raises: RuntimeError (Argument \\`exclude\\` is not valid)
	"""
