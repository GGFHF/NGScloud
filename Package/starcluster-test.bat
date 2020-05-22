@echo off

rem ----------------------------------------------------------------------------

rem Set run environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHONPATH=.

set STARCLUSTER_CONFIG=.\config\test-ngscloud-config.txt

rem ----------------------------------------------------------------------------

rem Execute the program starcluster.exe

:STARCLUSTER

starcluster.exe %*
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

:END

if %ERROR% equ 0 (
    rem exit 0
)

if %ERROR% equ 1 (
    echo *** ERROR: StarCluster ended with return code %RC%.
    rem exit %RC%
)

rem ----------------------------------------------------------------------------
