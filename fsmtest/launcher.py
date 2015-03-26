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
import sys
import time
import signal
import eventlet
import subprocess
from shutil import copy

# Needed! Don't loose this!
from fsmtest.log_factory import LogFactory
from fsmtest.exit_watcher import ExitWatcher
from fsmtest.utils import make_zipfile, mkdir_p
from fsmtest.resource_centre import ResourceCentre
from fsmtest.xunit_xml_builder import XunitXmlBuilder
# from fsmtest.web_socket_utils import WebSocketConnection
from fsmtest.process_communicator import ProcessCommunicator
from fsmtest.state_machine_wrapper import StateMachineWrapper

# global websocket_connection


class Launcher():
    """
    Launcher for the FSM based system unittest program.
    """

    # Evil. See: http://eventlet.net/doc/basic_usage.html#eventlet.monkey_patch
    eventlet.monkey_patch()

    def __init__(self, log_level_, log_file_level_, log_folder_, disable_termcolor_,
                 _kill_timeout, path_to_scxml_file_):
        """
        Constructor for the launcher.

        :param options:
        :param log_level: Level on which logging is supposed to be set (i.e.
                          DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO
        :param output: All given options as parsed by the standard OptionParser
        :param path_to_scxml_file: The path to the SCXML to be executed.
        """

        self.log_level = log_level_
        self.log_folder = log_folder_
        self.log_file_level = log_file_level_
        self.kill_timeout = float(_kill_timeout)
        self.disable_termcolor = disable_termcolor_
        self.path_to_scxml_file = path_to_scxml_file_
        self.log = ""
        self.log_base = ""
        self.is_setup = False
        self.log_folder_fsm = ""
        self.log_folder_data = ""
        self.log_folder_logs = ""
        self.log_folder_plots = ""
        self.log_folder_videos = ""
        self.log_folder_images = ""
        self.absolute_log_folder = ""
        self.state_xunit_xml_path = ""
        self.current_run_timestamp = ""

    def setup(self):
        """
        Setup class preparing all required classes and settings. Has to be called BEFORE the run() method.
        """
        #######################################################################
        # Log folder creation
        #######################################################################
        if self.log_folder == "":
            self.log_folder = "/tmp/%s/fsmt/" % os.environ['USER']

        self.absolute_log_folder = self.log_folder
        self.current_run_timestamp = str(time.strftime("%m-%d_%H%M%S", time.localtime()))
        self.log_base = self.log_folder
        self.log_folder = os.path.join(self.log_folder, self.current_run_timestamp)
        self.log_folder_fsm = os.path.join(self.log_folder, "fsm")
        self.log_folder_images = os.path.join(self.log_folder, "images")
        self.log_folder_plots = os.path.join(self.log_folder, "plots")
        self.log_folder_videos = os.path.join(self.log_folder, "videos")
        self.log_folder_data = os.path.join(self.log_folder, "data")
        self.log_folder_logs = os.path.join(self.log_folder, "logs")
        self.state_xunit_xml_path = os.path.join(self.log_folder, "data", "state_component_run_test.xml")

        if not os.path.exists(self.log_folder):
            try:
                mkdir_p(self.log_folder)
                mkdir_p(self.log_folder_logs)
            except Exception, e:
                print "Error creating log folder(s) at %s! %s" % (self.log_folder, e)
                sys.exit(1)

        # Sanity check
        if not os.access(self.log_folder, os.W_OK):
            print "Exiting, logging path " + self.log_folder + " is not writable or does not exist"
            sys.exit(1)

        #######################################################################
        # Creating the logger itself
        #######################################################################
        log_factory = LogFactory()
        log_factory.set_up((not self.disable_termcolor), self.log_level, self.log_folder_logs, self.log_file_level)
        self.log = log_factory.get_logger()
        self.log.info("Log path: %s", self.log_folder_logs)
        self.log.info("Kill Timeout: %f", self.kill_timeout)
        self.log.debug("Log setup: level/colouring: %s/%s", self.log_level, (not self.disable_termcolor))
        self.log.debug("Execution path: %s", os.path.dirname(os.path.abspath(__file__)))
        self.log.debug("Current working directory: %s", os.getcwd())

        #######################################################################
        # Creating the remaining folders now with the known logger
        #######################################################################

        # And create the remaining folders
        mkdir_p(self.log_folder_fsm)
        mkdir_p(self.log_folder_images)
        mkdir_p(self.log_folder_plots)
        mkdir_p(self.log_folder_videos)
        mkdir_p(self.log_folder_data)

        # Remember the file we are going to execute
        copy(self.path_to_scxml_file, self.log_folder_fsm)

        #######################################################################
        # Setup of some environment variables
        #######################################################################
        os.environ['FSMBASE'] = self.log_folder
        os.environ['FSMLOG'] = self.log_folder_logs
        os.environ['FSMFSM'] = self.log_folder_fsm
        os.environ['FSMIMG'] = self.log_folder_images
        os.environ['FSMPLO'] = self.log_folder_plots
        os.environ['FSMVID'] = self.log_folder_videos
        os.environ['FSMDAT'] = self.log_folder_data
        os.environ['FSMTRA'] = self.current_run_timestamp

        self.log.debug("Environment VAR $%s set to %s", "FSMBASE", os.environ['FSMBASE'])
        self.log.debug("Environment VAR $%s set to %s", "FSMLOG", os.environ['FSMLOG'])
        self.log.debug("Environment VAR $%s set to %s", "FSMTRA", os.environ['FSMTRA'])
        self.log.debug("Environment VAR $%s set to %s", "FSMFSM", os.environ['FSMFSM'])
        self.log.debug("Environment VAR $%s set to %s", "FSMIMG", os.environ['FSMIMG'])
        self.log.debug("Environment VAR $%s set to %s", "FSMPLO", os.environ['FSMPLO'])
        self.log.debug("Environment VAR $%s set to %s", "FSMVID", os.environ['FSMVID'])
        self.log.debug("Environment VAR $%s set to %s", "FSMDAT", os.environ['FSMDAT'])
        self.is_setup = True

    def run(self):
        """
        Runner method. Sets-up the state machine properly and starts the SCXML Engine.
        """
        # global websocket_connection

        if self.is_setup:
            self.log.debug("Creating FSMT instance using your config: %s", self.path_to_scxml_file[:])
            state_machine_wrapper = StateMachineWrapper()
            state_machine_wrapper.create_state_machine(self.path_to_scxml_file)

            state_machine_wrapper.log_setup(
                self.log, self.log_folder, self.log_folder_fsm,
                self.log_folder_images, self.log_folder_plots,
                self.log_folder_videos, self.log_folder_data,
                self.log_folder_logs, self.kill_timeout)

            state_machine_wrapper.xunit_xml_builder = XunitXmlBuilder("FSMT run on %s" % self.path_to_scxml_file[:],
                                                                      self.state_xunit_xml_path)

            process_communicator = ProcessCommunicator()
            process_communicator.setup(state_machine_wrapper, None, self.log)
            state_machine_wrapper.process_communicator = process_communicator

            #####################################
            ###   Start of actual SM script   ###
            #####################################

            # Web Sockets
            # ws_connection = WebSocketConnection()
            # websocket_connection = ws_connection
            # state_machine_wrapper.wsconn = None

            # This signal handler enables us to trap the CTRL+C command and
            # send a exit_grace aka statemachine.send(unsatisfied_criteria)
            # to the SM interpreter. All procs should be killed then.
            def signal_handler(signal, frame):
                self.log.warning("\n\nYou pressed CTRL+C! Trying to gracefully terminate all running processes\n\n")
                state_machine_wrapper.exit_grace = True

            signal.signal(signal.SIGINT, signal_handler)

            # Watch for exit_grace = True, this needs to be a eventlet
            # thread! Otherwise you cannot switch context
            state_machine_wrapper.exit_watcher = ExitWatcher(state_machine_wrapper)

            # Exit watcher is closed in the clean_up block
            eventlet.spawn(state_machine_wrapper.exit_watcher.do_watch)

            init_time = time.time()
            state_machine_wrapper.init_time = init_time
            fsm_pid = os.getpid()
            resource_centre = ResourceCentre(fsm_pid)
            eventlet.spawn(resource_centre.resource_counter)
            state_machine_wrapper.unsatisfied = False
            state_machine_wrapper.start()

            # Build the component based xunit XML
            state_machine_wrapper.xunit_xml_builder.write_xml()

            # Zipping it all up
            source = self.log_folder
            destination = (self.log_folder + ".zip")
            # self.log.info("Writing log archive to %s", destination)
            make_zipfile(source, destination)

            # 'Softlink' latest ZIP Archive and xUnit XML file
            up_dir = self.log_base
            current_file_name = os.path.basename(self.path_to_scxml_file[:])
            current_run = up_dir + current_file_name + "-latest.run"
            current_zip = up_dir + current_file_name + "-latest.zip"
            current_xunit = up_dir + current_file_name + "-latest-xunit.xml"
            # Cleanup old softlink before creating new one
            if os.path.isfile(current_run):
                subprocess.call(["rm", "-f", current_run])
            subprocess.call(["ln", "-sfn", self.log_folder, current_run])
            subprocess.call(["ln", "-sf", str(self.state_xunit_xml_path), current_xunit])
            subprocess.call(["ln", "-sf", str(destination), current_zip])
            self.log.info("Softlink latest RUN %s", str(current_run))
            self.log.info("Softlink latest XUnit %s", str(current_xunit))
            self.log.info("Softlink latest ZIP archive %s", str(current_zip))

            self.log.info("Absolute runtime : %s seconds" % round((time.time() - init_time), 3))

            resource_centre.stop()

            self.log.info("Maximum CPU usage: %s %%", round(resource_centre.max_cpu, 3))
            self.log.info("Average CPU usage: %s %%", round(resource_centre.get_average_cpu(), 3))
            self.log.info("Maximum MEM usage: %s %%", round(resource_centre.max_mem, 3))

            # Cores does not make sense here since fsmt itself will not use more than one core.
            # self.log.info("Maximum CORES    : %s", resource_centre.max_thr)

            if state_machine_wrapper.exit_grace or state_machine_wrapper.unsatisfied:
                result = ""
                if state_machine_wrapper.exit_grace:
                    result += "CTRL+C DETECTED...FSMT RUN ABORTED"
                    state_machine_wrapper.log.warning(result)
                self.log.error(">> FSMT RUN ABORTED OR FAILED <<")
                sys.exit(1)
            else:
                self.log.info(">> FSMT RUN WAS SUCCESSFUL <<")
        else:
            self.log.error("You need to call setup() before calling the run() method!")
            sys.exit(1)
