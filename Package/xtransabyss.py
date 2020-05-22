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
This file contains functions related to the Trans-ABySS process used in both
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

def create_transabyss_config_file(experiment_id='exp001', read_dataset_id=xlib.get_uploaded_read_dataset_name(), read_type = 'PE', file_1_list=['rnaseq-a_1.fastq'], file_2_list=['rnaseq-a_2.fastq']):
    '''
    Create Trans-ABySS config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # create the Trans-ABySS config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_transabyss_config_file())):
            os.makedirs(os.path.dirname(get_transabyss_config_file()))
        with open(get_transabyss_config_file(), mode='w', encoding='utf8') as file_id:
            file_id.write('{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# The read files must be located in the cluster directory {0}/experiment_id/read_dataset_id'.format(xlib.get_cluster_read_dir())))
            file_id.write('{0}\n'.format('# The experiment_id and read_dataset_id names are fixed in the identification section.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# You can consult the parameters of Trans-ABySS and their meaning in http://www.bcgsc.ca/platform/bioinfo/software/trans-abyss.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# There are two formats to set an option:'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    option = value                             <- if the option supports a single value'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    option = value-1, value-2, ..., value-n    <- if the option supports a values list'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# In section "Trans-ABySS parameters", the key "other_parameters" allows you to input additional parameters in the format:'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    other_parameters = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# parameter-i is a parameter name of Trans-ABySS and value-i a valid value of parameter-i, e.g.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    other_parameters = --qends=4; --noref)'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information that identifies the experiment.'))
            file_id.write('{0}\n'.format('[identification]'))
            file_id.write('{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write('{0:<50} {1}\n'.format('read_dataset_id = {0}'.format(read_dataset_id), '# read dataset identification'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information to set the Trans-ABySS parameters'))
            file_id.write('{0}\n'.format('[Trans-ABySS parameters]'))
            file_id.write('{0:<50} {1}\n'.format('threads = 2', '# number of threads for use'))
            file_id.write('{0:<50} {1}\n'.format('length = 100', '# minimum output sequence length'))
            file_id.write('{0:<50} {1}\n'.format('kmer = 32', '# value or values list of k-mer size'))
            file_id.write('{0:<50} {1}\n'.format('cov = 2', '# minimum mean k-mer coverage of a unitig'))
            file_id.write('{0:<50} {1}\n'.format('eros = 2', '# minimum erosion k-mer coverage'))
            file_id.write('{0:<50} {1}\n'.format('seros = 0', '# minimum erosion k-mer coverage per strand'))
            file_id.write('{0:<50} {1}\n'.format('gsim = 2', '# maximum iterations of graph simplification'))
            file_id.write('{0:<50} {1}\n'.format('indel = 1', '# indel size tolerance'))
            file_id.write('{0:<50} {1}\n'.format('island = 0', '# minimum length of island unitigs'))
            file_id.write('{0:<50} {1}\n'.format('useblat = NO', '# use BLAT alignments to remove redundant sequences: YES or NO'))
            file_id.write('{0:<50} {1}\n'.format('pid = 0.95', '# minimum percent sequence identity of redundant sequences'))
            file_id.write('{0:<50} {1}\n'.format('walk = 0.05', '# percentage of mean k-mer coverage of seed for path-walking'))
            file_id.write('{0:<50} {1}\n'.format('cleanup = 1', '# level of clean-up of intermediate files: 0 or 1 or 2 or 3'))
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
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transabyss_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_transabyss_process(cluster_name, log, function=None):
    '''
    Run an experiment corresponding to the options in Trans-ABySS config file.
    '''

    # initialize the control variable
    OK = True

    # get the Trans-ABySS option dictionary
    transabyss_option_dict = xlib.get_option_dict(get_transabyss_config_file())

    # get the experiment identification
    experiment_id = transabyss_option_dict['identification']['experiment_id']

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the Trans-ABySS config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(xlib.get_transabyss_name()))
    (OK, error_list) = validate_transabyss_config_file(strict=True)
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

    # verify Trans-ABySS is setup
    if OK:
        (OK, error_list, is_setup) = xbioinfoapp.is_setup_bioconda_package(xlib.get_transabyss_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** ERROR: {0} is not setup.\n'.format(xlib.get_transabyss_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} setup could not be performed.\n'.format(xlib.get_transabyss_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # for each kmer value, build the process, copy it the cluster and run it
    if OK:

        # get the kmer list
        kmer = transabyss_option_dict['Trans-ABySS parameters']['kmer']
        kmer_list = xlib.split_literal_to_integer_list(kmer)
        
        # for each kmer value, do the tasks
        i = 1
        for kmer_value in kmer_list:

            # determine the run directory in the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Determining the run directory for kmer {0} in the cluster ...\n'.format(kmer_value))
            if i > 1:
                current_run_dir = '{0}-{1}'.format(xlib.get_cluster_current_run_dir(experiment_id, xlib.get_transabyss_code()), i)
            else:
                current_run_dir = '{0}'.format(xlib.get_cluster_current_run_dir(experiment_id, xlib.get_transabyss_code()))
            command = 'mkdir --parents {0}'.format(current_run_dir)
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                log.write('The directory path is {0}.\n'.format(current_run_dir))
            else:
                log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))
            i += 1

            # build the Trans-ABySS process script
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Building the process script {0} ...\n'.format(get_transabyss_process_script()))
            (OK, error_list) = build_transabyss_process_script(cluster_name, current_run_dir, kmer_value)
            if OK:
                log.write('The file is built.\n')
            if not OK:
                log.write('*** ERROR: The file could not be built.\n')
                break

            # upload the process script in the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Uploading the process script {0} in the directory {1} of the master ...\n'.format(get_transabyss_process_script(), current_run_dir))
            cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_transabyss_process_script()))
            (OK, error_list) = xssh.put_file(sftp_client, get_transabyss_process_script(), cluster_path)
            if OK:
                log.write('The file id uploaded.\n')
            else:
                for error in error_list:
                    log.write('{0}\n'.format(error))
                break

            # set run permision to the process script in the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transabyss_process_script())))
            command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_transabyss_process_script()))
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                log.write('The run permision is set on.\n')
            else:
                log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

            # build the process starter
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Building the process starter {0} ...\n'.format(get_transabyss_process_starter()))
            (OK, error_list) = build_transabyss_process_starter(current_run_dir)
            if OK:
                log.write('The file is built.\n')
            if not OK:
                log.write('***ERROR: The file could not be built.\n')
                break

            # upload the process starter in the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Uploading the process starter {0} in the directory {1} of the master ...\n'.format(get_transabyss_process_starter(), current_run_dir))
            cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_transabyss_process_starter()))
            (OK, error_list) = xssh.put_file(sftp_client, get_transabyss_process_starter(), cluster_path)
            if OK:
                log.write('The file is uploaded.\n')
            else:
                for error in error_list:
                    log.write('{0}\n'.format(error))
                break

            # set run permision to the process starter in the cluster
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transabyss_process_starter())))
            command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_transabyss_process_starter()))
            (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
            if OK:
                log.write('The run permision is set on.\n')
            else:
                log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

            # submit the process
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_transabyss_process_starter())))
            sge_env = xcluster.get_sge_env()
            command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_transabyss_process_starter()))
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

def validate_transabyss_config_file(strict):
    '''
    Validate the Trans-ABySS config file verifying the all the options have right values.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        transabyss_option_dict = xlib.get_option_dict(get_transabyss_config_file())
    except:
        error_list.append('*** ERROR: The options dictionary could not be built from the config file')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in transabyss_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = transabyss_option_dict.get('identification', {}).get('experiment_id', not_found)
            is_experiment_id_OK = True
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                is_experiment_id_OK = False
                OK = False

            # check section "identification" - key "read_dataset_id"
            read_dataset_id = transabyss_option_dict.get('identification', {}).get('read_dataset_id', not_found)
            is_read_dataset_id_OK = True
            if read_dataset_id == not_found:
                error_list.append('*** ERROR: the key "read_dataset_id" is not found in the section "identification".')
                is_read_dataset_id_OK = False
                OK = False

        # check section "Trans-ABySS parameters"
        if 'Trans-ABySS parameters' not in sections_list:
            error_list.append('*** ERROR: the section "Trans-ABySS parameters" is not found.')
            OK = False
        else:

            # check section "Trans-ABySS parameters" - key "threads"
            threads = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('threads', not_found)
            is_threads_OK = True
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "Trans-ABySS parameters".')
                is_threads_OK = False
                OK = False
            else:
                try:
                    if int(threads) < 1:
                        error_list.append('*** ERROR: the key "threads" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 1.')
                        is_threads_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "threads" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 1.')
                    is_threads_OK = False
                    OK = False

            # check section "Trans-ABySS parameters" - key "length"
            length = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('length', not_found)
            is_length_OK = True
            if length == not_found:
                error_list.append('*** ERROR: the key "length" is not found in the section "Trans-ABySS parameters".')
                is_length_OK = False
                OK = False
            else:
                try:
                    if int(length) < 1:
                        error_list.append('*** ERROR: the key "length" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 1.')
                        is_length_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "length" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 1.')
                    is_length_OK = False
                    OK = False

            # check section "Trans-ABySS parameters" - key "kmer"
            kmer = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('kmer', not_found)
            is_kmer_OK = True
            if kmer == not_found:
                error_list.append('*** ERROR: the key "kmer" is not found in the section Trans-ABySS parameters".')
                is_kmer_OK = False
                OK = False
            else:
                kmer_list = xlib.split_literal_to_integer_list(kmer)
                if kmer_list == []:
                    error_list.append('*** ERROR: the key "kmer" in the section "Trans-ABySS parameters" must be an integer value or an integer value list.')
                    is_kmer_OK = False
                    OK = False
                else:
                    for kmer_item in kmer_list:
                        if int(kmer_item) < 0:
                            error_list.append('*** ERROR: the key "kmer" in the section "Trans-ABySS parameters" must be an integer value or an integer value list.')
                            is_kmer_OK = False
                            OK = False
                            break

            # check section "Trans-ABySS parameters" - key "cov"
            cov = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('cov', not_found)
            is_cov_OK = True
            if cov == not_found:
                error_list.append('*** ERROR: the key "cov" is not found in the section "Trans-ABySS parameters".')
                is_cov_OK = False
                OK = False
            else:
                try:
                    if int(cov) < 0:
                        error_list.append('*** ERROR: the key "cov" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                        is_cov_OK = True
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "cov" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                    is_cov_OK = True
                    OK = False

            # check section "Trans-ABySS parameters" - key "eros"
            eros = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('eros', not_found)
            is_eros_OK = True
            if eros == not_found:
                error_list.append('*** ERROR: the key "eros" is not found in the section "Trans-ABySS parameters".')
                is_eros_OK = False
                OK = False
            else:
                try:
                    if int(eros) < 0:
                        error_list.append('*** ERROR: the key "eros" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                        is_eros_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "eros" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                    is_eros_OK = False
                    OK = False

            # check section "Trans-ABySS parameters" - key "seros"
            seros = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('seros', not_found)
            is_seros_OK = True
            if seros == not_found:
                error_list.append('*** ERROR: the key "seros" is not found in the section "Trans-ABySS parameters".')
                is_seros_OK = False
                OK = False
            else:
                try:
                    if int(seros) < 0:
                        error_list.append('*** ERROR: the key "seros" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                        is_seros_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "seros" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                    is_seros_OK = False
                    OK = False

            # check section "Trans-ABySS parameters" - key "gsim"
            gsim = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('gsim', not_found)
            is_gsim_OK = True
            if gsim == not_found:
                error_list.append('*** ERROR: the key "gsim" is not found in the section "Trans-ABySS parameters".')
                is_gsim_OK = False
                OK = False
            else:
                try:
                    if int(gsim) < 0:
                        error_list.append('*** ERROR: the key "gsim" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                        is_gsim_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "gsim" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                    is_gsim_OK = False
                    OK = False

            # check section "Trans-ABySS parameters" - key "indel"
            indel = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('indel', not_found)
            is_indel_OK = True
            if indel == not_found:
                error_list.append('*** ERROR: the key "indel" is not found in the section "Trans-ABySS parameters".')
                is_indel_OK = False
                OK = False
            else:
                try:
                    if int(indel) < 0:
                        error_list.append('*** ERROR: the key "indel" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                        is_indel_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "indel" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                    is_indel_OK = False
                    OK = False

            # check section "Trans-ABySS parameters" - key "island"
            island = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('island', not_found)
            is_island_OK = True
            if island == not_found:
                error_list.append('*** ERROR: the key "island" is not found in the section "Trans-ABySS parameters".')
                is_island_OK = False
                OK = False
            else:
                try:
                    if int(island) < 0:
                        error_list.append('*** ERROR: the key "island" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                        is_island_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "island" in the section "Trans-ABySS parameters" must be an integer value greater or equal to 0.')
                    is_island_OK = False
                    OK = False

            # check section "Trans-ABySS parameters" - key "useblat"
            useblat = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('useblat', not_found).upper()
            is_useblat_OK = True
            if useblat == not_found:
                error_list.append('*** ERROR: the key "useblat" is not found in the section "Trans-ABySS parameters".')
                is_useblat_OK = False
                OK = False
            elif useblat not in ['YES', 'NO']:
                error_list.append('*** ERROR: the key "useblat" value in the section "Trans-ABySS parameters" must be YES or NO.')
                is_useblat_OK = False
                OK = False

            # check section "Trans-ABySS parameters" - key "pid"
            pid = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('pid', not_found)
            is_pid_OK = True
            if pid == not_found:
                error_list.append('*** ERROR: the key "pid" is not found in the section "Trans-ABySS parameters".')
                is_pid_OK = False
                OK = False
            else:
                try:
                    if float(pid) < 0 or float(pid) > 1:
                        error_list.append('*** ERROR: the key "pid" in the section "Trans-ABySS parameters" must be a float value between 0 and 1.')
                        is_pid_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "pid" in the section "Trans-ABySS parameters" must be a float value between 0 and 1.')
                    is_pid_OK = False
                    OK = False

            # check section "Trans-ABySS parameters" - key "walk"
            walk = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('walk', not_found)
            is_walk_OK = True
            if walk == not_found:
                error_list.append('*** ERROR: the key "walk" is not found in the section "Trans-ABySS parameters".')
                is_walk_OK = False
                OK = False
            else:
                try:
                    if float(walk) < 0 or float(walk) > 1:
                        error_list.append('*** ERROR: the key "walk" in the section "Trans-ABySS parameters" must be a float value between 0 and 1.')
                        is_walk_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "walk" in the section "Trans-ABySS parameters" must be a float value between 0 and 1.')
                    is_walk_OK = False
                    OK = False

            # check section "Trans-ABySS parameters" - key "cleanup"
            cleanup = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('cleanup', not_found).upper()
            is_cleanup_OK = True
            if cleanup == not_found:
                error_list.append('*** ERROR: the key "cleanup" is not found in the section "Trans-ABySS parameters".')
                is_cleanup_OK = False
                OK = False
            elif cleanup not in ['0', '1', '2', '3']:
                error_list.append('*** ERROR: the key "cleanup" value in the section "Trans-ABySS parameters" must be 0 or 1 or 2 or 3.')
                is_cleanup_OK = False
                OK = False

            # check section "Trans-ABySS parameters" - key "other_parameters"
            not_allowed_parameters_list = ['threads', 'length', 'kmer', 'cov', 'eros', 'seros', 'gsim', 'indel', 'island', 'useblat', 'pid', 'walk', 'cleanup']
            other_parameters = transabyss_option_dict.get('Trans-ABySS parameters', {}).get('other_parameters', not_found)
            is_other_parameters_OK = True
            if other_parameters == not_found:
                error_list.append('*** ERROR: the key "other_parameters" is not found in the section "Trans-ABySS parameters".')
                is_other_parameters_OK = False
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
                            error_list.append('*** ERROR: the value of the key "other_parameters" in the section "Trans-ABySS parameters" must be NONE or a valid parameter list.')
                            is_other_parameters_OK = False
                            OK = False
                            break
                        if parameter_name in not_allowed_parameters_list:
                            error_list.append('*** ERROR: the parameter {0} is not allowed in the key "other_parameters" of the section "Trans-ABySS parameters" because it is controled by NGScloud.'.format(parameter_name))
                            is_other_parameters_OK = False
                            OK = False

        # check section "library"
        if 'library' not in sections_list:
            error_list.append('*** ERROR: the section "library" is not found.')
            OK = False
        else:

            # check section "library" - key "format"
            format = transabyss_option_dict.get('library', {}).get('format', not_found).upper()
            is_format_OK = True
            if format == not_found:
                error_list.append('*** ERROR: the key "format" is not found in the section "library".')
                is_format_OK = False
                OK = False
            elif format not in ['FASTA', 'FASTQ']:
                error_list.append('*** ERROR: the key "format" value in the section "library" must be FASTA or FASTQ.')
                is_format_OK = False
                OK = False

            # check section "library" - key "read_type"
            read_type = transabyss_option_dict.get('library', {}).get('read_type', not_found).upper()
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

            if section not in ['identification', 'Trans-ABySS parameters', 'library']:

                # verify than the section identification is like library-n 
                if not re.match('^library-[0-9]+$', section):
                    error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                    OK = False

                else:

                    # check section "library-n" - key "read_file_1"
                    read_file_1 = transabyss_option_dict.get(section, {}).get('read_file_1', not_found)
                    is_read_file_1_OK = True
                    if read_file_1 == not_found:
                        error_list.append('*** ERROR: the key "read_file_1" is not found in the section "{0}"'.format(section))
                        is_read_file_1_OK = False
                        OK = False

                    # check section "library-n" - key "read_file_2"
                    read_file_2 = transabyss_option_dict.get(section, {}).get('read_file_2', not_found)
                    is_read_file_2_OK = True
                    if read_file_2 == not_found:
                        error_list.append('*** ERROR: the key "read_file_2" is not found in the section "{0}"'.format(section))
                        is_read_file_2_OK = False
                        OK = False

    # warn that the Trans-ABySS config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_transabyss_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_transabyss_process_script(cluster_name, current_run_dir, kmer_value):
    '''
    Build the current Trans-ABySS process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the option dictionary
    transabyss_option_dict = xlib.get_option_dict(get_transabyss_config_file())

    # get the options
    experiment_id = transabyss_option_dict['identification']['experiment_id']
    read_dataset_id = transabyss_option_dict['identification']['read_dataset_id']
    threads = transabyss_option_dict['Trans-ABySS parameters']['threads']
    length = transabyss_option_dict['Trans-ABySS parameters']['length']
    cov = transabyss_option_dict['Trans-ABySS parameters']['cov']
    eros = transabyss_option_dict['Trans-ABySS parameters']['eros']
    seros = transabyss_option_dict['Trans-ABySS parameters']['seros']
    gsim = transabyss_option_dict['Trans-ABySS parameters']['gsim']
    indel = transabyss_option_dict['Trans-ABySS parameters']['indel']
    island = transabyss_option_dict['Trans-ABySS parameters']['island']
    useblat = transabyss_option_dict['Trans-ABySS parameters']['useblat']
    pid = transabyss_option_dict['Trans-ABySS parameters']['pid']
    walk = transabyss_option_dict['Trans-ABySS parameters']['walk']
    cleanup = transabyss_option_dict['Trans-ABySS parameters']['cleanup']
    other_parameters = transabyss_option_dict['Trans-ABySS parameters']['other_parameters']
    format = transabyss_option_dict['library']['format']
    read_type = transabyss_option_dict['library']['read_type']

    # get the sections list
    sections_list = []
    for section in transabyss_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build library files
    file_list = ''
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^library-[0-9]+$', section):
            read_file_1 = transabyss_option_dict[section]['read_file_1']
            read_file_1 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_1)
            file_list += read_file_1 + ' '
            if read_type.upper() == 'PE':
                read_file_2 = transabyss_option_dict[section]['read_file_2']
                read_file_2 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_2)
                file_list += read_file_2 + ' '
    file_list = file_list[:len(file_list) - 1]

    # set the transcriptome file name
    transcriptome_file = 'transabyss'

    # write the Trans-ABySS process script
    try:
        if not os.path.exists(os.path.dirname(get_transabyss_process_script())):
            os.makedirs(os.path.dirname(get_transabyss_process_script()))
        with open(get_transabyss_process_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('TRANSABYSS_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_transabyss_bioconda_code())))
            file_id.write('{0}\n'.format('PATH=$TRANSABYSS_PATH:$PATH'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('source activate {0}'.format(xlib.get_transabyss_bioconda_code())))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function run_transabyss_process'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        transabyss \\'))
            file_id.write('{0}\n'.format('            --threads {0} \\'.format(threads)))
            file_id.write('{0}\n'.format('            --stage final \\'.format(kmer_value)))
            if read_type.upper() == 'PE':
                file_id.write('{0}\n'.format('            --pe {0} \\'.format(file_list)))
            else:
                file_id.write('{0}\n'.format('            --se {0} \\'.format(file_list)))
            file_id.write('{0}\n'.format('            --length {0} \\'.format(length)))
            file_id.write('{0}\n'.format('            --kmer {0} \\'.format(kmer_value)))
            file_id.write('{0}\n'.format('            --cov {0} \\'.format(cov)))
            file_id.write('{0}\n'.format('            --eros {0} \\'.format(eros)))
            file_id.write('{0}\n'.format('            --seros {0} \\'.format(seros)))
            file_id.write('{0}\n'.format('            --gsim {0} \\'.format(gsim)))
            file_id.write('{0}\n'.format('            --indel {0} \\'.format(indel)))
            file_id.write('{0}\n'.format('            --island {0} \\'.format(island)))
            if useblat.upper() == 'YES':
                file_id.write('{0}\n'.format('            --useblat \\'))
            file_id.write('{0}\n'.format('            --pid {0} \\'.format(pid)))
            file_id.write('{0}\n'.format('            --walk {0} \\'.format(walk)))
            file_id.write('{0}\n'.format('            --outdir {0} \\'.format(current_run_dir)))
            if other_parameters.upper() == 'NONE':
                file_id.write('{0}\n'.format('            --name {0}'.format(transcriptome_file)))
            else:
                file_id.write('{0}\n'.format('            --name {0} \\'.format(transcriptome_file)))
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
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error transabyss $RC; fi'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_transabyss_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_transabyss_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_transabyss_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_transabyss_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('run_transabyss_process'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transabyss_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_transabyss_process_starter(current_run_dir):
    '''
    Build the starter of the current Trans-ABySS process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the Trans-ABySS process starter
    try:
        if not os.path.exists(os.path.dirname(get_transabyss_process_starter())):
            os.makedirs(os.path.dirname(get_transabyss_process_starter()))
        with open(get_transabyss_process_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_transabyss_process_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_transabyss_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_transabyss_config_file():
    '''
    Get the Trans-ABySS config file path.
    '''

    # assign the Trans-ABySS config file path
    transabyss_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_transabyss_code())

    # return the Trans-ABySS config file path
    return transabyss_config_file

#-------------------------------------------------------------------------------

def get_transabyss_process_script():
    '''
    Get the Trans-ABySS process script path in the local computer.
    '''

    # assign the Trans-ABySS script path
    transabyss_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_transabyss_code())

    # return the Trans-ABySS script path
    return transabyss_process_script

#-------------------------------------------------------------------------------

def get_transabyss_process_starter():
    '''
    Get the Trans-ABySS process starter path in the local computer.
    '''

    # assign the Trans-ABySS process starter path
    transabyss_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_transabyss_code())

    # return the Trans-ABySS starter path
    return transabyss_process_starter

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the Trans-ABySS process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
