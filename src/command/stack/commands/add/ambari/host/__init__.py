import os
import time
import rocks.commands
import rocks.ambari
import urllib2

class Command(rocks.commands.Command,
	rocks.commands.HostArgumentProcessor):
	"""
	Bootstrap Hosts, and add them to Ambari
	<arg name="host" type="string">
	Hosts to add
	</arg>
	"""

	def run(self, params, args):
		# Get the Ambari Client object
		self.ambari = rocks.ambari.AmbariClient(self.db)
		hosts = self.ambari.getFQDNames(args)

		# Get RSA Private Key
		f = open("/root/.ssh/id_rsa",'r')
		id_rsa = f.read()
		f.close()
		id_rsa = id_rsa.strip()
		# Set command body
		cmd_body = {
			'verbose': True,
			'sshKey': id_rsa,
			'hosts':hosts,
			'user': 'root',
			'userRunAs': 'root'
			}

		# Bootstrap the hosts
		j = self.ambari.run("bootstrap", command="POST", params=cmd_body)

		# Wait for the bootstrap process to complete
		req_id = int(j['requestId'])
		req_stmt = "bootstrap/%d" % int(req_id)
		done = False
		while not done:
			done = True
			j = self.ambari.run(req_stmt, command="GET")
			status = j['status']
			if status == 'SUCCESS':
				done = True
				continue
			if status == 'RUNNING':
				done = False
				time.sleep(1)
				continue
			if status == 'ERROR':
				done = True
				log = ""
				for hs in j['hostsStatus']:
					if hs['status'] == 'FAILED':
						log = log + hs['log']
				continue
			if not j.has_key('hostsStatus'):
				done = False
				time.sleep(1)
				continue
			for hs in j['hostsStatus']:
				if hs["status"] != "DONE":
					done = False
					time.sleep(1)
					break
		# Make sure all hosts specified
		# are registered with the Ambari
		# server
		if status == 'ERROR':
			print log
			self.abort('Failed to bootstrap')
		done = False
		while not done:
			done = True
			for host in hosts:
				hr = "hosts/%s" % host
				try:
					self.ambari.run(hr)
				except urllib2.HTTPError, e:
					done = False
					time.sleep(1)
