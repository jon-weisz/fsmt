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

import os


class SoftwareComponent(object):

    def __init__(self):
        """
        TODO
        """
        self.name = "None"
        self.command = "None"
        self.path = "None"
        self.host = "localhost"
        self.check_types = []
        self.pid = "None"
        self.counter_name = ""
        self.parent_state = "None"
        self.execution_type = "default"
        self.check_execution = False
        self.identifier = id(self)
        self._girlfriend = "None"  # boo :(
        self._boyfriend = "flo"  # yay
        self.environment = None

    def add_check_type(self, check_type):
        """
        :param check_type:
        """
        self.check_types.append(check_type)

    def print_info(self):
        """
        TODO
        """
        import pprint

        pprint.pprint(self.__dict__)
        for a in self.check_types:
            pprint.pprint(a.__dict__)

    def get_complete_executable_path_with_arguments(self):
        if self.environment:
            os.environ = self.environment
        return os.path.expandvars(os.path.join(self.path, self.command))

    def path_and_command_is_valid(self):
        """
        :return:
        """
        if self.command is None:
            return False
        if self.path is None:
            return False
        if not os.path.exists(
                self.get_complete_executable_path_with_arguments().split()[0]):
            return False
        return True

    def _contains(self, list_, filter_):
        """
        :param list:
        :param filter:
        :return:
        """
        for x in list_:
            if filter_(x):
                return True
        return False

    def has_blocking_observers(self):
        """
        :return:
        """
        return self._contains(self.check_types, lambda x: x.blocking)
