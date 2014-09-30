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

from fsmtest.exceptions.class_not_set_up_exception import \
    ClassNotSetUpException
import eventlet
import time


##########################################################################
# So in theory this is quite simple:
#    1. We start a worker for each software component (i.e a program)
#    2. Each worker waits for the observers (if any) to send their success/fail
#    3. In case of having blocking ones, we WAIT for them before we send
#       a success event to the state machine
##########################################################################


class ProcessCommunicator():
    """
    Communicator class to allow inter-process communication.

    Note: Currently useless due to the use of eventlets. But it will be
    important once eventlets are removed from FSMT!
    """

    # Evil.
    eventlet.monkey_patch()

    def __init__(self):
        """
        Constructor.
        """
        self.log = None
        self.worker = []
        self.status = []
        self.at_work = False
        self.is_setup = False
        self.c_pipe_list = []
        self.abort_sent = False
        self.state_machine = None
        self.software_components = []
        self.all_program_executors = None

    def setup(self, state_machine_, all_program_executors_, log_):
        """
        Setup function setting all required variables etc.
        :param state_machine:
        :param all_program_executors:
        :param log:
        """
        self.log = log_
        self.state_machine = state_machine_
        self.all_program_executors = all_program_executors_
        self.log.debug("Process communicator is setting up now ...")
        self.is_setup = True

    def add_software_component(self, a_software_component,
                               communication_pipe):
        """
        Spawns a worker thread for a given software component which allows for
        inter-process communication.

        :param a_software_component:
        :param communication_pipe:
        :raise: ClassNotSetUpException:
        """
        if self.is_setup:
            self.abort_sent = False
            self.log.debug("Spawning a communication worker for %s",
                           a_software_component.name)
            worker_status = []
            a_worker = eventlet.spawn(self.work,
                                      a_software_component,
                                      communication_pipe,
                                      self.state_machine,
                                      worker_status)
            self.status.append(worker_status)
            self.software_components.append(a_software_component)
            self.worker.append(a_worker)
        else:
            raise ClassNotSetUpException(
                "Class was not properly setup on init!")

    def work(self, software_component, communication_pipe, state_machine,
             status):
        """
        Worker method which implements the communication between software
        component related processes. These are the spawned observers and
        the state machine itself (using a multiprocessing communication pipe).

        :param software_component:
        :param communication_pipe:
        :param state_machine:
        :return:
        """
        # Accumulate all check_types, e.g., pid, stdout ...
        number_of_observers_to_wait_for = len(software_component.check_types)
        # How many of them are blocking?
        number_of_blocking_observers = \
            len([x for x in software_component.check_types if x.blocking])
        global_success_event_sent = False

        # Abort if CTRL+C was hit inbetween
        if state_machine.exit_grace is True:
            state_machine.log.warning(
                ("Process Communicator thread for %s does" +
                 " not start CTRL+C was hit before"),
                software_component.name)
            status.append("(%s) never ran" % software_component.name)
            state_machine.send("external_abortion")

        # Abort if check_execution is false
        # If executionChecks DISABLED, we fire a SUCCESS
        # event and return in this observer anyway and always.
        if software_component.check_execution is False or \
            number_of_observers_to_wait_for == 0:
            state_machine.log.warning(
                ("[%s] Execution check is disabled - " + \
                 "triggering un-checked success event"), software_component.name)
            global_success_event_sent = True
            if software_component.execution_type == "parallel":
                state_machine.log.critical(
                       "If you see this log message, please write a bug " + \
                       "report and include the ziped log folder!")
                state_machine.datamodel[
                    software_component.counter_name
                ] += 1
            elif software_component.execution_type == "default":
                state_machine.send(software_component.name +
                                   ".execute_program.success")
                state_machine.block_diagram[
                    'content'] += software_component.parent_state + "-" + \
                    software_component.name + " -> "
            # Return, because checkExec is disabled
            status.append("(%s) returned, check_execution == False" %
                          software_component.name)

        # Log that we start and for how many observers we wait
        state_machine.log.debug(
            "[%s] communicator is waiting for %d observers",
            software_component.name,
            number_of_observers_to_wait_for)
        while number_of_observers_to_wait_for > 0:
            eventlet.sleep(0.02)
            # Check for gracefully exit, only works if observation is "True".
            if self.abort_sent:
                state_machine.log.debug("Shutting down communication for %s",
                                        software_component.name)
                status.append("(%s) returned, abort was sent" %
                              software_component.name)
                return 1
            if state_machine.exit_grace:
                if not self.abort_sent:
                    # Shut go into cleanup-state
                    state_machine.log.warning(
                        "Sending abort to State Machine " +
                        "from within a Process Communicator (%s)",
                        software_component.name)
                    status.append("(%s) returned, unsatisfied_criteria" %
                                  software_component.name)
                    state_machine.send("external_abortion")
                    return 1

            if communication_pipe.poll():
                # One down
                number_of_observers_to_wait_for -= 1
                # This is what we read
                try:
                    exchange_data = communication_pipe.recv()
                except EOFError, e:
                    self.log.error("Process communication suddenly died: " +
                                   "EOFError (most likely ended externally)")
                    state_machine.unsatisfied = True
                    state_machine.send("unsatisfied_criteria")
                    return 1
                except Exception, e:
                    self.log.error("Process communication suddenly died: ", e)
                    state_machine.unsatisfied = True
                    state_machine.send("unsatisfied_criteria")
                    return 1

                if exchange_data.successful:
                    state_machine.log.debug(
                        "Communicator (%s) got _POSITIVE_" +
                        "data back: %s",
                        software_component.name,
                        exchange_data.info_to_string())
                else:
                    state_machine.log.debug(
                        "Communicator (%s) got _NEGATIVE_" +
                        " data back: %s",
                        software_component.name,
                        exchange_data.info_to_string())
                status.append("(%s) %s returned!" %
                              (software_component.name,
                               exchange_data.type))

                # Do updates of the software_component if necessary
                # Override the PID if there is an update
                if exchange_data.pid != software_component.pid:
                    if exchange_data.pid != "None":
                        software_component.pid = exchange_data.pid
                # Update if we got a blocking one here
                for a_check_type in software_component.check_types:
                    if a_check_type.id == exchange_data.sender_id:
                        if a_check_type.blocking:
                            number_of_blocking_observers -= 1

                # If all blocking are done, then we can send the msg straight
                if number_of_blocking_observers == 0 and\
                        not global_success_event_sent:
                    global_success_event_sent = True
                    if exchange_data.successful:
                        if software_component.execution_type == \
                                "parallel":
                            state_machine.log.critical(
                               "If you see this log message, please write a" + \
                               " bug report and include the ziped log folder!")
                            state_machine.datamodel[
                                software_component.counter_name] += 1
                        elif software_component.execution_type == \
                                "default":
                            state_machine.send(
                                exchange_data.message +
                                ".execute_program.success")
                            if state_machine.wsconn.get_is_connected():
                                message = \
                                    state_machine.wsconn.get_current_message()
                                insert = state_machine.wsconn.get_inner_event()
                                insert["name"] = exchange_data.parent_state
                                insert["events"] = [{
                                    "name": software_component.name,
                                    "time": (
                                        str(round(time.time() -
                                                  state_machine.init_time, 3))
                                    ),
                                    "state": exchange_data.parent_state,
                                    "component": software_component.name
                                }]
                                message["events"].append(insert)
                                state_machine.wsconn.set_current_mMessage(
                                    message)
                                state_machine.wsconn.send_update()
                            state_machine.block_diagram['content'] += \
                                " -> " + \
                                exchange_data.parent_state + \
                                "-" + \
                                software_component.name
                        else:
                            state_machine.log.error(
                                "The execution type %s is unknown!",
                                software_component.execution_type)
                            state_machine.send("unsatisfied_criteria")
                            status.append("(%s) returned, unknown execution" %
                                          software_component.name)
                            return 1
                    else:
                        state_machine.send("unsatisfied_criteria")
                        status.append(
                            "(%s) returned, exchange data not successful" %
                            software_component.name)
                        return 1
                else:
                    """
                    This is a special case: we have blocking and non-blocking
                    observers in this case. the blocking ones are all done
                    (or only some of them) and we already sent the success evnt
                    (or don't want to yet) as the non-blocking/other blocking
                    are not finished.
                    """
                    if exchange_data.successful:
                        """
                        Well, 2 situations here:
                        1. There are still blocking observers and we will wait
                           for those, too (== pass here)
                        2. All blocking ones are done and we all know it worked
                           already ... so no further event is needed
                        """
                        pass
                    else:
                        """
                            Now a non-blocking finished with an error...
                            so in this case we just send an error event.
                        """
                        state_machine.send("unsatisfied_criteria")
                        status.append("unsatisfied_criteria %s" %
                                      software_component.name)
                        return 1
        status.append(
            "(%s) closing, all done" %
            software_component.name)
        state_machine.log.debug(
            ("Communication worker for (%s) is done! " +
             "Going to sleep now. Nighty-night!"),
            software_component.name)
        communication_pipe.close()
        return 0

    def kill_all_worker(self):
        """
        Kills all present workers by closing the communication channels and
        ending the according worker thread.
        """
        for worker, anID in zip(self.worker, xrange(0, len(self.worker))):
            self.abort_sent = True
            wait_status = worker.wait()
            if wait_status > 0:
                self.log.warning(("Communication worker #%d " +
                                 "closed in emergency state"), anID)
                worker.kill()
            else:
                self.log.debug(("Communication worker #%d " +
                               "closed successfully"), anID)
