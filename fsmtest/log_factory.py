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

from fsmtest.utils import mkdir_p
from logging import currentframe
from termcolor import colored
import logging.handlers
import os
import sys
import threading
import time
import traceback


class ColorLog(object):
    '''
    Wrapper hook class to realise coloured terminal output for the log.
    '''
    colormap = dict(
        debug=dict(color='grey', attrs=['bold']),
        info=dict(color='green'),
        warn=dict(color='yellow', attrs=['bold']),
        warning=dict(color='yellow', attrs=['bold']),
        error=dict(color='red'),
        critical=dict(color='red', attrs=['bold', 'underline']),
        # TODO: Check why outline is not working
        outline=dict(color='blue'))

    def __init__(self, logger):
        """
        :param logger:
        """
        self.custom_logger = logger

        def find_caller_no_lambda():
            """
            Find the stack frame of the caller so that we can note the source
            file name, line number and function name.
            """
            f = currentframe()
            # On some versions of IronPython, currentframe() returns None if
            # IronPython isn't run with -X:Frames.
            if f is not None:
                f = f.f_back
            rv = "(unknown file)", 0, "(unknown function)"
            while hasattr(f, "f_code"):
                co = f.f_code
                filename = os.path.normcase(co.co_filename)
                if filename == logging._srcfile or \
                        filename.find('fsmtest/Utils.py') > 0 or \
                        f.f_code.co_name == "<lambda>":  # New line
                    f = f.f_back  # Original line for context.
                    continue      # Original line for context.
                rv = (co.co_filename, f.f_lineno, co.co_name)
                break
            return rv

        self.custom_logger.findCaller = find_caller_no_lambda

    def __getattr__(self, name):
        """
        :param name:
        :return:
        """
        if name in ['debug', 'info', 'warn', 'warning',
                    'error', 'critical', 'outline']:
            return lambda s, *args: getattr(self.custom_logger, name)(
                colored(s, **self.colormap[name]), *args)
        return getattr(self.custom_logger, name)


