# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division)
__metaclass__ = type


from ansible.module_utils.basic import AnsibleModule
import pytest
import sys
from mock import call

# Used my some mock modules, should match import directly below
IMPORT_NAME = 'ansible_collections_ibm_zos_core.plugins.modules.zos_operator'


# * Tests for zos_operator

dummy_dict1 = {
    'cmd': 'd u,all',
    'verbose': False,
    'debug': True
}

dummy_dict2 = {
    'cmd': 'dd u,all',
    'verbose': True,
    'debug': False
}

dummy_dict3 = {
    'cmd': 'd u,all'
}

dummy_dict4 = {
    'cmd': 'd u,all',
    'verbose': True
}

dummy_dict5 = {
    'cmd': 'd u,all',
    'debug': True
}

dummy_return_dict1 = {
    'rc': 0,
    'message': 'good result'
}

dummy_return_dict2 = {
    'rc': 1,
    'message': None
}

test_data = [
    (dummy_dict1, dummy_return_dict1, True),
    (dummy_dict1, {}, False),
    (dummy_dict2, dummy_return_dict2, False),
    (dummy_dict3, dummy_return_dict1, True),
    (dummy_dict4, dummy_return_dict1, True),
    (dummy_dict5, dummy_return_dict1, True)
]

@pytest.mark.parametrize("args,return_value,expected", test_data)
def test_zos_opreator_various_args(zos_import_mocker, args, return_value, expected):
    mocker, importer = zos_import_mocker
    zos_operator = importer(IMPORT_NAME)
    passed = True
    mocker.patch('zoautil_py.OperatorCmd.execute',
                create=True, return_value=return_value)
    try:
        zos_operator.run_operator_command(args)
    except zos_operator.OperatorCmdError:
        passed = False
    except TypeError as e:
        # MagicMock throws TypeError when input args is None
        # But if it gets that far we consider it passed
        if 'MagicMock' not in str(e):
            passed = False
    assert passed == expected


def test_zos_opreator_missing_all_args(zos_import_mocker):
    mocker, importer = zos_import_mocker
    zos_operator = importer(IMPORT_NAME)
    mocker.patch('zoautil_py.OperatorCmd.execute', create=True)
    with pytest.raises(TypeError):
        zos_operator.run_operator_command()


def test_exception_receiving_name(zos_import_mocker):
    mocker, importer = zos_import_mocker
    zos_operator = importer(IMPORT_NAME)
    dummy_return_dict = {
    'rc': 1,
    'message': 'bad result'
    }
    mocker.patch('zoautil_py.OperatorCmd.execute', create=True, return_value=dummy_return_dict)
    message = 'bad result'
    cmd = 'd u,all'
    args={'cmd': 'd u,all'}
    patched_method = mocker.patch.object(
        zos_operator.OperatorCmdError, '__init__', return_value=None)
    try:
        zos_operator.run_operator_command(args)
    except zos_operator.OperatorCmdError:
        pass
    patched_method.assert_called_with(cmd,message)
