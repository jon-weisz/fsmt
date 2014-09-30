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

from websocket import create_connection
import sys
import socket
import string
import random
import json


class WebSocketConnection():

    def __init__(self):
        """
        TODO
        """
        self.random_string = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in range(8)
        )
        # self.raw_message = json.loads('{ "name": "fsmtest", "events": [] }')
        self.json_message = json.loads('{ "name": "fsmtest", "events": [] }')
        self.is_connected = False
        self.ws = None
        try:
            self.ws = create_connection("ws://localhost:8008/")
        except socket.error, e:
            pass
        if not self.ws is None:
            self.is_connected = True

    def set_current_message(self, update):
        self.json_message = update

    def get_current_message(self):
        return self.json_message

    def get_raw_message(self):
        return json.loads('{ "name": "fsmtest", "events": [] }')

    def get_outer_event(self):
        return {
            "name": "name",
            "time": "0",
            "state": "init",
            "component": "init"
        }

    def get_inner_event(self):
        return {
            "name": "eventname",
            "events": [{
                    "name": "eventname",
                "time": "0",
                "state": "init",
                "component": "init"
            }]
        }

    def get_is_connected(self):
        """
        :return:
        """
        return self.is_connected

    def end(self):
        """
        TODO
        """
        self.ws.close()

    def send_update(self):
        """
        TODO
        """
        if self.is_connected:
            if int(sys.getsizeof(json.dumps(self.json_message)) < 16384):
                self.ws.send(json.dumps(self.json_message))
            else:
                print "Warning: Web Socket Message too big > 16384 byte"
        else:
            print "Warning, not connected to Web Socket server"
