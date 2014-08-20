# Copyright (c) 2013-14 Intel, Inc.
# Author igor.stoppa@intel.com
# Based on original code from Antti Kervinen <antti.kervinen@intel.com>
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
Class implementing a Tester interface.
"""


import os
import time
import ConfigParser
import logging
from aft.classloader import ClassLoader

VERSION = "0.1.0"


# Disable "Too few public methods."
# This class is meant to perform one single task
# and therefore requires only one public method
# pylint: disable=too-few-public-methods
class Tester(object):
    """
    Class representing a Tester interface.
    """
    _TEST_MODULES = os.getenv("AFT_TEST_MODULES",
                              "/usr/share/aft/test_modules/")

    _TEST_EXEC_ROOT = os.getenv("AFT_EXECROOT", "./aft_results.")

    _start_time = 0
    _end_time = 0
    _results = []
    _required_test_cases = []
    _test_plan = []
    _xunit_results = ""

    @classmethod
    def init(cls, test_plan):
        """
        Initialization of Class variables
        """
        return cls._build_test_plan(test_plan_file=test_plan)

    @classmethod
    def _build_test_plan(cls, test_plan_file):
        """
        Gathers list of required test cases.
        """
        config = ConfigParser.SafeConfigParser()
        try:
            config.read(test_plan_file)
            for test_case_name in config.sections():
                tester = config.get(test_case_name, "tester")
                test = config.get(test_case_name, "test")
                parameters = config.get(test_case_name, "parameters")
                pass_regex = config.get(test_case_name, "pass_regex")
                user = config.get(test_case_name, "user")
                tester_class = ClassLoader.load_plugin(
                    class_name="".join([tester, "TestCase"]))
                if not callable(getattr(tester_class, test)):
                    logging.critical("Error in Test Plan {0}:"
                                     " no method {1} in test class {2}"
                                     .format(test_plan_file, test_case_name,
                                             tester))
                    return False

                cls._test_plan.append(
                    tester_class(
                        name=test_case_name,
                        test=test,
                        parameters=parameters,
                        pass_regex=pass_regex,
                        user=user))
        except (ImportError, AttributeError, ConfigParser.Error) as error:
            logging.critical("Error while loading test plan {0}:\n{1}"
                             .format(test_plan_file, error))
            return False
        if len(cls._test_plan) == 0:
            logging.warn("Building test plan: no test cases available.")
            return False
        return True

    @classmethod
    def _execute_test_plan(cls, device):
        """
        Execute the test plan.
        """
        if len(cls._test_plan) == 0:
            logging.warn("Executing the test plan: no test cases available.")
            return False
        cls._start_time = time.time()
        for test_case in cls._test_plan:
            test_case.execute(device=device)
        cls._end_time = time.time()
        return True

    @classmethod
    def _results_to_xunit(cls):
        """
        Return test results formatted in xunit XML
        """
        xml = [('<?xml version="1.0" encoding="utf-8"?>\n'
                '<testsuite errors="0" failures="{0}" '
                .format(len([test_case for test_case in cls._test_plan
                             if not test_case["result"]])) +
                'name="aft.{0}.{1}" skips="0" '
                .format(time.strftime("%Y%m%d%H%M%S",
                                      time.localtime(cls._start_time)),
                        os.getpid()) +
                'tests="{0}" time="{1}">\n'
                .format(len(cls._results),
                        cls._end_time - cls._start_time))]
        for test_case in cls._test_plan:
            xml.append(test_case["xunit_section"])
        xml.append('</testsuite>\n')
        cls._xunit_results = "".join(xml)

    @classmethod
    def _save_test_results(cls):
        """
        Store the test results.
        """
        cls._results_to_xunit()
        results_filename = os.path.join(cls._test_plan[0]["test_dir"],
                                        "..", "results.xml")
        with open(results_filename, "w") as results:
            results.write(cls._xunit_results)
        logging.info("Results saved to {0}.".format(results_filename))

        return True

    @classmethod
    def test(cls, device):
        """Run specific test cases and save the results."""
        return cls._execute_test_plan(device=device) and\
            cls._save_test_results()

# pylint: enable=too-few-public-methods
