#!/bin/bash
# functions.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

print_banner () {
	local slength=${#1}
	local line="+-"
	local i=1
	while ((i<=${slength})); do
		line=${line}'-'
		let i++
	done
	line=${line}'-+'
	local cyan="\e[1;36m"
	local bold="\033[1m"
	local reset="\033[0m"
	echo -e "${cyan}${bold}${line}${reset}"
	echo -e "${cyan}${bold}| $1 |${reset}"
	echo -e "${cyan}${bold}${line}${reset}"
}

# Mostly From https://stackoverflow.com/questions/12199631/convert-seconds-to-hours-minutes-seconds-in-bash
show_time () {
	num=$1
	local sec=0
	local min=0
	local hour=0
	local day=0
	if ((num>59)); then
		((sec=num%60))
		((num=num/60))
		if ((num>59)); then
			((min=num%60))
			((num=num/60))
			if ((num>23)); then
				((hour=num%24))
				((day=num/24))
			else
				((hour=num))
			fi
		else
			((min=num))
		fi
	else
		((sec=num))
	fi
	local ret="Ellapsed time: "
	if [ "${day}" != 0 ]; then
		ret="${ret} ${day}d"
		if [ "${hour}" != 0 ] || [ "${min}" != 0 ] || [ "${sec}" != 0 ]; then
			ret="${ret}, "
		fi
	fi
	if [ "${hour}" != 0 ]; then
		ret="${ret} ${hour}h"
		if [ "${min}" != 0 ] || [ "${sec}" != 0 ]; then
			ret="${ret}, "
		fi
	fi
	if [ "${min}" != 0 ]; then
		ret="${ret} ${min}m"
		if [ "${sec}" != 0 ]; then
			ret="${ret}, "
		fi
	fi
	if [ "${sec}" != 0 ]; then
		ret="${ret} ${sec}s"
	fi
	echo -e "\n${ret}\n"
}
