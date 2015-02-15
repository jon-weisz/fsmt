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

import time
import unittest
import eventlet
import subprocess
from fsmtest.launcher import *
from fsmtest.parser import fsminiparser
from fsmtest.resource_centre import ResourceCentre


class Test(unittest.TestCase):
    def setUp(self):
        self.current_cpu_avg = 0.001
        pass

    def tearDown(self):
        pass

    def test_launch_fsmtest_0(self):
        print "Starting test_launch_fsmtest_0"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq0.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 6.5)
        self.assertGreater(duration, 2)

    def test_launch_fsmtest_1(self):
        print "Starting test_launch_fsmtest_1"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq1.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 10)
        self.assertGreater(duration, 5)

    def test_launch_fsmtest_2(self):
        print "Starting test_launch_fsmtest_2"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq2.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 11)
        self.assertGreater(duration, 5)

    def test_launch_fsmtest_3(self):
        print "Starting test_launch_fsmtest_3"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq3.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 16)
        self.assertGreater(duration, 12)

    def test_launch_fsmtest_4(self):
        print "Starting test_launch_fsmtest_4"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq4.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 15)
        self.assertGreater(duration, 10)

    def test_launch_fsmtest_5(self):
        print "Starting test_launch_fsmtest_5"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq5.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 11)
        self.assertGreater(duration, 6)

    def test_launch_fsmtest_6(self):
        print "Starting test_launch_fsmtest_6"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq6.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 15)
        self.assertGreater(duration, 10)

    def test_launch_fsmtest_7(self):
        print "Starting test_launch_fsmtest_7"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq7.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 6)
        self.assertGreater(duration, 3)

    def test_launch_fsmtest_8(self):
        print "Starting test_launch_fsmtest_8"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq8.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 11)
        self.assertGreater(duration, 6)

    def test_launch_fsmtest_9(self):
        print "Starting test_launch_fsmtest_9"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq9.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 10)
        self.assertGreater(duration, 6)

    def test_launch_fsmtest_10(self):
        print "Starting test_launch_fsmtest_10"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq10.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 13)
        self.assertGreater(duration, 5)

    def test_launch_fsmtest_11(self):
        print "Starting test_launch_fsmtest_11"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq11.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 3)
        self.assertGreater(duration, 1)

    def test_launch_fsmtest_12(self):
        print "Starting test_launch_fsmtest_12"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq12.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 18)
        self.assertGreater(duration, 10)

    def test_launch_fsmtest_13(self):
        print "Starting test_launch_fsmtest_13"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq13.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 8)
        self.assertGreater(duration, 2)

    def test_launch_fsmtest_14(self):
        print "Starting test_launch_fsmtest_14"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq14.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 6)
        self.assertGreater(duration, 2)

    def test_launch_fsmtest_15(self):
        print "Starting test_launch_fsmtest_15"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq15.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertGreater(duration, 21)
        self.assertLess(duration, 26)

    def test_launch_fsmtest_16(self):
        print "Starting test_launch_fsmtest_16"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq16.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        sub_proc_ret_code = sub_process.wait()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertGreater(duration, 2)
        self.assertLess(duration, 6)

    def test_launch_fsmtest_regression_1(self):
        print "Starting test_launch_fsmtest_regression_1"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq11.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        pid = sub_process.pid
        rc = ResourceCentre(int(pid))
        print "PID" + str(pid)
        rc_spawn = eventlet.spawn(rc.resource_counter, "reg1")
        sub_proc_ret_code = sub_process.wait()
        rc.stop()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual("reg1", rc.caller)
        self.assertEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 3)
        self.assertGreater(duration, 1)
        self.current_cpu_avg = rc.get_average_cpu()
        # This is much more because the internal logger does
        # not take the startup phase into account, however.
        # We need to check this for regression testing
        self.assertLess(self.current_cpu_avg, 20)
        rc_spawn.kill()

    def test_launch_fsmtest_regression_2(self):
        print "Starting test_launch_fsmtest_regression_2"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq8.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        pid = sub_process.pid
        print "PID" + str(pid)
        rc = ResourceCentre(int(pid))
        rc_spawn = eventlet.spawn(rc.resource_counter, "reg2")
        sub_proc_ret_code = sub_process.wait()
        rc.stop()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual("reg2", rc.caller)
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 11)
        self.assertGreater(duration, 6)
        self.current_cpu_avg = rc.get_average_cpu()
        # This is much more because the internal logger does
        # not take the startup phase into account, however.
        # We need to check this for regression testing
        self.assertLess(self.current_cpu_avg, 20)
        rc_spawn.kill()

    def test_launch_fsmtest_regression_3(self):
        print "Starting test_launch_fsmtest_regression_3"
        cmd = ["../../bin/fsmt", "../data/scxml/launchtests_seq5.scxml"]
        sub_process = subprocess.Popen(cmd)
        t0 = time.time()
        pid = sub_process.pid
        rc = ResourceCentre(int(pid))
        rc_spawn = eventlet.spawn(rc.resource_counter, "reg3")
        sub_proc_ret_code = sub_process.wait()
        rc.stop()
        t1 = time.time()
        duration = t1 - t0
        self.assertEqual("reg3", rc.caller)
        self.assertEqual(sub_proc_ret_code, 0)
        self.assertNotEqual(sub_proc_ret_code, 1)
        self.assertNotEqual(sub_proc_ret_code, -9)
        self.assertNotEqual(sub_proc_ret_code, -15)
        self.assertNotEqual(sub_proc_ret_code, -2)
        self.assertLess(duration, 12)
        self.assertGreater(duration, 6)
        self.current_cpu_avg = rc.get_average_cpu()
        # This is much more because the internal logger does
        # not take the startup phase into account, however.
        # We need to check this for regression testing
        self.assertLess(self.current_cpu_avg, 20)
        rc_spawn.kill()


if __name__ == "__main__":
    unittest.main()
