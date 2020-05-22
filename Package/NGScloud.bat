@echo off

rem ----------------------------------------------------------------------------

rem Set run environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHONOPTIONS=
set PYTHONPATH=.
set NGSCLOUD=.
set ARGV=

cd %NGSCLOUD%

rem ----------------------------------------------------------------------------

rem Execute the program NGScloud.py

:NGSCLOUD

python.exe %PYTHONOPTIONS% NGScloud.py %* %ARGV%
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

:END

if %ERROR% equ 0 (
    rem -- exit 0
)

if %ERROR% equ 1 (
    echo *** ERROR: The program ended with return code %RC%.
    rem -- pause
    rem -- exit %RC%
)

rem ----------------------------------------------------------------------------
