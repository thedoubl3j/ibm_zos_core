# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import os
import sys
import warnings

import ansible.constants
import ansible.errors
import ansible.utils
import pytest

__metaclass__ = type


def test_zos_raw_IEFBR14(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_raw(program='IEFBR14')
    for result in results.contacted.values():
        assert result.get('return_code') == '0'
        assert result.get('changed') == True


 def test_zos_raw_iebgener(ansible_zos_module):
    dds_test = [{'ddName': 'sysin', 'dataset': 'dummy'},
            {'ddName': 'sysut1', 'dataset': 'imstestl.ims1.test05'},
            {'ddName': 'sysut2', 'dataset': 'imstestl.ims1.test06'},
            {'ddName': 'sysprint', 'dataset': 'stdout'}
            ]
    hosts = ansible_zos_module
    hosts.all.zos_dataset(name='imstestl.ims1.test05', state='present', type='seq', replace=True)
    hosts.all.zos_dataset(name='imstestl.ims1.test06', state='present', type='seq', replace=True)
    results = hosts.all.zos_raw(program='iebgener', dds=dds_test, debug=True)
    for result in results.contacted.values():
        assert result.get('return_code') == '0'
        assert result.get('changed') == True

def test_zos_raw_ISRSUPC(ansible_zos_module):
        # Compare 2 PDS members olddd and newdd and write the output to outdd. 
        # The content of newdd and olddd is not the same, so failed with rc 35.
    dds_test = [{'ddName': 'newdd', 'dataset': 'BJMAXY.MVSUTIL.PYTHON.MVSCMD.A'},
            {'ddName': 'olddd', 'dataset': 'BJMAXY.MVSUTIL.PYTHON.MVSCMD.B'},
            {'ddName': 'sysin', 'dataset': 'BJMAXY.MVSUTIL.PYTHON.MVSCMD.OPT'},
            {'ddName': 'outdd', 'dataset': 'BJMAXY.MVSUTIL.PYTHON.MVSCMD.RESULT'}
            ]
    hosts = ansible_zos_module
    results = hosts.all.zos_raw(program='ISRSUPC', dds=dds_test, debug=True)
    for result in results.contacted.values():
        assert result.get('return_code') == '35'

def test_zos_raw_ISRSUPC_content(ansible_zos_module):
        # Compare 2 PDS members olddd and newdd and write the output to outdd. 
        # The content of newdd and olddd is the same, so rc=0.
    dds_test = [{'ddName': 'newdd', 'content': 'test'},
            {'ddName': 'olddd', 'content': 'test'},
            {'ddName': 'sysin', 'content': '   CMPCOLM 1:72'},
            {'ddName': 'outdd', 'dataset': 'BJMAXY.MVSUTIL.PYTHON.MVSCMD.RESULT'}
            ]
    hosts = ansible_zos_module
    results = hosts.all.zos_raw(program='ISRSUPC', dds=dds_test, debug=True)
    for result in results.contacted.values():
        assert result.get('return_code') == '0'
