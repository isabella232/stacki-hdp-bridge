#@SI_Copyright@
#@SI_Copyright@

RPM.STRATEGY = copy
ROLLROOT = ../../
include $(STACKBUILD)/etc/CCRules.mk

rpm::	build
	cp jdk-8u111-linux-x64.rpm $(REDHAT.RPMS)/$(ARCH)

build::
	mkdir -p $(REDHAT.RPMS)/$(ARCH)
