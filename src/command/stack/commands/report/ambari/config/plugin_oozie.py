from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'OOZIE'

	def set_appliances(self):
		self.oozie_server = None
		for host in self.hostmap:
			for component in self.hostmap[host]:
				if component == 'OOZIE_SERVER':
					self.oozie_server = host

	def get_variables(self):
		self.set_appliances()
		p = self.get_largest_part(host=self.oozie_server)
  		v = {
  			"oozie-site.oozie.base.url": "http://%s:11000/oozie" % self.oozie_server,
  			"oozie-env.oozie_data_dir": "%s/oozie/data" % p,
			"oozie-env.oozie_hostname": self.oozie_server

		}
		return v
