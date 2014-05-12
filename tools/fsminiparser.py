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

from optparse import OptionParser
import types
import StringIO
import traceback
import ConfigParser
import xml.etree.ElementTree as ET
import sys

Tscxml_body = '''<?xml version="1.0" encoding="UTF-8"?>
            <scxml  xmlns="http://www.w3.org/2005/07/scxml"
                    version="1.0" initial="initialise_test"
                    id="%(testName)s" xmlns:my_ns="%(namespace)s">

                %(datamodel)s

                <transition event="unsatisfied_criteria" target="criteria_error" >
                    <log label="ERROR" expr="'Received unsatisfied_criteria event!'" />
                </transition>
                <transition event="external_abortion" target="abortion_error" >
                    <log label="ERROR" expr="'Received unsatisfied_criteria event!'" />
                </transition>
                <transition event="execute_program.fail" target="execution_error" >
                    <log label="ERROR" expr="'Recieved execution_error event!'" />
                </transition>
                <state id="initialise_test">
                    <onentry>
                        <log label="INFO" expr="'Entering State initialise_test'" />
                    </onentry>
                    <transition target="run_test"/>
                    <onexit>
                        <log label="INFO" expr="'Exiting State: initialise_test'" />
                    </onexit>
                </state>
                <state id="run_test" initial="%(initialRunStateName)s"> <!-- COMPONENTS START -->

                    %(runStates)s

                </state> <!-- ALL COMPONENTS ARE UP AND RUNNING -->
                <state id="result_assessment" initial="clean"> <!-- ASSESS YOUR RESULTS -->

                    <state id="clean"> <!-- END ALL PROCESSES -->
                        <onentry>
                           <log label="INFO" expr="'Entering State: Cleanup components'" />
                           <my_ns:cleanUp expr="executable" value="" />
                        </onentry>
                        <transition target="%(initialAssessmentState)s"/>
                        <onexit>
                          <log label="INFO" expr="'Exiting State: Done cleaning up'" />
                        </onexit>
                    </state> <!-- ALL PROCESSES ENDED -->

                    %(assessStates)s

                </state> <!-- RESULTS ASSESSED -->
                <state id="criteria_error">
                    <onentry>
                        <log label="ERROR" expr="'criteria_error state entered - Exiting!'" />
                        <my_ns:error value="criteria" />
                    </onentry>
                    <transition target="exit_test" />
                </state>
                <state id="execution_error">
                    <onentry>
                        <log label="ERROR" expr="'execution_error state entered - Exiting!'" />
                        <my_ns:error value="executionFail" />
                    </onentry>
                    <transition target="exit_test" />
                </state>
                <state id="abortion_error">
                    <onentry>
                        <log label="ERROR" expr="'execution_error state entered - Exiting!'" />
                        <my_ns:error value="abortion" />
                    </onentry>
                    <transition target="exit_test" />
                </state>
                <final id="exit_test">
                    <onentry>
                        <log label="INFO" expr="'Entering State: exit_test'" />
                        <my_ns:cleanUp expr="executable" value="" />
                    </onentry>
                    <onexit>
                        <log label="INFO" expr="'Exiting State: exit_test'" />
                    </onexit>
                </final>
            </scxml>'''

# Create raw nodes to be altered and inserted into the template
# %(parallelCounters)s, %(environmentVariables)s, %(softwareComponents)s
TdataModel = '''
                <datamodel>
                    %(parallelCounters)s
                    <data id="environment"> <!-- DEFINE ENVIRONMENT VARIABLES -->
                        %(environmentVariables)s
                    </data> <!-- ENVIRONMENT VARIABLES DEFINED -->

                    <data id="hosts"> <!-- !!! NOT WORKING IN CURRENT VERSION !!! -->
                        <hostinfo name="localhost" ip="127.0.0.1"/>
                    </data>

                    <data id="component_bundle"> <!-- DEFINE COMPONENTS -->
                        %(softwareComponents)s
                    </data> <!-- COMPONENTS DEFINED -->
                </datamodel>'''

