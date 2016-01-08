#!/bin/bash
# build-docs.sh
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details

set -e

finish() {
	export TRACER_DIR=""
	cd ${cpwd}
}
trap finish EXIT

input_file=${1:-my_module.py}
output_file=${2:-my_module.py}
export TRACER_DIR=$(dirname ${input_file})
cog.py -e -x -o ${input_file}.tmp ${input_file} > /dev/null && \
	mv -f ${input_file}.tmp ${input_file}
cog.py -e -o ${input_file}.tmp ${input_file} > /dev/null && \
	mv -f ${input_file}.tmp ${output_file}
