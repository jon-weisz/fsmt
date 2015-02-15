Creating Tests
===============

In general, ``fsmt`` tests are based on *SCXML* descriptions. However, for 
your convenience, you don't need to write SCXML files. We have designed a 
*quasi DSL*, based on the widespread *ini* syntax. So all you need to do is 
to invoke the ``fsmt_iniparser``::

    $ fsmt_iniparser [/path/to/ini_file.ini]

Optionally, one can also define the output (default is /tmp/output.scxml) via the switch ``-o``::

    $ fsmt_iniparser -o [/some/path/a_test_file.scxml] [/path/to/a_test_file.ini]

Again, you can find various examples in the ``configuration`` folder. Anyway, 
in the remainder of this chapter, we will explain most of the features and 
their implications.

INI File Notation
-----------------

The required notation of the ini file is as follows (taken from the stdtools.ini example)::

    [environment]
    prefix = /vol/robocup/2013/
    PATH = $PATH:/vol/robocup2013/bin/
    component_path = /usr/bin/
    release_prefix = /
    PKG_CONFIG_PATH = /usr/lib/pkgconfig

    [component-1]
    name = evince
    command = evince
    path = $component_path
    execution_host = localhost
    check_execution = True
    check_type = pid
    timeout = 2
    blocking = True
    ongoing = False
    criteria =

    [component-2]
    name = xeyes
    command = xeyes
    path = /usr/bin/
    execution_host = localhost
    check_execution = True
    check_type = pid
    timeout = 2
    blocking = True
    ongoing = False
    criteria =

    [run]
    name = stdTest
    run_order = ('xeyes','evince'),
    run_execution_duration = 3
    result_assessment_order = ('xeyes','evince'),
    result_assessment_execution_duration = 3

*Please note the following general rules:*

* The sections **[environment]**, **[run]** and their according options (``run_order``, ``result_assessment_order``) are required
* At least **one** component (as in [component-1]) is required
* Additional components can be added by increasing the numbering (e.g. [component-**2**], [component-**3**], etc.)
* Do not use any quotes ("" or '') in component descriptions. Strings are separated using **comma**.
* Except for the ``criteria`` option, all inputs are removed of leading and trailing white spaces

Step by Step descriptions
-------------------------
In the following subsections, each section of the ``ini`` file notation is explained in detail. Please read these
carefully before creating an ``ini`` file to avoid errors in ``fsmt`` execution.

Step by Step: ENVIRONMENT
^^^^^^^^^^^^^^^^^^^^^^^^^

The description of environment variables is pretty straight forward. Simply add an ``option`` and value pair for each
environment variable you would like to be set when launching components::

    prefix = /usr/local/sbin/
    PATH = $PATH:/vol/robocup2013/bin/


..  note:: Previously set environment variables are respected by ``fsmt`` so 
		 that concatenation is possible (see second example). Therefore, 
		 you can explicitly decide what to define/overwrite in your 
		 **[environment]** configuration in your ``ini`` file. Please
		 consider that your project/team members maybe did not set 
		 variables or source setup files (e.g. ``/opt/ros/groovy/setup.bash``). 
		 Make sure you are as explicit as possible. 
			 
		 
Step by Step: COMPONENT
^^^^^^^^^^^^^^^^^^^^^^^

In the following, each ``option`` of a **[component-n]** section is separately 
listed and described in detail.

::

	name = xeyes
	
Describes the name of the component. This has to be used in the ``order`` option within the **run** section.
The name does not necessarily have to be the same as the command, you are free to choose.

::

	command = xeyes
	
The command, is the name of the actual executable of a component.

::

	path = /usr/bin/
	
Absolute path to the command, please append a trailing slash.

::

	path = $component_path   
    
You may instead also use environment variables (also those defined in the **[environment]** section)

::

	execution_host = localhost

The host on which the command will be run. 

.. note:: Important: This feature is **not yet supported** in FSMT but will be in
		future versions. Anyway, localhost is currently **required** for successful 
		``fsmt`` execution

::

	check_execution = True

Switch to toggle the use of all execution checks provided by ``fsmt``. Often, 
it doesn't make sense to disable checks, so we recommend to leave this 
setting to ``True``. If you set check_execution to ``False`` ``fsmt`` will run 
through each state not caring about whether a component has been started successfully or not


Step by Step: OBSERVERS
^^^^^^^^^^^^^^^^^^^^^^^

This section explains the observers that are used in order to monitor component execution. If the ``check_execution``
switch is set to "True", at least one observer has to be defined.

Currently, the following observers are available: ``pid``, ``lockfile``, ``stdout``, and ``stdoutexclude``.

* ``pid``: Checks for the existence of a process (using ``psutils``)
* ``lockfile``: Check for the existence of a *lockfile* in the file system (e.g. ``.spread`` file of spread deamon)
* ``stdout``: Checks whether a given string is found in the ``stdout`` of a component
* ``stdoutexclude``: Checks weather a string appears in the ``stdout`` of a component, if it finds the string, execution is
  aborted. For instance, you could search for ``error while starting robot``

