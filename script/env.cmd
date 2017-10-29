:<<"::CMDLITERAL"
@echo off
goto :CMDSCRIPT
::CMDLITERAL
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

script_name=$1
shift
args=$*
this_dir=$(cd $(dirname $0); pwd -P)
root_dir=$(dirname $this_dir)
env_dir=$root_dir/env
bin_dir=$env_dir/bin

if [ ! -e $bin_dir/python ]; then
    echo "Please create or update your virtual environment by running script/virtualenv"
    exit 1
fi

script_path=$bin_dir/$script_name

$script_path $args
exit $?
:CMDSCRIPT
setlocal
set script_name=%1
for /f "tokens=1,* delims= " %%a in ("%*") do set args=%%b
call :Main "%~dp0" "%~dp0.." || exit /b 1
exit /b 0

:Main
set x=%~f1
set this_dir=%x:~0,-1%
set root_dir=%~f2
set env_dir=%root_dir%\env
set bin_dir=%env_dir%\Scripts

if not exist "%bin_dir%\python.exe" (
    echo Please create or update your virtual environment by running script\virtualenv
    exit /b 1
)

set script_path=%bin_dir%\%script_name%.exe

%script_path% %args% || exit /b 1
exit /b 0
