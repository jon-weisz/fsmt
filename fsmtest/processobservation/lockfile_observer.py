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

from fsmtest.processobservation.process_observer import ProcessObserver
import os
import time


class LockfileObserver(ProcessObserver):

    def __init__(self, process_executer, parent_pipe, check_type,
                 process_exchange_data, state_machine):
        """
        :param process_executer:
        :param parent_pipe:
        :param check_type:
        :param process_exchange_data:
        """
        ProcessObserver.__init__(
            self, process_executer, parent_pipe, check_type,
            process_exchange_data, state_machine)

    def run(self):
        """
        TODO
        """
        component_name = self.process_executer.software_component.name
        self.file_was_found = False
        self.log_start()
        t0 = time.time()
        while ((time.time() - t0) < self.check_type.timeout) and \
                not self.end_thread:
            # Reduce CPU load a little ;)
            time.sleep(0.005)
            if os.path.exists(self.check_type.criteria):
                self.log_success()
                self.send_positive_result_to_pyscxml()
                self.log.info("Lock file found for %s at %s" %
                              (component_name, self.check_type.criteria))
                self.end_thread = True
                self.file_was_found = True

        if not self.file_was_found:
                self.log_failure(("No lock file was found for %s at %s!" +
                                  " Aborting!") %
                                 (component_name, self.check_type.criteria))
                self.send_negative_result_to_pyscxml()
                return 1
        else:
            if self.check_type.ongoing:
                self.log.warning("Currently not implemented")
                self.end_thread = True
                return 0

        return 1