# %(name)s, %(value)s
TenvironmentVariable = '''<variable var="%(name)s" val="%(value)s" />'''

# %(name)s, %(command)s, %(path)s, %(execution_host)s, %(check_execution)s
TsoftwareComponent = '''
                    <component val="%(name)s">
                        <command val="%(command)s"/>
                        <path val="%(path)s"/>
                        <execution_host val="%(execution_host)s"/>
                        <check_execution val="%(check_execution)s">
                            %(check_types)s
                        </check_execution>
                    </component>'''

# %(name)s, %(command)s, %(path)s, %(execution_host)s, %(check_execution)s
TsoftwareDefaultAssessmentComponent = '''
                    <component val="default">
                        <command val="ls $FSMFSM"/>
                        <path val="/bin/"/>
                        <execution_host val="localhost"/>
                        <check_execution val="True">
                            <check_type blocking="False" criteria="" ongoing="False" timeout="3" val="pid" />
                        </check_execution>
                    </component>'''

# %(check_type)s, %(criteria)s, %(timeout)s, %(blocking)s, %(ongoingFlag)s
Tcheck_type = '''
                <check_type val="%(check_type)s" criteria="%(criteria)s" timeout="%(timeout)s" blocking="%(blocking)s" ongoing="%(ongoing)s"/>'''

# %(name)s, %(componentToCall)s, %(target)s
Tstate = '''
                <state id="%(name)s">
                    <onentry>
                        <log label="INFO" expr="'Entering State: %(name)s'" />
                        <my_ns:execute_program value="%(componentToCall)s" />
                    </onentry>
                    <transition event="%(name)s.execute_program.success" target="%(target)s" />
                    <onexit>
                        <log label="INFO" expr="'Exiting State: %(name)s'" />
                    </onexit>
                </state>'''

# %(name)s, %(componentToCall)s, %(target)s
Tstate_inParallel_finalTransition = '''
                <state id="%(name)s">
                    <onentry>
                        <log label="INFO" expr="'Entering State: %(name)s'" />
                        <my_ns:execute_program value="%(componentToCall)s" />
                    </onentry>
                    <transition target="%(target)s_final" event="%(name)s.execute_program.success" />
                    <onexit>
                        <log label="INFO" expr="'Exiting State: %(name)s'" />
                    </onexit>
                </state>'''

# %(name)s, %(componentToCall)s
Tstate_noTransition = '''
                <state id="%(name)s">
                    <onentry>
                        <log label="INFO" expr="'Entering State: %(name)s'" />
                        <my_ns:execute_program value="%(componentToCall)s" />
                    </onentry>
                    <onexit>
                        <log label="INFO" expr="'Exiting State: %(name)s'" />
                    </onexit>
                </state>'''

# %(name)s, %(states)s, %(parallelVariableToIncrease)s
Tsuper_state_noTransition = '''
                <state id="%(name)s">
                    <onentry>
                        <log label="INFO" expr="'Entering State: %(name)s'" />
                    </onentry>

                    %(states)s

                    <final id="%(name)s_final">
                        <onentry>
                            <log expr="'Substate-Final reached: Increasing parallel counter %(parallelVariableToIncrease)s_parallelcount'" label="DEBUG" />
                            <assign location="%(parallelVariableToIncrease)s_parallelcount" expr="%(parallelVariableToIncrease)s_parallelcount+1" />
                        </onentry>
                    </final>

                    <onexit>
                        <log label="INFO" expr="'Exiting State: %(name)s'" />
                    </onexit>
                </state>'''

# %(name)s, %(componentToCall)s
Tstate_noTransition_typeParallel = '''
                <state id="%(name)s">
                    <onentry>
                        <log label="INFO" expr="'Entering State: %(name)s'" />
                        <my_ns:execute_program value="%(componentToCall)s" type="parallel"/>
                    </onentry>
                    <onexit>
                        <log label="INFO" expr="'Exiting State: %(name)s'" />
                    </onexit>
                </state>'''

