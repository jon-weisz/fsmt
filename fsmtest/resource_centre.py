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

import psutil
import eventlet


class ResourceCentre:
    """
    Container class to gather information about the used resources of the
    FSMT program itself for profiling purposes.
    """

    def __init__(self, pid):
        """
        :param pid:
        """
        self.max_cpu = 0.0
        self.avg_cpu = 0.0
        self.max_mem = 0.0
        self.max_thr = 0.0
        self.cycle = 0.0
        self.proc = psutil.Process(int(pid))
        self.name = self.proc.name
        self.path = self.proc.cmdline
        self.user = self.proc.username
        self.exit = False
        self.caller = ""

    def stop(self):
        """
        TODO
        """
        self.exit = True

    def get_average_cpu(self):
        """
        :return:
        """
        return self.avg_cpu / self.cycle

    def resource_counter(self, _caller="nodody"):
        """
        TODO
        """
        p = self.proc
        self.caller = _caller
        while not self.exit:
            self.cycle += 1.0
            cpu_consumption = p.get_cpu_percent(interval=0.6)
            self.avg_cpu += cpu_consumption
            mem_consumption = p.get_memory_percent()
            threads = p.get_num_threads()
            if cpu_consumption > self.max_cpu:
                self.max_cpu = cpu_consumption
            if mem_consumption > self.max_mem:
                self.max_mem = mem_consumption
            if threads > self.max_thr:
                self.max_thr = threads
            eventlet.sleep(0.06)
