#!/bin/bash
# pkg-validate.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

# Exit upon error
set -e

source $(dirname "${BASH_SOURCE[0]}")/functions.sh

print_usage_message () {
	echo -e "pkg-validate.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  pkg-validate.sh -h" >&2
	echo -e "  pkg-validate.sh [-n num-cpus] [-e env]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
	echo -e "  -e  Interpreter version [default: PY27|py34]" >&2
	echo -e "  -n  Number of CPUs to use [default: 1]" >&2
}

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))
src_dir=${pkg_dir}/putil
cwd=${PWD}

finish() {
	cd ${cwd}
	exit $1
}

# Read command line options
num_cpus=""
interp=""
while getopts ":he:n:" opt; do
	case ${opt} in
		h)
			print_usage_message
			finish 0
			;;
		e)
			interp=${OPTARG}
			;;
		n)
			num_cpus=${OPTARG}
			;;
		\?)
			echo "pkg-validate.sh: invalid option" >&2
			print_usage_message
			finish 1
			;;
	esac
done
shift $((${OPTIND} - 1))
if [ "$#" != 0 ]; then
	echo "pkg-validate.sh: too many command line arguments" >&2
	finish 1
fi

# Argument validation
nopt=$(validate_num_cpus "pkg-validate.sh" "${num_cpus}")
if [ $? != 0 ]; then
	finish 1
fi


interp=${interp,,}
if [ "${interp}" != "py27" ] && [ "${interp}" != "py34" ] && [ "${interp}" != "" ]; then
	echo "pkg-validate.sh: invalid interpreter version" >&2
	finish 1
fi
if [ "${interp}" == "py27" ]; then
	print_green_line "Python 2.7 package validation"
	eopt="-e py27"
	doc_versions=(docs27)
elif [ "${interp}" == "py34" ]; then
	print_green_line  "Python 3.4 package validation"
	eopt="-e py34"
	doc_versions=(docs34)
else
	print_green_line "Python 2.7 and 3.4 package validation"
	eopt=""
	doc_versions=(docs27 docs34)
fi


# Processing
cd ${pkg_dir}
${pkg_dir}/sbin/test.sh ${nopt} -d ${eopt}
${pkg_dir}/sbin/test.sh ${nopt} -c ${eopt}
print_banner "Verifying exceptions auto-documentation"
${pkg_dir}/sbin/build-docs.sh ${nopt} -r -t
print_banner "Testing documentation"
for version in ${doc_versions[@]}; do
	tox -e ${version}
done
print_banner "Verifying Pylint annotations"
${pkg_dir}/sbin/pylint-cleaner.py
print_banner "Verifying files standard compliance"
${pkg_dir}/sbin/check-files-compliance.py
