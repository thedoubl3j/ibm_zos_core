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
  auth:
    required: false
    type: bool
    default: false
    description: 
      - Instruct whether this program should run authorized or not. 
      - If set to true, the program will be run as APF authorized, otherwise the program runs as unauthorized.
  dds:
    required: false 
    type: List<dict>
    description:
      - Specify a DDName to associate with a dataset, HFS file or volume
      - If you want to input from stdin , use option "content"
    contains: 
      ddname: 
         description: The DD name 
         type: str 
      dataset/content: 
         description: 
            - For dataset, specify a dataset name associated with the ddname.  
            - For content, input the content directly, and the module will generate a temp dataset 
              internally for processing. Please see EXAMPLES section. 
         type: str
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
ret_code: 
    description: The return code. 
    returned : always
    type: dict
    contains:
        msg:
            description: Holds the return code 
            type: str
        msg_code: 
            description: Holds the return code string 
            type: str
        msg_txt: 
            description: Holds additional information related to the program that may be useful to the user.
            type: str
        code: 
            description: return code converted to integer value (when possible)
            type: int 
    sample: Value 0 indicates success, non-zero indicates failure.
       - code: 0
       - msg: "0"
       - msg_code: "0"
       - msg_txt: "THE z/OS PROGRAM EXECUTION SUCCEED." 
ddnames:
    description: All the related dds with the program. 
    returned: always
    type: list<dict> 
    contains:
        ddname:
          description: data definition name
          type: str
        dataset:
          description: the dataset name  
          type: str
        content:
          description: ddname content
          type: list[str] 
        record_count:
          description: the lines of the content 
          type: int
        byte_count:
          description: bytes count
          type: int
    samples:         
        - ddname: "SYSIN", "SYSPRINT",etc.
        - dataset: "TEST.TESTER.DATA", "stdout", "dummy", etc
        - content: " "
        - record_count: 4
        - byte_count:  415
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
    auth: true
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
     
- name: Run isrsupc program,Compare 2 PDS members olddd and newdd and write the output to outdd. 
  zos_raw:
    program: ISRSUPC
    parms: DELTAL,LINECMP
    dds: [{ddName: newdd, dataset: TESTER.MVSUTIL.PYTHON.MVSCMD.A},
          {ddName: olddd, dataset: TESTER.MVSUTIL.PYTHON.MVSCMD.B},
          {ddName: sysin, dataset: TESTER.MVSUTIL.PYTHON.MVSCMD.OPT},
          {ddName: outdd, dataset: TESTER.MVSUTIL.PYTHON.MVSCMD.RESULT},
          {ddName: sysprint, dataset: TESTER.MVSUTIL.PYTHON.MVSCMD.RESULT2}
         ]

     
EXAMPLE RESULTS:
"msg": "    
    "changed": true,
    "ddnames": [
        {
            "byte_count": "748",
            "content": "TEST                                                                            ",
            "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.A",
            "ddname": "newdd",
            "record_count": 1
        },
        {
            "byte_count": "748",
            "content": "TEST                                                                            ",
            "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.B",
            "ddname": "olddd",
            "record_count": 1
        },
        {
            "byte_count": "748",
            "content": "   CMPCOLM 1:72                                                                 ",
            "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.OPT",
            "ddname": "sysin",
            "record_count": 1
        },
        {
            "byte_count": "3400",
            "content": "
                       ISRSUPC   -   MVS/PDF FILE/LINE/WORD/BYTE/SFOR COMPARE UTILITY- ISPF FOR z/OS         2020/02/25   3.36    PAGE     1
                        NEW: TESTER.MVSUTIL.PYTHON.MVSCMD.A                          OLD: TESTER.MVSUTIL.PYTHON.MVSCMD.B                       
                                                                                                                       
                                            LINE COMPARE SUMMARY AND STATISTICS                                                             
                                                                                                                       
                                                                                                                       
                                                                                                                       
                            1 NUMBER OF LINE MATCHES               0  TOTAL CHANGES (PAIRED+NONPAIRED CHNG)                                 
                            0 REFORMATTED LINES                    0  PAIRED CHANGES (REFM+PAIRED INS/DEL)                                  
                            0 NEW FILE LINE INSERTIONS             0  NON-PAIRED INSERTS                                                    
                            0 OLD FILE LINE DELETIONS              0  NON-PAIRED DELETES                                                    
                            1 NEW FILE LINES PROCESSED                                                                                      
                            1 OLD FILE LINES PROCESSED                                                                                      
                                                                                                                       
                    LISTING-TYPE = DELTA      COMPARE-COLUMNS =    1:72        LONGEST-LINE = 80                                           
                    PROCESS OPTIONS USED: NONE                                                                                             
                                                                                                                       
                    THE FOLLOWING PROCESS STATEMENTS (USING COLUMNS 1:72) WERE PROCESSED:                                                  
                            CMPCOLM 1:72                                                                                                     
                     " 
            "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.RESULT",
            "ddname": "outdd",
            "record_count": 20
        },
        {
            "byte_count": "0",
            "content": "",
            "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.RESULT2",
            "ddname": "sysprint",
            "record_count": 1
        }
    ],
    "ret_code": {
        "code": 0,
        "msg": 0,
        "msg_code": 0,
        "msg_txt": "THE z/OS PROGRAM EXECUTION SUCCEED.",
    }
"

