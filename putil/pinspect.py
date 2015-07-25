# pinspect.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0611,F0401,W0212,W0631

import ast
import copy
try:    # pragma: no cover
    from funcsigs import signature
except ImportError: # pragma: no cover
    from inspect import signature
import os
import re
import sys
import types

import putil.misc
if sys.version_info.major == 2: # pragma: no cover
    from putil.compat2 import _unicode_char
else:   # pragma: no cover
    from putil.compat3 import _unicode_char


###
# Functions
###
def _get_module_name_from_fname(fname):
    """ Get module name from module file name """
    iobj = [
        item
        for item in sys.modules.values()
        if item and hasattr(item, '__file__')
    ]
    fname = fname.replace('.pyc', '.py')
    for mobj in iobj:
        if mobj.__file__.replace('.pyc', '.py') == fname:
            module_name = mobj.__name__
            return module_name
    raise RuntimeError('Module could not be found')


def _is_parg(arg):
    """
    Returns True if arg argument is the name of a positional variable
    argument (i.e. *pargs)
    """
    return (len(arg) > 1) and (arg[0] == '*') and (arg[1] != '*')


def _is_kwarg(arg):
    """
    Returns True if arg argument is the name of a keyword variable argument
    (i.e. **kwargs)
    """
    return (len(arg) > 2) and (arg[:2] == '**')


def get_function_args(func, no_self=False, no_varargs=False):
    """
    Returns a tuple of the function argument names in the order they are
    specified in the function signature

    :param  func: Function
    :type   func: function object
    :param  no_self: Flag that indicates whether the function argument *self*,
     if present, is included in the output (False) or not (True)
    :type   no_self: boolean
    :param  no_varargs: Flag that indicates whether keyword arguments are
     included in the output (True) or not (False)
    :rtype: tuple

    For example:

        >>> import putil.pinspect
        >>> class MyClass(object):
        ...     def __init__(self, value, **kwargs):
        ...         pass
        ...
        >>> putil.pinspect.get_function_args(MyClass.__init__)
        ('self', 'value', '**kwargs')
        >>> putil.pinspect.get_function_args(
        ...     MyClass.__init__, no_self=True
        ... )
        ('value', '**kwargs')
        >>> putil.pinspect.get_function_args(
        ...     MyClass.__init__, no_self=True, no_varargs=True
        ... )
        ('value',)
        >>> putil.pinspect.get_function_args(
        ...     MyClass.__init__, no_varargs=True
        ... )
        ('self', 'value')
    """
    par_dict = signature(func).parameters
    args = [
        '{0}{1}'.format(
            '*'
            if par_dict[par].kind == par_dict[par].VAR_POSITIONAL
            else (
                '**'
                if par_dict[par].kind == par_dict[par].VAR_KEYWORD else
                ''
            ),
            par
        )
        for par in par_dict
    ]
    self_filtered_args = args if not args else (
        args[1 if (args[0] == 'self') and no_self else 0:]
    )
    varargs_filtered_args = tuple([
        arg
        for arg in self_filtered_args
        if ((not no_varargs) or
           (no_varargs and (not _is_parg(arg)) and (not _is_kwarg(arg))))
    ])
    return varargs_filtered_args


def get_module_name(module_obj):
    r"""
    Retrieves the module name from a module object

    :param  module_obj: Module object
    :type   module_obj: object
    :rtype: string
    :raises:
     * RuntimeError (Argument \`module_obj\` is not valid)

     * RuntimeError (Module object \`*[module_name]*\` could not be found in
       loaded modules)

    For example:

        >>> import putil.pinspect
        >>> putil.pinspect.get_module_name(sys.modules['putil.pinspect'])
        'putil.pinspect'
    """
    if not is_object_module(module_obj):
        raise RuntimeError('Argument `module_obj` is not valid')
    name = module_obj.__name__
    if name not in sys.modules:
        raise RuntimeError(
            'Module object `{0}` could not be found in loaded modules'.format(
                name
            )
        )
    return name


def is_object_module(obj):
    """
    Tests if the argument is a module object

    :param  obj: Object
    :type   obj: any
    :rtype: boolean
    """
    return isinstance(obj, types.ModuleType)


def is_special_method(name):
    """
    Tests if a callable name is a special Python method (has a :code:`'__'`
    prefix and suffix)

    :param  name: Callable name
    :type   name: string
    :rtype: boolean
    """
    return name.startswith('__')


