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

import unittest
from fsmtest.launcher import *
from fsmtest.parser import fsminiparser


class Test(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_parse_ini_file(self):
		print "------------------" + os.getcwd()
		for i in range(1, 5):
			cur_ini_file_str = '../data/ini/iniparser_cfg%s.ini' % str(i)
			cur_ini_file = open(cur_ini_file_str, 'r')
			cur_test_file_name = '/tmp/output_test_cfg%s.scxml' % str(i)
			cur_test_file_name_target = '../data/scxml/reference_output_cfg%s.scxml' % str(i)
			fsminiparser.parse_ini_file(cur_ini_file, cur_test_file_name,
										silent=True)
			self.assertMultiLineEqual("".join(open(cur_test_file_name, 'r').readlines()), "".join(open(cur_test_file_name_target, 'r').readlines()))


if __name__ == "__main__":
	unittest.main()
