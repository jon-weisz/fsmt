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
from lxml import etree
from logging import currentframe
from fsmtest.log_factory import LogFactory
from fsmtest.containers.check_type import CheckType
from fsmtest.containers.software_component import SoftwareComponent
from fsmtest.exceptions.faulty_component_exception import FaultyComponentException


def advanced_pyscxml_logfunction(label, msg):
    """
    Logging function for the PYSCXML framework to adjust the logging style to
    fit our corporate design.
    :param label:
    :param msg:
    :return:
    """
    log_factory = LogFactory()
    log = log_factory.get_logger()
    os.path.normcase(currentframe().f_code.co_filename)
    label = str.lower(label)
    if label not in ['debug', 'info', 'warn', 'warning', 'error', 'critical']:
        if isinstance(label, str):
            if isinstance(msg, list):
                msg.reverse()
                msg.append(label)
                msg.reverse()
            elif isinstance(msg, tuple):
                msg = (label,) + msg
            else:
                msg = "%s %s" % (label, msg)
        label = "info"

    def f(x):
        if etree.iselement(x):
            return etree.tostring(x).strip()
        elif isinstance(x, etree._ElementStringResult):
            return str(x)
        return x

    if isinstance(msg, list) or isinstance(msg, tuple):
        msg = map(f, msg)
        try:
            msg = "\n".join(msg)
        except:
            msg = str(msg)
    log_method = getattr(log, label)
    log_method("%s" % msg)


def extract_software_component(component_name,
                               list_of_components,
                               state_machine):
    """
    :param component_name:
    :param list_of_components:
    :param state_machine:
    :return: :raise:
    """
    log = LogFactory().gl()
    a_software_component = SoftwareComponent()
    a_software_component.environment = state_machine.environment_setup
    for a_component in list_of_components:
        if a_component.get("val") == component_name:
            a_software_component.name = component_name
            a_software_component.parent_state = \
                state_machine.interpreter.configuration[-1].id
            for an_Element in a_component.getchildren():
                if an_Element.tag[1:].split("}")[1] == "command":
                    a_software_component.command = an_Element.get("val")
                elif an_Element.tag[1:].split("}")[1] == "path":
                    a_software_component.path = an_Element.get("val")
                elif an_Element.tag[1:].split("}")[1] == "execution_host":
                    a_software_component.host = an_Element.get("val")
                elif an_Element.tag[1:].split("}")[1] == "check_execution":
                    # Check anyways, so all components go through the same
                    # "pipeline". In case of exec_check == false, we fire a
                    # success event in the observer, no matter if pid is found
                    # to fulfill the users wish, transparently.
                    if an_Element.get("val") == "False":
                        a_software_component.check_execution = False
                    else:
                        a_software_component.check_execution = True
                        for a_check_type in an_Element.getchildren():
                            new_check_type = CheckType()
                            new_check_type.type = a_check_type.get('val') \
                                if a_check_type.get('val') is not None \
                                else new_check_type.type
                            new_check_type.criteria = \
                                a_check_type.get('criteria') \
                                if a_check_type.get('criteria') is not None \
                                else new_check_type.criteria
                            new_check_type.timeout = float(
                                a_check_type.get('timeout')) \
                                if a_check_type.get('timeout') is not None \
                                else new_check_type.timeout
                            tmp = a_check_type.get('blocking') \
                                if a_check_type.get('blocking') is not None \
                                else new_check_type.blocking
                            new_check_type.blocking = True \
                                if tmp == 'True' \
                                else False
                            tmp = a_check_type.get('ongoing') \
                                if a_check_type.get('ongoing') is not None \
                                else new_check_type.ongoing
                            new_check_type.ongoing = True \
                                if tmp == 'True' \
                                else False
                            new_check_type.id = hash(new_check_type)
                            a_software_component.add_check_type(new_check_type)
                else:
                    raise FaultyComponentException(
                       "Unknown tag in %s software component!", component_name)

    if "" in [a_software_component.command,
              a_software_component.path,
              a_software_component.host]:

        raise FaultyComponentException(
             ("Triplet command ('%s'), path ('%s'), host ('%s') is wrong, " +
             "check SCXML! This will cause unpredictable behaviour!"),
            a_software_component.command, a_software_component.path,
            a_software_component.host)

    if not a_software_component.path_and_command_is_valid():
        raise FaultyComponentException(
            ("The defined component '%s' is faulty. The path/command does " +
             "not exist: '%s' -- CWD '%s'") %
            (component_name,
             a_software_component.
             get_complete_executable_path_with_arguments().split()[0],
             os.getcwd()))

    if a_software_component.check_execution is False:
        log.warning(
            "check_execution is disabled for component %s!" + \
            " A crash will be undetected!", component_name)

    if a_software_component.check_execution is True and \
        len(a_software_component.check_types) == 0:
        log.warning(
            "There are no execution checks defined for component %s!" +
            " A crash will be undetected!", component_name)

    return a_software_component


def extract_execution_type(state_machine, node):
    """
    :param state_machine:
    :param node:
    :return:
    """
    execution_type = "default"
    if 'type' in node.keys():
        execution_type = node.get('type')
    counter_name = None
    new = node
    while True:
        new = new.getparent()
        if new is None:
            break
        elif new.tag[1:].split("}")[1] == "parallel":
            counter_name = "%s_parallelcount" % new.get('id')
            if execution_type == "default":
                pass
            if not counter_name in state_machine.datamodel:
                state_machine.log.critical( "If you see this log message, please write a bug "
                                            "report and include the zipped log folder! Thanks!")
                state_machine.datamodel[counter_name] = 0
            break
    return execution_type, counter_name
