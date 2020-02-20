# -*- coding: utf-8 -*-


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION=r"""
module: zos_raw 
author:
    - Xiao Yuan Ma bjmaxy@cn.ibm.com"
short_description: Run a z/OS program  
version_added: "2.9"
options:
  program: 
    required: true
    type: str
    description: The name of the z/OS program that will be run
    samples: IDCAMS, IEFBR14, IEBGENER, etc.
  parms:
    required: false 
    type: str
    description:
      - The program arguments, e.g. -a='MARGINS(1,72)'. 
  dds:
    required: false 
    type: List
    description:
      -  Specify a DDName to associate with a dataset, HFS file or volume
  verbose:
    required: false  
    type: bool
    description: verbose messages
  debug: 
    required: false
    type: bool 
    description: Display debug messages
"""

RETURN = """
return_code: 
    description: The return code. 
    returned : always
    type: str
    sample: Value 0 indicates success, non-zero indicates failure.
outdd:
    description: The program output.
    returned : Displayed if outdd is returned. 
    type: str
sysprint:
    description: The sysprint message. 
    returned : always
    type: str
stdout:
    description: The standard IZOAU command line output. 
    returned : always
    type: str
changed: 
    description: Indicates if any changes were made during module operation.
    type: bool
"""

EXAMPLES = r"""
- name: Run IEFBR14 program. This is a simple program, no output.  
  zos_raw:
     program: IEFBR14

- name: run IDCAMS program to list the catagory of dataset 'TESTER.DATASET'  
  zos_raw:
    program: IDCAMS
    parms:
    dds: [{ddName: sysin, content: LISTCAT ENT('TESTER.DATASET')},
          {ddName: sysprint, dataset: TESTER.DATASET.RESULT}
         ] 
- name: Run IEBGENER program. This program copy the content from sysut1 to sysut2.       
  zos_raw:
     program: IEBGENER
     dds: [ {ddName: sysin, dataset: dummy},
            {ddName: sysut1, dataset: TESTER.MVSUTIL.PYTHON.MVSCMD.A},
            {ddName: sysut2, dataset: TESTER.MVSUTIL.PYTHON.MVSCMD.B},
            {ddName: sysprint, dataset: stdout}
            ]
     debug: True
     
- name: Run ISRSUPC program. Compare 2 PDS members olddd and newdd and write the output to outdd.   
  zos_raw:
     program: ISRSUPC
     parms: DELTAL,LINECMP
     dds: [{ddName: newdd, content: TEST},
           {ddName: olddd, content: TEST},
           {ddName: sysin, content:    CMPCOLM 1:72},
           {ddName: outdd, dataset: TESTER.MVSUTIL.PYTHON.MVSCMD.RESULT}
          ]
     verbose: True
     
Example results:
"msg": " {'msg': 'THE z/OS PROGRAM EXECUTION SUCCEED.', 
          'changed': True, 
          'outdd': None, 
          'sysprint': None, 
          'return_code': '0', 
          'stdout': '1DATA SET UTILITY - GENERATE PAGE 0001\\n-\\n PROCESSING ENDED AT EOD\\n0\\n', 
          'stdout_lines': ['1DATA SET UTILITY - GENERATE PAGE 0001  ', '- ', ' PROCESSING ENDED AT EOD', '0'], 
          'failed': False}" 
          
 "msg": " {'msg': 'THE z/OS PROGRAM EXECUTION SUCCEED.', 
           'changed': True, 
           'outdd': None, 
           'sysprint': \"1IDCAMS  SYSTEM SERVICES TIME: 08:40:45        02/06/20     PAGE 1\\n0\\n  
                        LISTCAT ENT('TESTER.DATASET')\\n
                        0NONVSAM ------- TESTER.DATASET\\n      IN-CAT --- ICFCAT.SYSPLEX2.CATALOGB\\n
                        1IDCAMS  SYSTEM SERVICES TIME: 08:40:45        02/06/20     PAGE      2\\n0
                        THE NUMBER OF ENTRIES PROCESSED WAS:\\n
                          AIX -------------------0\\n
                          ALIAS -----------------0\\n                    
                          CLUSTER ---------------0\\n                    
                          DATA ------------------0\\n                    
                          GDG -------------------0\\n                    
                          INDEX -----------------0\\n                    
                          NONVSAM ---------------1\\n                    
                          PAGESPACE -------------0\\n                    
                          PATH ------------------0\\n                    
                          SPACE -----------------0\\n                    
                          USERCATALOG -----------0\\n                    
                          TAPELIBRARY -----------0\\n                    
                          TAPEVOLUME ------------0\\n                    
                          TOTAL -----------------1\\n0         
                        THE NUMBER OF PROTECTED ENTRIES SUPPRESSED WAS 0\\n0
                        IDC0001I FUNCTION COMPLETED, HIGHEST CONDITION CODE WAS 0\\n0        \\n
                        0IDC0002I IDCAMS PROCESSING COMPLETE. MAXIMUM CONDITION CODE WAS 0\", 
           'return_code': '0', 
           'stdout': '0\\n', 
           'stdout_lines': ['0'], 
           'failed': False}"

"""

