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

import os
import select
import eventlet
from fsmtest.log_factory import LogFactory


class PTYLogWriter():
    eventlet.monkey_patch()

    def __init__(self, name):
        """
        :param name:
        """
        self.name = name
        self.process = None
        self.is_setup = False
        self.logfile = None
        self.un_poll_able = False
        self.log_file_name = None
        self.log = LogFactory().get_logger()
        self.terminate = False

    def close_logger(self):
        """
        :param _close:
        """
        self.terminate = True

    def setup(self, _process, _logfile):
        """
        :param _process:
        :param _logfile:
        """
        self.process = _process
        self.log_file_name = _logfile
        self.is_setup = True

    def logger(self):
        """
        TODO
        """
        if self.is_setup:
            try:
                a_file = open(self.log_file_name, "w+")
                self.logfile = a_file
            except IOError as e:
                self.log.error("Exception in log file reader of %s, cannot read the file %s", self.name,
                               self.log_file_name)
                a_file.close()
                return 1

            self.log.info("%s log %s", self.name, self.log_file_name)

            try:
                # Log while the process is alive, if not, stop logging.
                while self.process.poll() is None:
                    # Checks if there is any data on the pty
                    ready, _, _ = select.select([self.process.master], [], [], 0.1)
                    if ready:
                        # This line actually reads from the pty
                        data = os.read(self.process.master, 512)
                        if not data:
                            continue
                        # So here was repr(data), from what i read this is not
                        # really necessary here. So I changed it to str()
                        # as repr() created silly single quotes around the
                        # returned string. --nkoester
                        a_file.write(str(data))
                        a_file.flush()
                        self.log.stream("%s Writing to log >> %s", self.name, str(data))

                    elif self.process.poll() is not None:
                        self.log.info("%s Became un-pollable (exited) while reading...OK.", self.name)
                        self.un_poll_able = True
                        a_file.close()
                        return 0
                    if self.terminate:
                        break
                    # Reduce CPU Load
                    eventlet.sleep(0.008)

            except IOError as e:
                self.log.error("Exception in log file reader of %s, probably the process pipe is dead? %s", self.name,
                               format(e.errno, e.strerror))
                a_file.close()
                return 1

            except RuntimeError as e:
                self.log.error("ERROR: In log file reader of %s is %s", (self.name, e))
                a_file.close()
                return 1

            if self.un_poll_able:
                self.log.error("ERROR: Process %s is un-pollable - Exiting", self.name)
                a_file.close()
                return 1

            if self.terminate:
                self.log.debug("%s Internal terminate flag set - Exiting & Returning 0!", self.name)
                a_file.close()
                return 0

        else:
            self.log.error("%s ERROR: Log writer has not been setup properly!", self.name)
            return 1
