import os
import time
import rocks.commands
import rocks.ambari
import urllib2

class Command(rocks.commands.Command,
	rocks.commands.HostArgumentProcessor):
	"""
	Add hosts to the Ambari Cluster
	<arg name="hosts" type="string">
	Hosts to add to the Cluster
	</arg>
	<param name="cluster" type="string">
	Name of cluster
	</param>
	"""

	def run(self, params, args):
		# Get the Ambari Client object
		self.ambari = rocks.ambari.AmbariClient(self.db)
		hosts = self.ambari.getFQDNames(args)

		(cluster, ) = self.fillParams([
			('cluster', None),
		])

		if not cluster:
			self.abort('Cluster name required')

		for host in hosts:
			hr = "clusters/%s/hosts/%s" % (cluster, host)
			self.ambari.run(hr, command="POST")
		# check if the host actually got added
		done = False
		while not done:
			done = True
			for host in hosts:
				hr = "clusters/%s/hosts/%s" % (cluster, host)
				try:
					self.ambari.run(hr)
				except urllib2.HTTPError, e:
					done = False
					time.sleep(1)
