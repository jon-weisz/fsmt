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

import xml.etree.ElementTree as ET
import xml.dom.minidom


class XunitXmlBuilder(object):

    """
    Class to create a xunit test xml file. After initial build, one can add
    test cases via the constructor (list) or one by one with the add_test_case
    method. Next, calling write_xml will cause _build_xunit_xml to be executed
    and the XML is created and written to the given path.
    """

    def __init__(self, testsuit_name, xml_path, test_cases=None):
        '''
        Constructor.

        :param testsuit_name:
        :param test_cases:
        :param total_tests:
        :param total_failures:
        '''
        self.testsuit_name = testsuit_name

        if test_cases:
            self.test_cases = test_cases
        else:
            self.test_cases = []

        self.xml_path = xml_path
        self.failing_test_cases = self._get_failing_test_cases()

    def _get_failing_test_cases(self):
        '''
        Internal helper to determine the number of failed tests.
        '''
        return set([a_case for a_case in self.test_cases
                    if a_case.is_failure()])

    def _build_xunit_xml(self):
        '''
        Creates a xml tree from a given testsuite name and testcase
        '''

        total_tests = len(self.test_cases)
        total_failures = len(self.failing_test_cases)
        self.xml_root = ET.Element("testsuite",
                                   {
                                       "name": unicode(self.testsuit_name),
                                       "failures": unicode(total_failures),
                                       "tests": unicode(total_tests)
                                   }
                                   )

        for a_case in self.test_cases:
            test_case_element = ET.SubElement(
                self.xml_root,
                "testcase",
                {"name": unicode(a_case.name)})
            if a_case.is_failure():
                failure_element = ET.Element("failure")
                failure_element.text = a_case.contents
                test_case_element.append(failure_element)

    def add_test_case(self, a_testcase):
        '''
        Adds a testcase to the list of test cases. Duh! :D
        :param a_testcase:
        '''
        self.test_cases.append(a_testcase)

    def get_xml_content(self, prettyForamt=True):
        '''
        Returns the xUnit XML tree as a string.

        :param prettyForamt: Pretty pretty please with sugar on top!
        '''

        self._build_xunit_xml()

        result = ET.tostring(self.xml_root)
        if prettyForamt:
            dom = xml.dom.minidom.parseString(result)
            result = dom.toprettyxml()
        return result

    def write_xml(self, xml_path=None):
        '''
        Method to write the XML file.
        :param path: Override the path given in the setup.
        '''
        if xml_path:
            self.xml_path = xml_path

        a_file = open(self.xml_path, 'w')
        a_file.write(self.get_xml_content())
        a_file.close()
