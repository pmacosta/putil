#!/bin/bash

# Exit upon error
set -e

release=$1
working_release=$2

install_pkg () {
	if ! dpkg --status $1 >/dev/null; then
		if apt-get --yes --force-yes --simulate --no-install-recommends install $1; then
			echo -e "\tInstalling package $1"
			apt-get --yes --force-yes --no-install-recommends install $1
		else
			echo -e "\tPackage $1 not available"
		fi
	else
		echo -e "\tPackage $1 already installed"
	fi
}

install_pkg_list () {
	# $1: install flag, $2: message, $3: package list
	if [ $1 == 1 ]; then
		if [ -n "$2" ]; then
			echo -e "$2"
		fi
		shift 2
		for pkg in "$@"; do
			install_pkg ${pkg}
		done
	fi
}

pip_install_pkg () {
	if ! pip freeze | grep $1; then
		if [ "$#" -eq 2 ]; then
			echo -e "\tInstalling package $1 version $2"
			pip install "$1"=="$2"
		else
			echo -e "\tInstalling package $1"
			pip install $1
		fi
	else
		echo -e "\tPackage $1 already installed"
	fi
}

pip_install_pkg_list () {
	# $1: install flag, $2: message, $3: package list
	if [ $1 == 1 ]; then
		if [ -n "$2" ]; then
			echo -e "$2"
		fi
		shift 2
		for pkg in "$@"; do
			pip_install_pkg ${pkg}
		done
	fi
}

install_base_pkgs=1
install_python_pkgs=1
debug=0
base_pkgs=(gfortran libfreetype6-dev liblapack-dev python-dev libpng12-dev python-pip g++)
python_pip_install_pkgs=(coverage funcsigs matplotlib mock numpy Pillow PyContracts pytest pytest-cov scipy)

# Modify login banner
echo "Debian ${release^^} (${working_release}) Docker Image" > ${wdir}/etc/motd

# Apt-get install packages
install_pkg_list ${install_base_pkgs} "Installing packages" ${base_pkgs[@]}

# Link to freetype2 header that for some reason Matplotlib cannot find when pip-installed
if [ ! -f /usr/include/ft2build.h ]; then
	ln -s /usr/include/freetype2/ft2build.h /usr/include/.
fi

if [ "${debug}" == 1 ]; then
	# Pip-install packages
	pip_install_pkg_list ${install_python_pkgs} "Pip-installing Python-related packages" ${python_pip_install_pkgs[@]}

	# Select Matplotli backend
	echo "backend : Agg" > /usr/local/lib/python2.7/dist-packages/matplotlib/mpl-data/matplotlibrc

	# Install test package and run tests (only for debugging)
	pip_install_pkg /root/putil-0.9.tar.gz
	cd /root
	py.test -s -vv 
fi

# Clean-up
rm -rf /var/lib/apt/lists/*