class LogFactory(object):

    '''
    Singlet factory to create a unified logger for the entire FSMT system.
    '''

    _instance = None
    _isSetup  = False

    def __new__(cls, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        if not cls._instance:
            cls._instance = super(LogFactory, cls).\
                __new__(cls, *args, **kwargs)
        return cls._instance

    def _setup_custom_logger(self, use_colour_logging,
                             level="INFO",
                             log_file_level="NOTSET",
                             disable_all_logging=False,
                             log_to_console=True,
                             log_to_file=True,
                             enable_stream=True,
                             logging_directory="/tmp/FSMtest/"):
        '''
        Private function which sets up everything.

        :param use_colour_logging:
        :param level:
        :param log_file_level:
        :param disable_all_logging:
        :param log_to_console:
        :param log_to_file:
        :param enable_stream:
        :param logging_directory:
        '''

        self._use_colour_logging = use_colour_logging

        stream_level = 5
        center_integer = 5
        level_names = {
            50: '[CRITICAL]'.center(center_integer),
            40: '[ERROR]'.center(center_integer),
            30: '[WARNING]'.center(center_integer),
            20: '[INFO]'.ljust(center_integer),
            10: '[DEBUG]'.center(center_integer),
            stream_level: '[STREAM]'.center(center_integer),
            0:  '[NOTSET]'.center(center_integer),
            '[CRITICAL]': 50, '[ERROR]': 40,
            '[WARN]': 30, '[WARNING]': 30,
            '[INFO]': 20, '[DEBUG]': 10,
            '[STREAM]': stream_level, '[NOTSET]': 0,
        }

        class SingleLevelFilter(logging.Filter):

            '''
            A filter for the new level.
            '''

            def __init__(self, passlevel, stream_level, reject):
                '''
                Constructor.

                :param passlevel:
                :param stream_level:
                :param reject:
                '''
                self.passlevel = passlevel
                self.reject = reject
                self.stream_level = stream_level

            def filter(self, record):
                '''
                The filtering method.
                :param record:
                '''
                if self.reject:
                    return (record.levelno > self.passlevel) \
                        and (record.levelno != self.stream_level)
                else:
                    return (record.levelno <= self.passlevel) \
                        or (record.levelno == self.stream_level)

        #======================================================================
        # Defining the formatter
        #======================================================================
        format_date = "%H:%M:%S"

        format_args_part_a = dict(color='white',
                                  attrs=['bold'])
        format_args_part_b = dict(color='white',
                                  attrs=['bold', 'underline'])

        format_a  = '%(asctime)s %(levelname)s ['
        format_b  = '%(module)s.py@%(lineno)d'
        format_c1 = ']:'
        format_d1 = ' %(message)s'
        format_c2 = ']: %(message)s'

        format_a_info  = '%(asctime)s %(levelname)s'
        format_c1_info = ':'
        format_d1_info = ' %(message)s'

        no_colour_log_formatter = logging.Formatter(
            fmt=format_a + format_b + format_c2,
            datefmt=format_date)

        if use_colour_logging and level != "INFO":
            log_formatter = logging.Formatter(
                fmt=colored(format_a, **format_args_part_a) +
                colored(format_b, **format_args_part_b) +
                colored(format_c1, **format_args_part_a) +
                format_d1, datefmt=format_date)
        else:
            log_formatter = logging.Formatter(
                fmt=format_a + format_b + format_c2,
                datefmt=format_date)

        if use_colour_logging and level == "INFO":
            log_formatter = logging.Formatter(
                fmt=colored(format_a_info, **format_args_part_a) +
                colored(format_c1_info, **format_args_part_a) +
                format_d1_info, datefmt=format_date)
        else:
            log_formatter = logging.Formatter(
                fmt=format_a + format_b + format_c2,
                datefmt=format_date)

        # Deactivates logging in the statemachine but also suppresses own logs
        # in the custom_executable.
        # TODO: investigate
        # logging.get_logger("pyscxml").propagate = False

        #======================================================================
        # Create the logger
        #======================================================================
        if use_colour_logging:
            logger = ColorLog(logging.getLogger())
        else:
            logger = logging.getLogger()

        logger.setLevel(logging.NOTSET)
        logging._levelNames = level_names
        logging.STREAM = stream_level

        try:
            self._level = getattr(logging, level)
        except AttributeError:
            print "########################################################"
            print "# ERROR - Level '%s' is unknown! Using 'INFO' instead. #"
            print "########################################################"
            self._level = logging.INFO

        self._log_file_level = eval("logging." + log_file_level)

        if disable_all_logging:
            logger.disabled = 1
        import types

        #======================================================================
        # Add the stream level
        #======================================================================
        logger.enableStream = enable_stream

        def stream(self, msg, *args, **kwargs):
            if self.enableStream and self.isEnabledFor(stream_level):
                self._log(stream_level, msg, args, **kwargs)

        f = types.MethodType(stream, logger, logging.RootLogger)
        logger.stream = f  # add method to specific instance

        # Logging to console
        if log_to_console:
            # Logging to stdout
            console_handler_STDOUT = logging.StreamHandler(sys.stdout)
            STDOUT_console_filter = SingleLevelFilter(
                logging.INFO, logging.STREAM, False)  # @UndefinedVariable
            console_handler_STDOUT.addFilter(STDOUT_console_filter)
            console_handler_STDOUT.setLevel(self._level)
            console_handler_STDOUT.setFormatter(log_formatter)
            logger.addHandler(console_handler_STDOUT)

            # Logging to stderr
            console_handler_STDERR = logging.StreamHandler(sys.stderr)
            STDERRconsoleFilter = SingleLevelFilter(
                logging.INFO, logging.STREAM, True)  # @UndefinedVariable
            console_handler_STDERR.addFilter(STDERRconsoleFilter)
            console_handler_STDERR.setLevel(self._level)
            console_handler_STDERR.setFormatter(log_formatter)
            logger.addHandler(console_handler_STDERR)

        # logging to file
        if log_to_file:
            if not os.path.exists(logging_directory):
                mkdir_p(logging_directory)
            username = os.getenv("USER", "unknown")
            curTime = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(logging_directory, "FSMT-" +
                                    username + "-" + str(curTime)
                                    + "_full.log")

            file_handler = logging.handlers.RotatingFileHandler(
                filename,
                mode='a',
                maxBytes=3145728,
                backupCount=5)
            file_handler.setLevel(self._log_file_level)
            file_handler.setFormatter(no_colour_log_formatter)
            logger.addHandler(file_handler)

        # replace excepthook (allows to log exceptions and asserts :) )
        def _replacement_excepthook(type, value, tracebk, thread=None):
            """Replacement for sys.excepthook."""
            # collect traceback info
            tb = "".join(traceback.format_exception(type, value, tracebk))
            if thread:
                if not isinstance(thread, threading._MainThread):
                    tb = "Exception in thread %s:\n%s" % (thread.getName(), tb)

            # log all the gathered info
            logger.critical(tb)

        _old_sys_excepthook = sys.excepthook
        sys.excepthook = _replacement_excepthook

        return logger

    def set_up(self, use_colour_logging, level, log_folder, log_file_level):
        """
        Public wrapper for the private function.

        :param use_colour_logging:
        :param level:
        """
        self.log = self._setup_custom_logger(use_colour_logging,
                                             level=level,
                                             log_file_level=log_file_level,
                                             logging_directory=log_folder)
        self._isSetup = True
        return self.log

    def get_logger(self):
        """
        :return:
        """
        if self._isSetup:
            return self.log

    def gl(self):
        """
        :return:
        """
        if self._isSetup:
            return self.log
