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

SCRIPTS = getname.py getvers.py
REPOFILES = $(RELEASE)/ambari.repo $(RELEASE)/hdp.repo 
DEPENDS.FILES = $(SCRIPTS) $(REPOFILES) repo-makefile

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	$(INSTALL) -m 0644 $(RELEASE)/*.repo $(ROOT)/$(PKGROOT)/
	$(INSTALL) -m 0755 getname.py $(ROOT)/$(PKGROOT)/getname
	$(INSTALL) -m 0755 getvers.py $(ROOT)/$(PKGROOT)/getvers
	$(INSTALL) -m 0644 repo-makefile $(ROOT)/$(PKGROOT)/Makefile

clean::
