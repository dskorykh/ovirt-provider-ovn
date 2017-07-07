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

import ovsdbapp.backend.ovs_idl.connection
from ovsdbapp.schema.ovn_northbound.impl_idl import OvnNbApiIdlImpl

import ovirt_provider_config
from ovirt_provider_config import CONFIG_SECTION_OVN_REMOTE
from ovirt_provider_config import DEFAULT_OVN_REMOTE_AT_LOCALHOST
from ovirt_provider_config import KEY_OVN_REMOTE
from ovndb.ovn_north_mappers import NetworkMapper
from ovndb.ovn_north_mappers import RestDataError


class OvnNorth(object):

    OVN_NORTHBOUND = 'OVN_Northbound'
    TABLE_LS = 'Logical_Switch'
    ROW_LS_NAME = 'name'

    def __init__(self):
        ovsdb_connection = ovsdbapp.backend.ovs_idl.connection.Connection(
            idl=ovsdbapp.backend.ovs_idl.connection.OvsdbIdl.from_server(
                self._ovn_remote(),
                OvnNorth.OVN_NORTHBOUND
            ),
            timeout=100)
        self.idl = OvnNbApiIdlImpl(ovsdb_connection)

    @NetworkMapper.map_to_rest
    def list_networks(self):
        return self.idl.ls_list().execute()

    @NetworkMapper.map_to_rest
    def get_network(self, network_id):
        return self.idl.ls_get(network_id).execute()

    @NetworkMapper.validate_add
    @NetworkMapper.map_from_rest
    @NetworkMapper.map_to_rest
    def add_network(self, name):
        # TODO: ovirt allows multiple networks with the same name
        # in oVirt, but OVS does not (may_exist=False will cause early fail)
        return self.idl.ls_add(switch=name, may_exist=False).execute()

    @NetworkMapper.validate_update
    @NetworkMapper.map_from_rest
    def update_network(self, network_id, name):
        self.idl.db_set(
            self.TABLE_LS,
            network_id,
            (self.ROW_LS_NAME, name),
        ).execute()
        return self.get_network(network_id)

    def delete_network(self, network_id):
        network = self.idl.ls_get(network_id).execute()
        if not network:
            raise RestDataError('Network %s does not exist' % network_id)
        if network.ports:
            raise RestDataError(
                'Unable to delete network %s. Ports exist for the network'
                % network_id
            )

        # TODO: once subnets are added we need to do:
        # subnets = self.idl.dhcp_options_list(ids_only=False).execute()
        # for subnet in subnets:
        #    if subnet.external_ids.get('ovirt_network_id'):
        #        if id == str(subnet.uuid):
        #            self.idl.dhcp_options_del(subnet.uuid).execute()

        self.idl.ls_del(network_id).execute()

    def list_ports(self):
        return []

    def get_port(self, port_id):
        return None

    def add_port(
        self,
        network_id,
        name,
        mac=None,
        is_enabled=None,
        is_up=None,
        external_device_id=None,
        external_owner=None,
    ):
        return None

    def update_port(
        self,
        port_id,
        network_id=None,
        name=None,
        mac=None,
        is_enabled=None,
        is_up=None,
        external_device_id=None,
        external_owner=None,
    ):
        return None

    def update_port_mac(self, port_id, macaddress):
        pass

    def delete_port(self, port_id):
        pass

    def list_subnets(self):
        return []

    def get_subnet(self, subnet_id):
        return None

    def add_subnet(
        self,
        name,
        cidr,
        network_id,
        dns=None,
        gateway=None
    ):
        return None

    def update_subnet(
        self,
        subnet_id,
        name=None,
        cidr=None,
        dns=None,
        gateway=None
    ):
        return None

    def delete_subnet(self, subnet_id):
        pass

    @staticmethod
    def _ovn_remote():
        return ovirt_provider_config.get(
            CONFIG_SECTION_OVN_REMOTE,
            KEY_OVN_REMOTE,
            DEFAULT_OVN_REMOTE_AT_LOCALHOST
        )