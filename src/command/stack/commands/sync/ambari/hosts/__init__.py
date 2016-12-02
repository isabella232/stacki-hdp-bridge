import os
import rocks.commands
import rocks.ambari
import urllib2
import json

class Command(rocks.commands.Command,
	rocks.commands.HostArgumentProcessor):
	"""
	Synchronize Hosts from the Database to Ambari
	<arg name="cluster" type="string">
	Name of Cluster
	</arg>
	"""
	def run(self, params, args):
		(cluster, ) = self.fillParams([
			('cluster', None),
			])

		self.ambari = rocks.ambari.AmbariClient(self.db)

		if not cluster:
			self.abort("Please specify cluster")

		db_hosts = self.ambari.getHostsFromDB()

		ambari_hosts = self.ambari.getHostsFromAmbari()
		a_cl_hosts =  self.ambari.getHostsFromAmbariCluster(cluster)

		extra_db_hosts = list(set(db_hosts).difference(set(ambari_hosts)))
		if len(extra_db_hosts):
			self.command('add.ambari.host', extra_db_hosts)

		extra_cl_hosts = list(set(db_hosts).difference(set(a_cl_hosts)))
		if len(extra_cl_hosts):
			cmd_args = ['cluster=%s' % cluster]
			cmd_args.extend(extra_cl_hosts)
			self.command('add.ambari.cluster.host', cmd_args)