# %(name)s, %(parallelStates)s, %(numberOfParallelStates)s, %(target)s
TparallelState = '''
                <parallel id="%(name)s"> <!-- PARALLEL START -->
                    <onentry>
                        <assign location="%(name)s_parallelcount" expr="0" />
                        <log label="INFO" expr="'Entering State: %(name)s (PARALLEL)'" />
                    </onentry>

                    %(parallelStates)s

                    <transition cond="%(name)s_parallelcount==%(numberOfParallelStates)s" target="%(target)s">
                        <log label="Exiting Count" expr="%(name)s_parallelcount" />
                    </transition>

                    <onexit>
                        <log label="INFO" expr="'Exiting State: %(name)s (PARALLEL)'" />
                    </onexit>

                </parallel> <!-- END PARALLEL -->'''

# %(name)s, %(parallelStates)s, %(numberOfParallelStates)s, %(parallelVariableToIncrease)s
TparallelState_nested = '''
                <parallel id="%(name)s"> <!-- PARALLEL START -->
                    <onentry>
                        <assign location="%(name)s_parallelcount" expr="0" />
                        <log label="INFO" expr="'Entering State: %(name)s (PARALLEL)'" />
                    </onentry>

                    %(parallelStates)s

                    <transition cond="%(name)s_parallelcount==%(numberOfParallelStates)s">
                        <log label="Exiting Count" expr="%(name)s_parallelcount" />
                        <assign location="%(parallelVariableToIncrease)s_parallelcount" expr="%(parallelVariableToIncrease)s_parallelcount+1" />
                    </transition>

                    <onexit>
                        <log label="INFO" expr="'Exiting State: %(name)s (PARALLEL)'" />
                    </onexit>

                </parallel> <!-- END PARALLEL -->'''


# %(name)s
TparallelCounter = '<data id="%(name)s_parallelcount" expr="0" />'

# %(name)s %(time)s, %(target)s
TwaitState = '''
                <state id="%(name)s"> <!-- COLLECT DATA -->
                    <onentry>
                        <log label="INFO" expr="'Entering State: Wait (collecting data for %(time)s seconds)'" />
                        <send event="wait.finish" delay="'%(time)ss'" />
                    </onentry>
                    <transition event="wait.finish" target="%(target)s"/>
                    <onexit>
                        <log label="INFO" expr="'Exiting State: Wait (collected data for %(time)s seconds)'" />
                    </onexit>
                </state> <!-- DATA COLLECTED -->'''


def get_tuples(config, section, options):
    result = {}
    for an_option in options:
        result[an_option] = get_tuple(config, section, an_option)
    return result


def get_tuple(config, section, option):
    read_string = config.get(section, option)
    result = tuple(read_string.split(','))
    return result


