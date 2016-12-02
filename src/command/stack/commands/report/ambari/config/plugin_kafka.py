from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'KAFKA'

	def requires(self):
		return []

	def set_appliances(self):
		self.kafka_broker = None
		self.zk = []
		for host in self.hostmap:
			for component in self.hostmap[host]:
				if component == 'KAFKA_BROKER':
					self.kafka_broker = host
				if component == 'ZOOKEEPER_SERVER':
					self.zk.append(host)

	def get_variables(self):
		self.set_appliances()

		v = {}

		# Set Zookeepers
		f = lambda x: "%s:2181" % x
		z = map(f, self.zk)
		zk = ','.join(z)
		v["zookeeper.connect"] = zk

		# Set Log directories
		l = self.get_largest_part(host = self.kafka_broker)
		v['log.dirs'] = "%s/kafka-logs" % l

		f = lambda x: ("kafka-broker.%s" % x[0], x[1])
		variables = dict(map(f, v.items()))
		return variables
