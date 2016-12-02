import rocks.commands
import rocks.ambari
import json

class Command(rocks.commands.Command):
	"""
	Stop a host component.
	<arg name="hosts" type="string">
	Hostnames
	</arg>
	<param name="component" type="string">
	Component name
	</param>
	<param name="cluster" type="string">
	Name of cluster
	</param>
	<example cmd='stop ambari host component compute-0-4 component=JOURNALNODE cluster=dev'>
	Stop JOURNALNODE on compute-0-4
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
		component=component.upper()
		for host in hosts:
			p = {
			"RequestInfo": {"context" :"Installing/Stopping %s on %s" % \
					(component, host)},
				"Body": {'HostRoles':
					{'state':'INSTALLED'}}
			}
			resource='clusters/%s/hosts/%s/host_components/%s' \
				% (cluster, host, component)
			print "Installing/Stopping %s on %s" % (component, host)
			self.ambari.run(resource, command='PUT', params=p)
