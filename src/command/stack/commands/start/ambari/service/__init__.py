import rocks.commands
import rocks.ambari
import urllib2

class Command(rocks.commands.Command):
	"""
	Start HDP service
	<param name="cluster" type="string">
	Cluster name
	</param>
	<param name="service" type="string">
	Service Name
	</param>
	<example cmd='start ambari service cluster=dev service=HDFS'>
	Start HDFS on cluster "dev"
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
		print "Starting %s" % service
		p = {
			"RequestInfo": {"context" :"Starting %s" % service},
			"Body": {"ServiceInfo":{"state":"STARTED"}}
		}
		self.ambari.run(url, command="PUT", params=p)

