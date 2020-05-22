@echo off

rem ----------------------------------------------------------------------------

rem Set run environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHONPATH=.

set STARCLUSTER_CONFIG=.\config\%1-ngscloud-config.txt

rem ----------------------------------------------------------------------------

rem Execute the program StarCluster.exe

:STARCLUSTER

starcluster.exe sshnode %2 %3
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

:END

if %ERROR% equ 0 (
    exit 0
)

if %ERROR% equ 1 (
    echo *** ERROR: StarCluster ended with return code %RC%.
    exit %RC%
)

rem ----------------------------------------------------------------------------
