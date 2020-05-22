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
This file contains functions related to the FastQC process used in both console
mode and gui mode.
'''

#-------------------------------------------------------------------------------

import os
import re
import sys

import xbioinfoapp
import xcluster
import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def create_fastqc_config_file(experiment_id='exp001', read_dataset_id=xlib.get_uploaded_read_dataset_name(), file_list=['rnaseq-a_1.fastq', 'rnaseq-a_2.fastq']):
    '''
    Create FastQC config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # create the FastQC config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_fastqc_config_file())):
            os.makedirs(os.path.dirname(get_fastqc_config_file()))
        with open(get_fastqc_config_file(), mode='w', encoding='utf8') as file_id:
            file_id.write('{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# The files must be located in the cluster directory {0}/experiment_id/read_dataset_id'.format(xlib.get_cluster_read_dir())))
            file_id.write('{0}\n'.format('# The experiment_id and read_dataset_id names are fixed in the identification section.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# You can consult the parameters of FastQC and their meaning in http://www.bioinformatics.babraham.ac.uk/projects/fastqc/.'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information identifies the experiment.'))
            file_id.write('{0}\n'.format('[identification]'))
            file_id.write('{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write('{0:<50} {1}\n'.format('read_dataset_id = {0}'.format(read_dataset_id), '# read dataset identification'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information to set the FastQC parameters'))
            file_id.write('{0}\n'.format('[FastQC parameters]'))
            file_id.write('{0:<50} {1}\n'.format('threads = 2', '# number of threads for use'))
            for i in range(len(file_list)):
                file_id.write('{0}\n'.format(''))
                if i == 0:
                    file_id.write('{0}\n'.format('# This section has the information of the first file.'))
                file_id.write('{0}\n'.format('[file-{0}]'.format(i + 1)))
                file_id.write('{0:<50} {1}\n'.format('file_name = {0}'.format(os.path.basename(file_list[i])), '# read file name'))
                if i == 0:
                    file_id.write('{0}\n'.format(''))
                    file_id.write('{0}\n'.format('# If there are more files, you must repeat the section file-1 with the data of each file.'))
                    file_id.write('{0}\n'.format('# The section identification must be library-n (n is an integer not repeated)'))
    except:
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_fastqc_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_fastqc_process(cluster_name, log, function=None):
    '''
    Run a FastQC process.
    '''

    # initialize the control variable
    OK = True

    # get the FastQC option dictionary
    fastqc_option_dict = xlib.get_option_dict(get_fastqc_config_file())

    # get the experiment identification
    experiment_id = fastqc_option_dict['identification']['experiment_id']

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the FastQC config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(xlib.get_fastqc_name()))
    (OK, error_list) = validate_fastqc_config_file(strict=True)
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

    # verify the FastQC is set up
    if OK:
        (OK, error_list, is_setup) = xbioinfoapp.is_setup_bioconda_package(xlib.get_fastqc_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** ERROR: {0} is not setup.\n'.format(xlib.get_fastqc_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} setup could not be performed.\n'.format(xlib.get_fastqc_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_fastqc_code())
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the FastQC process script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process script {0} ...\n'.format(get_fastqc_process_script()))
        (OK, error_list) = build_fastqc_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the FastQC process script to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(get_fastqc_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_fastqc_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_fastqc_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the FastQC process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_fastqc_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_fastqc_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the FastQC process starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_fastqc_process_starter()))
        (OK, error_list) = build_fastqc_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the FastQC process starter to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(get_fastqc_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_fastqc_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_fastqc_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the FastQC process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_fastqc_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_fastqc_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the FastQC process
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_fastqc_process_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_fastqc_process_starter()))
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

def validate_fastqc_config_file(strict):
    '''
    Validate the FastQC config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        fastqc_option_dict = xlib.get_option_dict(get_fastqc_config_file())
    except:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in fastqc_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = fastqc_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "read_dataset_id"
            read_dataset_id = fastqc_option_dict.get('identification', {}).get('read_dataset_id', not_found)
            if read_dataset_id == not_found:
                error_list.append('*** ERROR: the key "read_dataset_id" is not found in the section "identification".')
                OK = False

        # check section "FastQC parameters"
        if 'FastQC parameters' not in sections_list:
            error_list.append('*** ERROR: the section "FastQC parameters" is not found.')
            OK = False
        else:

            # check section "FastQC parameters" - key "threads"
            threads = fastqc_option_dict.get('FastQC parameters', {}).get('threads', not_found)
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "FastQC parameters".')
                OK = False
            else:
                try:
                    if int(threads) < 1:
                        error_list.append('*** ERROR: the key "threads" in the section "FastQC parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "threads" in the section "FastQC parameters" must be an integer value greater or equal to 1.')
                    OK = False

        # check section "file-1"
        if 'file-1' not in sections_list:
            error_list.append('*** ERROR: the section "file-1" is not found.')
            OK = False

        # check all sections "file-n"
        for section in sections_list:

            if section not in ['identification', 'FastQC parameters']:

                # verify than the section identification is like file-n 
                if not re.match('^file-[0-9]+$', section):
                    error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                    OK = False

                else:

                    # check section "file-n" - key "file_name"
                    file_name = fastqc_option_dict.get(section, {}).get('file_name', not_found)
                    if file_name == not_found:
                        error_list.append('*** ERROR: the key "file_name" is not found in the section "{0}".'.format(section))
                        OK = False
                    elif not xlib.is_valid_path(file_name, 'linux'):
                        error_list.append('*** ERROR: the file {0} in the key "file_name" of the section "{1}" has a non valid file name.'.format(file_name, section))
                        OK = False

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_fastqc_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_fastqc_process_script(cluster_name, current_run_dir):
    '''
    Build the current FastQC process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the FastQC option dictionary
    fastqc_option_dict = xlib.get_option_dict(get_fastqc_config_file())

    # get the options
    experiment_id = fastqc_option_dict['identification']['experiment_id']
    read_dataset_id = fastqc_option_dict['identification']['read_dataset_id']
    threads = fastqc_option_dict['FastQC parameters']['threads']

    # get the sections list
    sections_list = []
    for section in fastqc_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build the file name list
    file_name_list = []
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^file-[0-9]+$', section):
            file_name = fastqc_option_dict[section]['file_name']
            file_name_list.append(file_name)

    # write the FastQC process script
    try:
        if not os.path.exists(os.path.dirname(get_fastqc_process_script())):
            os.makedirs(os.path.dirname(get_fastqc_process_script()))
        with open(get_fastqc_process_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('FASTQC_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_fastqc_bioconda_code())))
            file_id.write('{0}\n'.format('PATH=$FASTQC_PATH:$PATH'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('source activate {0}'.format(xlib.get_fastqc_bioconda_code())))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function run_fastqc_process'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    fastqc --version'))
            for file_name in file_name_list:
                file_id.write('{0}\n'.format('    echo "$SEP"'))
                file_id.write('{0}\n'.format('    /usr/bin/time \\'))
                file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
                file_id.write('{0}\n'.format('        fastqc \\'))
                file_id.write('{0}\n'.format('            {0} \\'.format(xlib.get_cluster_read_file(experiment_id, read_dataset_id, file_name))))
                file_id.write('{0}\n'.format('            --threads={0} \\'.format(threads)))
                file_id.write('{0}\n'.format('            --outdir={0}'.format(current_run_dir)))
                file_id.write('{0}\n'.format('    RC=$?'))
                file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error fastqc $RC; fi'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_fastqc_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_fastqc_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_fastqc_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_fastqc_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('run_fastqc_process'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_fastqc_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_fastqc_process_starter(current_run_dir):
    '''
    Build the starter of the current FastQC process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the FastQC process starter
    try:
        if not os.path.exists(os.path.dirname(get_fastqc_process_starter())):
            os.makedirs(os.path.dirname(get_fastqc_process_starter()))
        with open(get_fastqc_process_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_fastqc_process_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_fastqc_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_fastqc_config_file():
    '''
    Get the FastQC config file path.
    '''

    # assign the FastQC config file path
    fastqc_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_fastqc_code())

    # return the FastQC config file path
    return fastqc_config_file

#-------------------------------------------------------------------------------

def get_fastqc_process_script():
    '''
    Get the FastQC process script path in the local computer.
    '''

    # assign the FastQC script path
    fastqc_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_fastqc_code())

    # return the FastQC script path
    return fastqc_process_script

#-------------------------------------------------------------------------------

def get_fastqc_process_starter():
    '''
    Get the FastQC process starter path in the local computer.
    '''

    # assign the FastQC process starter path
    fastqc_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_fastqc_code())

    # return the FastQC starter path
    return fastqc_process_starter

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the FastQC process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
