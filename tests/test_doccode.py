# test_doccode.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,R0914,W0212,W0640

from __future__ import print_function
import os
import subprocess
import sys

import putil.misc
import putil.test


def test_exdoc_doccode():
    """ Test code used in exdoc module """
    def remove_header(stdout):
        """ Remove py.test header """
        actual_text = []
        off_header = False
        lines = (
            stdout.split('\n')
            if sys.version_info.major == 2 else
            stdout.decode('ascii').split('\n')
        )
        for line in lines:
            off_header = line.startswith('Callable:') or off_header
            if off_header:
                actual_text.append(line)
        return '\n'.join(actual_text)
    # Test tracing module #1 (py.test based)
    script_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'docs',
        'support'
    )
    script_name = os.path.join(script_dir, 'trace_my_module_1.py')
    proc = subprocess.Popen(['python', script_name], stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]
    actual_text = remove_header(stdout)
    ref_text = (
        'Callable: docs.support.my_module.func\n'
        '.. Auto-generated exceptions documentation for\n'
        '.. docs.support.my_module.func\n'
        '\n'
        ':raises: TypeError (Argument \\`name\\` is not valid)\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
        'Callable: docs.support.my_module.MyClass.value\n'
        '.. Auto-generated exceptions documentation for\n'
        '.. docs.support.my_module.MyClass.value\n'
        '\n'
        ':raises:\n'
        ' * When assigned\n'
        '\n'
        '   * RuntimeError (Argument \\`value\\` is not valid)\n'
        '\n'
        ' * When retrieved\n'
        '\n'
        '   * RuntimeError (Attribute \\`value\\` not set)\n'
        '\n'
        '\n'
        '\n'
        '\n'
    )
    assert actual_text == ref_text
    # Test tracing module #2 (simple usage based)
    script_name = os.path.join(script_dir, 'trace_my_module_2.py')
    proc = subprocess.Popen(['python', script_name], stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]
    actual_text = remove_header(stdout)
    assert actual_text == ref_text
    # Test cogging
    script_name = os.path.join(script_dir, 'build-docs.sh')
    input_file = os.path.join(script_dir, 'my_module.py')
    output_file = os.path.join(script_dir, 'my_module_out.py')
    proc = subprocess.Popen(
        [script_name, input_file, output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    proc.communicate()
    # Read reference
    ref_fname = os.path.join(script_dir, 'my_module_ref.py')
    with open(ref_fname, 'r') as fobj:
        ref_text = fobj.readlines()
    # Read generated output
    with open(output_file, 'r') as fobj:
        actual_text = fobj.readlines()
    with putil.misc.ignored(OSError):
        os.remove(output_file)
    # First line is the file name, which is different
    assert actual_text[1:] == ref_text[1:]


def test_pcsv_doccode():
    """ Test code used in pcsv module """
    script_dir = os.path.join(
        os.path.dirname(__file__), '..', 'docs', 'support'
    )
    for num in range(1, 7):
        script_name = os.path.join(
            script_dir, 'pcsv_example_{}.py'.format(num))

        proc = subprocess.Popen(
            ['python', script_name], stdout=subprocess.PIPE
        )
        proc.communicate()
        assert proc.returncode == 0


def test_pcontracts_doccode():
    """ Test code used in pcontracts module """
    # pylint: disable=W0612
    from docs.support.pcontracts_example_2 import (custom_contract_a,
                                                  custom_contract_b)
    @putil.pcontracts.contract(name='custom_contract_a')
    def funca(name):
        print('My name is {0}'.format(name))
    @putil.pcontracts.contract(name='custom_contract_b')
    def funcb(name):
        print('My name is {0}'.format(name))
    putil.test.assert_exception(
        funca,
        {'name':''},
        RuntimeError,
        'Only one exception'
    )
    funca('John')
    putil.test.assert_exception(
        funcb,
        {'name':''},
        RuntimeError,
        'Empty'
    )
    putil.test.assert_exception(
        funcb,
        {'name':'[Bracket]'},
        RuntimeError,
        'Invalid name'
    )
    funcb('John')

    from docs.support.pcontracts_example_3 import (custom_contract1,
                                                   custom_contract2,
                                                   custom_contract3,
                                                   custom_contract4,
                                                   custom_contract5)
    from docs.support.pcontracts_example_3 import (custom_contract6,
                                                   custom_contract7,
                                                   custom_contract8,
                                                   custom_contract9,
                                                   custom_contract10)
    # Contract 1
    @putil.pcontracts.contract(name='custom_contract1')
    def func1(name):
        return name
    putil.test.assert_exception(
        func1, {'name':''}, RuntimeError, 'Invalid name'
    )
    assert func1('John') == 'John'
    # Contract 2
    @putil.pcontracts.contract(name='custom_contract2')
    def func2(name):
        return name
    putil.test.assert_exception(
        func2, {'name':''}, RuntimeError, 'Invalid name'
    )
    assert func2('John') == 'John'
    # Contract 3
    @putil.pcontracts.contract(name='custom_contract3')
    def func3(name):
        return name
    putil.test.assert_exception(
        func3,
        {'name':''},
        ValueError,
        'Argument `name` is not valid'
    )
    assert func3('John') == 'John'
    # Contract 4
    @putil.pcontracts.contract(name='custom_contract4')
    def func4(name):
        return name
    putil.test.assert_exception(
        func4,
        {'name':''},
        ValueError,
        'Argument `name` is not valid'
    )
    assert func4('John') == 'John'
    # Contract 5
    @putil.pcontracts.contract(name='custom_contract5')
    def func5(name):
        return name
    putil.test.assert_exception(
        func5, {'name':''}, RuntimeError, 'Invalid name'
    )
    assert func5('John') == 'John'
    # Contract 6
    @putil.pcontracts.contract(name='custom_contract6')
    def func6(name):
        return name
    putil.test.assert_exception(
        func6, {'name':''}, RuntimeError, 'Invalid name'
    )
    assert func6('John') == 'John'
    # Contract 7
    @putil.pcontracts.contract(name='custom_contract7')
    def func7(name):
        return name
    putil.test.assert_exception(
        func7,
        {'name':''},
        OSError,
        'File could not be opened'
    )
    assert func7('John') == 'John'
    # Contract 8
    @putil.pcontracts.contract(name='custom_contract8')
    def func8(name):
        return name
    putil.test.assert_exception(
        func8, {'name':''}, RuntimeError, 'Invalid name'
    )
    assert func8('John') == 'John'
    # Contract 9
    @putil.pcontracts.contract(name='custom_contract9')
    def func9(name):
        return name
    putil.test.assert_exception(
        func9,
        {'name':''},
        TypeError,
        'Argument `name` is not valid'
    )
    assert func9('John') == 'John'
    # Contract 10
    @putil.pcontracts.contract(name='custom_contract10')
    def func10(name):
        return name
    putil.test.assert_exception(
        func10,
        {'name':''},
        RuntimeError,
        'Argument `name` is not valid'
    )
    assert func10('John') == 'John'

def test_plot_doccode():
    """ Test used in plot module """
    from tests.plot.fixtures import compare_images, IMGTOL
    script_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'docs',
        'support'
    )
    script_name = os.path.join(script_dir, 'plot_example_1.py')
    output_file = 'test_image.png'
    proc = subprocess.Popen(
        ['python', script_name, output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    proc.communicate()
    test_fname = os.path.join(script_dir, output_file)
    ref_fname = os.path.join(script_dir, 'plot_example_1.png')
    metrics = compare_images(ref_fname, test_fname)
    result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
    ref_ci_fname = os.path.join(script_dir, 'plot_example_1_ci.png')
    metrics_ci = compare_images(ref_ci_fname, test_fname)
    result_ci = (metrics_ci[0] < IMGTOL) and (metrics_ci[1] < IMGTOL)
    if (not result) and (not result_ci):
        print('Images do not match')
        print(
            'Reference image: file://{0}'.format(os.path.realpath(ref_fname))
        )
        print('Reference CI image: file://{0}'.format(
            os.path.realpath(ref_ci_fname)
        ))
        print('Actual image: file://{0}'.format(os.path.realpath(test_fname)))
    if result or result_ci:
        with putil.misc.ignored(OSError):
            os.remove(test_fname)
    assert result or result_ci
    # Test ABC example
    import numpy, docs.support.plot_example_2
    obj = docs.support.plot_example_2.MySource()
    obj.indep_var = numpy.array([1, 2, 3])
    obj.dep_var = numpy.array([-1, 1, -1])
    assert obj.indep_var.tolist() == [1, 2, 3]
    assert obj.dep_var.tolist() == [-1, 1, -1]
    assert obj._complete
    #
    import docs.support.plot_example_3
    ivar, dvar = docs.support.plot_example_3.proc_func1(
        1e-12, numpy.array([1, 2])
    )
    dvar = dvar.tolist()
    assert ivar, dvar == (1, [0, 1])
    obj = docs.support.plot_example_3.create_csv_source()
    assert obj.indep_var.tolist() == [2, 3, 4]
    assert obj.dep_var.tolist() == [0, -30, 10]
    #
    import docs.support.plot_example_4
    obj = docs.support.plot_example_4.create_basic_source()
    assert obj.indep_var.tolist() == [2, 3]
    assert obj.dep_var.tolist() == [-10, 10]
    assert obj._complete
    #
    import docs.support.plot_example_5
    obj = docs.support.plot_example_5.create_csv_source()
    assert obj.indep_var.tolist() == [10, 11, 12, 13, 14]
    assert obj.dep_var.tolist() == [16, 6, 26, -4, 36]
