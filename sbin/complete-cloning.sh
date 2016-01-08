#!/bin/bash
# complete-cloning.sh
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details

source $(dirname "${BASH_SOURCE[0]}")/functions.sh

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))
bin_dir=${pkg_dir}/sbin
cpwd=${PWD}

print_usage_message () {
	echo -e "complete-cloning.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  complete-cloning.sh -h -e\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  show this help message and exit" >&2
	echo -e "  -e  enforce e-mail check when Git pushing" >&2
}

check_email=0
# Read command line options
while getopts ":he" opt; do
	case ${opt} in
		h)
			print_usage_message
			exit 0
			;;
		e)
			check_email=1
			;;
		\?)
			echo "complete-cloning.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((${OPTIND} - 1))

# Set up pre-commit Git hooks
echo "Installing Git hooks"
source ${bin_dir}/setup-git-hooks.sh
if [ "${check_email}" == 1 ]; then
	sed -i -r 's/^check_email=[0|1]$/check_email=1/g' \
		${pkg_dir}/.hooks/pre-commit
else
	sed -i -r 's/^check_email=[0|1]$/check_email=0/g' \
		${pkg_dir}/.hooks/pre-commit
fi

# Build documentation
${bin_dir}/build_docs.py
