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

from fsmtest.log_factory import LogFactory
from fsmtest.pty_log_writer import PTYLogWriter
from fsmtest.containers.process_exchange_data import ProcessExchangeData
from fsmtest.processobservation.process_observer import ProcessObserver
from fsmtest.processobservation.lockfile_observer import LockfileObserver
from fsmtest.processobservation.pid_observer import PidObserver
from fsmtest.processobservation.screenpid_observer import ScreenpidObserver
from fsmtest.processobservation.screenstdout_observer import \
    ScreenstdoutObserver
from fsmtest.processobservation.stdout_observer import StdoutObserver
from fsmtest.processobservation.stdoutexclude_observer import \
    StdoutexcludeObserver
import eventlet
import itertools
import pty
import subprocess
import time
# SSH prepare...
# import paramiko


class ProcessExecutor():

    eventlet.monkey_patch()

    def __init__(self, process_pipe_, software_component_, environment_map_,
                 log_folder_, init_time_, state_machine_):
        """
        TODO
        :type software_component: object
        :param process_pipe:
        :param software_component:
        :param environment_map:
        :param log_folder:
        """
        # multiprocessing.Process.__init__(self)
        self.log = LogFactory().get_logger()
        self.parent_pipe = process_pipe_
        self.software_component = software_component_
        self.environment_map = environment_map_
        self.process_observers = []
        self.blocking_process_observers = []
        self.log_folder = log_folder_
        self.component_runner = None
        self.logger_runner = None
        self.subprocess = None
        self.subprocess_pid = "None"
        self.ptylog_writer = None
        self.log_file_name = None
        self.init_time = init_time_
        self.log.debug("Program Executor initialisation for %s",
                       self.software_component.name)
        self.state_machine = state_machine_
        self.pty_log_runner = None

        for check_type_ in self.software_component.check_types:
            process_exchange_data = ProcessExchangeData()
            class_to_call = check_type_.type.strip().lower().capitalize() + \
                "Observer"
            self.log.debug("Found observer type: %s", class_to_call)
            # Create an process exchange data object for the observer to send
            # later on ...
            process_exchange_data.message = self.software_component.name
            process_exchange_data.counter_name = \
                self.software_component.counter_name
            process_exchange_data.execution_type = \
                self.software_component.execution_type
            process_exchange_data.parent_state = \
                self.software_component.parent_state
            process_exchange_data.sender_id = \
                check_type_.id
            process_exchange_data.type = \
                check_type_.type

            try:
                constructor = globals()[class_to_call]
                new_observer = constructor(
                    self, self.parent_pipe, check_type_,
                    process_exchange_data, state_machine_)
            except Exception, e:
                self.log.critical(
                    "Class {0:s} could not be found. {1:s}".format(
                        check_type_.type + "Observer", e))
            if check_type_.blocking:
                self.blocking_process_observers.append(new_observer)
            else:
                self.process_observers.append(new_observer)
        self.log_file_name = self.log_folder + "/" + \
            self.software_component.name + ".log"
        self.ptylog_writer = PTYLogWriter(self.software_component.name)
        self.component_runner = eventlet.spawn(self.component_runner_function)

    # ex "run"
    def component_runner_function(self):
        """
        Run dos, run. This method actaully starts a component.
        """

        # Open a pty for read and write to logging
        master, slave = pty.openpty()

        # Preparation for remote host execution
        '''
        if self.software_component.host != "localhost":
            client = paramiko.SSHClient()
            # client.get_host_keys().add('ssh.example.com', 'ssh-rsa', key)
            policy = paramiko.client.WarningPolicy()
            client.set_missing_host_key_policy(policy)
            client.connect(self.software_component.host,
            username='me', password='password')
            stdin, stdout, stderr =
                        client.exec_command(self.software_component.path +
                        self.software_component.command)
        '''
        # Actually the lib 'fabric' seems to be more suitable for this! It re-
        # uses the paramiko lib in order to easily deploy commands via ssh.
        # The following line will make a remote call
        #
        # import fabric.operations
        # x = open('/tmp/test','w')
        # answer = fabric.operations.run("source /vol/sandbox_flobi/setup.bash && /vol/sandbox_flobi/fsmt/bin/fsmt_exouttimed 4 1", stdout=x, stderr=x)
        #
        # This seems easy and straight forward. it even makes the PTY writer
        # obsolete.

        self.log.log(
            5, "This component lives in the following environment %s",
            self.environment_map)
        # Actually call the command now...
        self.subprocess = subprocess.Popen(
            "exec " + self.software_component.
            get_complete_executable_path_with_arguments(),
            shell=True, stdin=slave, stdout=slave, stderr=slave,
            bufsize= -1, executable='/bin/bash', env=self.environment_map)

        # In general we will try to speed up log writing using Linux std tools
        # like tee. So in this case we open the subprocess and redirect the
        # output to tee which 'tees' and then passes the output to the pty()
        # master. You can also pass a buffer_size=-1 to indicate that you want
        # to use line-buffering, i.e. read a line at a time from the child
        # process. (This may only work as expected if the child process flushes
        # its output buffers after every line.).

        # Problem: Buffer does not get flushed!! ?!?!
        # cmd_splitter = ["tee", "%s" % self.log_file_name]
        # tee = subprocess.Popen(cmd_splitter, stdin=master,
        #            stdout=slave_tee, stderr=slave_tee, bufsize=-1)
        # self.tee_process = tee

        '''
        # We could also append more subprocess processing right here.
        # In case we need this some time.
        grep = subprocess.Popen(['grep', '.. include::'],
                        stdin=cat.stdout,
                        stdout=subprocess.PIPE,
                        )

        cut = subprocess.Popen(['cut', '-f', '3', '-d:'],
                        stdin=grep.stdout,
                        stdout=subprocess.PIPE,
                        )

        '''

        self.subprocess.master = master
        self.subprocess.slave = slave

        self.ptylog_writer.setup(self.subprocess, self.log_file_name)
        self.pty_log_runner = eventlet.spawn(self.ptylog_writer.logger)
        # self.pty_log_runner = self.ptylog_writer.start()

        # Remember its PID, the PID is a member of the POpen class
        self.subprocess_pid = self.subprocess.pid
        self.software_component.pid = str(self.subprocess_pid)

        the_time = time.time()
        self.log.info(
            (
                "--> Launching " +
                "%s [%s] %sms since FSMT init"),
            self.software_component.name,
            self.software_component.pid,
            str(round((the_time - self.init_time), 3) * 1000))

        '''
        ####        Deprecated for now         ####
        ###########################################
        ##  Screen_stdout information grep part  ##
        ###########################################
        #  Requirements:
        #  1. Start vdemo components with logging enabled (use -l before start)
        #  2. Log path will be listed then...
        #  3. The following loop will find the log path,
        #     parse it and tell the according observer about its location
        all_observers = itertools.chain(self.process_observers,
                 self.blocking_process_observers)
        for an_obs in all_observers:
            if an_obs.type == ("screen_stdout"):
                # Open the process output
                with open(self.stdout_screen_file.name, 'r') as a_file:
                    print "Setting log file for screen_stdout observer ..."
                    while True:
                        # Reduce CPU load a little ;)
                        time.sleep(0.002)
                        curLine = a_file.readline()
                        # Find log file
                        if "Logging to" in curLine:
                            print " ... done!"
                            an_obs.log_lile =
                                curLine.replace("\n", "").split(" ")[2]
                            break
        '''
        # Make all the observers 'observe' the program by starting their
        # threads
        self.log.debug("(%s) Starting all observer threads" %
                       self.software_component.name)
        for an_observer in itertools.chain(
                self.process_observers,
                self.blocking_process_observers):
            # Possibly a duplicate, but to make sure...
            an_observer.process_exchange_data.pid = \
                str(self.software_component.pid)
            an_observer.name = self.software_component.name + "-" + \
                self.software_component.pid
            self.log.debug(
                "(%s) %s Observer starts now",
                an_observer.check_type.type, self.software_component.name)
            an_observer.start()

        # DO NOT CHANGE THIS!
        sub_proc_ret_code = self.subprocess.wait()
        self.log.debug(
            "Subprocess %s ended - ending PTYlogger & %d observers now" %
            (self.software_component.name, len(self.process_observers) +
             len(self.blocking_process_observers)))

        # Our subprocess terminated so we tell the PTYlogger to end it soon
        self.ptylog_writer.close_logger()
        # BUT we wait for it to write whatever is left
        self.log.debug("(%s) waiting for PTYlogger now",
                       self.software_component.name)
        _ = self.pty_log_runner.wait()

        # Now we can end all observers (in case the subprocess had some
        # 'convincing' last argument which was written by the PTYlogger and
        # will satisfy an observer)
        for an_observer in itertools.chain(
                self.process_observers,
                self.blocking_process_observers):
            an_observer.stop()
            # thread stop+join == eventlet stop+wait (__IF__ threads are
            # bug-free!!! which is actually also true for eventlets...anyways)
            an_observer.join()
            self.log.debug("(%s) Observer %s is done!",
                           self.software_component.name, an_observer.name)

        self.log.info("(%s) Exited with return code %s",
                      self.software_component.name, sub_proc_ret_code)

        # Close the processCommunicator pipe too
        self.parent_pipe.close()
        # / END DO NOT CHANGE THIS!
        return sub_proc_ret_code
