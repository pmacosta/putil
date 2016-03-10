#!/usr/bin/env python
# coveragerc_manager.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import os
import sys


###
# Global variables
###
SUBMODULES_LIST = ['plot', 'pcsv']


###
# Functions
###
def _write(fobj, data):
    """ Simple file write """
    fobj.write(data)


def get_source_files(sdir):
    """
    Get Python source files that are not __init__.py and
    interpreter-specific
    """
    ver = 3 if sys.hexversion < 0x03000000 else 2
    isf = []
    isf.append('conftest.py')
    isf.append('compat{0}.py'.format(ver))
    return [
        file_name
        for file_name in os.listdir(sdir)
        if file_name.endswith('.py') and (file_name != '__init__.py') and
        (not any([file_name.endswith(item) for item in isf]))
    ]


def main(argv):
    """ Processing """
    # pylint: disable=R0912,R0914,R0915,W0702
    debug = True
    env = argv[0].strip('"').strip("'")
    # Unpack command line arguments
    print('Coverage manager')
    print('Arguments received: {0}'.format(argv))
    if env == 'tox':
        print('Tox mode')
        if len(argv[1:]) == 4:
            mode_flag, interp, _, site_pkg_dir, submodules, module = (
                argv[1:]+[SUBMODULES_LIST, '']
            )
            print('   mode_flag: {0}'.format(mode_flag))
            print('   interp: {0}'.format(interp))
            print('   site_pkg_dir: {0}'.format(site_pkg_dir))
            print('   submodules: {0}'.format(submodules))
            print('   module: {0}'.format(module))
        else:
            mode_flag, interp, _, module = argv[1:]+['']
            print('   mode_flag: {0}'.format(mode_flag))
            print('   interp: {0}'.format(interp))
            print('   module: {0}'.format(module))
    elif env == 'ci':
        print('Continuous integration mode')
        mode_flag, interp, _, site_pkg_dir, submodules, module = (
            argv[1],
            argv[2],
            os.environ['REPO_DIR'],
            argv[3],
            SUBMODULES_LIST,
            ''
        )
        print('   mode_flag: {0}'.format(mode_flag))
        print('   interp: {0}'.format(interp))
        print('   site_pkg_dir: {0}'.format(site_pkg_dir))
        print('   submodules: {0}'.format(submodules))
        print('   module: {0}'.format(module))
    elif env == 'local':
        print('Local mode')
        if len(argv[1:]) == 4:
            mode_flag, interp, _, site_pkg_dir, submodules, module = (
                argv[1],
                argv[2],
                argv[3],
                argv[3],
                [argv[4]],
                argv[4]
            )
        else:
            mode_flag, interp, _, site_pkg_dir, submodules, module = (
                argv[1],
                argv[2],
                argv[3],
                argv[3],
                [''],
                ''
            )
        print('   mode_flag: {0}'.format(mode_flag))
        print('   interp: {0}'.format(interp))
        print('   site_pkg_dir: {0}'.format(site_pkg_dir))
        print('   submodules: {0}'.format(submodules))
        print('   module: {0}'.format(module))
    # Generate .coveragerc file
    is_submodule = module in SUBMODULES_LIST
    source_dir = os.path.join(site_pkg_dir, 'putil')
    output_file_name = os.path.join(
        site_pkg_dir,
        'putil',
        '.coveragerc_{0}_{1}'.format(env, interp)
    )
    coverage_file_name = os.path.join(
        site_pkg_dir, 'putil', '.coverage_{0}'.format(interp)
    )
    conf_file = []
    conf_file.append(os.path.join(source_dir, 'conftest.py'))
    conf_file.append(os.path.join(source_dir, 'plot', 'conftest.py'))
    if mode_flag == '1':
        lines = []
        lines.append(
            '# .coveragerc_{0} to control coverage.py during {1} runs'.format(
                env,
                env.capitalize()
            )
        )
        lines.append('[report]')
        lines.append('show_missing = True')
        lines.append('[run]')
        lines.append('branch = True')
        lines.append('data_file = {0}'.format(coverage_file_name))
        start_flag = True
        # Include modules
        source_files = get_source_files(os.path.join(site_pkg_dir, 'putil'))
        for file_name in [
                item
                for item in source_files
                if (env != 'local') or ((env == 'local') and
                   (not is_submodule) and (item == '{0}.py'.format(module)))]:
            if file_name.endswith('version.py'):
                continue
            start_flag, prefix = (
                (False, 'include = ')
                if start_flag else
                (False, 10*' ')
            )
            lines.append(
                '{0}{1}'.format(prefix, os.path.join(
                    site_pkg_dir,
                    'putil',
                    file_name
            )))
        # Include sub-modules
        if (env != 'local') or ((env == 'local') and is_submodule):
            for submodule in submodules:
                for file_name in [
                        item
                        for item in get_source_files(os.path.join(
                                site_pkg_dir,
                                'putil',
                                submodule))]:
                    start_flag, prefix = (
                        (False, 'include = ')
                        if start_flag else
                        (False, 10*' ')
                    )
                    lines.append('{0}{1}'.format(prefix, os.path.join(
                        site_pkg_dir,
                        'putil',
                        submodule,
                        file_name
                    )))
        # Generate XML reports for continuous integration
        if env == 'ci':
            lines.append('[xml]')
            lines.append('output = {0}'.format(os.path.join(
                os.environ['RESULTS_DIR'],
                'codecoverage',
                'coverage.xml'
            )))
        # Write file
        with open(output_file_name, 'w') as fobj:
            _write(fobj, ('\n'.join(lines))+'\n')
        # Echo file
        if debug:
            print('File: {0}'.format(output_file_name))
            with open(output_file_name, 'r') as fobj:
                print(''.join(fobj.readlines()))
        # Generate conftest.py files to selectively
        # skip Python 2 or Python 3 files
        skip_file = (
            "# pylint: disable=E0012,C0103,C0111,C0411\n"
            "import sys\n"
            "import matplotlib\n"
            "matplotlib.rcParams['backend'] = 'Agg'\n"
            "collect_ignore = []\n"
            "if sys.hexversion < 0x03000000:\n"
            "    collect_ignore.append('compat3.py')\n"
            "else:\n"
            "    collect_ignore.append('compat2.py')\n"
        )
        with open(conf_file[0], 'w') as fobj:
            _write(fobj, skip_file)
    else:
        del_files = conf_file
        del_files.append(output_file_name)
        del_files.append(coverage_file_name)
        try:
            for fname in del_files:
                print('Deleting file {0}'.format(fname))
                os.remove(fname)
        except:
            pass


if __name__ == '__main__':
    main(sys.argv[1:])
