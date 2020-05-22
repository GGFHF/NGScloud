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
This file contains functions related to the gzip process used in both console
mode and gui mode.
'''

#-------------------------------------------------------------------------------

import os
import re
import sys

import xcluster
import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def create_gzip_config_file(action='compress', dataset_type='read', experiment_id='exp001', dataset_id=xlib.get_uploaded_read_dataset_name(), file_list=['default']):
    '''
    Create gzip config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # adapt the values by default to the dataset type when the gzip config file is created
    if file_list[0] == 'default':
        if dataset_type == 'reference':
            experiment_id = None
            dataset_id = 'Athaliana'
            file_list = ['./GCF_000001735.3_TAIR10_genomic.fna']
        elif dataset_type == 'database':
            experiment_id = None
            dataset_id = 'RefSeq_Plan_Protein'
            file_list = ['./RefSeq_Plan_Protein.faa', './RefSeq_Plan_Protein.pal']
        elif dataset_type == 'read':
            file_list = ['./rnaseq-a_1.fastq', './rnaseq-a_2.fastq']
        elif dataset_type == 'result':
            dataset_id = 'fastqc-170224-134133'
            file_list = ['./fixed_reads_end1_fastqc.html', './fixed_reads_end2_fastqc.html']
        elif dataset_type in ['whole-result']:
            dataset_id = 'fastqc-170224-134133'
            file_list = [None]

    # create the gzip config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_gzip_config_file(dataset_type))):
            os.makedirs(os.path.dirname(get_gzip_config_file(dataset_type)))
        with open(get_gzip_config_file(dataset_type), mode='w', encoding='utf8') as file_id:
            file_id.write('{0}\n'.format('# This section has the information identifies the dataset.'))
            file_id.write('{0}\n'.format('[identification]'))
            value = 'NONE' if dataset_type == 'reference' else experiment_id
            comment = 'It must be always NONE' if dataset_type == 'reference' else 'experiment identification'
            file_id.write('{0:<50} {1}\n'.format('experiment_id = {0}'.format(value), '# {0}'.format(comment)))
            file_id.write('{0:<50} {1}\n'.format('dataset_type = {0}'.format(dataset_type), '# dataset type (it must be always {0})'.format(dataset_type)))
            file_id.write('{0:<50} {1}\n'.format('dataset_id = {0}'.format(dataset_id), '# dataset identification'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information to set the gzip parameters'))
            file_id.write('{0}\n'.format('[gzip parameters]'))
            file_id.write('{0:<50} {1}\n'.format('action = {0}'.format(action), '# action: compress or decompress'))
            if dataset_type in ['reference', 'database', 'read', 'result']:
                for i in range(len(file_list)):
                    file_id.write('{0}\n'.format(''))
                    if i == 0:
                        file_id.write('{0}\n'.format('# This section has the information of the first file.'))
                    file_id.write('{0}\n'.format('[file-{0}]'.format(i + 1)))
                    file_id.write('{0:<50} {1}\n'.format('dataset_subdirectory = {0}'.format(os.path.dirname(file_list[i])), '# subdirectory of {0} dataset'.format(dataset_type)))
                    file_id.write('{0:<50} {1}\n'.format('file_name = {0}'.format(os.path.basename(file_list[i])), '# {0} file name'.format(dataset_type)))
                    if i == 0:
                        file_id.write('{0}\n'.format(''))
                        file_id.write('{0}\n'.format('# If there are more files, you must repeat the section file-1 with the data of each file.'))
                        file_id.write('{0}\n'.format('# The section identification must be library-n (n is an integer not repeated)'))
    except:
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_gzip_config_file(dataset_type)))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_gzip_process(cluster_name, dataset_type, log, function=None):
    '''
    Run a gzip process.
    '''

    # initialize the control variable
    OK = True

    # get the gzip code and name
    gzip_code = xlib.get_gzip_code()
    gzip_name = xlib.get_gzip_name()

    # get the gzip option dictionary
    gzip_option_dict = xlib.get_option_dict(get_gzip_config_file(dataset_type))

    # get the experiment identification
    experiment_id = gzip_option_dict['identification']['experiment_id']

    # get the gzip process script path in the local computer
    gzip_process_script = get_gzip_process_script(dataset_type)

    # get the gzip process starter path in the local computer
    gzip_process_starter = get_gzip_process_starter(dataset_type)

    # get the aplication directory in the cluster
    cluster_app_dir = xlib.get_cluster_app_dir()

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the gzip config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(gzip_name))
    (OK, error_list) = validate_gzip_config_file(dataset_type, strict=True)
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

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        if dataset_type == 'reference':
            current_run_dir = xlib.get_cluster_current_run_dir('reference', gzip_code)
        elif dataset_type == 'database':
            current_run_dir = xlib.get_cluster_current_run_dir('database', gzip_code)
        else:
            current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, gzip_code)
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the gzip process script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process script {0} ...\n'.format(gzip_process_script))
        (OK, error_list) = build_gzip_process_script(cluster_name, dataset_type, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        else:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the gzip process script to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(gzip_process_script, current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(gzip_process_script))
        (OK, error_list) = xssh.put_file(sftp_client, gzip_process_script, cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the gzip process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(gzip_process_script)))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(gzip_process_script))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the gzip process starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(gzip_process_starter))
        (OK, error_list) = build_gzip_process_starter(dataset_type, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        else:
            log.write('***ERROR: The file could not be built.\n')

    # upload the gzip process starter to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(gzip_process_starter, current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(gzip_process_starter))
        (OK, error_list) = xssh.put_file(sftp_client, gzip_process_starter, cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the gzip process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(gzip_process_starter)))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(gzip_process_starter))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the gzip process
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(gzip_process_starter)))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(gzip_process_starter))
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

