#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
#
# Copyright (c) 2013, 2014, 2015 Intel, Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

"""Setup for Automated Flasher and Tester Tool."""

from setuptools import setup
import os

PROJECT_NAME = "aft"
DATA_PATH = os.path.join("share", PROJECT_NAME)
DATA_CFG_PATH = os.path.join(DATA_PATH, "cfg")
DATA_TEST_PLAN_PATH = os.path.join(DATA_CFG_PATH, "test_plan")
DATA_TEST_DATA_PATH = os.path.join(DATA_CFG_PATH, "test_data")
DATA_DOCS_PATH = os.path.join(DATA_CFG_PATH, "docs")

setup(name=PROJECT_NAME,
      version="0.1.2",
      description="Automated Flasher and Tester for OS SW images",
      author="Igor Stoppa",
      author_email="igor.stoppa@intel.com",
      package_dir={PROJECT_NAME: "src"},
      packages=[PROJECT_NAME,
                ".".join((PROJECT_NAME, "plugins")),
               ],
      data_files=[(DATA_PATH, []),
                  (DATA_CFG_PATH, []),
                  (DATA_TEST_PLAN_PATH, []),
                  (DATA_TEST_DATA_PATH, []),
                  (DATA_DOCS_PATH, []),
                 ],
      include_package_data=True,
      entry_points={'console_scripts': ['aft = aft.main:main'],},
     )