########################################################################
# RECURSIVE PARALLEL STATE EXTRACTOR
########################################################################
#
# BUGS TO FIX:
#    1. result assessment transition bug
#    2. assessment via ini includation
#
def work_parallel_states(run_states_tmp, element, depth_counter,
                         nested_name_prefix, predecessor_variable_name,
                         general_name_prefix='', next_target_name=None):
    '''
    Recursive function which will transform a given parallel software component
    order in ini notation (e.g. (a,b),[(c,d)],e) into SCXML notation.
    :param run_states_tmp:
    :param element:
    :param depth_counter:
    :param nested_name_prefix:
    :param predecessor_variable_name:
    :param next_target_name:
    '''
    parallel_state_construct_final = ""
    all_parallel_states_final = ""
    parallel_counters_final = ""
    parallel_state_counter = 0

    if nested_name_prefix == "":
        # %(name)s, %(parallelStates)s, %(numberOfParallelStates)s, %(target)s
        parallel_state_transition_name = general_name_prefix + \
            '%sstate_%d' % (nested_name_prefix, depth_counter)
    else:
        # parallel_state_transition_name = '%s%d' % \
        # (nested_name_prefix, depth_counter)
        parallel_state_transition_name = '%s' % nested_name_prefix

    for (a_parallel_element, i) in zip(element, range(0, len(element))):
        current_state_name = parallel_state_transition_name + "_pstate_%d" % i

        # Sequential listing
        if isinstance(a_parallel_element, types.TupleType):
            # %(name)s, %(states)s
            a, b = work_sequential_states(
                a_parallel_element, parallel_state_counter, None,
                name_prefix=current_state_name)
            innerStates = a
            parallel_state_counter = b

            outerSuperState_FINAL = Tsuper_state_noTransition % {
                'name': current_state_name,
                'states': innerStates,
                'parallelVariableToIncrease': parallel_state_transition_name}
            all_parallel_states_final += outerSuperState_FINAL

        # Recursion for parallel
        elif isinstance(a_parallel_element, types.ListType):
            # parallel_state_transition_name was current_state_name
            # last was: current_state_name + "_parallelcount"
            a, b, c, d = work_parallel_states(
                all_parallel_states_final, a_parallel_element, 0,
                current_state_name, parallel_state_transition_name)
            all_parallel_states_final += a
            parallel_counters_final += b
        else:
            raise Exception("Order of software components in parallel " +
                            "element is faulty. Unknown element: " +
                            a_parallel_element + ' | In: ' +
                            a_parallel_element)

    # Only applies for root node (if recursive)
    if nested_name_prefix == "":
        parallelState = TparallelState % {
            'name': parallel_state_transition_name,
            'parallelStates': all_parallel_states_final,
            'numberOfParallelStates': str(len(element)),
            'target': nested_name_prefix + next_target_name}
    else:
        # %(name)s, %(parallelStates)s, %(numberOfParallelStates)s,
        # %(parallelVariableToIncrease)s
        parallelState = TparallelState_nested % {
            'name': parallel_state_transition_name,
            'parallelStates': all_parallel_states_final,
            'numberOfParallelStates': str(len(element)),
            'parallelVariableToIncrease': predecessor_variable_name}
    parallel_state_construct_final += parallelState + '\n'
    # %(name)s
    parallel_counters_final += TparallelCounter % {
        'name':
        parallel_state_transition_name} + '\n'
    depth_counter += 1

    return (parallel_state_construct_final, parallel_counters_final,
            depth_counter, parallel_state_transition_name)


def work_sequential_states(element, counter, final_target_name,
                           name_prefix=""):
    '''
    Given a tuple of individual software components that are supposed to be run
    sequentially, this method creates the according scxml state structure. This
    includes the naming and transitioning from one to the next.

    :param element: A tuple of individual software components, which are
                    supposed to be transformed into SCXML notation.
    :param counter: A counter of the current number of states. Is used for
                    naming of the states (e.g. state_%d)
    :param target_name: name of the target to which the last element of element
                    is supposed to transition to. If empty (==""),
                    _NO_ transition is made and the <transition> tag is
                    removed.
    :param name_prefix: Optional. Prefix that is prepended before the state
                    names. Use this for nested naming to avoid name collisions.
    '''

    result = ""
    in_parallel_mode = True if final_target_name is None else False
    filler = "_" if in_parallel_mode else ""
    last_elem_mode = True if final_target_name != "" else False
    number_of_elements = len(element)

    for (anElement, i) in zip(element, range(0, len(element))):
        isLastElement = (i + 1 == number_of_elements)
        if i == 0:
            current_stat_name = name_prefix + filler + 'state_%d' % counter
        else:
            current_stat_name = name_prefix + filler + 'state_%d_%d' % \
                (counter, i)

        if not in_parallel_mode and isLastElement:
            target_name = final_target_name

        else:
            target_name = name_prefix + filler + 'state_%d_%d' % \
                (counter, i + 1)
                # target_name = name_prefix + 'state_%d_%d' % (counter,i+1)

        # Last sequential element within a prallel state (=no transition
        # necessary)
        if in_parallel_mode and isLastElement:
            # %(name)s, %(componentToCall)s, %(target)s
            a_state = Tstate_inParallel_finalTransition % {
                'name': current_stat_name,
                'componentToCall': anElement,
                'target': name_prefix}
        else:
            # %(name)s, %(componentToCall)s, %(target)s
            a_state = Tstate % {'name': current_stat_name,
                                'componentToCall': anElement,
                                'target': target_name}

        result += a_state + '\n'
    counter += 1
    return result, counter


