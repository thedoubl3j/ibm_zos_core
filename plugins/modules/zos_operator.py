# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: zos_operator
description:
    - Execute an operator command and receive the output.
author: Ping Xiao <xiaoping@cn.ibm.com>
options:
  cmd:
    description:
      - The command to execute.
    type: str
    required: true
  verbose:
    description:
      - Return verbose information.
    type: bool
    required: false
    default: false
  debug:
    description:
      - Return debugging information.
    type: bool
    required: false
    default: false 
'''

EXAMPLES = r'''
- name: Execute an operator command to show active jobs
  zos_operator:
    cmd: 'd u,all'

- name: Execute an operator command to show active jobs with verbose information
  zos_operator:
    cmd: 'd u,all'
    verbose: true

- name: Execute an operator command to show active jobs with verbose and debug information
  zos_operator:
    cmd: 'd u,all'
    verbose: true
    debug: true
'''

RETURN = r'''
result:
    description: Result that is returned from executing the operator command
    returned: success
    type: list[dict]
    contains:
        rc:
            description: Return code of the operator command
            returned: success
            type: int
            sample: 0
        content:
            description: The response resulting from the execution of the operator command
            returned: success
            type: list[str]
            sample:
                - >
                [ "MV2C      2020039  04:29:57.58             ISF031I CONSOLE XIAOPIN ACTIVATED ",                  
                  "MV2C      2020039  04:29:57.58            -D U,ALL                           ",                                             
                  "MV2C      2020039  04:29:57.59             IEE457I 04.29.57 UNIT STATUS 948  ",               
                  "         UNIT TYPE STATUS        VOLSER     VOLSTATE      SS                 ",
                  "          0100 3277 OFFLINE                                 0                ",
                  "          0101 3277 OFFLINE                                 0                "
                ]
message:
    description:
        - > 
          The output message returned from this module. 
          If a 'rc' 0 is returned, then the message will be 'The operator command has been issued successfully'.
          If a non-zero 'rc' is returned, then the message it will be that of the operator command.
          If unknown exception occurs , then the message returned will be 'An unexpected error occurred'. 
    type: dict
    returned: always
    stdout:
        description: The output from the module
        type: str
        sample: The operator command has been issued successfully
    stderr: 
        description: Any error text from the module
        type: str
        sample: If a non-zero 'rc' is returned, then the message it will be that of the operator command.
original_message:
    description: The original list of parameters and arguments and any defaults used.
    returned: always
    type: dict
changed: 
    description: Indicates if any changes were made during module operation. Given operator 
    commands can introduce change and unknown to the module, True is always returned unless
    either a module or command failure has occurred. 
    returned: always
    type: bool
'''

from ansible.module_utils.basic import AnsibleModule
import argparse
import re
from traceback import format_exc
from zoautil_py import OperatorCmd
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import BetterArgParser

def run_module():
    module_args = dict(
        cmd=dict(type='str', required=True),
        verbose=dict(type='bool',default=False),
        debug=dict(type='bool', default=False),
    )

    arg_defs=dict(
        cmd = dict(
            arg_type='str',
            required=True
        ),
        verbose=dict(
            arg_type='bool',
            required=False
        ),
        debug=dict(
            arg_type='bool',
            required=False
        )
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result['original_message'] = module.params
    
    try:
        parser = BetterArgParser(arg_defs)
        new_params = parser.parse_args(module.params)
        rc_message = run_operator_command(new_params)
        result['rc'] = rc_message.get('rc')
        result['response'] = rc_message.get('message')
    except Error as e:
        module.fail_json(msg=e.msg, **result)
    except Exception as e:
        trace = format_exc()
        module.fail_json(msg='An unexpected error occurred: {0}'.format(trace), **result)
    result['message'] = {'stdout': 'The operator command has been issued successfully.', '  ': ''}
    result['changed'] = True
    module.exit_json(**result)

def run_operator_command(params):
    command = params.get('cmd')
    verbose = params.get('verbose')
    debug = params.get('debug')
    rc_message = []
    rc_message = OperatorCmd.execute(command,"",verbose,debug)
    rc = rc_message.get('rc')
    message = rc_message.get('message')
    if rc > 0:
        raise OperatorCmdError(message)
    return rc_message

class Error(Exception):
    pass

class OperatorCmdError(Error):
    def __init__(self, message):
        self.msg = 'An error occurred while executing the command, the response is "{0}"'.format(message)
        

def main():
    run_module()

if __name__ == '__main__':
    main()