#!/bin/sh
# Copyright 2016-2021 Red Hat, Inc.
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

set -e

# Default SSL certificate files location
key_file=/etc/pki/vdsm/ovn/ovn-key.pem
cert_file=/etc/pki/vdsm/ovn/ovn-cert.pem
ca_file=/etc/pki/vdsm/ovn/ca-cert.pem

options=$(getopt --options "" \
    --long help,central-ip:,tunnel-ip:,host-fqdn:,ovn-key:,ovn-cert:,ovn-ca-cert: \
    -- "${@}")
eval set -- "$options"
while true; do
    case "$1" in
    --central-ip)
        shift
        central_ip="$1"
        ;;
    --tunnel-ip)
        shift
        tunnel_ip="$1"
        ;;
    --host-fqdn)
        shift
        host_fqdn="$1"
        ;;
    --ovn-key)
        shift
        key_file="$1"
        ;;
    --ovn-cert)
        shift
        cert_file="$1"
        ;;
    --ovn-ca-cert)
        shift
        ca_file="$1"
        ;;
    --help)
        set +x
        echo -n "$0 [--help] [--host-fqdn=<HOST_FQDN>] [--central-ip=<OVN_CENTRAL_IP>] [--tunnel-ip=<OVN_TUNNEL_IP>]"
        echo -n "[--ovn-key=<OVN_KEY>] [--ovn-cert=<OVN_CERT>] [--ovn-ca-cert=<OVN_CA_CERT>]"
        echo ""
        exit
        ;;
    --)
        shift
        break
        ;;
    esac
    shift
done

if [ -n "$host_fqdn" ]; then
  # Set system-id before starting ovsdb-server to be the same as host FQDN
  echo "$host_fqdn" > /etc/openvswitch/system-id.conf
fi


systemctl restart ovsdb-server

ovs-vsctl --no-wait set open . external-ids:ovn-remote=ssl:$central_ip:6642
ovs-vsctl --no-wait set open . external-ids:ovn-encap-type=geneve
ovs-vsctl --no-wait set open . external-ids:ovn-encap-ip=$tunnel_ip
ovs-vsctl --no-wait set open . external_ids:ovn-remote-probe-interval=60000
ovs-vsctl --no-wait set open . external_ids:ovn-openflow-probe-interval=60

cat > /etc/sysconfig/ovn-controller << EOF
# this file is auto-generated by ovirt-provider-ovn-driver
OVN_CONTROLLER_OPTS="--ovn-controller-ssl-key=${key_file} --ovn-controller-ssl-cert=${cert_file} --ovn-controller-ssl-ca-cert=${ca_file}"
EOF

ovs-vsctl --no-wait set open . other_config:private_key=${key_file}
ovs-vsctl --no-wait set open . other_config:certificate=${cert_file}
ovs-vsctl --no-wait set open . other_config:ca_cert=${ca_file}

systemctl enable openvswitch
systemctl enable openvswitch-ipsec
systemctl enable ovn-controller

systemctl restart openvswitch
systemctl restart openvswitch-ipsec
systemctl restart ovn-controller
