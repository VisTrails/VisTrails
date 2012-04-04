.. _chap-vistrails-server:

***********************
VisTrails Server Setup
***********************

.. index:: server 

* lets assume that everything is going to be put in the /server dir::

    $ cd /server
    $ mkdir vistrails

* put VisTrails Source in vistrails/ folder::

    $ cd vistrails
    $ git clone git://vistrails.org:vistrails.git git # or just download the latest release or nightly build

* make a logs dir for the server::

    $ mkdir logs

* if you are running the server without crowdLabs or as a remote server, you need to create a media directory with the following structure::

    /path/to/media_dir/
                       wf_execution/
                       graphs/
                              workflows/
                              vistrails/
                       medleys/
                              images/
  You can run ``python scripts/create_server_media_dir_structure.py /path/to/media_dir`` to create the directory structure automatically.

* Determine how you will start the vistrails server. You have a choice of using Xvfb or not. If you use it, /server/vistrails/git/scripts/start_vistrails_xvfb.sh is what you will use, otherwise, use start_vistrails.sh

Using Xvfb is slower and not recommended if your workflows will make use of volume rendering or other graphics-card intensive techniques. 

.. _sec-server-using-xvfb:

Using Xvfb
===========

* edit /server/vistrails/git/scripts/start_vistrails_xvfb.sh file and make sure it is consistent with your system setup::

    LOG_DIR=/server/vistrails/logs
    Xvfb_CMD=/usr/bin/Xvfb
    VIRTUAL_DISPLAY=":6"
    VISTRAILS_DIR=/server/vistrails/git/vistrails
    ADDRESS="<your_server.com>"
    PORT="8081" #the port where the server will listen for requests
    CONF_FILE="server.cfg"
    NUMBER_OF_OTHER_VISTRAILS_INSTANCES="1"
    MULTI_OPTION="-M" #execute the main instance multithreaded

* The setup above will execute 2 instances of the server. You can add more instances by changing the variable NUMBER_OF_OTHER_VISTRAILS_INSTANCES. When using multiple instances, the ports and virtual displays will be used incrementally, so if the main instance is using port 8081 and virtual display :6, the next instance will use port 8082 and virtual display :7, and so on. 

.. _sec-server-using-x-directly:

Connecting to X server directly
===============================

* If you decide no to use Xvfb, edit /server/vistrails/git/scripts/start_vistrails.sh file and make sure it is consistent with your system setup::

    LOG_DIR=/server/vistrails/logs
    VISTRAILS_DIR=/server/vistrails/git/vistrails
    ADDRESS="<your_server.com>"
    PORT="8081" #the port where the server will listen for requests
    CONF_FILE="server.cfg"
    NUMBER_OF_OTHER_VISTRAILS_INSTANCES="2"
    MULTI_OPTION="-M" #execute the main instance multithreaded

* The setup above will execute 3 instances of the server. You can add or remove more instances by changing the variable NUMBER_OF_OTHER_VISTRAILS_INSTANCES. When using multiple instances, the ports will be used incrementally, so if the main instance is using port 8081, the next instance will use port 8082, and so on. 

.. _sec-server-basic-configuration:

Basic Configuration
===================

* If the vistrails server will receive requests from the outside world and if you are using a firewall, make sure the ports used by the vistrails server are open and accessible.

* create a file called server.cfg in /server/vistrails/git/vistrails/ as follows::

    [access]
    permitted_addresses = localhost, 127.0.0.1, <crowdlabs-server-address>

    [media]
    media_dir=/server/crowdlabs/site_media/media

    [database]
    host = <vistrail database address>
    read_user = <read user>
    read_password = <read password>
    write_user = <write user>
    write_password = <write user password>

    [script]
    script_file=/server/vistrails/git/scripts/start_vistrails.sh
    virtual_display=<virtual display number>

* change permitted_addresses variable in to include the address of the machine running of the crowdLabs server (or other machines you want to be able to connect to the server)::

    [access]
    permitted_addresses = localhost, 127.0.0.1, <crowdlabs-server-address>


* Add the password for the full permission mysql user created in :ref:`VisTrails Database Setup <mysql-full-perm-user>`::

    write_user = <write user>
    write_password = <write user password>

* Configure the full path to the script file and if you are using Xvfb, also specify the virtual display of the main instance::

    [script]
    script_file=/server/vistrails/git/scripts/start_vistrails.sh
    virtual_display=0 #not using any display

* run vistrails in server mode::

    $ cd /server/vistrails/git/scripts
    # If you are running Xvfb:
    $ ./start_vistrails_xvfb.sh
    # Or if you are connecting to X server directly:
    $ ./start_vistrails.sh