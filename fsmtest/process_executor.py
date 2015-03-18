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
import pty
import time
import select
import eventlet
import itertools
import subprocess

from fsmtest.log_factory import LogFactory
from fsmtest.pty_log_writer import PTYLogWriter
from fsmtest.processobservation.pid_observer import PidObserver
from fsmtest.processobservation.stdout_observer import StdoutObserver
from fsmtest.processobservation.process_observer import ProcessObserver
from fsmtest.containers.process_exchange_data import ProcessExchangeData
from fsmtest.processobservation.lockfile_observer import LockfileObserver
from fsmtest.processobservation.screenpid_observer import ScreenpidObserver
from fsmtest.processobservation.screenstdout_observer import ScreenstdoutObserver
from fsmtest.processobservation.stdoutexclude_observer import StdoutexcludeObserver


class ProcessExecutor():

    # Evil. See: http://eventlet.net/doc/basic_usage.html#eventlet.monkey_patch
    eventlet.monkey_patch()

    def __init__(self, process_pipe_, software_component_, environment_map_, log_folder_, init_time_, state_machine_):
        """
        TODO
        :type  software_component: object
        :param process_pipe:
        :param software_component:
        :param environment_map:
        :param log_folder:
        """
        self.subprocess = None
        self.logger_runner = None
        self.pty_log_writer = None
        self.log_file_name = None
        self.pty_log_runner = None
        self.init_time = init_time_
        self.process_observers = []
        self.component_runner = None
        self.subprocess_pid = "None"
        self.log_folder = log_folder_
        self.parent_pipe = process_pipe_
        self.state_machine = state_machine_
        self.blocking_process_observers = []
        self.log = LogFactory().get_logger()
        self.environment_map = environment_map_
        self.software_component = software_component_

        self.log.debug("Program Executor initialisation for %s", self.software_component.name)

        for check_type_ in self.software_component.check_types:

            process_exchange_data = ProcessExchangeData()
            class_to_call = check_type_.type.strip().lower().capitalize() + "Observer"

            self.log.debug("Found observer type: %s", class_to_call)

            process_exchange_data.message = self.software_component.name
            process_exchange_data.counter_name = self.software_component.counter_name
            process_exchange_data.execution_type = self.software_component.execution_type
            process_exchange_data.parent_state = self.software_component.parent_state
            process_exchange_data.sender_id = check_type_.id
            process_exchange_data.type = check_type_.type

            try:
                constructor = globals()[class_to_call]
                new_observer = constructor(self, self.parent_pipe, check_type_, process_exchange_data, state_machine_)
            except Exception, e:
                self.log.critical("Class {0:s} could not be found. {1:s}".format(check_type_.type + "Observer", e))
            if check_type_.blocking:
                self.blocking_process_observers.append(new_observer)
            else:
                self.process_observers.append(new_observer)

        self.log_file_name = self.log_folder + "/" + self.software_component.name + ".log"
        self.pty_log_writer = PTYLogWriter(self.software_component.name)
        self.component_runner = eventlet.spawn(self.component_runner_function)

    def component_runner_function(self):
        """
        Runner. This method invokes a component.
        """

        # If we are on 'localhost' we use the native/faster approach of spawning local processes and logging in/out
        # streams
        if self.software_component.host == "localhost":

            # Open a PTY for reading and writing to logfile
            master, slave = pty.openpty()

            # Execute the command
            self.subprocess = subprocess.Popen(
                "exec " + self.software_component.get_complete_executable_path_with_arguments(),
                shell=True, stdin=slave, stdout=slave, stderr=slave,
                bufsize=8192, executable='/bin/bash', env=self.environment_map)

            self.subprocess.master = master
            self.subprocess.slave = slave

            self.pty_log_writer.setup(self.subprocess, self.log_file_name)
            self.pty_log_runner = eventlet.spawn(self.pty_log_writer.logger)

            # Remember its PID, the PID is a member of the POpen class
            self.subprocess_pid = self.subprocess.pid
            self.software_component.pid = str(self.subprocess_pid)

            the_time = time.time()

            self.log.info(
                ("\x1b[94m--> Launching " + "%s [%s] %sms since FSMT init"),
                self.software_component.name,
                self.software_component.pid,
                str(round((the_time - self.init_time), 3) * 1000))

            # Make all the observers observe the program by starting their threads
            self.log.debug("(%s) Starting all observer threads" % self.software_component.name)

            for an_observer in itertools.chain(self.process_observers, self.blocking_process_observers):
                an_observer.process_exchange_data.pid = str(self.software_component.pid)
                an_observer.name = self.software_component.name + "-" + self.software_component.pid
                self.log.debug("(%s) %s Observer starts now", str(an_observer.check_type.type).upper(),
                               self.software_component.name)
                an_observer.start()

            # DO NOT CHANGE THIS!
            sub_proc_ret_code = self.subprocess.wait()

            # Give it some time to write what is left
            time.sleep(0.2)

            # The subprocess terminated, we tell the PTY Logger to end it soon
            self.pty_log_writer.close_logger()

            # However, we wait for it to write whatever is left
            _ = self.pty_log_runner.wait()

            # Now we can end all observers in case the subprocess had some 'convincing' last argument which
            # was written by the PTYlogger and will satisfy an observer
            for an_observer in itertools.chain(self.process_observers, self.blocking_process_observers):
                an_observer.stop()
                an_observer.join()
                self.log.debug("(%s) Observer %s is done!", self.software_component.name, an_observer.name)

            self.log.info("%s [%s] quit, return code %s", self.software_component.name, self.software_component.pid, sub_proc_ret_code)

            # Close the ProcessCommunicator for the pipe too
            self.parent_pipe.close()
            # END DO NOT CHANGE THIS!
            return sub_proc_ret_code

        else:
            if self.software_component.host != "localhost":

                # Open a PTY for reading and writing to logfile
                master, slave = pty.openpty()

                # Get the current user
                u = os.getenv('USER')
                # Get the desired host from ini/scxml file
                host = self.software_component.host.strip()
                # Predefined ssh command that opens a PTY
                basic_ssh_cmd = "ssh -tt -C "+u+"@"+host+" ' echo $$; export DISPLAY=:0; exec "
                # Build the complete command
                ssh_cmd = basic_ssh_cmd + self.software_component.get_complete_executable_path_with_arguments()+" '"

                # Execute the command
                self.subprocess = subprocess.Popen(ssh_cmd, shell=True, stdin=slave, stdout=slave, stderr=slave,
                                                   bufsize=8192, executable='/bin/bash', env=self.environment_map)

                self.subprocess.master = master
                self.subprocess.slave = slave

                pid_found = False
                inherit_pid = -1
                now = time.time()


                # We wait for the the SSH connection to be ready. If the connection attempt fails,
                # the subprocess will have the PID -1 assigned. This will make the PID (STDOUT, ...)
                # observer fail in any case. However, if the connection attempt is successful, the
                # subprocess will be alive as long as the remote process lives, thus the monitored PID
                # will be the one of the subprocess. This is _not_ perfect, but as a first approximation
                # this works quite well.
                while pid_found is False and time.time() - now < 10:
                    self.log.info("[SSH] Waiting for connection to host %s..." % host)
                    try:
                        # Checks if there is any data on the pty
                        ready, _, _ = select.select([master], [], [], 0.1)
                        # This line actually reads from the pty
                        if ready:
                                data = os.read(master, 5)
                                if not data:
                                    continue
                                else:
                                    if not pid_found:
                                        tmp = data.strip()
                                        if tmp.isdigit():
                                            # We don't use this yet, but in later versions
                                            # there will be a remote PID observer which will
                                            # make use of the inherit_pid. For now, as described
                                            # above the subprocess PID will serve for monitoring
                                            # purposes.
                                            inherit_pid = int(tmp)
                                            pid_found = True
                                            self.log.info("[SSH] Connected to host %s " % host)
                                            break
                    except Exception, e:
                        pass
                    time.sleep(0.1)

                self.pty_log_writer.setup(self.subprocess, self.log_file_name)
                self.pty_log_runner = eventlet.spawn(self.pty_log_writer.logger)

                # Remember its PID, the PID is a member of the POpen class, if no pid found,
                # e.g., SSH process is stale. Set PID = -1 in order to make all observers fail.
                if pid_found is False:
                    self.subprocess_pid = str(inherit_pid)
                    self.software_component.pid = str(inherit_pid)
                else:
                    # Remember its PID, the PID is a member of the POpen class
                    self.subprocess_pid = self.subprocess.pid
                    self.software_component.pid = str(self.subprocess_pid)

                the_time = time.time()

                self.log.info(
                    ("\x1b[94m--> [SSH] Launching " + "%s [%s] on host %s %sms since FSMT init"),
                    self.software_component.name,
                    str(self.subprocess_pid), host,
                    str(round((the_time - self.init_time), 3) * 1000))

                # Make all the observers observe the program by starting their threads
                self.log.debug("(%s) Starting all observer threads" % self.software_component.name)

                for an_observer in itertools.chain(self.process_observers, self.blocking_process_observers):
                    an_observer.process_exchange_data.pid = str(self.software_component.pid)
                    an_observer.name = self.software_component.name + "-" + self.software_component.pid
                    self.log.debug("(%s) %s Observer starts now", str(an_observer.check_type.type).upper(),
                                   self.software_component.name)
                    an_observer.start()

                # DO NOT CHANGE THIS!
                sub_proc_ret_code = self.subprocess.wait()

                # Give it some time to write what is left
                time.sleep(0.2)

                # The subprocess terminated, we tell the PTY Logger to end it soon
                self.pty_log_writer.close_logger()

                # However, we wait for it to write whatever is left
                _ = self.pty_log_runner.wait()

                # Now we can end all observers in case the subprocess had some 'convincing' last argument which
                # was written by the PTYlogger and will satisfy an observer
                for an_observer in itertools.chain(self.process_observers, self.blocking_process_observers):
                    an_observer.stop()
                    an_observer.join()
                    self.log.debug("(%s) Observer %s is done!", self.software_component.name, an_observer.name)

                self.log.info("%s [%s] quit, return code %s", self.software_component.name, self.software_component.pid, sub_proc_ret_code)

                # Close the ProcessCommunicator for the pipe too
                self.parent_pipe.close()
                # END DO NOT CHANGE THIS!
                return sub_proc_ret_code