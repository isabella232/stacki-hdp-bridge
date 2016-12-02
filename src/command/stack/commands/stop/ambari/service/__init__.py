import rocks.commands
import rocks.ambari
import urllib2

class Command(rocks.commands.Command):
	"""
	Stop an ambari service
	<param type="string" name="cluster">
	Cluster name
	</param>
	<param type="string" name="service">
	Service Name
	</param>
	<example cmd='stop ambari service cluster=dev service=YARN'>
	Stop the YARN service on cluster "dev"
	</example>
	"""

	def run(self, params, args):
		(cluster, service) = self.fillParams([
			('cluster',None),
			('service',None),
		])
		if service == None:
			self.abort('Please specify service')
		if cluster == None:
			self.abort('Please specify Cluster')
		self.ambari = rocks.ambari.AmbariClient(self.db)

		service = service.upper()
		url = 'clusters/%s/services/%s' % (cluster, service)
		p = {"RequestInfo": {"context" :"Stopping %s" % service},
			"Body":{"ServiceInfo":{"state":"INSTALLED"}}}
		print "Stopping %s" % service
		self.ambari.run(url, command="PUT", params=p)