"msg" : "
    "changed": true,
    "ddnames": [
        {
            "byte_count": "748",
            "content": "  LISTCAT ENT('TESTER.HILL3')                                                   ",
            "dataset": "TESTER.P3621680.T0979893.C0000000",
            "ddname": "sysin",
            "record_count": 1
        },
        {
            "byte_count": "2006",
            "content": "
                        1IDCAMS  SYSTEM SERVICES                                           TIME: 04:04:12        02/25/20     PAGE      1 
                        0                                                                                                                 
                        LISTCAT ENT('TESTER.HILL3')                                                                                    
                        0NONVSAM ------- TESTER.HILL3                                                                                     
                              IN-CAT --- ICFCAT.SYSPLEX2.CATALOGB                                                                         
                        1IDCAMS  SYSTEM SERVICES                                           TIME: 04:04:12        02/25/20     PAGE      2 
                        0         THE NUMBER OF ENTRIES PROCESSED WAS:                                                                    
                                            AIX -------------------0                                                                      
                                            ALIAS -----------------0                                                                      
                                            CLUSTER ---------------0                                                                      
                                            DATA ------------------0                                                                      
                                            GDG -------------------0                                                                      
                                            INDEX -----------------0                                                                      
                                            NONVSAM ---------------1                                                                      
                                            PAGESPACE -------------0                                                                      
                                            PATH ------------------0                                                                      
                                            SPACE -----------------0                                                                      
                                            USERCATALOG -----------0                                                                      
                                            TAPELIBRARY -----------0                                                                      
                                            TAPEVOLUME ------------0                                                                      
                                            TOTAL -----------------1                                                                      
                        0         THE NUMBER OF PROTECTED ENTRIES SUPPRESSED WAS 0                                                        
                        0IDC0001I FUNCTION COMPLETED, HIGHEST CONDITION CODE WAS 0                                                        
                        0                                                                                                                 
                        0IDC0002I IDCAMS PROCESSING COMPLETE. MAXIMUM CONDITION CODE WAS 0                                                
            " 
            "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.AUTH.OUT",
            "ddname": "sysprint",
            "record_count": 25
        }
    ], 
    "ret_code": {
        "code": 0,
        "msg": 0,
        "msg_code": 0,
        "msg_txt": "THE z/OS PROGRAM EXECUTION SUCCEED."
    }


"


"""

from ansible.module_utils.basic import *
from zoautil_py import MVSCmd, Datasets
import re

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

def parse_dds(dds,stdout):
    ddnames = []
    for item in dds:
        if item['dataset'] == 'stdout':
            content = stdout
            ddname = {
                'ddname': item['ddName'],
                'dataset': item['dataset'],
                'content': content,
                'record_count': len(re.split(r'\n*', content)),  # the lines of the content
                'byte_count': content.__sizeof__(),  # the bytes of the content
            }
        elif item['dataset'] == 'dummy':
            content = ""
            ddname = {
                'ddname': item['ddName'],
                'dataset': item['dataset'],
                'content': content,
                'record_count': '0',
                'byte_count': '0',
            }
        else:
            content = Datasets.read(item['dataset'])
            dataset_info = Datasets.list(item['dataset'], verbose=True)
            if content == None:
                content = ""
            ddname = {
                'ddname': item['ddName'],
                'dataset': item['dataset'],
                'content': content,
                'record_count': len(re.split(r'\n', content)),
                'byte_count': re.split(r'[\s]\s*', dataset_info)[6]  # In the position 6, it's used bytes.
            }

        ddnames.append(ddname)
    return ddnames


def run_module():
    module_args = dict(
        program=dict(type='str', required=True),
        auth=dict(type='bool', required=False, default=False),
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
        ddnames='',
        ret_code='',
    )
    hlq = Datasets.hlq()
    temp_dds = []

    if module.params.get("program") == None:
        module.fail_json(msg='THE z/OS PROGRAM CAN NOT BE EMPTY.', **result)

    try:
        dds = module.params.get("dds")
        contain_sysprint = False

        if dds != None:
            for item in dds:
                if item.get('ddName') == 'sysprint':
                    contain_sysprint = True
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
        ret_code = {
            'msg': rc,
            'msg_code': rc,
            'msg_txt': "",
            'code': rc,
        }
        if rc == 0 :
            ret_code['msg_txt'] = 'THE z/OS PROGRAM EXECUTION SUCCEED.'
        if rc == 36:
            ret_code['msg_txt'] = "BGYSC0236E Unable to call authorized program "+module.params.get("program")+". Please specify option 'auth' to true."
        elif rc != 0:
            ret_code['msg_txt'] = "THE z/OS PROGRAM EXECUTION FAILED."

        ddnames = parse_dds(dds,stdout)

        result['ddnames'] = ddnames
        result['ret_code'] = ret_code

        if rc != 0:
            module.fail_json(msg="THE z/OS program execution failed, please check the rec_code.",**result)
    except ZOSRawError as e:
        module.fail_json(msg="ZOSRawError :"+str(e), **result)
    except Exception as e:
        module.fail_json(msg="Exception :"+str(e), **result)
    finally:
        delete_data_sets(temp_dds)

    result['changed'] = True
    module.exit_json(**result)

class Error(Exception):
    pass

class ZOSRawError(Error):
    def __init__(self, program):
        self.msg = 'An error occurred during execution of z/OS program {}.'.format(program)


def main():
    run_module()


if __name__ == '__main__':
    main()
