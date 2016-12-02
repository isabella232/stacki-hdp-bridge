#
# @SI_Copyright@
# @SI_Copyright@
#

import os
import sys
import rocks.commands
import rocks.ambari
import urllib2
import json
import copy

class Command(rocks.commands.Command,
	rocks.commands.HostArgumentProcessor):
	"""
	Report Ambari / HDP Configuration.
	This command reports a fully resolved
	configuration from HDP Configuration templates,
	calculated configuration attributes, and StackIQ
	database configuration attributes.

	By default it outputs Configuration, Value, and Source.
	If a specific output-format is requested,
	the configuration file, configuration,
	and value are printed.
	<param name="cluster" type="string">
	Name of Cluster
	</param>
	"""
	def get_hdfs_name(self):
		return self.hdfs_name

	def set_hdfs_name(self, hdfs_name):
		self.hdfs_name = hdfs_name

	def run(self, params, args):
		(self.cluster,) = self.fillParams([
			('cluster', self.db.getHostAttr('localhost','hdp.cluster')),
			])

		trim = True
		if not params.has_key('output-format'):
			trim = False
				
		if self.cluster == None:
			self.abort('Please specify cluster')

		self.ambari = rocks.ambari.AmbariClient(self.db)

		self.host_map = self.ambari.getComponentsFromDB()
		self.hosts = self.host_map.keys()

		self.service_list = self.ambari.getServicesFromDB()

		# Get the default configuration from templates
		template_attrs = self.getConfigFromTemplate()

		# Calculate configs
		c_attrs = self.calculateAttrs()

		# Get the overrides from the database
		db_attrs = self.getConfigFromDB()

		# Merge the database and template configuration
		m1 = self.mergeConfig(c_attrs, template_attrs)
		merged_attrs = self.mergeConfig(db_attrs, m1)

		attr_list = {}
		for service in template_attrs:
			for scope in template_attrs[service]:
				for attr in template_attrs[service][scope]:
					a = 'hdp.%s.conf.%s.%s' % (service.lower(), scope, attr)
					v = template_attrs[service][scope][attr]
					s = 'T'
					attr_list[a] = (v, s)

		for service in c_attrs:
			for scope in c_attrs[service]:
				for attr in c_attrs[service][scope]:
					a = 'hdp.%s.conf.%s.%s' % (service.lower(), scope, attr)
					v = c_attrs[service][scope][attr]
					s = 'C'
					attr_list[a] = (v, s)

		for service in db_attrs:
			for scope in db_attrs[service]:
				for attr in db_attrs[service][scope]:
					a = 'hdp.%s.conf.%s.%s' % (service.lower(), scope, attr)
					v = db_attrs[service][scope][attr]
					s = 'D'
					attr_list[a] = (v, s)

		# get service configuration dictionary
		service_attrs = {}
		for service in merged_attrs:
			for scope in merged_attrs[service]:
				if not service_attrs.has_key(scope):
					service_attrs[scope] = {}
				service_attrs[scope].update(merged_attrs[service][scope])

		self.beginOutput()
		if trim == False:
			for a in attr_list:
				v = attr_list[a][0]
				s = attr_list[a][1]
				self.addOutput('localhost', [a, v, s])
			self.endOutput(header=['host', 'attr', 'value','source'], padChar='')
		else:
			self.addOutput('localhost', json.dumps(service_attrs))
			self.endOutput(header=['host','content'])
			

	def getConfigFromDB(self):
		attr_dict = {}
		host_attrs = self.db.getHostAttrs('localhost',filter='hdp.')
		for a in host_attrs:
			attr = a.split('.')[1:]
			# Ignore the hdp.* attributes
			if len(attr) < 2:
				continue

			# Ignore all attributes that are
			# not configuration attributes
			if attr[1] != 'conf':
				continue

			# Check to see if configuration attribute
			# belongs to a service that is actually
			# active
			service = attr[0].upper().strip()
			if service not in self.service_list:
				continue

			# Finally if all that is true, get the
			# filename, variable, and value
			var = '.'.join(attr[3:])

			# Get filename that the configuration file
			# needs to go into.
			# Since the filename is part of the attribute
			# we need the ability to store the filename
			# without using ".". This is because the "."
			# will cause the attribute to be split in a
			# different way.
			filename = attr[2]
			f = filename.split('__')
			if len(f) > 1:
				filename = '.'.join(f)

			# Get the Value of the attribute
			value = host_attrs[a]
			if not attr_dict.has_key(service):
				attr_dict[service] = {}
			if not attr_dict[service].has_key(filename):
				attr_dict[service][filename] = {}
			attr_dict[service][filename][var] = value

		return attr_dict

	def getConfigFromTemplate(self):
		attr_dict = {}
		# All configuration templates are stored
		# in the directory mentioned below.
		config_dir = '/opt/rocks/share/HDP/templates'
		for dir in os.listdir(config_dir):
			# Directory names map directly to
			# service names. Check to make sure
			# that the service is actually active
			if dir not in self.service_list:
				continue
			
			service_dir = '%s/%s' % (config_dir, dir)
			# Get a list of all files in the service directory
			for fname in os.listdir(service_dir):
				# Load the JSON from the file
				filename = '%s/%s' % (service_dir, fname)
				f = open(filename, 'r')
				try:
					attrs = json.load(f)
				except ValueError:
					sys.stderr.write("File %s has error\n" % filename)
					raise
				f.close()
				# Populate the attribute dictionary. This will
				# be a global dictionary.
				if not attr_dict.has_key(dir):
					attr_dict[dir] = {}
				attr_dict[dir][fname] = attrs

		return attr_dict

	def mergeConfig(self, attrs_a, attrs_b):
		# Merge Attribute sets
		# Every element of attrs_a is added
		# to attrs_b, and overrides attrs_b

		# Copy attrs dictionary. Don't modify in place
		# This is because python passes dictionaries
		# by reference, and not by value
		attr_dict = copy.deepcopy(attrs_b)

		for service in attrs_a:
			if not attr_dict.has_key(service):
				attr_dict[service] = {}
			for filename in attrs_a[service]:
				if not attr_dict[service].has_key(filename):
					attr_dict[service][filename] = {}
				attr_dict[service][filename].update(attrs_a[service][filename])

		return attr_dict

	def calculateAttrs(self):
		plugins = self.loadPlugins()
		attrs = {}
		req_plugins = []
		for plugin in plugins:
			if plugin.provides() in self.service_list:
				req_plugins.append(plugin)

		for plugin in req_plugins:
			plugin.init(self.host_map)
			vars = plugin.get_variables()
			service = plugin.provides()
			if not attrs.has_key(service):
				attrs[service] = {}
			for a in vars:
				conffile, attr = a.split('.', 1)
				f = conffile.split('__')
				if len(f) > 1:
					conffile = '.'.join(f)
				
				if not attrs[service].has_key(conffile):
					attrs[service][conffile] = {}
				attrs[service][conffile][attr] = vars[a]

		return attrs