A basic example::

    ``check_type = pid``

The criteria that is supposed to be satisfied is handled via the ``citeria`` 
option. This is especially important in case of a ``stdout``, or ``lockfile``
observer. Given this case, one has to provide either the string that is 
supposed to be found (e.g. ``criteria = FINDME``), or the absolute path to the 
lockfile that is supposed to be found (e.g. ``criteria = /some/path/.lock``). 
As the pid observer only checks for the existence of the PID,
**no critera** needs to be provided. Please keep in mind, no "" or '' are 
needed. In fact, the fsmt_iniparser will exit (warning) if you provide quotes 
or double quotes.

::

    criteria = 

The timeout defines the time (in seconds) until a certain success criteria has 
to be found. If the timeout is hit, the observer is regarded unsuccessful and ``fsmt`` execution is aborted.::

    timeout = 2

By using the blocking switch, one can force the state machine to completely 
halt further component execution until the observer is either successful or 
fails. Keep in mind, if you provide more than one observer per component, 
and one is blocking, execution is halted until the blocking observer returns.::

    blocking = True

The ongoing flag triggers the observer to repeatedly check for a certain 
criteria during the complete ``fsmt`` runtime. This is useful for observers 
such as the ``pid`` observer, because it enables to constantly check for the 
existence of the ``pid`` and will trigger an execution abort in case of a 
component crash. The ongoing procedure starts after the component has been
reported as "started successfully".::

    ongoing = False

.. note:: Currently, there is no ``restart-on-death`` option. This might be
		  implemented in future versions.

Step by Step: USING MULTIPLE OBSERVERS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to define multiple observers (even of the same type), by simply 
listing all elements in a **comma** separated list. It is important to note that 
even if no criteria are necessary, still a comma has to be put to allow correct 
parsing. You must configure the criteria ``column-wise``, so pid,stdout,stdout would be: ,something,something

::

    check_execution = True
    check_type = pid, stdout, stdout
    timeout = 2, 4, 20
    blocking = False, True, False
    ongoing = True, False, False
    criteria = ,Initialization complete, Late Initialization complete
    

Step by Step: RUN    
^^^^^^^^^^^^^^^^^

In the following, each option of the run section is separately listed and described in detail.

::

    [run]
    name = robot_test
    run_order = ('robot-navigation','navigation-logger'),
    run_execution_duration = 60
    result_assessment_order = ('aggregate-logs','gnuplut-logs'),
    result_assessment_execution_duration = 15


The name of your test, you are free to name it whatever you like::

    name = robot_test

The order of launching previously defined software components. 
(Detailed usage description is listed below)::

    run_order = ('robot-navigation','navigation-logger'),

Once the system is set up (i.e. the all components are running), the state 
machine execution halts for a defined amount of time (seconds), as set with the
``run_execution_duration`` option. As soon as the 
execution duration is over, components are stopped gently and the result 
assessment phase is entered::

    run_execution_duration = 60

Basically, the ``result_assessment_order`` option works as the ``run_order`` 
option, but this time for the result assessment phase where you might launch 
your post-processing components, e.g., assess log files, or compute graphs::

    result_assessment_order = ('aggregate-logs','gnuplut-logs'),

Lastly, ``result_assessment_execution_duration`` works idetical th the 
``execution_duration`` option but for the result assessment phase::

    result_assessment_execution_duration = 15

.. note:: The trailing comma is **needed** in ``run_order`` and ``result_assessment_order``


More on RUN ORDERS
""""""""""""""""""

The way how and when individual components are launched is determined by the 
``order`` option in the **run** section. Simply listing the names (in single 
quotes) of the components in a comma separated list represents the order of 
execution.

Used control mechanism are:

* Round brackets (i.e. '()') are used to describe components that are supposed to be launched **sequentially**
* Square brackets (i.e '[]') hold elements which are executed in **parallel**

.. note:: It is important that single elements in square brackets 
	  (parallel execution) have to be inside a round bracket 'tuple'
	  (which means they need to have round brackets and a trailing ",").


For example::

	A) ('robot','logger'),
	B) [('robot',),('logger',)],

In the above example A will launch robot, then logger. B will launch robot and 
logger in parallel. Again, please note the positions of commas.

The mentioned control mechanisms can be nested as desired. However we recommend
to keep your run order as simple as possible with only few 1 or 2 level nesting.

A nested example could be::

    run_order = ('robot',),[('goal_setter',),('goal_logger',)],

This will first launch ``robot``, and then the ``goal_setter`` and ``goal_logger`` 
in parallel, allowing to log all output of the ``goal_setter``

Or::

    run_order = ('robot',),[('goal_logger','goal_setter',),('task_logger','task_setter',),],

This will first launch ``robot``, and then in parallel
 
* ``goal_logger`` and ``goal_setter`` sequentially, as well as 
* ``task_logger`` and ``task_setter`` sequentially.