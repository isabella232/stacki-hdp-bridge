#
# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@
#

import os
import sys
import time
import json
import re
import urllib
import urllib2
import cookielib
import base64
import rocks.commands

class AmbariClient(rocks.commands.HostArgumentProcessor,
	rocks.commands.PartitionArgumentProcessor):
	def __init__(self, db=None, server=None,
		port=None, username=None, passwd=None):

		self.db = db

		# Try to get infomation from the database
		self.set_ambari_info(server, port, username, passwd)

		# Unset debugging to start with. We can set it
		# as needed
		self.unset_debug()
		self.unset_dump()

		if os.environ.has_key('ROCKSDEBUG') or \
			os.environ.has_key('AMBARIDEBUG'):
			self.set_debug()
			self.set_dump()
		# Setup the cookie jar
		self.cookie = cookielib.CookieJar()

		# Setup the HTTP cookie processor
		o = urllib2.build_opener(
			urllib2.HTTPCookieProcessor(self.cookie)
			)
		# Install the processor
		urllib2.install_opener(o)

	def set_method(self, method="GET"):
		self.method = method

	def get_method(self):
		return self.method

	def set_body(self, body):
		self.body = body

	def set_ambari_info(self, s, p, u, pw):
		# If there's no database setup, set the values to the
		# ones that we pass as arguments or the default values
		if not self.db:
			s = s or 'localhost'
			p = p or 8080
			u = u or 'admin'
			pw = pw or 'admin'
		# If there is a database set up correctly, the values assigned
		# are in the following order ('>' denotes precedence)- 
		# user provided > database provided > default 
		else:
			s = s or self.db.getHostAttr('localhost','ambari.server')
			p = p or self.db.getHostAttr('localhost','ambari.port') or 8080
			u = u or self.db.getHostAttr('localhost','ambari.user') or 'admin'
			pw = pw or self.db.getHostAttr('localhost','ambari.passwd') or 'admin'

		# If the 'ambari.server' variable is not set
		# in the database, attempt to calculate it using
		# the ambari appliance. if it's still not set,
		# use 'localhost' as ambari server
		if not s:
			sql = """select n.name from nodes n,
			appliances a where n.appliance=a.id
			and a.name="ambari" """
			r = self.db.execute(sql)
			if r == 0:
				s = 'localhost'
			else:
				s = self.db.fetchone()[0]

		self.set_server(s)
		self.set_port(p)
		self.set_user(u)
		self.set_passwd(pw)

	def get_body(self):
		return self.body

	def set_server(self, server):
		self.server = server

	def set_port(self, port):
		self.port = port

	def set_user(self, user):
		self.user = user

	def set_passwd(self, passwd):
		self.passwd = passwd

	def set_debug(self):
		self.debug = True

	def unset_debug(self):
		self.debug = False

	def set_dump(self):
		self.dump = True

	def unset_dump(self):
		self.dump = False

	def is_cookie_set(self):
		if len(self.cookie) > 0:
			return True
		else:
			return False
	def dump_cmd(self, resource, command, params):
		cmd = "rocks run ambari api resource=%s command=%s" % \
			(resource, command)
		if params:
			cmd = "%s params='%s'" % (cmd, json.dumps(params))
		print cmd

	def run(self, resource, command='GET', params = None):
		# If we want to get a list of all commands that were run,
		# set dump to true
		if self.dump:
			self.dump_cmd(resource, command, params)
		# Set the method for the HTTP Call. This determines
		# the actual operation.
		self.set_method(method=command)

		# Get the URL to fetch
		url = "http://%s:%d/api/v1/%s" % (self.server, self.port, resource)

		# Create a request
		req = urllib2.Request(url)

		# Set the method for the request
		req.get_method = self.get_method

		# If cookie is not set, use basic authentication and
		# authorization
		if not self.is_cookie_set():
			req.add_header("Authorization", "Basic %s" % \
				base64.b64encode("%s:%s" % (self.user, self.passwd)))

		# If we're bootstrapping, we need another header
		if resource == 'bootstrap':
			req.add_header('Content-Type', 'application/json')

		req.add_header('X-Requested-By', 'ambari')
		# If params are provided, add to the body of the
		# request
		if params:
			req.add_data(json.dumps(params))

		# Open the URL
		if self.debug:
			print url, command
			print req.header_items()
			if req.has_data():
				print req.get_data()
			
		try:
			f = urllib2.urlopen(req)
		except urllib2.HTTPError,e:
			code = e.getcode()
			j = e.read()
			print code, j
			raise
		j = f.read()
		# Get the code
		code = f.getcode()

		if self.debug:
			print code
			if j:
				o = json.loads(j)
				print json.dumps(o, indent=2)
			

		# If we haven't crashed yet, get the output, and
		# load it as json
		o = None
		if j:
			o = json.loads(j)

		# if code is 202, it's an asynchronous command. Wait
		# till the command is complete
		if code == 202:
			out = self.wait_for_output(o)
			return out
		else:
			return o

	# function to parse the href arg, and strip out all the noise,
	# and return only the resource to query next
	def get_resource_from_href(self, href):
		st = "(http://%s:%d/api/v1/)([A-Za-z0-9/-_]+)" % (self.server, self.port)
		r = re.compile(st)
		m = r.match(href)
		return m.group(2)

	# function that waits for output
	def wait_for_output(self, o):
		if not o:
			return o
		resource = self.get_resource_from_href(o['href'])
		complete = False
		finished_status = ['COMPLETED', 'FAILED', 'ABORTED']
		f = self.run(resource, 'GET')
		task_list = []
		for task in f['tasks']:
			task_resource = self.get_resource_from_href(task['href'])
			task_list.append(task_resource)
		while not complete:
			complete = True
			for task in task_list:
				t = self.run(task, 'GET')
				status = t['Tasks']['status']
				if not status in finished_status:
					complete = False
					time.sleep(1)
					break

	# Helper Functions to get information from DB,
	# and from the Ambari service.

	# Function to get Fully Qualified Domain Names
	# of all hosts mentioned in args
	def getFQDNames(self, args = []):
		# Get a list of all hostnames
		h = self.getHostnames(args)
		host_list = []
		for host in h:
			# Get the primary_net interface for each host
			# This determines the hostname for the host
			i = self.db.getHostAttr(host, 'primary_net')
			if not i:
				i = 'private'
			# Get FQDN
			fqdn = self.getHostnames([host], subnet=i)[0]
			host_list.append(fqdn)
		return host_list

	#
	# There are 3 types of hdp. attributes
	#
	# 1. hdp.* - generic variables that are used
	# to configure the ambari service
	#
	# 2. hdp.<service>.<component> - True/False variable
	# that is host specific, and determines the services
	# to be configured using ambari.
	#
	# 3. hdp.<service>.conf.<conffile>.config.var.iable
	# Service-specific, hadoop config variable.
	#

	### Function to get a list of services from the DB
	def getServicesFromDB(self):
		# Get a list of all hosts
		hosts = self.getHostnames([])
		sl = []
		for host in hosts:
			# For every host, get the hdp.* host
			host_attrs = self.db.getHostAttrs(host, filter='hdp.')
			for a in host_attrs:
				# Strip the "hdp." part from the attribute
				attr = a.split('.')[1:]
				#
				# We only care about the hdp.<service>.<component>
				# type of attribute
				if len(attr) != 2:
					continue
				service = attr[0].upper()
				# Add the service to the list of enabled services
				try:
					sl.index(service)
				except:
					sl.append(service)

		return sl

	# Function to get list of components from DB
	def getComponentsFromDB(self):
		host_map = {}
		# Get FQDN for all hosts
		hosts = self.getFQDNames([])
		for host in hosts:
			host_attrs = self.db.getHostAttrs(host, filter='hdp.')
			for a in host_attrs:
				attr = a.split('.')[1:]
				# Use only the hdp.<service>.<component> attributes
				if len(attr) != 2:
					continue
				component = attr[1].upper()

				if not host_map.has_key(host):
					host_map[host] = []
				host_map[host].append(component)

		return host_map


	# Get a list of services configured on an ambari cluster
	def getServicesFromAmbari(self, cluster):
		c = self.run('clusters/%s/services' % cluster)
		f = lambda x: x['ServiceInfo']['service_name']
		services = map(f, c['items'])
		return services

	# Get the list of 
	def getComponentsFromAmbari(self, cluster):
		host_map = {}

		hosts = self.getHostsFromAmbariCluster(cluster)
		# Lambda function to get component name from output
		f_comp = lambda x: x['HostRoles']['component_name']
		for host in hosts:
			# Query Ambari to get a list of all host components
			resource = 'clusters/%s/hosts/%s/host_components' % \
				(cluster, host)
			c = self.run(resource)
			components = map(f_comp, c['items'])
			host_map[host] = components
		return host_map

	def getHostsFromAmbari(self):
		hosts = self.run('hosts')['items']
		f = lambda x: x['Hosts']['host_name']
		hl = map(f, hosts)
		return hl

	def getHostsFromAmbariCluster(self, cluster):
		hosts = self.run('clusters/%s/hosts' % cluster)['items']
		f = lambda x: x['Hosts']['host_name']
		hl = map(f, hosts)
		return hl

	def getHostsFromDB(self):
		host_map = self.getComponentsFromDB()
		return host_map.keys()

	def getConfigFromAmbari(self, cluster, conf, attr):
		val = None
		try:
			# Get the URL for the configuration
			url = 'clusters/%s?fields=Clusters/desired_configs/%s' % (cluster, conf)
			c = self.run(url)

			# Get the latest version of desired_configs
			tag = c['Clusters']['desired_configs'][conf]['tag']
			url = 'clusters/%s/configurations?type=%s&tag=%s' % (cluster, conf, tag)
			i = self.run(url)

			# Get all the properties
			props = i['items'][0]['properties']

			# Get the prop we were looking for
			val = props[attr]
		except:
			pass

		return val
		