def parse_ini_file(iniFileObject, output_path, silent=False):
    '''
    Function for automated scxml generation from a given ini file.

    :param pathToINIFile: The path to the ini file.
    :param output_path: path to where the output is supposed to be written.
    '''

    if not silent:
        print "\nWARNING: This converter is in its early BETA phase..."
        print "WARNING: Not all features may work as intended..."
    try:
        #======================================================================
        # PARSINT INTITIALISATION
        #======================================================================
        # Get the corresponding ini file
        config = ConfigParser.RawConfigParser(allow_no_value=False)
        # Preserve CAPITALS in env vars!!
        config.optionxform = str
        config.readfp(iniFileObject)

        run_order = config.get('run', 'run_order')

        # namespace setting
        # using this isntead of config.get('run', 'namespace')
        namespace = "de.unibi.citec.clf.fsmt"

        # Unsafe but easy
        run_order = eval('(' + run_order + ')')
        execution_duration = config.get('run', 'run_execution_duration')
        result_assessment_execution_duration = config.get(
            'run', 'result_assessment_execution_duration')

        assessment_order = config.get('run', 'result_assessment_order')
        if not assessment_order:
            print "WARNING: No assessment component has been set." + \
                " Creating a default \'ls\' component.\n"
            assessment_order = '(\'default\',),'
        assessment_order = eval('(' + assessment_order + ')')

        #======================================================================
        # ENVIRONMENT PARSING
        #======================================================================
        environment_variables_final = ""
        name_val_pairs = dict(config.items('environment'))
        for aName in name_val_pairs.keys():
            # %(name)s, %(value)s
            environment_variables_final += \
                TenvironmentVariable % {'name': aName,
                                        'value': name_val_pairs[aName]} + '\n'

        # print 'environment_variables_final: ', environment_variables_final

        #======================================================================
        # SOFTWARE COMPONENT PARSING
        #======================================================================
        software_components_final = ""
        software_components_final += TsoftwareDefaultAssessmentComponent + '\n'
        for a_section in config.sections():
            if 'component-' in a_section and config.has_option(a_section,
                                                               'name'):
                section_values = dict(config.items(a_section))
                check_type_options = ['check_type', 'timeout',
                                      'blocking', 'ongoing', 'criteria']
                check_type_tuple_dict = get_tuples(
                    config, a_section, check_type_options)
                all_check_types_final = ''

                for cur_num in \
                    range(0, len(check_type_tuple_dict['check_type'])):

                    if check_type_tuple_dict['check_type'][cur_num] != '':
                        a_check_type_option_dict = {}
                        for an_option in check_type_options:
                            a_check_type_option_dict[an_option] = \
                                check_type_tuple_dict[an_option][cur_num]

            # %(check_type)s, %(timeout)s, %(blockingFlag)s, %(ongoingFlag)s
                        a_check_type = Tcheck_type % a_check_type_option_dict
                        all_check_types_final += a_check_type + '\n'

                section_values['check_types'] = all_check_types_final

            # %(name)s, %(command)s, %(path)s, %(host)s, %(check_executionFlag)s
                a_software_component = TsoftwareComponent % section_values
                software_components_final += a_software_component + '\n'

        #======================================================================
        # STATE PARSING
        #======================================================================
        def order_to_scxml_convert(order, state_name_prefix='',
                                   wait_duration=1,
                                   last_elem_target_name='result_assessment'):
            wait_state_name = 'pre_' + last_elem_target_name + '_wait'
            run_states_final = ""
            parallel_counters_final = ""
            state_counter = 0
            for (element, index) in zip(order, range(0, len(order))):
                is_last_element = state_counter + 1 == len(order)
                if is_last_element:
                    target_name = state_name_prefix + \
                        wait_state_name  # last_elem_target_name
                else:
                    target_name = state_name_prefix + \
                        'state_%d' % (state_counter + 1)

                # Sequential
                if isinstance(element, types.TupleType):
                    # print "SEQ"
                    a, b = work_sequential_states(
                        element, state_counter, target_name,
                        name_prefix=state_name_prefix)
                    run_states_final += a
                    state_counter = b

                # Parallel
                elif isinstance(element, types.ListType):
                    # print "CALL WITH :::: ", state_counter, "", "",
                    # target_name
                    a, b, _, _ = work_parallel_states(
                        run_states_final, element, state_counter, "", "",
                        next_target_name=target_name,
                        general_name_prefix=state_name_prefix)
                    run_states_final += a
                    parallel_counters_final += b
                    state_counter += 1
                else:
                    print ("Order of software components is faulty." +
                           " Unknown element: %s | type: %s | in order : %s" +
                           " | Exprected Tuple or List instead.") % \
                        (element, str(type(element)), order)
                    sys.exit(-1)

            # %(name)s %(time)s, %(target)s
            run_states_final += TwaitState % {
                'name': state_name_prefix + wait_state_name,
                'time': wait_duration,
                'target': last_elem_target_name}
            return run_states_final, parallel_counters_final

        print "Phase 1/2 ... done "
        run_states_final, parallel_counters_final = order_to_scxml_convert(
            run_order, wait_duration=execution_duration)
        print "Phase 2/2 ... done ",
        assessment_states_final, \
            assessment_parallel_counters_final = order_to_scxml_convert(
                assessment_order, state_name_prefix="assessment_",
                wait_duration=result_assessment_execution_duration,
                last_elem_target_name='exit_test')

        #======================================================================
        # FINAL MERGE OF PARSED INFO
        #======================================================================
        # %(parallelCounters)s, %(environmentVariables)s,
        # %(softwareComponents)s
        data_model_final = TdataModel % {
            'parallelCounters': parallel_counters_final +
            assessment_parallel_counters_final,
            'environmentVariables': environment_variables_final,
            'softwareComponents': software_components_final}

        # %(datamodel)s, %(runStates)s, %(assessStates)s
        # %(testName)s, %(namespace)s,  %(initialRunStateName)s,
        # %(initialAssessmentState)s
        total_scxml_final = Tscxml_body % {
            'testName': config.get('run', 'name'),
            'namespace': namespace,
            # TODO: FIX!!
            'initialRunStateName': 'state_0',
            # TODO: fix!!
            'initialAssessmentState': 'assessment_state_0',
            'datamodel': data_model_final,
            'runStates': run_states_final,
            'assessStates': assessment_states_final}

        # Register namespaces
        ET.register_namespace('my_ns', namespace)
        ET.register_namespace('', "http://www.w3.org/2005/07/scxml")
        # Read the raw example scxml and find nodes
        tree = ET.parse(StringIO.StringIO(total_scxml_final))
        # root = tree.getroot()\
        # TODO: append elements into tree by using the tree object instead of %
        # string

        indent(tree.getroot())
        tree.write(output_path)
        if not silent:
            print "\nFinish! Result written to '%s'!\n\n" % output_path

    except:
        print "Catched error while converting :( "
        print "######## Traceback: #########"
        tb = traceback.format_exc()
    else:
        tb = None
    finally:
        if tb is not None:
            print tb


def indent(element, level=0):
    '''
    Allows pretty print (inplace!) for xml trees. just call
    indent(tree.getroot()).
    :param element: Root element of the tree.
    :param level: Level for indents.
    '''
    i = "\n" + level * "    "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = i + "    "
        if not element.tail or not element.tail.strip():
            element.tail = i
        for element in element:
            indent(element, level + 1)
        if not element.tail or not element.tail.strip():
            element.tail = i
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = i


if __name__ == '__main__':

    parser = OptionParser(usage="Usage: %prog PATH_TO_INI_FILE",
                          version="%prog 0.1")

    parser.add_option("-o", "--output",
                      action="store",
                      dest="output",
                      default="/tmp/output.scxml",
                      help=
                      "Set output path, the default is: [/tmp/output.scxml]")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        parser.error("Wrong number of arguments, RTFM!")

    parse_ini_file(open(args[0]), options.output)
