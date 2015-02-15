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

from fsmtest.log_factory import LogFactory
from fsmtest.process_executor import ProcessExecutor
from scxml.pyscxml import StateMachine, custom_executable
from fsmtest.containers.xunit_test_case import XUnitTestCase
from fsmtest.exceptions.faulty_component_exception import FaultyComponentException
from fsmtest.scxml_helper import advanced_pyscxml_logfunction, extract_software_component, extract_execution_type
from fsmtest.utils import update_environment_setup, log_process_pids, end_process_and_children, write_fsm_file, write_fsm_diag

import os
import sys
import time
import operator
import traceback
import multiprocessing


class StateMachineWrapper(object):
    """
    Wrapper class for the PYSCXML state machine.
    """
    _instance = None
    datamodel = None
    _statemachine = None

    def __new__(cls, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        if not cls._instance:
            cls._instance = super(StateMachineWrapper, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def create_state_machine(self, path_to_scxml_file):
        """
        TODO
        :param path_to_scxml_file:
        """
        self._statemachine = StateMachine(path_to_scxml_file, log_function=advanced_pyscxml_logfunction)
        self.datamodel = self._statemachine.datamodel
        self.interpreter = self._statemachine.interpreter
        self.exit_grace = False
        self.block_diagram = {'opening': 'blockdiag {', 'content': 'initialise_state', 'ending': '}'}

    def log_setup(self, log_, log_folder_, log_folder_fsm_, log_folder_images_, log_folder_plots_, log_folder_videos_,
                  log_folder_data_, log_folder_logs_):
        """
        TODO
        :param log:
        :param log_folder:
        :param log_folder_fsm:
        :param log_folder_images:
        :param log_folder_plots:
        :param log_folder_videos:
        :param log_folder_data:
        :param log_folder_logs:
        """
        self.log = log_
        self.log_folder = log_folder_
        self.log_folder_fsm = log_folder_fsm_
        self.log_folder_data = log_folder_data_
        self.log_folder_logs = log_folder_logs_
        self.log_folder_plots = log_folder_plots_
        self.log_folder_videos = log_folder_videos_
        self.log_folder_images = log_folder_images_

    def send(self, name, data={}):
        """
        Wraps the send function of the PYSCXML state machine.
        :param name:
        :param data:
        """
        self._statemachine.send(name, data=data)

    def start(self):
        """
        Wraps the start function of the PYSCXML state machine.
        """
        self._statemachine.start()


global all_program_executors
all_program_executors = {}

global negative_result
negative_result = False

global final_cleanup
final_cleanup = False

global all_program_observers
all_program_observers = []

# !!Don't loose the following line or all hell breaks loose!! #


@custom_executable("de.unibi.citec.clf.fsmt")
def custom_executable(node, something):
    """
    :param node:
    :param something:
    """
    global all_program_executors, all_program_observers, negative_result, final_cleanup, websocket_connection

    execution_tag = node.tag[1:].split("}")[1]
    component_name = node.get("value")
    state_machine = StateMachineWrapper()
    log = LogFactory().gl()

    current_component_xunit_testcase = None

    if execution_tag == "execute_program":
        try:
            current_component_xunit_testcase = XUnitTestCase(component_name, "", test_type="failure")
            # Update environment $VAR set if necessary ...
            system_environment = update_environment_setup(state_machine)
            # Get the software and its properties on how to launch...
            a_software_component = extract_software_component(component_name,
                                                              state_machine.datamodel["component_bundle"],
                                                              state_machine)
            # Find execution type (normal vs. parallel)
            execution_type, counter_name = extract_execution_type(state_machine, node)
            a_software_component.counter_name = counter_name
            a_software_component.execution_type = execution_type
            # Create communication pipes
            # Parent conn, child conn
            pe_pipe, pc_pipe = multiprocessing.Pipe()
            process_executor = ProcessExecutor(
                pe_pipe, a_software_component,
                system_environment,
                state_machine.log_folder_logs,
                # state_machine.log_folder,
                state_machine.init_time,
                state_machine)
            # Add the component to the Communicator
            state_machine.process_communicator.add_software_component(
                a_software_component, pc_pipe)
            all_program_executors[process_executor] = \
                str(len(all_program_executors)) + "_" + \
                process_executor.software_component.name
            # Add all observers to the list, so we can check their status
            # later.
            if len(process_executor.process_observers) > 0:
                all_program_observers.append(process_executor.process_observers)
            if len(process_executor.blocking_process_observers) > 0:
                all_program_observers.append(process_executor.blocking_process_observers)
            if len(process_executor.blocking_process_observers) == 0:
                log.debug("No blocking observers are active")

            current_component_xunit_testcase.test_type = "success"

            log.debug("Execute component (%s) is done!", component_name)

        except FaultyComponentException, e:
            current_component_xunit_testcase.contents = str(sys.exc_traceback.tb_lineno) + str(e)

            log.error("Error while executing a user defined component. %s", str(e))
            state_machine.send("execute_program.fail")

        except Exception, e:

            current_component_xunit_testcase.contents = str(sys.exc_traceback.tb_lineno) + str(e)
            log.error("A wild error occurred while executing component '%s'", component_name)
            log.debug("Error in line %s! Message: %s", sys.exc_traceback.tb_lineno, e)
            log.debug("Traceback: %s", (traceback.format_exc()))
            state_machine.send("execute_program.fail")

    elif execution_tag == "emergency_exit":
        current_component_xunit_testcase = XUnitTestCase("DEPRECATED_Emergency_Exit", component_name,
                                                         test_type="failure")
        state_machine.unsatisfied = True
        log.warning("Usage of execution tag 'emergency_exit' is deprecated.")

    elif execution_tag == "error":
        # Possible errors that can occur here:
        # unsatisfied_criteria, execution_error, abortion_error
        current_component_xunit_testcase = XUnitTestCase("ERROR", component_name, test_type="failure")
        negative_result = True
        state_machine.unsatisfied = True

    elif execution_tag == "cleanUp":
        ############################
        ## Post-Process clean-up ###
        ############################
        log.debug(
            "\n#########################################################\n" +
            "## Cleaning up remaining processes and their observers ##\n" +
            "#########################################################")
        log.debug(
            ">> We have %d communication worker, holding multiple observers" %
            len(state_machine.process_communicator.worker))

        # We have to kill the communication pipe first, explicitly.
        id_all = 0
        all_status = state_machine.process_communicator.status

        for s in all_status:
            log.debug("Comm #%d returned:%s", id_all, s)
            id_all += 1

        state_machine.process_communicator.kill_all_worker()
        log.debug("<Next State> and <Current State>: %s", state_machine.interpreter.configuration)

        # Kill Observers explicitly.
        try:
            id_obs = 0
            for observer_list in all_program_observers:
                id_obs += len(observer_list)
            log.debug(">> We have %d observers configured, shutdown now", id_obs)
            id_obs = 0
            obs_idx = 0

            for observer_list in all_program_observers:
                for observer in observer_list:
                    obs_idx += 1
                    log.debug("Observer #%d status: %s %s", obs_idx, observer.name, observer)
                    if observer.isAlive():
                        observer.stop()
                        time.sleep(0.02)
                        id_obs += 1
                    if observer.isAlive():
                        time.sleep(0.02)
                        observer.stop()
            # We cannot force kill a thread
            log.debug("Shutdown %d observers, the rest already exited (NOT ONGOING)", id_obs)
        except Exception as e:
            log.warning("Unknown Exception occurred during observer 'war': %s", e)

        log_process_pids(all_program_executors, log)
        # Kill in reverse order, check this.
        # Old approach. Did not work properly.
        # all_program_executors_sorted = sorted(all_program_executors.iterkeys(), reverse=True)
        sorted_reverse = sorted(all_program_executors.items(), key=operator.itemgetter(1), reverse=True)
        log.debug("Executers Reverse Sort %s", sorted_reverse)

        for one_program_executor, name_value in sorted_reverse:
            pid = one_program_executor.software_component.pid
            name = one_program_executor.software_component.name

            # Try to terminate the subprocess, properly, send signal and wait
            # for the return value of the GreenThread which has spawned the
            # subprocess
            log.debug("Closing log writer for %s (%s)", name, pid)
            one_program_executor.pty_log_writer.close_logger()
            logger_status = one_program_executor.pty_log_runner.wait()
            if logger_status != 0:
                log.warning("Log writer was closed >> Force Quit")
            else:
                log.debug("Closing log writer done, status 0, Good")

            try:
                log.info("Ending process %s [%s] and its children", name, pid)
                end_process_and_children(pid, one_program_executor.subprocess, log)
            except Exception, e:
                log.warning("Error killing %s [%s]: %s. Considering it already dead", name, pid, e)

            all_program_executors.pop(one_program_executor)

        log.debug("Writing FSM results in %s", state_machine.log_folder_fsm)
        if negative_result:
            if state_machine.exit_grace:
                log.warning("You pressed CTRL+C")
            else:
                log.error("State Machine returned an error!")

            trial_path = os.environ['FSMFSM']
            write_fsm_file("negative_result", trial_path + "/fsmstatus", "ERROR")
            state_machine.block_diagram['content'] += " -> exit_state;"
            write_fsm_diag(trial_path + "/blockdiag.diag",
                           state_machine.block_diagram['opening'] + "\n" +
                           state_machine.block_diagram['content'] + "\n" +
                           state_machine.block_diagram['ending'])
            log.debug("Blockdiag written to %s", trial_path + "/blockdiag.diag")

            if state_machine.wsconn.get_is_connected():
                message = state_machine.wsconn.get_current_message()
                insert = state_machine.wsconn.get_inner_event()
                insert["name"] = "cleanup after fail"
                insert["events"] = [
                    {"name": "cleanup after fail",
                     "time": (
                         str(round(time.time() -
                                   state_machine.init_time, 3))),
                     "state": "cleanup",
                     "component": "cleanup after fail"}
                ]
                message["events"].append(insert)
                state_machine.wsconn.set_current_message(message)
                state_machine.wsconn.send_update()
            state_machine.exit_watcher.close(True)
        else:
            log.log(5, "%s" % "\n\
                ###############################\n\
                # FINISHED ALL THE PROCS!!!!! #\n\
                ###############################\n\
                #                         ';; #\n\
                #                          '' #\n\
                #            ____          || #\n\
                #           ;    \         || #\n\
                #            \,---'-,-,    || #\n\
                #            /     (  o)   || #\n\
                #          (o )__,--'-' \  || #\n\
                # ,,,,       ;'uuuuu''   ) ;; #\n\
                # \   \      \ )      ) /\//  #\n\
                # '--'       \'nnnnn' /  \     #\n\
                #   \\      //'------'    \    #\n\
                #    \\    //  \           \   #\n\
                #     \\  //    )           )  #\n\
                #      \\//     |           |  #\n\
                #       \\     /            |  #\n\
                ###############################\n\
                ")
            trial_path = os.environ['FSMFSM']
            write_fsm_file("cleanUp", trial_path + "/fsmstatus", "FINISHED ALL THE PROCS")
            if final_cleanup:
                state_machine.exit_watcher.close(True)
                state_machine.block_diagram['content'] += " -> exit_state;"
                write_fsm_diag(trial_path + "/blockdiag.diag",
                               state_machine.block_diagram['opening'] + "\n" +
                               state_machine.block_diagram['content'] + "\n" +
                               state_machine.block_diagram['ending'])
                log.debug("Blockdiag written to %s", trial_path + "/blockdiag.diag")
                state_machine.exit_watcher.close(True)

                if state_machine.wsconn.get_is_connected():
                    message = state_machine.wsconn.get_current_message()
                    insert = state_machine.wsconn.get_inner_event()
                    insert["name"] = "cleanup"
                    insert["events"] = [{
                                            "name": "cleanup",
                                            "time": (str(round(
                                                time.time() - state_machine.init_time,
                                                3
                                            ))),
                                            "state": "cleanup",
                                            "component": "cleanup"
                                        }]
                    message["events"].append(insert)
                    state_machine.wsconn.set_current_message(message)
                    state_machine.wsconn.send_update()
            final_cleanup = True

    else:
        log.critical("'Custom Executable' called but the tag %s was not recognised!", execution_tag)

    if current_component_xunit_testcase:
        state_machine.xunit_xml_builder.add_test_case(current_component_xunit_testcase)