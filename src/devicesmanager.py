# Copyright (c) 2013, 2014, 2015 Intel, Inc.
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

"""Tool for managing collection of devices from the same host PC"""

import logging
from argparse import ArgumentParser
from ConfigParser import SafeConfigParser
import re
import os
from aft.classloader import ClassLoader
from aft.tester import Tester


VERSION = "0.1.0"


# Disable "Too few public methods."
# This class has only one high-level task to perform
# pylint: disable=too-few-public-methods
class DevicesManager(object):
    """Class handling devices connected to the same host PC"""
    __CFG_BASE_PATH = "/usr/share/aft/cfg/"

    __DEFAULT_CFG_FILE_NAME = os.path.join(__CFG_BASE_PATH, "platform.cfg")

    __TOPOLOGY_CLASS_NAME_ENDING = "sTopology"
    __DEVICE_CLASS_NAME_ENDING = "Device"

    __CATALOG_BASE_PATH = __CFG_BASE_PATH
    __CATALOG_FILE_NAME_ENDING = "_catalog.cfg"

    __TOPOLOGY_BASE_PATH = __CFG_BASE_PATH
    __TOPOLOGY_FILE_NAME_ENDING = "_topology.cfg"

    __TEST_PLAN_BASE_PATH = os.path.join(__CFG_BASE_PATH, "test_plan")
    __TEST_PLAN_FILE_NAME_ENDING = "_test_plan.cfg"

    _testability = None
    _file_name = None
    _cfg_file_name = None
    _topology_class = None
    _device_class = None
    _device_init_data = None
    _cutter_class = None
    _topology_file_name = None
    _catalog_file_name = None
    _success = False

    @classmethod
    def _load_config(cls):
        """
        Loads the master configuration file:
        processes known parameters and leaves a dictionary
        containing the remaining parameters, which belonging
        to specific device types, for later processing.
        """
        try:
            config = SafeConfigParser()
            if [] == config.read(cls._cfg_file_name):
                logging.critical("Error: configuration file {0} not found."
                                 .format(cls._cfg_file_name))
                return False
            for section in config.sections():
                if not re.match(config.get(section, "regex"), cls._file_name):
                    continue
                logging.info("Loading configuration for platform {0} ."
                             .format(section))

                parms = dict(config.items(section))
                del parms["regex"]

                platform = parms["platform"]
                name = platform + cls.__TOPOLOGY_CLASS_NAME_ENDING
                cls._topology_class = ClassLoader.load_plugin(class_name=name)
                name = platform + cls.__DEVICE_CLASS_NAME_ENDING
                cls._device_class = ClassLoader.load_plugin(class_name=name)
                del parms["platform"]

                cls._catalog_file_name = \
                    os.path.join(cls.__CATALOG_BASE_PATH,
                                 parms["catalog"] +
                                 cls.__CATALOG_FILE_NAME_ENDING)
                cls._topology_file_name = \
                    os.path.join(cls.__TOPOLOGY_BASE_PATH,
                                 parms["catalog"] +
                                 cls.__TOPOLOGY_FILE_NAME_ENDING)
                del parms["catalog"]

                cls._cutter_class = \
                    ClassLoader.load_plugin(class_name=parms["cutter"])
                del parms["cutter"]

                cls._test_plan = \
                    os.path.join(cls.__TEST_PLAN_BASE_PATH,
                                 parms["test_plan"] +
                                 cls.__TEST_PLAN_FILE_NAME_ENDING)
                del parms["test_plan"]

                if not (cls._topology_class and cls._device_class and
                        cls._cutter_class and cls._test_plan):
                    logging.critical("Loading failed.\n"
                                     "Malformed section {0} in file {1}."
                                     .format(section, cls._cfg_file_name))
                    return False
                logging.info("Configuration loaded.")
                break
        except KeyError as error:
            logging.critical("Missing configuration key from configuration "
                             "file:\n{0}".format(error))
            return False
        cls._device_init_data = parms
        return True

    @classmethod
    def _generate_topology(cls):
        """
        Scan and record the layout of devices and cutters
        """
        return cls._success and \
            cls._topology_class.generate()

    @classmethod
    def _image_is_supported(cls):
        """
        Loads the topology descriptor and verifies if the image
        is supported for testing.
        """
        return cls._success and \
            cls._topology_class.load() and \
            cls._topology_class.identify_model_and_type(cls._file_name)

    @classmethod
    def _reserve(cls):
        """
        Loads the topology descriptor and reserves a device
        of the appropriate type and model, if available.
        """
        return cls._success and \
            cls._topology_class.reserve()

    @classmethod
    def _write_image(cls):
        """
        Writes the image to the reserved device.
        """
        return cls._success and \
            cls._topology_class.reserved_device and \
            cls._topology_class.reserved_device.write_image(cls._file_name)

    @classmethod
    def _test(cls):
        """
        Runs tests on the device
        """
        return cls._success and \
            cls._topology_class.reserved_device and \
            cls._topology_class.reserved_device.test()

    @classmethod
    def _validate(cls):
        """
        Grabs a compatible device, writes to it the image and tests it.
        """
        return cls._success and \
            cls._reserve() and \
            cls._write_image() and \
            cls._test()

    @classmethod
    def _load_configuration_files(cls):
        """
        Performs all the initializations preceding the writing of the image
        and testing steps.
        """
        cls._success = \
            cls._load_config() and \
            Tester.init(test_plan=cls._test_plan) and \
            cls._device_class.init_class(init_data=cls._device_init_data) and \
            cls._topology_class.init(
                topology_file_name=cls._topology_file_name,
                catalog_file_name=cls._catalog_file_name,
                cutter_class=cls._cutter_class)
        if not cls._success:
            logging.critical("Error while loading configuration files.")
        return cls._success

    @classmethod
    def run(cls):
        """
        Parse arguments and act accordingly.
        """
        parser = ArgumentParser()
        parser.add_argument("--testable", action="store_true",
                            default=False,
                            help="Test if a specified image is supported.")
        parser.add_argument("--cfg", action="store",
                            default=cls.__DEFAULT_CFG_FILE_NAME,
                            help="Configuration file describing "
                                 "supported platforms.")
        parser.add_argument("file_name", action="store",
                            help="Image to write: a local file, "
                                 "compatible with the supported platforms.")
        args = parser.parse_args()
        if not hasattr(args, "file_name"):
            logging.critical("Error parsing arguments: missing image name")
            return -1
# pylint: disable=protected-access
        cls._file_name = args.file_name
        cls._cfg_file_name = args.cfg
        result = cls._load_configuration_files() and \
            cls._image_is_supported() and \
            (args.testable or cls._validate())
# pylint: enable=protected-access
        if cls._topology_class is not None and \
                cls._topology_class.reserved_device is not None:
            cls._topology_class.reserved_device.detach()
        if result is True:
            logging.info("Done.")
        else:
            logging.critical("Failure.")
        return result is False
# pylint: enable=too-few-public-methods
