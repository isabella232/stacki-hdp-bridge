import json
from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'STORM'

	def set_appliances(self):
		self.zookeepers = []
		for host in self.hostmap:
			for component in self.hostmap[host]:
				if component == 'ZOOKEEPER_SERVER':
					self.zookeepers.append(host)
				if component == 'NIMBUS':
					self.nimbus = host

	def get_variables(self):
		self.set_appliances()
		p = self.get_largest_part(host=self.nimbus)
		v = {
			"storm.zookeeper.servers": "%s" % json.dumps(self.zookeepers),
			"nimbus.host": "%s" % self.nimbus,
			"storm.local.dir": "%s/hadoop/storm" % p,
		}

		f = lambda x: ("storm-site.%s" % x[0], x[1])
		self.variables = dict(map(f, v.items()))
		return self.variables
