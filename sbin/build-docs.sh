#!/bin/bash
# build-docs.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

set -e

source $(dirname "${BASH_SOURCE[0]}")/functions.sh

print_usage_message () {
	echo -e "build-docs.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  build-docs.sh -h" >&2
	echo -e "  build-docs.sh -r [-n num-cpus] [module-name]" >&2
	echo -e "  build-docs.sh [module-name]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
	echo -e "  -r  Rebuild exceptions documentation. If no module name" >&2
	echo -e "      is given all modules with auto-generated exceptions" >&2
	echo -e "      documentation are rebuilt" >&2
	echo -e "  -n  Number of CPUs to use [default: 1]" >&2
}

finish() {
	export TRACER_DIR=""
	export NOPTION=""
	export SUPPORT_DIR=""
	cd ${cpwd}
}
trap finish EXIT

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))
src_dir=${pkg_dir}/putil
cpwd=${PWD}
export TRACER_DIR=${pkg_dir}/docs/support
plot_submodules=(basic_source csv_source figure functions panel series)

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
export NOPTION=$(validate_num_cpus "build-docs.sh" "${num_cpus}")
if [ $? != 0 ]; then
	exit 1
fi

if [ "${NOPTION}" != "" ] && [ ${rebuild} == 0 ]; then
	echo "build-docs.sh: multiple CPUs not allowed" >&2
	exit 1
fi

if [ ${rebuild} == 1 ]; then
	echo "Are you sure [Y/N]? "
	read -s -n 1 answer
	if [ "${answer^^}" != "Y" ]; then
		exit 0
	fi
fi

if [ ${rebuild} == 1 ]; then
	echo "Rebuilding exceptions documentation"
	start_time=$(date +%s)
	for module in ${modules[@]}; do
		if [ "${module}" == "plot" ]; then
			module_dir=${src_dir}/plot
			submodules=${plot_submodules}
		else
			module_dir=${src_dir}
			submodules=(${module})
		fi
		for submodule in ${submodules[@]}; do
			smf="${module_dir}"/"${submodule}".py
			if [ ! -f "${smf}" ]; then
				echo "Module ${smf} not found"
				exit 1
			fi
			echo "   Processing module ${smf}"
			if cog.py -e -x -o ${smf}.tmp ${smf}; then
				mv -f ${smf}.tmp ${smf}
				if cog.py -e -o ${smf}.tmp ${smf}; then
					mv -f ${smf}.tmp ${smf}
				else
					echo "Error generating exceptions"\
					     "documentation in module"\
					     "${smf}"
					exit 1
				fi
			else
				echo "Error deleting exceptions documentation"\
				     "in module ${smf}"
				exit 1
			fi
		done
	done
	stop_time=$(date +%s)
	ellapsed_time=$((stop_time-start_time))
	show_time ${ellapsed_time}
fi

echo "Inserting files into docstrings"
modules=(misc pcontracts plot tree)
for module in ${modules[@]}; do
	if [ "${module}" == "plot" ]; then
		module_dir=${src_dir}/plot
		submodules=${plot_submodules}
	else
		module_dir=${src_dir}
		submodules=(${module})
	fi
	for submodule in ${submodules[@]}; do
		smf="${module_dir}"/"${submodule}".py
		if [ ! -f "${smf}" ]; then
			echo "Module ${smf} not found"
			exit 1
		elif ! grep -q "incfile.incfile" ${smf}; then
			continue
		fi
		echo "   Processing module ${smf}"
		if cog.py --markers='=[=cog =]= =[=end=]=' \
		   -e -x -o ${smf}.tmp ${smf}; then
			mv -f ${smf}.tmp ${smf}
			if cog.py --markers='=[=cog =]= =[=end=]=' \
			   -e -o ${smf}.tmp ${smf}; then
				mv -f ${smf}.tmp ${smf}
			else
				echo "Error inserting files in docstrings"\
			             "in module ${smf}"
				exit 1
			fi
		else
			echo "Error deleting insertion of files in"\
			     "docstrings in module ${smf}"
			exit 1
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
