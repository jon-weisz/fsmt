Installation
===============


General Build Information
--------------------------------------
In order to use ``fsmt`` you require:

* **Python 2.7.x** (Python 3.x is **not** supported)
* **setuptools** for Python

Install setuptools if not yet installed::

    $ sudo apt-get install python-setuptools


In general, these are all the steps required to install ``fsmt``. You might
change the installation prefix to any prefix you want. For anything below "/"
(root) you will obviously need **root** permissions for installation. For
**/home/$USER** (see below) you can omit the sudo command, but you will have
to change the paths accordingly.

So, if you for example want to install into a sandbox in ``~/sandbox/``, 
you have to do::

   $ mkdir -p ~/sandbox/lib/python2.7/site-packages/ && cd ~/sandbox/
   $ mkdir -p src/fsmt && cd src/fsmt
   $ git clone https://openresearch.cit-ec.de/git/fsmt.git .
   $ export PYTHONPATH=~/sandbox/lib/python2.7/site-packages/:$PYTHONPATH
   $ export PATH=~/sandbox/bin:$PATH
   $ python setup.py install --prefix=~/sandbox --record installed_files.txt

You can check the installed requirements in the setup.py, they are automatically 
installed via setuptools. However, it is noteworthy that PySCXML is **required**.
You nned to install it separately from GIT::

    $ cd ~/sandbox/src
    $ mkdir pyscxml && cd pyscxml
    $ git clone https://github.com/jroxendal/PySCXML.git .
    $ export PYTHONPATH=~/sandbox/python2.7/site-packages:$PYTHONPATH
    $ python setup.py install --prefix=~/sandbox/


Once everything is installed and your environment variables ``PYTHONPATH`` and 
``PATH`` are set, you can easily call ``fsmt`` with a configuration file. For 
example, you can call a standard test from the sources::
    
    $ fsmt ~/sandbox/src/fsmt/configuration/std/stdtools.scxml

.. note:: There are several tools alongside ``fsmt``. Please see :doc:`tools` 
		  for details. 


Build the documentation
------------------------

Actually, build **this** documentation::

    $ cd ~/FSMtesting/src/fsmtest
    $ python setup.py build_sphinx

You can then find the documentation at::

    ~/FSMtesting/fsmt/documentation/build/


ROS based examples
---------------------

In order to use ROS based examples, please install ROS first::

   $ sudo apt-get install ros-groovy-desktop-full ros-groovy-pr2-common ros-groovy-pr2-mechanism-msgs \
   ros-groovy-pr2-controllers ros-groovy-rxtools
