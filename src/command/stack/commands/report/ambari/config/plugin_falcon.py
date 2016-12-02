from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'FALCON'

	def requires(self):
		return ['OOZIE', 'HDFS']

	def set_appliances(self):
		self.falcon_server = None
		for host in self.hostmap:
			for component in self.hostmap[host]:
				if component == 'FALCON_SERVER':
					self.falcon_server = host

	def get_variables(self):
		self.set_appliances()
		p = self.get_largest_part(host=self.falcon_server)
  		v = {
		"*.broker.url" : "tcp://%s:61616" % self.falcon_server,
		"*.falcon.graph.serialize.path": "%s/hadoop/falcon/data/lineage" % p,
		"*.falcon.graph.storage.directory": "%s/hadoop/falcon/data/lineage/graphdb" % p
		}

		f = lambda x: ("falcon-startup__properties.%s" % x[0], x[1])
		self.variables = dict(map(f, v.items()))
		return self.variables
