"""

This file is part of FINITE STATE MACHINE BASED TESTING.

Copyright(c) <Florian Lier, Norman Koester>
http://opensource.cit-ec.de/fsmt

This file may be licensed under the terms of the
GNU Lesser General Public License Version 3 (the ``LGPL''),
or (at your option) any later version.

Software distributed under the License is distributed
on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
express or implied. See the LGPL for the specific language
governing rights and limitations.

You should have received a copy of the LGPL along with this
program. If not, go to http://www.gnu.org/licenses/lgpl.html
or write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

The development of this software was supported by the
Excellence Cluster EXC 277 Cognitive Interaction Technology.
The Excellence Cluster EXC 277 is a grant of the Deutsche
Forschungsgemeinschaft (DFG) in the context of the German
Excellence Initiative.

Authors: Florian Lier, Norman Koester
<flier, nkoester>@techfak.uni-bielefeld.de

"""

import subprocess
from setuptools import setup, find_packages

version = "master"
filename = "master"

setup(name="fsmtest",

      version=filename,

      description="A generic and configurable state machine based process to support automated system testing on a "
                  "functional level",

      long_description="This framework introduces a generic and configurable state machine based process: Finite "
                       "State Machine" +
                       "Testing to automate environment setup, system bootstrapping, functional system tests, "
                       "result assessment," +
                       "exit and clean-up strategy.",

      author="Florian Lier and Norman Koester",

      author_email="flier[at]techfak.uni-bielefeld.de and nkoester[at]techfak.uni-bielefeld.de",

      url="http://opensource.cit-ec.de/projects/fsmt",

      download_url="http://opensource.cit-ec.de/projects/fsmt",

      packages=find_packages(exclude=["*.tests",
                                      "*.tests.*",
                                      "tests.*",
                                      "tests"]),

      scripts=["bin/fsmt", "bin/fsmt_iniparser"],

      package_data={'fsmtest': ['configuration/*']},

      include_package_data=True,

      keywords=['Testing', 'Test', 'System Testing',
                'Component Based Testing', 'Simulation Testing',
                'Software Tests'],

      license="LGPLv3",

      classifiers=[
          'Development Status :: Beta',
          'Environment :: Console',
          'Environment :: Robotics',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Library or ' +
          'Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Text Processing :: Markup :: XML'
      ],

      install_requires=['Louie', 'termcolor', 'eventlet', 'suds',
                        'restlib', 'lxml', 'nose==1.2.1', 'coverage',
                        'nosexcover', 'pylint', 'setuptools-lint',
                        'psutil', 'websocket-client', 'paramiko',
                        'setuptools-pep8'])

# Make scripts executable
subprocess.call(["chmod -R ugo+x bin"], shell=True)
