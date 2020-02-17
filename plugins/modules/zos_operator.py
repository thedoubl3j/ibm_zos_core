# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: zos_operator
short_description: Run an operator command
description:
    - Run an operator command and return the output from the console
author: "Ping Xiao <xiaoping@cn.ibm.com>"
options:
  cmd:
    description:
      - The command to execute.
    type: free form
    required: True
  verbose:
    description:
      - print out verbose security information
    type: bool
    required: False
    default: False
  debug:
    description:
      - print out debug messages
    type: bool
    required: False
    default: False 
seealso: []
requirements:
    - Z Open Automation Utilities
    - Python 3.6 or higher 
    - |
      Set the following environment variables for the playbook:
        `_BPXK_AUTOCVT=ON`
        `ZOAU_ROOT=/usr/lpp/IBM/zoautil`
        `PYTHONPATH=${ZOAU_ROOT}/lib/`
'''

EXAMPLES = '''
# Task(s) is a call to an ansible module, basically an action needing to be accomplished
- name: issue an operator command for show active jobs 
  zos_operator:
    cmd: 'd u,all'
- Sample result('rc' field and 'response' field):
{
    rc:0,
    response："MV2C      2020039  04:29:57.58             ISF031I CONSOLE XIAOPIN ACTIVATED                   
    MV2C      2020039  04:29:57.58            -D U,ALL                                             
    MV2C      2020039  04:29:57.59             IEE457I 04.29.57 UNIT STATUS 948                    
                    UNIT TYPE STATUS        VOLSER     VOLSTATE      SS 
                    0100 3277 OFFLINE                                 0 
                    0101 3277 OFFLINE                                 0 
                    0110 3277 OFFLINE                                 0 
                    0111 3277 OFFLINE                                 0 
                    0120 3270 OFFLINE                                 0 
                    0121 3270 OFFLINE                                 0 
                    0130 3270 OFFLINE                                 0 
                    0131 3270 OFFLINE                                 0 
                    0A42 349L O-NRD  -AS                   /REMOV     0 
                    0A43 349L O-NRD  -AS                   /REMOV     0 
                    0A44 349L O-NRD  -AS                   /REMOV     0 
                    0A45 349L O-NRD  -AS                   /REMOV     0 
                    0A46 349L O-NRD  -AS                   /REMOV     0 
                    0A47 349L O-NRD  -AS                   /REMOV     0 
                    0A48 349L O-NRD  -AS                   /REMOV     0 
                    0A49 349L O-NRD  -AS                   /REMOV     0 "
}


- name: issue an operator command for show active jobs with security information and debug message
  zos_operator:
    cmd: 'd u,all'
    verbose: True
