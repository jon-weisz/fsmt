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


class ProcessExchangeData():
    """
    Data object used as exchange data between processes.
    """

    def __init__(self):
        """
        Constructor.
        TODO: Rename message to "name"
        """
        self.message = None
        self.successful = False
        self.pid = "None"
        self.counter_name = ""
        self.execution_type = "default"
        self.sender_id = ""
        self.parent_state = None
        self.type = "unset"

    def info_to_string(self):
        """
        :return:
        """
        a = ""
        for key, value in self.__dict__.iteritems():
            a += "%s: %s, " % (key, value)
        return a
