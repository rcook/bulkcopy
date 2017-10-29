:<<"::CMDLITERAL"
@echo off
goto :CMDSCRIPT
::CMDLITERAL
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

this_dir=$(cd $(dirname $0); pwd -P)
root_dir=$(dirname $this_dir)
env_dir=$root_dir/env
python_path=$env_dir/bin/python
pip_path=$env_dir/bin/pip

if [ ! -e $python_path ]; then
    virtualenv $env_dir
fi

cd $root_dir
$pip_path install -r $root_dir/requirements.txt
exit $?
:CMDSCRIPT
setlocal
set args=%*
call :Main "%~dp0" "%~dp0.." || exit /b 1
exit /b 0

:Main
set x=%~f1
set this_dir=%x:~0,-1%
set root_dir=%~f2
set env_dir=%root_dir%\env
set python_path=%env_dir%\Scripts\python.exe
set pip_path=%env_dir%\Scripts\pip.exe

if not exist "%python_path%" (
    mkdir "%env_dir%"
    cd /d "%env_dir%"
    python -m virtualenv . || exit /b 1
)

cd /d "%root_dir%"
"%pip_path%" install -r "%root_dir%\requirements.txt" || exit /b 1
exit /b 0
