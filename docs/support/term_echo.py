# term_echo.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import os, subprocess, sys

def ste(command, nindent, mdir, fpointer):
    """
    Simplified term_echo
    """
    term_echo(
        '${{PUTIL_DIR}}{sep}sbin{sep}{cmd}'.format(
            sep=os.path.sep, cmd=command
        ),
        nindent,
        {'PUTIL_DIR':mdir},
        fpointer
    )

def term_echo(command, nindent=0, env=None, fpointer=None):
    """
    Prints stdout resulting from a given shell
    command formatted in reStructuredText
    """
    command_int = command
    if env:
        for var, repl in env.items():
            command_int = command_int.replace('${'+var+'}', repl)
    proc = subprocess.Popen(
        command_int.split(' '),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout = proc.communicate()[0]

    if sys.hexversion >= 0x03000000:
        stdout = stdout.decode('utf-8')
    stdout = stdout.split('\n')
    indent = nindent*' '
    fpointer('\n', dedent=False)
    fpointer('{0}.. code-block:: bash\n'.format(indent), dedent=False)
    fpointer('\n', dedent=False)
    fpointer('{0}    $ {1}\n'.format(indent, command), dedent=False)
    for line in stdout:
        if line.strip():
            fpointer(
                indent+'    '+line.replace('\t', '    ')+'\n', dedent=False
            )
        else:
            fpointer('\n', dedent=False)
    fpointer('\n', dedent=False)
