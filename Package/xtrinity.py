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
This file contains functions related to the Trinity process used in both
console mode and gui mode.
'''

#-------------------------------------------------------------------------------

import os
import re
import subprocess
import sys

import xbioinfoapp
import xcluster
import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def create_trinity_config_file(experiment_id='exp001', read_dataset_id=xlib.get_uploaded_read_dataset_name(), read_type = 'PE', file_1_list=['rnaseq-a_1.fastq'], file_2_list=['rnaseq-a_2.fastq']):
    '''
    Create Trinity config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # create the Trinity config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_trinity_config_file())):
            os.makedirs(os.path.dirname(get_trinity_config_file()))
        with open(get_trinity_config_file(), mode='w', encoding='utf8') as file_id:
            file_id.write('{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# The read files must be located in the cluster directory {0}/experiment_id/read_dataset_id'.format(xlib.get_cluster_read_dir())))
            file_id.write('{0}\n'.format('# The experiment_id and read_dataset_id names are fixed in the identification section.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# You can consult the parameters of Trinity and their meaning in https://github.com/trinityrnaseq/trinityrnaseq/wiki.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# There are two formats to set an option:'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    option = value                             <- if the option supports a single value'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    option = value-1, value-2, ..., value-n    <- if the option supports a values list'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# In section "Trinity parameters", the key "other_parameters" allows you to input additional parameters in the format:'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    other_parameters = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# parameter-i is a parameter name of Trinity and value-i a valid value of parameter-i, e.g.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    other_parameters = --inchworm_cpu=8; --genome_guided_max_intron=10000'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information that identifies the experiment.'))
            file_id.write('{0}\n'.format('[identification]'))
            file_id.write('{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write('{0:<50} {1}\n'.format('read_dataset_id = {0}'.format(read_dataset_id), '# read dataset identification'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information to set the Trinity parameters'))
            file_id.write('{0}\n'.format('[Trinity parameters]'))
            file_id.write('{0:<50} {1}\n'.format('kmer = 25', '# value or values list of K-MER size (maximum: 32)'))
            file_id.write('{0:<50} {1}\n'.format('ncpu = 8', '# number of cpu for use'))
            file_id.write('{0:<50} {1}\n'.format('max_memory = 60', '# suggested maximum memory in GiB to use by Trinity where limiting can be enabled'))
            file_id.write('{0:<50} {1}\n'.format('min_kmer_cov = 1', '# minimum count for K-mers to be assembled by Inchworm'))
            file_id.write('{0:<50} {1}\n'.format('bfly_heap_space_max = 4', '# java maximum heap space setting in GiB'))
            file_id.write('{0:<50} {1}\n'.format('bfly_calculate_cpu = YES', '# calculate CPUs based on 0.8 of max_memory divided by heap space setting for Butterfly (YES or NO)'))
            file_id.write('{0:<50} {1}\n'.format('normalized_reads = NO', '# use normalized reads (YES or NO)'))
            file_id.write('{0:<50} {1}\n'.format('other_parameters = NONE', '# additional parameters to the previous ones or NONE'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the global information of all libraries.'))
            file_id.write('{0}\n'.format('[library]'))
            file_id.write('{0:<50} {1}\n'.format('format = FASTQ', '# FASTQ or FASTA'))
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
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_trinity_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_trinity_process(cluster_name, log, function=None):
    '''
    Run an experiment corresponding to the options in Trinity config file.
    '''

    # initialize the control variable
    OK = True

    # get the Trinity option dictionary
    trinity_option_dict = xlib.get_option_dict(get_trinity_config_file())

    # get the experiment identification
    experiment_id = trinity_option_dict['identification']['experiment_id']

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the Trinity config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(xlib.get_trinity_name()))
    (OK, error_list) = validate_trinity_config_file(strict=True)
    if OK:
        log.write('The config file is OK.\n')
    else:
        log.write('*** ERROR: The Trinity config file is not valid.\n')
        log.write('Please, correct this file or recreate it.\n')

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

    # verify Trinity is set up
    if OK:
        (OK, error_list, is_setup) = xbioinfoapp.is_setup_bioconda_package(xlib.get_trinity_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** ERROR: {0} is not setup.\n'.format(xlib.get_trinity_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} setup could not be performed.\n'.format(xlib.get_trinity_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # for each kmer value, build the process, copy it the cluster and run it
    if OK:

        # get the kmer list
        kmer = trinity_option_dict['Trinity parameters']['kmer']
        kmer_list = xlib.split_literal_to_integer_list(kmer)
        
        # for each kmer value, do the tasks
        i = 1
        for kmer_value in kmer_list:

            # determine the run directory in the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Determining the run directory for kmer {0} in the cluster ...\n'.format(kmer_value))
            if i > 1:
                current_run_dir = '{0}-{1}'.format(xlib.get_cluster_current_run_dir(experiment_id, xlib.get_trinity_code()), i)
            else:
                current_run_dir = '{0}'.format(xlib.get_cluster_current_run_dir(experiment_id, xlib.get_trinity_code()))
            command = 'mkdir --parents {0}'.format(current_run_dir)
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                log.write('The directory path is {0}.\n'.format(current_run_dir))
            else:
                log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))
            i += 1

            # build the Trinity process script
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Building the process script {0} ...\n'.format(get_trinity_process_script()))
            (OK, error_list) = build_trinity_process_script(cluster_name, current_run_dir, kmer_value)
            if OK:
                log.write('The file is built.\n')
            if not OK:
                log.write('*** ERROR: The file could not be built.\n')
                break

            # upload the process script to the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(get_trinity_process_script(), current_run_dir))
            cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_trinity_process_script()))
            (OK, error_list) = xssh.put_file(sftp_client, get_trinity_process_script(), cluster_path)
            if OK:
                log.write('The file id uploaded.\n')
            else:
                for error in error_list:
                    log.write('{0}\n'.format(error))
                break

            # set run permision to the process script in the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_trinity_process_script())))
            command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_trinity_process_script()))
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                log.write('The run permision is set on.\n')
            else:
                log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

            # build the process starter
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Building the process starter {0} ...\n'.format(get_trinity_process_starter()))
            (OK, error_list) = build_trinity_process_starter(current_run_dir)
            if OK:
                log.write('The file is built.\n')
            if not OK:
                log.write('***ERROR: The file could not be built.\n')
                break

            # upload the process starter to the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(get_trinity_process_starter(), current_run_dir))
            cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_trinity_process_starter()))
            (OK, error_list) = xssh.put_file(sftp_client, get_trinity_process_starter(), cluster_path)
            if OK:
                log.write('The file is uploaded.\n')
            else:
                for error in error_list:
                    log.write('{0}\n'.format(error))
                break

            # set run permision to the process starter in the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_trinity_process_starter())))
            command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_trinity_process_starter()))
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                log.write('The run permision is set on.\n')
            else:
                log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

            # submit the process
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_trinity_process_starter())))
            sge_env = xcluster.get_sge_env()
            command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_trinity_process_starter()))
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

