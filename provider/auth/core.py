# Copyright 2017 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#
from __future__ import absolute_import

import importlib
import logging

import ovirt_provider_config

from .plugin import Plugin

CONFIG_SECTION = 'AUTH'
AUTH_PLUGIN = 'auth.plugins.static_token:Plugin'

plugin = None


def init():
    global plugin
    plugin = _load_plugin(_auth_plugin())


def _load_plugin(plugin_name):
    try:
        module_name, class_name = plugin_name.rsplit(':', 1)
        plugin_class = getattr(importlib.import_module(module_name),
                               class_name)
        try:
            isinstance(plugin_class, Plugin)
        except TypeError as e:
            logging.error(
                "Auth plugin '%s' is of wrong type: %s",
                plugin_class.__name__, e)
            raise e
        return plugin_class()
    except Exception as e:
        logging.error(
            "Unable to load auth plugin '%s'", plugin_name)
        raise e


def plugin_loaded():
    global plugin
    if not plugin:
        raise AttributeError('No auth plugin loaded')


def _auth_plugin():
    return ovirt_provider_config.get(CONFIG_SECTION, 'plugin', AUTH_PLUGIN)