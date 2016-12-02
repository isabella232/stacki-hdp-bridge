from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'YARN'

	def set_appliances(self):
		self.resource_mgr = None
		self.hist_server = None
		self.app_tl_server = None
		self.nm = []
		self.zk = []
		for host in self.hostmap:
			for component in self.hostmap[host]:
				if component == 'RESOURCEMANAGER':
					self.resource_mgr = host
				if component == 'HISTORYSERVER':
					self.hist_server = host
				if component == 'APP_TIMELINE_SERVER':
					self.app_tl_server = host
				if component == 'NODEMANAGER':
					self.nm.append(host)
				if component == 'ZOOKEEPER_SERVER':
					self.zk.append(host)

	def get_variables(self):
		self.set_appliances()
		# Get lowest common denominator of
		# partitions for all the Nodemanager.

		# First get the parts for the first NodeManager
		parts = set(self.get_parts(host=self.nm[0]))

		if len(self.nm) > 1:
			# For every subsequent NodeManager, get the parts
			# and only take the intersection
			for host in self.nm[1:]:
				host_parts = set(self.get_parts(host=host))
				parts = parts.intersection(host_parts)
		# Finally convert the list of
		# partitions to a string
		p = list(parts)
		p.sort()
		f1 = lambda x: "%s/yarn/local" % x
		f2 = lambda x: "%s/yarn/log" % x
		local_dir_parts = map(f1, p)
		log_dir_parts = map(f2, p)
		log_dirs = ','.join(log_dir_parts)
		local_dirs = ','.join(local_dir_parts)
		level_db_dir = self.get_largest_part(host = self.app_tl_server)
		v = {
			"yarn.resourcemanager.resource-tracker.address": "%s:8025" % self.resource_mgr,
			"yarn.resourcemanager.hostname": "%s" % self.resource_mgr,
			"yarn.resourcemanager.address": "%s:8050" % self.resource_mgr,
			"yarn.resourcemanager.scheduler.address": "%s:8030" % self.resource_mgr,
			"yarn.timeline-service.webapp.address": "%s:8188" % self.app_tl_server,
			"yarn.timeline-service.address": "%s:10200" % self.app_tl_server,
			"yarn.resourcemanager.webapp.address": "%s:8088" % self.resource_mgr,
			"yarn.resourcemanager.webapp.https.address": "%s:8090" % self.resource_mgr,
			"yarn.log.server.url": "http://%s:19888/jobhistory/logs" % self.hist_server,
			"yarn.resourcemanager.admin.address": "%s:8141" % self.resource_mgr,
			"yarn.timeline-service.webapp.https.address": "%s:8190" % self.app_tl_server,
			"yarn.nodemanager.local-dirs": local_dirs,
			"yarn.nodemanager.log-dirs": log_dirs,
			"yarn.timeline-service.leveldb-timeline-store.path":
				"%s/yarn/timeline" % level_db_dir,
		}
		# Zookeepers
		f = lambda x: "%s:2181" % x
		z = map(f, self.zk)
		zk = ','.join(z)
		v["hadoop.registry.zk.quorum"] = zk
		v["yarn.resourcemanager.zk-address"] = z[0]

		f = lambda x: ("yarn-site.%s" % x[0], x[1])
		variables = dict(map(f, v.items()))
		return variables
