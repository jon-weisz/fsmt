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
import subprocess
import os.path
import time
import sys


class PidObserver(ProcessObserver):
    def __init__(self, process_executer, parent_pipe, check_type, process_exchange_data, state_machine_):
        """
        :param process_executer:
        :param parent_pipe:
        :param check_type:
        :param process_exchange_data:
        """
        ProcessObserver.__init__(self, process_executer, parent_pipe, check_type, process_exchange_data, state_machine_)

    def run(self):
        the_pid = self.process_executer.subprocess_pid
        self.log_start()

        t0 = time.time()
        while (time.time() - t0) < self.check_type.timeout and not self.end_thread:
            # Reduce CPU load a little, give it 1ms for scheduling ;)
            self.internalOK = False
            if not hasattr(self.proc_exec_subprocess, "pid"):
                # If there is no PID before observation, something is horribly
                # wrong, so exit observation
                self.log_failure("No PID found on initialisation. NOT starting observation")
                self.send_negative_result_to_pyscxml()
                self.internalOK = False
                self.end_thread = True
                return 1
                # OS check, currently we decide between MAC OSX and Linux/Unix
            if sys.platform == 'darwin':
                # TODO USE PSUTILS
                cmd = ['ps', '-ef', '%s' % the_pid]
                darwin_pid = subprocess.Popen(
                    cmd, bufsize=-1, stdout=subprocess.PIPE)
                out, err = darwin_pid.communicate()
                # MAC OSX: If process is not found, new while loop, if found
                # break the loop
                if str(self.process_executer.subprocess_pid) not in out:
                    self.internalOK = False
                else:
                    self.internalOK = True
                    self.end_thread = True
                    # We found the PID set this while to "end", and go on!
                    break
            else:
                # LINUX/UNIX: If process is not found, new while loop, if found
                # break the loop
                if not os.path.exists("/proc/%s" % the_pid):
                    self.internalOK = False
                else:
                    self.internalOK = True
                    self.end_thread = True
                    # We found the PID, go on!
                    break
            time.sleep(0.001)

        # At this point we either came here because of a "break", or the time is up.
        if self.internalOK:
            self.send_positive_result_to_pyscxml()
            t = time.time()
            self.log_success("PID was found in %sms" % str(((t - t0) * 1000))[:4])
        else:
            t = time.time()
            self.log_failure("PID was not found")
            self.send_negative_result_to_pyscxml()
            self.end_thread = True
            # This is the point of "no return" after this we will check for
            # ongoing mode, which means we mustn't exit earlier than this
            return 1

        if self.check_type.ongoing:
            while not self.stop_ongoing:
                time.sleep(0.010)
                if sys.platform == 'darwin':
                    # TODO USE PSUTILS
                    cmd = ['ps', '-ef', '%s' % the_pid]
                    darwin_pid = subprocess.Popen(
                        cmd, bufsize=-1, stdout=subprocess.PIPE)
                    out, err = darwin_pid.communicate()
                    # MAC OSX: If process is not found, new while loop, if
                    # found break the loop
                    if str(the_pid) not in out:
                        self.log_failure("PID disappeared!")
                        self.send_negative_result_to_pyscxml()
                        self.stop_ongoing = True
                        return 1
                    else:
                        pass
                else:
                    # LINUX/UNIX: If process is not found, new while loop, if
                    # found break the loop
                    if not os.path.exists("/proc/%s" % the_pid):
                        self.log_failure("PID disappeared!")
                        self.send_negative_result_to_pyscxml()
                        self.stop_ongoing = True
                        return 1
                    else:
                        pass
        # If not ongoing, and we haven't exited yet, we can safely return
        self.log.debug("Exiting PID observer")
        self.end_thread = True
        return 0
