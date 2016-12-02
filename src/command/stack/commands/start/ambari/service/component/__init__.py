import rocks.commands
import rocks.ambari
import json

class Command(rocks.commands.Command):
	"""
	Start Service component on a cluster
	<param type="string" name="cluster">
	Name of Cluster
	</param>
	<param type="string" name="component">
	Name of component
	</param>
	<param type="string" name="service">
	Name of service
	</param>
	<example cmd='start service component service=HDFS component=DATANODE cluster=dev'>
	Starts Datanodes on cluster "dev"
	</example>
	"""
	def run(self, params, args):
		(service, component, cluster) = self.fillParams([
			('service', None),
			('component', None),
			('cluster', None),
		])

		if not cluster:
			self.abort('Please specify cluster')
	
		if not service:
			self.abort('Please specify Service')

		if not component:
			self.abort('Please specify component')

		self.ambari = rocks.ambari.AmbariClient(self.db)
		hdp_version = self.db.getHostAttr('localhost','hdp.version')
		url = 'stacks/HDP/versions/%s/services/%s' % (hdp_version, service.upper())
		try:
			self.ambari.run(url)
		except:
			self.abort('Cannot find service %s' % service)

		component=component.upper()
		service=service.upper()
		url = 'stacks/HDP/versions/%s/services/%s/components/%s' \
			% (hdp_version, service, component)

		try:
			self.ambari.run(url)
		except:
			self.abort('Cannot find component %s for service %s' \
			% (component, service))
		p = {
			"RequestInfo": {"context" :"Starting %s" % component},
			"Body": {'ServiceComponentInfo':{'state':'STARTED'}}
			}
		print "Starting %s" % component
		resource='clusters/%s/services/%s/components/%s' \
			% (cluster, service, component)
		self.ambari.run(resource, command='PUT', params=p)