def validate_trinity_config_file(strict):
    '''
    Validate the Trinity configu file verifying the all the options have right values.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        trinity_option_dict = xlib.get_option_dict(get_trinity_config_file())
    except:
        error_list.append('*** ERROR: The options dictionary could not be built from the config file')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in trinity_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = trinity_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "read_dataset_id"
            run_id = trinity_option_dict.get('identification', {}).get('read_dataset_id', not_found)
            if run_id == not_found:
                error_list.append('*** ERROR: the key "read_dataset_id" is not found in the section "identification".')
                OK = False

        # check section "Trinity parameters"
        if 'Trinity parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Trinity parameters" is not found.')
            OK = False
        else:

            # check section "Trinity parameters" - key "kmer"
            kmer = trinity_option_dict.get('Trinity parameters', {}).get('kmer', not_found)
            if kmer == not_found:
                error_list.append('*** ERROR: the key "kmer" is not found in the section Trinity parameters".')
                OK = False
            else:
                kmer_list = xlib.split_literal_to_integer_list(kmer)
                if kmer_list == []:
                    error_list.append('*** ERROR: the key "kmer" in the section "Trinity parameters" must be an integer value or an integer values lower or equal than 32.')
                    OK = False
                else:
                    for kmer_item in kmer_list:
                        if int(kmer_item) < 0 or int(kmer_item) > 32:
                            error_list.append('*** ERROR: the key "kmer" in the section "Trinity parameters" must be an integer value or an integer values lower or equal than 32.')
                            OK = False
                            break

            # check section "Trinity parameters" - key "ncpu"
            ncpu = trinity_option_dict.get('Trinity parameters', {}).get('ncpu', not_found)
            if ncpu == not_found:
                error_list.append('*** ERROR: the key "ncpu" is not found in the section "Trinity parameters".')
                OK = False
            else:
                try:
                    if int(ncpu) < 1:
                        error_list.append('*** ERROR: the key "ncpu" in the section "Trinity parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "ncpu" in the section "Trinity parameters" must be an integer value greater or equal to 1.')
                    OK = False

            # check section "Trinity parameters" - key "max_memory"
            max_memory = trinity_option_dict.get('Trinity parameters', {}).get('max_memory', not_found)
            if max_memory == not_found:
                error_list.append('*** ERROR: the key "max_memory" is not found in the section "Trinity parameters".')
                OK = False
            else:
                try:
                    if int(max_memory) < 1:
                        error_list.append('*** ERROR: the key "max_memory" in the section "Trinity parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "max_memory" in the section "Trinity parameters" must be an integer value greater or equal to 1.')
                    OK = False

            # check section "Trinity parameters" - key "min_kmer_cov"
            min_kmer_cov = trinity_option_dict.get('Trinity parameters', {}).get('min_kmer_cov', not_found)
            if min_kmer_cov == not_found:
                error_list.append('*** ERROR: the key "min_kmer_cov" is not found in the section "Trinity parameters".')
                OK = False
            else:
                try:
                    if int(min_kmer_cov) < 1:
                        error_list.append('*** ERROR: the key "min_kmer_cov" in the section "Trinity parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "min_kmer_cov" in the section "Trinity parameters" must be an integer value greater or equal to 1.')
                    OK = False

            # check section "Trinity parameters" - key "bfly_heap_space_max"
            bfly_heap_space_max = trinity_option_dict.get('Trinity parameters', {}).get('bfly_heap_space_max', not_found)
            if bfly_heap_space_max == not_found:
                error_list.append('*** ERROR: the key "bfly_heap_space_max" is not found in the section "Trinity parameters".')
                OK = False
            else:
                try:
                    if int(bfly_heap_space_max) < 1:
                        error_list.append('*** ERROR: the key "bfly_heap_space_max" in the section "Trinity parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "bfly_heap_space_max" in the section "Trinity parameters" must be an integer value greater or equal to 1.')
                    OK = False

            # check section "Trinity parameters" - key "bfly_calculate_cpu"
            bfly_calculate_cpu = trinity_option_dict.get('Trinity parameters', {}).get('bfly_calculate_cpu', not_found).upper()
            if bfly_calculate_cpu == not_found:
                error_list.append('*** ERROR: the key "bfly_calculate_cpu" is not found in the section "Trinity parameters".')
                OK = False
            elif bfly_calculate_cpu not in ['YES', 'NO']:
                error_list.append('*** ERROR: the key "bfly_calculate_cpu" value in the section "Trinity parameters" must be YES or NO.')
                OK = False

            # check section "Trinity parameters" - key "normalized_reads"
            normalized_reads = trinity_option_dict.get('Trinity parameters', {}).get('normalized_reads', not_found).upper()
            if normalized_reads == not_found:
                error_list.append('*** ERROR: the key "normalized_reads" is not found in the section "Trinity parameters".')
                OK = False
            elif normalized_reads not in ['YES', 'NO']:
                error_list.append('*** ERROR: the key "normalized_reads" value in the section "Trinity parameters" must be YES or NO.')
                OK = False

            # check section "Trinity parameters" - key "other_parameters"
            not_allowed_parameters_list = ['seqType', 'left', 'right', 'single', 'KMER_SIZE', 'CPU', 'max_memory', 'bflyHeapSpaceMax', 'bflyCalculateCPU', 'no_normalize_reads', 'output']
            other_parameters = trinity_option_dict.get('Trinity parameters', {}).get('other_parameters', not_found)
            if other_parameters == not_found:
                error_list.append('*** ERROR: the key "other_parameters" is not found in the section "Trinity parameters".')
                OK = False
            else:
                if other_parameters.upper() != 'NONE':
                    parameter_list = [x.strip() for x in other_parameters.split(';')]
                    for parameter in parameter_list:
                        try:
                            if parameter.find('=') > 0:
                                pattern = r'^--(.+)=(.+)$'
                                mo = re.search(pattern, parameter)
                                parameter_name = mo.group(1).strip()
                                parameter_value = mo.group(2).strip()
                            else:
                                pattern = r'^--(.+)$'
                                mo = re.search(pattern, parameter)
                                parameter_name = mo.group(1).strip()
                        except:
                            error_list.append('*** ERROR: the value of the key "other_parameters" in the section "Trinity parameters" must be NONE or a valid parameter list.')
                            OK = False
                            break
                        if parameter_name in not_allowed_parameters_list:
                            error_list.append('*** ERROR: the parameter {0} is not allowed in the key "other_parameters" of the section "Trinity parameters" because it is controled by {1}.'.format(parameter_name, xlib.get_project_name()))
                            OK = False

        # check section "library"
        if 'library' not in sections_list:
            error_list.append('*** ERROR: the section "library" is not found.')
            OK = False
        else:

            # check section "library" - key "format"
            format = trinity_option_dict.get('library', {}).get('format', not_found).upper()
            if format == not_found:
                error_list.append('*** ERROR: the key "format" is not found in the section "library".')
                OK = False
            elif format not in ['FASTA', 'FASTQ']:
                error_list.append('*** ERROR: the key "format" value in the section "library" must be FASTA or FASTQ.')
                OK = False

            # check section "library" - key "read_type"
            read_type = trinity_option_dict.get('library', {}).get('read_type', not_found).upper()
            if read_type == not_found:
                error_list.append('*** ERROR: the key "read_type" is not found in the section "library".')
                OK = False
            elif read_type not in ['PE', 'SE']:
                error_list.append('*** ERROR: the key "read_type" value in the section "library" must be SE or PE.')
                OK = False

        # check section "library-1"
        if 'library-1' not in sections_list:
            error_list.append('*** ERROR: the section "library-1" is not found.')
            OK = False

        # check all sections "library-n"
        for section in sections_list:

            if section not in ['identification', 'Trinity parameters', 'library']:

                # verify than the section identification is like library-n 
                if not re.match('^library-[0-9]+$', section):
                    error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                    OK = False

                else:

                    # check section "library-n" - key "read_file_1"
                    read_file_1 = trinity_option_dict.get(section, {}).get('read_file_1', not_found)
                    if read_file_1 == not_found:
                        error_list.append('*** ERROR: the key "read_file_1" is not found in the section "{0}"'.format(section))
                        OK = False

                    # check section "library-n" - key "read_file_2"
                    read_file_2 = trinity_option_dict.get(section, {}).get('read_file_2', not_found)
                    if read_file_2 == not_found:
                        error_list.append('*** ERROR: the key "read_file_2" is not found in the section "{0}"'.format(section))
                        OK = False

    # warn that the Trinity config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_trinity_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_trinity_process_script(cluster_name, current_run_dir, kmer_value):
    '''
    Build the current Trinity process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the option dictionary
    trinity_option_dict = xlib.get_option_dict(get_trinity_config_file())

    # get the options
    experiment_id = trinity_option_dict['identification']['experiment_id']
    read_dataset_id = trinity_option_dict['identification']['read_dataset_id']
    ncpu = trinity_option_dict['Trinity parameters']['ncpu']
    max_memory = trinity_option_dict['Trinity parameters']['max_memory']
    bfly_heap_space_max = trinity_option_dict['Trinity parameters']['bfly_heap_space_max']
    bfly_calculate_cpu = trinity_option_dict['Trinity parameters']['bfly_calculate_cpu']
    normalized_reads = trinity_option_dict['Trinity parameters']['normalized_reads']
    other_parameters = trinity_option_dict['Trinity parameters']['other_parameters']
    format = 'fq' if trinity_option_dict['library']['format'].upper() == 'FASTQ' else 'fa'
    read_type = trinity_option_dict['library']['read_type']

    # get the sections list
    sections_list = []
    for section in trinity_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build library files
    files1 = ''
    files2 = ''
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^library-[0-9]+$', section):
            read_file_1 = trinity_option_dict[section]['read_file_1']
            read_file_1 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_1)
            files1 += read_file_1 + ','
            if read_type.upper() == 'PE':
                read_file_2 = trinity_option_dict[section]['read_file_2']
                read_file_2 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_2)
                files2 += read_file_2 + ','
    files1 = files1[:len(files1) - 1]
    if read_type.upper() == 'PE':
        files2 = files2[:len(files2) - 1]

    # write the Trinity process script
    try:
        if not os.path.exists(os.path.dirname(get_trinity_process_script())):
            os.makedirs(os.path.dirname(get_trinity_process_script()))
        with open(get_trinity_process_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('TRINITY_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_trinity_bioconda_code())))
            file_id.write('{0}\n'.format('PATH=$TRINITY_PATH:$PATH'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('source activate {0}'.format(xlib.get_trinity_bioconda_code())))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function run_trinity_process'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    Trinity --version'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        Trinity \\'))
            file_id.write('{0}\n'.format('            --seqType {0} \\'.format(format)))
            if read_type.upper() == 'PE':
                file_id.write('{0}\n'.format('            --left {0} \\'.format(files1)))
                file_id.write('{0}\n'.format('            --right {0} \\'.format(files2)))
            else:
                file_id.write('{0}\n'.format('            --single {0} \\'.format(files1)))
            file_id.write('{0}\n'.format('            --KMER_SIZE {0} \\'.format(kmer_value)))
            file_id.write('{0}\n'.format('            --CPU {0} \\'.format(ncpu)))
            file_id.write('{0}\n'.format('            --max_memory {0}G \\'.format(max_memory)))
            file_id.write('{0}\n'.format('            --bflyHeapSpaceMax {0}G \\'.format(bfly_heap_space_max)))
            if bfly_calculate_cpu.upper() == 'YES':
                file_id.write('{0}\n'.format('            --bflyCalculateCPU \\'))
            if normalized_reads.upper() == 'NO':
                file_id.write('{0}\n'.format('            --no_normalize_reads \\'))
            if other_parameters.upper() == 'NONE':
                file_id.write('{0}\n'.format('            --output {0}'.format(current_run_dir)))
            else:
                file_id.write('{0}\n'.format('            --output {0} \\'.format(current_run_dir)))
                parameter_list = [x.strip() for x in other_parameters.split(';')]
                for i in range(len(parameter_list)):
                    if parameter_list[i].find('=') > 0:
                        pattern = r'^--(.+)=(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        parameter_value = mo.group(2).strip()
                        if i < len(parameter_list) - 1:
                            file_id.write('{0}\n'.format('            --{0} {1} \\'.format(parameter_name, parameter_value)))
                        else:
                            file_id.write('{0}\n'.format('            --{0} {1}'.format(parameter_name, parameter_value)))
                    else:
                        pattern = r'^--(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        if i < len(parameter_list):
                            file_id.write('{0}\n'.format('            --{0} \\'.format(parameter_name)))
                        else:
                            file_id.write('{0}\n'.format('            --{0}'.format(parameter_name)))
                    i += 1
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error Trinity $RC; fi'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_trinity_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_trinity_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_trinity_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_trinity_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('run_trinity_process'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_trinity_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_trinity_process_starter(current_run_dir):
    '''
    Build the starter of the current Trinity process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Trinity process starter
    try:
        if not os.path.exists(os.path.dirname(get_trinity_process_starter())):
            os.makedirs(os.path.dirname(get_trinity_process_starter()))
        with open(get_trinity_process_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_trinity_process_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_trinity_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def determine_trinity_cluster():
    '''
    Determine the cluster to the current Trinity experiment.
    '''

    # initialize the template and cluster names
    template_name = ''
    cluster_name = ''

    # ...

    # return the template and cluster names
    return (template_name, cluster_name)

#-------------------------------------------------------------------------------

def get_trinity_config_file():
    '''
    Get the Trinity config file path.
    '''

    # assign the Trinity config file path
    trinity_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_trinity_code())

    # return the Trinity config file path
    return trinity_config_file

#-------------------------------------------------------------------------------

def get_trinity_process_script():
    '''
    Get the Trinity process script path in the local computer.
    '''

    # assign the Trinity script path
    trinity_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_trinity_code())

    # return the Trinity script path
    return trinity_process_script

#-------------------------------------------------------------------------------

def get_trinity_process_starter():
    '''
    Get the Trinity process starter path in the local computer.
    '''

    # assign the Trinity process starter path
    trinity_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_trinity_code())

    # return the Trinity starter path
    return trinity_process_starter

#-------------------------------------------------------------------------------

def create_insilico_read_normalization_config_file(experiment_id='exp001', read_dataset_id=xlib.get_uploaded_read_dataset_name(), read_type = 'PE', file_1_list=['rnaseq-a_1.fastq'], file_2_list=['rnaseq-a_2.fastq']):
    '''
    Create insilico_read_normalization config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # create the Trinity config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_insilico_read_normalization_config_file())):
            os.makedirs(os.path.dirname(get_insilico_read_normalization_config_file()))
        with open(get_insilico_read_normalization_config_file(), mode='w', encoding='utf8') as file_id:
            file_id.write('{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# The read files must be located in the cluster directory {0}/experiment_id/read_dataset_id'.format(xlib.get_cluster_read_dir())))
            file_id.write('{0}\n'.format('# The experiment_id and read_dataset_id names are fixed in the identification section.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# You can consult the parameters of insilico_read_normalization (Trinity package) and their meaning in https://github.com/trinityrnaseq/trinityrnaseq/wiki.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# In section "insilico_read_normalization parameters", the key "other_parameters" allows you to input additional parameters in the format:'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    other_parameters = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# parameter-i is a parameter name of insilico_read_normalization and value-i a valid value of parameter-i, e.g.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    other_parameters = --pairs_together; --PARALLEL_STATS'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information that identifies the experiment.'))
            file_id.write('{0}\n'.format('[identification]'))
            file_id.write('{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write('{0:<50} {1}\n'.format('read_dataset_id = {0}'.format(read_dataset_id), '# read dataset identification'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information to set the insilico_read_normalization parameters'))
            file_id.write('{0}\n'.format('[insilico_read_normalization parameters]'))
            file_id.write('{0:<50} {1}\n'.format('kmer = 25', '# K-MER size'))
            file_id.write('{0:<50} {1}\n'.format('ncpu = 8', '# number of threads to use'))
            file_id.write('{0:<50} {1}\n'.format('jm = 10', '# maximum memory in GiB to use for k-mer counting by jellyfish'))
            file_id.write('{0:<50} {1}\n'.format('max_cov = 30', '# targeted maximum coverage for reads'))
            file_id.write('{0:<50} {1}\n'.format('cleanup = NO', '# leave intermediate files (YES or NO)'))
            file_id.write('{0:<50} {1}\n'.format('other_parameters = NONE', '# additional parameters to the previous ones or NONE'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the global information of all libraries.'))
            file_id.write('{0}\n'.format('[library]'))
            file_id.write('{0:<50} {1}\n'.format('format = FASTQ', '# FASTQ or FASTA'))
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
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_insilico_read_normalization_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_insilico_read_normalization_process(cluster_name, log, function=None):
    '''
    Run an experiment corresponding to the options in insilico_read_normalization config file.
    '''

    # initialize the control variable
    OK = True

    # get the insilico_read_normalization option dictionary
    insilico_read_normalization_option_dict = xlib.get_option_dict(get_insilico_read_normalization_config_file())

    # get the experiment identification
    experiment_id = insilico_read_normalization_option_dict['identification']['experiment_id']

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the insilico_read_normalization config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(xlib.get_insilico_read_normalization_name()))
    (OK, error_list) = validate_insilico_read_normalization_config_file(strict=True)
    if OK:
        log.write('The config file is OK.\n')
    else:
        log.write('*** ERROR: The config file is not valid.\n')
        log.write('Please, correct this file or recreate it.\n')

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

    # verify Trinity is set up
    if OK:
        (OK, error_list, is_setup) = xbioinfoapp.is_setup_bioconda_package(xlib.get_trinity_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** ERROR: {0} is not setup.\n'.format(xlib.get_trinity_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} setup could not be performed.\n'.format(xlib.get_trinity_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = '{0}'.format(xlib.get_cluster_current_run_dir(experiment_id, xlib.get_insilico_read_normalization_code()))
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the insilico_read_normalization process script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process script {0} ...\n'.format(get_insilico_read_normalization_process_script()))
        (OK, error_list) = build_insilico_read_normalization_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the insilico_read_normalization process script to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(get_insilico_read_normalization_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_insilico_read_normalization_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_insilico_read_normalization_process_script(), cluster_path)
        if OK:
            log.write('The file id uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the insilico_read_normalization process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_insilico_read_normalization_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_insilico_read_normalization_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set on.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the insilico_read_normalization process starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_insilico_read_normalization_process_starter()))
        (OK, error_list) = build_insilico_read_normalization_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the insilico_read_normalization process starter to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(get_insilico_read_normalization_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_insilico_read_normalization_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_insilico_read_normalization_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the insilico_read_normalization process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_insilico_read_normalization_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_insilico_read_normalization_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set on.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the insilico_read_normalization process
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_insilico_read_normalization_process_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_insilico_read_normalization_process_starter()))
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

def validate_insilico_read_normalization_config_file(strict):
    '''
    Validate the insilico_read_normalization configu file verifying the all the options have right values.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        insilico_read_normalization_option_dict = xlib.get_option_dict(get_insilico_read_normalization_config_file())
    except:
        error_list.append('*** ERROR: The options dictionary could not be built from the config file')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in insilico_read_normalization_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = insilico_read_normalization_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "read_dataset_id"
            run_id = insilico_read_normalization_option_dict.get('identification', {}).get('read_dataset_id', not_found)
            if run_id == not_found:
                error_list.append('*** ERROR: the key "read_dataset_id" is not found in the section "identification".')
                OK = False

        # check section "insilico_read_normalization parameters"
        if 'insilico_read_normalization parameters' not in sections_list:
            error_list.append('*** ERROR: the section "insilico_read_normalization parameters" is not found.')
            OK = False
        else:

            # check section "insilico_read_normalization parameters" - key "kmer"
            kmer = insilico_read_normalization_option_dict.get('insilico_read_normalization parameters', {}).get('kmer', not_found)
            if kmer == not_found:
                error_list.append('*** ERROR: the key "kmer" is not found in the section "insilico_read_normalization parameters".')
                OK = False
            else:
                try:
                    if int(kmer) < 1:
                        error_list.append('*** ERROR: the key "kmer" in the section "insilico_read_normalization parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "kmer" in the section "insilico_read_normalization parameters" must be an integer value greater or equal to 1.')
                    OK = False

            # check section "insilico_read_normalization parameters" - key "ncpu"
            ncpu = insilico_read_normalization_option_dict.get('insilico_read_normalization parameters', {}).get('ncpu', not_found)
            if ncpu == not_found:
                error_list.append('*** ERROR: the key "ncpu" is not found in the section "insilico_read_normalization parameters".')
                OK = False
            else:
                try:
                    if int(ncpu) < 1:
                        error_list.append('*** ERROR: the key "ncpu" in the section "insilico_read_normalization parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "ncpu" in the section "insilico_read_normalization parameters" must be an integer value greater or equal to 1.')
                    OK = False

            # check section "insilico_read_normalization parameters" - key "jm"
            jm = insilico_read_normalization_option_dict.get('insilico_read_normalization parameters', {}).get('jm', not_found)
            if jm == not_found:
                error_list.append('*** ERROR: the key "jm" is not found in the section "insilico_read_normalization parameters".')
                OK = False
            else:
                try:
                    if int(jm) < 1:
                        error_list.append('*** ERROR: the key "jm" in the section "insilico_read_normalization parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "jm" in the section "insilico_read_normalization parameters" must be an integer value greater or equal to 1.')
                    OK = False

            # check section "insilico_read_normalization parameters" - key "max_cov"
            max_cov = insilico_read_normalization_option_dict.get('insilico_read_normalization parameters', {}).get('max_cov', not_found)
            if max_cov == not_found:
                error_list.append('*** ERROR: the key "max_cov" is not found in the section "insilico_read_normalization parameters".')
                OK = False
            else:
                try:
                    if int(max_cov) < 1:
                        error_list.append('*** ERROR: the key "max_cov" in the section "insilico_read_normalization parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "max_cov" in the section "insilico_read_normalization parameters" must be an integer value greater or equal to 1.')
                    OK = False

            # check section "insilico_read_normalization parameters" - key "cleanup"
            cleanup = insilico_read_normalization_option_dict.get('insilico_read_normalization parameters', {}).get('cleanup', not_found).upper()
            if cleanup == not_found:
                error_list.append('*** ERROR: the key "cleanup" is not found in the section "insilico_read_normalization parameters".')
                OK = False
            elif cleanup not in ['YES', 'NO']:
                error_list.append('*** ERROR: the key "cleanup" value in the section "insilico_read_normalization parameters" must be YES or NO.')
                OK = False

            # check section "insilico_read_normalization parameters" - key "other_parameters"
            not_allowed_parameters_list = ['seqType', 'left', 'right', 'left_list', 'right_list', 'single', 'single_list', 'KMER_SIZE', 'CPU', 'JM', 'max_cov', 'no_cleanup', 'output']
            other_parameters = insilico_read_normalization_option_dict.get('insilico_read_normalization parameters', {}).get('other_parameters', not_found)
            if other_parameters == not_found:
                error_list.append('*** ERROR: the key "other_parameters" is not found in the section "insilico_read_normalization parameters".')
                OK = False
            else:
                if other_parameters.upper() != 'NONE':
                    parameter_list = [x.strip() for x in other_parameters.split(';')]
                    for parameter in parameter_list:
                        try:
                            if parameter.find('=') > 0:
                                pattern = r'^--(.+)=(.+)$'
                                mo = re.search(pattern, parameter)
                                parameter_name = mo.group(1).strip()
                                parameter_value = mo.group(2).strip()
                            else:
                                pattern = r'^--(.+)$'
                                mo = re.search(pattern, parameter)
                                parameter_name = mo.group(1).strip()
                        except:
                            error_list.append('*** ERROR: the value of the key "other_parameters" in the section "insilico_read_normalization parameters" must be NONE or a valid parameter list.')
                            OK = False
                            break
                        if parameter_name in not_allowed_parameters_list:
                            error_list.append('*** ERROR: the parameter {0} is not allowed in the key "other_parameters" of the section "insilico_read_normalization parameters" because it is controled by {1}.'.format(parameter_name, xlib.get_project_name()))
                            OK = False

        # check section "library"
        if 'library' not in sections_list:
            error_list.append('*** ERROR: the section "library" is not found.')
            OK = False
        else:

            # check section "library" - key "format"
            format = insilico_read_normalization_option_dict.get('library', {}).get('format', not_found).upper()
            if format == not_found:
                error_list.append('*** ERROR: the key "format" is not found in the section "library".')
                OK = False
            elif format not in ['FASTA', 'FASTQ']:
                error_list.append('*** ERROR: the key "format" value in the section "library" must be FASTA or FASTQ.')
                OK = False

            # check section "library" - key "read_type"
            read_type = insilico_read_normalization_option_dict.get('library', {}).get('read_type', not_found).upper()
            if read_type == not_found:
                error_list.append('*** ERROR: the key "read_type" is not found in the section "library".')
                OK = False
            elif read_type not in ['PE', 'SE']:
                error_list.append('*** ERROR: the key "read_type" value in the section "library" must be SE or PE.')
                OK = False

        # check section "library-1"
        if 'library-1' not in sections_list:
            error_list.append('*** ERROR: the section "library-1" is not found.')
            OK = False

        # check all sections "library-n"
        for section in sections_list:

            if section not in ['identification', 'insilico_read_normalization parameters', 'library']:

                # verify than the section identification is like library-n 
                if not re.match('^library-[0-9]+$', section):
                    error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                    OK = False

                else:

                    # check section "library-n" - key "read_file_1"
                    read_file_1 = insilico_read_normalization_option_dict.get(section, {}).get('read_file_1', not_found)
                    if read_file_1 == not_found:
                        error_list.append('*** ERROR: the key "read_file_1" is not found in the section "{0}"'.format(section))
                        OK = False

                    # check section "library-n" - key "read_file_2"
                    read_file_2 = insilico_read_normalization_option_dict.get(section, {}).get('read_file_2', not_found)
                    if read_file_2 == not_found:
                        error_list.append('*** ERROR: the key "read_file_2" is not found in the section "{0}"'.format(section))
                        OK = False

    # warn that the insilico_read_normalization config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_insilico_read_normalization_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_insilico_read_normalization_process_script(cluster_name, current_run_dir):
    '''
    Build the current insilico_read_normalization process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the option dictionary
    insilico_read_normalization_option_dict = xlib.get_option_dict(get_insilico_read_normalization_config_file())

    # get the options
    experiment_id = insilico_read_normalization_option_dict['identification']['experiment_id']
    read_dataset_id = insilico_read_normalization_option_dict['identification']['read_dataset_id']
    kmer = insilico_read_normalization_option_dict['insilico_read_normalization parameters']['kmer']
    ncpu = insilico_read_normalization_option_dict['insilico_read_normalization parameters']['ncpu']
    jm = insilico_read_normalization_option_dict['insilico_read_normalization parameters']['jm']
    max_cov = insilico_read_normalization_option_dict['insilico_read_normalization parameters']['max_cov']
    cleanup = insilico_read_normalization_option_dict['insilico_read_normalization parameters']['cleanup']
    other_parameters = insilico_read_normalization_option_dict['insilico_read_normalization parameters']['other_parameters']
    format = 'fq' if insilico_read_normalization_option_dict['library']['format'].upper() == 'FASTQ' else 'fa'
    read_type = insilico_read_normalization_option_dict['library']['read_type']

    # get the sections list
    sections_list = []
    for section in insilico_read_normalization_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build library files
    read_file_1_list = []
    read_file_2_list = []
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^library-[0-9]+$', section):
            read_file_1 = insilico_read_normalization_option_dict[section]['read_file_1']
            read_file_1 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_1)
            read_file_1_list.append(read_file_1)
            if read_type.upper() == 'PE':
                read_file_2 = insilico_read_normalization_option_dict[section]['read_file_2']
                read_file_2 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_2)
                read_file_2_list.append(read_file_2)

    # set the output normalised read directory
    normalised_read_dir = xlib.get_cluster_experiment_read_dataset_dir(experiment_id, os.path.basename(current_run_dir))

    # write the insilico_read_normalization process script
    try:
        if not os.path.exists(os.path.dirname(get_insilico_read_normalization_process_script())):
            os.makedirs(os.path.dirname(get_insilico_read_normalization_process_script()))
        with open(get_insilico_read_normalization_process_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('TRINITY_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_trinity_bioconda_code())))
            file_id.write('{0}\n'.format('PATH=$TRINITY_PATH:$PATH'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('source activate {0}'.format(xlib.get_trinity_bioconda_code())))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function run_insilico_read_normalization_process'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    Trinity --version'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        insilico_read_normalization.pl \\'))
            file_id.write('{0}\n'.format('            --seqType {0} \\'.format(format)))
            if read_type.upper() == 'PE':
                if len(read_file_1_list) == 1:
                    file_id.write('{0}\n'.format('            --left {0} \\'.format(read_file_1_list[0])))
                    file_id.write('{0}\n'.format('            --right {0} \\'.format(read_file_2_list[0])))
                else:
                    for i in range(len(read_file_1_list)):
                        file_id.write('{0}\n'.format('            --left_list {0} \\'.format(read_file_1_list[i])))
                        file_id.write('{0}\n'.format('            --right_list {0} \\'.format(read_file_2_list[i])))
            else:
                if len(read_file_1_list) == 1:
                    file_id.write('{0}\n'.format('            --single {0} \\'.format(read_file_1_list[0])))
                else:
                    for i in range(len(read_file_1_list)):
                        file_id.write('{0}\n'.format('            --single_list {0} \\'.format(read_file_1_list[0])))
            file_id.write('{0}\n'.format('            --KMER_SIZE {0} \\'.format(kmer)))
            file_id.write('{0}\n'.format('            --CPU {0} \\'.format(ncpu)))
            file_id.write('{0}\n'.format('            --JM {0}G \\'.format(jm)))
            file_id.write('{0}\n'.format('            --max_cov {0} \\'.format(max_cov)))
            if cleanup.upper() == 'NO':
                file_id.write('{0}\n'.format('            --no_cleanup \\'))
            if other_parameters.upper() == 'NONE':
                file_id.write('{0}\n'.format('            --output {0}'.format(normalised_read_dir)))
            else:
                file_id.write('{0}\n'.format('            --output {0} \\'.format(normalised_read_dir)))
                parameter_list = [x.strip() for x in other_parameters.split(';')]
                for i in range(len(parameter_list)):
                    if parameter_list[i].find('=') > 0:
                        pattern = r'^--(.+)=(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        parameter_value = mo.group(2).strip()
                        if i < len(parameter_list) - 1:
                            file_id.write('{0}\n'.format('            --{0} {1} \\'.format(parameter_name, parameter_value)))
                        else:
                            file_id.write('{0}\n'.format('            --{0} {1}'.format(parameter_name, parameter_value)))
                    else:
                        pattern = r'^--(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        if i < len(parameter_list):
                            file_id.write('{0}\n'.format('            --{0} \\'.format(parameter_name)))
                        else:
                            file_id.write('{0}\n'.format('            --{0}'.format(parameter_name)))
                    i += 1
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error insilico_read_normalization.pl $RC; fi'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_insilico_read_normalization_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_insilico_read_normalization_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_insilico_read_normalization_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_insilico_read_normalization_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('run_insilico_read_normalization_process'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_insilico_read_normalization_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_insilico_read_normalization_process_starter(current_run_dir):
    '''
    Build the starter of the current insilico_read_normalization process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the insilico_read_normalization process starter
    try:
        if not os.path.exists(os.path.dirname(get_insilico_read_normalization_process_starter())):
            os.makedirs(os.path.dirname(get_insilico_read_normalization_process_starter()))
        with open(get_insilico_read_normalization_process_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_insilico_read_normalization_process_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(insilico_read_normalization_process_starter))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_insilico_read_normalization_config_file():
    '''
    Get the insilico_read_normalization config file path.
    '''

    # assign the insilico_read_normalization config file path
    insilico_read_normalization_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_insilico_read_normalization_code())

    # return the insilico_read_normalization config file path
    return insilico_read_normalization_config_file

#-------------------------------------------------------------------------------

def get_insilico_read_normalization_process_script():
    '''
    Get the insilico_read_normalization process script path in the local computer.
    '''

    # assign the insilico_read_normalization script path
    insilico_read_normalization_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_insilico_read_normalization_code())

    # return the insilico_read_normalization script path
    return insilico_read_normalization_process_script

#-------------------------------------------------------------------------------

def get_insilico_read_normalization_process_starter():
    '''
    Get the insilico_read_normalization process starter path in the local computer.
    '''

    # assign the insilico_read_normalization process starter path
    insilico_read_normalization_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_insilico_read_normalization_code())

    # return the insilico_read_normalization starter path
    return insilico_read_normalization_process_starter

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the Trinity process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
