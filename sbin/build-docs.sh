#!/bin/bash
# build-docs.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

set -e

print_usage_message () {
	echo -e "build-docs.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  build-docs.sh [-h] [-n num-cpus] [-r] [module-name]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
	echo -e "  -r  Rebuild exceptions documentation. If no module name" >&2
	echo -e "      is given all modules with auto-generated exceptions" >&2
	echo -e "      documentation are rebuilt" >&2
	echo -e "  -n  Number of CPUs to use (greater than 2)" >&2
}

finish() {
	export TRACER_DIR=""
	export NOPTION=""
	export SUPPORT_DIR=""
	cd ${cpwd}
}
trap finish EXIT

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

source ${pkg_dir}/sbin/functions.sh

# Default values for command line options
rebuild=0
modules=(eng pcsv plot tree)
num_cpus=""
# Read command line options
while getopts ":rhn:" opt; do
	case ${opt} in
		r)
			rebuild=1
			;;
		h)
			print_usage_message
			exit 0
			;;
		n)
			num_cpus=${OPTARG}
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

# Argument validation
export NOPTION=""
if [ "${num_cpus}" != "" ]; then
	num_cpus=$(echo "${num_cpus}" | grep "^[2-9][0-9]*$")
	if [ "${num_cpus}" == "" ]; then
		echo "build-docs.sh: number of CPUs has to be an intenger greater than 1"
		exit 1
	fi
	if ! pip freeze | grep -q pytest-xdist; then
		echo "build-docs.sh: pytest-xdist needs to be installed to use multiple CPUS"
		exit 1
	fi
	export NOPTION="-n ${num_cpus}"
fi


if [ ${rebuild} == 1 ]; then
	echo "Are you sure [Y/N]? "
	read -s -n 1 answer
	if [ "${answer^^}" == "Y" ]; then
		echo "Rebuilding exceptions documentation"
		start_time=$(date +%s)
		for module in ${modules[@]}; do
			if [ "${module}" == "plot" ]; then
				module_dir=${src_dir}/plot
				submodules=(basic_source csv_source figure functions panel series)
			else
				module_dir=${src_dir}
				submodules=(${module})
			fi
			for submodule in ${submodules[@]}; do
				submodule_file="${module_dir}"/"${submodule}".py
				if [ ! -f "${submodule_file}" ]; then
					echo "Module ${submodule_file} not found"
					exit 1
				else
					echo "   Processing module ${submodule_file}"
					if cog.py -e -x -o ${submodule_file}.tmp ${submodule_file}; then
						mv -f ${submodule_file}.tmp ${submodule_file}
						if cog.py -e -o ${submodule_file}.tmp ${submodule_file}; then
							mv -f ${submodule_file}.tmp ${submodule_file}
						else
							echo "Error generating exceptions documentation in module ${submodule_file}"
							exit 1
						fi
					else
						echo "Error deleting exceptions documentation in module ${submodule_file}"
						exit 1
					fi
				fi
			done
		done
		stop_time=$(date +%s)
		ellapsed_time=$((stop_time-start_time))
		show_time ${ellapsed_time}
	else
		exit 0
	fi
fi

echo "Inserting files into docstrings"
if [ ${rebuild} == 1 ]; then
	modules=(misc pcontracts)
else
	modules=(misc pcontracts plot tree)
fi
for module in ${modules[@]}; do
	if [ "${module}" == "plot" ]; then
		module_dir=${src_dir}/plot
		submodules=(basic_source csv_source figure functions panel series)
	else
		module_dir=${src_dir}
		submodules=(${module})
	fi
	for submodule in ${submodules[@]}; do
		submodule_file="${module_dir}"/"${submodule}".py
		if [ ! -f "${submodule_file}" ]; then
			echo "Module ${submodule_file} not found"
			exit 1
		elif grep -q "incfile.incfile" ${submodule_file}; then
			echo "   Processing module ${submodule_file}"
			if cog.py --markers='=[=cog =]= =[=end=]=' -e -x -o ${submodule_file}.tmp ${submodule_file}; then
				mv -f ${submodule_file}.tmp ${submodule_file}
				if cog.py --markers='=[=cog =]= =[=end=]=' -e -o ${submodule_file}.tmp ${submodule_file}; then
					mv -f ${submodule_file}.tmp ${submodule_file}
				else
					echo "Error inserting files in docstrings in module ${submodule_file}"
					exit 1
				fi
			else
				echo "Error deleting insertion of files in docstrings in module ${submodule_file}"
				exit 1
			fi
		fi
	done
done

file=${pkg_dir}/README.rst
echo "Inserting files into ${file}"
if cog.py -e -x -o ${file}.tmp ${file}; then
	mv -f ${file}.tmp ${file}
	if cog.py -e -o ${file}.tmp ${file}; then
		mv -f ${file}.tmp ${file}
	else
		echo "Error inserting file output in ${file}"
	fi
else
	echo "Error inserting file output in ${file}"
fi

cd ${pkg_dir}/docs
make html
