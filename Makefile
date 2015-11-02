# Makefile
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

PKG_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

asort:
	@echo "Sorting Aspell whitelist"
	@sort $(PKG_DIR)/data/aspell-whitelist > $(PKG_DIR)/data/aspell-whitelist.tmp
	@mv -f $(PKG_DIR)/data/aspell-whitelist.tmp $(PKG_DIR)/data/aspell-whitelist

bdist:
	@cd $(PKG_DIR)/sbin; ./gen_pkg_manifest.py
	@cd $(PKG_DIR); python setup.py bdist

check: FORCE
	@$(PKG_DIR)/sbin/check_files_compliance.py -tsp

clean: FORCE
	@find $(PKG_DIR) -name '*.pyc' -exec rm -rf {} \;
	@find $(PKG_DIR) -name '__pycache__' -exec rm -rf {} \;
	@find $(PKG_DIR) -name '.coverage*' -exec rm -rf {} \;
	@find $(PKG_DIR) -name '*.tmp' -exec rm -rf {} \;
	@find $(PKG_DIR) -name '*.pkl' -exec rm -rf {} \;
	@rm -rf $(PKG_DIR)/build $(PKG_DIR)/dist $(PKG_DIR)/putil.egg-info
	@rm -rf $(PKG_DIR)/docs/_build

docs: FORCE
	@$(PKG_DIR)/sbin/build-docs.sh $(ARGS)

default:
	@echo "No default action"

FORCE:

lint:
	@echo "Running Pylint on package files"
	@pylint --rcfile=$(PKG_DIR)/.pylintrc -f colorized -r no $(PKG_DIR)/putil
	@pylint --rcfile=$(PKG_DIR)/.pylintrc -f colorized -r no $(PKG_DIR)/sbin
	@pylint --rcfile=$(PKG_DIR)/.pylintrc -f colorized -r no $(PKG_DIR)/tests
	@pylint --rcfile=$(PKG_DIR)/.pylintrc -f colorized -r no $(PKG_DIR)/docs/support

sdist:
	@cd $(PKG_DIR)/sbin; ./gen_pkg_manifest.py
	@cd $(PKG_DIR); python setup.py sdist --formats=gztar,zip

sterile: clean
	@rm -rf $(PKG_DIR)/.tox

test: FORCE
	@$(PKG_DIR)/sbin/rtest.sh $(ARGS)

upload: clean sdist wheel
	@twine upload $(PKG_DIR)/dist/*

wheel:
	@cp $(PKG_DIR)/MANIFEST.in $(PKG_DIR)/MANIFEST.in.tmp
	@cd $(PKG_DIR)/sbin; ./gen_pkg_manifest.py wheel
	@cp -f $(PKG_DIR)/setup.py $(PKG_DIR)/setup.py.tmp
	@sed -r -i 's/data_files=DATA_FILES,/data_files=None,/g' $(PKG_DIR)/setup.py
	@cd $(PKG_DIR); python setup.py bdist_wheel
	@mv -f $(PKG_DIR)/setup.py.tmp $(PKG_DIR)/setup.py
	@rm -rf $(PKG_DIR)/MANIFEST.in.tmp