def validate_gzip_config_file(dataset_type, strict):
    '''
    Validate the gzip config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        gzip_option_dict = xlib.get_option_dict(get_gzip_config_file(dataset_type))
    except:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in gzip_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = gzip_option_dict.get('identification', {}).get('experiment_id', not_found).upper()
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False
            elif dataset_type.upper() == 'REFERENCE' and experiment_id != 'NONE':
                error_list.append('*** ERROR: the key "experiment_id" in the section "identification" must be always NONE')
                OK = False

            # check section "identification" - key "dataset_type"
            dataset_type_2 = gzip_option_dict.get('identification', {}).get('dataset_type', not_found).upper()
            if dataset_type_2 == not_found:
                error_list.append('*** ERROR: the key "dataset_type" is not found in the section "identification".')
                OK = False
            else:
                if dataset_type in ['reference', 'read']:
                    if dataset_type_2 != dataset_type.upper():
                        error_list.append('*** ERROR: the key "dataset_type" value in the section "identification" must be {0}.'.format(dataset_type))
                        OK = False
                elif dataset_type == 'result':
                    if dataset_type_2 not in ['RESULT', 'WHOLE-RESULT']:
                        error_list.append('*** ERROR: the key "dataset_type" value in the section "identification" must be result or whole-result.')
                        OK = False

            # check section "identification" - key "dataset_id"
            dataset_id = gzip_option_dict.get('identification', {}).get('dataset_id', not_found)
            if dataset_id == not_found:
                error_list.append('*** ERROR: the key "dataset_id" is not found in the section "identification".')
                OK = False

        # check section "gzip parameters"
        if 'gzip parameters' not in sections_list:
            error_list.append('*** ERROR: the section "gzip parameters" is not found.')
            OK = False
        else:

            # check section "gzip parameters" - key "action"
            action = gzip_option_dict.get('gzip parameters', {}).get('action', not_found).lower()
            if action == not_found:
                error_list.append('*** ERROR: the key "action" is not found in the section "gzip parameters".')
                OK = False
            else:
                if action not in ['compress', 'decompress']:
                    error_list.append('*** ERROR: the key "action" value in the section "gzip parameters" must be compress or decompress.')
                    OK = False

        # check section "file-1"
        if dataset_type_2 in ['reference', 'database', 'read', 'result']:
            if 'file-1' not in sections_list:
                error_list.append('*** ERROR: the section "file-1" is not found.')
                OK = False

        # check all sections "file-n"
        if dataset_type_2 in ['reference', 'database', 'read', 'result']:
            for section in sections_list:

                if section not in ['identification', 'gzip parameters']:

                    # verify than the section identification is like file-n 
                    if not re.match('^file-[0-9]+$', section):
                        error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                        OK = False

                    else:

                        # check section "file-n" - key "dataset_subdirectory"
                        dataset_subdirectory = gzip_option_dict.get(section, {}).get('dataset_subdirectory', not_found)
                        if dataset_subdirectory == not_found:
                            error_list.append('*** ERROR: the key "dataset_subdirectory" is not found in the section "{0}".'.format(section))
                            OK = False
                        elif not xlib.is_valid_path(dataset_subdirectory, 'linux'):
                            error_list.append('*** ERROR: the file {0} in the key "dataset_subdirectory" of the section "{1}" has a non valid file name.'.format(dataset_subdirectory, section))
                            OK = False

                        # check section "file-n" - key "file_name"
                        file_name = gzip_option_dict.get(section, {}).get('file_name', not_found)
                        if file_name == not_found:
                            error_list.append('*** ERROR: the key "file_name" is not found in the section "{0}".'.format(section))
                            OK = False
                        elif not xlib.is_valid_path(file_name, 'linux'):
                            error_list.append('*** ERROR: the file {0} in the key "file_name" of the section "{1}" has a non valid file name.'.format(file_name, section))
                            OK = False

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_gzip_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_gzip_process_script(cluster_name, dataset_type, current_run_dir):
    '''
    Build the current gzip process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the gzip option dictionary
    gzip_option_dict = xlib.get_option_dict(get_gzip_config_file(dataset_type))

    # get the options
    experiment_id = gzip_option_dict['identification']['experiment_id']
    dataset_type_2 = gzip_option_dict['identification']['dataset_type']
    dataset_id = gzip_option_dict['identification']['dataset_id']
    action = gzip_option_dict['gzip parameters']['action']

    # get the sections list
    sections_list = []
    for section in gzip_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build the dataset subdirectory and file name lists
    dataset_subdirectory_list = []
    file_name_list = []
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^file-[0-9]+$', section):
            dataset_subdirectory = gzip_option_dict[section]['dataset_subdirectory']
            dataset_subdirectory_list.append(dataset_subdirectory)
            file_name = gzip_option_dict[section]['file_name']
            file_name_list.append(file_name)

    # get the dataset directory
    if dataset_type_2 == 'reference':
        dataset_dir = xlib.get_cluster_reference_dataset_dir(dataset_id)
    elif dataset_type_2 == 'database':
        dataset_dir = xlib.get_cluster_database_dataset_dir(dataset_id)
    elif dataset_type_2 == 'read':
        dataset_dir = xlib.get_cluster_experiment_read_dataset_dir(experiment_id, dataset_id)
    elif dataset_type_2 == 'result':
        dataset_dir = xlib.get_cluster_experiment_result_dataset_dir(experiment_id, dataset_id)
    elif dataset_type_2 == 'whole-result':
        dataset_dir = xlib.get_cluster_experiment_result_dataset_dir(experiment_id, dataset_id)

    # write the gzip process script
    try:
        if not os.path.exists(os.path.dirname(get_gzip_process_script(dataset_type_2))):
            os.makedirs(os.path.dirname(get_gzip_process_script(dataset_type_2)))
        with open(get_gzip_process_script(dataset_type_2), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
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
            file_id.write('{0}\n'.format('function run_gzip_process'))
            file_id.write('{0}\n'.format('{'))
            if dataset_type_2 in ['reference', 'database', 'read', 'result']:
                file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
                for i in range(len(dataset_subdirectory_list)):
                    file_id.write('{0}\n'.format('    echo "$SEP"'))
                    file_id.write('{0}\n'.format('    echo "Compressing/decompressing {0}/{1}/{2} ..."'.format(dataset_dir, dataset_subdirectory_list[i], file_name_list[i])))
                    file_id.write('{0}\n'.format('    /usr/bin/time \\'))
                    file_id.write('{0}\n'.format('        --format="Elapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
                    if action == 'compress':
                        file_id.write('{0}\n'.format('        gzip {0}/{1}/{2}'.format(dataset_dir, dataset_subdirectory_list[i], file_name_list[i])))
                    elif action == 'decompress':
                        file_id.write('{0}\n'.format('        gzip --decompress {0}/{1}/{2}'.format(dataset_dir, dataset_subdirectory_list[i], file_name_list[i])))
                    file_id.write('{0}\n'.format('    RC=$?'))
                    file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error gzip $RC; fi'))
            elif dataset_type_2 == 'whole-result':
                file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
                file_id.write('{0}\n'.format('    echo "$SEP"'))
                file_id.write('{0}\n'.format('    echo "Compressing/decompressing {0} ..."'.format(dataset_dir)))
                file_id.write('{0}\n'.format('    /usr/bin/time \\'))
                file_id.write('{0}\n'.format('        --format="Elapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
                if action == 'compress':
                    file_id.write('{0}\n'.format('        tar --create --gzip --verbose --file={0}.tar.gz {0}'.format(dataset_dir)))
                elif action == 'decompress':
                    file_id.write('{0}\n'.format('        tar --extract --gzip --verbose --file={0} --directory=/'.format(dataset_dir)))
                file_id.write('{0}\n'.format('    RC=$?'))
                file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error tar $RC; fi'))
                file_id.write('{0}\n'.format('    echo "$SEP"'))
                file_id.write('{0}\n'.format('    echo "Removing {0} ..."'.format(dataset_dir)))
                file_id.write('{0}\n'.format('    /usr/bin/time \\'))
                file_id.write('{0}\n'.format('        --format="Elapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
                file_id.write('{0}\n'.format('        rm -rf {0}'.format(dataset_dir)))
                file_id.write('{0}\n'.format('    RC=$?'))
                file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error rm $RC; fi'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_gzip_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {0} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_gzip_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_gzip_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {0} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_gzip_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('run_gzip_process'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_gzip_process_script(dataset_type_2)))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_gzip_process_starter(dataset_type, current_run_dir):
    '''
    Build the starter of the current gzip process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the log file name
    log_file = xlib.get_cluster_log_file()

    # write the gzip process starter
    try:
        if not os.path.exists(os.path.dirname(get_gzip_process_starter(dataset_type))):
            os.makedirs(os.path.dirname(get_gzip_process_starter(dataset_type)))
        with open(get_gzip_process_starter(dataset_type), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_gzip_process_script(dataset_type)), log_file)))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_gzip_process_starter(dataset_type)))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_gzip_config_file(dataset_type):
    '''
    Get the gzip config file path.
    '''

    # assign the gzip config file path
    name = 'result' if dataset_type == 'whole-result' else dataset_type
    gzip_config_file = '{0}/{1}-{2}-config.txt'.format(xlib.get_config_dir(), xlib.get_gzip_code(), name)

    # return the gzip config file path
    return gzip_config_file

#-------------------------------------------------------------------------------

def get_gzip_process_script(dataset_type):
    '''
    Get the gzip process script path in the local computer.
    '''

    # assign the gzip script path
    name = 'result' if dataset_type == 'whole-result' else dataset_type
    gzip_process_script = '{0}/{1}-{2}-process.sh'.format(xlib.get_temp_dir(), xlib.get_gzip_code(), name)

    # return the gzip script path
    return gzip_process_script

#-------------------------------------------------------------------------------

def get_gzip_process_starter(dataset_type):
    '''
    Get the gzip process starter path in the local computer.
    '''

    # assign the gzip process starter path
    name = 'result' if dataset_type == 'whole-result' else dataset_type
    gzip_process_starter = '{0}/{1}-{2}-starter.sh'.format(xlib.get_temp_dir(), xlib.get_gzip_code(), name)

    # return the gzip starter path
    return gzip_process_starter

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the gzip process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
