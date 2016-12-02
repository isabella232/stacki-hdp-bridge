# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@

ROLL.MEMBERSHIP = None
PKGROOT = /opt/stack/share/HDP
ROLLROOT = ../../
DEPENDS.DIR = templates
DEPENDS.FILES = $(wildcard $(DEPENDS.DIR)/*/*)

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	find templates -type f | cpio -pudv $(ROOT)/$(PKGROOT)
