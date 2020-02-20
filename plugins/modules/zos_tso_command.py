# /usr/bin/python
# -*- coding: utf-8 -*-


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION=r"""
module: zos_tso_command 
author:
    - "Xiao Yuan Ma "
short_description: Execute a TSO command on the target z/OS system
version_added: "2.9"
options:
  command:
    required: true
    description:
      - The TSO command to execute on the target z/OS system 
notes:
    - This module only supports z/OS distributions.
requirements:
    - Python 3.6 or higher 
"""

RETURN = """
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
    description: Indicates if any changes were made during module operation.
    type: bool
"""

EXAMPLES = r"""
  - name: Execute TSO command: allocate a new dataset.
    zos_tso_command:
        command: alloc da('TEST.HILL3.TEST') like('TEST.HILL3')
  - name: Execute TSO command: delete an existing dataset. 
    zos_tso_command:
        command: delete 'TEST.HILL3.TEST'
        

Example outputs : 
    {'msg': 'The TSO command execution succeeded.', 
     'changed': True, 
     'stdout': 'IDC0550I ENTRY (A) TEST.HILL3.TEST DELETED\\n', 
     'stderr': \"delete 'TEST.HILL3.TEST'\\n\", 
     'return_code': 0, 
     'stdout_lines': ['IDC0550I ENTRY (A) TEST.HILL3.TEST DELETED'], 
     'stderr_lines': [\"delete 'TEST.HILL3.TEST'\"], 
     'failed': False
     }
 
"""

from ansible.module_utils.basic import *
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