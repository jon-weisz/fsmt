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
import sys
import time
import ctypes
import psutil
import signal
import subprocess
import multiprocessing
from fsmtest.utils import mkdir_p


class FSMTstarter(multiprocessing.Process):
	"""
	Starts a FSMT instance in its own process.
	"""

	def __init__(self, scxml_file_, log_folder_):
		multiprocessing.Process.__init__(self)
		self.scxml_file = scxml_file_
		self.log_folder = log_folder_

	def run(self):
		time.sleep(.5)
		FNULL = open(os.devnull, 'w')
		_ = subprocess.Popen([
								 "fsmtest",
								 self.scxml_file,
								 "--nocolour",
								 "--output=" + self.log_folder,
								 "-l ERROR"],
								stdout=FNULL,
								stderr=FNULL
		)
		FNULL.close()


class ProcessExitTimeExtractorMuchPreciseVerySmart(multiprocessing.Process):
	"""
	Wrapper class which looks for the precise end of a certain process.
	"""

	exit_time = -1

	def __init__(self, a_process):
		"""
		Constructor which sets communication vaulue.
		:param a_pid:
		"""
		multiprocessing.Process.__init__(self)
		self.process = a_process
		self.exit_time = multiprocessing.Value(ctypes.c_double, 0.0)

	def run(self):
		"""
		Run dos run.
		"""
		self.process.wait()
		self.exit_time.value = time.time()


class MySubprocessDataType():
	"""
	Meta container class which holds detailed information of a spawned process.
	"""

	name = ""
	pid = -1
	start_time = 1
	_end_time = -1
	_duration = -1

	def __init__(self, a_subprocess):
		"""
		Constructor.

		:param a_subprocess: The subprocess from which meta data will be
							gathered
		"""
		self.cmdline = a_subprocess.cmdline
		self.name = a_subprocess.name
		self.pid = a_subprocess.pid
		self.start_time = a_subprocess.create_time
		self.exit_time_extractor = \
			ProcessExitTimeExtractorMuchPreciseVerySmart(a_subprocess)
		self.exit_time_extractor.start()

	def get_end_time(self):
		"""
		Extracts the end time of a process if possible.

		:returns the exit time of the process or -1 if it is still running.
		"""

		if not self.exit_time_extractor.is_alive():
			if self._end_time == -1:
				self._end_time = self.exit_time_extractor.exit_time.value
			return self._end_time
		else:
			return -1

	def get_duration(self):
		"""
		Calculates and returns the duration the process ran for.
		"""

		if self._end_time != -1:
			self._duration = self._end_time - self.start_time
		return self._duration


def gather_process_data(process_name):
	"""
	Gathers all the needed information of a process and its sub-processes
	and returns it.
	"""

	# Loop looking for a FSMT instance
	while True:
		start_time, process_instance = find_process_instance(process_name)
		if start_time is not None and process_instance is not None:
			break
		time.sleep(0.01)

	# The following happens once we found a FSMT instance!
	process_name = process_instance.name
	process_pid = process_instance.pid

	# Process to extract exact exit time.
	process_exit_time_extractor = \
		ProcessExitTimeExtractorMuchPreciseVerySmart(process_instance)
	process_exit_time_extractor.start()

	# While the other process searches for the end time, we can focus on
	# finding subprocesses.
	subprocess_order = []
	subprocess_order_pids = []

	while True:
		# This assumes that a process looks after its children
		if not process_exit_time_extractor.is_alive():
			end_time = process_exit_time_extractor.exit_time.value
			break

		children = []
		try:
			children = process_instance.get_children()
		except Exception, _:
			# process might be gone in between ...
			pass

		if len(children) > 0:
			for a_subprocess in children:
				if a_subprocess.pid not in subprocess_order_pids:
					subprocess_order.append(MySubprocessDataType(a_subprocess))
					# easier ...
					subprocess_order_pids.append(a_subprocess.pid)

		time.sleep(0.1)

	return (process_instance, process_pid, process_name, start_time,
			end_time, (end_time - start_time), subprocess_order)


def find_process_instance(PROCNAME):
	"""
	Searches for the FSMT instance
	"""
	for a_process in psutil.process_iter():
		if a_process.name == PROCNAME:
			start_time = a_process.create_time
			# print "Found FSMT instace: ", start_time
			return (start_time, a_process)
	return None, None


