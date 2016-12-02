from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'ZOOKEEPER'

	def get_variables(self):
		h = None
		for host in self.hostmap:
			for c in self.hostmap[host]:
				if c == 'ZOOKEEPER_SERVER':
					h == host
					break

		p = self.get_largest_part(host=h)
		v = {
			"zoo__cfg.dataDir": "%s/zookeeper" % p,
		}
		return v
