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
This file contains functions related to the DETONATE process used in
both console mode and gui mode.
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

def create_rsem_eval_config_file(experiment_id='exp001', read_dataset_id=xlib.get_uploaded_read_dataset_name(), read_type = 'PE', file_1_list=['rnaseq-a_1.fastq'], file_2_list=['rnaseq-a_2.fastq'], assembly_dataset_id='sdnt-170101-235959', assembly_type='CONTIGS'):
    '''
    Create RSEM-EVAL config file with the default options. It is necessary
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

    # create the RSEM-EVAL config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_rsem_eval_config_file())):
            os.makedirs(os.path.dirname(get_rsem_eval_config_file()))
        with open(get_rsem_eval_config_file(), mode='w', encoding='utf8') as file_id:
            file_id.write('{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# The read files must be located in the cluster directory {0}/experiment_id/read_dataset_id'.format(xlib.get_cluster_read_dir())))
            file_id.write('{0}\n'.format('# The assembly files must be located in the cluster directory {0}/experiment_id/assembly_dataset_id'.format(xlib.get_cluster_result_dir())))
            file_id.write('{0}\n'.format('# The experiment_id, read_dataset_id and assembly_dataset_id names are fixed in the identification section.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# You can consult the parameters of RSEM-EVAL (DETONATE package) and their meaning in http://deweylab.biostat.wisc.edu/detonate/.'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information identifies the assembly result dataset.'))
            file_id.write('{0}\n'.format('[identification]'))
            file_id.write('{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write('{0:<50} {1}\n'.format('read_dataset_id = {0}'.format(read_dataset_id), '# read dataset identification'))
            file_id.write('{0:<50} {1}\n'.format('assembly_software = {0}'.format(assembly_software), '# assembly software: {0} ({1}) or {2} ({3}) or {4} ({5}) or {6} ({7} or {8} ({9})'.format(xlib.get_soapdenovotrans_code(), xlib.get_soapdenovotrans_name(), xlib.get_trinity_code(), xlib.get_trinity_name(), xlib.get_star_code(), xlib.get_star_name(), xlib.get_cd_hit_est_code(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_code(), xlib.get_transcript_filter_name())))
            file_id.write('{0:<50} {1}\n'.format('assembly_dataset_id = {0}'.format(assembly_dataset_id), '# assembly dataset identification'))
            file_id.write('{0:<50} {1}\n'.format('assembly_type = {0}'.format(assembly_type), '# CONTIGS or SCAFFOLDS in {0}; NONE in {1}, {2}, {3} and {4}'.format(xlib.get_soapdenovotrans_name(),  xlib.get_trinity_name(),  xlib.get_star_name(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_name())))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information to set the RSEM-EVAL parameters'))
            file_id.write('{0}\n'.format('[RSEM-EVAL parameters]'))
            file_id.write('{0:<50} {1}\n'.format('num_threads = 2', '# number of threads for use'))
            file_id.write('{0:<50} {1}\n'.format('bowtie2_mismatch_rate = 0.1', '# maximum mismatch rate allowed (Bowtie 2 parameter)'))
            file_id.write('{0:<50} {1}\n'.format('keep_intermediate_files = NO', '# keep temporary files generated: YES or NO'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the global information of all libraries.'))
            file_id.write('{0}\n'.format('[library]'))
            file_id.write('{0:<50} {1}\n'.format('format = FASTQ', '# FASTQ or FASTA'))
            file_id.write('{0:<50} {1}\n'.format('read_type = {0}'.format(read_type), '# SE (single-end) or PE (paired-end)'))
            file_id.write('{0:<50} {1}\n'.format('length = 200', '# average read length in SE read type or average fragment length in PE read type'))
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
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_rsem_eval_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_rsem_eval_process(cluster_name, log, function=None):
    '''
    Run a RSEM-EVAL process.
    '''

    # initialize the control variable
    OK = True

    # get the RSEM-EVAL option dictionary
    rsem_eval_option_dict = xlib.get_option_dict(get_rsem_eval_config_file())

    # get the experiment identification
    experiment_id = rsem_eval_option_dict['identification']['experiment_id']

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the RSEM-EVAL config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(xlib.get_rsem_eval_name()))
    (OK, error_list) = validate_rsem_eval_config_file(strict=True)
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

    # verify the DETONATE is set up
    if OK:
        (OK, error_list, is_setup) = xbioinfoapp.is_setup_bioconda_package(xlib.get_detonate_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** ERROR: {0} is not setup.\n'.format(xlib.get_detonate_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} setup could not be performed.\n'.format(xlib.get_detonate_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_rsem_eval_code())
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the RSEM-EVAL process script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process script {0} ...\n'.format(get_rsem_eval_process_script()))
        (OK, error_list) = build_rsem_eval_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the RSEM-EVAL process script to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(get_rsem_eval_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_rsem_eval_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_rsem_eval_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the RSEM-EVAL process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_rsem_eval_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_rsem_eval_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the RSEM-EVAL process starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_rsem_eval_process_starter()))
        (OK, error_list) = build_rsem_eval_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the RSEM-EVAL process starter to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(get_rsem_eval_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_rsem_eval_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_rsem_eval_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the RSEM-EVAL process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_rsem_eval_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_rsem_eval_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the RSEM-EVAL process
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_rsem_eval_process_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_rsem_eval_process_starter()))
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

def validate_rsem_eval_config_file(strict):
    '''
    Validate the RSEM-EVAL config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        rsem_eval_option_dict = xlib.get_option_dict(get_rsem_eval_config_file())
    except:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in rsem_eval_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = rsem_eval_option_dict.get('identification', {}).get('experiment_id', not_found)
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "read_dataset_id"
            read_dataset_id = rsem_eval_option_dict.get('identification', {}).get('read_dataset_id', not_found)
            if read_dataset_id == not_found:
                error_list.append('*** ERROR: the key "read_dataset_id" is not found in the section "identification".')
                OK = False

            # check section "identification" - key "assembly_software"
            assembly_software = rsem_eval_option_dict.get('identification', {}).get('assembly_software', not_found)
            if assembly_software == not_found:
                error_list.append('*** ERROR: the key "assembly_software" is not found in the section "identification".')
                OK = False
            elif assembly_software not in [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]:
                error_list.append('*** ERROR: the key "assembly_software" value in the section "identification" must be {0} or {1} or {2} or {3} or {4} OR {5}.'.format(xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()))
                OK = False

            # check section "identification" - key "assembly_dataset_id"
            assembly_dataset_id = rsem_eval_option_dict.get('identification', {}).get('assembly_dataset_id', not_found)
            if assembly_dataset_id == not_found:
                error_list.append('*** ERROR: the key "assembly_dataset_id" is not found in the section "identification".')
                OK = False
            elif not assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()) and not assembly_dataset_id.startswith(xlib.get_transabyss_code()) and not assembly_dataset_id.startswith(xlib.get_trinity_code()) and not assembly_dataset_id.startswith(xlib.get_star_code()) and not assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) and not assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
                error_list.append('*** ERROR: the key "assembly_dataset_id" value is not a {0} nor {1} nor {2} nor {3} nor {4} nor {5} assembly.'.format(xlib.get_soapdenovotrans_name(), xlib.get_transabyss_name(), xlib.get_trinity_name(), xlib.get_star_name(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_code()))
                OK = False

            # check section "identification" - key "assembly_type"
            assembly_type = rsem_eval_option_dict.get('identification', {}).get('assembly_type', not_found)
            if assembly_type == not_found:
                error_list.append('*** ERROR: the key "assembly_type" is not found in the section "identification".')
                OK = False
            elif assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
                if assembly_type.upper() not in ['CONTIGS', 'SCAFFOLDS']:
                    error_list.append('*** ERROR: the key "assembly_type" must be "CONTIGS" or "SCAFFOLDS" when {0} is the assembly software.'.format(xlib.get_soapdenovotrans_name()))
                    OK = False
            elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
                if assembly_type.upper() != 'NONE':
                    error_list.append('*** ERROR: the key "assembly_type" must be "NONE" when {0} or {1} or {2} or {3} or {4} is the assembly software.'.format(xlib.get_transabyss_name(), xlib.get_trinity_name(), xlib.get_star_name(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_name()))
                    OK = False

        # check section "RSEM-EVAL parameters"
        if 'RSEM-EVAL parameters' not in sections_list:
            error_list.append('*** ERROR: the section "RSEM-EVAL parameters" is not found.')
            OK = False
        else:

            # check section "RSEM-EVAL parameters" - key "threads"
            num_threads = rsem_eval_option_dict.get('RSEM-EVAL parameters', {}).get('num_threads', not_found)
            if num_threads == not_found:
                error_list.append('*** ERROR: the key "threads" is not found in the section "RSEM-EVAL parameters".')
                OK = False
            else:
                try:
                    if int(num_threads) < 1:
                        error_list.append('*** ERROR: the key "threads" in the section "RSEM-EVAL parameters" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "threads" in the section "RSEM-EVAL parameters" must be an integer value greater or equal to 1.')
                    OK = False

            # check section "RSEM-EVAL parameters" - key "bowtie2_mismatch_rate"
            bowtie2_mismatch_rate = rsem_eval_option_dict.get('RSEM-EVAL parameters', {}).get('bowtie2_mismatch_rate', not_found)
            if bowtie2_mismatch_rate == not_found:
                error_list.append('*** ERROR: the key "bowtie2_mismatch_rate" is not found in the section "RSEM-EVAL parameters".')
                OK = False
            else:
                try:
                    if float(bowtie2_mismatch_rate) < 0.0 or float(bowtie2_mismatch_rate) > 1.0:
                        error_list.append('*** ERROR: the key "bowtie2_mismatch_rate" in the section "RSEM-EVAL parameters" must be a float value between 0.0 and 1.0.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "bowtie2_mismatch_rate" in the section "RSEM-EVAL parameters" must be a float value between 0.0 and 1.0.')
                    OK = False

            # check section "RSEM-EVAL parameters" - key "keep_intermediate_files"
            keep_intermediate_files = rsem_eval_option_dict.get('RSEM-EVAL parameters', {}).get('keep_intermediate_files', not_found).upper()
            if keep_intermediate_files == not_found:
                error_list.append('*** ERROR: the key "keep_intermediate_files" is not found in the section "RSEM-EVAL parameters".')
                OK = False
            elif keep_intermediate_files not in ['YES', 'NO']:
                error_list.append('*** ERROR: the key "keep_intermediate_files" value in the section "RSEM-EVAL parameters" must be YES or NO.')
                OK = False

        # check section "library"
        if 'library' not in sections_list:
            error_list.append('*** ERROR: the section "library" is not found.')
            OK = False
        else:

            # check section "library" - key "format"
            format = rsem_eval_option_dict.get('library', {}).get('format', not_found).upper()
            if format == not_found:
                error_list.append('*** ERROR: the key "format" is not found in the section "library".')
                OK = False
            elif format not in ['FASTA', 'FASTQ']:
                error_list.append('*** ERROR: the key "format" value in the section "library" must be FASTA or FASTQ.')
                OK = False

            # check section "library" - key "read_type"
            read_type = rsem_eval_option_dict.get('library', {}).get('read_type', not_found).upper()
            if read_type == not_found:
                error_list.append('*** ERROR: the key "read_type" is not found in the section "library".')
                OK = False
            elif read_type not in ['PE', 'SE']:
                error_list.append('*** ERROR: the key "read_type" value in the section "library" must be SE or PE.')
                OK = False

            # check section "library" - key "length"
            length = rsem_eval_option_dict.get('library', {}).get('length', not_found)
            if length == not_found:
                error_list.append('*** ERROR: the key "length" is not found in the section "library".')
                OK = False
            else:
                try:
                    if int(length) < 1:
                        error_list.append('*** ERROR: the key "length" in the section "library" must be an integer value greater or equal to 1.')
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "length" in the section "library" must be an integer value greater or equal to 1.')
                    OK = False

        # check section "library-1"
        if 'library-1' not in sections_list:
            error_list.append('*** ERROR: the section "library-1" is not found.')
            OK = False

        # check all sections "library-n"
        for section in sections_list:

            if section not in ['identification', 'RSEM-EVAL parameters', 'library']:

                # verify than the section identification is like library-n 
                if not re.match('^library-[0-9]+$', section):
                    error_list.append('*** ERROR: the section "{0}" has a wrong identification.'.format(section))
                    OK = False

                else:

                    # check section "library-n" - key "read_file_1"
                    read_file_1 = rsem_eval_option_dict.get(section, {}).get('read_file_1', not_found)
                    if read_file_1 == not_found:
                        error_list.append('*** ERROR: the key "read_file_1" is not found in the section "{0}"'.format(section))
                        OK = False

                    # check section "library-n" - key "read_file_2"
                    read_file_2 = rsem_eval_option_dict.get(section, {}).get('read_file_2', not_found)
                    if read_file_2 == not_found:
                        error_list.append('*** ERROR: the key "read_file_2" is not found in the section "{0}"'.format(section))
                        OK = False

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_rsem_eval_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_rsem_eval_process_script(cluster_name, current_run_dir):
    '''
    Build the current RSEM-EVAL process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the option dictionary
    rsem_eval_option_dict = xlib.get_option_dict(get_rsem_eval_config_file())

    # get the options
    experiment_id = rsem_eval_option_dict['identification']['experiment_id']
    read_dataset_id = rsem_eval_option_dict['identification']['read_dataset_id']
    assembly_software = rsem_eval_option_dict['identification']['assembly_software']
    assembly_dataset_id = rsem_eval_option_dict['identification']['assembly_dataset_id']
    assembly_type = rsem_eval_option_dict['identification']['assembly_type']
    num_threads = rsem_eval_option_dict['RSEM-EVAL parameters']['num_threads']
    bowtie2_mismatch_rate = rsem_eval_option_dict['RSEM-EVAL parameters']['bowtie2_mismatch_rate']
    keep_intermediate_files = rsem_eval_option_dict['RSEM-EVAL parameters']['keep_intermediate_files']
    format = rsem_eval_option_dict['library']['format'].upper()
    read_type = rsem_eval_option_dict['library']['read_type'].upper()
    length = rsem_eval_option_dict['library']['length']

    # get the sections list
    sections_list = []
    for section in rsem_eval_option_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build library files
    files1 = ''
    files2 = ''
    for section in sections_list:
        # if the section identification is like library-n
        if re.match('^library-[0-9]+$', section):
            read_file_1 = rsem_eval_option_dict[section]['read_file_1']
            read_file_1 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_1)
            files1 += read_file_1 + ','
            if read_type == 'PE':
                read_file_2 = rsem_eval_option_dict[section]['read_file_2']
                read_file_2 = xlib.get_cluster_read_file(experiment_id, read_dataset_id, read_file_2)
                files2 += read_file_2 + ','
    files1 = files1[:len(files1) - 1]
    if read_type == 'PE':
        files2 = files2[:len(files2) - 1]

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

    # set the distribution file path
    distribution_file = '{0}/distribution.txt'.format(current_run_dir)

    # set the temporaly directory path
    temp_dir = '{0}/temp'.format(current_run_dir)

    # write the RSEM-EVAL process script
    try:
        if not os.path.exists(os.path.dirname(get_rsem_eval_process_script())):
            os.makedirs(os.path.dirname(get_rsem_eval_process_script()))
        with open(get_rsem_eval_process_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('DETONATE_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_detonate_bioconda_code())))
            file_id.write('{0}\n'.format('BOWTIE2_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_bowtie2_bioconda_code())))
            file_id.write('{0}\n'.format('PATH=$DETONATE_PATH:$BOWTIE2_PATH:$PATH'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('source activate {0}'.format(xlib.get_detonate_bioconda_code())))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function run_rsem_eval_process'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    rsem-eval-calculate-score --version'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Running rsem-eval-estimate-transcript-length-distribution ... "'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        rsem-eval-estimate-transcript-length-distribution \\'))
            file_id.write('{0}\n'.format('            {0} \\'.format(transcriptome_file)))
            file_id.write('{0}\n'.format('            {0}'.format(distribution_file)))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error rsem-eval-estimate-transcript-length-distribution $RC; fi'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Running rsem-eval-calculate-score ... "'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        rsem-eval-calculate-score \\'))
            file_id.write('{0}\n'.format('            --num-threads {0} \\'.format(num_threads)))
            file_id.write('{0}\n'.format('            --bowtie2 \\'))
            file_id.write('{0}\n'.format('            --bowtie2-mismatch-rate {0} \\'.format(bowtie2_mismatch_rate)))
            file_id.write('{0}\n'.format('            --transcript-length-parameters {0} \\'.format(distribution_file)))
            file_id.write('{0}\n'.format('            --temporary-folder {0} \\'.format(temp_dir)))
            if keep_intermediate_files.upper() == 'YES':
                file_id.write('{0}\n'.format('            --keep-intermediate-files \\'))
            if format == 'FASTA':
                file_id.write('{0}\n'.format('            --no-qualities \\'))
            if read_type == 'PE':
                file_id.write('{0}\n'.format('            --paired-end {0} {1} \\'.format(files1, files2)))
            else:
                file_id.write('{0}\n'.format('            {0} \\'.format(files1)))
            file_id.write('{0}\n'.format('            {0} \\'.format(transcriptome_file)))
            file_id.write('{0}\n'.format('            {0} \\'.format(current_run_dir)))
            file_id.write('{0}\n'.format('            {0}'.format(length)))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then rsem-eval-calculate-score $RC; fi'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function move_result_files'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Moving result files ... "'))
            file_id.write('{0}\n'.format('    mv ../{0}.stat/* .'.format(os.path.basename(current_run_dir))))
            file_id.write('{0}\n'.format('    rm -fr ../{0}.stat'.format(os.path.basename(current_run_dir))))
            file_id.write('{0}\n'.format('    mv ../{0}.* .'.format(os.path.basename(current_run_dir))))
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
            file_id.write('{0}\n'.format('    echo "FILTERING_DATA - ASSEMBLY_SOFTWARE: {0}"'.format(assembly_software)))
            file_id.write('{0}\n'.format('    echo "FILTERING_DATA - ASSEMBLY_DATASET_ID: {0}"'.format(assembly_dataset_id)))
            file_id.write('{0}\n'.format('    echo "FILTERING_DATA - ASSEMBLY_TYPE: {0}"'.format(assembly_type)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    RECIPIENT={0}'.format(xconfiguration.get_contact_data())))
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_rsem_eval_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {0} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_rsem_eval_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_rsem_eval_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {0} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_rsem_eval_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('run_rsem_eval_process'))
            file_id.write('{0}\n'.format('move_result_files'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_rsem_eval_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_rsem_eval_process_starter(current_run_dir):
    '''
    Build the starter of the current RSEM-EVAL process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the RSEM-EVAL process starter
    try:
        if not os.path.exists(os.path.dirname(get_rsem_eval_process_starter())):
            os.makedirs(os.path.dirname(get_rsem_eval_process_starter()))
        with open(get_rsem_eval_process_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_rsem_eval_process_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_rsem_eval_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_rsem_eval_config_file():
    '''
    Get the RSEM-EVAL config file path.
    '''

    # assign the RSEM-EVAL config file path
    rsem_eval_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_rsem_eval_code())

    # return the RSEM-EVAL config file path
    return rsem_eval_config_file

#-------------------------------------------------------------------------------

def get_rsem_eval_process_script():
    '''
    Get the RSEM-EVAL process script path in the local computer.
    '''

    # assign the RSEM-EVAL script path
    rsem_eval_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_rsem_eval_code())

    # return the RSEM-EVAL script path
    return rsem_eval_process_script

#-------------------------------------------------------------------------------

def get_rsem_eval_process_starter():
    '''
    Get the RSEM-EVAL process starter path in the local computer.
    '''

    # assign the RSEM-EVAL process starter path
    rsem_eval_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_rsem_eval_code())

    # return the RSEM-EVAL starter path
    return rsem_eval_process_starter

