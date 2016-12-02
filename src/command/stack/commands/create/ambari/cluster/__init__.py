import rocks.commands
import rocks.ambari
import urllib2
import json

class Command(rocks.commands.Command):
	"""
	Create, Install, and start a HDP Cluster.
	Before this command is run, every relevant
	attribute must be present in the StackIQ
	database.

	This command synchronizes hosts, services,
	host &lt;-&gt; service-component mapping.

	It creates all the services, installs them,
	and starts the cluster.

	It also has support for Namenode HA.
	<arg type="string" name="cluster">
	Name of Cluster
	</arg>
	"""

	def run(self, params, args):
		if len(args) != 1:
			self.abort('Please specify Cluster')
		cluster = args[0]
		self.ambari = rocks.ambari.AmbariClient(self.db)

		# Check if cluster exists
		c = self.ambari.run('clusters')['items']
		cl_found = False
		for cl in c:
			if cl['Clusters']['cluster_name'] == cluster:
				cl_found = True

		if cl_found:
			self.abort('Cluster %s already exists' % cluster)


		# Add the cluster to Ambari
		print "Adding Ambari Cluster"
		self.call('add.ambari.cluster',[cluster])

		# Add all the hosts from Ambari to the cluster
		print "Synchronising hosts"
		self.call('sync.ambari.hosts',['cluster=%s' % cluster])

		# Sync the cluster configuration
		print "Synchronising Ambari Config"
		self.call('sync.ambari.config',['cluster=%s' % cluster])

		# Sync the cluster configuration
		print "Synchronising Ambari Services"
		self.call('sync.ambari.services',['cluster=%s' % cluster])

		# Set the GUI state on Ambari to DEFAULT view
		cluster_status = {
			"clusterName": cluster,
			"clusterState":"DEFAULT"
			}
		self.ambari.run('persist', command="POST", params={
			"CLUSTER_CURRENT_STATUS":json.dumps(cluster_status)
			})

		# Tell Ambari GUI that the cluster is now installed.
		p = {"Clusters":{"provisioning_state":"INSTALLED"}}
		self.ambari.run('clusters/%s' % cluster, command="PUT", params=p)

		# Install the cluster services
		print "Installing Cluster Services"
		p = {
			"RequestInfo": {"context" :"Installing Cluster Services"},
			"Body": {"ServiceInfo":{"state":"INSTALLED"}}
		}
		self.ambari.run('clusters/%s/services?ServiceInfo/state=INIT' % cluster,
			command="PUT", params=p)


		ha_enabled = self.check_ha()

		if ha_enabled:
			self.install_ha(cluster)

		# Start the cluster services
		print "Starting Ambari Cluster"
		self.call('start.ambari.cluster',[cluster])


	def check_ha(self):
		hostmap = self.ambari.getComponentsFromDB()
		count = 0
		for host in hostmap:
			if 'NAMENODE' in hostmap[host]:
				count = count + 1
		if count > 1:
			return True
		return False
				
	def install_ha(self, cluster):
		print "Installing HA"
		self.call('start.ambari.service',
			['service=ZOOKEEPER',
			'cluster=%s' % cluster]
			)

		self.call('start.ambari.service.component',
			['service=HDFS',
			'component=JOURNALNODE',
			'cluster=%s' % cluster])

		hdfs_name = self.ambari.getConfigFromAmbari(cluster,
			'hdfs-site','dfs.nameservices')
		nn0 = self.ambari.getConfigFromAmbari(cluster, 
			'hdfs-site','dfs.namenode.http-address.%s.nn0' % hdfs_name)
		nn1 = self.ambari.getConfigFromAmbari(cluster, 
			'hdfs-site','dfs.namenode.http-address.%s.nn1' % hdfs_name)
		nn0_host = nn0.split(':')[0]
		nn1_host = nn1.split(':')[0]

		# Format the HDFS filesystem
		print "Formatting Namenode on %s" % nn0_host
		cmd = "su -l hdfs -c \"hdfs namenode -format -force -nonInteractive\""
		print cmd
		self.command("run.host",[nn0_host, "command=%s" % cmd])

		# Create dfs.include and dfs.exclude files. Otherwise, Ambari complains
		cmd = "touch /etc/hadoop/conf/dfs.include /etc/hadoop/conf/dfs.exclude"
		print cmd
		self.command("run.host",[nn0_host, "command=%s" % cmd])

		# Initialize shared edits
		print "Initializing Shared Edits"
		cmd = "yes | su -l hdfs -c \"hdfs namenode -initializeSharedEdits\""
		print cmd
		print self.command("run.host",[nn0_host, "command=%s" % cmd])

		# Start the primary namenode
		self.command("start.ambari.host.component",
			[nn0_host, "cluster=%s" % cluster,
			"component=NAMENODE"])

		# Format Zookeeper failover controller partition
		print "Formatting Zookeeper Failover Controller"
		cmd = "su -l hdfs -c \"hdfs zkfc -formatZK -nonInteractive\""
		print cmd
		print self.command("run.host",[nn0_host, "command=%s" % cmd])


		# Initialize the Failover namenode
		print "Bootstrapping Standby Namenode %s" % nn1_host
		cmd = "su -l hdfs -c \"hdfs namenode -bootstrapStandby\""
		print cmd
		print self.command("run.host",[nn1_host, "command=%s" % cmd])

		# Create /tmp on HDFS with the correct permissions. Otherwise,
		# some services will fail to start
		self.command("start.ambari.service",
			["cluster=%s" % cluster, "service=HDFS"])
		print "Creating /tmp directory on HDFS"
		cmd = "su -l hdfs -c \"hdfs dfs -mkdir hdfs://%s/tmp\"" % hdfs_name
		print cmd
		print self.command("run.host",[nn0_host, "command=%s" % cmd])
		cmd = "su -l hdfs -c \"hdfs dfs -chmod 0777 hdfs://%s/tmp\"" % hdfs_name
		print cmd
		print self.command("run.host",[nn0_host, "command=%s" % cmd])