###
# Classes
###
class Callables(object):
    r"""
    Generates a list of module callables (functions, classes, methods and class
    properties) and gets their attributes (callable type, file name, lines
    span). Information from multiple modules can be stored in the callables
    database of the object by repeatedly calling
    :py:meth:`putil.pinspect.Callables.trace` with different module file names.
    A :py:class:`putil.pinspect.Callables` object retains knowledge of which
    modules have been traced so repeated calls to
    :py:meth:`putil.pinspect.Callables.trace` with the *same* module object
    will *not* result in module re-traces (and the consequent performance hit).

    :param  fnames: File names of the modules to trace
    :type   fnames: list
    :raises:
     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`fnames\` is not valid)
    """
    # pylint: disable=R0903
    def __init__(self, fnames=None):
        self._callables_db = {}
        self._reverse_callables_db = {}
        self._modules_dict = {}
        self._fnames = []
        self._module_names = []
        self._class_names = []
        if fnames:
            self.trace(fnames)

    def __add__(self, other):
        """
        Merges two objects.

        :raises: RuntimeError (Conflicting information between objects)

        For example:

            >>> import putil.eng, putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj2 = putil.pinspect.Callables(
            ...     [sys.modules['putil.eng'].__file__]
            ... )
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
        robj._reverse_callables_db.update(
            copy.deepcopy(other._reverse_callables_db)
        )
        robj._modules_dict = copy.deepcopy(self._modules_dict)
        robj._modules_dict.update(copy.deepcopy(other._modules_dict))
        robj._module_names = list(
            set(self._module_names[:]+other._module_names[:])
        )
        robj._class_names = list(
            set(self._class_names[:]+other._class_names[:])
        )
        robj._fnames = list(set(self._fnames[:]+other._fnames[:]))
        return robj

    def __copy__(self):
        """
        Copies object. For example:

            >>> import copy, putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj2 = copy.copy(obj1)
            >>> obj1 == obj2
            True

        """
        cobj = Callables()
        for prop_name in putil.misc.private_props(self):
            setattr(cobj, prop_name, copy.deepcopy(getattr(self, prop_name)))
        return cobj

    def __eq__(self, other):
        """
        Tests object equality. For example:

            >>> import putil.eng, putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj2 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj3 = putil.pinspect.Callables(
            ...     [sys.modules['putil.eng'].__file__]
            ... )
            >>> obj1 == obj2
            True
            >>> obj1 == obj3
            False
            >>> 5 == obj3
            False

        """
        return isinstance(other, Callables) and all([
            sorted(getattr(self, attr)) == sorted(getattr(other, attr))
            for attr in putil.misc.private_props(self)]
        )

    def __iadd__(self, other):
        """
        Merges an object into an existing object.

        :raises: RuntimeError (Conflicting information between objects)

        For example:

            >>> import putil.eng, putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj2 = putil.pinspect.Callables(
            ...     [sys.modules['putil.eng'].__file__]
            ... )
            >>> obj3 = putil.pinspect.Callables([
            ...     sys.modules['putil.exh'].__file__,
            ...     sys.modules['putil.eng'].__file__,
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
        self._reverse_callables_db.update(
            copy.deepcopy(other._reverse_callables_db)
        )
        self._modules_dict.update(copy.deepcopy(other._modules_dict))
        self._module_names = list(
            set(self._module_names+other._module_names[:])
        )
        self._class_names = list(set(self._class_names+other._class_names[:]))
        self._fnames = list(set(self._fnames+other._fnames[:]))
        return self

    def __nonzero__(self):  # pragma: no cover
        """
        Returns :code:`False` if no modules have been traced, :code:`True`
        otherwise. For example:

            >>> from __future__ import print_function
            >>> import putil.eng, putil.pinspect, sys
            >>> obj = putil.pinspect.Callables()
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: False
            >>> obj.trace([sys.modules['putil.eng'].__file__])
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: True
        """
        return bool(self._module_names)

    def __bool__(self): # pragma: no cover
        """
        Returns :code:`False` if no modules have been traced, :code:`True`
        otherwise. For example:

            >>> from __future__ import print_function
            >>> import putil.eng, putil.pinspect, sys
            >>> obj = putil.pinspect.Callables()
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: False
            >>> obj.trace([sys.modules['putil.eng'].__file__])
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: True
        """
        return bool(self._module_names)

    def __repr__(self):
        """
        Returns a string with the expression needed to re-create the object.
        For example:

            >>> import putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> repr(obj1)  #doctest: +ELLIPSIS
            "putil.pinspect.Callables(['.../exh.py'])"
            >>> exec("obj2="+repr(obj1))
            >>> obj1 == obj2
            True

        """
        return 'putil.pinspect.Callables({0})'.format(sorted(self._fnames))

    def __str__(self):
        """
        Returns a string with a detailed description of the object's contents.
        For example:

            >>> from __future__ import print_function
            >>> import putil.pinspect, os, sys
            >>> import docs.support.pinspect_example_1
            >>> cobj = putil.pinspect.Callables([
            ...     sys.modules['docs.support.pinspect_example_1'].__file__
            ... ])
            >>> print(cobj) #doctest: +ELLIPSIS
            Modules:
               ...pinspect_example_1
            Classes:
               ...pinspect_example_1.my_func.MyClass
            ...pinspect_example_1.my_func: func (9-25)
            ...pinspect_example_1.my_func.MyClass: class (11-25)
            ...pinspect_example_1.my_func.MyClass.__init__: meth (18-20)
            ...pinspect_example_1.my_func.MyClass._get_value: meth (21-23)
            ...pinspect_example_1.my_func.MyClass.value: prop (24-25)
            ...pinspect_example_1.print_name: func (26-27)

        The numbers in parenthesis indicate the line number in which the
        callable starts and ends within the file it is defined in.
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
                dict_value = self._modules_dict[entry]
                for value in sorted(dict_value, key=lambda x: x['code_id'][1]):
                    start_line = value['code_id'][1]
                    stop_line = value['last_lineno']
                    line_text = (' ({0}-{1})'.format(
                        start_line, stop_line) if start_line != stop_line
                        else ' ({0})'.format(start_line
                    ))
                    ret.append(
                        '{0}: {1}{2}'.format(
                            value['name'],
                            value['type'],
                            line_text
                        )
                    )
            return '\n'.join(ret)
        else:
            return ''

    def _check_intersection(self, other):
        """
        Check that intersection of two objects is congruent, i.e. that they
        have identical information in the intersection
        """
        props = ['_callables_db', '_reverse_callables_db', '_modules_dict']
        for prop in props:
            self_dict = getattr(self, prop)
            other_dict = getattr(other, prop)
            keys_self = set(self_dict.keys())
            keys_other = set(other_dict.keys())
            intersection = keys_self & keys_other
            for key in intersection:
                if ((type(self_dict[key]) != type(other_dict[key])) or
                   ((type(self_dict[key]) == type(other_dict[key])) and
                   ((isinstance(self_dict[key], list) and
                   (not all(
                       [
                           item in self_dict[key] for item in other_dict[key]
                       ]
                   ))) or
                   (
                       isinstance(self_dict[key], dict) and
                       (
                           set(self_dict[key].items()) !=
                           set(other_dict[key].items())
                       )
                   ) or
                   (isinstance(self_dict[key], str) and
                   (self_dict[key] != other_dict[key]))))):
                    raise RuntimeError(
                        'Conflicting information between objects'
                    )

    def _get_callables_db(self):
        """ Getter for callables_db property """
        return self._callables_db

    def _get_reverse_callables_db(self):
        """ Getter for reverse_callables_db property """
        return self._reverse_callables_db

    def get_callable_from_line(self, module_file, lineno):
        """ Get the callable that the line number belongs to """
        module_name = _get_module_name_from_fname(module_file)
        if module_name not in self._modules_dict:
            self.trace([module_file])
        ret = None
        for value in sorted(self._modules_dict[module_name],
                            key=lambda x: x['code_id'][1]):
            if value['code_id'][1] <= lineno <= value['last_lineno']:
                ret = value['name']
            elif value['code_id'][1] > lineno:
                break
        return ret if ret else module_name

    def trace(self, fnames):
        r"""
        Generates a list of module callables (functions, classes, methods and
        class properties) and gets their attributes (callable type, file name,
        lines span)

        :param  fnames: File names of the modules to trace
        :type   fnames: list
        :raises:
         * OSError (File *[fname]* could not be found)

         * RuntimeError (Argument \`fnames\` is not valid)
        """
        if fnames and (not isinstance(fnames, list)):
            raise RuntimeError('Argument `fnames` is not valid')
        if fnames and any([not isinstance(item, str) for item in fnames]):
            raise RuntimeError('Argument `fnames` is not valid')
        for fname in fnames:
            if not os.path.exists(fname):
                raise OSError('File {0} could not be found'.format(fname))
        fnames = [item.replace('.pyc', '.py') for item in fnames]
        for fname in fnames:
            if fname not in self._fnames:
                module_name = _get_module_name_from_fname(fname)
                with open(fname, 'r') as fobj:
                    lines = fobj.readlines()
                # Eliminate all Unicode characters till the first ASCII
                # character is found in first line of file, to deal with
                # Unicode-encoded source files
                for num, char in enumerate(lines[0]):   # pragma: no cover
                    if not _unicode_char(char):
                        break
                lines[0] = lines[0][num:]
                tree = ast.parse(''.join(lines))
                aobj = _AstTreeScanner(fname, lines)
                aobj.visit(tree)
                fake_node = putil.misc.Bundle(
                    lineno=len(lines)+1,
                    col_offset=-1
                )
                aobj._close_callable(fake_node, force=True)
                self._class_names += aobj._class_names[:]
                self._module_names.append(module_name)
                for name, item in aobj._callables_db.items():
                    self._callables_db[name] = item
                for name, item in aobj._reverse_callables_db.items():
                    self._reverse_callables_db[name] = copy.deepcopy(item)
                # Split into modules
                self._modules_dict[module_name] = []
                for entry in [
                        item for item in self._callables_db.values()
                        if item['name'].startswith('{0}.'.format(module_name))
                ]:
                    self._modules_dict[module_name].append(entry)
        self._fnames = list(set(
            self._fnames+[item.replace('.pyc', '.py') for item in fnames]
        ))

    callables_db = property(
        _get_callables_db,
        doc='Module(s) callables database'
    )
    """
    Returns the callables database

    :rtype: dictionary

    The callable database is a dictionary that has the following structure:

    * **full callable name** *(string)* -- Dictionary key. Elements in the
      callable path are separated by periods (:code:`'.'`). For example, method
      :code:`my_method()` from class
      :code:`MyClass` from module :code:`my_module` appears as
      :code:`'my_module.MyClass.my_method'`

     * **callable properties** *(dictionary)* -- Dictionary value. The elements
       of this dictionary are:

      * **type** *(string)* -- :code:`'class'` for classes, :code:`'meth'` for
        methods, :code:`'func'` for functions or :code:`'prop'` for properties
        or class attributes

      * **code_id** *(tuple or None)* -- A tuple with the following items:

        * **file name** *(string)* -- the first item contains the file name
          where the callable can be found

        * **line number** *(integer)* -- the second item contains the line
          number in which the callable code starts (including decorators)

      * **last_lineno** *(integer)* -- line number in which the callable code
        ends (including blank lines and comments regardless of their
        indentation level)
    """
    reverse_callables_db = property(
        _get_reverse_callables_db,
        doc='Reverse module(s) callables database'
    )
    """
    Returns the reverse callables database

    :rtype: dictionary

    The reverse callable database is a dictionary that has the following
    structure:

     * **callable id** *(tuple)* -- Dictionary key. Two-element tuple in which
       the first tuple item is the file name where the callable is defined
       and the second tuple item is the line number where the callable
       definition starts

     * **full callable name** *(string)* -- Dictionary value. Elements in the
       callable path are separated by periods (:code:`'.'`). For example,
       method :code:`my_method()` from class :code:`MyClass` from module
       :code:`my_module` appears as :code:`'my_module.MyClass.my_method'`
    """


class _AstTreeScanner(ast.NodeVisitor):
    """ Get all callables from a given module """
    # pylint: disable=R0902
    def __init__(self, fname, lines):
        super(_AstTreeScanner, self).__init__()
        self._lines = lines
        self._wsregexp = re.compile(r'^(\s*).+')
        self._fname = fname.replace('.pyc', '.py')
        self._module = _get_module_name_from_fname(fname)
        self._indent_stack = [{
            'level':0,
            'type':'module',
            'prefix':'',
            'full_name':None,
            'lineno':0
        }]
        self._callables_db = {}
        self._reverse_callables_db = {}
        self._class_names = []
        self._num_decorators = 0
        self._processed_line = 0

    def _close_callable(self, node, force=False):
        """ Record last line number of callable """
        # Print statements for debug
        # print 'Close callable'

        # If node has no line number, ignore it since it cannot be used
        # for closing out a callable
        try:
            lineno = node.lineno
        except AttributeError:
            return
        # If node is from a past line ignore it since the line has been
        # processed already
        if lineno <= self._processed_line:
            return
        self._processed_line = lineno
        if self._num_decorators:
            self._num_decorators -= 1
            # Print statements for debug
            # print '    num_decorators = {} @ {}'.format(
            #     self._num_decorators, lineno
            # )
            return
        # Extract node name for property closing. Once a property is found,
        # it can only be closed out by a node type that has a name
        name = ''
        if not force:
            try:
                name = self._pop_indent_stack(
                    node, node_type='prop', action=None, add=False
                )
            except AttributeError:
                pass
        # Print statements for debug
        # print '    Name {} @ {}'.format(name if name else 'None', lineno)
        # Traverse backwards through call stack and close callables as needed
        indent = self._get_indent(node)
        count = -1
        while count >= -len(self._indent_stack):
            element_full_name = self._indent_stack[count]['full_name']
            edict = self._callables_db.get(element_full_name, None)
            stack_indent = self._indent_stack[count]['level']
            open_callable = element_full_name and (not edict['last_lineno'])
            # Print statements for debug
            # print '    Name {}, indent, {}, stack_indent {}'.format(
            #     element_full_name, indent, stack_indent
            # )
            if (open_callable and (force or (indent < stack_indent) or
               ((indent <= stack_indent) and
               ((edict['type'] != 'prop') or ((edict['type'] == 'prop') and
               (name and (name != element_full_name))))))):
                # Print statements for debug
                # print '    Closing {} @ {}'.format(
                #     element_full_name, lineno-1
                # )
                edict['last_lineno'] = lineno-1
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
        for indent_dict in reversed(self._indent_stack):    # pragma: no branch
            if ((indent_dict['level'] < indent) or
               (indent_dict['type'] == 'module')):
                return indent_dict['type'] == 'class'

    def _pop_indent_stack(self, node, node_type=None, action=None, add=True):
        indent = self._get_indent(node)
        indent_stack = copy.deepcopy(self._indent_stack)
        while (((indent <= indent_stack[-1]['level']) and
              (indent_stack[-1]['type'] != 'module')) or
              (indent_stack[-1]['type'] == 'prop')):
            indent_stack.pop()
        name = (
            node.targets[0].id
            if hasattr(node.targets[0], 'id') else
            node.targets[0].value.id
        ) if node_type == 'prop' else node.name
        element_full_name = '.'.join([self._module]+[
            indent_dict['prefix']
            for indent_dict in indent_stack
            if indent_dict['type'] != 'module'
        ]+[name])+('({0})'.format(action) if action else '')
        if add:
            self._indent_stack = indent_stack
            self._indent_stack.append({
                'level':indent,
                'prefix':name,
                'type':node_type,
                'full_name':element_full_name,
                'lineno':node.lineno
            })
        return element_full_name

    def generic_visit(self, node):
        """ Generic node """
        self._close_callable(node)
        super(_AstTreeScanner, self).generic_visit(node)

    def visit_Assign(self, node):
        """
        Assignment walker (to parse class properties defined via the
        property() function)
        """
        self._close_callable(node)
        # It may also be a class attribute that is not a property, record it
        # anyway, no harm in doing so as it is not attached to a callable
        if self._in_class(node):
            element_full_name = self._pop_indent_stack(node, 'prop')
            code_id = (self._fname, node.lineno)
            self._callables_db[element_full_name] = {
                'name':element_full_name,
                'type':'prop',
                'code_id':code_id,
                'last_lineno':None
            }
            self._reverse_callables_db[code_id] = element_full_name
            # Print statements for debug
            # print 'Visiting property {} @ {}'.format(
            #     element_full_name, code_id[1]
            # )
            # Get property actions
            self.generic_visit(node)

    def visit_ClassDef(self, node):
        """ Class walker """
        self._close_callable(node)
        element_full_name = self._pop_indent_stack(node, 'class')
        code_id = (self._fname, node.lineno)
        self._class_names.append(element_full_name)
        self._callables_db[element_full_name] = {
            'name':element_full_name,
            'type':'class',
            'code_id':code_id,
            'last_lineno':None
        }
        self._reverse_callables_db[code_id] = element_full_name
        # Print statements for debug
        # print 'Visiting class {} @ {}'.format(element_full_name, code_id[1])
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """ Function/method walker """
        self._close_callable(node)
        in_class = self._in_class(node)
        decorator_list = [
            dobj.id if hasattr(dobj, 'id') else dobj.attr
            for dobj in node.decorator_list
            if hasattr(dobj, 'id') or hasattr(dobj, 'attr')
        ]
        self._num_decorators = len(decorator_list)
        self._num_decorators = len(node.decorator_list)
        action = ('getter' if 'property' in decorator_list else
                 ('setter' if 'setter' in decorator_list else
                 ('deleter' if 'deleter' in decorator_list else None)))
        element_type = 'meth' if in_class else 'func'
        element_full_name = self._pop_indent_stack(
            node, element_type, action=action
        )
        code_id = (self._fname, node.lineno)
        self._callables_db[element_full_name] = {
            'name':element_full_name,
            'type':element_type,
            'code_id':code_id,
            'last_lineno':None
        }
        self._reverse_callables_db[code_id] = element_full_name
        # Print statements for debug
        # print 'Visiting callable {}  @ {}'.format(
        #     element_full_name, code_id[1]
        # )
        # print '    num_decorators = {}'.format(self._num_decorators)
        self.generic_visit(node)
