from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'HBASE'

	def requires(self):
		return ['HDFS']

	def set_appliances(self):
		self.zookeepers = []
		self.hbase_master = None
		for host in self.hostmap:
			for component in self.hostmap[host]:
				if component == 'ZOOKEEPER_SERVER':
					self.zookeepers.append(host)
				if component == 'HBASE_MASTER':
					self.hbase_master = host
				if component == 'NAMENODE':
					self.namenode = host

	def get_variables(self):
		self.set_appliances()
		p = self.get_largest_part(host=self.hbase_master)
		hdfs_name = self.owner.get_hdfs_name()
		v = {
			"hbase.zookeeper.quorum": ','.join(self.zookeepers),
			"hbase.rootdir": "%s/apps/hbase/data" % hdfs_name,
			"hbase.tmp.dir": "%s/hbase" % p,
		}
		f = lambda x: ("hbase-site.%s" % x[0], x[1])
		self.variables = dict(map(f, v.items()))
		return self.variables
