import rocks.commands
import rocks.ambari
import time
import re

class Command(rocks.commands.Command,
	rocks.commands.HostArgumentProcessor):
	"""
	Create an ambari cluster
	<arg name="cluster" type="string">
	Name of cluster
	</arg>
	<param name="version" type="string">
	HDP version of the Cluster
	</param>
	"""
	def run(self, params, args):
		# Get the Ambari Client object
		self.ambari = rocks.ambari.AmbariClient(self.db)
		if len(args) < 1:
			self.abort("Missing cluster name")
		self.cluster = args[0]

		if not self.validClusterName():
			self.abort('Cluster Name invalid')

		(self.hdp_version,) = self.fillParams([
			('version',self.db.getHostAttr(self.ambari.server,'hdp.version')),
		])

		if not self.hdp_version:
			self.abort("Please set hdp.verion global attribute")

		# Create the cluster
		body = {'Clusters':{
			'version':"HDP-%s" % \
			self.hdp_version
			}}
		self.ambari.run(
			"clusters/%s" % self.cluster,
			command="POST", params=body)

	def validClusterName(self):
		r = re.compile("^[a-zA-Z]+$")
		if r.match(self.cluster):
			return True
		return False
