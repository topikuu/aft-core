# Copyright (c) 2013-14 Intel, Inc.
# Author igor.stoppa@intel.com
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

"""
Abstract Model of a Command Line tool.
"""

import abc
import sys
import logging
import subprocess
import multiprocessing

VERSION = "0.1.0"


# pylint: disable=too-few-public-methods
class CmdLineTool(object):
    """
    Abstract Base Class for wrapping cmdline tools.
    """
    __metaclass__ = abc.ABCMeta
    DEFAULT_TIMEOUT = 5

    @classmethod
    def init_class(cls, command=None, timeout=DEFAULT_TIMEOUT,
                   exit_on_error=False):
        """
        Init function for class variables.
        """
        cls.command = command
        cls._exit_on_error = exit_on_error
        cls._timeout = timeout
        return cls._probe_command()

    @classmethod
    def _probe_command(cls):
        """
        Tests if a certain shell command is available.
        Can either return error or throw an exception.
        """
        logging.info("Testing for presence of \"{0}\" command."
                     .format(cls.command))
        try:
            subprocess.check_output(["which", cls.command],
                                    stderr=subprocess.STDOUT)
            logging.info("Command {0} found.".format(cls.command))
            return True
        except subprocess.CalledProcessError:
            logging.critical("Error: cannot locate {0} command."
                             .format(cls.command))
            if cls._exit_on_error:
                sys.exit(-1)
            return False

    @classmethod
    def _run(cls, parms=(), timeout=-1, verbose=False):
        """
        Runs the command in a separate thread, with timeout.
        """
        result_q = multiprocessing.Queue()
        result = False
        process = multiprocessing.Process(target=_runner,
                                          args=[cls.command, parms,
                                                result_q, verbose])
        timeout = cls._timeout if timeout == -1 else timeout
        try:
            process.start()
            process.join(timeout=timeout)
            if process.is_alive():
                process.terminate()
                process.join()
            else:
                result = result_q.get()
        except multiprocessing.TimeoutError:
            logging.warn("Command timedout:"
                         "{0} {1}".format(cls.command, parms))
        if cls._exit_on_error and result is False:
            sys.exit(-1)
        return result


def _runner(command, parms, result_q, verbose=False):
    """
    Executes the command with the given parameters.
    It's meant to run from a thread with timeout.
    """
    try:
        command = (command,) + parms
        if verbose:
            logging.debug("{0}".format(command))
        process = subprocess.Popen(command,
                                   stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE,)
        stdoutdata, stderrdata = process.communicate()
        if process.returncode != 0:
            result_q.put(False)
            logging.debug("Error running:\n{0}\n".format(command) +
                          "Returned error code {0} and error message\n{1}".
                          format(process.returncode, stderrdata))
        result_q.put(stdoutdata)
    except OSError as error:
        logging.debug("OSError running:\n{0}\n".format(command) +
                      "Returned error code {0} and error message\n{1}".
                      format(error.errno, error.strerror))
        result_q.put(False)
# pylint: enable=too-few-public-methods
