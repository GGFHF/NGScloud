#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This software has been developed by:

    GI Genética, Fisiología e Historia Forestal
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politécnica de Madrid
    http://gfhforestal.com/
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

'''
This file contains functions related to BioInfo applications used in both console
mode and gui mode.
'''

#-------------------------------------------------------------------------------

import os
import re
import subprocess
import sys

import xcluster
import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def is_setup_miniconda3(cluster_name, passed_connection, ssh_client):
    '''
    Verify if Miniconda3 is set up.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # initialize the setup control variable
    is_setup = False

    # create the SSH client connection
    if not passed_connection:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if not OK:
            for error in error_list:
                error_list.append('{0}\n'.format(error))
                OK = False

    # verify the Miniconda3 directory is created
    if OK:
        command = '[ -d {0}/{1} ] && echo RC=0 || echo RC=1'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] == 'RC=0':
            OK = True
            is_setup = True
        else:
            OK = True
            is_setup = False

    # close the SSH client connection
    if OK and not passed_connection:
        xssh.close_ssh_client_connection(ssh_client)

    # return the control variable, error list and setup control variable
    return (OK, error_list, is_setup)

#-------------------------------------------------------------------------------

def setup_miniconda3(cluster_name, log, function=None):
    '''
    Set up the Miniconda3 in the cluster.
    '''

    # initialize the control variable
    OK = True

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # create the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH client ...\n')
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if OK:
            log.write('The SSH client is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SSH transport connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH transport ...\n')
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name, 'master')
        if OK:
            log.write('The SSH transport is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SFTP client 
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SFTP client ...\n')
        sftp_client = xssh.create_sftp_client(ssh_transport)
        log.write('The SFTP client is connected.\n')

    # warn that the requirements are being verified 
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Verifying process requirements ...\n')

    # verify the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir('setup', xlib.get_miniconda3_code())
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the Miniconda3 setup script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the setup script {0} ...\n'.format(get_miniconda3_setup_script()))
        (OK, error_list) = build_miniconda3_setup_script(cluster_name)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Miniconda3 setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the setup script {0} in the directory {1} of the master ...\n'.format(get_miniconda3_setup_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_miniconda3_setup_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_miniconda3_setup_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Miniconda3 setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_miniconda3_setup_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_miniconda3_setup_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the Miniconda3 setup starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_miniconda3_setup_starter()))
        (OK, error_list) = build_miniconda3_setup_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Miniconda3 setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} in the directory {1} of the master ...\n'.format(get_miniconda3_setup_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_miniconda3_setup_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_miniconda3_setup_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Miniconda3 setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_miniconda3_setup_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_miniconda3_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the Miniconda3 setup
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_miniconda3_setup_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_miniconda3_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                log.write('{0}\n'.format(line))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # close the SSH transport connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH transport connection ...\n')
        xssh.close_ssh_transport_connection(ssh_transport)
        log.write('The connection is closed.\n')

    # close the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def build_miniconda3_setup_script(cluster_name):
    '''
    Build the Miniconda3 setup script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the name, version and download URL of Miniconda3
    (miniconda3_version, miniconda3_url) = xconfiguration.get_bioinfo_app_data(xlib.get_miniconda3_name())

    # write the the Miniconda3 setup script
    try:
        if not os.path.exists(os.path.dirname(get_miniconda3_setup_script())):
            os.makedirs(os.path.dirname(get_miniconda3_setup_script()))
        with open(get_miniconda3_setup_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('export DEBIAN_FRONTEND=noninteractive'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function remove_miniconda3_directory'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Removing {0} directory ..."'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    cd {0}'.format(xlib.get_cluster_app_dir())))
            file_id.write('{0}\n'.format('    if [ -d "{0}" ]; then'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('        rm -rf {0}'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('        echo "The directory is removed."'))
            file_id.write('{0}\n'.format('    else'))
            file_id.write('{0}\n'.format('        echo "The directory is not found."'))
            file_id.write('{0}\n'.format('    fi'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function download_miniconda3_package'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Downloading the {0} installation package ..."'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    cd {0}'.format(xlib.get_cluster_app_dir())))
            file_id.write('{0}\n'.format('    wget --quiet --output-document {0}.sh {1}'.format(xlib.get_miniconda3_name(), miniconda3_url)))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error wget $RC; fi'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    echo "The package is downloaded."'))
            file_id.write('{0}\n'.format('    chmod u+x {0}.sh'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    echo "The run permision is set on."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_miniconda3'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing {0} to create Python 3 environment ..."'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    cd {0}'.format(xlib.get_cluster_app_dir())))
            file_id.write('{0}\n'.format('    ./{0}.sh -b -p {0}'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error {0} $RC; fi'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    echo "Python 3 environment is created."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function remove_miniconda3_package'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Removing the {0} installation package ..."'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    cd {0}'.format(xlib.get_cluster_app_dir())))
            file_id.write('{0}\n'.format('    rm -f {0}.sh'.format(xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    echo "The software is removed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_joblib_python3'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing joblib package in Python 3 environment ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./pip install --quiet joblib'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error pip $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_gffutils_python3'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing gffutils package in Python 3 environment ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./pip install --quiet gffutils'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error pip $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_matplotlib_python3'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing Matplotlib package in Python 3 environment ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./pip install --quiet matplotlib'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error pip $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_biopython_python3'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing BioPython package in Python 3 environment ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./pip install --quiet biopython'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error pip $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function create_python2_environment'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Creating the Python 2 environment ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda create --quiet --yes --name py27 python=2.7'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The environment is created."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_joblib_python2'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing joblib package in Python 2 environment ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    source activate py27'))
            file_id.write('{0}\n'.format('    pip install --quiet joblib'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error pip $RC; fi'))
            file_id.write('{0}\n'.format('    source deactivate py27'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_gffutils_python2'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing gffutils package in Python 2 environment ..."'))
            file_id.write('{0}\n'.format('    source activate py27'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    pip install --quiet gffutils'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error pip $RC; fi'))
            file_id.write('{0}\n'.format('    source deactivate py27'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_matplotlib_python2'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing Matplotlib package in Python 2 environment ..."'))
            file_id.write('{0}\n'.format('    source activate py27'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    pip install --quiet matplotlib'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error pip $RC; fi'))
            file_id.write('{0}\n'.format('    source deactivate py27'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_biopython_python2'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing BioPython package in Python 2 environment ..."'))
            file_id.write('{0}\n'.format('    source activate py27'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    pip install --quiet biopython'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error pip $RC; fi'))
            file_id.write('{0}\n'.format('    source deactivate py27'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function end'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script ended OK at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} setup"'.format(xlib.get_project_name(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} setup in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_miniconda3_name(), cluster_name)))
            file_id.write('{0}\n'.format('    mail --append "Content-type: text/html;"  --subject "$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"'))
            file_id.write('{0}\n'.format('    exit 0'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function manage_error'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "ERROR: $1 returned error $2"'))
            file_id.write('{0}\n'.format('    echo "Script ended WRONG at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} setup"'.format(xlib.get_project_name(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} setup in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_miniconda3_name(), cluster_name)))
            file_id.write('{0}\n'.format('    mail --append "Content-type: text/html;"  --subject "$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"'))
            file_id.write('{0}\n'.format('    exit 3'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function calculate_duration'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    DURATION=`expr $END_DATETIME - $INIT_DATETIME`'))
            file_id.write('{0}\n'.format('    HH=`expr $DURATION / 3600`'))
            file_id.write('{0}\n'.format('    MM=`expr $DURATION % 3600 / 60`'))
            file_id.write('{0}\n'.format('    SS=`expr $DURATION % 60`'))
            file_id.write('{0}\n'.format('    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('init'))
            file_id.write('{0}\n'.format('remove_miniconda3_directory'))
            file_id.write('{0}\n'.format('download_miniconda3_package'))
            file_id.write('{0}\n'.format('install_miniconda3'))
            file_id.write('{0}\n'.format('remove_miniconda3_package'))
            file_id.write('{0}\n'.format('install_joblib_python3'))
            file_id.write('{0}\n'.format('install_gffutils_python3'))
            file_id.write('{0}\n'.format('install_matplotlib_python3'))
            file_id.write('{0}\n'.format('install_biopython_python3'))
            file_id.write('{0}\n'.format('create_python2_environment'))
            file_id.write('{0}\n'.format('install_joblib_python2'))
            file_id.write('{0}\n'.format('install_gffutils_python2'))
            file_id.write('{0}\n'.format('install_matplotlib_python2'))
            file_id.write('{0}\n'.format('install_biopython_python2'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_miniconda3_setup_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_miniconda3_setup_starter(current_run_dir):
    '''
    Build the starter of the Miniconda3 setup.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Miniconda3 setup starter
    try:
        if not os.path.exists(os.path.dirname(get_miniconda3_setup_starter())):
            os.makedirs(os.path.dirname(get_miniconda3_setup_starter()))
        with open(get_miniconda3_setup_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_miniconda3_setup_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_miniconda3_setup_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_miniconda3_setup_script():
    '''
    Get the Miniconda3 setup path in the local computer.
    '''

    # assign the Miniconda3 setup path
    miniconda3_setup_script = '{0}/{1}-setup.sh'.format(xlib.get_temp_dir(), xlib.get_miniconda3_name())

    # return the Miniconda3 setup path
    return miniconda3_setup_script

#-------------------------------------------------------------------------------

def get_miniconda3_setup_starter():
    '''
    Get the Miniconda3 setup starter path in the local computer.
    '''

    # assign the Miniconda3 setup starter path
    miniconda3_setup_starter = '{0}/{1}-setup-starter.sh'.format(xlib.get_temp_dir(), xlib.get_miniconda3_name())

    # return the Miniconda3 setup starter path
    return miniconda3_setup_starter

#-------------------------------------------------------------------------------

def is_setup_conda_package(python_version, channel_code, package_code, cluster_name, passed_connection, ssh_client):
    '''
    Verify if a Conda package is set up.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # initialize the setup control variable
    is_setup = False

    # create the SSH client connection
    if not passed_connection:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if not OK:
            for error in error_list:
                error_list.append('{0}\n'.format(error))
                OK = False

    # verify the Conda package is set up
    if OK:
        if python_version in [2, 3]:
            if python_version == 3:
                command = 'cd {0}/{1}/bin; ./conda list {2}'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), package_code)
            elif python_version == 2:
                command = 'cd {0}/{1}/bin; source activate py27; ./conda list {2}'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), package_code)
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                for line in stdout:
                    if package_code in line:
                        is_setup = True
            else:
                error_list.append('*** ERROR: Wrong command ---> {0}\n'.format(command))
        else:
            error_list.append('Invalid Python version {0}\n'.format(python_version))
            OK = False

    # close the SSH client connection
    if OK and not passed_connection:
        xssh.close_ssh_client_connection(ssh_client)

    # return the control variable, error list and setup control variable
    return (OK, error_list, is_setup)

#-------------------------------------------------------------------------------

def setup_conda_package_list(app_code, app_name, python_version, channel_code, package_code_list, cluster_name, log, function=None):
    '''
    Set up a Conda package list.
    '''

    # initialize the control variable
    OK = True

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # create the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH client ...\n')
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if OK:
            log.write('The SSH client is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SSH transport connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH transport ...\n')
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name, 'master')
        if OK:
            log.write('The SSH transport is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SFTP client 
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SFTP client ...\n')
        sftp_client = xssh.create_sftp_client(ssh_transport)
        log.write('The SFTP client is connected.\n')

    # warn that Conda package setup requirements are being verified
    if OK: 
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Verifying the Conda package list ({0}) setup requirements ...\n'.format(str(package_code_list).strip('[]').replace('\'','')))

    # verify the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # verify the app directory is created
    if OK:
        command = '[ -d {0} ] && echo RC=0 || echo RC=1'.format(xlib.get_cluster_app_dir())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] == 'RC=0':
            OK = True
        else:
            log.write('*** ERROR: There is not any volume mounted in the directory.\n')
            log.write('You must link a volume in the mounting point {0} for the template {1}.\n'.format(xlib.get_cluster_app_dir(), cluster_name))
            OK = False

    # verify the Miniconda3 setup
    if OK:
        (OK, error_list, is_setup) = is_setup_miniconda3(cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** error: {0} is not setup. It must be previously set up.\n'.format(xlib.get_miniconda3_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification can not run.\n')

    # warn that the requirements are OK 
    if OK:
        log.write('Setup requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir('setup', app_code)
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the Conda package setup script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the setup script {0} ...\n'.format(get_conda_package_setup_script()))
        (OK, error_list) = build_conda_package_setup_script(app_name, python_version, channel_code, package_code_list, cluster_name)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Conda package setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the setup script {0} in the directory {1} of the master ...\n'.format(get_conda_package_setup_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_conda_package_setup_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_conda_package_setup_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Conda package setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_conda_package_setup_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_conda_package_setup_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the Conda package setup starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_conda_package_setup_starter()))
        (OK, error_list) = build_conda_package_setup_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Conda package setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} in the directory {1} of the master ...\n'.format(get_conda_package_setup_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_conda_package_setup_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_conda_package_setup_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Conda package setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_conda_package_setup_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_conda_package_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the Conda package setup
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_conda_package_setup_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_conda_package_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                log.write('{0}\n'.format(line))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # close the SSH transport connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH transport connection ...\n')
        xssh.close_ssh_transport_connection(ssh_transport)
        log.write('The connection is closed.\n')

    # close the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def build_conda_package_setup_script(app_name, python_version, channel_code, package_code_list, cluster_name):
    '''
    Build the Conda package setup script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the name, version and download URL of Miniconda3
    (miniconda3_version, miniconda3_url) = xconfiguration.get_bioinfo_app_data(xlib.get_miniconda3_name())

    # write the the Conda package setup script
    try:
        if not os.path.exists(os.path.dirname(get_conda_package_setup_script())):
            os.makedirs(os.path.dirname(get_conda_package_setup_script()))
        with open(get_conda_package_setup_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('export DEBIAN_FRONTEND=noninteractive'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            for package_code in package_code_list:
                file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
                file_id.write('{0}\n'.format('function install_conda_package_{0}'.format(package_code)))
                file_id.write('{0}\n'.format('{'))
                file_id.write('{0}\n'.format('    echo "$SEP"'))
                file_id.write('{0}\n'.format('    echo "Installing {0} package {1} ..."'.format(xlib.get_conda_name(), package_code)))
                file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
                if python_version == 2:
                    file_id.write('{0}\n'.format('    source activate py27'))
                if channel_code is None:
                    file_id.write('{0}\n'.format('    ./conda install --yes --quiet {0}'.format(package_code)))
                else:
                    file_id.write('{0}\n'.format('    ./conda install --yes --quiet --channel {0} {1}'.format(channel_code, package_code)))
                file_id.write('{0}\n'.format('    RC=$?'))
                file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
                if python_version == 2:
                    file_id.write('{0}\n'.format('    source deactivate py27'))
                file_id.write('{0}\n'.format('    echo "The package is installed."'))
                file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function end'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script ended OK at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} setup"'.format(xlib.get_project_name(), app_name)))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} setup in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(app_name, cluster_name)))
            file_id.write('{0}\n'.format('    mail --append "Content-type: text/html;"  --subject "$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"'))
            file_id.write('{0}\n'.format('    exit 0'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function manage_error'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "ERROR: $1 returned error $2"'))
            file_id.write('{0}\n'.format('    echo "Script ended WRONG at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} setup"'.format(xlib.get_project_name(), app_name)))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} setup in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(app_name, cluster_name)))
            file_id.write('{0}\n'.format('    mail --append "Content-type: text/html;"  --subject "$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"'))
            file_id.write('{0}\n'.format('    exit 3'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function calculate_duration'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    DURATION=`expr $END_DATETIME - $INIT_DATETIME`'))
            file_id.write('{0}\n'.format('    HH=`expr $DURATION / 3600`'))
            file_id.write('{0}\n'.format('    MM=`expr $DURATION % 3600 / 60`'))
            file_id.write('{0}\n'.format('    SS=`expr $DURATION % 60`'))
            file_id.write('{0}\n'.format('    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('init'))
            for package_code in package_code_list:
                file_id.write('{0}\n'.format('install_conda_package_{0}'.format(package_code)))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_conda_package_setup_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_conda_package_setup_starter(current_run_dir):
    '''
    Build the starter of the Conda package setup.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Conda package setup starter
    try:
        if not os.path.exists(os.path.dirname(get_conda_package_setup_starter())):
            os.makedirs(os.path.dirname(get_conda_package_setup_starter()))
        with open(get_conda_package_setup_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_conda_package_setup_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_conda_package_setup_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_conda_package_setup_script():
    '''
    Get the Conda package setup path in the local computer.
    '''

    # assign the Conda package setup path
    conda_package_setup_script = '{0}/{1}-setup.sh'.format(xlib.get_temp_dir(), xlib.get_conda_name())

    # return the Conda package setup path
    return conda_package_setup_script

#-------------------------------------------------------------------------------

def get_conda_package_setup_starter():
    '''
    Get the Conda package setup starter path in the local computer.
    '''

    # assign the Conda package setup starter path
    conda_package_setup_starter = '{0}/{1}-setup-starter.sh'.format(xlib.get_temp_dir(), xlib.get_conda_name())

    # return the Conda package setup starter path
    return conda_package_setup_starter

#-------------------------------------------------------------------------------

def is_setup_bioconda_package(package_code, cluster_name, passed_connection, ssh_client):
    '''
    Verify if a Bioconda package is set up.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # initialize the setup control variable
    is_setup = False

    # create the SSH client connection
    if not passed_connection:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if not OK:
            for error in error_list:
                error_list.append('{0}\n'.format(error))
                OK = False

    # verify the Bioconda package directory is created
    if OK:
        command = '[ -d {0}/{1}/envs/{2} ] && echo RC=0 || echo RC=1'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), package_code)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] == 'RC=0':
            OK = True
            is_setup = True
        else:
            OK = True
            is_setup = False

    # close the SSH client connection
    if OK and not passed_connection:
        xssh.close_ssh_client_connection(ssh_client)

    # return the control variable, error list and setup control variable
    return (OK, error_list, is_setup)

#-------------------------------------------------------------------------------

def setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, log, function=None):
    '''
    Set up the Bioconda package list in the cluster.
    '''

    # initialize the control variable
    OK = True

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # create the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH client ...\n')
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if OK:
            log.write('The SSH client is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SSH transport connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH transport ...\n')
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name, 'master')
        if OK:
            log.write('The SSH transport is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SFTP client 
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SFTP client ...\n')
        sftp_client = xssh.create_sftp_client(ssh_transport)
        log.write('The SFTP client is connected.\n')

    # warn that Bioconda package setup requirements are being verified
    if OK: 
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Verifying the Bioconda package list ({0}) setup requirements ...\n'.format(str(package_code_list).strip('[]').replace('\'','')))

    # verify the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # verify the app directory is created
    if OK:
        command = '[ -d {0} ] && echo RC=0 || echo RC=1'.format(xlib.get_cluster_app_dir())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] == 'RC=0':
            OK = True
        else:
            log.write('*** ERROR: There is not any volume mounted in the directory.\n')
            log.write('You must link a volume in the mounting point {0} for the template {1}.\n'.format(xlib.get_cluster_app_dir(), cluster_name))
            OK = False

    # verify the Miniconda3 setup
    if OK:
        (OK, error_list, is_setup) = is_setup_miniconda3(cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** error: {0} is not setup. It must be previously set up.\n'.format(xlib.get_miniconda3_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification can not run.\n')

    # warn that the requirements are OK 
    if OK:
        log.write('Setup requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir('setup', app_code)
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the Bioconda package setup script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the setup script {0} ...\n'.format(get_bioconda_package_setup_script()))
        (OK, error_list) = build_bioconda_package_setup_script(app_name, package_code_list, cluster_name)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Bioconda package setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the setup script {0} in the directory {1} of the master ...\n'.format(get_bioconda_package_setup_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_bioconda_package_setup_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_bioconda_package_setup_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Bioconda package setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_bioconda_package_setup_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_bioconda_package_setup_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the Bioconda package setup starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_bioconda_package_setup_starter()))
        (OK, error_list) = build_bioconda_package_setup_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Bioconda package setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} in the directory {1} of the master ...\n'.format(get_bioconda_package_setup_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_bioconda_package_setup_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_bioconda_package_setup_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Bioconda package setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_bioconda_package_setup_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_bioconda_package_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the Bioconda package setup
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_bioconda_package_setup_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_bioconda_package_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                log.write('{0}\n'.format(line))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # close the SSH transport connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH transport connection ...\n')
        xssh.close_ssh_transport_connection(ssh_transport)
        log.write('The connection is closed.\n')

    # close the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def build_bioconda_package_setup_script(app_name, package_code_list, cluster_name):
    '''
    Build the Bioconda package setup script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the name, version and download URL of Miniconda3
    (miniconda3_version, miniconda3_url) = xconfiguration.get_bioinfo_app_data(xlib.get_miniconda3_name())

    # write the the Bioconda package setup script
    try:
        if not os.path.exists(os.path.dirname(get_bioconda_package_setup_script())):
            os.makedirs(os.path.dirname(get_bioconda_package_setup_script()))
        with open(get_bioconda_package_setup_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('export DEBIAN_FRONTEND=noninteractive'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function add_channel_defaults'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Adding channel defaults ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda config --add channels defaults'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The channel is added."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function add_channel_conda_forge'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Adding channel conda-forge ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda config --add channels conda-forge'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The channel is added."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function add_channel_r'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Adding channel r ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda config --add channels r'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The channel is added."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function add_channel_bioconda'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Adding channel bioconda ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda config --add channels bioconda'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The channel is added."'))
            file_id.write('{0}\n'.format('}'))
            for package_code in package_code_list:
                file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
                file_id.write('{0}\n'.format('function remove_bioconda_package_{0}'.format(package_code)))
                file_id.write('{0}\n'.format('{'))
                file_id.write('{0}\n'.format('    echo "$SEP"'))
                file_id.write('{0}\n'.format('    echo "Removing {0} package {1} ..."'.format(xlib.get_bioconda_name(), package_code)))
                file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
                file_id.write('{0}\n'.format('    ./conda env remove --yes --quiet --name {0}'.format(package_code)))
                file_id.write('{0}\n'.format('    RC=$?'))
                file_id.write('{0}\n'.format('    if [ $RC -eq 0 ]; then'))
                file_id.write('{0}\n'.format('      echo "The old package is removed."'))
                file_id.write('{0}\n'.format('    else'))
                file_id.write('{0}\n'.format('      echo "The old package is not found."'))
                file_id.write('{0}\n'.format('    fi'))
                file_id.write('{0}\n'.format('}'))
                file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
                file_id.write('{0}\n'.format('function install_bioconda_package_{0}'.format(package_code)))
                file_id.write('{0}\n'.format('{'))
                file_id.write('{0}\n'.format('    echo "$SEP"'))
                file_id.write('{0}\n'.format('    echo "Installing {0} package {1} ..."'.format(xlib.get_bioconda_name(), package_code)))
                file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
                file_id.write('{0}\n'.format('    ./conda create --yes --quiet --name {0} {0}'.format(package_code)))
                file_id.write('{0}\n'.format('    RC=$?'))
                file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
                file_id.write('{0}\n'.format('    echo "The package is installed."'))
                file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function end'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script ended OK at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} setup"'.format(xlib.get_project_name(), app_name)))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} setup in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(app_name, cluster_name)))
            file_id.write('{0}\n'.format('    mail --append "Content-type: text/html;"  --subject "$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"'))
            file_id.write('{0}\n'.format('    exit 0'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function manage_error'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "ERROR: $1 returned error $2"'))
            file_id.write('{0}\n'.format('    echo "Script ended WRONG at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} setup"'.format(xlib.get_project_name(), app_name)))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} setup in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(app_name, cluster_name)))
            file_id.write('{0}\n'.format('    mail --append "Content-type: text/html;"  --subject "$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"'))
            file_id.write('{0}\n'.format('    exit 3'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function calculate_duration'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    DURATION=`expr $END_DATETIME - $INIT_DATETIME`'))
            file_id.write('{0}\n'.format('    HH=`expr $DURATION / 3600`'))
            file_id.write('{0}\n'.format('    MM=`expr $DURATION % 3600 / 60`'))
            file_id.write('{0}\n'.format('    SS=`expr $DURATION % 60`'))
            file_id.write('{0}\n'.format('    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('init'))
            file_id.write('{0}\n'.format('add_channel_defaults'))
            file_id.write('{0}\n'.format('add_channel_conda_forge'))
            file_id.write('{0}\n'.format('add_channel_r'))
            file_id.write('{0}\n'.format('add_channel_bioconda'))
            for package_code in package_code_list:
                file_id.write('{0}\n'.format('remove_bioconda_package_{0}'.format(package_code)))
                file_id.write('{0}\n'.format('install_bioconda_package_{0}'.format(package_code)))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_bioconda_package_setup_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_bioconda_package_setup_starter(current_run_dir):
    '''
    Build the starter of the Bioconda package setup.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Bioconda package setup starter
    try:
        if not os.path.exists(os.path.dirname(get_bioconda_package_setup_starter())):
            os.makedirs(os.path.dirname(get_bioconda_package_setup_starter()))
        with open(get_bioconda_package_setup_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_bioconda_package_setup_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_bioconda_package_setup_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_bioconda_package_setup_script():
    '''
    Get the Bioconda package setup path in the local computer.
    '''

    # assign the Bioconda package setup path
    bioconda_package_setup_script = '{0}/{1}-setup.sh'.format(xlib.get_temp_dir(), xlib.get_bioconda_name())

    # return the Bioconda package setup path
    return bioconda_package_setup_script

#-------------------------------------------------------------------------------

def get_bioconda_package_setup_starter():
    '''
    Get the Bioconda package setup starter path in the local computer.
    '''

    # assign the Bioconda package setup starter path
    bioconda_package_setup_starter = '{0}/{1}-setup-starter.sh'.format(xlib.get_temp_dir(), xlib.get_bioconda_name())

    # return the Bioconda package setup starter path
    return bioconda_package_setup_starter

#-------------------------------------------------------------------------------

def is_setup_r(cluster_name, passed_connection, ssh_client):
    '''
    Verify if R is set up.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # initialize the setup control variable
    is_setup = False

    # create the SSH client connection
    if not passed_connection:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if not OK:
            for error in error_list:
                error_list.append('{0}\n'.format(error))
                OK = False

    # verify the Bioconda package directory is created
    if OK:
        command = '[ -d {0}/{1}/envs/{2} ] && echo RC=0 || echo RC=1'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_r_name())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] == 'RC=0':
            OK = True
            is_setup = True
        else:
            OK = True
            is_setup = False

    # close the SSH client connection
    if OK and not passed_connection:
        xssh.close_ssh_client_connection(ssh_client)

    # return the control variable, error list and setup control variable
    return (OK, error_list, is_setup)

#-------------------------------------------------------------------------------

def setup_r(cluster_name, log, function=None):
    '''
    Set up the Bioconda package list in the cluster.
    '''

    # initialize the control variable
    OK = True

    # set the addicional R package code list
    package_code_list = []

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # create the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH client ...\n')
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if OK:
            log.write('The SSH client is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SSH transport connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH transport ...\n')
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name, 'master')
        if OK:
            log.write('The SSH transport is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SFTP client 
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SFTP client ...\n')
        sftp_client = xssh.create_sftp_client(ssh_transport)
        log.write('The SFTP client is connected.\n')

    # warn that R setup requirements are being verified
    if OK: 
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Verifying the R and analysis packages ({0}) setup requirements ...\n'.format(str(package_code_list).strip('[]').replace('\'','')))

    # verify the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # verify the app directory is created
    if OK:
        command = '[ -d {0} ] && echo RC=0 || echo RC=1'.format(xlib.get_cluster_app_dir())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] == 'RC=0':
            OK = True
        else:
            log.write('*** ERROR: There is not any volume mounted in the directory.\n')
            log.write('You must link a volume in the mounting point {0} for the template {1}.\n'.format(xlib.get_cluster_app_dir(), cluster_name))
            OK = False

    # verify the Miniconda3 setup
    if OK:
        (OK, error_list, is_setup) = is_setup_miniconda3(cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** error: {0} is not setup. It must be previously set up.\n'.format(xlib.get_miniconda3_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification can not run.\n')

    # warn that the requirements are OK 
    if OK:
        log.write('Setup requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir('setup', xlib.get_r_code())
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the R setup script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the setup script {0} ...\n'.format(get_r_setup_script()))
        (OK, error_list) = build_r_setup_script(package_code_list, cluster_name)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the R setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the setup script {0} in the directory {1} of the master ...\n'.format(get_r_setup_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_r_setup_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_r_setup_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the R setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_r_setup_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_r_setup_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the R setup starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_r_setup_starter()))
        (OK, error_list) = build_r_setup_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the R setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} in the directory {1} of the master ...\n'.format(get_r_setup_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_r_setup_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_r_setup_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the R setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_r_setup_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_r_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the R setup
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_r_setup_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_r_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                log.write('{0}\n'.format(line))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # close the SSH transport connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH transport connection ...\n')
        xssh.close_ssh_transport_connection(ssh_transport)
        log.write('The connection is closed.\n')

    # close the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def build_r_setup_script(package_code_list, cluster_name):
    '''
    Build the R setup script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the name, version and download URL of Miniconda3
    (miniconda3_version, miniconda3_url) = xconfiguration.get_bioinfo_app_data(xlib.get_miniconda3_name())

    # write the the R setup script
    #try:
    if True:
        if not os.path.exists(os.path.dirname(get_r_setup_script())):
            os.makedirs(os.path.dirname(get_r_setup_script()))
        with open(get_r_setup_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('export DEBIAN_FRONTEND=noninteractive'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function add_channel_defaults'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Adding channel defaults ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda config --add channels defaults'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The channel is added."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function add_channel_conda_forge'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Adding channel conda-forge ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda config --add channels conda-forge'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The channel is added."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function add_channel_r'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Adding channel r ..."'))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda config --add channels r'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The channel is added."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function remove_r'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Removing {0} ..."'.format(xlib.get_r_name())))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda env remove --yes --quiet --name {0}'.format(xlib.get_r_name())))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -eq 0 ]; then'))
            file_id.write('{0}\n'.format('      echo "The old package is removed."'))
            file_id.write('{0}\n'.format('    else'))
            file_id.write('{0}\n'.format('      echo "The old package is not found."'))
            file_id.write('{0}\n'.format('    fi'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_r'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing {0} ..."'.format(xlib.get_r_name())))
            file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('    ./conda create --yes --quiet --name {0} r-essentials'.format(xlib.get_r_name())))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            for package_code in package_code_list:
                file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
                file_id.write('{0}\n'.format('function install_r_package_{0}'.format(package_code)))
                file_id.write('{0}\n'.format('{'))
                file_id.write('{0}\n'.format('    echo "$SEP"'))
                file_id.write('{0}\n'.format('    echo "Installing {0} package {1} ..."'.format(xlib.get_conda_name(), package_code)))
                file_id.write('{0}\n'.format('    cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
                file_id.write('{0}\n'.format('    source activate {0}'.format(xlib.get_r_name())))
                file_id.write('{0}\n'.format('    ./conda install --yes --quiet {0}'.format(package_code)))
                file_id.write('{0}\n'.format('    RC=$?'))
                file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error conda $RC; fi'))
                file_id.write('{0}\n'.format('    source deactivate {0}'.format(xlib.get_r_name())))
                file_id.write('{0}\n'.format('    echo "The package is installed."'))
                file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function end'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script ended OK at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} and analysis packages setup"'.format(xlib.get_project_name(), xlib.get_r_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The setup of {0} and analysis packages ({1}) in node $HOSTNAME of cluster {0} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_r_name(), str(package_code_list).strip('[]').replace('\'',''), cluster_name)))
            file_id.write('{0}\n'.format('    mail --append "Content-type: text/html;"  --subject "$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"'))
            file_id.write('{0}\n'.format('    exit 0'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function manage_error'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    END_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_END_DATETIME=`date --date="@$END_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    calculate_duration'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "ERROR: $1 returned error $2"'))
            file_id.write('{0}\n'.format('    echo "Script ended WRONG at $FORMATTED_END_DATETIME UTC with a run duration of $DURATION s ($FORMATTED_DURATION)."'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} and analysis packages setup"'.format(xlib.get_project_name(), xlib.get_r_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The setup of {0} and analysis packages ({1}) in node $HOSTNAME of cluster {0} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_r_name(), str(package_code_list).strip('[]').replace('\'',''), cluster_name)))
            file_id.write('{0}\n'.format('    mail --append "Content-type: text/html;"  --subject "$SUBJECT" "$RECIPIENT" <<< "$MESSAGE"'))
            file_id.write('{0}\n'.format('    exit 3'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function calculate_duration'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    DURATION=`expr $END_DATETIME - $INIT_DATETIME`'))
            file_id.write('{0}\n'.format('    HH=`expr $DURATION / 3600`'))
            file_id.write('{0}\n'.format('    MM=`expr $DURATION % 3600 / 60`'))
            file_id.write('{0}\n'.format('    SS=`expr $DURATION % 60`'))
            file_id.write('{0}\n'.format('    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('init'))
            file_id.write('{0}\n'.format('add_channel_defaults'))
            file_id.write('{0}\n'.format('add_channel_conda_forge'))
            file_id.write('{0}\n'.format('add_channel_r'))
            file_id.write('{0}\n'.format('remove_r'))
            file_id.write('{0}\n'.format('install_r'))
            for package_code in package_code_list:
                file_id.write('{0}\n'.format('install_r_package_{0}'.format(package_code)))
            file_id.write('{0}\n'.format('end'))
    #except:
    #    error_list.append('*** ERROR: The file {0} can not be created'.format(get_r_setup_script()))
    #    OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_r_setup_starter(current_run_dir):
    '''
    Build the starter of the R setup.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the R setup starter
    try:
        if not os.path.exists(os.path.dirname(get_r_setup_starter())):
            os.makedirs(os.path.dirname(get_r_setup_starter()))
        with open(get_r_setup_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_r_setup_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_r_setup_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_r_setup_script():
    '''
    Get the R setup path in the local computer.
    '''

    # assign the R setup path
    r_setup_script = '{0}/{1}-setup.sh'.format(xlib.get_temp_dir(), xlib.get_r_name())

    # return the R setup path
    return r_setup_script

#-------------------------------------------------------------------------------

def get_r_setup_starter():
    '''
    Get the R setup starter path in the local computer.
    '''

    # assign the R setup starter path
    r_setup_starter = '{0}/{1}-setup-starter.sh'.format(xlib.get_temp_dir(), xlib.get_r_name())

    # return the R setup starter path
    return r_setup_starter

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to BioInfo applications used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
