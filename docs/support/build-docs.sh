#!/bin/bash
set -e
module_file=my_module.py
cog.py -e -x -o ${module_file}.tmp ${module_file} > /dev/null && mv -f ${module_file}.tmp ${module_file}
cog.py -e -o ${module_file}.tmp ${module_file} > /dev/null && mv -f ${module_file}.tmp ${module_file}
