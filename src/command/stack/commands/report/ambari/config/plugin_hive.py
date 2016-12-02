from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'HIVE'

	def set_appliances(self):
		self.mysql_server = None
		self.hive_server = None
		self.hive_metastore = None
		self.webhcat_server = None
		self.zookeepers = []

		for host in self.hostmap:
			for component in self.hostmap[host]:
				if component == 'ZOOKEEPER_SERVER':
					self.zookeepers.append(host)
				if component == 'HIVE_SERVER':
					self.hive_server = host
				if component == 'HIVE_METASTORE':
					self.hive_metastore = host
				if component == 'MYSQL_SERVER':
					self.mysql_server = host
				if component == 'WEBHCAT_SERVER':
					self.webhcat_server = host

		if self.hive_metastore == None:
			self.hive_metastore = self.hive_server
		if self.mysql_server == None:
			self.mysql_server = self.hive_server
		if self.webhcat_server == None:
			self.mysql_server = self.hive_server

	def get_variables(self):
		self.set_appliances()
		v = {
			"hive.metastore.uris": "thrift://%s:9083" % self.hive_metastore, 
			"javax.jdo.option.ConnectionURL": "jdbc:mysql://%s/hive?createDatabaseIfNotExist=true" % self.mysql_server,
		}
		# Zookeepers
		f = lambda x: "%s:2181" % x
		z = map(f, self.zookeepers)
		zookeeper_hosts = ','.join(z)
		v["hive.zookeeper.quorum"] = zookeeper_hosts
		v["hive.cluster.delegation.token.store.zookeeper.connectString"] = zookeeper_hosts

		f = lambda x: ("hive-site.%s" % x[0], x[1])
		self.variables = dict(map(f, v.items()))

		# Hive Env Variables
		self.variables['hive-env.hive_hostname'] = self.hive_server

		# WebHcat Variables
		self.variables['webhcat-site.templeton.zookeeper.hosts'] = zookeeper_hosts
		self.variables['webhcat-site.templeton.hive.properties'] = "hive.metastore.local=false,hive.metastore.uris=thrift://%s:9083,hive.metastore.sasl.enabled=false,hive.metastore.execute.setugi=true" % self.hive_metastore
		return self.variables

