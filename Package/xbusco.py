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
This file contains functions related to the BUSCO process used in both console
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

def create_busco_config_file(experiment_id='exp001', assembly_dataset_id='sdnt-170101-235959', assembly_type='CONTIGS'):
    '''
    Create BUSCO config file with the default options. It is necessary
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

    # create the BUSCO config file and write the default options
    try:
        if not os.path.exists(os.path.dirname(get_busco_config_file())):
            os.makedirs(os.path.dirname(get_busco_config_file()))
        with open(get_busco_config_file(), mode='w', encoding='utf8') as file_id:
            file_id.write('{0}\n'.format('# You must review the information of this file and update the values with the corresponding ones to the current run.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# The reference file must be located in the cluster directory {0}/experiment_id/reference_dataset_id'.format(xlib.get_cluster_reference_dir())))
            file_id.write('{0}\n'.format('# The assembly files must be located in the cluster directory {0}/experiment_id/assembly_dataset_id'.format(xlib.get_cluster_result_dir())))
            file_id.write('{0}\n'.format('# The experiment_id and assembly_dataset_id names are fixed in the identification section.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# In section "BUSCO parameters", the key "augustus_options" allows you to input additional August parameters in the format:'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    augustus_options = --parameter-1[=value-1][; --parameter-2[=value-2][; ...; --parameter-n[=value-n]]]'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# parameter-i is a parameter name of Augustus and value-i a valid value of parameter-i, e.g.'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('#    augustus_options = --translation_table=6 --progress=true)'))
            file_id.write('{0}\n'.format('#'))
            file_id.write('{0}\n'.format('# You can consult the parameters of BUSCO and their meaning in http://busco.ezlab.org/.'))
            file_id.write('{0}\n'.format('# and August ones in http://bioinf.uni-greifswald.de/augustus/.'))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information identifies the experiment.'))
            file_id.write('{0}\n'.format('[identification]'))
            file_id.write('{0:<50} {1}\n'.format('experiment_id = {0}'.format(experiment_id), '# experiment identification'))
            file_id.write('{0:<50} {1}\n'.format('assembly_software = {0}'.format(assembly_software), '# assembly software: {0} ({1}) or {2} ({3}) or {4} ({5}) or {6} ({7}) or {8} ({9}) or {10} ({11})'.format(xlib.get_soapdenovotrans_code(), xlib.get_soapdenovotrans_name(), xlib.get_transabyss_code(), xlib.get_transabyss_name(), xlib.get_trinity_code(), xlib.get_trinity_name(), xlib.get_star_code(), xlib.get_star_name(), xlib.get_cd_hit_est_code(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_code(), xlib.get_transcript_filter_name())))
            file_id.write('{0:<50} {1}\n'.format('assembly_dataset_id = {0}'.format(assembly_dataset_id), '# assembly dataset identification'))
            file_id.write('{0:<50} {1}\n'.format('assembly_type = {0}'.format(assembly_type), '# CONTIGS or SCAFFOLDS in {0}; NONE in {1}, {2}, {3}, {4} and {5}'.format(xlib.get_soapdenovotrans_name(),  xlib.get_transabyss_name(),  xlib.get_trinity_name(),  xlib.get_star_name(), xlib.get_cd_hit_est_name(), xlib.get_transcript_filter_name())))
            file_id.write('{0}\n'.format(''))
            file_id.write('{0}\n'.format('# This section has the information to set the BUSCO parameters'))
            file_id.write('{0}\n'.format('[BUSCO parameters]'))
            file_id.write('{0:<50} {1}\n'.format('ncpu = 2', '# number of threads/cores for use'))
            file_id.write('{0:<50} {1}\n'.format('lineage_data = embryophyta_odb9', '# value to find the lineage data url in BUSCO web (e.g. embryophyta -> http://busco.ezlab.org/v2/datasets/embryophyta_odb9.tar.gz)'))
            file_id.write('{0:<50} {1}\n'.format('mode = tran', '# geno (genome assemblies, DNA) or tran (transcriptome assemblies, DNA) or prot (annotated gene sets, proteins)'))
            file_id.write('{0:<50} {1}\n'.format('evalue = 1e-03', '# E-value cutoff for BLAST searches'))
            file_id.write('{0:<50} {1}\n'.format('limit = 3', '# number of candidate regions to consider'))
            file_id.write('{0:<50} {1}\n'.format('species = NONE', '# identifier of existing Augustus species gene finding parameters or NONE'))
            file_id.write('{0:<50} {1}\n'.format('long = NO', '# Augustus optimization mode for self-training: YES or NO'))
            file_id.write('{0:<50} {1}\n'.format('augustus_options = NONE', '# additional parameters to August or NONE'))
    except:
        error_list.append('*** ERROR: The file {0} can not be recreated'.format(get_busco_config_file()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def run_busco_process(cluster_name, log, function=None):
    '''
    Run a BUSCO process.
    '''

    # initialize the control variable
    OK = True

    # get the BUSCO option dictionary
    busco_option_dict = xlib.get_option_dict(get_busco_config_file())

    # get the experiment identification
    experiment_id = busco_option_dict['identification']['experiment_id']

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # validate the BUSCO config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Validating the {0} config file ...\n'.format(xlib.get_busco_name()))
    (OK, error_list) = validate_busco_config_file(strict=True)
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

    # verify BUSCO is setup
    if OK:
        (OK, error_list, is_setup) = xbioinfoapp.is_setup_bioconda_package(xlib.get_busco_bioconda_code(), cluster_name, True, ssh_client)
        if OK:
            if not is_setup:
                log.write('*** ERROR: {0} is not setup.\n'.format(xlib.get_busco_name()))
                OK = False
        else:
            log.write('*** ERROR: The verification of {0} setup could not be performed.\n'.format(xlib.get_busco_name()))

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # determine the run directory in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Determining the run directory in the cluster ...\n')
        current_run_dir = xlib.get_cluster_current_run_dir(experiment_id, xlib.get_busco_code())
        command = 'mkdir --parents {0}'.format(current_run_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory path is {0}.\n'.format(current_run_dir))
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the BUSCO process script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process script {0} ...\n'.format(get_busco_process_script()))
        (OK, error_list) = build_busco_process_script(cluster_name, current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('*** ERROR: The file could not be built.\n')

    # upload the BUSCO process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process script {0} in the directory {1} of the master ...\n'.format(get_busco_process_script(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_busco_process_script()))
        (OK, error_list) = xssh.put_file(sftp_client, get_busco_process_script(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the BUSCO process script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_busco_process_script())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_busco_process_script()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # build the BUSCO process starter
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the process starter {0} ...\n'.format(get_busco_process_starter()))
        (OK, error_list) = build_busco_process_starter(current_run_dir)
        if OK:
            log.write('The file is built.\n')
        if not OK:
            log.write('***ERROR: The file could not be built.\n')

    # upload the busco process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the process starter {0} in the directory {1} of the master ...\n'.format(get_busco_process_starter(), current_run_dir))
        cluster_path = '{0}/{1}'.format(current_run_dir, os.path.basename(get_busco_process_starter()))
        (OK, error_list) = xssh.put_file(sftp_client, get_busco_process_starter(), cluster_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the BUSCO process starter in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision of {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_busco_process_starter())))
        command = 'chmod u+x {0}/{1}'.format(current_run_dir, os.path.basename(get_busco_process_starter()))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the BUSCO process
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the process script {0}/{1} ...\n'.format(current_run_dir, os.path.basename(get_busco_process_starter())))
        sge_env = xcluster.get_sge_env()
        command = '{0}; qsub -V -b n -cwd {1}/{2}'.format(sge_env, current_run_dir, os.path.basename(get_busco_process_starter()))
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

def validate_busco_config_file(strict):
    '''
    Validate the BUSCO config file of a run.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # intitialize variable used when value is not found
    not_found = '***NOTFOUND***'.upper()

    # get the option dictionary
    try:
        busco_option_dict = xlib.get_option_dict(get_busco_config_file())
    except:
        error_list.append('*** ERROR: The syntax is WRONG.')
        OK = False
    else:

        # get the sections list
        sections_list = []
        for section in busco_option_dict.keys():
            sections_list.append(section)
        sections_list.sort()

        # check section "identification"
        if 'identification' not in sections_list:
            error_list.append('*** ERROR: the section "identification" is not found.')
            OK = False
        else:

            # check section "identification" - key "experiment_id"
            experiment_id = busco_option_dict.get('identification', {}).get('experiment_id', not_found)
            is_experiment_id_OK = True
            if experiment_id == not_found:
                error_list.append('*** ERROR: the key "experiment_id" is not found in the section "identification".')
                is_experiment_id_OK = False
                OK = False

            # check section "identification" - key "assembly_software"
            assembly_software = busco_option_dict.get('identification', {}).get('assembly_software', not_found)
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
            assembly_dataset_id = busco_option_dict.get('identification', {}).get('assembly_dataset_id', not_found)
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
            assembly_type = busco_option_dict.get('identification', {}).get('assembly_type', not_found)
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

        # check section "BUSCO parameters"
        if 'BUSCO parameters' not in sections_list:
            error_list.append('*** ERROR: the section "BUSCO parameters" is not found.')
            OK = False
        else:

            # check section "BUSCO parameters" - key "ncpu"
            ncpu = busco_option_dict.get('BUSCO parameters', {}).get('ncpu', not_found)
            is_ncpu_OK = True
            if ncpu == not_found:
                error_list.append('*** ERROR: the key "ncpu" is not found in the section "BUSCO parameters".')
                is_ncpu_OK = False
                OK = False
            else:
                try:
                    if int(ncpu) < 1:
                        error_list.append('*** ERROR: the key "ncpu" in the section "BUSCO parameters" must be an integer value greater or equal to 1.')
                        is_ncpu_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "ncpu" in the section "BUSCO parameters" must be an integer value greater or equal to 1.')
                    is_ncpu_OK = False
                    OK = False

            # check section "BUSCO parameters" - key "lineage_data"
            lineage_data = busco_option_dict.get('BUSCO parameters', {}).get('lineage_data', not_found)
            is_lineage_data_OK = True
            if lineage_data == not_found:
                error_list.append('*** ERROR: the key "lineage_data" is not found in the section "BUSCO parameters"')
                is_lineage_data_OK = False
                OK = False

            # check section "BUSCO parameters" - key "mode"
            mode = busco_option_dict.get('BUSCO parameters', {}).get('mode', not_found).lower()
            is_mode_OK = True
            if mode == not_found:
                error_list.append('*** ERROR: the key "mode" is not found in the section "BUSCO parameters".')
                is_mode_OK = False
                OK = False
            elif mode not in ['geno', 'tran', 'prot']:
                error_list.append('*** ERROR: the key "mode" value in the section "BUSCO parameters" must be geno or tran or prot.')
                is_mode_OK = False
                OK = False

            # check section "BUSCO parameters" - key "evalue"
            evalue = busco_option_dict.get('BUSCO parameters', {}).get('evalue', not_found)
            is_evalue_OK = True
            if evalue == not_found:
                error_list.append('*** ERROR: the key "evalue" is not found in the section "BUSCO parameters".')
                is_evalue_OK = False
                OK = False
            else:
                try:
                    if float(evalue) <= 0:
                        error_list.append('*** ERROR: the key "evalue" in the section "BUSCO parameters" must be a float value greater than 0.')
                        is_evalue_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "evalue" in the section "BUSCO parameters" must be a float value greater than 0.')
                    is_evalue_OK = False
                    OK = False

            # check section "BUSCO parameters" - key "limit"
            limit = busco_option_dict.get('BUSCO parameters', {}).get('limit', not_found)
            is_limit_OK = True
            if limit == not_found:
                error_list.append('*** ERROR: the key "limit" is not found in the section "BUSCO parameters".')
                OK = False
            else:
                try:
                    if int(limit) < 1:
                        error_list.append('*** ERROR: the key "limit" in the section "BUSCO parameters" must be an integer value greater or equal to 1.')
                        is_limit_OK = False
                        OK = False
                except:
                    error_list.append('*** ERROR: the key "limit" in the section "BUSCO parameters" must be an integer value greater or equal to 1.')
                    is_limit_OK = False
                    OK = False

            # check section "BUSCO parameters" - key "species"
            species = busco_option_dict.get('BUSCO parameters', {}).get('species', not_found)
            is_species_OK = True
            if species == not_found:
                error_list.append('*** ERROR: the key "species" is not found in the section "BUSCO parameters"')
                is_species_OK = False
                OK = False

            # check section "BUSCO parameters" - key "long"
            long = busco_option_dict.get('BUSCO parameters', {}).get('long', not_found).upper()
            is_long_OK = True
            if long == not_found:
                error_list.append('*** ERROR: the key "long" is not found in the section "BUSCO parameters".')
                is_long_OK = False
                OK = False
            elif long not in ['YES', 'NO']:
                error_list.append('*** ERROR: the key "long" value in the section "BUSCO parameters" must be YES or NO.')
                is_long_OK = False
                OK = False

            # check section "BUSCO parameters" - key "augustus_options"
            augustus_options = busco_option_dict.get('BUSCO parameters', {}).get('augustus_options', not_found)
            is_augustus_options_OK = True
            if augustus_options == not_found:
                error_list.append('*** ERROR: the key "augustus_options" is not found in the section "BUSCO parameters".')
                is_augustus_options_OK = False
                OK = False
            else:
                if augustus_options.upper() != 'NONE':
                    parameter_list = [x.strip() for x in augustus_options.split(';')]
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
                            error_list.append('*** ERROR: the value of the key "augustus_options" in the section "BUSCO parameters" must be NONE or a valid August parameter list.')
                            is_augustus_options_OK = False
                            OK = False
                            break

    # warn that the results config file is not valid if there are any errors
    if not OK:
        error_list.append('\nThe {0} config file is not valid. Please, correct this file or recreate it.'.format(xlib.get_busco_name()))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_busco_process_script(cluster_name, current_run_dir):
    '''
    Build the current BUSCO process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the BUSCO option dictionary
    busco_option_dict = xlib.get_option_dict(get_busco_config_file())

    # get the options
    experiment_id = busco_option_dict['identification']['experiment_id']
    assembly_software = busco_option_dict['identification']['assembly_software']
    assembly_dataset_id = busco_option_dict['identification']['assembly_dataset_id']
    assembly_type = busco_option_dict['identification']['assembly_type']
    ncpu = busco_option_dict['BUSCO parameters']['ncpu']
    lineage_data = busco_option_dict['BUSCO parameters']['lineage_data']
    lineage_data_file = '{0}.tar.gz'.format(lineage_data)
    lineage_data_url = 'http://busco.ezlab.org/v2/datasets/{0}'.format(lineage_data_file)
    mode = busco_option_dict['BUSCO parameters']['mode'].lower()
    evalue = busco_option_dict['BUSCO parameters']['evalue']
    limit = busco_option_dict['BUSCO parameters']['limit']
    species = busco_option_dict['BUSCO parameters']['species']
    long = busco_option_dict['BUSCO parameters']['long'].upper()
    augustus_options = busco_option_dict['BUSCO parameters']['augustus_options'].upper()

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

    # write the BUSCO process script
    try:
        if not os.path.exists(os.path.dirname(get_busco_process_script())):
            os.makedirs(os.path.dirname(get_busco_process_script()))
        with open(get_busco_process_script(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('BUSCO_PATH={0}/{1}/envs/{2}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name(), xlib.get_busco_bioconda_code())))
            file_id.write('{0}\n'.format('export PATH=$BUSCO_PATH:$PATH'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('cd {0}/{1}/bin'.format(xlib.get_cluster_app_dir(), xlib.get_miniconda3_name())))
            file_id.write('{0}\n'.format('source activate {0}'.format(xlib.get_busco_bioconda_code())))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function download_lineage_data'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Downloading lineage data ..."'))
            file_id.write('{0}\n'.format('    wget --quiet --output-document ./{0} {1}'.format(lineage_data_file, lineage_data_url)))
            file_id.write('{0}\n'.format('    tar -xzvf ./{0}'.format(lineage_data_file)))
            file_id.write('{0}\n'.format('    rm ./{0}'.format(lineage_data_file)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function run_busco_process'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    cd {0}'.format(current_run_dir)))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    run_BUSCO.py --version'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    /usr/bin/time \\'))
            file_id.write('{0}\n'.format('        --format="$SEP\\nElapsed real time (s): %e\\nCPU time in kernel mode (s): %S\\nCPU time in user mode (s): %U\\nPercentage of CPU: %P\\nMaximum resident set size(Kb): %M\\nAverage total memory use (Kb):%K" \\'))
            file_id.write('{0}\n'.format('        run_BUSCO.py \\'))
            file_id.write('{0}\n'.format('            --cpu={0} \\'.format(ncpu)))
            file_id.write('{0}\n'.format('            --lineage_path=./{0} \\'.format(lineage_data)))
            file_id.write('{0}\n'.format('            --mode={0} \\'.format(mode)))
            file_id.write('{0}\n'.format('            --evalue={0} \\'.format(evalue)))
            file_id.write('{0}\n'.format('            --limit={0} \\'.format(limit)))
            if species.upper() != 'NONE':
                file_id.write('{0}\n'.format('            --species={0} \\'.format(species)))
            if long == 'YES':
                file_id.write('{0}\n'.format('            --long \\'))
            if augustus_options.upper() != 'NONE':
                file_id.write('{0}\n'.format("            --august_options='{0}' \\".format(augustus_options)))
            file_id.write('{0}\n'.format('            --in={0} \\'.format(transcriptome_file)))
            file_id.write('{0}\n'.format('            --out={0}'.format(os.path.basename(current_run_dir))))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error run_BUSCO.py $RC; fi'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_busco_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_busco_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: {1} process"'.format(xlib.get_project_name(), xlib.get_busco_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The {0} process in node $HOSTNAME of cluster {1} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION). Please review its log.<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(xlib.get_busco_name(), cluster_name)))
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
            file_id.write('{0}\n'.format('download_lineage_data'))
            file_id.write('{0}\n'.format('run_busco_process'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_busco_process_script()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def build_busco_process_starter(current_run_dir):
    '''
    Build the starter of the current BUSCO process.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # write the BUSCO process starter
    try:
        if not os.path.exists(os.path.dirname(get_busco_process_starter())):
            os.makedirs(os.path.dirname(get_busco_process_starter()))
        with open(get_busco_process_starter(), mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('{0}/{1} &>{0}/{2}'.format(current_run_dir, os.path.basename(get_busco_process_script()), xlib.get_cluster_log_file())))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(get_busco_process_starter()))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_busco_config_file():
    '''
    Get the BUSCO config file path.
    '''

    # assign the BUSCO config file path
    busco_config_file = '{0}/{1}-config.txt'.format(xlib.get_config_dir(), xlib.get_busco_code())

    # return the BUSCO config file path
    return busco_config_file

#-------------------------------------------------------------------------------

def get_busco_process_script():
    '''
    Get the BUSCO process script path in the local computer.
    '''

    # assign the BUSCO script path
    busco_process_script = '{0}/{1}-process.sh'.format(xlib.get_temp_dir(), xlib.get_busco_code())

    # return the BUSCO script path
    return busco_process_script

#-------------------------------------------------------------------------------

def get_busco_process_starter():
    '''
    Get the BUSCO process starter path in the local computer.
    '''

    # assign the BUSCO process starter path
    busco_process_starter = '{0}/{1}-process-starter.sh'.format(xlib.get_temp_dir(), xlib.get_busco_code())

    # return the BUSCO starter path
    return busco_process_starter

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains functions related to the BUSCO process used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
