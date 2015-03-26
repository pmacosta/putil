#!/bin/bash
# build-container.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

# Exit upon error
set -e

# Find directory where script is (from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in)
source="${BASH_SOURCE[0]}"
while [ -h "$source" ]; do # resolve $source until the file is no longer a symlink
	dir="$( cd -P "$( dirname "$source" )" && pwd )"
	source="$(readlink "$source")"
	[[ $source != /* ]] && source="$dir/$source" # if $source was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
dir="$( cd -P "$( dirname "$source" )" && pwd )"
package_root=$(dirname ${dir})
package_name=$(basename ${package_root})

exit_if_not_root () {
	if [ ${EUID} -ne 0 ]; then
		echo "build-container.sh: root privileges needed"
		return 1
	fi
}

print_usage_message () {
	echo -e "build-container.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  build-container.sh [-h] [stable|testing] [docker-user-name]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
}

get_debian_distro_name () {
	local name=$(curl $1 2> /dev/null | grep "<title>Debian" | sed -r -e 's/.*&ldquo;(.*)&rdquo;.*/\1/g')
	# Sub-shell spawned, if an error occurs the sub-shell is exited so have to check result is valid
	local word_count=$(echo ${name} | wc -w)
	if [ ${word_count} -gt 1 ]; then
		return 1
	fi
	echo ${name}
}

get_all_distro_names () {
	# global stable_distro_name, testing_distro_name
	echo 'Obtaining names of stable, testing and current distributions'
	stable_distro_name=$(get_debian_distro_name https://www.debian.org/releases/stable/)
	echo -e "\tstable: ${stable_distro_name}"
	testing_distro_name=$(get_debian_distro_name https://www.debian.org/releases/testing/)
	echo -e "\ttesting: ${testing_distro_name}"
}

print_banner () {
	echo -e "Bulding Docker image for Debian ${release^^} (${working_release})"
	echo -e "\tWorking directory: ${wdir}"
	echo -e "\tImage name: ${docker_hub_user}/${working_release}"
}

process_command_line_argument () {
	# global release, wdir, current_release, docker_hub_user
	while getopts ":h" opt; do
		case $opt in
			h)
				print_usage_message
				exit 0
				;;
			\?)
				echo "build-container.sh: invalid option" >&2
				print_usage_message
				;;
		esac
	done
	shift $(($OPTIND - 1))
	if [ "$#" != 2 ]; then
		echo "build-container.sh: invalid number of arguments"
		exit 1
	fi
	release=${1:-"testing"}
	release=${release,,}
	if [ "${release}" != "stable" -a "${release}" != "testing" ]; then
		echo "build-container.sh: invalid argument ${release}" >&2
		print_usage_message
		exit 1
	fi
	working_release=${testing_distro_name}
	if [ "${release}" == "stable" ]; then
		working_release=${stable_distro_name}
	fi
	wdir=${HOME}/vdisks/chroot/${working_release}
	docker_hub_user=$2
}

get_system () {
	echo -e "Installing base distribution"
	rm -rf ${wdir}
	mkdir -p ${wdir}
	debootstrap --variant=minbase ${working_release} ${wdir} http://ftp.us.debian.org/debian
}

configure_system () {
	cp ${package_root}/sbin/.build-container-chroot.sh ${wdir}/root/.
	cp ${package_root}/dist/* ${wdir}/root/.
	cp -r ${package_root}/tests ${wdir}/root/.
	chroot ${wdir} /root/.build-container-chroot.sh $1 $2
}

create_image () {
	echo -e "Creating Docker image tar ball"
	local cwd=${PWD}
	cd ${HOME}/vdisks/chroot/
	#if docker images | grep ${working_release}; then
	#	image_id=$(docker images | grep ${working_release} | sed -r "s/.*${working_release}\s+\w+\s+(\w+)\s+.*/\1/g")
	#	echo "Removing existing image ${image_id}"
	#	docker rmi -f ${image_id}
	#fi
	tar -C ${working_release} -c . | docker import - ${working_release}
	docker tag jessie:latest ${docker_hub_user}/${working_release}:latest
	cd ${cwd}
	docker images
	docker run ${working_release} echo /etc/motd
}

###
# Processing
###
exit_if_not_root
get_all_distro_names
process_command_line_argument $@
print_banner
get_system
configure_system ${release} ${working_release}
create_image
