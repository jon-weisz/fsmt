Installation
===============


General Build Information
--------------------------------------
In order to use ``fsmt`` you require:

* **Python 2.7.x** (python 3.x will **not** work)
* **setuptools** for python

First, you have to get the `fsmt` sourcecode::
	
	$ mkdir ~/FSMtesting/fsmt && cd ~/FSMtesting/fsmt
	$ git clone https://openresearch.cit-ec.de/git/fsmt.git .
	$ python setup.py setup.py install

Generally, these are all the steps required to install ``fsmt``. You might 
change the installation prefix to any prefix you want. For 
anything below "/" (root) you will obviously need **sudo** for installation. 
For **/home/$USER** you can omit the sudo command, but you will have to
change the paths accordingly.

So, if you for example want to install into a sandbox in ``/vol/sandbox/``, 
you have to do::

   $ sudo mkdir -p /vol/sandbox/fsmt/lib/python2.7/site-packages/
   $ export PYTHONPATH=/vol/sandbox/fsmt/lib/python2.7/site-packages/:$PYTHONPATH
   $ export PATH=/vol/sandbox/fsmt/bin:$PATH
   $ python setup.py install --prefix=/vol/sandbox/fsmt/ --record installed_files.txt

You can check the installed requirements in the setup.py, they are automatically 
installed via setuptools. However, it is noteworthy that PySCXML is required. 
If you want to install it separately::

    $ git clone https://github.com/jroxendal/PySCXML.git
    $ cd PySCXML
    $ export PYTHONPATH=/vol/sandbox/fsmt/python2.7/site-packages:$PYTHONPATH
    $ python setup.py install --prefix=/vol/sandbox/fsmt/


Once everything is installed and your environment variables ``PYTHONPATH`` and 
``PATH`` are set, you can easily call ``fsmt`` with a configuration file. For 
example, you can call a standard test from the sources::
    
    $ fsmt ~/FSMtesting/fsmt/configuration/std/stdtools.scxml

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
