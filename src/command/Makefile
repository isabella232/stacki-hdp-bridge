# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@
#
#

ROLL.MEMBERSHIP = None
PKROOT = /opt/stack
ROLLROOT = ../../
DEPENDS.DIR = stack
PYFILES = $(shell find stack/commands -type f -name \*.py)
INITPYFILES = $(shell find stack/commands -type f -name __init__.py)
DEPENDS.FILES=$(PYFILES)

include $(STACKBUILD)/etc/CCRules.mk


build:
	for i in $(INITPYFILES); do \
		echo $$i | awk '{ print "\nRollName = \"$(ROLL)\"" >> $$1;}';\
	done;
	$(PYTHON) -mcompileall -q stack/commands

install::
	mkdir -p $(ROOT)/$(PY.STACK)/
	find stack -type f -name \*.pyc | cpio -pudv $(ROOT)/$(PY.STACK)/
ifeq ($(DEVEL), 1)
	find stack -type f -name \*.py | cpio -pudv $(ROOT)/$(PY.STACK)/
endif

clean::
	find stack -type f -name \*.pyc -exec rm -rf {} \;
