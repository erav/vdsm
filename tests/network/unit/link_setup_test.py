# Copyright 2016-2022 Red Hat, Inc.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#

from __future__ import absolute_import
from __future__ import division

from vdsm.network.nmstate.options import BridgeOptsBuilder


def test_parse_nets_bridge_opts():
    nets = {
        'br1': 'multicast_router=0 multicast_snooping=0',
        'br2': 'multicast_router=1 multicast_snooping=1',
    }
    expected = {
        'br1': {
            'multicast-router': 0,
            'multicast-snooping': False,
            'stp': {'enabled': False},
        },
        'br2': {
            'multicast-router': 1,
            'multicast-snooping': True,
            'stp': {'enabled': False},
        },
    }

    for name, opts in nets.items():
        parsed_opts = BridgeOptsBuilder().parse(opts)
        assert expected[name] == parsed_opts
