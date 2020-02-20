# -*- coding: utf-8 -*-
import sys
import unittest
from unittest.mock import MagicMock, Mock
import pytest

IMPORT_NAME = 'ansible_collections_ibm_zos_core.plugins.modules.zos_raw'

class DummyModule(object):
    """Used in place of Ansible's module 
    so we can easily mock the desired behavior."""
    
    def __init__(self, rc, stdout, stderr):
        self.rc = 0
        self.stdout = stdout
        self.stderr = stderr

    def run_command(self, *args, **kwargs):
        return (self.rc, self.stdout, self.stderr)


dds = [{"ddName": "sysin", "dataset": "TEST.MVSUTIL.PYTHON.MVSCMD.AUTH.IN"},
       {"ddName": "sysprint", "dataset": "TEST.MVSUTIL.PYTHON.MVSCMD.AUTH.OUT"}
       ]
test_data_success = [
    ("IDCAMS", "", dds, False, False, "0\\n", '', 0, True, "/tmp", "tmp12234w"),
]
#program, args, dds, verbose, debug, module
@pytest.mark.parametrize("program, args, dds, verbose, debug, stdout, stderr,rc, expected,tmpdir,tmpfile", test_data_success)
def test_run_mvs_program_success(zos_import_mocker, program, args, dds, verbose, debug, stdout, stderr, rc, expected, tmpdir, tmpfile):
    mocker, importer = zos_import_mocker
    raw = importer(IMPORT_NAME)
    mocker.patch('{0}.copy_temp_file'.format(
        IMPORT_NAME), create=True, return_value=(tmpdir, tmpfile))
    mocker.patch('{0}.remove'.format(IMPORT_NAME),
                 create=True, return_value="")
    module = DummyModule(rc, stdout, stderr)
    passed = True
    try:
        raw.run_mvs_program(program, args, dds, verbose, debug, module)
        print(stdout, stderr, rc)
    except raw.ZOSRawError as e:
        print(e)
        passed = False
    assert passed == expected


dds_2 = [{"ddName": "sysin", "dataset": "dummy"},
         {"ddName": "sysut1", "dataset": "BJMAXY.MVSUTIL.PYTHON.MVSCMD.A"},
         {"ddName": "sysut2", "dataset": "BJMAXY.MVSUTIL.PYTHON.MVSCMD.B"},
         {"ddName": "sysprint", "dataset": "stdout"}
         ]

stdout = '1DATA SET UTILITY - GENERATE                                                                       PAGE 0001             \\n-                                                                                                                        \\n PROCESSING ENDED AT EOD                                                                                                 \\n0\\n'
test_data_2 = [
    ("iebgener", "", dds_2, False, True, stdout, "", 0, True, "/tmp", "tmp12234w"),
]
@pytest.mark.parametrize("program, args, dds, verbose, debug, stdout, stderr,rc, expected,tmpdir,tmpfile", test_data_2)
def test_run_mvs_program_failure(zos_import_mocker, program, args, dds, verbose, debug, stdout, stderr, rc, expected, tmpdir, tmpfile):
    mocker, importer = zos_import_mocker
    raw = importer(IMPORT_NAME)
    mocker.patch('{0}.copy_temp_file'.format(
        IMPORT_NAME), create=True, return_value=(tmpdir, tmpfile))
    mocker.patch('{0}.remove'.format(IMPORT_NAME),
                 create=True, return_value="")
    module = DummyModule(rc, stdout, stderr)
    passed = True
    try:
        stdout, stderr, rc = raw.run_mvs_program(
            program, args, dds, verbose, debug, module)
        print(stdout, stderr, rc)
    except raw.ZOSRawError as e:
        print(e)
        passed = False
    assert passed == expected
