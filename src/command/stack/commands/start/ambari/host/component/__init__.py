import rocks.commands
import rocks.ambari
import json

class Command(rocks.commands.Command):
	"""
	Start a specific service component
	on a cluster host.
	<arg type="string" name="hosts">
	Hostnames
	</arg>
	<param type="string" name="cluster">
	Name of Cluster
	</param>
	<param type="string" name="component">
	Service component to start
	</param>
	<example cmd='start ambari host component compute-0-2 component=NODEMANAGER cluster=dev'>
	Start Nodemananger service associated with cluster "dev" on compute-0-2 
	</example>
	"""
	def run(self, params, args):
		(component, cluster) = self.fillParams([
			('component', None),
			('cluster', None),
		])
		if not cluster:
			self.abort('Please specify cluster')
	
		if not component:
			self.abort('Please specify component')
		self.ambari = rocks.ambari.AmbariClient(self.db)
		hosts = self.ambari.getFQDNames(args)
		if not hosts:
			self.abort('Please specify atleast one host')
		component = component.upper()
		for host in hosts:
			p = {
			"RequestInfo": {"context" :"Starting %s on %s" % \
					(component, host)},
				"Body": {'HostRoles':
					{'state':'STARTED'}}
			}
			print "Starting %s on %s" % (component, host)
			resource='clusters/%s/hosts/%s/host_components/%s' \
				% (cluster, host, component)
			self.ambari.run(resource, command='PUT', params=p)
