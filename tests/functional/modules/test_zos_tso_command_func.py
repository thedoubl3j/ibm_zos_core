# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division

import os
import sys
import warnings

import ansible.constants
import ansible.errors
import ansible.utils
import pytest

__metaclass__ = type


def test_zos_tso_command(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="alloc da('bjmaxy.hill3.test') like('bjmaxy.hill3')")
    for result in results.contacted.values():
        assert result.get('return_code') == 0
        assert result.get('changed') == True

def test_zos_tso_command_2(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="delete 'BJMAXY.HILL3.TEST'")
    for result in results.contacted.values():
        assert result.get('return_code') == 0
        assert result.get('changed') == True

def test_zos_tso_command_failure(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="LISTGRP")
    for result in results.contacted.values():
        assert result.get('return_code') == 4
        assert result.get('changed') == True 