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
import select
import time
import os


class ScreenstdoutObserver(ProcessObserver):

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

    # TODO: Check Implementation
    def run(self):
        """
        :return:
        """
        """
        self.log_start()
        print "screen_stdout case"
        self.log.error(
            "The observer type %s is not yet fully supported and" + \
            " therefore not usable." % self.check_type.type)
        self.send_negative_result_to_pyscxml()
        return
        t0 = time.time()
        while ((time.time() - t0) < self.check_type.timeout) and \
            not self.end_thread:
            # Reduce CPU load a little ;)
            time.sleep(0.001)
            self.hit_timeout = True
            self.unpollable = True
            ready, _, _ = select.select([self.pe.p.master], [], [], .04)
            if ready:
                # This line actually reads from the pty
                data = os.read(self.pe.p.master, 1024)
                if not data:
                    break
                lines = repr(data).split('\\n')
                for aLine in [i.strip().replace('\\r', '').replace("\\n", "")
                    for i in lines]:
                    if aLine != "" and aLine != "\n":
                        self.log.debug("%s: Reads from log: %s",
                            (self.get_my_name(), aLine))

                        if self.check_type.criteria in aLine:
                            self.log.info(
                                "%s: '%s' was found in STDOUT (within %.4fs).",
                                (self.get_my_name(),
                                self.check_type.criteria,
                                time.time() - t0))
                            self.send_positive_result_to_pyscxml()
                            return
            elif self.pe.p.poll() is not None:  # Select timeout
                self.hit_timeout = False
                self.unpollable = True
                break
        if self.hit_timeout:
            self.log_failure(
                "%s: Hit timeout (%ds) while searching for '%s'!" % (
                self.get_my_name(),
                self.check_type.timeout,
                self.check_type.criteria)
                )
                self.send_negative_result_to_pyscxml()
        elif self.unpollable:
            self.log_failure("%s: Process became un-pollable while searching" +
                " for '%s'!" % (
                self.get_my_name(), self.check_type.criteria))
            self.send_negative_result_to_pyscxml()
        """
        self.log.warning("Currently not implemented")
