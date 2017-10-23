:<<"::CMDLITERAL"
@echo off
goto :CMDSCRIPT
::CMDLITERAL
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

script_dir=$(cd $(dirname $0); pwd -P)
python_path=$script_dir/bin/python
pip_path=$script_dir/bin/pip

if [ ! -e $python_path ]; then
    virtualenv $script_dir
fi

$pip_path install -q -r $script_dir/requirements.txt
$python_path $*

exit $?
:CMDSCRIPT
@echo off
setlocal

set python_path=%~dp0Scripts\python.exe
set pip_path=%~dp0Scripts\pip.exe

if not exist "%python_path%" (
    cd /d "%~dp0"
    python -m virtualenv .
    if errorlevel 1 (
        echo virtualenv failed
        exit /b 1
    )
)

"%pip_path%" install -q -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo pip failed
    exit /b 1
)

"%python_path%" %*
if errorlevel 1 (
    echo script failed
    exit /b 1
)
