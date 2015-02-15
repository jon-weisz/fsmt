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

import eventlet


class ExitWatcher(object):
    """
    Watcher for ctrl+c interception.
    """

    # Evil. See: http://eventlet.net/doc/basic_usage.html#eventlet.monkey_patch
    eventlet.monkey_patch()

    def __init__(self, state_machine_):
        """
        :param state_machine:
        """
        self.state_machine = state_machine_
        self.close_exit_watcher = False
        self.state_machine.log.debug("Emergency Exit Watcher initialised")

    def close(self, end):
        """
        :param end:
        """
        self.close_exit_watcher = end

    def do_watch(self):
        """
        Watches for the
        """
        while self.close_exit_watcher is False:
            if self.state_machine.exit_grace:
                self.state_machine.send("external_abortion")
                # self.state_machine.send("wait.finish")
                self.state_machine.log.debug(
                    "CTRL+C detected - Closing Exit Watcher")
                self.close_exit_watcher = True
                break
            if self.close_exit_watcher:
                self.state_machine.log.debug(
                    "Closing Exit Watcher, called close")
                break
            else:
                eventlet.sleep(0.1)