Installation
===============


General Build Information
--------------------------
In order to use ``fsmt`` you require:

* **Python 2.7.x** (Python 3.x is **not** supported)
* **setuptools** for Python

Install setuptools if not yet installed::

    $ sudo apt-get install python-setuptools python-sphinx


In general, these are allsteps required to install ``fsmt``. You might
change the installation prefix to any prefix you want. For anything below "/"
you will, obviously, need **root** permissions for installation. For
**/home/$USER** (see below) you can omit the *sudo* command, but you will have
to change the (python) paths accordingly.


FSMT
----

So, if you for example want to install into a sandbox in ``~/sandbox/``, 
you have to do::

   $ mkdir -p ~/sandbox/lib/python2.7/site-packages/ && cd ~/sandbox/
   $ mkdir -p src/fsmt && cd src/fsmt
   $ git clone https://openresearch.cit-ec.de/git/fsmt.git .
   $ export PYTHONPATH=~/sandbox/lib/python2.7/site-packages/:$PYTHONPATH
   $ export PATH=~/sandbox/bin:$PATH
   $ python setup.py install --prefix=~/sandbox --record installed_files.txt


PySCXML
-------

You can check the installed requirements in the setup.py, they are automatically
installed via setuptools. However, it is noteworthy that PySCXML is **required**.
You need to install it separately from GIT::

    $ cd ~/sandbox/src
    $ mkdir pyscxml && cd pyscxml
    $ git clone https://github.com/warp1337/PySCXML.git .
    $ export PYTHONPATH=~/sandbox/python2.7/site-packages:$PYTHONPATH
    $ python setup.py install --prefix=~/sandbox/


Quickstart
-----------

Once everything is installed and your environment variables ``PYTHONPATH`` and
``PATH`` are set, you can easily call ``fsmt`` with a configuration file. For 
example, you can call a standard test from the sources::

    $ sudo apt-get install x11-apps evince

    $ fsmt ~/sandbox/src/fsmt/configuration/std/stdtools.scxml

.. note:: There are several tools alongside ``fsmt``. Please see :doc:`tools` 
		  for details.


Build the Documentation
------------------------

Actually, build **this** documentation::

    $ cd ~/sandbox/src/fsmt
    $ python setup.py build_sphinx

You can then find the documentation at::

    ~/sandbox/src/fsmt/documentation/build/


ROS Based Examples
---------------------

In order to use ROS based examples, please install ROS first::

   $ sudo apt-get install ros-indigo-desktop-full ros-indigo-pr2-common ros-indigo-pr2-mechanism-msgs ros-indigo-pr2-controllers ros-indigo-rxtools
