import os
import rocks.commands
import rocks.ambari
import urllib2

class Command(rocks.commands.Command):
	"""
	Add Service to the Ambari cluster
	<param type="string" name="cluster">
	Name of Cluster
	</param>
	<param type="string" name="service">
	Service to add to cluster
	</param>
	<example cmd="add ambari service cluster=dev service=HDFS">
	Add the HDFS service to cluster "dev"
	</example>
	"""

	def run(self, params, args):
		(cluster, service)= self.fillParams([
			('cluster',None),
			('service',None),
			])
		if not cluster:
			self.abort('Please specify cluster')
		if not service:
			self.abort('Please specify service')

		# Get the Ambari Client object
		hdp_version = self.db.getHostAttr('localhost', 'hdp.version')
		self.ambari = rocks.ambari.AmbariClient(self.db)

		resource = "stacks/HDP/versions/%s/services/%s/components" % \
			(hdp_version, service.upper())
		try:
			c = self.ambari.run(resource)
		except urllib2.HTTPError, e:
			code = e.getcode()
			info = e.info()
			if code == 404:
				self.abort('Cannot find service %s' % service)

		l = lambda x: x['StackServiceComponents']['component_name']
		components = map(l, c['items'])

		service_link = 'clusters/%s/services/%s' % (cluster, service.upper())
		self.ambari.run(service_link, command="POST")
		for component in components:
			comp_link = "%s/components/%s" % (service_link, component)
			self.ambari.run(comp_link, command="POST")
