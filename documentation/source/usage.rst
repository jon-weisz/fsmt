Usage
=====

General Usage
-------------

If you installed ``fsmt`` in a custom path, make sure you add this path to your 
**$PYTHONPATH** & **$PATH** before starting fsmt::

    $ export PYTHONPATH=~/sandbox/fsmt/lib/python2.7/site-packages:$PYTHONPATH
    $ export PATH=~/sandbox/fsmt/bin/:$PATH

In general it is sufficient to just type ``fsmt`` and provde a path to a SCXML configuration file::

    $ fsmt configuration/std/stdtools.scxml

You can find some examples in the **configuration** folder of the fsmt source code. However, you can get some more info on how to use ``fsmt`` via::

    $ fsmt --help

For example, the ``-c`` switch will disable colour logging::

    $ fsmt -c configuration/std/stdtools.scxml
    
Or, with the ``-l`` switch, you can change the logging output level on console.
Choosing ``DEBUG`` will give you detailed debug information on the ``fsmt`` run::

    $ fsmt configuration/std/stdtools.scxml -l DEBUG
	

Logging
-------

Within ``fsmt``, there is a separate logging level called STREAM (5) (right
below DEBUG (10)), which is used for component output (stdout and stderr) that is written or read within the system.
In general, ``fsmt`` logs the output of **each** started component. You will find the log files at::

    /$log_path/fsmt/$TIMESTAMP/logs/$component-name.log
    
Additionally, a complete log is written into the logs folder. The default level for this log is set to STREAM. You can find this log at::

    /$log_path/fsmt/$TIMESTAMP/logs/FSMT-$USERNAME-$TIMESTAMP_full.log
    

Once ``fsmt`` is finished, a ``ZIP`` archive of the entire ``fsmt`` run is created at ``/$log_path/fsmt/$TIMESTAMP.zip``,
to allow you to easily share run information or report bugs/issues. Softlinks to the latest run are also created.

Log Folder
----------

For your convenience, ``fsmt`` creates several log directories on startup. These directories are::

    /tmp/$USER/fsmt/$TIMESTAMP/data
    /tmp/$USER/fsmt/$TIMESTAMP/fsm
    /tmp/$USER/fsmt/$TIMESTAMP/images
    /tmp/$USER/fsmt/$TIMESTAMP/plots
    /tmp/$USER/fsmt/$TIMESTAMP/videos
    /tmp/$USER/fsmt/$TIMESTAMP/logs

The default_path for these files is ``/tmp/$USER/``, you can specify your own path using the "-o" option::

    fsmt -o ~/sandbox/logs/ configuration/std/stdtools.scxml


Environment Variables
--------------------------

``fsmt`` automatically exports environment variables during each run, which you might use in your software/script/tools
in order to access log directory paths. For instance::

    14:48:42 INFO  [Utils.py@33]: Logging initialized at level INFO
    14:48:42 DEBUG [Utils.py@33]: Output path initialized in /tmp/flier/fsmtesting/05-26_144842
    14:48:42 DEBUG [Utils.py@33]: Envionment var $FSMTRA set to 05-26_144842
    14:48:42 DEBUG [Utils.py@33]: Envionment var $FSMBASE set to /tmp/flier/fsmtesting/05-26_144842/
    14:48:42 DEBUG [Utils.py@33]: Envionment var $FSMLOG set to /tmp/flier/fsmtesting/05-26_144842/logs
    14:48:42 DEBUG [Utils.py@33]: Envionment var $FSMFSM set to /tmp/flier/fsmtesting/05-26_144842/fsm
    14:48:42 DEBUG [Utils.py@33]: Envionment var $FSMIMG set to /tmp/flier/fsmtesting/05-26_144842/images
    14:48:42 DEBUG [Utils.py@33]: Envionment var $FSMPLO set to /tmp/flier/fsmtesting/05-26_144842/plots
    14:48:42 DEBUG [Utils.py@33]: Envionment var $FSMVID set to /tmp/flier/fsmtesting/05-26_144842/videos
    14:48:42 DEBUG [Utils.py@33]: Envionment var $FSMDAT set to /tmp/flier/fsmtesting/05-26_144842/data
    14:48:42 DEBUG [Utils.py@33]: Creating FSM instance using your config: configuration/std/stdtools.scxml

In a shell script, for instance, you could do something like this::

    #!/bin/bash
    cat $FSMDAT/my_logfile.log | grep ERROR

