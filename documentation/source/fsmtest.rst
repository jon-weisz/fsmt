fsmtest Package
===============

This part represents the API-DOC of ``fsmt``. Unfortunately, ``sphinx-apidoc``
is not yet integrated in ``setuptools`` and therefore, this was created by hand. 
Once ``sphinx-apidoc`` is included in setuptools, use the following line 
in the conf.py of sphinx to add the path

::

   sys.path.insert(0, os.path.abspath('.') + '/../../fsmtest')

Then teh API-DOC will be autogeneratable. Otherwise, for now *create* API-DOC by hand via:

::

   $ sphinx-apidoc -F -o /tmp/docc fsmtest
   
and add the auto created *.rst files from /tmp/docc into the project documentation
source folder. After that you only have to reference the fsmtest.rst in the index.rst!

.. note:: ALSO USE THESE STEPS FOR UPDATING THE API-DOC!!

:mod:`fsmtest` Package
----------------------

.. automodule:: fsmtest.__init__
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`exit_watcher` Module
--------------------------

.. automodule:: fsmtest.exit_watcher
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`launcher` Module
----------------------

.. automodule:: fsmtest.launcher
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`log_factory` Module
-------------------------

.. automodule:: fsmtest.log_factory
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`process_communicator` Module
----------------------------------

.. automodule:: fsmtest.process_communicator
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`process_executor` Module
------------------------------

.. automodule:: fsmtest.process_executor
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`pty_log_writer` Module
----------------------------

.. automodule:: fsmtest.pty_log_writer
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`resource_centre` Module
-----------------------------

.. automodule:: fsmtest.resource_centre
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`scxml_helper` Module
--------------------------

.. automodule:: fsmtest.scxml_helper
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`state_machine_wrapper` Module
-----------------------------------

.. automodule:: fsmtest.state_machine_wrapper
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`utils` Module
-------------------

.. automodule:: fsmtest.utils
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`web_socket_utils` Module
------------------------------

.. automodule:: fsmtest.web_socket_utils
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`xunit_xml_builder` Module
-------------------------------

.. automodule:: fsmtest.xunit_xml_builder
    :members:
    :undoc-members:
    :show-inheritance:

Subpackages
-----------

.. toctree::

    fsmtest.containers
    fsmtest.exceptions
    fsmtest.processobservation

