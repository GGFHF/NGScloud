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
This file contains functions related to the GAMP-GSNAP process used in both console
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

def create_gmap_config_file(experiment_id='exp001', reference_dataset_id='NONE', reference_file='NONE', assembly_dataset_id='sdnt-170101-235959', assembly_type='CONTIGS'):
    '''
    Create GMAP config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # set the app
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

    # create the GMAP config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_gmap_config_file())):
            os.makedirs(os.path.dirname(get_gmap_config_file()))
        with open(get_gmap_config_file(), mode='w', encoding='utf8') as file_id:
            file_id.write('{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# The reference file must be located in the cluster directory {0}/experiment_id/reference_dataset_id'.format(xlib.get_cluster_reference_dir())))
            file_id.write('{0}\n'.format('# The assembly files must be located in the cluster directory {0}/experiment_id/assembly_dataset_id'.format(xlib.get_cluster_result_dir())))
            file_id.write('{0}\n'.format('# The experiment_id, reference_dataset_id, reference_file and assembly_dataset_id are fixed in the identification section.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# You can consult the parameters of GMAP and their meaning in http://research-pub.gene.com/gmap/.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# In section "GMAP parameters", the key "other_parameters" allows you to input additional parameters in the format:'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    other_parameters = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# parameter-i is a parameter name of GMAP and value-i a valid value of parameter-i, e.g.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    other_parameters = --no-chimeras; --canonical-mode=2'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information identifies the experiment.'))
            file_id.write('{0}\n'.format('[identification]'))
            file_id.write('{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write('{0:<50} {1}\n'.format('reference_dataset_id = {0}'.format(reference_dataset_id), '# reference dataset identification or NONE'))
            file_id.write('{0:<50} {1}\n'.format('reference_file = {0}'.format(reference_file), '# reference file name or NONE'))
            file_id.write('{0:<50} {1}\n'.format('assembly_software = {0}'.format(assembly_software), '# assembly software: {0} ({1}) or {2} ({3}) or {4} ({5}) or {6} ({7}) or {8} ({9}) or {10} ({11})'.format(xlib.get_soapdenovotrans_code(), xlib.get_soapdenovotrans_name(), xlib.get_transabyss_code(), xlib.get_transabyss_name(), xlib.get_trinity_code(), xlib.get_trinity_name(), xlib.get_star_code(), xlib.get_star_name(), xlib.get_cd_hit_est_code(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_code(), xlib.get_transcript_filter_name())))
            file_id.write('{0:<50} {1}\n'.format('assembly_dataset_id = {0}'.format(assembly_dataset_id), '# assembly dataset identification'))
            file_id.write('{0:<50} {1}\n'.format('assembly_type = {0}'.format(assembly_type), '# CONTIGS or SCAFFOLDS in {0}; NONE in {1}, {2}, {3}, {4} and {5}'.format(xlib.get_soapdenovotrans_name(),  xlib.get_transabyss_name(),  xlib.get_trinity_name(),  xlib.get_star_name(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_name())))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information to set the GMAP parameters'))
            file_id.write('{0}\n'.format('[GMAP parameters]'))
            file_id.write('{0:<50} {1}\n'.format('threads = 2', '# number of threads for use'))
            file_id.write('{0:<50} {1}\n'.format('kmer = NONE', '# kmer size to use in genome database or NONE (the program will find the highest available kmer size in the genome database)'))
            file_id.write('{0:<50} {1}\n'.format('sampling = NONE', '# Sampling to use in genome database or NONE (the program will find the smallest available sampling value in the genome database within selected k-mer size)'))
            file_id.write('{0:<50} {1}\n'.format('input-buffer-size = 1000', '# size of input buffer'))
            file_id.write('{0:<50} {1}\n'.format('output-buffer-size = 1000', '# size of buffer size in queries for output thread'))
            file_id.write('{0:<50} {1}\n'.format('prunelevel = 0', '# pruning level: 0 (no pruning) or 1 (poor seqs) or 2 (repetitive seqs) or 3 (poor and repetitive)'))
            file_id.write('{0:<50} {1}\n'.format('format = COMPRESS', '# format for output: COMPRESS or SUMMARY or ALIGN or PLS or GFF3_GENE or SPLICESITES or INTRONS or MAP_EXONS or MAP_RANGES or COORDS'))
            file_id.write('{0:<50} {1}\n'.format('other_parameters = NONE', '# additional parameters to the previous ones or NONE'))
    except:
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_gmap_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_gmap_process(cluster_name, log, function=None):
    '''
    Run a GMAP process.
    '''

    # initialize the control variable
    OK = True

    # get the GMAP option dictionary
    gmap_option_dict = xlib.get_option_dict(get_gmap_config_file())

    # get the experiment identification
    experiment_id = gmap_option_dict['identification']['experiment_id']

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the GMAP config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(xlib.get_gmap_name()))
    (OK, error_list) = validate_gmap_config_file(strict=True)
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

    # verify the GMAP-GSNAP is setup
    if OK:
        (OK, error_list, is_setup) = xbioinfoapp.is_setup_bioconda_package(xlib.get_gmap_gsnap_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** ERROR: {0} is not setup.\n'.format(xlib.get_gmap_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} setup could not be performed.\n'.format(xlib.get_gmap_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_gmap_code())
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the GMAP process script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process script {0} ...\n'.format(get_gmap_process_script()))
        (OK, error_list) = build_gmap_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the GMAP process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process script {0} in the directory {1} of the master ...\n'.format(get_gmap_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_gmap_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_gmap_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the GMAP process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_gmap_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_gmap_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the GMAP process starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_gmap_process_starter()))
        (OK, error_list) = build_gmap_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the GMAP process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} in the directory {1} of the master ...\n'.format(get_gmap_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_gmap_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_gmap_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the GMAP process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_gmap_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_gmap_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the GMAP process
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_gmap_process_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_gmap_process_starter()))
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

def validate_gmap_config_file(strict):
    '''
    Validate the GMAP config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        gmap_option_dict = xlib.get_option_dict(get_gmap_config_file())
    except:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in gmap_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = gmap_option_dict.get('identification', {}).get('experiment_id', not_found)
            is_experiment_id_OK = True
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                is_experiment_id_OK = False
                OK = False

            # check section "identification" - key "reference_dataset_id"
            reference_dataset_id = gmap_option_dict.get('identification', {}).get('reference_dataset_id', not_found)
            is_reference_dataset_id_OK = True
            if reference_dataset_id == not_found:
                error_list.append('*** ERROR: the key "reference_dataset_id" is not found in the section "identification".')
                is_reference_dataset_id_OK = False
                OK = False

            # check section "identification" - key "reference_file"
            reference_file = gmap_option_dict.get('identification', {}).get('reference_file', not_found)
            is_reference_file_OK = True
            if reference_file == not_found:
                error_list.append('*** ERROR: the key "reference_file" is not found in the section "identification".')
                is_reference_file_OK = False
                OK = False

            # check section "identification" - key "assembly_software"
            assembly_software = gmap_option_dict.get('identification', {}).get('assembly_software', not_found)
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
            assembly_dataset_id = gmap_option_dict.get('identification', {}).get('assembly_dataset_id', not_found)
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
            assembly_type = gmap_option_dict.get('identification', {}).get('assembly_type', not_found)
            is_assembly_type_OK = True
            if assembly_type == not_found:
                error_list.append('*** ERROR: the key "assembly_type" is not found in the section "identification".')
                is_assembly_type_OK = False
                OK = False
            elif assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
                if assembly_type.upper() not in ['CONTIGS', 'SCAFFOLDS']:
                    error_list.append('*** ERROR: the key "assembly_type" must be "CONTIGS" or "SCAFFOLDS" when {0} is the assembly software.'.format(xlib.get_soapdenovotrans_name()))
                    is_assembly_type_OK = False
                    OK = False
            elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
                if assembly_type.upper() != 'NONE':
                    error_list.append('*** ERROR: the key "assembly_type" must be "NONE" when {0} or {1} or {2} or {3} or {4} is the assembly software.'.format(xlib.get_transabyss_name(), xlib.get_trinity_name(), xlib.get_star_name(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_name()))
                    is_assembly_type_OK = False
                    OK = False

        # check section "GMAP parameters"
        if 'GMAP parameters' not in sections_list:
            error_list.append('*** ERROR: the section "GMAP parameters" is not found.')
            OK = False
        else:

            # check section "GMAP parameters" - key "threads"
            threads = gmap_option_dict.get('GMAP parameters', {}).get('threads', not_found)
            is_threads_OK = True
            if threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "GMAP parameters".')
                is_threads_OK = False
                OK = False
            else:
                try:
                    if int(threads) < 1:
                        error_list.append('*** ERROR: the key "threads" in the section "GMAP parameters" must be an integer value greater or equal to 1.')
                        is_threads_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "threads" in the section "GMAP parameters" must be an integer value greater or equal to 1.')
                    is_threads_OK = False
                    OK = False

            # check section "GMAP parameters" - key "kmer"
            kmer = gmap_option_dict.get('GMAP parameters', {}).get('kmer', not_found)
            is_kmer_OK = True
            if kmer == not_found:
                error_list.append('*** ERROR: the key "kmer" is not found in the section "GMAP parameters".')
                is_kmer_OK = False
                OK = False
            else:
                try:
                    if kmer.upper() != 'NONE' and (int(kmer) < 1 or int(kmer) > 16):
                        error_list.append('*** ERROR: the key "kmer" in the section "GMAP parameters" must be an integer value between 1 and 16 or NONE.')
                        is_kmer_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "kmer" in the section "GMAP parameters" must be an integer value between 1 and 16 or NONE.')
                    is_kmer_OK = False
                    OK = False

            # check section "GMAP parameters" - key "sampling"
            sampling = gmap_option_dict.get('GMAP parameters', {}).get('sampling', not_found)
            is_sampling_OK = True
            if sampling == not_found:
                error_list.append('*** ERROR: the key "sampling" is not found in the section "GMAP parameters".')
                is_sampling_OK = False
                OK = False
            else:
                try:
                    if sampling.upper() != 'NONE' and int(sampling) < 1:
                        error_list.append('*** ERROR: the key "sampling" in the section "GMAP parameters" must be an integer value greater or equal to 1 or NONE.')
                        is_sampling_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "sampling" in the section "GMAP parameters" must be an integer value greater or equal to 1 or NONE.')
                    is_sampling_OK = False
                    OK = False

            # check section "GMAP parameters" - key "input-buffer-size"
            input_buffer_size = gmap_option_dict.get('GMAP parameters', {}).get('input-buffer-size', not_found)
            is_input_buffer_size_OK = True
            if input_buffer_size == not_found:
                error_list.append('*** ERROR: the key "input-buffer-size" is not found in the section "GMAP parameters".')
                is_input_buffer_size_OK = False
                OK = False
            else:
                try:
                    if int(input_buffer_size) < 1:
                        error_list.append('*** ERROR: the key "input-buffer-size" in the section "GMAP parameters" must be an integer value greater or equal to 1.')
                        is_input_buffer_size_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "input-buffer-size" in the section "GMAP parameters" must be an integer value greater or equal to 1.')
                    is_input_buffer_size_OK = False
                    OK = False

            # check section "GMAP parameters" - key "output-buffer-size"
            output_buffer_size = gmap_option_dict.get('GMAP parameters', {}).get('output-buffer-size', not_found)
            is_output_buffer_size_OK = True
            if output_buffer_size == not_found:
                error_list.append('*** ERROR: the key "output-buffer-size" is not found in the section "GMAP parameters".')
                is_output_buffer_size_OK = False
                OK = False
            else:
                try:
                    if int(output_buffer_size) < 1:
                        error_list.append('*** ERROR: the key "output-buffer-size" in the section "GMAP parameters" must be an integer value greater or equal to 1.')
                        is_output_buffer_size_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "output-buffer-size" in the section "GMAP parameters" must be an integer value greater or equal to 1.')
                    is_output_buffer_size_OK = False
                    OK = False

            # check section "GMAP parameters" - key "prunelevel"
            prunelevel = gmap_option_dict.get('GMAP parameters', {}).get('prunelevel', not_found)
            is_prunelevel_OK = True
            if prunelevel == not_found:
                error_list.append('*** ERROR: the key "prunelevel" is not found in the section "GMAP parameters".')
                is_prunelevel_OK = False
                OK = False
            else:
                if prunelevel not in ['0', '1', '2', '3']:
                    error_list.append('*** ERROR: the key "prunelevel" in the section "GMAP parameters" must be 0 (no pruning) or 1 (poor seqs) or 2 (repetitive seqs) or 3 (poor and repetitive).')
                    is_prunelevel_OK = False
                    OK = False

            # check section "GMAP parameters" - key "format"
            format = gmap_option_dict.get('GMAP parameters', {}).get('format', not_found)
            is_format_OK = True
            if format == not_found:
                error_list.append('*** ERROR: the key "format" is not found in the section "GMAP parameters".')
                is_format_OK = False
                OK = False
            else:
                if format.upper() not in ['COMPRESS', 'SUMMARY', 'ALIGN', 'PLS', 'GFF3_GENE', 'SPLICESITES', 'INTRONS', 'MAP_EXONS', 'MAP_RANGES', 'COORDS']:
                    error_list.append('*** ERROR: the key "format" in the section "GMAP parameters" must be COMPRESS or SUMMARY or ALIGN or PLS or GFF3_GENE or SPLICESITES or INTRONS or MAP_EXONS or MAP_RANGES or COORDS.')
                    is_format_OK = False
                    OK = False

            # check section "GMAP parameters" - key "other_parameters"
            not_allowed_parameters_list = ['nthreads', 'kmer', 'sampling', 'input-buffer-size', 'output-buffer-size', 'prunelevel', 'compress', 'summary', 'align', 'format' ]
            other_parameters = gmap_option_dict.get('GMAP parameters', {}).get('other_parameters', not_found)
            is_other_parameters_OK = True
            if other_parameters == not_found:
                error_list.append('*** ERROR: the key "other_parameters" is not found in the section "GMAP parameters".')
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
                            error_list.append('*** ERROR: the value of the key "other_parameters" in the section "GMAP parameters" must be NONE or a valid parameter list.')
                            is_other_parameters_OK = False
                            OK = False
                            break
                        else:
                            if parameter_name in not_allowed_parameters_list:
                                error_list.append('*** ERROR: the parameter {0} is not allowed in the key "other_parameters" of the section "GMAP parameters" because it is controled by NGScloud.'.format(parameter_name))
                                is_other_parameters_OK = False
                                OK = False

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_gmap_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_gmap_process_script(cluster_name, current_run_dir):
    '''
    Build the current GMAP process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the GMAP option dictionary
    gmap_option_dict = xlib.get_option_dict(get_gmap_config_file())

    # get the options
    experiment_id = gmap_option_dict['identification']['experiment_id']
    reference_dataset_id = gmap_option_dict['identification']['reference_dataset_id']
    reference_file = gmap_option_dict['identification']['reference_file']
    assembly_software = gmap_option_dict['identification']['assembly_software']
    assembly_dataset_id = gmap_option_dict['identification']['assembly_dataset_id']
    assembly_type = gmap_option_dict['identification']['assembly_type']
    threads = gmap_option_dict['GMAP parameters']['threads']
    kmer = gmap_option_dict['GMAP parameters']['kmer']
    sampling = gmap_option_dict['GMAP parameters']['sampling']
    input_buffer_size = gmap_option_dict['GMAP parameters']['input-buffer-size']
    output_buffer_size = gmap_option_dict['GMAP parameters']['output-buffer-size']
    prunelevel = gmap_option_dict['GMAP parameters']['prunelevel']
    format = gmap_option_dict['GMAP parameters']['format']
    other_parameters = gmap_option_dict['GMAP parameters']['other_parameters']

    # set the cluster reference dataset directory
    cluster_reference_dataset_dir = xlib.get_cluster_reference_dataset_dir(reference_dataset_id)

    # set the cluster reference file
    cluster_reference_file = xlib.get_cluster_reference_file(reference_dataset_id, reference_file)

    # set the GMAP database name
    reference_file_name, reference_file_extension = os.path.splitext(reference_file)
    gmap_database = '{0}-gmap_database'.format(reference_file_name)

    # set the transcriptome file path
    if assembly_software == xlib.get_soapdenovotrans_code():
        if assembly_type.upper() == 'CONTIGS':
            transcriptome_file = '{0}/{1}-{2}.contig'.format(xlib.get_cluster_experiment_result_dataset_dir(experiment_id, assembly_dataset_id), experiment_id, assembly_dataset_id)
        elif assembly_type.upper() == 'SCAFFOLDS':
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

    # set the output file path
    output_file = 'gmap_output_{0}.txt'.format(format.lower())

    # get the GMAP process script name
    gmap_process_script = get_gmap_process_script()

    # write the GMAP process script
    try:
        if not os.path.exists(os.path.dirname(gmap_process_script)):
            os.makedirs(os.path.dirname(gmap_process_script))
        with open(gmap_process_script, mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('GMAP_GSNAP_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_gmap_gsnap_bioconda_code())))
            file_id.write('{0}\n'.format('PATH=$GMAP_GSNAP_PATH:$PATH'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('source activate {0}'.format(xlib.get_gmap_gsnap_bioconda_code())))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function build_gmap_database'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        gmap_build \\'))
            file_id.write('{0}\n'.format('            --dir={0}\\'.format(cluster_reference_dataset_dir)))
            file_id.write('{0}\n'.format('            --db={0}\\'.format(gmap_database)))
            if kmer.upper() != 'NONE':
                file_id.write('{0}\n'.format('            --kmer={0} \\'.format(kmer)))
            file_id.write('{0}\n'.format('            {0}'.format(cluster_reference_file)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function run_gmap_process'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    gmap --version'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        gmap \\'))
            file_id.write('{0}\n'.format('            --nthreads={0} \\'.format(threads)))
            file_id.write('{0}\n'.format('            --dir={0} \\'.format(cluster_reference_dataset_dir)))
            file_id.write('{0}\n'.format('            --db={0} \\'.format(gmap_database)))
            if kmer.upper() != 'NONE':
                file_id.write('{0}\n'.format('            --kmer={0} \\'.format(kmer)))
            if sampling.upper() != 'NONE':
                file_id.write('{0}\n'.format('            --sampling={0} \\'.format(sampling)))
            file_id.write('{0}\n'.format('            --input-buffer-size={0} \\'.format(input_buffer_size)))
            file_id.write('{0}\n'.format('            --output-buffer-size={0} \\'.format(output_buffer_size)))
            file_id.write('{0}\n'.format('            --prunelevel={0} \\'.format(prunelevel)))
            if format.upper() == 'COMPRESS':
                file_id.write('{0}\n'.format('            --compress \\'))
            elif format.upper() == 'SUMMARY':
                file_id.write('{0}\n'.format('            --summary \\'))
            elif format.upper() == 'ALIGN':
                file_id.write('{0}\n'.format('            --align \\'))
            else:
                file_id.write('{0}\n'.format('            --format={0} \\'.format(format.lower())))
            file_id.write('{0}\n'.format('            --ordered \\'))
            file_id.write('{0}\n'.format('            --nofails \\'))
            if other_parameters.upper() != 'NONE':
                parameter_list = [x.strip() for x in other_parameters.split(';')]
                for i in range(len(parameter_list)):
                    if parameter_list[i].find('=') > 0:
                        pattern = r'^--(.+)=(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        parameter_value = mo.group(2).strip()
                        file_id.write('{0}\n'.format('            --{0}={1} \\'.format(parameter_name, parameter_value)))
                    else:
                        pattern = r'^--(.+)$'
                        mo = re.search(pattern, parameter_list[i])
                        parameter_name = mo.group(1).strip()
                        file_id.write('{0}\n'.format('            --{0} \\'.format(parameter_name)))
            file_id.write('{0}\n'.format('            {0} \\'.format(transcriptome_file)))
            file_id.write('{0}\n'.format('            > {0}'.format(output_file)))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error gmap $RC; fi'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_gmap_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_gmap_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_gmap_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_gmap_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('build_gmap_database'))
            file_id.write('{0}\n'.format('run_gmap_process'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(gmap_process_script))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_gmap_process_starter(current_run_dir):
    '''
    Build the starter of the current GMAP process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the GMAP process starter
    try:
        if not os.path.exists(os.path.dirname(get_gmap_process_starter())):
            os.makedirs(os.path.dirname(get_gmap_process_starter()))
        with open(get_gmap_process_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_gmap_process_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_gmap_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_gmap_config_file():
    '''
    Get the GMAP config file path.
    '''

    # assign the GMAP config file path
    gmap_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_gmap_code())

    # return the GMAP config file path
    return gmap_config_file

#-------------------------------------------------------------------------------

def get_gmap_process_script():
    '''
    Get the GMAP process script path in the local computer.
    '''

    # assign the GMAP script path
    gmap_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_gmap_code())

    # return the GMAP script path
    return gmap_process_script

#-------------------------------------------------------------------------------

def get_gmap_process_starter():
    '''
    Get the GMAP process starter path in the local computer.
    '''

    # assign the GMAP process starter path
    gmap_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_gmap_code())

    # return the GMAP starter path
    return gmap_process_starter

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the GMAP-GSNAP process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
