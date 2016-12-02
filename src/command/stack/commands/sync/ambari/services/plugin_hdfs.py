#
# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@
#

import rocks.commands

class Plugin(rocks.commands.Plugin):
	def provides(self):
		return 'HDFS'

	def extraComponents(self, hostmap):
		## This function is necessary
		## Only if we're running HDFS
		## Namenode in HA mode
		namenodes = []
		for host in hostmap:
			if 'NAMENODE' in hostmap[host]:
				namenodes.append(host)
		if len(namenodes) > 1:
			for host in namenodes:
				hostmap[host].append('ZKFC')

	def clientComponents(self):
		return ['HDFS_CLIENT']
