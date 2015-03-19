#!/bin/bash
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

# Default values for command line options
rebuild=0
modules=(eng pcsv plot tree)

# Read command line options
while getopts "r --long rebuild" opt; do
	case ${opt} in
		r|rebuild)
			rebuild=1
			;;
		\?)
			echo 'Invalid option: $OPTARG' >&2
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
cd ${cpwd}
