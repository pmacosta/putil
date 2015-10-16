#!/bin/bash
# install-python.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

# Exit upon error
set -e

source $(dirname "${BASH_SOURCE[0]}")/functions.sh
cwd=${PWD}
pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))

finish() {
	cd ${cwd}
	exit $1
}

exit_if_not_root () {
	if [ ${EUID} -ne 0 ]; then
		echo "install-python.sh: root privileges needed"
		finish 1
	fi
}

install_pkg () {
	if ! dpkg --status $1 >/dev/null; then
		if apt-get --yes --force-yes --simulate install $1; then
			echo "Installing package $1"
			apt-get --yes --force-yes install $1
		else
			echo "Package $1 not available"
		fi
	else
		echo "Package $1 already installed"
	fi
}

trap finish EXIT ERR SIGINT

exit_if_not_root

vers=(3.0.1 3.1.5 3.2.6 3.3.6)
for ver in ${vers[@]}; do
	short_ver=$(echo ${ver} | sed -r 's/(.+)\.(.+)(\..*)/\1.\2/g')
	python_cmd=python${short_ver}
	pip_cmd=pip${short_ver}
	build_dir=${HOME}/build/python-${ver}
	dest_dir=/opt/${python_cmd}
	tar_file=Python-${ver}.tgz
	inst=get-pip.py
	if which ${python_cmd} >/dev/null; then
		print_green_line \
			"Python ${short_ver} (${ver}) already installed"
	else
		print_green_line "Installing Python ${short_ver} (${ver})"
		install_pkg zlib1g
		install_pkg zlib1g-dev
		mkdir -p ${build_dir}
		wget https://www.python.org/ftp/python/${ver}/${tar_file} \
			-O ${build_dir}/${tar_file}
		cd ${build_dir}
		tar xvfz ${tar_file}
		mkdir -p ${dest_dir}
		cd ${tar_file%.*}
		./configure --prefix=${dest_dir}
		make
		sudo make install
		sudo ln -s /opt/python${short_ver}/bin/python${short_ver} \
			/usr/bin/python${short_ver}
	fi
	if which ${pip_cmd} >/dev/null; then
		print_green_line "pip ${short_ver} already installed"
	else
		print_green_line "Installing pip ${short_ver}"
		mkdir -p ${build_dir}
		wget https://bootstrap.pypa.io/${inst} -O ${build_dir}/${inst}
		cd ${build_dir}
		${python_cmd} ${inst}
		sudo ln -s /opt/python${short_ver}/bin/pip${short_ver} \
			/usr/bin/pip${short_ver}
	fi
	rm -rf ${build_dir}
done
