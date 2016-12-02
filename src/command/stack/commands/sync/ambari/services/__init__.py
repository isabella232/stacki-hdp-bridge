import os
import sys
import rocks.commands
import rocks.ambari
import urllib2
import json

class Command(rocks.commands.Command):
	"""
	Synchronize services from the Database to Ambari
	<arg name="cluster" type="string">
	Name of Cluster
	</arg>
	"""
	def run(self, params, args):
		(self.cluster, ) = self.fillParams([
			('cluster', None),
			])

		self.ambari = rocks.ambari.AmbariClient(self.db)

		if not self.cluster:
			self.abort("Please specify cluster")


		db_services = self.ambari.getServicesFromDB()
		cl_services = self.ambari.getServicesFromAmbari(self.cluster)

		for s in db_services:
			if s in cl_services:
				continue
			if s not in cl_services:
				cmd = 'add.ambari.service'
				cmd_args = [
					'cluster=%s' % self.cluster,
					'service=%s' % s,
					]
				self.command(cmd, cmd_args)

		# Plugins to get extra components and client
		# components
		plugins = self.loadPlugins()
		req_plugins = []
		for plugin in plugins:
			if plugin.provides() in db_services:
				req_plugins.append(plugin)

		# Get the host <-> component mapping from
		# the database
		db_map = self.ambari.getComponentsFromDB()
		clients = []
		for plugin in req_plugins:
			# Check if a plugin has extra components
			# and update the host-component map
			# Also get the client components from
			# plugin
			try:
				plugin.extraComponents(db_map)
			except:
				pass
			try:
				c = plugin.clientComponents()
				clients.extend(c)
			except:
				pass

		# Update the host<->component mapping with
		# client components. Here we're adding every
		# client component to every host in the service
		for host in db_map:
			for client in clients:
				if client in db_map[host]:
					continue
				db_map[host].append(client)

		# Get components from Ambari
		cl_map = self.ambari.getComponentsFromAmbari(self.cluster)

		# Synchronise components between Ambari and
		# the Database
		for host in db_map:
			db_components = db_map[host]
			cl_components = cl_map[host]
			for comp in db_components:
				if comp not in cl_components:
					cmd = 'add.ambari.host.component'
					cmd_args = [
						host,
						'cluster=%s' % self.cluster,
						'component=%s' % comp
					]
					self.command(cmd, cmd_args)
