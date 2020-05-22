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
This file contains the functions related to forms corresponding to dataset
menu items in mode console.
'''

#-------------------------------------------------------------------------------

import os
import sys

import cinputs
import clib
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def form_list_cluster_experiment_processes():
    '''
    List the processes of an experiment in the cluster.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Logs - List experiment processes in the cluster')

    # get the cluster name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) != []:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)
    else:
        print('WARNING: There is not any running cluster.')
        OK = False

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the result dataset list of the experiment
    if OK:
        command = 'cd  {0}/{1}; for list in `ls`; do ls -ld $list | grep -v ^- > /dev/null && echo $list; done;'.format(xlib.get_cluster_result_dir(), experiment_id)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            result_dataset_id_list = []
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    result_dataset_id_list.append(line)

    # print the result dataset identification list of the experiment
    if OK:
        print(xlib.get_separator())
        if result_dataset_id_list == []:
            print('*** WARNING: There is not any result dataset of the experiment {0}.'.format(experiment_id))
        else:
            result_dataset_id_list.sort()
            # set data width
            result_dataset_width = 25
            bioinfo_app_width = 25
            # set line template
            line_template = '{0:' + str(result_dataset_width) + '}   {1:' + str(bioinfo_app_width) + '}'
            # print header
            print(line_template.format('Result dataset', 'Bioinfo app / Utility'))
            print(line_template.format('=' * result_dataset_width, '=' * bioinfo_app_width))
            # print detail lines
            for result_dataset_id in result_dataset_id_list:
                if result_dataset_id.startswith(xlib.get_bedtools_code()+'-'):
                    bioinfo_app_name = xlib.get_bedtools_name()
                elif result_dataset_id.startswith(xlib.get_blastplus_code()+'-'):
                    bioinfo_app_name = xlib.get_blastplus_name()
                elif result_dataset_id.startswith(xlib.get_bowtie2_code()+'-'):
                    bioinfo_app_name = xlib.get_bowtie2_name()
                elif result_dataset_id.startswith(xlib.get_busco_code()+'-'):
                    bioinfo_app_name = xlib.get_busco_name()
                elif result_dataset_id.startswith(xlib.get_cd_hit_code()+'-'):
                    bioinfo_app_name = xlib.get_cd_hit_est_name()
                elif result_dataset_id.startswith(xlib.get_cd_hit_code()+'-'):
                    bioinfo_app_name = xlib.get_cd_hit_est_name()
                elif result_dataset_id.startswith(xlib.get_detonate_code()+'-'):
                    bioinfo_app_name = xlib.get_detonate_name()
                elif result_dataset_id.startswith(xlib.get_emboss_code()+'-'):
                    bioinfo_app_name = xlib.get_emboss_name()
                elif result_dataset_id.startswith(xlib.get_fastqc_code()+'-'):
                    bioinfo_app_name = xlib.get_fastqc_name()
                elif result_dataset_id.startswith(xlib.get_gmap_code()+'-'):
                    bioinfo_app_name = xlib.get_gmap_name()
                elif result_dataset_id.startswith(xlib.get_gmap_gsnap_code()+'-'):
                    bioinfo_app_name = xlib.get_gmap_gsnap_name()
                elif result_dataset_id.startswith(xlib.get_gzip_code()+'-'):
                    bioinfo_app_name = xlib.get_gzip_name()
                elif result_dataset_id.startswith(xlib.get_insilico_read_normalization_code()+'-'):
                    bioinfo_app_name = xlib.get_insilico_read_normalization_name()
                elif result_dataset_id.startswith(xlib.get_miniconda3_code()+'-'):
                    bioinfo_app_name = xlib.get_miniconda3_name()
                elif result_dataset_id.startswith(xlib.get_ngshelper_code()+'-'):
                    bioinfo_app_name = xlib.get_ngshelper_name()
                elif result_dataset_id.startswith(xlib.get_quast_code()+'-'):
                    bioinfo_app_name = xlib.get_quast_name()
                elif result_dataset_id.startswith(xlib.get_r_code()+'-'):
                    bioinfo_app_name = xlib.get_r_name()
                elif result_dataset_id.startswith(xlib.get_ref_eval_code()+'-'):
                    bioinfo_app_name = xlib.get_ref_eval_name()
                elif result_dataset_id.startswith(xlib.get_rnaquast_code()+'-'):
                    bioinfo_app_name = xlib.get_rnaquast_name()
                elif result_dataset_id.startswith(xlib.get_rsem_code()+'-'):
                    bioinfo_app_name = xlib.get_rsem_name()
                elif result_dataset_id.startswith(xlib.get_rsem_eval_code()+'-'):
                    bioinfo_app_name = xlib.get_rsem_eval_name()
                elif result_dataset_id.startswith(xlib.get_samtools_code()+'-'):
                    bioinfo_app_name = xlib.get_samtools_name()
                elif result_dataset_id.startswith(xlib.get_soapdenovotrans_code()+'-'):
                    bioinfo_app_name = xlib.get_soapdenovotrans_name()
                elif result_dataset_id.startswith(xlib.get_star_code()+'-'):
                    bioinfo_app_name = xlib.get_star_name()
                elif result_dataset_id.startswith(xlib.get_transabyss_code()+'-'):
                    bioinfo_app_name = xlib.get_transabyss_name()
                elif result_dataset_id.startswith(xlib.get_transcript_filter_code()+'-'):
                    bioinfo_app_name = xlib.get_transcript_filter_name()
                elif result_dataset_id.startswith(xlib.get_transcriptome_blastx_code()+'-'):
                    bioinfo_app_name = xlib.get_transcriptome_blastx_name()
                elif result_dataset_id.startswith(xlib.get_transrate_code()+'-'):
                    bioinfo_app_name = xlib.get_transrate_name()
                elif result_dataset_id.startswith(xlib.get_trimmomatic_code()+'-'):
                    bioinfo_app_name = xlib.get_trimmomatic_name()
                elif result_dataset_id.startswith(xlib.get_trinity_code()+'-'):
                    bioinfo_app_name = xlib.get_trinity_name()
                else:
                    bioinfo_app_name = 'xxx'
                print(line_template.format(result_dataset_id, bioinfo_app_name))

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_view_cluster_experiment_process_log():
    '''
    View the log of an experiment process in the cluster.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Logs - View an experiment process log in the cluster')

    # get the clustner name
    if OK:
        print(xlib.get_separator())
        if xec2.get_running_cluster_list(volume_creator_included=False) != []:
            cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)
        else:
            print('WARNING: There is not any running cluster.')
            OK = False

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # create the SSH transport connection
    if OK:
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # create the SFTP client 
    if OK:
        sftp_client = xssh.create_sftp_client(ssh_transport)

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster has not experiment data.')
            OK = False

    # get the result_dataset identification
    if OK:
        result_dataset_id = cinputs.input_result_dataset_id('uncompressed', ssh_client, experiment_id, help=True)
        if result_dataset_id == '':
            print('WARNING: The experiment {0} has not result datasets.'.format(experiment_id))
            OK = False

    # create the local path
    if not os.path.exists(xlib.get_temp_dir()):
        os.makedirs(xlib.get_temp_dir())

    # get the log file name and build local and cluster paths
    if OK:
        log_file = xlib.get_cluster_log_file()
        local_path = '{0}/{1}'.format(xlib.get_temp_dir(), log_file)
        cluster_path = '{0}/{1}/{2}'.format(xlib.get_cluster_experiment_result_dir(experiment_id), result_dataset_id, log_file)

    # download the log file from the cluster
    if OK:
        print(xlib.get_separator())
        print('The file {0} is being downloaded from {1} ...'.format(log_file, cluster_path))
        OK = xssh.get_file(sftp_client, cluster_path, local_path)
        if OK:
            print('The file has been uploaded.')

    # close the SSH transport connection
    if OK:
        xssh.close_ssh_transport_connection(ssh_transport)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)
    
    # view the log file
    if OK:
        text = 'Logs - View an experiment process log in the cluster'
        OK = clib.view_file(local_path, text)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains the functions related to forms corresponding to dataset menu items in mode console.')
     sys.exit(0)

#-------------------------------------------------------------------------------
