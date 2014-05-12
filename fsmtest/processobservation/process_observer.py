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
import threading


class ProcessObserver(threading.Thread):

    """
    Abstract Process Observer class.
    """

    def __init__(self, process_executer_, parent_pipe_, check_type_,
                 process_exchange_data_, state_machine_):
        """
        DO NOT USE THE _SM directly to send results, this is what the
        ProcessCommunicator is for. Anyways, if a process disappears during
        ongoing checks, the ProcessCommunicator is already closed, because it
        returned (successfully). ONLY in this case, use send for the SM
        directly. See exception in send_negative_result_to_pyscxml().

        :param process_executer:
        :param parent_pipe:
        :param check_type:
        :param process_exchange_data:
        """
        threading.Thread.__init__(self)

        self.process_executer = process_executer_
        self.parent_pipe = parent_pipe_
        self.process_exchange_data = process_exchange_data_
        self.state_machine = state_machine_

        self.log_file = None
        self.end_thread = False
        self.hit_timeout = False
        self.observer_type = None
        self.unsatisfied = False
        self.un_poll_able = False
        self.stop_ongoing = False
        self.success_timeout = None
        self.success_criteria = None
        self.check_type = check_type_
        self.proc_exec_subprocess = None
        self.log = LogFactory().get_logger()
        self.blocking_until_criteria_met = None

    def stop(self):
        """
        External switch function to completely stop the observer (also includes
        ongoing-mode) at next possible injection point.
        """
        self.end_thread = True
        self.stop_ongoing = True

    def send_negative_result_to_pyscxml(self):
        """
        Helper function which tries to send a negative result back to the
        ProcessCommunictor via the given pipe and also logs the result to the
        DEBUG log stream.

        Issues such as broken pipe or others are handled by a direct
        interaction with the state machine.
        NOTE: This only works due to the use of eventlets. If eventlets will be
        removed from FSMT one day, this function NEEDS TO BE ADJUSTED!
        """
        try:
            self.process_exchange_data.successful = False
            self.log.debug(
                "%s: Sending _NEGATIVE_ exchange data to PYSCXML " +
                "via pipe: %s",
                self.process_exchange_data.message +
                " " + self.process_exchange_data.type,
                self.process_exchange_data.info_to_string())
            self.parent_pipe.send(self.process_exchange_data)
            self.state_machine.unsatisfied = True
        except IOError as e:
            self.log.error("Emergency exit %s", e)
            self.state_machine.unsatisfied = True
            self.state_machine.send("unsatisfied_criteria")

    def send_positive_result_to_pyscxml(self):
        """
        Helper function which tries to send a positive result back to the
        ProcessCommunictor via the given pipe and also logs the result to the
        DEBUG log stream.

        Issues such as broken pipe or others are handled by a direct
        interaction with the state machine.
        NOTE: This only works due to the use of eventlets. If eventlets will be
        removed from FSMT one day, this function NEEDS TO BE ADJUSTED!
        """
        try:
            self.process_exchange_data.successful = True
            self.log.debug(
                "%s: Sending _POSITIVE_ exchange data to PYSCXML " +
                "via pipe: %s",
                self.process_exchange_data.message +
                " " + self.process_exchange_data.type,
                self.process_exchange_data.info_to_string())
            self.parent_pipe.send(self.process_exchange_data)
        except IOError as e:
            self.log.error("Emergency exit %s" % e)
            self.state_machine.unsatisfied = True
            self.state_machine.send("unsatisfied_criteria")

    def send_result_to_pyscxml(self, result):
        """
        Helper function which tries to send a given result back to the
        ProcessCommunictor via the given pipe and also logs the result to the
        DEBUG log stream.

        Issues such as broken pipe or others are handled by a
        direct interaction with the state machine.
        NOTE: This only works due to the use of eventlets. If eventlets will be
        removed from FSMT one day, this function NEEDS TO BE ADJUSTED!

        :param result:
        """
        try:
            self.log.debug("%s: Sending exchange data to PYSCXML via pipe: %s",
                           "%s %s" % (self.process_exchange_data.message,
                                      self.process_exchange_data.type),
                           result.info_to_string())
            self.parent_pipe.send(result)
        except IOError as e:
            self.log.error("Emergency exit %s" % e)
            self.state_machine.unsatisfied = True
            self.state_machine.send("unsatisfied_criteria")

    def log_start(self):
        """
        Helper to log the start of an observer.
        """
        try:
            self.proc_exec_subprocess = self.process_executer.subprocess
            self.log.info("%s [%s] %s observer is starting (blocking %s)!",
                          self.process_executer.software_component.name,
                          str(self.process_executer.subprocess_pid),
                          self.check_type.type, self.check_type.blocking)
        except IOError as e:
            self.log.error("Emergency exit %s" % e)
            self.state_machine.unsatisfied = True
            self.state_machine.send("unsatisfied_criteria")

    def log_success(self, message=""):
        '''
        Helper to log the success of an observer.

        :param message:
        '''
        try:
            self.log.info("%s [%s] %s observer successful! %s",
                          self.process_executer.software_component.name,
                          str(self.process_executer.subprocess_pid),
                          self.check_type.type, message)
        except IOError as e:
            self.log.error("Emergency exit %s" % e)
            self.state_machine.unsatisfied = True
            self.state_machine.send("unsatisfied_criteria")

    def log_failure(self, message):
        """
        Helper to log the failure of an observer.

        :param message:
        """
        self.log.error("%s [%s] %s observer failed! %s",
                       self.process_executer.software_component.name,
                       str(self.process_executer.subprocess_pid),
                       self.check_type.type, message)
        self.state_machine.unsatisfied = True

    def log_cancel(self, message):
        """
        Helper to log the cancellation of an observer.

        :param message:
        """
        self.log.warning("%s [%s] %s observer cancelled! %s",
                         self.process_executer.software_component.name,
                         str(self.process_executer.subprocess_pid),
                         self.check_type.type, message)
        # Observer cancellation will not stop the SM, just throw a warning.
        # self.state_machine.unsatisfied = True

    def get_my_name(self):
        """
        Getter function.
        :return:
        """
        return "%s:%s" % (self.process_executer.software_component.name,
                          str(self.process_executer.subprocess_pid))

    def run(self):
        """
        Dummy method to force a developer extending this class to actually
        implement it.

        :raise:
        """
        raise NotImplementedError("You should have implemented this...")
