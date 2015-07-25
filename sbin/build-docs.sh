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
	echo -e "  build-docs.sh -r -t [-d dir] [-n num-cpus] [module-name]" >&2
	echo -e "  build-docs.sh [-d dir] [module-name]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
	echo -e "  -r  Rebuild exceptions documentation. If no module name" >&2
	echo -e "      is given all modules with auto-generated exceptions" >&2
	echo -e "      documentation are rebuilt" >&2
	echo -e "  -d  Specify source file directory" >&2
	echo -e "      [default: (build-docs.sh directory)/../putil]" >&2
	echo -e "  -t  Diff original and rebuilt file(s) (exit code 0" >&2
	echo -e "      indicates file(s) are identical, exit code 1" >&2
	echo -e "      file(s) are different" >&2
	echo -e "  -n  Number of CPUs to use [default: 1]" >&2
}

cpwd=${PWD}
finish() {
	export TRACER_DIR=""
	export NOPTION=""
	export SUPPORT_DIR=""
	rm -rf ${smf}.tmp
	cd ${cpwd}
}
trap finish EXIT ERR SIGINT

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))
export TRACER_DIR=${pkg_dir}/docs/support
src_dir=${pkg_dir}/putil
plot_submodules=(basic_source csv_source figure "functions" panel series)

# Default values for command line options
rebuild=0
modules=(eng pcsv plot tree)
num_cpus=""
test_mode=0
# Read command line options
while getopts ":rthn:d:" opt; do
	case ${opt} in
		h)
			print_usage_message
			exit 0
			;;
		d)
			src_dir=${OPTARG}
			;;
		n)
			num_cpus=${OPTARG}
			;;
		r)
			rebuild=1
			;;
		t)
			test_mode=1
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

if [ ${rebuild} == 1 ] && [ ${test_mode} == 0 ]; then
	echo "Are you sure [Y/N]? "
	read -s -n 1 answer
	if [ "${answer^^}" != "Y" ]; then
		exit 0
	fi
fi

if [ ! -d "${src_dir}" ]; then
	echo "build-docs.sh: source directory ${src_dir} does not exist" >&2
	exit 1
fi

if [ ${rebuild} == 1 ]; then
	echo "Rebuilding exceptions documentation"
	start_time=$(date +%s)
	for module in ${modules[@]}; do
		if [ "${module}" == "plot" ]; then
			module_dir=${src_dir}/plot
			submodules=(${plot_submodules[@]})
		else
			module_dir=${src_dir}
			submodules=(${module})
		fi
		for submodule in ${submodules[@]}; do
			smf="${module_dir}"/"${submodule}".py
			istring="File ${smf} identical from original"
			dstring="File ${smf} differs from original"
			if [ ! -f "${smf}" ]; then
				echo "Module ${smf} not found"
				exit 1
			fi
			echo "   Processing module ${smf}"
			orig_file=${smf}.orig
			if [ ${test_mode} == 1 ]; then
				cp ${smf} ${orig_file}
			fi
			if cog.py -e -o ${smf}.tmp ${smf}; then
				mv -f ${smf}.tmp ${smf}
				if [ ${test_mode} == 1 ]; then
					if diff ${smf} ${orig_file}; then
						echo ${istring}
						rm -rf ${orig_file}
					else
						echo ${dstring}
						cp -f ${smf} ${smf}.error
						mv -f ${orig_file} ${smf}
						exit 1
					fi
				fi
			else
				echo "Error generating exceptions"\
				     "documentation in module"\
				     "${smf}"
				exit 1
			fi
		done
	done
	stop_time=$(date +%s)
	ellapsed_time=$((stop_time-start_time))
	show_time ${ellapsed_time}
fi

if [ ${test_mode} == 1 ]; then
	exit 0
fi

echo "Inserting files into docstrings"
modules=(misc pcontracts plot tree)
for module in ${modules[@]}; do
	if [ "${module}" == "plot" ]; then
		module_dir=${src_dir}/plot
		submodules=(${plot_submodules[@]})
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
