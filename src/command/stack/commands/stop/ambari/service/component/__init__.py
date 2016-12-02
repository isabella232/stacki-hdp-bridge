import rocks.commands
import rocks.ambari
import json

class Command(rocks.commands.Command):
	"""
	Stop an ambari service component
	<param type="string" name="cluster">
	Cluster name
	</param>
	<param type="string" name="service">
	Service Name
	</param>
	<param type="string" name="component">
	</param>
	<example cmd='stop ambari service component cluster=dev service=YARN component=NODEMANAGER'>
	Stop all the NODEMANAGER components on cluster "dev"
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
		p = {
			"RequestInfo": {"context" :"Stopping %s" % component},
			"Body": {'ServiceComponentInfo':{'state':'INSTALLED'}}
			}
		print "Stopping %s" % component
		resource='clusters/%s/services/%s/components/%s' \
			% (cluster, service, component)
		self.ambari.run(resource, command='PUT', params=p)

