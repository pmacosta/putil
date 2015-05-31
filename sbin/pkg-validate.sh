#!/bin/bash
# pkg-validate.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

set -e

source $(dirname "${BASH_SOURCE[0]}")/functions.sh

print_usage_message () {
	echo -e "pkg-validate.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  pkg-validate.sh -h" >&2
	echo -e "  pkg-validate.sh [-n num-cpus]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
	echo -e "  -n  Number of CPUs to use [default: 1]" >&2
}

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))
src_dir=${pkg_dir}/putil
cpwd=${PWD}

# Read command line options
num_cpus=""
while getopts ":hn:" opt; do
	case ${opt} in
		h)
			print_usage_message
			exit 0
			;;
		n)
			num_cpus=${OPTARG}
			;;
		\?)
			echo "pkg-validate.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((${OPTIND} - 1))
if [ "$#" != 0 ]; then
	echo "pkg-validate.sh: too many command line arguments" >&2
	exit 1
fi

# Argument validation
noption=$(validate_num_cpus "pkg-validate.sh" "${num_cpus}")
if [ $? != 0 ]; then
	exit 1
fi

# Processing
cd ${pkg_dir}
${pkg_dir}/sbin/test.sh ${noption} -d
${pkg_dir}/sbin/test.sh ${noption} -c
print_banner "Testing documentation"
tox -e docs
print_banner "Verifying Pylint annotations"
${pkg_dir}/sbin/pylint-cleaner.py
print_banner "Verifying files standard compliance"
${pkg_dir}/sbin/check-files-compliance.py
cd ${cpwd}
