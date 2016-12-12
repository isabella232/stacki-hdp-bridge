Introduction
============

The Hortonworks Data Platform (HDP) is an enterprise-grade Hadoop distribution from Hortonworks. Architected, developed, and built completely in the open, HDP provides Hadoop designed to meet the needs of enterprise data processing.

The deployment of HDP on a cluster is a non-trivial task. The Ambari service, developed by Hortonworks, aids in the installation of HDP. Ambari provides a web interface that enables the deployment of Hadoop services across a cluster. However, this requires an additional deployment step. While Ambari is used to deploy HDP on a cluster, Ambari itself needs to be setup on a cluster too. Stacki automates the deployment of Ambari in a few simple steps.

The Stacki bridge Roll for HDP provides the software necessary to easily deploy Ambari on a cluster.

Installing Ambari/HDP with Stacki
----------------------------------

The installation of Ambari and subsequent deployment of HDP on your cluster requires:

A working stacki frontend with an internet connection.
The stacki-hdp-bridge pallet.
The HDP repositories pulled from the Hortonworks site. 

Luckily, we have made this easy for you.

1. First install a stacki fronted.
This has been documented before. If you're on this documentation, you have already installed a frontend. If you are here without a stacki frontend. Go install one. Then come back. I can wait...(Are we there yet?)

2. Install the stacki-hdp-pallet.
```
# git clone this repository 
```
or
```
# wget * the iso
```
Add and then enable the pallet:
```
# stack add pallet stacki-hdp-pallet*.iso
# stack list pallet 
```

to make sure it's present

Then enable it:
```
# stack enable pallet stacki-hdp-pallet
```
Now run it. A pallet generally has both frontend and backend configuration. To get the frontend configuration to happen for a pallet that contains it, run the pallet
```
# stack run pallet stacki-hdp-bridge
```
To see what scripts are going to run, and then run it for real:
```
# stack run pallet stacki-hdp-bridge | bash
```
The hdp-bridge pallet creates an ambari appliance, some key/value pairs (attributes), and sets-up a directory for getting the HDP repository you want. 

Let's get the HDP and HDP-UTILS and Ambari repositories
```
# cd /export/HDP
```
```
# cat hdp.cfg

[default]
distribution = 2.x
os = centos7
ambari = 2.4.2.0
hdp = 2.5.3.0
```


The hdp.cfg is an ini-style file that tells the "gethdp" program which versions of the Ambari and HDP to download. You'll note that this is latest and greatest. To get something different, change the appropriate entries and run the "gethdp" script in that directory.

Get the distribution:

If you do:
```
# stack list pallet
```
You won't have any HDP or Ambari pallets yet. We are going to get them now.

```
# gethdp
```

This generates the ambari.repo and hdp.repo files in the /export/HDP directory. Then it uses those repo files to download the Updates-ambari, HDP, and HDP-Utils repositories and turns them into pallets. (Combines them into an iso which is what a pallet gets installed as.) 

Now wait. Depending on your connection to the outside world, this can take minutes to hours. Go to lunch. Do yoga and then take a nap. Go to the dentist for the three root canals you've been putting off. (I recommend the nitrous.) Or drink more coffee than you ever have in your life and go home a quivering mass of stressed-out flesh. In the morning, these will be done. Hopefully you'll have slept.

Once they're downloaded, this script will add the HDP, HDP-Utils and Ambari pallets and it will enable them too. Maybe that's presumptuous of me to decide that for you, but why did you download this if you weren't going to do that? 

It should look like this:
```
# stack list pallet

NAME               VERSION  RELEASE ARCH   OS     BOXES
CentOS:            7        7.x     x86_64 redhat default
stacki:            3.3      7.x     x86_64 redhat default
CentOS-Updates:    7.2      0       x86_64 redhat default
HDP-UTILS:         1.1.0.21 7.x     x86_64 redhat default
HDP:               2.5.3.0  7.x     x86_64 redhat default
Updates-ambari:    2.4.2.0  7.x     x86_64 redhat default
stacki-hdp-bridge: 2.5      7.x     x86_64 redhat default
```

Installing an Ambari Server
===================================

The bridge pallet creates an ambari appliance when you do the "stack run pallet stacki-hdp-bridge | bash" command.

```
# stack list appliance
APPLIANCE LONG NAME PUBLIC
frontend: Frontend  no
backend:  Backend   yes
ambari:   Ambari    yes
```

This allows us to set-up the configuration on initial installation so you have a fully functioning Ambari instance. From this Ambari machine, you can deploy HDP on the rest of the machines. 

Separating the Ambari server from the frontend (many of our application pallets do this) separates the roles of the machines in the cluster. If you lose the frontend (rare), you still have a fully functioning Ambari/HDP cluster. 

Right now they're all "backend" appliances:
```
# stack list host
HOST         RACK RANK CPUS APPLIANCE BOX     ENVIRONMENT RUNACTION INSTALLACTION
stacki34:    0    0    2    frontend  default ----------- os        install
backend-0-0: 0    0    2    backend   default ----------- os        install
backend-0-1: 0    1    2    backend   default ----------- os        install
backend-0-2: 0    2    2    backend   default ----------- os        install
backend-0-3: 0    3    2    backend   default ----------- os        install
backend-0-4: 0    4    2    backend   default ----------- os        install
```
We will designate backend-0-0 as the Ambari server by setting its appliance type to "ambari".

```
# stack set host appliance backend-0-0 appliance=ambari

# stack list host
HOST         RACK RANK CPUS APPLIANCE BOX     ENVIRONMENT RUNACTION INSTALLACTION
stacki34:    0    0    2    frontend  default ----------- os        install
backend-0-0: 0    0    2    ambari    default ----------- os        install
backend-0-1: 0    1    2    backend   default ----------- os        install
backend-0-2: 0    2    2    backend   default ----------- os        install
backend-0-3: 0    3    2    backend   default ----------- os        install
backend-0-4: 0    4    2    backend   default ----------- os        install
```

Now we'll install the Ambari appliance. If you have not installed all the backend machines yet, you can do so at this time. There are no dependencies between the Ambari server and the backend machines. 

Set the disks and controllers to nuke if this is the first time:
```
# stack set host attr backend ambari attr=nukedisks value=true
# stack set host attr backend ambari attr=nukecontroller value=true
```
(The "backend ambari" in the above commands automatically apply the command to any machine that is one of those appliances. You can use regexes too. Neato huh?)

Set them to install on the next pxe boot. (Your machines are set to pxe first right? If you're managing a cluster and they're not, why not? You need to explain.

```
# stack set host boot backend ambari action=install
```
Now reboot or power cycle in whatever manner you have. My condolences if you have to do this via a java web app.

Once the machines are up, go to the next section to setup Hadoop.

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
