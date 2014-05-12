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


class XUnitTestCase(object):

    '''
    Class representing a xUnit test case. The XunitXml accepts
    these and uses them to create x xunit XML tree.
    '''

    def __init__(self, name, contents, test_type=""):
        '''
        Constructor.

        :param name:
        :param contents:
        :param test_type:
        '''
        self.name = name
        self.contents = contents
        self.test_type = test_type

    def is_failure(self):
        '''
        Allows to determine if a test case is a failure.
        '''
        return self.test_type == "failure"
