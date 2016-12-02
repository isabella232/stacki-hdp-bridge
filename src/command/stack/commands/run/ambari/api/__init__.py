#@ SI_Copyright@
#@ SI_Copyright@

import rocks.commands
import rocks.ambari
import json
import os, sys

class Command(rocks.commands.Command):
	"""
	Command that makes an Ambari API Call
	<param name="resource" type="string">
	Resource to query
	</param>
	<param name="command" type="string">
	HTTP Command to run. Defaults to "GET".
	Options are GET | PUT | POST | DELETE.
	GET returns the state of the resource.
	POST creates the resource.
	PUT modifies the resource.
	DELETE deletes the resource.
	</param>
	<param name="body" type="string">
	Arguments to the command to be run.
	Used only with PUT or POST commands
	</param>
	<example cmd='run ambari api resource=clusters'>
	Returns all the clusters in Ambari
	</example>

	<example cmd='run ambari api resource=clusters/dev2 command=POST body=&apos;{&quot;Clusters&quot;:{&quot;version&quot;:&quot;HDP-2.0.6&quot;}}'>
	Create an Ambari Cluster called "dev2" with HDP Version 2.0.6
	</example>
	"""
	def run(self, params, args):

		(resource, cmd, body) = self.fillParams([
			('resource', None),
			('command','GET'),
			('body', None),
			])
		if not resource:
			self.abort("Please specify resource")

		a = rocks.ambari.AmbariClient(self.db)
		if body:
			try:
				b = json.loads(body)
				body = b
			except:
				self.abort("body is malformed")

		o = a.run(resource, cmd, body)
	
		if o:
			self.beginOutput()
			try:
				if sys.stdout.isatty():
					self.addOutput('localhost', json.dumps(o, indent=2))
				else:
					self.addOutput('localhost', json.dumps(o))
			except:
				self.addOutput('localhost', o)
			self.endOutput()
