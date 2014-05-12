'''

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

'''

from fsmtest.processobservation.process_observer import ProcessObserver
import subprocess
import time
import os


class ScreenpidObserver(ProcessObserver):
    # TODO: Check Implementation

    def __init__(self, process_executer, parent_pipe,
                 check_type, process_exchange_data, state_machine):
        """
        :param process_executer:
        :param parent_pipe:
        :param check_type:
        :param process_exchange_data:
        """
        ProcessObserver.__init__(
            self, process_executer, parent_pipe, check_type,
            process_exchange_data, state_machine)
        self.end_thread = False
        self.internalOK = False
        self.foundPID = -1

    def run(self):
        """
        :return:
        """
        '''
        self.log_start()
        t0 = time.time()
        # Work within the time frame or until we are told to stop/end
        # the thread
        while ((time.time() - t0) < self.check_type.timeout) and \
            not self.end_thread:
            # Reduce CPU load a little ;)
            time.sleep(0.001)
            # The negative approach: assume the program is dead initially
            # every run and adjust if not
            self.internalOK = False
            # Command magic to find pid of software started via vdemo
            #in a screen session
            pid_find_string = \
                "screen -ls | awk '/\.%s\\t/ {print strtonum($1)}'"
            # Finding and replacing according to the vdemo syntax
            checkCommand = (self.pe.software_component.path +
                self.pe.software_component.command).\
                replace("-l", "").replace(" start", "").strip()
            if checkCommand.rfind("component_") >= 0:
                checkCommand =
                    checkCommand[checkCommand.rfind("component_") + 10:] + "_"
            # Run the command
            p = subprocess.Popen("exec " + pid_find_string % checkCommand,
                             shell = True,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.STDOUT,
                             executable = '/bin/bash',
                             env = self.pe.environment_map)
            p.wait()
            lineOutput = (p.stdout.readlines())
            # If we get more PIDs than one, then something is fishy... oO
            if len(lineOutput) == 1:
                # And if the element itself in the list is empty ... well,
                # then we didnt find the PID...
                if lineOutput[0] != "":
                    # Extract the pid
                    self.foundPID = lineOutput[0].strip().replace("\n", "")
                    # Is the PID dead?
                    if not os.path.exists("/proc/%s" % self.foundPID):
                        self.internalOK = False
                        if not self.check_type.ongoing:
                            self.log_failure("PID (%s) not found. Process "+
                            "%s is dead." %
                            (self.foundPID, self.pe.software_component.name))
                            self.send_negative_result_to_pyscxml()
                            return
                        else:
                            time.sleep(0.001)
                    # No? good!
                    else:
                        # Remember the update
                        self.process_exchange_data.pid = self.foundPID
                        self.internalOK = True
                        # We want to end the thread only if we just look for
                        # the PID once
                        if not self.check_type.ongoing:
                            self.log_success("PID (%s) was found in /proc/" % \
                                self.foundPID)
                            self.send_positive_result_to_pyscxml()
                            return
                        else:
                            # The pid is still alive... lets just check in .1
                            # seconds again - that'll do...
                            time.sleep(.1)
        # Are we ongoing and did we find the PID all the time?
        if self.check_type.ongoing:
            if self.internalOK:
                self.log_success(
                    "PID (%s) was found in /proc/ (ongoing-mode)." % \
                    self.foundPID)
                self.send_positive_result_to_pyscxml()
            else:
                self.log_failure("No internal OK found (==PID not found). "+
                    "Process %s is dead (ongoing-mode)." % \
                    self.pe.software_component.name)
                self.send_negative_result_to_pyscxml()
        # Not ongoing, means timeout was hit
        else:
            self.log_failure("Timeout hit (==PID not found). "+
                "Process %s is dead." % self.pe.software_component.name)
            self.send_negative_result_to_pyscxml()
        '''
        self.log.warning("Currently not implemented")
