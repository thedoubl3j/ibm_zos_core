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

# Simple test without output.
def test_zos_raw_IEFBR14(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_raw(program='IEFBR14')
    for result in results.contacted.values():
        assert result.get('ret_code').get('code') == 0
        assert result.get('changed') == True

#run program iebgener, copy the content from sysut1 to sysut2.
def test_zos_raw_iebgener(ansible_zos_module):
    dds_test = [{'ddName': 'sysin', 'dataset': 'dummy'},
            {'ddName': 'sysut1', 'dataset': 'IMSTESTL.IMS1.TEST05'},
            {'ddName': 'sysut2', 'dataset': 'IMSTESTL.IMS1.TEST06'},
            {'ddName': 'sysprint', 'dataset': 'stdout'}
            ]
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST05', state='present', type='seq', replace=True)
    hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST06', state='present', type='seq', replace=True)
    results = hosts.all.zos_raw(program='iebgener', dds=dds_test, debug=True)
    for result in results.contacted.values():
        assert result.get('ret_code').get('code') == 0
        assert result.get('changed') == True

# def test_zos_raw_ISRSUPC(ansible_zos_module):
#         # Compare 2 PDS members olddd and newdd and write the output to outdd. 
#         # The content of newdd and olddd is the same, so rc=0.
#         # The content of newdd and olddd can be just a simple string like "TEST".
#         # If you want to play this case, fill in the newdd and olddd with the same string content.
#     dds_test = [{'ddName': 'newdd', 'dataset': 'IMSTESTL.IMS1.TEST05'},
#             {'ddName': 'olddd', 'dataset': 'IMSTESTL.IMS1.TEST06'},
#             {'ddName': 'sysin', 'content': '   CMPCOLM 1:72'},
#             {'ddName': 'outdd', 'dataset': 'IMSTESTL.IMS1.TEST07'}
#             ]
#     hosts = ansible_zos_module
#     hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST05', state='present', type='seq', replace=True)
#     hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST06', state='present', type='seq', replace=True)
#     hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST07', state='present', type='seq', replace=True)
#     results = hosts.all.zos_raw(program='ISRSUPC', dds=dds_test, debug=True)
#     for result in results.contacted.values():
#         assert result.get('ret_code').get('code') == 0

def test_zos_raw_ISRSUPC_with_content(ansible_zos_module):
        # Compare 2 PDS members olddd and newdd and write the output to outdd. 
        # The content of newdd and olddd is not the same, so rc=1.
    dds_test = [{'ddName': 'newdd', 'content': 'TEST'},
            {'ddName': 'olddd', 'content': 'TEST12'},
            {'ddName': 'sysin', 'content': '   CMPCOLM 1:72'},
            {'ddName': 'outdd', 'dataset': 'IMSTESTL.IMS1.TEST07'}
            ]
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST07', state='present', type='seq', replace=True)
    results = hosts.all.zos_raw(program='ISRSUPC', dds=dds_test, debug=True)
    for result in results.contacted.values():
        assert result.get('ret_code').get('code') == 1

def test_zos_raw_IDCAMS(ansible_zos_module):
        # run IDCAMS program: list catalog of dataset IMSTESTL.IMS1.TEST05
    dds_test = [{'ddName': 'sysin', 'content': "LISTCAT ENT('IMSTESTL.IMS1.TEST05')"},
            {'ddName': 'sysprint', 'dataset': 'IMSTESTL.IMS1.TEST08'},
            ]
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST05', state='present', type='seq', replace=True)
    hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST08', state='present', type='seq', replace=True)
    results = hosts.all.zos_raw(program='IDCAMS', auth=True, dds=dds_test, debug=True)
    for result in results.contacted.values():
        assert result.get('ret_code').get('code') == 0

def test_zos_raw_IDCAMS_failure(ansible_zos_module):
        # run IDCAMS program: list catalog of dataset IMSTESTL.IMS1.TEST05.0000 which does not exist.
        # return error code 12
    dds_test = [{'ddName': 'sysin', 'content': "LISTCAT ENT('IMSTESTL.IMS1.TEST05.0000')"},
            {'ddName': 'sysprint', 'dataset': 'IMSTESTL.IMS1.TEST08'},
            ]
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST08', state='present', type='seq', replace=True)
    results = hosts.all.zos_raw(program='IDCAMS', auth=True, dds=dds_test, debug=True)
    for result in results.contacted.values():
        assert result.get('ret_code').get('code') == 12

def test_zos_raw_IDCAMS_without_auth(ansible_zos_module):
        # run IDCAMS program: list catalog of dataset IMSTESTL.IMS1.TEST05
    dds_test = [{'ddName': 'sysin', 'content': "LISTCAT ENT('IMSTESTL.IMS1.TEST05')"},
            {'ddName': 'sysprint', 'dataset': 'IMSTESTL.IMS1.TEST08'},
            ]
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='IMSTESTL.IMS1.TEST08', state='present', type='seq', replace=True)
    results = hosts.all.zos_raw(program='IDCAMS', dds=dds_test, debug=True)
    for result in results.contacted.values():
        assert result.get('ret_code').get('code') == 36