# test_doccode.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,E1129,R0914,R0915,W0212,W0640

# Standard library imports
from __future__ import print_function
import os
import shutil
import subprocess
import sys
# PyPI imports
import matplotlib
# Putil imports
import putil.misc
from putil.test import AE

# Default to non-interactive PNG to avoid any
# matplotlib back-end misconfiguration
matplotlib.rcParams['backend'] = 'Agg'


###
# Functions
###
def export_image(fname, method=True):
    tdir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    artifact_dir = os.path.join(tdir, 'artifacts')
    if not os.path.exists(artifact_dir):
        os.makedirs(artifact_dir)
    if method:
        src = fname
        dst = os.path.join(artifact_dir, os.path.basename(fname))
        shutil.copyfile(src, dst)
    else:
        if os.environ.get('APPVEYOR', None):
            proc = subprocess.Popen(
                ['appveyor', 'PushArtifact', os.path.realpath(fname)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            proc.communicate()
        elif os.environ.get('TRAVIS', None):
            # If only a few binary files need to be exported a hex dump works,
            # otherwise the log can grow past 4MB and the process is terminated
            # by Travis
            proc = subprocess.Popen(
                [
                    os.path.join(tdir, 'sbin', 'png-to-console.sh'),
                    os.path.realpath(fname)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, _ = proc.communicate()
            print(stdout)


def test_exdoc_doccode():
    """ Test code used in exdoc module """
    def remove_header(stdout):
        """ Remove py.test header """
        actual_text = []
        off_header = False
        lines = (
            stdout.split('\n')
            if sys.hexversion < 0x03000000 else
            stdout.decode('ascii').split('\n')
        )
        for line in lines:
            off_header = line.startswith('Callable:') or off_header
            if off_header:
                actual_text.append(line)
        return '\n'.join(actual_text)
    # Test tracing module #1 (py.test based)
    script_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'docs',
        'support'
    )
    script_name = os.path.join(script_dir, 'trace_my_module_1.py')
    proc = subprocess.Popen(['python', script_name], stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    actual_text = remove_header(stdout)
    ref_list = []
    ref_list.append('Callable: docs.support.my_module.func')
    ref_list.append('.. Auto-generated exceptions documentation for')
    ref_list.append('.. docs.support.my_module.func')
    ref_list.append('')
    ref_list.append(':raises: TypeError (Argument \\`name\\` is not valid)')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('Callable: docs.support.my_module.MyClass.value')
    ref_list.append('.. Auto-generated exceptions documentation for')
    ref_list.append('.. docs.support.my_module.MyClass.value')
    ref_list.append('')
    ref_list.append(':raises:')
    ref_list.append(' * When assigned')
    ref_list.append('')
    ref_list.append('   * RuntimeError (Argument \\`value\\` is not valid)')
    ref_list.append('')
    ref_list.append(' * When retrieved')
    ref_list.append('')
    ref_list.append('   * RuntimeError (Attribute \\`value\\` not set)')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_text = (os.linesep).join(ref_list)
    if actual_text != ref_text:
        print('STDOUT: {0}'.format(stdout))
        print('STDERR: {0}'.format(stderr))
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
    with putil.misc.ignored(OSError):
        os.remove(output_file)
    bin_dir = os.environ['BIN_DIR']
    proc = subprocess.Popen(
        [
            'python',
            os.path.join(bin_dir, 'cog.py'),
            '-e',
            '-o', output_file,
            input_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, _ = proc.communicate()
    retcode = proc.returncode
    if retcode:
        print(stdout)
        raise RuntimeError('Tracing did not complete successfully')
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
        os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'support'
    )
    for num in range(1, 7):
        script_name = os.path.join(
            script_dir, 'pcsv_example_{0}.py'.format(num))
        proc = subprocess.Popen(
            ['python', script_name], stdout=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            print('Script: {0}'.format(script_name))
            print('STDOUT: {0}'.format(stdout))
            print('STDERR: {0}'.format(stderr))
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
    AE(funca, RuntimeError, 'Only one exception', name='')
    funca('John')
    AE(funcb, RuntimeError, 'Empty', name='')
    AE(funcb, RuntimeError, 'Invalid name', name='[Bracket]')
    funcb('John')
    from docs.support.pcontracts_example_3 import (
        custom_contract1,
        custom_contract2,
        custom_contract3,
        custom_contract4,
        custom_contract5
    )
    from docs.support.pcontracts_example_3 import (
        custom_contract6,
        custom_contract7,
        custom_contract8,
        custom_contract9,
        custom_contract10
    )
    # Contract 1
    @putil.pcontracts.contract(name='custom_contract1')
    def func1(name):
        return name
    AE(func1, RuntimeError, 'Invalid name', name='')
    assert func1('John') == 'John'
    # Contract 2
    @putil.pcontracts.contract(name='custom_contract2')
    def func2(name):
        return name
    AE(func2, RuntimeError, 'Invalid name', name='')
    assert func2('John') == 'John'
    # Contract 3
    @putil.pcontracts.contract(name='custom_contract3')
    def func3(name):
        return name
    AE(func3, ValueError, 'Argument `name` is not valid', name='')
    assert func3('John') == 'John'
    # Contract 4
    @putil.pcontracts.contract(name='custom_contract4')
    def func4(name):
        return name
    AE(func4, ValueError, 'Argument `name` is not valid', name='')
    assert func4('John') == 'John'
    # Contract 5
    @putil.pcontracts.contract(name='custom_contract5')
    def func5(name):
        return name
    AE(func5, RuntimeError, 'Invalid name', name='')
    assert func5('John') == 'John'
    # Contract 6
    @putil.pcontracts.contract(name='custom_contract6')
    def func6(name):
        return name
    AE(func6, RuntimeError, 'Invalid name', name='')
    assert func6('John') == 'John'
    # Contract 7
    @putil.pcontracts.contract(name='custom_contract7')
    def func7(name):
        return name
    AE(func7, OSError, 'File could not be opened', name='')
    assert func7('John') == 'John'
    # Contract 8
    @putil.pcontracts.contract(name='custom_contract8')
    def func8(name):
        return name
    AE(func8, RuntimeError, 'Invalid name', name='')
    assert func8('John') == 'John'
    # Contract 9
    @putil.pcontracts.contract(name='custom_contract9')
    def func9(name):
        return name
    AE(func9, TypeError, 'Argument `name` is not valid', name='')
    assert func9('John') == 'John'
    # Contract 10
    @putil.pcontracts.contract(name='custom_contract10')
    def func10(name):
        return name
    AE(func10, RuntimeError, 'Argument `name` is not valid', name='')
    assert func10('John') == 'John'

def test_plot_doccode(capsys):
    """ Test used in plot module """
    # pylint: disable=E1103,R0204
    from tests.plot.fixtures import compare_images
    script_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'docs',
        'support'
    )
    script_name = os.path.join(script_dir, 'plot_example_1.py')
    output_file = os.path.join(script_dir, 'test_image.png')
    proc = subprocess.Popen(
        ['python', script_name, output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, stderr = proc.communicate()
    test_fname = output_file
    nimages = 11
    ref_names = [
        'plot_example_1_{0}.png'.format(item) for item in range(1, nimages+1)
    ]
    ref_fnames = [os.path.join(script_dir, item) for item in ref_names]
    result = []
    for ref_fname in ref_fnames:
        try:
            result.append(compare_images(ref_fname, test_fname))
        except IOError:
            print('Error comparing images')
            print('STDOUT: {0}'.format(stdout))
            print('STDERR: {0}'.format(stderr))
            raise
    if not any(result):
        print('Images do not match')
        print('STDOUT: {0}'.format(stdout))
        print('STDERR: {0}'.format(stderr))
        for num, ref_fname in enumerate(ref_fnames):
            print(
                'Reference image {0}: file://{1}'.format(
                    num, os.path.realpath(ref_fname)
                )
            )
        print('Actual image: file://{0}'.format(os.path.realpath(test_fname)))
        export_image(test_fname)
    assert result
    with putil.misc.ignored(OSError):
        os.remove(test_fname)
    # Test ABC example
    import numpy
    import docs.support.plot_example_2
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
    #
    import docs.support.plot_example_6
    docs.support.plot_example_6.panel_iterator_example(no_print=False)
    stdout, stderr = capsys.readouterr()
    ref = (
        'Series 1:\n'
        'Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]\n'
        'Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]\n'
        'Label: Goals\n'
        'Color: k\n'
        'Marker: o\n'
        'Interpolation: CUBIC\n'
        'Line style: -\n'
        'Secondary axis: False\n'
        '\n'
        'Series 2:\n'
        'Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]\n'
        'Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]\n'
        'Label: Saves\n'
        'Color: b\n'
        'Marker: None\n'
        'Interpolation: STRAIGHT\n'
        'Line style: --\n'
        'Secondary axis: False\n\n'
    )
    assert stdout == ref