def test_fsmt_functionality(file_, runs, output):
	"""
	Tests the correct functionality of FSMT by repeatedly running FSMT
	for a certain SCXML and logging launching times.
	"""

	# Get the options
	scxml_file_to_test = file_
	number_of_runs_to_do = int(runs)
	log_folder = os.path.join(output,
							  str(time.strftime("%m-%d_%H%M%S",
												time.localtime())))
	log_folder_fsmt_runs = os.path.join(log_folder, "fsmt_runs")

	if not os.path.exists(scxml_file_to_test):
		print "Error - SCXML file not found at %s\n\nexiting" % \
			  scxml_file_to_test
		sys.exit(1)

	if not os.path.exists(log_folder_fsmt_runs):
		try:
			mkdir_p(log_folder_fsmt_runs)
		except Exception, e:
			print "Error creating log folder(s) at %s! MSG: %s" % \
				  (log_folder, e)
			sys.exit(1)

	# Sanity check
	if not os.access(log_folder, os.W_OK):
		print "Exiting, logging path " + log_folder + " is not " + \
			  "writable or does not exist."
		sys.exit(1)

	print "\n\nWriting verification log files to %s\n\n" % log_folder

	# Create the log files
	output_file = open(log_folder + "/functionality_verification_result.csv",
					   "w")
	output_file.write(
		'"process_name","pid","start_time","exit_time","process_duration",' +
		'"num_subprocess","subp_name;subp_pid;subp_start_time;' +
		'subp_end_time;subp_duration,all_durations"\n')
	output_file.flush()

	process_order_file = open(
		log_folder +
		"/functionality_verification_process_order.csv",
		"w")
	process_order_file.write('"run","order"\n')
	process_order_file.flush()

	intervall_file = \
		open(log_folder + "/functionality_verification_result_intervalls.csv",
			 "w")

	# Ensure CTRL+C is handled correctly
	global interruption
	interruption = False
	global masterPID
	masterPID = os.getpid()

	def signal_handler(signal, frame):
		global interruption
		global masterPID
		if os.getpid() == masterPID:
			print '\n\nDetected Ctrl+C! Ending current FSMT run.\n\n'
			interruption = True

	signal.signal(signal.SIGINT, signal_handler)

	flag = True
	counter = 1
	while counter <= number_of_runs_to_do and not interruption:
		print "Running and observing FSMT (run %d of %d)" % \
			  (counter, number_of_runs_to_do)

		# Start an instance of FSMT
		fsmt_starter = FSMTstarter(scxml_file_to_test, log_folder_fsmt_runs)
		fsmt_starter.start()

		# Find the FSMT and get all its info
		# print "Looking for FSMT instance ..."

		_, fsmt_pid, fsmt_name, fsmt_start_time, fsmt_end_time, \
		fsmt_duration, subprocess_order = \
			gather_process_data("fsmtest")

		print "  L__ Finished - FSMT ran for %.3fs" % fsmt_duration
		# , "start ", fsmt_start_time, "end ", fsmt_end_time

		# Write the results
		output_file.write("%s,%s,%f,%f,%f,%d," % (fsmt_name,
												  fsmt_pid,
												  fsmt_start_time,
												  fsmt_end_time,
												  fsmt_duration,
												  len(subprocess_order)))

		process_order_file.write("%d," % counter)
		final_order_string = ""
		for a_subprocess in subprocess_order:
			final_order_string += "%s," % " ".join(a_subprocess.cmdline)
			output_file.write("%s;" % a_subprocess.name)
			output_file.write("%d;" % a_subprocess.pid)
			output_file.write("%f;" % a_subprocess.start_time)
			output_file.write("%f;" % a_subprocess.get_end_time())
			output_file.write("%f," % (a_subprocess.get_duration()))

		# get rid of last ';'
		if len(final_order_string) > 0:
			final_order_string = final_order_string[:-1]
		final_order_string += "\n"
		process_order_file.write(final_order_string)
		process_order_file.flush()

		for a_subprocess in subprocess_order:
			output_file.write("%f," % (a_subprocess.get_duration()))

		output_file.write("\n")
		output_file.flush()

		if flag:
			flag = False

			for i in range(0, len(subprocess_order)):
				intervall_file.write('"intervall_%d_duration","process_%d_duration",' % (i, i))
			intervall_file.write('"end_intervall_duration","total_duration"\n')
			intervall_file.flush()

		last_start_time = fsmt_start_time
		for a_subprocess in subprocess_order:
			intervall_file.write('%f,' %
								 (a_subprocess.start_time - last_start_time))
			intervall_file.write('%f,' % a_subprocess.get_duration())
			last_start_time = a_subprocess.start_time

		if len(subprocess_order) > 0:
			intervall_file.write('%f,%f\n' % (fsmt_end_time - subprocess_order[- 1].get_end_time(), fsmt_duration))
		else:
			print "     L__ Warning: No subprocesses were spawned by FSMT!"
			intervall_file.write('%f,%f\n' % (-1, fsmt_duration))
		intervall_file.flush()
		counter += 1