#-------------------------------------------------------------------------------

def create_ref_eval_config_file(experiment_id='exp001', read_dataset_id=xlib.get_uploaded_read_dataset_name(), read_type = 'PE', file_1_list=['rnaseq-a_1.fastq'], file_2_list=['rnaseq-a_2.fastq'], assembly_dataset_id='sndt-170101-235959', assembly_type='CONTIGS'):
    '''
    Create REF-EVAL config file with the default options. It is necessary
    update the options in each run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    #...

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_ref_eval_process(cluster_name, log, function=None):
    '''
    Run a REF-EVAL process.
    '''

    # initialize the control variable
    OK = True

    # get the REF-EVAL option dictionary
    ref_eval_option_dict = xlib.get_option_dict(get_ref_eval_config_file())

    # get the experiment identification
    experiment_id = ref_eval_option_dict['identification']['experiment_id']

    # get the REF-EVAL process script path in the local computer
    ref_eval_process_script = get_ref_eval_process_script()

    # get the REF-EVAL process starter path in the local computer
    ref_eval_process_starter = get_ref_eval_process_starter()

    # get the aplication directory in the cluster
    cluster_app_dir = xlib.get_cluster_app_dir()

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the REF-EVAL config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(xlib.get_ref_eval_name()))
    (OK, error_list) = validate_ref_eval_config_file(strict=True)
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

    # verify the DETONATE is set up
    if OK:
        command = '[ -d {0}/{1} ] && echo RC=0 || echo RC=1'.format(cluster_app_dir, xlib.get_detonate_name())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] != 'RC=0':
            log.write('*** ERROR: {0} is not setup.\n'.format(xlib.get_detonate_name()))
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_ref_eval_code())
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the REF-EVAL process script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process script {0} ...\n'.format(ref_eval_process_script))
        (OK, error_list) = build_ref_eval_process_script(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the REF-EVAL process script to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process script {0} to the directory {1} of the master ...\n'.format(ref_eval_process_script, current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(ref_eval_process_script))
        (OK, error_list) = xssh.put_file(sftp_client, ref_eval_process_script, cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the REF-EVAL process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(ref_eval_process_script)))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(ref_eval_process_script))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the REF-EVAL process starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(ref_eval_process_starter))
        (OK, error_list) = build_ref_eval_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the REF-EVAL process starter to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} to the directory {1} of the master ...\n'.format(ref_eval_process_starter, current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(ref_eval_process_starter))
        (OK, error_list) = xssh.put_file(sftp_client, ref_eval_process_starter, cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the REF-EVAL process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(ref_eval_process_starter)))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(ref_eval_process_starter))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the REF-EVAL process
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(ref_eval_process_starter)))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(ref_eval_process_starter))
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

def validate_ref_eval_config_file(strict):
    '''
    Validate the RSEM-EVAL config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # ...

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_ref_eval_process_script(current_run_dir):
    '''
    Build the current RSEM-EVAL process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # ...

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_ref_eval_process_starter(current_run_dir):
    '''
    Build the starter of the current RSEM-EVAL process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the RSEM-EVAL process starter
    try:
        if not os.path.exists(os.path.dirname(get_ref_eval_process_starter())):
            os.makedirs(os.path.dirname(get_ref_eval_process_starter()))
        with open(get_ref_eval_process_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_ref_eval_process_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_ref_eval_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_ref_eval_config_file():
    '''
    Get the REF-EVAL config file path.
    '''

    # assign the REF-EVAL config file path
    ref_eval_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_ref_eval_code())

    # return the REF-EVAL config file path
    return ref_eval_config_file

#-------------------------------------------------------------------------------

def get_ref_eval_process_script():
    '''
    Get the REF-EVAL process script path in the local computer.
    '''

    # assign the REF-EVAL script path
    ref_eval_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_ref_eval_code())

    # return the REF-EVAL script path
    return ref_eval_process_script

#-------------------------------------------------------------------------------

def get_ref_eval_process_starter():
    '''
    Get the REF-EVAL process starter path in the local computer.
    '''

    # assign the REF-EVAL process starter path
    ref_eval_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_ref_eval_code())

    # return the REF-EVAL starter path
    return ref_eval_process_starter

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the DETONATE process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
