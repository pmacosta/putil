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
	echo -e "      indicates file(s) are different)" >&2
	echo -e "  -n  Number of CPUs to use [default: 1]" >&2
}

cpwd=${PWD}
finish() {
	export TRACER_DIR=""
	export NOPTION=""
	export SUPPORT_DIR=""
	rm -rf ${smf}.tmp
	find ${pkg_dir}/docs -type f -name '*.json'\
		-not -name 'moddb.json' -delete
	cd ${cpwd}
}
trap finish EXIT ERR SIGINT

echo_cyan() {
	if [ ${test_mode} == 1 ]; then
		print_cyan_line "$1"
	else
		echo "$1"
	fi
}

echo_green() {
	if [ ${test_mode} == 1 ]; then
		print_green_line "$1"
	else
		echo "$1"
	fi
}

echo_red() {
	if [ ${test_mode} == 1 ]; then
		print_red_line "$1" >&2
	else
		echo "$1" >&2
	fi
}

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))
export TRACER_DIR=${pkg_dir}/docs/support
src_dir=${pkg_dir}/putil
plot_submodules=(basic_source csv_source figure "functions" panel series)
pcsv_submodules=(concatenate csv_file dsort merge replace write)

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

if [ ${test_mode} == 1 ]; then
	rm -rf ${TRACER_DIR}/*.pkl ${TRACER_DIR}/plot/*.pkl
fi
if [ ${rebuild} == 1 ]; then
	test_msg=""
	if [ ${test_mode} == 1 ]; then
		test_msg="(test mode)"
	fi
	${pkg_dir}/sbin/refresh_moddb.py
	echo_cyan "Rebuilding exceptions documentation ${test_msg}"
	start_time=$(date +%s)
	for module in ${modules[@]}; do
		if [ "${module}" == "plot" ]; then
			module_dir=${src_dir}/plot
			submodules=(${plot_submodules[@]})
			pkl_dir=${TRACER_DIR}
		elif [ "${module}" == "pcsv" ]; then
			module_dir=${src_dir}/pcsv
			submodules=(${pcsv_submodules[@]})
			pkl_dir=${TRACER_DIR}
		else
			pkl_dir=${TRACER_DIR}
			module_dir=${src_dir}
			submodules=(${module})
		fi
		for submodule in ${submodules[@]}; do
			smf="${module_dir}"/"${submodule}".py
			pkl_file="${pkl_dir}"/"${submodule}".pkl
			istring="   File ${smf} identical from original"
			dstring="   File ${smf} differs from original"
			if [ ! -f "${smf}" ]; then
				echo "Module ${smf} not found"
				exit 1
			fi
			echo_cyan "   Processing module ${smf}"
			orig_file=${smf}.orig
			if [ ${test_mode} == 1 ]; then
				cp ${smf} ${orig_file}
			fi
			trace_error=0
			if [ ${test_mode} == 1 ]; then
				if cog.py -e -o ${smf}.tmp ${smf} &>/dev/null
				then
					trace_error=0
				else
					trace_error=1
				fi
			else
				if cog.py -e -o ${smf}.tmp ${smf}; then
					trace_error=0
				else
					trace_error=1
				fi
			fi
			if [ "${trace_error}" == 0 ]; then
				mv -f ${smf}.tmp ${smf}
				if [ ${test_mode} == 1 ]; then
					if diff ${smf} ${orig_file}; then
						echo_green "${istring}"
						rm -rf ${orig_file} ${pkl_file}
					else
						echo_red "${dstring}"
						cp -f ${smf} ${smf}.error
						mv -f ${orig_file} ${smf}
						exit 1
					fi
				else
					rm -rf ${pkl_file}
				fi
			else
				echo "Error generating exceptions"\
				     "documentation in module"\
				     "${smf}" >&2
				exit 1
			fi
		done
	done
	${pkg_dir}/sbin/build_moddb.py
	stop_time=$(date +%s)
	ellapsed_time=$((stop_time-start_time))
	show_time ${ellapsed_time}
fi

echo "Performing module-specific actions"
for module in ${modules[@]}; do
	if [ "${module}" == "plot" ]; then
		echo "   Processing module ${module}"
		python $TRACER_DIR/plot_example_1.py plot_example_1.png 1
	fi
done

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

files=(${pkg_dir}/README.rst ${pkg_dir}/docs/pcontracts.rst)
echo "Inserting files documentation files"
for file in "${files[@]}"; do
	echo "   Processing file ${file}"
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
done

cd ${pkg_dir}/docs
rm -rf _build
# Build documentation turning warnings into errors
make html SPHINXOPTS=-W
