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
This file contains functions related to the Transrate process used in both console
mode and gui mode.
'''

#-------------------------------------------------------------------------------

import os
import re
import sys
import urllib

import xbioinfoapp
import xcluster
import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def is_setup_transrate(cluster_name, passed_connection, ssh_client):
    '''
    Verify if Transrate is setup.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # initialize the setup control variable
    is_setup = False

    # get the aplication directory in the cluster
    cluster_app_dir = xlib.get_cluster_app_dir()

    # create the SSH client connection
    if not passed_connection:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if not OK:
            for error in error_list:
                error_list.append('{0}\n'.format(error))
                OK = False

    # verify the Transrate directory is created
    if OK:
        command = '[ -d {0}/{1} ] && echo RC=0 || echo RC=1'.format(cluster_app_dir, xlib.get_Transrate_name())
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

def setup_transrate(cluster_name, log, function=None):
    '''
    Set up the Transrate software in the cluster.
    '''

    # initialize the control variable
    OK = True

    # get the version and download URL of Transrate
    (transrate_version, transrate_url) = xconfiguration.get_bioinfo_app_data(xlib.get_transrate_name())

    # get the aplication directory in the cluster
    cluster_app_dir = xlib.get_cluster_app_dir()

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('Do not close this window, please wait!\n')

    # create the SSH client connection
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
        log.write('Verifying setup requirements ...\n')

    # verify the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # verify the app directory is created
    if OK:
        command = '[ -d {0} ] && echo RC=0 || echo RC=1'.format(cluster_app_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] != 'RC=0':
            log.write('*** ERROR: There is not any volume mounted in the directory.\n')
            log.write('You must link a volume in the mounting point {0} for the template {1}.\n'.format(cluster_app_dir, cluster_name))
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Setup requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir('setup', xlib.get_transrate_code())
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # download the Transrate compressed file to local computer
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Downloading the {0} compressed file to local computer ...\n'.format(xlib.get_transrate_name()))
        local_path = '{0}/{1}.tar.gz'.format(xlib.get_temp_dir(), xlib.get_transrate_name())
        if not os.path.exists(os.path.dirname(local_path)):
            os.makedirs(os.path.dirname(local_path))
        try:
            urllib.request.urlretrieve(transrate_url, local_path)
        except:
            log.write('*** ERROR: The file {0} can not be downloaded.\n'.format(transrate_url))
            OK = False
        else:
            log.write('The file is downloaded.\n')

    # upload the Transrate compressed file to cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the {0} compressed file to the cluster ...\n'.format(xlib.get_transrate_name()))
        cluster_path = '{0}/{1}'.format(cluster_app_dir, os.path.basename(local_path))
        (OK, error_list) = xssh.put_file(sftp_client, local_path, cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # build the Transrate setup script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the setup script {0} ...\n'.format(get_transrate_setup_script()))
        (OK, error_list) = build_transrate_setup_script(cluster_name)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Transrate setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the setup script {0} in the directory {1} of the master ...\n'.format(get_transrate_setup_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_transrate_setup_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_transrate_setup_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Transrate setup script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transrate_setup_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_transrate_setup_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the Transrate setup starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_transrate_setup_starter()))
        (OK, error_list) = build_transrate_setup_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Transrate setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} in the directory {1} of the master ...\n'.format(get_transrate_setup_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_transrate_setup_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_transrate_setup_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Transrate setup starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transrate_setup_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_transrate_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the Transrate setup
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transrate_setup_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_transrate_setup_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                log.write('{0}\n'.format(line))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # close the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # execute final function
    if function is not None:
        function()

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def build_transrate_setup_script(cluster_name):
    '''
    Build the Transrate setup script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the version and download URL of Transrate
    (transrate_version, transrate_url) = xconfiguration.get_bioinfo_app_data(xlib.get_transrate_name())

    # write the the Transrate setup script
    try:
        if not os.path.exists(os.path.dirname(get_transrate_setup_script())):
            os.makedirs(os.path.dirname(get_transrate_setup_script()))
        with open(get_transrate_setup_script(), mode='w', encoding='utf8', newline='\n') as file_id:
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
            file_id.write('{0}\n'.format('function remove_transrate_directory'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Removing {0} directory ..."'.format(xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    cd {0}'.format(xlib.get_cluster_app_dir())))
            file_id.write('{0}\n'.format('    if [ -d "{0}" ]; then'.format(xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('        rm -rf {0}'.format(xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('        echo "The directory is removed."'))
            file_id.write('{0}\n'.format('    else'))
            file_id.write('{0}\n'.format('        echo "The directory is not found."'))
            file_id.write('{0}\n'.format('    fi'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function decompress_transrate_setup_file'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Decompressing the {0} setup file ..."'.format(xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    cd {0}'.format(xlib.get_cluster_app_dir())))
            file_id.write('{0}\n'.format('    tar -xzvf {0}.tar.gz'.format(xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error tar $RC; fi'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    echo "The file is decompressed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function rename_transrate_directory'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Renaming the {0} directory ..."'.format(xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    cd {0}'.format(xlib.get_cluster_app_dir())))
            file_id.write('{0}\n'.format('    mv {0}-{1}-linux-x86_64 {2}'.format(xlib.get_transrate_code(), transrate_version, xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error mv $RC; fi'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    echo "The directory is renamed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function remove_transrate_setup_file'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Removing the {0} setup file ..."'.format(xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    cd {0}'.format(xlib.get_cluster_app_dir())))
            file_id.write('{0}\n'.format('    rm -f {0}.tar.gz'.format(xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error rm $RC; fi'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    echo "The file is removed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_dependencies'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing {0} dependencies ..."'.format(xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    cd {0}/{1}'.format(xlib.get_cluster_app_dir(), xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    ./transrate --install-deps ref'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error transrate $RC; fi'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    echo "The directory is renamed."'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} setup"'.format(xlib.get_project_name(), xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} setup in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_transrate_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} setup"'.format(xlib.get_project_name(), xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} setup in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_transrate_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('remove_transrate_directory'))
            file_id.write('{0}\n'.format('decompress_transrate_setup_file'))
            file_id.write('{0}\n'.format('rename_transrate_directory'))
            file_id.write('{0}\n'.format('remove_transrate_setup_file'))
            file_id.write('{0}\n'.format('install_dependencies'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transrate_setup_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_transrate_setup_starter(current_run_dir):
    '''
    Build the starter of the Transrate setup.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Transrate setup starter
    try:
        if not os.path.exists(os.path.dirname(get_transrate_setup_starter())):
            os.makedirs(os.path.dirname(get_transrate_setup_starter()))
        with open(get_transrate_setup_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_transrate_setup_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transrate_setup_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_transrate_setup_script():
    '''
    Get the Transrate setup path in the local computer.
    '''

    # assign the Transrate setup path
    transrate_setup_script = '{0}/{1}-setup.sh'.format(xlib.get_temp_dir(), xlib.get_transrate_name())

    # return the Transrate setup path
    return transrate_setup_script

#-------------------------------------------------------------------------------

def get_transrate_setup_starter():
    '''
    Get the Transrate setup starter path in the local computer.
    '''

    # assign the Transrate setup starter path
    transrate_setup_starter = '{0}/{1}-setup-starter.sh'.format(xlib.get_temp_dir(), xlib.get_transrate_name())

    # return the Transrate setup starter path
    return transrate_setup_starter

#-------------------------------------------------------------------------------

def create_transrate_config_file(experiment_id='exp001', reference_dataset_id='Athaliana', reference_file='GCF_000001735.3_TAIR10_genomic.fna', read_dataset_id=xlib.get_uploaded_read_dataset_name(), read_type = 'PE', file_1_list=['rnaseq-a_1.fastq'], file_2_list=['rnaseq-a_2.fastq'], assembly_dataset_id='sdnt-170101-235959', assembly_type='CONTIGS'):
    '''
    Create Transrate config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # set the assembly software
    if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
        assembly_software = xlib.get_soapdenovotrans_code()
    elif assembly_dataset_id.startswith(xlib.get_transabyss_code()):
        assembly_software = xlib.get_transabyss_code()
    elif assembly_dataset_id.startswith(xlib.get_trinity_code()):
        assembly_software = xlib.get_trinity_code()
    elif assembly_dataset_id.startswith(xlib.get_star_code()):
        assembly_software = xlib.get_star_code()
    elif assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()):
        assembly_software = xlib.get_cd_hit_est_code()
    elif assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
        assembly_software = xlib.get_transcript_filter_code()

    # create the Transrate config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_transrate_config_file())):
            os.makedirs(os.path.dirname(get_transrate_config_file()))
        with open(get_transrate_config_file(), mode='w', encoding='utf8') as file_id:
            file_id.write('{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# The reference file must be located in the cluster directory {0}/experiment_id/reference_dataset_id'.format(xlib.get_cluster_reference_dir())))
            file_id.write('{0}\n'.format('# The read files must be located in the cluster directory {0}/experiment_id/read_dataset_id'.format(xlib.get_cluster_read_dir())))
            file_id.write('{0}\n'.format('# The assembly files must be located in the cluster directory {0}/experiment_id/assembly_dataset_id'.format(xlib.get_cluster_result_dir())))
            file_id.write('{0}\n'.format('# The experiment_id, reference_dataset_id, reference_file_name, read_dataset_id and assembly_dataset_id names are fixed in the identification section.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# You can consult the parameters of Transrate and their meaning in http://hibberdlab.com/transrate/.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# WARNING: The files have to be decompressed.'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information identifies the experiment.'))
            file_id.write('{0}\n'.format('[identification]'))
            file_id.write('{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write('{0:<50} {1}\n'.format('reference_dataset_id = {0}'.format(reference_dataset_id), '# reference dataset identification or NONE'))
            file_id.write('{0:<50} {1}\n'.format('reference_file = {0}'.format(reference_file), '# reference file name or NONE'))
            file_id.write('{0:<50} {1}\n'.format('read_dataset_id = {0}'.format(read_dataset_id), '# read dataset identification'))
            file_id.write('{0:<50} {1}\n'.format('assembly_software = {0}'.format(assembly_software), '# assembly software: {0} ({1}) or {2} ({3}) or {4} ({5}) or {6} ({7}) or {8} ({9}) or {10} ({11})'.format(xlib.get_soapdenovotrans_code(), xlib.get_soapdenovotrans_name(), xlib.get_transabyss_code(), xlib.get_transabyss_name(), xlib.get_trinity_code(), xlib.get_trinity_name(), xlib.get_star_code(), xlib.get_star_name(), xlib.get_cd_hit_est_code(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_code(), xlib.get_transcript_filter_name())))
            file_id.write('{0:<50} {1}\n'.format('assembly_dataset_id = {0}'.format(assembly_dataset_id), '# assembly dataset identification'))
            file_id.write('{0:<50} {1}\n'.format('assembly_type = {0}'.format(assembly_type), '# CONTIGS or SCAFFOLDS in {0}; NONE in {1}, {2}, {3}, {4} and {5}'.format(xlib.get_soapdenovotrans_name(),  xlib.get_transabyss_name(),  xlib.get_trinity_name(),  xlib.get_star_name(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_name())))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information to set the Transrate parameters'))
            file_id.write('{0}\n'.format('[Transrate parameters]'))
            # -- file_id.write('{0:<50} {1}\n'.format('threads = 2', '# number of threads for use'))
            file_id.write('{0:<50} {1}\n'.format('loglevel = INFO', '# log level: ERROR or INFO or WARN or DEBUG]'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the global information of all libraries.'))
            file_id.write('{0}\n'.format('[library]'))
            file_id.write('{0:<50} {1}\n'.format('format = FASTQ', '# only the FASTQ format is allowed'))
            file_id.write('{0:<50} {1}\n'.format('read_type = {0}'.format(read_type), '# SE (single-end) or PE (paired-end)'))
            for i in range(len(file_1_list)):
                file_id.write('{0}\n'.format(''))
                if i == 0:
                    file_id.write('{0}\n'.format('# This section has the information of the first library.'))
                file_id.write('{0}\n'.format('[library-{0}]'.format(i + 1)))
                file_id.write('{0:<50} {1}\n'.format('read_file_1 = {0}'.format(os.path.basename(file_1_list[i])), '# name of the read file in SE read type or the + strand read file in PE case'))
                if read_type == 'SE':
                    file_id.write('{0:<50} {1}\n'.format('read_file_2 = NONE', '# name of the - strand reads file in PE read type or NONE in SE case'))
                elif read_type == 'PE':
                    file_id.write('{0:<50} {1}\n'.format('read_file_2 = {0}'.format(os.path.basename(file_2_list[i])), '# name of the - strand reads file in PE read type or NONE in SE case'))
                if i == 0:
                    file_id.write('{0}\n'.format(''))
                    file_id.write('{0}\n'.format('# If there are more libraries, you must repeat the section library-1 with the data of each file.'))
                    file_id.write('{0}\n'.format('# The section identification must be library-n (n is an integer not repeated)'))
    except:
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_transrate_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_transrate_process(cluster_name, log, function=None):
    '''
    Run a Transrate process.
    '''

    # initialize the control variable
    OK = True

    # get the Transrate option dictionary
    transrate_option_dict = xlib.get_option_dict(get_transrate_config_file())

    # get the experiment identification
    experiment_id = transrate_option_dict['identification']['experiment_id']

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the Transrate config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(xlib.get_transrate_name()))
    (OK, error_list) = validate_transrate_config_file(strict=True)
    if OK:
        log.write('The config file is OK.\n')
    else:
        log.write('*** ERROR: The config file is not valid.\n')
        log.write('Please correct this file or recreate the config files.\n')

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

    # verify the Transrate is setup
    if OK:
        command = '[ -d {0}/{1} ] && echo RC=0 || echo RC=1'.format(xlib.get_cluster_app_dir(), xlib.get_transrate_name())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] != 'RC=0':
            log.write('*** ERROR: {0} is not set up.\n'.format(xlib.get_transrate_name()))
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_transrate_code())
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the Transrate process script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process script {0} ...\n'.format(get_transrate_process_script()))
        (OK, error_list) = build_transrate_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the Transrate process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process script {0} in the directory {1} of the master ...\n'.format(get_transrate_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_transrate_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_transrate_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Transrate process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transrate_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_transrate_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the Transrate process starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_transrate_process_starter()))
        (OK, error_list) = build_transrate_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the Transrate process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} in the directory {1} of the master ...\n'.format(get_transrate_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_transrate_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_transrate_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the Transrate process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transrate_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_transrate_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the Transrate process
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transrate_process_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_transrate_process_starter()))
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

def validate_transrate_config_file(strict):
    '''
    Validate the Transrate config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        transrate_option_dict = xlib.get_option_dict(get_transrate_config_file())
    except:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in transrate_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = transrate_option_dict.get('identification', {}).get('experiment_id', not_found)
            is_experiment_id_OK = True
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                is_experiment_id_OK = False
                OK = False

            # check section "identification" - key "reference_dataset_id"
            reference_dataset_id = transrate_option_dict.get('identification', {}).get('reference_dataset_id', not_found)
            is_reference_dataset_id_OK = True
            if reference_dataset_id == not_found:
                error_list.append('*** ERROR: the key "reference_dataset_id" is not found in the section "identification".')
                is_reference_dataset_id_OK = False
                OK = False

            # check section "identification" - key "reference_file"
            reference_file = transrate_option_dict.get('identification', {}).get('reference_file', not_found)
            is_reference_file_OK = True
            if reference_file == not_found:
                error_list.append('*** ERROR: the key "reference_file" is not found in the section "identification".')
                is_reference_file_OK = False
                OK = False
            elif reference_file.find('.gz') != -1:
                error_list.append('*** ERROR: the key "reference_file" in the section "identification" has to be a decompressed file.')
                is_reference_file_OK = False
                OK = False

            # check section "identification" - key "read_dataset_id"
            read_dataset_id = transrate_option_dict.get('identification', {}).get('read_dataset_id', not_found)
            is_read_dataset_id_OK = True
            if read_dataset_id == not_found:
                error_list.append('*** ERROR: the key "read_dataset_id" is not found in the section "identification".')
                is_read_dataset_id_OK = False
                OK = False

            # check section "identification" - key "assembly_software"
            assembly_software = transrate_option_dict.get('identification', {}).get('assembly_software', not_found)
            is_assembly_software_OK = True
            if assembly_software == not_found:
                error_list.append('*** ERROR: the key "assembly_software" is not found in the section "identification".')
                is_assembly_software_OK = False
                OK = False
            elif assembly_software not in [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]:
                error_list.append('*** ERROR: the key "assembly_software" value in the section "identification" must be {0} or {1} or {2} or {3} or {4} OR {5}.'.format(xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()))
                is_assembly_software_OK = False
                OK = False

            # check section "identification" - key "assembly_dataset_id"
            assembly_dataset_id = transrate_option_dict.get('identification', {}).get('assembly_dataset_id', not_found)
            is_assembly_dataset_id_OK = True
            if assembly_dataset_id == not_found:
                error_list.append('*** ERROR: the key "assembly_dataset_id" is not found in the section "identification".')
                is_assembly_dataset_id_OK = False
                OK = False
            elif not assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()) and not assembly_dataset_id.startswith(xlib.get_transabyss_code()) and not assembly_dataset_id.startswith(xlib.get_trinity_code()) and not assembly_dataset_id.startswith(xlib.get_star_code()) and not assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) and not assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
                error_list.append('*** ERROR: the key "assembly_dataset_id" value is not a {0} nor {1} nor {2} nor {3} nor {4} nor {5} assembly.'.format(xlib.get_soapdenovotrans_name(), xlib.get_transabyss_name(), xlib.get_trinity_name(), xlib.get_star_name(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_code()))
                is_assembly_dataset_id_OK = False
                OK = False

            # check section "identification" - key "assembly_type"
            assembly_type = transrate_option_dict.get('identification', {}).get('assembly_type', not_found)
            is_assembly_type_id_OK = True
            if assembly_type == not_found:
                error_list.append('*** ERROR: the key "assembly_type" is not found in the section "identification".')
                is_assembly_type_id_OK = False
                OK = False
            elif assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
                if assembly_type.upper() not in ['CONTIGS', 'SCAFFOLDS']:
                    error_list.append('*** ERROR: the key "assembly_type" must be "CONTIGS" or "SCAFFOLDS" when {0} is the assembly software.'.format(xlib.get_soapdenovotrans_name()))
                    is_assembly_type_id_OK = False
                    OK = False
            elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
                if assembly_type.upper() != 'NONE':
                    error_list.append('*** ERROR: the key "assembly_type" must be "NONE" when {0} or {1} or {2} or {3} or {4} is the assembly software.'.format(xlib.get_transabyss_name(), xlib.get_trinity_name(), xlib.get_star_name(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_name()))
                    is_assembly_type_id_OK = False
                    OK = False

        # check section "Transrate parameters"
        if 'Transrate parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Transrate parameters" is not found.')
            OK = False
        else:

            # check section "Transrate parameters" - key "threads"
            # -- threads = transrate_option_dict.get('Transrate parameters', {}).get('threads', not_found)
            # -- is_threads_OK = True
            # -- if threads == not_found:
            # --     error_list.append('*** ERROR: the key "threads" is not found in the section "Transrate parameters".')
            # --     is_threads_OK = False
            # --     OK = False
            # -- else:
            # --     try:
            # --         if int(threads) < 1:
            # --             error_list.append('*** ERROR: the key "threads" in the section "Transrate parameters" must be an integer value greater or equal to 1.')
            # --             is_threads_OK = False
            # --             OK = False
            # --     except:
            # --         error_list.append('*** ERROR: the key "threads" in the section "Transrate parameters" must be an integer value greater or equal to 1.')
            # --         is_threads_OK = False
            # --         OK = False

            # check section "Transrate parameters" - key "loglevel"
            loglevel = transrate_option_dict.get('Transrate parameters', {}).get('loglevel', not_found).upper()
            is_loglevel_OK = True
            if loglevel == not_found:
                error_list.append('*** ERROR: the key "loglevel" is not found in the section "Transrate parameters".')
                is_loglevel_OK = False
                OK = False
            elif loglevel not in ['ERROR', 'INFO', 'WARN', 'DEBUG']:
                error_list.append('*** ERROR: the key "loglevel" value in the section "Transrate parameters" must be ERROR or INFO or WARN or DEBUG.')
                is_loglevel_OK = False
                OK = False

        # check section "library"
        if 'library' not in sections_list:
            error_list.append('*** ERROR: the section "library" is not found.')
            OK = False
        else:

            # check section "library" - key "format"
            format = transrate_option_dict.get('library', {}).get('format', not_found).upper()
            is_format_OK = True
            if format == not_found:
                error_list.append('*** ERROR: the key "format" is not found in the section "library".')
                is_format_OK = False
                OK = False
            elif format not in ['FASTQ']:
                error_list.append('*** ERROR: the key "format" value in the section "library" must be FASTQ.')
                is_format_OK = False
                OK = False

            # check section "library" - key "read_type"
            read_type = transrate_option_dict.get('library', {}).get('read_type', not_found).upper()
            is_read_type_OK = True
            if read_type == not_found:
                error_list.append('*** ERROR: the key "read_type" is not found in the section "library".')
                is_read_type_OK = False
                OK = False
            elif read_type not in ['PE', 'SE']:
                error_list.append('*** ERROR: the key "read_type" value in the section "library" must be SE or PE.')
                is_read_type_OK = False
                OK = False

        # check section "library-1"
        if 'library-1' not in sections_list:
            error_list.append('*** ERROR: the section "library-1" is not found.')
            OK = False

        # check all sections "library-n"
        for section in sections_list:

            if section not in ['identification', 'Transrate parameters', 'library']:

                # verify than the section identification is like library-n 
                if not re.match('^library-[0-9]+$', section):
                    error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                    OK = False

                else:

                    # check section "library-n" - key "read_file_1"
                    read_file_1 = transrate_option_dict.get(section, {}).get('read_file_1', not_found)
                    is_read_file_1_OK = True
                    if read_file_1 == not_found:
                        error_list.append('*** ERROR: the key "read_file_1" is not found in the section "{0}"'.format(section))
                        is_read_file_1_OK = False
                        OK = False
                    elif read_file_1.find('.gz') != -1:
                        error_list.append('*** ERROR: the key "read_file_1" in the section "{0}" has to be a decompressed file.'.format(section))
                        is_reference_file_OK = False
                        OK = False

                    # check section "library-n" - key "read_file_2"
                    read_file_2 = transrate_option_dict.get(section, {}).get('read_file_2', not_found)
                    is_read_file_2_OK = True
                    if read_file_2 == not_found:
                        error_list.append('*** ERROR: the key "read_file_2" is not found in the section "{0}"'.format(section))
                        is_read_file_2_OK = False
                        OK = False
                    elif read_file_2.find('.gz') != -1:
                        error_list.append('*** ERROR: the key "read_file_2" in the section "{0}" has to be a decompressed file.'.format(section))
                        is_reference_file_OK = False
                        OK = False

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_transrate_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_transrate_process_script(cluster_name, current_run_dir):
    '''
    Build the current Transrate process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the Transrate option dictionary
    transrate_option_dict = xlib.get_option_dict(get_transrate_config_file())

    # get the options
    experiment_id = transrate_option_dict['identification']['experiment_id']
    reference_dataset_id = transrate_option_dict['identification']['reference_dataset_id']
    reference_file = transrate_option_dict['identification']['reference_file']
    assembly_software = transrate_option_dict['identification']['assembly_software']
    read_dataset_id = transrate_option_dict['identification']['read_dataset_id']
    assembly_dataset_id = transrate_option_dict['identification']['assembly_dataset_id']
    assembly_type = transrate_option_dict['identification']['assembly_type']
    # -- threads = transrate_option_dict['Transrate parameters']['threads']
    loglevel = transrate_option_dict['Transrate parameters']['loglevel']
    read_type = transrate_option_dict['library']['read_type']

    # get the sections list
    sections_list = []
    for section in transrate_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build library files
    experiment_read_dataset_dir = xlib.get_cluster_experiment_read_dataset_dir(experiment_id, read_dataset_id)
    files1 = ''
    files2 = ''
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^library-[0-9]+$', section):
            read_file_1 = transrate_option_dict[section]['read_file_1']
            read_file_1 = xlib.get_cluster_read_file(experiment_id, xlib.get_uploaded_read_dataset_name(), read_file_1)
            files1 += read_file_1 + ','
            if read_type == 'PE':
                read_file_2 = transrate_option_dict[section]['read_file_2']
                read_file_2 = xlib.get_cluster_read_file(experiment_id, xlib.get_uploaded_read_dataset_name(), read_file_2)
                files2 += read_file_2 + ','
    files1 = files1[:len(files1) - 1]
    if read_type == 'PE':
        files2 = files2[:len(files2) - 1]

    # set the reference file path
    if reference_dataset_id.upper() != 'NONE':
        reference_file = xlib.get_cluster_reference_file(reference_dataset_id, reference_file)

    # set the transcriptome file path
    if assembly_software == xlib.get_soapdenovotrans_code():
        if assembly_type == 'CONTIGS':
            transcriptome_file = '{0}/{1}-{2}.contig'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id), experiment_id, assembly_dataset_id)
        elif  assembly_type == 'SCAFFOLDS':
            transcriptome_file = '{0}/{1}-{2}.scafSeq'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id), experiment_id, assembly_dataset_id)
    elif assembly_software == xlib.get_transabyss_code():
        transcriptome_file = '{0}/transabyss-final.fa'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id))
    elif assembly_software == xlib.get_trinity_code():
        transcriptome_file = '{0}/Trinity.fasta'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id))
    elif assembly_software == xlib.get_star_code():
        transcriptome_file = '{0}/Trinity-GG.fasta'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id))
    elif assembly_software == xlib.get_cd_hit_est_code():
        transcriptome_file = '{0}/clustered-transcriptome.fasta'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id))
    elif assembly_software == xlib.get_transcript_filter_code():
        transcriptome_file = '{0}/filtered-transcriptome.fasta'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id))

    # write the Transrate process script
    try:
        if not os.path.exists(os.path.dirname(get_transrate_process_script())):
            os.makedirs(os.path.dirname(get_transrate_process_script()))
        with open(get_transrate_process_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('TRANSRATE_PATH={0}/{1}'.format(xlib.get_cluster_app_dir(), xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('export PATH=$TRANSRATE_PATH:$PATH'))
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
            file_id.write('{0}\n'.format('function run_transrate_process'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        transrate \\'))
            # -- file_id.write('{0}\n'.format('            --threads={0} \\'.format(threads)))
            file_id.write('{0}\n'.format('            --assembly={0} \\'.format(transcriptome_file)))
            if reference_dataset_id.upper() != 'NONE':
                file_id.write('{0}\n'.format('            --reference={0} \\'.format(reference_file)))
            file_id.write('{0}\n'.format('            --left={0} \\'.format(read_file_1)))
            if read_type.upper() == 'PE':
                file_id.write('{0}\n'.format('            --right={0} \\'.format(read_file_2)))
            file_id.write('{0}\n'.format('            --loglevel={0} \\'.format(loglevel.lower())))
            file_id.write('{0}\n'.format('            --output={0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error transrate $RC; fi'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_transrate_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_transrate_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_transrate_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('run_transrate_process'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transrate_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_transrate_process_starter(current_run_dir):
    '''
    Build the starter of the current Transrate process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Transrate process starter
    try:
        if not os.path.exists(os.path.dirname(get_transrate_process_starter())):
            os.makedirs(os.path.dirname(get_transrate_process_starter()))
        with open(get_transrate_process_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_transrate_process_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transrate_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_transrate_config_file():
    '''
    Get the Transrate config file path.
    '''

    # assign the Transrate config file path
    transrate_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_transrate_code())

    # return the Transrate config file path
    return transrate_config_file

#-------------------------------------------------------------------------------

def get_transrate_process_script():
    '''
    Get the Transrate process script path in the local computer.
    '''

    # assign the Transrate script path
    transrate_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_transrate_code())

    # return the Transrate script path
    return transrate_process_script

#-------------------------------------------------------------------------------

def get_transrate_process_starter():
    '''
    Get the Transrate process starter path in the local computer.
    '''

    # assign the Transrate process starter path
    transrate_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_transrate_code())

    # return the Transrate starter path
    return transrate_process_starter

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the Transrate process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
