# Copyright (c) 2015 Intel, Inc.
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
Main entry point for aft.
"""

import sys
import logging

from aft.devicesmanager import DevicesManager


def main(args=None):
    """
    Entry point for library-like use.
    """
    if args is not None:
        backup_args = sys.args
        sys.args = args
    DevicesManager()
    logging.basicConfig(filename='aft.log', level=logging.DEBUG)
    retval = DevicesManager.run()
    if backup_args in locals():
        sys.args = backup_args
    return retval


if __name__ == "__main__":
    sys.exit(main())
