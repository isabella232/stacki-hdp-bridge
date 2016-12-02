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

class plugin(rocks.commands.Plugin):
	def init(self, hostmap):
		self.hostmap = hostmap
		self.hdfs_name = None
		self.cluster = self.owner.cluster
		self.ambari = self.owner.ambari

	def provides(self):
		return None

	def requires(self):
		return []

	def client_attr(self):
		return []

	def get_variables(self):
		return {}

	def getHostVariables(self):
		return {}

	def get_largest_part(self, host=None):
		if host == None:
			return '/state/partition1/hadoop'

		p = self.ambari.getLargestPartition(host)
		if p == None:
			return "/state/partition1/hadoop"
		return p

	def get_parts(self, host=None):
		if not host:
			return ['/state/partition1/hadoop']
		p = self.ambari.getPartitions(hostname=host, partition="hadoop")
		if len(p) > 0:
			return p

		p = self.ambari.getPartitions(hostname=host, partition="state")
		if len(p) > 0:
			p = map(lambda x: "%s/hadoop" % x, p)
			return p

		return ['/state/partition1/hadoop']
