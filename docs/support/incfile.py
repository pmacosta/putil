# incfile.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0914

import os


def incfile(file_name, mobj, lrange='1,6-'):
    """
    Reads file ${TRACER_DIR}/file_name and passes lines (without file
    header to a function
    """
    # Read file
    fpointer = mobj.out
    file_dir = os.environ['TRACER_DIR']
    file_name = os.path.join(file_dir, file_name)
    with open(file_name) as fobj:
        lines = fobj.readlines()
    # Parse line specification
    tokens = [item.strip() for item in lrange.split(',')]
    inc_lines = []
    for token in tokens:
        if '-' in token:
            subtokens = token.split('-')
            lmin, lmax = (
                int(subtokens[0]),
                int(subtokens[1]) if subtokens[1] else len(lines)
            )
            for num in range(lmin, lmax+1):
                inc_lines.append(num)
        else:
            inc_lines.append(int(token))
    # Produce output
    fpointer('.. code-block:: python\n')
    fpointer('\n')
    for num, line in enumerate(lines):
        if num+1 in inc_lines:
            fpointer(
                '    '+line.replace('\t', '    ') if line.strip() else '\n'
            )
    fpointer('\n')
