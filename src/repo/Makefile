#
# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@
#

PKGROOT = /export/HDP
ROLLROOT = ../../

SCRIPTS = gethdp.py

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	$(INSTALL) -m 0755 gethdp.py $(ROOT)/$(PKGROOT)/gethdp

clean::
