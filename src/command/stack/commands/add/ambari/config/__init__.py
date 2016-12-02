import os
import json
import rocks.commands
import rocks.ambari
import urllib2
import time

class Command(rocks.commands.Command):
	"""
	Add Ambari Configuration.
	CAUTION:
	THIS COMMAND IS NOT MEANT TO BE RUN BY A SYSADMIN.
	THIS IS AN INTERNAL COMMAND.
	<param name="cluster" type="string">
	Cluster Name
	</param>
	<param name="config" type="string">
	Configuration file name to change
	</param>
	<param name="body" type="json">
	Configuration params as JSON.
	</param>
	"""
	def run(self, params, args):
		self.ambari = rocks.ambari.AmbariClient(self.db)
		(config, cluster, body, ) = self.fillParams([
			('config', None),
			('cluster', None),
			('body', None),
			])
		if not config:
			self.abort('Please specify config file')
		if not cluster:
			self.abort('Please specify cluster name')
		if not body:
			self.abort('Please specify properties in body')

		try:
			b = json.loads(body)
		except:
			self.abort("body is malformed")

		version = int(time.time())
		p = {
			"Clusters":{
				"desired_configs":{
					"type": config,
					"tag":"version%d" % version,
					"user":"admin",
					"properties":b
				}
			}
		}
		resource = 'clusters/%s' % cluster
		self.ambari.run(resource, command='PUT', params = p)
