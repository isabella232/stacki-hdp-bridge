import os
import sys
import rocks.commands
import rocks.ambari
import urllib2
import json
import copy

class Command(rocks.commands.Command,
	rocks.commands.HostArgumentProcessor):
	"""
	Synchronize configuration from the
	StackIQ database and template files
	to Ambari
	<param name="cluster" type="string">
	Name of Cluster
	</param>
	"""
	def run(self, params, args):
		(self.cluster, ) = self.fillParams([
			('cluster', self.db.getHostAttr('localhost','hdp.cluster')),
			])

		if self.cluster == None:
			self.abort('Please specify cluster')

	
		op = self.call('report.ambari.config',
			['cluster=%s' % self.cluster])
		j = json.loads(op[0]['content'])
		for scope in j:
			self.call('add.ambari.config',
				['config=%s' % scope,
				'cluster=%s' % self.cluster,
				'body=%s' % json.dumps(j[scope])])
