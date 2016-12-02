import os
import time
import rocks.commands
import rocks.ambari
import urllib2

class Command(rocks.commands.Command,
	rocks.commands.HostArgumentProcessor):
	"""
	Add component to host
	<arg type="string" name="host">
	Hostname
	</arg>
	<param type="string" name="cluster">
	Name of Ambari cluster
	</param>
	<param type="string" name="component">
	Component to add to host
	</param>
	<example cmd='add host component compute-0-1
	cluster=dev component=JOURNALNODE'>
	Add a JOURNALNODE service to compute-0-1 attached to
	cluster "dev"
	</example>
	"""

	def run(self, params, args):
		# Get the Ambari Client object
		self.ambari = rocks.ambari.AmbariClient(self.db)
		hosts = self.ambari.getFQDNames(args)
		(component, cluster) = self.fillParams([
			('component', None),
			('cluster', None)
			])

		if not component:
			self.abort('Please specify component')

		for host in hosts:
			hr = "clusters/%s/hosts/%s/host_components/%s" % \
				(cluster, host, component.upper())
			print "Adding Host Component %s on %s" \
				% (component.upper(), host)
			self.ambari.run(hr, command='POST')
