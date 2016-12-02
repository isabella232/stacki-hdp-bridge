from rocks.commands.sync.ambari import plugin

class Plugin(plugin):
	def provides(self):
		return 'MAPREDUCE2'

	def set_appliances(self):
		self.hist_server = None
		for host in self.hostmap:
			for component in self.hostmap[host]:
				if component == 'HISTORYSERVER':
					self.hist_server = host

	def get_variables(self):
		self.set_appliances()
		v = {
			"mapreduce.jobhistory.address": "%s:10020" % self.hist_server,
			"mapreduce.jobhistory.webapp.address": "%s:19888" % self.hist_server 
		}
		f = lambda x: ("mapred-site.%s" % x[0], x[1])
		variables = dict(map(f, v.items()))
		return variables

