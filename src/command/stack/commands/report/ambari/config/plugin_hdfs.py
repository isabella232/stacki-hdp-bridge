from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'HDFS'

	def set_appliances(self):
		self.datanodes = []
		self.namenodes = []
		self.zookeepers = []
		self.journalnodes = []
		self.hcatserver = None
		self.hiveserver = None
		self.oozieserver = None
		for host in self.hostmap:
			for c in self.hostmap[host]:
				if c == 'NAMENODE':
					self.namenodes.append(host)
				if c == 'SECONDARY_NAMENODE':
					self.sec_namenode = host
				if c == 'DATANODE':
					self.datanodes.append(host)
				if c == 'ZOOKEEPER_SERVER':
					self.zookeepers.append(host)
				if c == 'JOURNALNODE':
					self.journalnodes.append(host)
				if c == 'WEBHCAT_SERVER':
					self.hcatserver = host
				if c == 'HIVE_SERVER':
					self.hiveserver = host
				if c == 'OOZIE_SERVER':
					self.oozieserver = host


		# Get the primary namenode.
		self.nn_primary = self.namenodes[0]
		if len(self.namenodes) == 1:
			self.ha = False
		else:
			# If more than one namenode is specified,
			# then HA is required. By default, the first
			# is the active namenode, and second one is
			# the standby namenode, unless hdp.hdfs.namenode.active
			# attribute is specified
			self.ha = True
			active_nn = self.owner.db.getHostAttr('localhost',
					'hdp.hdfs.namenode.active')
			self.nn_standby = self.namenodes[1]
			if active_nn:
				try:
					active_nn = self.ambari.getFQDNames([active_nn])[0]
					if active_nn not in self.namenodes:
						print "%s is not a Namenode.\n" % active_nn,\
						"Using %s as namenode" % self.nn_primary
					self.nn_primary = self.namenodes.pop(
						self.namenodes.index(active_nn))
					self.nn_standby = self.namenodes[0]
				except:
					pass

	def get_variables(self):
		self.set_appliances()
		# Get Partitioning information for the primary namenode
		namenode_part = self.get_largest_part(host=self.nn_primary)
		# If we're not doing HA, get partition for secondary namenode
		if not self.ha:
			sec_namenode_part = self.get_largest_part(
				host=self.sec_namenode)

		# Get lowest common denominator of
		# partitions for all the datanodes.

		# First get the parts for the first datanode
		parts = set(self.get_parts(host=self.datanodes[0]))

		if len(self.datanodes) > 1:
			# For every subsequent datanode, get the parts
			# and only take the intersection
			for host in self.datanodes[1:]:
				host_parts = set(self.get_parts(host=host))
				parts = parts.intersection(host_parts)

		f = lambda x: "%s/hdfs/data" % x
		p = list(parts)
		p.sort()
		datanode_dir_list = map(f, p)
		# Finally convert the list of
		# partitions to a string
		p_string = ','.join(datanode_dir_list)

		# Attribute Assignment
		v = {
			"dfs.namenode.https-address": "%s:50470" % self.nn_primary,
			"dfs.datanode.data.dir": p_string, 
			"dfs.namenode.http-address": "%s:50070" % self.nn_primary,
			"dfs.namenode.name.dir": "%s/hdfs/namenode" % namenode_part,
			"dfs.namenode.checkpoint.dir": "%s/hdfs/checkpoint" % namenode_part
		}
		if not self.ha:
			v.update({
			"dfs.namenode.checkpoint.dir": "%s/hdfs/checkpoint" % sec_namenode_part,
			"dfs.namenode.secondary.http-address": "%s:50090" % self.sec_namenode, 
			})
		else:
			# HA Attributes
			ha_conf = {
			"dfs.ha.automatic-failover.enabled": "true",
			"dfs.ha.fencing.methods": "shell(/bin/true)",
			"dfs.nameservices": "%s" % self.cluster,
			"dfs.client.failover.proxy.provider.%s" % self.cluster: \
				"org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider"
			}

			# HDP Supports Active/Standby HA only. It also allows
			# for only one standby namenode

			# HA Namenode attributes
			idx = "dfs.namenode.http-address.%s.nn0" % self.cluster
			ha_conf[idx] = "%s:50070" % self.nn_primary
			idx = "dfs.namenode.rpc-address.%s.nn0" % self.cluster
			ha_conf[idx] = "%s:8020" % self.nn_primary

			idx = "dfs.namenode.http-address.%s.nn1" % self.cluster
			ha_conf[idx] = "%s:50070" % self.nn_standby
			idx = "dfs.namenode.rpc-address.%s.nn1" % self.cluster
			ha_conf[idx] = "%s:8020" % self.nn_standby

			ha_conf["dfs.ha.namenodes.%s" % self.cluster] = "nn0,nn1"

			# Journal Nodes
			f = lambda x: "%s:8485" % x
			j = map(f, self.journalnodes)
			j_list = ";".join(j)
			ha_conf["dfs.namenode.shared.edits.dir"] = "qjournal://%s/%s" % (j_list, self.cluster)
			v.update(ha_conf)


		f = lambda x: ("hdfs-site.%s" % x[0], x[1])
		self.variables = dict(map(f, v.items()))
		# Core-site attributes
		core_var = {}
		if self.ha:
			hdfs_name = "hdfs://%s" % self.cluster
			# Zookeepers
			f = lambda x: "%s:2181" % x
			z = map(f, self.zookeepers)
			core_var["ha.zookeeper.quorum"] =  ','.join(z)
		else:
			hdfs_name = "hdfs://%s:8020" % self.nn_primary
		core_var["fs.defaultFS"] = hdfs_name
		
		if self.hcatserver:
			core_var['hadoop.proxyuser.hcat.hosts'] = self.hcatserver
		if self.hiveserver:
			core_var['hadoop.proxyuser.hive.hosts'] = self.hiveserver
		if self.oozieserver:
			core_var['hadoop.proxyuser.oozie.hosts'] = self.oozieserver

		# Set hdfs_name for other plugins to use
		self.owner.set_hdfs_name(hdfs_name)

		f = lambda x: ("core-site.%s" % x[0], x[1])
		self.variables.update(dict(map(f, core_var.items())))
		return self.variables
