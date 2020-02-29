# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION=r'''
module: zos_tso_command 
author: Xiao Yuan Ma <bjmaxy@cn.ibm.com>
short_description: Execute a TSO command on the target z/OS system.
description: Execute a TSO command on the target z/OS system with the provided options and receive a structured response.
options:
  command:
      description:
        - The TSO command to execute on the target z/OS system.
      required: true
      type: str 
   auth:
      required: false
      type: bool
      default: false
      description: 
        - > 
          Instruct whether this program should run authorized or not. 
          If set to true, the program will be run as APF authorized, otherwise the program runs as unauthorized.
'''

RETURN = r'''
msg:
    description: The message of the tso command execution result. 
    returned: always 
    type: str
    sample: The TSO command execution succeeded..
return_code: 
    description: The return code. 
    returned : always
    type: str
    sample: 0 means success. others means failure.
stdout: 
    description: The standard output of the TSO command execution 
    returned : success, failure
    type: str
stderr:
    description: The error output of the tso command execution  
    returned : success, failure
    type: str
changed: 
    description: Indicates if any changes were made during module operation. Given TSO 
    commands can introduce change and unknown to the module, True is always returned unless
    either a module or command failure has occurred. 
    returned: always
    type: bool
result:
    description:
    returned:
    type: list[dict]
        ret_code:
            description: return code output received from the TSO command
            returned:
            type: list[dict]
            code:
                description: Holds the return code
                returned: always
                type: int
                sample: 00
            msg_code:
                description: Holds the return code string
                returned:always
                type: str
                sample: "00"
            msg_txt:
                description: Holds additional information related to the job that may be useful to the user.
                type: str
                sample: "Received return code 08, please configure IMS Connect"
        content:
            description: The response resulting from the execution of the TSO command
            returned: success
            type: list[str]
            sample:
               - >
               [ "NO MODEL DATA SET                                                OMVSADM",
                 "TERMUACC                                                                ",
                 "SUBGROUP(S)= VSAMDSET SYSCTLG  BATCH    SASS     MASS     IMSGRP1       ",
                 "             IMSGRP2  IMSGRP3  DSNCAT   DSN120   J42      M63           ",
                 "             J91      J09      J97      J93      M82      D67           ",
                 "             D52      M12      CCG      D17      M32      IMSVS         ",
                 "             DSN210   DSN130   RAD      CATLG4   VCAT     CSP           ",
                ]
        message:
            description: The output message returned from this module. 
            type: dict
            returned: always
            msg: 
                description: Message returned by the module 
                type: str
                sample: Successfully submitted TSO command.
            stdout:
                description: The output from the module
                type: str
                sample: The operator command has been issued successfully
            stderr: 
                description: Any error text from the module
                type: str
                sample: An exception has occurred.
        original_message:
            description: The original list of parameters and arguments and any defaults used.
            returned: always
            type: dict
        changed: 
            description: Indicates if any changes were made during module operation. Given TSO 
            commands can introduce change and unknown to the module, True is always returned unless
            either a module or command failure has occurred. 
            returned: always
            type: bool
    sample:
        {
            "result":{ 
            "ret_code":{    
                    "code":00,  
                    "msg_code":"00", 
                    "msg_txt":"Only if we can deduce from the return code that is helfpul",      
               },
            "content" : [
                "NO MODEL DATA SET                                                OMVSADM",
                "TERMUACC                                                                ",
                "SUBGROUP(S)= VSAMDSET SYSCTLG  BATCH    SASS     MASS     IMSGRP1       ",
                "             IMSGRP2  IMSGRP3  DSNCAT   DSN120   J42      M63           ",
                "             J91      J09      J97      J93      M82      D67           ",
                "             D52      M12      CCG      D17      M32      IMSVS         ",
                "             DSN210   DSN130   RAD      CATLG4   VCAT     CSP           ",
                "             DBRAD    UCAT     DB2R2CAT DB2R3CAT TESTCAT  DSNCAT1       ",
                "             DSNCAT2  LOGCAT   USERVSAM DSNC220  DSNC120  DSNC210       "
            ]},
            "message":{
                "msg": "The TSO command execution succeeded.",
                "stderr":"delete 'TEST.HILL3.TEST'",            
                "stdout":"'IDC0550I ENTRY (A) TEST.HILL3.TEST DELETED'"         
            },
            "original_message": {.....
            },
            "changed": false,
        }
'''

EXAMPLES = r'''
  - name: Execute TSO command: allocate a new dataset.
    zos_tso_command:
        command: alloc da('TEST.HILL3.TEST') like('TEST.HILL3')

  - name: Execute TSO command: delete an existing dataset. 
    zos_tso_command:
        command: delete 'TEST.HILL3.TEST'
'''

from ansible.module_utils.basic import AnsibleModule
from os import chmod, path, remove
from tempfile import NamedTemporaryFile

TSOCMD = 'tso'
TSOCMD_AUTH = 'tsocmd'
def run_tso_command(command,module):
    try:
        rc, stdout, stderr = module.run_command([TSOCMD, command])
        if "IKJ56652I You attempted to run an authorized command or program. " in stdout:
            rc, stdout, stderr = module.run_command("echo "+command+"| mvscmdauth --pgm=IKJEFT01 --sysprint=* --systsprt=* --systsin=stdin",use_unsafe_shell=True)
    except Exception as e:
        raise e
    return (stdout,stderr,rc )


def run_module():
    module_args = dict(
        command=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result = dict(
        changed=False,
        stdout='',
        stderr='',
        return_code='8'
    )

    command = module.params.get("command")
    if command == None or command.strip() == "":
        module.fail_json(msg='The "command" provided was null or an empty string.', **result)

    try:
        stdout, stderr, rc = run_tso_command(command, module)
        result['stdout'] = stdout
        result['stderr'] = stderr
        result['return_code'] = rc
        result['changed'] = True
        if rc == 0:
            module.exit_json(msg='The TSO command execution succeeded.', **result)
        else:
            module.fail_json(msg='The TSO command execution failed.', **result)

    except Exception as e:
        module.fail_json(msg=e, **result)

class Error(Exception):
    pass

# class TSOCommandError(Error):
#     def __init__(self, command):
#         self.msg = 'An error occurred during TSO command execution .'.format(command)

def main():
    run_module()

if __name__ == '__main__':
    main()