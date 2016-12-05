Introduction
============

|hdp| (HDP) is an enterprise-grade Hadoop distribution from Hortonworks. Architected, developed, and built completely in the open, HDP provides Hadoop designed to meet the needs of enterprise data processing.

The deployment of HDP on a cluster is a non-trivial task. The Ambari service, developed by Hortonworks, aids in the installation of |hdp|. Ambari provides a web interface that enables the deployment of Hadoop services across a cluster. However, this requires an additional deployment step. While Ambari is used to deploy HDP on a cluster, Ambari itself needs to be setup on a cluster too. |stackiq| Cluster Manager automates the deployment of Ambari in a few simple steps.

The |stackiq| Bridge Roll for HDP provides the software necessary to easily deploy Ambari on a cluster.

Installing StackIQ Enterprise Data
----------------------------------

1.  StackIQ Enterprise Data ISO, downloaded from  
    the [StackIQ Website](http://www.stackiq.com/).

1.  Wait for the figure-welcome-qsg.

    ![Welcome screen](images/install/install-welcome-6_5.png)

    > Click on **CD/DVD-based Roll**.

2.  Select the following Rolls on the figure-roll-select-qsg.

    -   Cluster-core
    -   OS
    -   hdp-bridge
    -   HDP-2.1.5.0
    -   Ambari-1.x

    \* Updates-Ambari-1.6.1  
    -   HDP-Utils-1.1.0.19

    ![Roll Selection Screen](images/install/install-select-rolls-sed-6_6.png)

    Click **Submit**.

3.  You should now be back on the original  
    Welcome Screen \<figure-selected-rolls-qsg\>. On the left-side, you should see a list of rolls that have been chosen.

    ![Selected Rolls](images/install/install-selected-rolls-sed-6_6.png)

    Click **Next**.

Deploying Hortonworks Data Platform
===================================

As mentioned in a previous section, |hdp| can be deployed using the Ambari Installation service. The Ambari service provides a web UI, as well as a HTTP ReST API that allows the administrator to deploy |hdp|.

The Ambari GUI is a web-based service that can be accessed using a web-browser.

The Ambari ReST API requires the admin to make HTTP calls to the Ambari service. |stackiq| provides a wrapper to the Ambari API that makes it easy to deploy |hdp| without using the Ambari GUI.

### Using the Ambari GUI

After the installation of all the backend nodes, the Ambari Server appliance allows the installation, configuration, monitoring, and management of the entire HDP stack using a web-based administration tool, called the Ambari GUI. This tool is accessible by a web-browser at port 8080 of the ambari server.

> **note**
>
> The instructions below will require you to
>
> -   Choose Hadoop Services
> -   Assign Hadoop components to individual hosts
> -   Configure Hadoop Services
>
> These tasks are entirely dependent on the needs of the client. If you require assistance with the choosing which Hadoop services to use, the most optimum mapping of hosts to services, etc., StackIQ recommends that the administrator contact Hortonworks Inc. for more information on the choices for installation and configuration of the HDP stack.
>
> This document lists a rudimentary HDP cluster with all services configured and installed.

1.  By default, the hostname of the ambari server is `ambari-0-0.local`. Using a web-browser from your StackIQ management node, navigate to `http://ambari-0-0.local:8080` This will bring up the figure-ambari-ui-login.

    ![Ambari Login Screen](images/ambari/ambari-login.png)

    By default, the Ambari administrator username is set to `admin`, and password is set to `admin`. Log in to the Web UI using these values.

    > **note**
    >
    > It is recommended that the cluster administrator change these values through the Ambari UI, soon after configuring the HDP installation.

2.  This will bring you to the figure-ambari-cluster. Name the HDP cluster. In this example, we use the name **dev**

    ![Ambari Cluster Name Screen](images/ambari/ambari-clustername.png)

    Click **Next**.

3.  The figure-ambari-stack requires the admin to point to the version of HDP to be used, and the location of the HDP repository.

    Here we choose HDP-2.1

    ![HDP Stacks](images/ambari/ambari-stacks.png)

    Click on \*\*Advanced Repository Options\*\* \<figure-ambari-repo\>.

    By default, all OSes other than **Redhat 6** are disabled. Verify that this is the case, and that it points to the distribution on the frontend.

    If the cluster-wide IP address of the StackIQ management node is `10.1.1.1`, the repository should point to `http://10.1.1.1/install/distributions/stack-dist/x86_64`.

    ![HDP RepoID and URL](images/ambari/ambari-repo.png)

    Click **Next**.

4.  The figure-ambari-bootstrap is where the administrator will enter information about the cluster.

    In the space meant for **Names of Hosts**, enter the names of all the **Compute** hosts in your cluster.

    In the space meant for *Private Key*, enter the contents of the `/root/.ssh/id_rsa` private key.

    ![Host Installation Screen](images/ambari/ambari-bootstrap-hosts.png)

    Click **Next**.

5.  The figure-ambari-hostinst shows you the status of installation and registration of compute nodes with the Ambari server.

    ![Host Installation Screen](images/ambari/ambari-hostinst.png)

    This process, depending on the number of hosts, typically takes a few minutes to complete. Once all the nodes have successfully installed, and you see the figure-ambari-hostinst-complete screen, click **Next**.

    ![Host Installation Completion](images/ambari/ambari-hostinst-complete.png)

    > **warning**
    >
    > During this process, the Ambari GUI may complain about IPtables, and about ganglia. These warnings can be ignored.

6.  The figure-ambari-services shows you all the available services in the HDP-2.1 stack. For this example we select all available services.

    ![HDP Services Screen](images/ambari/ambari-services.png)

    Click **Next**.

7.  The figure-ambari-service-map shows the mapping mapping between hosts and Master services. You may choose to leave this mapping as-is, or modify it to suit the needs of the installation.

    ![HDP Master Components screen](images/ambari/ambari-service-map.png)

    Click **Next**

8.  The figure-ambari-service-map2 shows the mapping of hosts to slave and client components.

    ![HDP Slave/Client Components screen](images/ambari/ambari-service-map2.png)

    Click **Next**

9.  The figure-ambari-service-conf shows the configuration of all the services selected. You can customize the services as necessary.

    ![HDP Service Configuration](images/ambari/ambari-service-conf.png)

    > **note**
    >
    > The services that have the red badge next to their  
    > name require attention. Navigate to those services, and fill in the required configuration.
    >
10. The figure-ambari-confirmation, shows the confirmation dialog before starting the installation.

    ![Confirmation/Deployment Screen](images/ambari/ambari-confirmation.png)

11. The figure-ambari-installing, shows the status and progress of the installation of the HDP components, and dependent services.

    ![HDP Installation Screen](images/ambari/ambari-installing.png)

12. The figure-ambari-finish, shows the completion of the HDP Installation

    ![HDP Installation Screen](images/ambari/ambari-finish.png)

At the end of this process, you should have a fully-functional HDP installation.

### Using the StackIQ CLI

The Ambari web interface is very user-friendly, but to help with automation of the cluster installation, a CLI is needed. To that end, the Ambari server provides a REST API to help deploy and configure HDP services and components. This REST API uses HTTP calls - GET, POST, PUT, and DELETE - to inspect, create, configure, and remove components and services in the Ambari server.

StackIQ’s Cluster Manager provides a CLI, with the moniker `stack`, that allows system administrators to manage large cluster installations with ease. The CLI has a complete view of the entire cluster, the hardware resources, and the software configuration.

The StackIQ CLI has been extended to talk to the Ambari server using the REST API. This allows us to use the familiar "stack" commands to add HDP clusters, hosts, services, components, and configure each of the services to fit the needs of the users.

There are two advantages to using the |stackiq| CLI to deploy |hdp|.

-   As mentioned earlier, a CLI allows for easy scripting -hence easy automation.
-   The StackIQ CLI is completely plugged into the StackIQ database, and can transfer knowledge about the cluster to the Ambari server.

The entire list of |stackiq| commands that talk to the Ambari server are in the rcl section

Some of the more commonly used commands are listed below.

-   The command that forms the basis of all other Ambari-specific commands is :

        # stack run ambari api [resource=string] [command=GET|PUT|POST|DELETE] [body=JSON]

    This command makes a generic API call to the Ambari server.

    For example, if we need to list all the clusters in an Ambari server, run :

        # stack run ambari api resource=clusters command=GET

-   To create a HDP cluster called **dev**, run :

        # stack run ambari api resource=clusters/dev command=POST
          body=’{"Clusters": {"version": "HDP-2.1"}}’

-   To add hosts to the Ambari server, run :

        # stack add ambari host {host}

    This command bootstraps the host, runs the ambari-agent on the host, and registers the host with the Ambari server.

-   Add a HDP cluster to the Ambari server, with the given name and version number :

        # stack add ambari cluster {cluster} [version=string]

> -   Add a host to the HDP cluster. The host must be added to the Ambari server using the `stack add ambari host` command before this command is run :
>
>         # stack add ambari cluster host {hosts} [cluster=string]
>
-   Send service specific configuration to the Ambari server as a JSON string :

        # stack add ambari config [body=JSON] [cluster=string] [config=string]

-   Add a HDP service (e.g., HDFS, MapReduce or YARN) to the HDP cluster :

        # stack add ambari service [cluster=string] [service=string]

-   Add a HDP component (e.g., HDFS Namenode, MapReduce History Server, etc.) to the HDP cluster :

        # stack add ambari host component {host} [cluster=string] [component=string]

-   Print the desired HDP cluster configuration :

        # stack report ambari config [cluster=string]

-   Start the HDP cluster through Ambari :

        # stack start ambari cluster {cluster}

-   Start a single host component in the HDP cluster :

        # stack start ambari host component {hosts} [cluster=string] [component=string]

-   Start a single service in the HDP cluster :

        # stack start ambari service [cluster=string] [service=string]

-   Start all instances of a service component in a HDP cluster :

        # stack start ambari service component [cluster=string] [component=string] [service=string]

-   Stop all services in a HDP cluster :

        # stack stop ambari cluster {cluster}

-   Stop a single instance of a service component running on the specified host :

        # stack stop ambari host component {hosts} [cluster=string] [component=string]

-   Stop a single service in the HDP cluster :

        # stack stop ambari service [cluster=string] [service=string]

-   Stop all instances of the specified component in a HDP cluster :

        # stack stop ambari service component [cluster=string] [component=string] [service=string]

-   Synchronize the configuration of an Ambari cluster to the configuration specified in the StackIQ database. This command gets the output of the "stack report ambari config" command, and applies it to the Ambari server :

        # stack sync ambari config [cluster=string]

-   Synchronize the hosts and host components to the HDP cluster. The database maintains a mapping of hosts to service components. For example, the StackIQ database contains data mapping the "HDFS datanode" service, and the "YARN Resource Manager" service to "compute-0-1" :

        # stack sync ambari hosts {cluster}

-   Synchronize all the services to the HDP cluster. The list of services , ex. HDFS, MapReduce, YARN, Nagios, etc., that the admin wants to deploy is gleaned from the StackIQ database. This command gets the list of services from the database, and creates the services in the HDP cluster :

        # stack sync ambari services {cluster}

-   This command is a meta command that runs some / all the commands listed above :

        # stack create ambari cluster {cluster}

#### Deploying a HDP cluster on a Newly Installed StackIQ Cluster

The `stack create ambari cluster` command can be used to initially deploy HDP on a newly installed StackIQ cluster.

Simply map the necessary HDP components to the specific backend nodes that you want the components to run on. This mapping can be done using the "stack set host attr" command.

For example, if we want to deploy a namenode on compute-0-2, we can run :

    # stack set host attr compute-0-2 attr=hdp.hdfs.namenode value=true

We repeat the above command for all the components that we want to deploy. At a minimum, HDFS, ZooKeeper, Ganglia, and Nagios service components must be mapped to compute nodes. Once the host-to-service component mapping is satisfactory, we can run the `stack create ambari cluster` command to deploy HDP.

This command gets a list of all hosts in the StackIQ cluster, checks to see which hosts are to be used in the HDP cluster, adds them, creates the required services, maps the service components to the hosts in the cluster, installs them, configures them, and then starts these services.

#### NameNode HA Mode

HDP provides for a feature called HDFS NameNode HA. This feature will allow the HDFS Namenode to operate in High-Availability Mode.

In this mode, 2 namenodes are defined, and a secondary NameNode is not defined.

The definition is done using the command :

    # stack set host attr compute-0-0 compute-0-1 attr=hdp.hdfs.namenode value=true

Once all the other requisite services are mapped with similar commands, run :

    # stack create ambari cluster <cluster name>

StackIQ Command Line for HDP-Bridge
===================================

The StackIQ Command Line Interface is used to install, configure and manage the |hdp| installation on a StackIQ Cluster

##### Updating the Hortonworks Data Platform Repository

The StackIQ cluster manager provides the requisite **YUM** repository files that will enable an admin to update the |hdp| bits, and integrating them into the StackIQ Cluster Manager.

Mirroring the HDP Repositories
==============================

StackIQ Enterprise enables easy mirroring of the |hdp| binaries.

1.  Create the |hdp| rolls :

        # cd /export/HDP
        # make
        Mirroring repo HDP-UTILS-1.1.0.19
        Creating disk1 (0.00MB)...
        Building ISO image for disk1 ...
        Mirroring repo Updates-ambari
        Creating disk1 (0.00MB)...
        Building ISO image for disk1 ...
        Mirroring repo Updates-HDP-2.1.5
        Creating disk1 (0.00MB)...
        Building ISO image for disk1 ...
        Mirroring repo ambari-1.x
        Creating disk1 (0.00MB)...
        Building ISO image for disk1 ...

    Depending on the outbound internet connection, the above command may take some time (On the order of 30 minutes to 3 hours).

2.  Once the HDP repositories are downloaded, the StackIQ Enterprise tools convert the repositories to StackIQ Rolls. This allows the administrator to add the repositories to the distribution and make them available for installation on all the backend nodes.
3.  With version |version| of the hdp-bridge roll, the ISO images created are
    -   ambari-1.x
    -   Updates-ambari-1.6.1
    -   Updates-HDP-2.1.5
    -   HDP-UTILS-1.1.0.19

4.  Add each of the above Roll ISO images to the StackIQ distribution, and enable them :

        # stack add roll ambari-1.x-6.6-0.x86_64.disk1.iso
        Copying ambari-1.x to Rolls.....77454 blocks
        # stack enable roll ambari-1.x
        # stack add roll HDP-UTILS-1.1.0.19-6.6-0.x86_64.disk1.iso
        Copying HDP-UTILS-1.1.0.19 to Rolls.....43259 blocks
        # stack enable roll HDP-UTILS-1.1.0.19
        # stack add roll HDP-2.1.5.0-6.6-0.x86_64.disk1.iso
        Copying HDP-2.1.5.0 to Rolls.....2816531 blocks
        # stack enable roll HDP-2.1.5.0
        # stack add roll Updates-ambari-1.6.1-6.5-0.x86_64.disk1.iso
        Copying Updates-ambari-1.6.1 to Rolls.....93430 blocks
        # stack enable roll Updates-ambari-1.6.1

5.  After all the required HDP rolls are added, recreate the default distribution :

        # stack create distro

Once this is process is complete, the StackIQ Cluster Manager has prepared the environment for upgrading the |hdp| software.

For more information about upgrading the |hdp| software on nodes running the Ambari service, and associated HDP services, contact Hortonworks Inc.