from ansible.module_utils.basic import *
from zoautil_py import MVSCmd, Datasets
from os import chmod, path, remove
from tempfile import NamedTemporaryFile

MVSCMD = "mvscmd"
MVSCMD_AUTH = "mvscmdauth"

def run_mvs_program(program, auth, parms, dds, verbose, debug, module):
    mvscmd_suffix_script = ''' --pgm='''+program

    if parms != None :
        mvscmd_suffix_script = mvscmd_suffix_script+''' --args=\"'''+parms+'''\"'''

    for item in dds:
        dd_name = item.get('ddName')
        dataset = item.get('dataset')
        mvscmd_suffix_script = mvscmd_suffix_script +''' --'''+dd_name+'''='''+dataset

    if verbose:
        mvscmd_suffix_script = mvscmd_suffix_script + ''' --verbose=''' + str(verbose)

    if debug:
        mvscmd_suffix_script = mvscmd_suffix_script + ''' --debug=''' + str(debug)

    mvscmd_command_auth = MVSCMD_AUTH + mvscmd_suffix_script
    mvscmd_command = MVSCMD + mvscmd_suffix_script

    try:
        if auth:
            rc, stdout, stderr = module.run_command(mvscmd_command_auth, use_unsafe_shell=True)
        else:
            rc, stdout, stderr = module.run_command(mvscmd_command, use_unsafe_shell=True)

    except Exception as e:
        raise ZOSRawError(e)
    return (stdout, stderr, rc)

def delete_data_sets(data_sets):
    for data_set in data_sets:
        Datasets.delete(data_set)

def run_module():
    module_args = dict(
        program=dict(type='str', required=True),
        auth=dict(type='bool', required=True, default='False'),
        parms=dict(type='str', required=False),
        dds=dict(type='list', required=False),
        verbose=dict(type='bool', required=False),
        debug=dict(type='bool', required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result = dict(
        changed=False,
        outdd='',
        sysprint='',
        return_code='',
        stdout=''
    )
    hlq = Datasets.hlq()
    temp_dds = []

    if module.params.get("program") == None:
        module.fail_json(msg='THE z/OS PROGRAM CAN NOT BE EMPTY.', **result)

    try:
        dds = module.params.get("dds")
        sysprint_DS = ''
        outdd = ''
        contain_sysprint = False

        if dds != None:
            for item in dds:
                if item.get('ddName') == 'sysprint':
                    contain_sysprint = True
                    sysprint_DS = item.get("dataset")
                if item.get('ddName') == 'outdd':
                    outdd = item.get('dataset')
                if 'content' in item.keys():
                    TEMP_SYSIN_DS = Datasets.temp_name(hlq)
                    if Datasets.exists(TEMP_SYSIN_DS):
                        raise ZOSRawError(
                            "There is an existing dataset for the allocated temporary dataset:" + TEMP_SYSIN_DS+".Please try again.")
                    temp_dds.append(TEMP_SYSIN_DS)
                    Datasets.create(TEMP_SYSIN_DS, type="SEQ", format="FB")
                    Datasets.write(TEMP_SYSIN_DS, '  ' + item.get('content'))
                    item.pop('content')
                    item['dataset'] = TEMP_SYSIN_DS

        if not contain_sysprint:
            TEMP_SYSPRINT_DS = Datasets.temp_name(hlq)
            if Datasets.exists(TEMP_SYSPRINT_DS):
                raise ZOSRawError("There is an existing dataset for the allocated temporary dataset:"+TEMP_SYSPRINT_DS+".Please try again.")
            temp_dds.append(TEMP_SYSPRINT_DS)
            Datasets.create(TEMP_SYSPRINT_DS, type="SEQ", format="FB")
            sysprint_DS = TEMP_SYSPRINT_DS
            sysprint_item = {'ddName': 'sysprint', 'dataset': sysprint_DS}
            if dds is None:
                dds = []
            dds.append(sysprint_item)

        stdout, stderr, rc = run_mvs_program(module.params.get("program"),
                                             module.params.get("auth"),
                                             module.params.get("parms"),
                                             dds,
                                             module.params.get("verbose"),
                                             module.params.get("debug"), module)

        result['outdd'] = Datasets.read(outdd)
        result['sysprint'] = Datasets.read(sysprint_DS)
        result['stdout'] = stdout
        result['return_code'] = rc

        if rc != 0:
            module.fail_json(msg="THE z/OS PROGRAM EXECUTION FAILED.", **result)
    except ZOSRawError as e:
        module.fail_json(msg=e, **result)
    except Exception as e:
        module.fail_json(msg=e, **result)
    finally:
        delete_data_sets(temp_dds)
    result['changed'] = True
    module.exit_json(msg='THE z/OS PROGRAM EXECUTION SUCCEED.', **result)

class Error(Exception):
    pass

class ZOSRawError(Error):
    def __init__(self, program):
        self.msg = 'An error occurred during execution of z/OS program {}.'.format(program)


def main():
    run_module()


if __name__ == '__main__':
    main()