- Sample result('rc' field and 'response' field):
{   ...
    rc:0,
    response："ISF050I USER=XIAOPIN GROUP= PROC=REXX TERMINAL=IY29TC26                                                
    ISF051I SAF No decision    SAFRC=4 ACCESS=READ CLASS=SDSF RESOURCE=GROUP.ISFSPROG.SDSF                 
    ISF057I GROUP=ISFSPROG Access denied  USERAUTH=JCL REQAUTH=OPER,ACCT,JCL RSN=01 Insufficient authority 
    ISF051I SAF No decision    SAFRC=4 ACCESS=READ CLASS=SDSF RESOURCE=GROUP.ISFOPER.SDSF                  
    ISF057I GROUP=ISFOPER Access denied  USERAUTH=JCL REQAUTH=OPER,JCL RSN=01 Insufficient authority       
    ISF051I SAF No decision    SAFRC=4 ACCESS=READ CLASS=SDSF RESOURCE=GROUP.ISFUSER.SDSF                  
    ISF057I GROUP=ISFUSER Access allowed USERAUTH=JCL REQAUTH=JCL                                          
    ISF050I USER=XIAOPIN GROUP=ISFUSER PROC=REXX TERMINAL=IY29TC26                                         
    ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFCMD.FILTER.PREFIX                
    ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFCMD.FILTER.OWNER                 
    ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFOPER.DEST.JES2                   
    ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFOPER.ANYDEST.JES2                
    ISF754I Command 'SET SECTRACE ON' generated from associated variable ISFSECTRACE.                      
    ISF776I Processing started for action 1 of 1.                                                          
    ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFOPER.SYSTEM                      
    ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFCMD.ODSP.ULOG.JES2               
    ISF769I System command issued, command text: D U,ALL.                                                  
    ISF766I Request completed, status: COMMAND ISSUED.                                                     
    MV2C      2020039  04:29:20.73             ISF031I CONSOLE XIAOPIN ACTIVATED                           
    MV2C      2020039  04:29:20.73            -D U,ALL                                                     
    MV2C      2020039  04:29:20.74             IEE457I 04.29.20 UNIT STATUS 852                            
                            UNIT TYPE STATUS        VOLSER     VOLSTATE      SS         
                            0100 3277 OFFLINE                                 0         
                            0101 3277 OFFLINE                                 0         
                            0110 3277 OFFLINE                                 0         
                            0111 3277 OFFLINE                                 0         
                            0120 3270 OFFLINE                                 0         
                            0121 3270 OFFLINE                                 0         
                            0130 3270 OFFLINE                                 0         
                            0131 3270 OFFLINE                                 0         
                            0A42 349L O-NRD  -AS                   /REMOV     0         
                            0A43 349L O-NRD  -AS                   /REMOV     0         
                            0A44 349L O-NRD  -AS                   /REMOV     0         
                            0A45 349L O-NRD  -AS                   /REMOV     0         
                            0A46 349L O-NRD  -AS                   /REMOV     0         
                            0A47 349L O-NRD  -AS                   /REMOV     0         
                            0A48 349L O-NRD  -AS                   /REMOV     0         
                            0A49 349L O-NRD  -AS                   /REMOV     0"
 ...                                                   
}
- name: issue an operator command for show active jobs with security information and debug message
  zos_operator:
    cmd: 'd u,all'
    verbose: True
    debug: True
- Sample result('rc' field and 'response' field):
{   ...
    rc:0,
    response："21 *-*    ISFSECTRACE=ON
       >L>      "ON"
    22 *-*    debug=1
       >L>      "1"
    23 *-*    verbose=1
       >L>      "1"
    24 *-*   end
    25 *-*  if Pos('V', options)<>0
       >L>    "V"
       >V>    "-D"
       >F>    "0"
       >L>    "0"
       >O>    "0"
    29 *-*  if Pos('?', options)<>0
       >L>    "?"
       >V>    "-D"
       >F>    "0"
       >L>    "0"
       >O>    "0"
    32 *-* end
    17 *-* do while (Pos('-', input)<>0)
    ...
    106 *-*  Call SayErr isfmsg2.x
       >C>    "ISFMSG2.18"
       >V>    "ISF766I Request completed, status: COMMAND ISSUED."
    82 *-*   SayErr:
       *-*   Procedure
    84 *-*   Parse Arg text
       >>>     "ISF766I Request completed, status: COMMAND ISSUED."
    85 *-*   Call syscalls 'ON'
       >L>     "ON"
       >>>     "0"
    86 *-*   buf=text || esc_n
       >V>     "ISF766I Request completed, status: COMMAND ISSUED."
       >V>     "?"
       >O>     "ISF766I Request completed, status: COMMAND ISSUED.?"
    87 *-*   Address syscall "write" 2 "buf"
       >L>     "write"
       >L>     "2"
       >O>     "write 2"
       >L>     "buf"
       >O>     "write 2 buf"
ISF766I Request completed, status: COMMAND ISSUED.
    89 *-*   Return 0
       >L>     "0"
       >>>    "0"
   108 *-*  Return
    75 *-* exit last_rc
       >V>   "0"
"
}
'''

RETURN = '''
changed:
    description: True if the state was changed, otherwise False
    returned: always
    type: bool
failed:
    description: True if operator command failed, othewise False
    returned: always
    type: bool
rc:
    description: return code of the operator command
    type: int
response:
    description: the response of the operator command
    type: str
message:
    description: Message returned on failure, if 'rc<0' it will be the response of operator command, else if other unknown exception happened,it will return 'An unexpected error occurred',eg 
    type: str
    returned: failure
    sample: 
      - changed: false,
      - failed: false,
      - msg: "An unexpected error occurred"
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
        self.msg = 'An error occurred during issue the operator command, the response is "{0}"'.format(message)
        

def main():
    run_module()

if __name__ == '__main__':
    main()