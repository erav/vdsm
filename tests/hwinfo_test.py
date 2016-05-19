#
# Copyright 2016 Red Hat, Inc.
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

import os.path
import platform
import tempfile

from monkeypatch import MonkeyPatch
from testlib import VdsmTestCase, namedTemporaryDir
from testlib import permutations, expandPermutations

from vdsm import cpuarch
from vdsm import cpuinfo
from vdsm import ppc64HardwareInfo


def _outfile(name):
    test_path = os.path.realpath(__file__)
    dir_name = os.path.split(test_path)[0]
    return os.path.join(dir_name, 'cpuinfo', name)


@expandPermutations
class TestHwinfo(VdsmTestCase):

    # TODO: The following tests are testing private functions. We want to avoid
    # that in future. In this case, we have to investigate creation of small
    # module to test device-tree.
    @permutations([
        [b'abc', 'abc'],
        [b'abc\0', 'abc'],
        [b'abc,\0', 'abc'],
        [b'\0abc\n', '\0abc\n'],
    ])
    def test_ppc_device_tree_parsing(self, test_input, expected_result):
        with namedTemporaryDir() as tmpdir:
            with tempfile.NamedTemporaryFile(dir=tmpdir) as f:
                f.write(test_input)
                f.flush()
                result = ppc64HardwareInfo._from_device_tree(
                    os.path.basename(f.name), tree_path=tmpdir)
                self.assertEqual(expected_result, result)

    def test_ppc_device_tree_no_file(self):
        result = ppc64HardwareInfo._from_device_tree(
            'nonexistent', tree_path='/tmp')
        self.assertEqual('unavailable', result)

    @MonkeyPatch(ppc64HardwareInfo, '_from_device_tree', lambda _: 'exists')
    @MonkeyPatch(cpuinfo, '_PATH', _outfile('cpuinfo_POWER8E_ppc64le.out'))
    @MonkeyPatch(platform, 'machine', lambda: cpuarch.PPC64LE)
    def test_ppc_hardware_info_structure(self):
        expected_result = {
            'systemProductName': 'exists',
            'systemSerialNumber': '8247-22L',
            'systemFamily': 'PowerNV',
            'systemVersion': 'PowerNV 8247-22L',
            'systemUUID': 'exists',
            'systemManufacturer': 'exists'
        }

        result = ppc64HardwareInfo.getHardwareInfoStructure()
        self.assertEqual(expected_result, result)
