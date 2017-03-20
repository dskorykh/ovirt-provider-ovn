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

import ovirt_provider_config

from auth import Unauthorized

from .plugin import OVirtPlugin
from .sso import get_token_info
from .sso import is_active

CONFIG_SECTION = 'OVIRT'
ENGINE_NETWORK_ADMIN_USER_NAME = 'netadmin@internal'


class AuthorizationByUserName(OVirtPlugin):

    def validate_token(self, token):
        return self._is_user_name(token, _admin_user_name())

    @staticmethod
    def _is_user_name(token, admin_user_name):

        token_info = get_token_info(
            token=token,
            engine_url=AuthorizationByUserName._engine_url(),
            ca_file=AuthorizationByUserName._engine_ca_file(),
            client_id=AuthorizationByUserName._sso_client_id(),
            client_secret=AuthorizationByUserName._sso_client_secret())

        if not is_active(token_info):
            raise Unauthorized('Token is not active.')

        return admin_user_name == token_info['user_id']


def _admin_user_name():
    return ovirt_provider_config.get(CONFIG_SECTION, 'admin-user-name',
                                     ENGINE_NETWORK_ADMIN_USER_NAME)