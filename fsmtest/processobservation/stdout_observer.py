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

from fsmtest.utils import seek_read
from fsmtest.processobservation.process_observer import ProcessObserver
import sys
import time


class StdoutObserver(ProcessObserver):
    """
    Observer Class which allows to search for a certain string within the
    output of a process.
    """

    def __init__(self, process_executer, parent_pipe, check_type, process_exchange_data, state_machine):
        """
        :param process_executer:
        :param parent_pipe:
        :param check_type:
        :param process_exchange_data:
        """
        ProcessObserver.__init__(self, process_executer, parent_pipe, check_type, process_exchange_data, state_machine)

    def run(self):
        """
        :return:
        """
        name = self.get_my_name()
        criteria = self.check_type.criteria
        self.log_start()
        if self.check_type.criteria == "":
            # No instructions for success criteria given
            # Assuming execution just works fine ... :/
            self.send_positive_result_to_pyscxml()
            self.log_scuccess("No criteria given")
            self.end_thread = True
            return 0
        t0 = time.time()
        file_position = 0
        been_read = 0
        # Open file as READ ONLY
        log_file = open(self.process_executer.log_file_name, mode="r")
        while (time.time() - t0) < self.check_type.timeout and not self.end_thread:
            self.hit_timeout = True
            try:
                log_lines = seek_read(log_file, file_position)
                been_read = len(log_lines)
            except ValueError, e:
                log_lines = "IOERROR in line %s" % str(sys.exc_traceback.tb_lineno)
            if log_lines != "" and log_lines != "\n" and been_read != 0:
                self.log.stream("%s: Reads from log < %s", name, log_lines)
                if self.check_type.criteria in log_lines:
                    self.log_success("'%s' was found in STDOUT within %.2fms" % (
                    self.check_type.criteria, (time.time() - t0) * 1000))
                    self.send_positive_result_to_pyscxml()
                    self.end_thread = True
                    self.hit_timeout = False
                    break
                if "IOERROR" in log_lines:
                    self.log_failure("IO Error in %s" % log_lines)
                    self.send_negative_result_to_pyscxml()
                    self.end_thread = True
                    break
            file_position += been_read
            # Reduce CPU load
            time.sleep(0.005)

        # Close the file again
        log_file.close()

        if self.hit_timeout:
            if (time.time() - t0) < self.check_type.timeout:
                self.log_cancel("Exited _BEFORE_ criteria was found _OR_ timeout was reached")
                self.log.debug("Exiting STDOUT observer")
                self.end_thread = True
                return 1
            else:
                self.log_failure("Hit timeout after %ds while searching for '%s'" % (self.check_type.timeout, criteria))
                self.send_negative_result_to_pyscxml()
                self.log.debug("Exiting STDOUT observer")
                self.end_thread = True
                return 1

        if self.check_type.ongoing:
            self.log.warning("Ongoing STDOUT observer defined")
        return 0
