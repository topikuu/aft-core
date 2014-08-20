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
Support for loading AFT plugins.
"""

from pkg_resources import iter_entry_points


# pylint: disable=too-few-public-methods
class ClassLoader(object):
    """
    Class for loading plugins.
    """
    @staticmethod
    def load_plugin(class_name):
        """
        Used to load dynamically one of the classes available.
        """
        for obj in iter_entry_points(group="aft_plugins",
                                     name=class_name.lower()):
            return obj.load()
# pylint: enable=too-few-public-methods
