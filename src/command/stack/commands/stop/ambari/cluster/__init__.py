import rocks.commands
import rocks.ambari
import urllib2

class Command(rocks.commands.Command):
	"""
	Stop all HDP services on specied cluster
	<arg name="cluster" type="string">
	Cluster name
	</arg>
	"""

	def run(self, params, args):
		if len(args) != 1:
			self.abort('Please specify Cluster')
		cluster = args[0]
		self.ambari = rocks.ambari.AmbariClient(self.db)
		p = {
			"RequestInfo": {"context" :"Stopping Cluster Services"},
			"Body":{"ServiceInfo":{"state":"INSTALLED"}}
		}
		self.ambari.run('clusters/%s/services' % cluster,
			command="PUT", params=p)
