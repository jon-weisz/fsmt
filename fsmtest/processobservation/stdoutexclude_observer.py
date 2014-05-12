'''

This file is part of FINITE STATE MACHINE BASED TESTING.

Copyright(c) <Florian Lier, Norman Köster>
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

Authors: Florian Lier, Norman Köster
<flier, nkoester>@techfak.uni-bielefeld.de

'''

from fsmtest.processobservation.process_observer import ProcessObserver
from fsmtest.utils import seek_read
import time


class StdoutexcludeObserver(ProcessObserver):

    """
    Observer Class which allows to search for a certain string within
    the output of a process.
    """

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
        name = self.get_my_name()
        component_name = self.process_executer.software_component.name
        criteria = self.check_type.criteria
        self.log_start()
        if self.check_type.criteria == "":
            # No string for success criteria given.
            # Assuming execution just works fine... :/
            self.send_positive_result_to_pyscxml()
            self.log_success()
            self.log.info(
                "Exiting STDOUTEXCLUDE observer for %s, no criteria given",
                component_name)
            self.end_thread = True
            return 0
        t0 = time.time()
        self.success = False
        file_pos = 0
        been_read = 0
        # Open file as READ ONLY
        log_file = open(self.process_executer.log_file_name, mode="r")
        while ((time.time() - t0) < self.check_type.timeout) and \
                not self.end_thread:
            # Reduce CPU load a little ;)
            time.sleep(0.05)
            self.hit_timeout = True
            self.success = True
            try:
                # Get the last 20 lines of the logfile
                log_lines = seek_read(log_file, file_pos)
                been_read = len(log_lines)
            except ValueError, e:
                log_lines = "IOERROR"
            if log_lines != "" and log_lines != "\n" and been_read != 0:
                self.log.stream("%s: Reads from log << %s", name, log_lines)
                if "IOERROR" in log_lines:
                    self.log.error("IO Error in component %s output",
                                   component_name)
                    self.send_negative_result_to_pyscxml()
                    self.end_thread = True
                    log_file.close()
                    return 1
                if self.check_type.criteria in log_lines:
                    t = time.time()
                    self.log.warning(
                        "%s: '%s' was found in STDOUTEXCLUDE within %s s ",
                        name, criteria, t - t0)
                    self.success = False
                    self.send_negative_result_to_pyscxml()
                    self.log.debug("Exiting STDOUTEXCLUDE observer for %s",
                                   component_name)
                    self.end_thread = True
                    self.hit_timeout = False
                    log_file.close()
                    return 1
            file_pos += been_read
            # print "ExcludeOB read: %d %s" % (file_pos, component_name)

        if self.hit_timeout:
            if (time.time() - t0) < self.check_type.timeout:
                self.log_cancel("'%s' timeout not reached. Bad!" %
                                self.check_type.timeout)
                self.log.debug("Exiting STDOUTEXCLUDE observer for %s",
                               component_name)
                self.end_thread = True
                log_file.close()
                return 1
            else:
                self.log_success(
                    "Hit timeout (%ds) while looking for '%s'.Good!" %
                    (self.check_type.timeout, criteria))
                self.send_positive_result_to_pyscxml()
                self.end_thread = True
        if self.check_type.ongoing:
            while not self.stop_ongoing:
                # Reduce the CPU load a little
                time.sleep(0.1)
                try:
                    # Get the last 20 lines of the logfile
                    log_lines = seek_read(log_file, file_pos)
                    been_read = len(log_lines)
                # DIRRRRTYY!!!@flier TODO
                except ValueError, e:
                    log_lines = "IOERROR"
                if log_lines != "" and log_lines != "\n" and been_read != 0:
                    self.log.stream("%s: Reads from log << %s",
                                    name, log_lines)
                    if "IOERROR" in log_lines:
                        self.log.error("IO Error in component %s output",
                                       component_name)
                        self.send_negative_result_to_pyscxml()
                        self.end_thread = True
                        log_file.close()
                        return 1
                    if self.check_type.criteria in log_lines:
                        t = time.time()
                        self.log.warning(
                            "%s: '%s' was found in STDOUTEXCLUDE within %s s ",
                            name, criteria, t - t0)
                        self.success = False
                        self.send_negative_result_to_pyscxml()
                        self.log.debug(
                            "Exiting STDOUTEXCLUDE observer for %s",
                            component_name)
                        self.end_thread = True
                        self.hit_timeout = False
                        log_file.close()
                        return 1
                file_pos += been_read
        log_file.close()
        return 0
