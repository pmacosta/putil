#!/bin/bash
# build-docs.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

print_usage_message () {
	echo -e "build-docs.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  build-docs.sh [-h] [-r] [module-name]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
	echo -e "  -r  Rebuild exceptions documentation. If no module name is given all" >&2
	echo -e "      modules with auto-generated exceptions documentation are rebuilt\n" >&2
}

# Find directory where script is (from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in)
source="${BASH_SOURCE[0]}"
while [ -h "${source}" ]; do # resolve $source until the file is no longer a symlink
	dir="$( cd -P "$( dirname "${source}" )" && pwd )"
	source="$(readlink "${source}")"
	[[ ${source} != /* ]] && source="$dir/$source" # if $source was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
dir="$( cd -P "$( dirname "${source}" )" && pwd )"
pkg_dir=$(dirname ${dir})
src_dir=${pkg_dir}/putil
cpwd=${PWD}
export TRACER_DIR=${pkg_dir}/docs/support

# Default values for command line options
rebuild=0
modules=(eng pcsv plot tree)

# Read command line options
while getopts ":rh" opt; do
	case ${opt} in
		r)
			rebuild=1
			;;
		h)
			print_usage_message
			exit 0
			;;
		\?)
			echo "build-docs.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((${OPTIND} - 1))
if [ "$#" != 0 ]; then
	modules=("$@")
fi

if [ ${rebuild} == 1 ]; then
	echo 'Rebuilding exceptions documentation'
	for module in ${modules[@]}; do
		module_file="${src_dir}"/"${module}".py
		if [ ! -f "${module_file}" ]; then
			echo "Module ${module_file} not found"
		else
			echo '   Processing module '${module_file}
			if cog.py -e -x -o ${module_file}.tmp ${module_file}; then
			       mv -f ${module_file}.tmp ${module_file}
			       if cog.py -e -o ${module_file}.tmp ${module_file}; then
					mv -f ${module_file}.tmp ${module_file}
			       else
					echo "Error generating exceptions documentation in module ${module_file}"
			       fi
		       else
			       echo "Error deleting exceptions documentation in module ${module_file}"
		       fi
		fi
	done
fi

cd ${pkg_dir}/docs
make html
export TRACER_DIR=""
cd ${cpwd}
