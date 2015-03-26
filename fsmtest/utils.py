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

import os
import errno
import psutil
import signal
import zipfile
import eventlet


def join_environment_variable_map_A_into_B(a, b):
    """
    Joins 2 environment variable dicts. duplicated entries are overwritten.

    :param a:
    :param b:
    """
    for an_a in a.keys():
        if an_a in b.keys():
            if b[an_a] != a[an_a]:
                b[an_a] = a[an_a]
        else:
            b[an_a] = a[an_a]
    return b


def update_environment_setup(sm):
    """
    :param state_machine:
    :return:
    """
    if not hasattr(sm, "environment_setup"):
        environment_map = {}
        environment_elements = sm.datamodel['environment']
        for an_elem in environment_elements:
            if an_elem.tag[1:].split("}")[1] == "variable":
                environment_map[an_elem.get('var')] = \
                    os.path.expandvars(an_elem.get('val'))
            else:
                sm.log.warning(
                    ("Wrong/Unknown tag in SCXML environment " +
                     "setup datamodel: %s"), an_elem.tag[1:].split("}")[1])
        sm.environment_setup = join_environment_variable_map_A_into_B(
            environment_map, os.environ.copy())
    return sm.environment_setup


def log_process_pids(proc_exec, log):
    """
    :param processes:
    :param log:
    """
    kill_list = ""
    for one_program_executor in proc_exec.keys():
        if one_program_executor.subprocess:
            if one_program_executor.subprocess.pid is not None:
                kill_list += "%s " % one_program_executor.subprocess.pid
    log.debug("These components will be ended now: %s" % kill_list)


def end_process_and_children(pid, process, log, kill_timeout):
    """
    :param pid:
    :param process:
    :param log:
    """
    if process.poll() is None:
        log.debug("Before killing, look for children of %s..." % str(pid))
        ret_child = kill_child_processes(pid, log, kill_timeout)
        if ret_child == 0:
            log.debug("Children of %s are all gone" % pid)
        else:
            log.debug("Error: Not all children of %s could be killed" % str(pid))

        log.debug("Ending parent process %s now" % str(pid))
        is_gone = kill_pid(pid, log, kill_timeout)

        if is_gone > 0:
            log.warning("Status of %s still unknown" % str(pid))
        else:
            log.debug("Ended process %s successfully!" % str(pid))
    else:
        log.debug("Process %s is already un-pollable. Doing nothing" % str(pid))


def kill_pid(pid, log, kill_timeout):
    """
    :param pid:
    """

    # Double check children
    p = psutil.Process(int(pid))
    if p.is_running():
        log.info("---* Sending SIGINT to %s [%s]", p.name, p.pid)
        p.send_signal(signal.SIGINT)
        eventlet.sleep(kill_timeout)
    if p.is_running():
        log.info("----* Sending SIGTERM to %s [%s]", p.name, p.pid)
        p.send_signal(signal.SIGTERM)
        eventlet.sleep(kill_timeout)
    if p.is_running():
        log.info("-----* Sending SIGKILL to %s [%s] Wow!", p.name, p.pid)
        p.kill()
        eventlet.sleep(kill_timeout)

    # Making really sure it is dead.
    if p.is_running():
        return 1
    else:
        return 0


def kill_child_processes(parent_pid, log, kill_timeout, self_call=False):
    """
    :param log:
    :param parent_pid:
    :return:
    """
    result = 0
    log.log(5, "Called kill children of %s - self_call:%s", parent_pid, str(self_call))

    if os.path.exists("/proc/%s" % parent_pid):
        a_process = psutil.Process(int(parent_pid))
        proc_children = a_process.get_children()
        if len(proc_children) == 0:
            if self_call:
                log.log(
                    5,
                    "Child %s has no further children - end of recursion",
                    parent_pid)
                result += kill_pid(parent_pid, log, kill_timeout)
            else:
                log.log(5, "No self call, no children, returning")
                return 0
        else:
            log.log(5, "There are %d children" % len(proc_children))
            for p in proc_children:
                log.log(
                    5, "Check if child %s of %s has children - recursive call",
                    p.pid, parent_pid)
                result += kill_child_processes(p.pid, log, kill_timeout, self_call=True)
    else:
        log.warning("Process %s and children is/are already dead.", parent_pid)

    log.log(5, "Returning form kill child %s", parent_pid)
    return result


def seek_read(f, _pos):
    """
    :param f:
    :param window:
    :return:
    """
    BUFSIZ = 512
    pos = _pos
    data = []
    try:
        f.seek(pos, 0)
    except ValueError, _:
        return "IOERROR"
    data.append(f.read(BUFSIZ))
    return '\n'.join(''.join(data).splitlines()[:])


def write_fsm_file(tag, name, content):
    # Providing name for the file to be created
    """
    :param tag:
    :param name:
    :param content:
    """
    # 'a' will append, 'w' will over-write
    target = open(name, 'a')
    # Writing the entered content to the file we just created
    stamp = os.environ['FSMTRA']
    target.write("Run: " + stamp + " Status: " + tag)
    target.write(" " + content)
    target.write("\n")
    # Providing information that writing task is completed
    target.close()


def write_fsm_diag(name, content):
    # Providing name for the file to be created
    """
    :param tag:
    :param name:
    :param content:
    """
    target = open(name, 'w')
    # Writing the entered content to the file we just created
    target.write(" " + content)
    target.write("\n")
    # Providing information that writing task is completed
    target.close()


def make_zipfile(source, destination, compress=True):
    """
    Helper which allows to create a (compressed) zip file of a given folder.
    :param source: the folder to be compressed
    :param destination: the path to where the zip file should be written
    :param compress: optional switch to disable compression
    """
    if compress:
        compression_flag = zipfile.ZIP_DEFLATED
    else:
        compression_flag = zipfile.ZIP_STORED
    relroot = os.path.abspath(os.path.join(source, ".."))
    with zipfile.ZipFile(destination, "w", compression_flag) as a_zip:
        for root, _, files in os.walk(source):
            # add directory (needed for empty dirs)
            a_zip.write(root, os.path.relpath(root, relroot))
            for a_file in files:
                filename = os.path.join(root, a_file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot),
                                           a_file)
                    a_zip.write(filename, arcname)


def mkdir_p(path):
    """
    Helper which realises the same functionality as mkdir -p
    :param path: path to be created
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
