#
# @SI_Copyright@
# @SI_Copyright@
#

import os
import sys
import rocks.commands
import rocks.ambari
import urllib2
import json
import copy

class Command(rocks.commands.Command,
	rocks.commands.HostArgumentProcessor):
	"""
	Report Host-specific Ambari configuration.
	<arg type="string" name="host">
	Hostname
	</arg>
	<param type="string" name="cluster">
	Cluster Name
	</param>
	"""
	def run(self, params, args):

		(cluster,) = self.fillParams([
				('cluster',None),
				])

		if cluster == None:
			self.abort('Cluster Name not specified')

		if len(args) != 1:
			self.abort('Please specify one hostname only.')

		host = self.getHostnames(args)[0]
		self.ambari = rocks.ambari.AmbariClient(self.db)
		service_list = self.ambari.getServicesFromDB()
	
		hdp_attrs = self.db.getHostAttrs(host, filter='hdp.', showsource=True)

		hdp_host_attrs = {}
		for attr in hdp_attrs:
			a = attr.split('.')[1:]
			# Ignore the hdp.* attributes
			if len(a) < 2:
				continue

			if a[1] != 'conf':
				continue

			service = a[0].upper()
			if service not in service_list:
				continue

			val = hdp_attrs[attr][0]
			source = hdp_attrs[attr][1]
			if source != 'H':
				continue

			hdp_host_attrs['.'.join(a)] = val

		self.beginOutput()
		for a in hdp_host_attrs:
			self.addOutput(host, [a, hdp_host_attrs[a]])
		self.endOutput(header=['host', 'attr','value'])
