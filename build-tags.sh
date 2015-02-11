#!/bin/bash
export PACKAGE_ROOT="$HOME/python/putil/"
ctags -V --tag-relative -f $PACKAGE_ROOT/tags -R $PACKAGE_ROOT/putil/*.py $PACKAGE_ROOT/tests/*.py
# */2 * * * * /proj/ad9625_e_expctl/sos_pacosta/pacosta/sim/bin/build_tags.sh &>/home/pacosta/log/cheetah_tags.log

