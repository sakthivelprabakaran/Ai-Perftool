import os
from typing import Dict, Any

# --- Template for globals.h ---
GLOBALS_H_TPL = """
#ifndef _GLOBALS_H
#define _GLOBALS_H

//--------------------------------------------------------------------
// Include Files
#include "lrun.h"
#include "web_api.h"
#include "lrw_custom_body.h"

//--------------------------------------------------------------------
// Global Variables

#endif // _GLOBALS_H
"""

# --- Template for vuser_init.c and vuser_end.c ---
VUSER_INIT_TPL = "vuser_init()\\n{\\n    return 0;\\n}"
VUSER_END_TPL = "vuser_end()\\n{\\n    return 0;\\n}"

# --- Template for default.cfg ---
DEFAULT_CFG_TPL = """
[General]
XlBridgeTimeout=120
DefaultRunLogic=default.usp
automatic_nested_transactions=1
AutomaticTransactions=1
[ThinkTime]
Options=NOTHINK
Factor=1
LimitFlag=0
Limit=1
[Iterations]
NumOfIterations=1
IterationPace=IterationASAP
StartEvery=60
RandomMin=60
RandomMax=90
[Log]
LogOptions=LogBrief
MsgClassData=0
MsgClassParameters=0
MsgClassFull=0
[WEB]
SearchForImages=1
WebRecorderVersion=8
MaxConnections=0
LogFileWriteTraceToFile=0
LogFileWrite=0
"""

# --- Template for default.usp ---
DEFAULT_USP_TPL = """
[RunLogic]
Action=Action
[VuserProfiles]
Profiles=1
"""

# --- Template for <ScriptName>.usr ---
SCRIPT_USR_TPL = """
[General]
Type=Web
Version=12.60
ScriptLanguage=C
[Actions]
vuser_init=vuser_init.c
Action=Action.c
vuser_end=vuser_end.c
[RunLogicFiles]
Default Profile=default.usp
"""

# --- Template for ScriptUploadMetadata.xml ---
METADATA_XML_TPL = """<?xml version="1.0" encoding="utf-8"?>
<VugenScriptMetadata>
  <ScriptName>{script_name}</ScriptName>
  <Protocol>Web - HTTP/HTML</Protocol>
  <ActionFiles>
    <FileEntry Name="vuser_init.c" Filter="2" />
    <FileEntry Name="Action.c" Filter="2" />
    <FileEntry Name="vuser_end.c" Filter="2" />
  </ActionFiles>
  <GeneralFiles>
    <FileEntry Name="{script_name}.usr" Filter="4" />
    <FileEntry Name="default.cfg" Filter="4" />
    <FileEntry Name="default.usp" Filter="4" />
    <FileEntry Name="globals.h" Filter="2" />
    <FileEntry Name="ScriptUploadMetadata.xml" Filter="2" />
    <FileEntry Name="Bookmarks.xml" Filter="2" />
    <FileEntry Name="Breakpoints.xml" Filter="2" />
  </GeneralFiles>
</VugenScriptMetadata>
"""

def _generate_action_c_content(test_case_data: Dict[str, Any]) -> str:
    """Generates the content for the Action.c file."""
    steps_code = []
    for i, step in enumerate(test_case_data.get("steps", [])):
        step_name = step.get("text", f"Step {i+1}").replace('"', '\\"')
        target_url = step.get("target", "").replace('"', '\\"')

        web_url_call = f'    web_url("Request {i+1}_{step_name}",\\n'
        web_url_call += f'        "URL={target_url}",\\n'
        web_url_call += '        "Resource=0",\\n'
        web_url_call += '        "RecContentType=text/html",\\n'
        web_url_call += '        "Mode=HTML",\\n'
        web_url_call += '        LAST);'
        steps_code.append(web_url_call)

    steps_str = "\\n\\n".join(steps_code)
    return f"Action()\\n{{\\n{steps_str}\\n\\n    return 0;\\n}}"

def export_to_loadrunner(test_case_data: Dict[str, Any], script_name: str, output_dir: str = ".") -> str:
    """
    Exports a test case to a LoadRunner script structure and returns the path.
    """
    script_path = os.path.join(output_dir, script_name)
    os.makedirs(script_path, exist_ok=True)

    files_to_create = {
        "Action.c": _generate_action_c_content(test_case_data),
        "vuser_init.c": VUSER_INIT_TPL,
        "vuser_end.c": VUSER_END_TPL,
        "globals.h": GLOBALS_H_TPL,
        "default.cfg": DEFAULT_CFG_TPL,
        "default.usp": DEFAULT_USP_TPL,
        f"{script_name}.usr": SCRIPT_USR_TPL,
        "ScriptUploadMetadata.xml": METADATA_XML_TPL.format(script_name=script_name),
        "Bookmarks.xml": "<Bookmarks />",
        "Breakpoints.xml": "<Breakpoints />",
    }

    for filename, content in files_to_create.items():
        with open(os.path.join(script_path, filename), "w", encoding="utf-8") as f:
            f.write(content)

    return os.path.abspath(script_path)
