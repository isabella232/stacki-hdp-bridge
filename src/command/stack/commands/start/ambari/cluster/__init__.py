import rocks.commands
import rocks.ambari
import urllib2

class Command(rocks.commands.Command):
	"""
	Starts an Ambari Cluster.
	<arg type="string" name="cluster">
	Name of cluster
	</arg>
	"""

	def run(self, params, args):
		if len(args) != 1:
			self.abort('Please specify Cluster')
		cluster = args[0]
		self.ambari = rocks.ambari.AmbariClient(self.db)
		p = {
			"RequestInfo": {"context" :"Starting Cluster Services"},
			"Body": {"ServiceInfo":{"state":"STARTED"}}
		}
		self.ambari.run('clusters/%s/services?ServiceInfo/state=INSTALLED' \
			% cluster, command="PUT", params=p)

