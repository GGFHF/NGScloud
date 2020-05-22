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
This file contains the functions related to forms corresponding BioInfo application
menu items in console mode.
'''

#-------------------------------------------------------------------------------

import subprocess
import sys

import cinputs
import clib
import xbioinfoapp
import xbusco
import xcdhit
import xconfiguration
import xdetonate
import xec2
import xfastqc
import xgmap
import xlib
import xngshelper
import xquast
import xrnaquast
import xsoapdenovotrans
import xstar
import xtransabyss
import xtransrate
import xtrimmomatic
import xtrinity
import xssh

#-------------------------------------------------------------------------------

def form_setup_bioinfo_app(app_code):
    '''
    Set up the bioinfo application software in the cluster.
    '''

    # initialize the control variable
    OK = True

    # set the bioinfo application name
    if app_code == xlib.get_bedtools_code():
        app_name = xlib.get_bedtools_name()
    elif app_code == xlib.get_blastplus_code():
        app_name = xlib.get_blastplus_name()
    elif app_code == xlib.get_bowtie2_code():
        app_name = xlib.get_bowtie2_name()
    elif app_code == xlib.get_busco_code():
        app_name = xlib.get_busco_name()
    elif app_code == xlib.get_cd_hit_code():
        app_name = xlib.get_cd_hit_name()
    elif app_code == xlib.get_detonate_code():
        app_name = xlib.get_detonate_name()
    elif app_code == xlib.get_emboss_code():
        app_name = xlib.get_emboss_name()
    elif app_code == xlib.get_fastqc_code():
        app_name = xlib.get_fastqc_name()
    elif app_code == xlib.get_gmap_gsnap_code():
        app_name = xlib.get_gmap_gsnap_name()
    elif app_code == xlib.get_miniconda3_code():
        app_name = xlib.get_miniconda3_name()
    elif app_code == xlib.get_ngshelper_code():
        app_name = xlib.get_ngshelper_name()
    elif app_code == xlib.get_quast_code():
        app_name = xlib.get_quast_name()
    elif app_code == xlib.get_r_code():
        app_name = xlib.get_r_name()
    elif app_code == xlib.get_rnaquast_code():
        app_name = xlib.get_rnaquast_name()
    elif app_code == xlib.get_rsem_code():
        app_name = xlib.get_rsem_name()
    elif app_code == xlib.get_samtools_code():
        app_name = xlib.get_samtools_name()
    elif app_code == xlib.get_soapdenovotrans_code():
        app_name = xlib.get_soapdenovotrans_name()
    elif app_code == xlib.get_star_code():
        app_name = xlib.get_star_name()
    elif app_code == xlib.get_transabyss_code():
        app_name = xlib.get_transabyss_name()
    elif app_code == xlib.get_transrate_code():
        app_name = xlib.get_transrate_name()
    elif app_code == xlib.get_trimmomatic_code():
        app_name = xlib.get_trimmomatic_name()
    elif app_code == xlib.get_trinity_code():
        app_name = xlib.get_trinity_name()

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Set up software'.format(app_name))

    # get the cluster name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # confirm the software set up
    if OK:
        print(xlib.get_separator())
        if app_code == xlib.get_miniconda3_code():
            OK = clib.confirm_action('{0} (Python & Bioconda environments) is going to be set up in the cluster {1}. All Bioconda packages previously set up will be lost and they must be reinstalled.'.format(app_name, cluster_name))
        elif app_code == xlib.get_r_code():
            OK = clib.confirm_action('{0} and analysis packages are going to be set up in the cluster {1}. The previous version will be lost, if it exists.'.format(app_name, cluster_name))
        elif app_code in [xlib.get_ngshelper_code(), xlib.get_rnaquast_code(), xlib.get_transrate_code()]:
            OK = clib.confirm_action('{0} is going to be set up in the cluster {1}. The previous version will be lost, if it exists.'.format(app_name, cluster_name))
        else:
            OK = clib.confirm_action('The {0} Bioconda/Conda package is going to be set up in the cluster {1}. The previous version will be lost, if it exists.'.format(app_name, cluster_name))

    # set up the software
    if OK:

        # set up the BEDtools software
        if app_code == xlib.get_bedtools_code():
            package_code_list = [xlib.get_bedtools_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the BLAST+ software
        elif app_code == xlib.get_blastplus_code():
            package_code_list = [xlib.get_blastplus_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the Bowtie2 software
        elif app_code == xlib.get_bowtie2_code():
            package_code_list = [xlib.get_bowtie2_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the BUSCO software
        elif app_code == xlib.get_busco_code():
            package_code_list = [xlib.get_busco_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the CD-HIT software
        elif app_code == xlib.get_cd_hit_code():
            package_code_list = [xlib.get_cd_hit_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the DETONATE software
        elif app_code == xlib.get_detonate_code():
            package_code_list = [xlib.get_detonate_bioconda_code(), xlib.get_bowtie2_bioconda_code(), xlib.get_rsem_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the EMBOSS software
        elif app_code == xlib.get_emboss_code():
            package_code_list = [xlib.get_emboss_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the FastQC software
        elif app_code == xlib.get_fastqc_code():
            package_code_list = [xlib.get_fastqc_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the GMAP-GSNAP software
        elif app_code == xlib.get_gmap_gsnap_code():
            package_code_list = [xlib.get_gmap_gsnap_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the Miniconda3 software
        elif app_code == xlib.get_miniconda3_code():
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_miniconda3.__name__)
            OK = xbioinfoapp.setup_miniconda3(cluster_name, devstdout, function=None)

        # set up the NGShelper software
        elif app_code == xlib.get_ngshelper_code():
            devstdout = xlib.DevStdOut(xngshelper.setup_ngshelper.__name__)
            OK = xngshelper.setup_ngshelper(cluster_name, devstdout, function=None)

        # set up the QUAST software
        elif app_code == xlib.get_quast_code():
            package_code_list = [xlib.get_quast_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up R and analysis packages
        elif app_code == xlib.get_r_code():
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_r.__name__)
            OK = xbioinfoapp.setup_r(cluster_name, devstdout, function=None)

        # set up the rnaQUAST software
        elif app_code == xlib.get_rnaquast_code():
            devstdout = xlib.DevStdOut(xrnaquast.setup_rnaquast.__name__)
            OK = xrnaquast.setup_rnaquast(cluster_name, devstdout, function=None)

        # set up the RSEM software
        elif app_code == xlib.get_rsem_code():
            package_code_list = [xlib.get_rsem_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the SAMtools software
        if app_code == xlib.get_samtools_code():
            package_code_list = [xlib.get_samtools_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the SOAPdenovo-Trans software
        elif app_code == xlib.get_soapdenovotrans_code():
            package_code_list = [xlib.get_soapdenovotrans_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the STAR software
        elif app_code == xlib.get_star_code():
            package_code_list = [xlib.get_star_bioconda_code(), xlib.get_trinity_bioconda_code(), xlib.get_bowtie2_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the Trans-ABySS software
        elif app_code == xlib.get_transabyss_code():
            package_code_list = [xlib.get_transabyss_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the Transrate software
        elif app_code == xlib.get_transrate_code():
            devstdout = xlib.DevStdOut(xtransrate.setup_transrate.__name__)
            OK = xtransrate.setup_transrate(cluster_name, devstdout, function=None)

        # set up the Trimmomatic software
        elif app_code == xlib.get_trimmomatic_code():
            package_code_list = [xlib.get_trimmomatic_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

        # set up the Trinity software
        elif app_code == xlib.get_trinity_code():
            package_code_list = [xlib.get_trinity_bioconda_code(), xlib.get_bowtie2_bioconda_code()]
            devstdout = xlib.DevStdOut(xbioinfoapp.setup_bioconda_package_list.__name__)
            OK = xbioinfoapp.setup_bioconda_package_list(app_code, app_name, package_code_list, cluster_name, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_busco_config_file():
    '''
    Recreate the BUSCO config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_busco_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the assembly dataset identification
    if OK:
        assembly_dataset_id = cinputs.input_assembly_dataset_id(ssh_client, experiment_id, help=True)
        if assembly_dataset_id == '':
            print('WARNING: The cluster {0} has not assembly datasets.'.format(cluster_name))
            OK = False

    # get the assembly type
    if OK:
        if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            assembly_type = cinputs.input_assembly_type(help=True)
        elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            assembly_type = 'NONE'

    # recreate the BUSCO config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xbusco.get_busco_config_file()))

        # recreate the config file
        if OK:
            (OK, error_list) = xbusco.create_busco_config_file(experiment_id, assembly_dataset_id, assembly_type)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_cd_hit_est_config_file():
    '''
    Recreate the CD-HIT-EST config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_cd_hit_est_name()))

    # get the cluster name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the assembly dataset identification
    if OK:
        assembly_dataset_id = cinputs.input_assembly_dataset_id(ssh_client, experiment_id, help=True)
        if assembly_dataset_id == '':
            print('WARNING: The cluster {0} has not assembly datasets.'.format(cluster_name))
            OK = False

    # get the assembly type
    if OK:
        if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            assembly_type = cinputs.input_assembly_type(help=True)
        elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            assembly_type = 'NONE'

    # recreate the CD-HIT-EST config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xcdhit.get_cd_hit_est_config_file()))

        # recreate the config file
        if OK:
            (OK, error_list) = xcdhit.create_cd_hit_est_config_file(experiment_id, assembly_dataset_id, assembly_type)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_fastqc_config_file():
    '''
    Recreate the FastQC config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_fastqc_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # create the FastQC config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xfastqc.get_fastqc_config_file()))

        # recreate the config file
        if OK:
            (OK, error_list) = xfastqc.create_fastqc_config_file(experiment_id, read_dataset_id, selected_file_list)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_gmap_config_file():
    '''
    Recreate the GMAP config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_gmap_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the reference dataset identification
    if OK:
        reference_dataset_id = cinputs.input_reference_dataset_id(ssh_client, allowed_none=False, help=True)
        if reference_dataset_id == '':
            print('WARNING: The cluster {0} has not reference datasets. NONE is assumed as value.'.format(cluster_name))
            OK = False

    # get the reference file
    if OK:
        reference_file = cinputs.input_reference_file(ssh_client, reference_dataset_id, help=True)
        if reference_file == '':
            print('WARNING: The reference dataset {0} has not reference files.'.format(reference_dataset_id))
            OK = False

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the assembly dataset identification
    if OK:
        assembly_dataset_id = cinputs.input_assembly_dataset_id(ssh_client, experiment_id, help=True)
        if assembly_dataset_id == '':
            print('WARNING: The cluster {0} has not assembly datasets.'.format(cluster_name))
            OK = False

    # get the assembly type
    if OK:
        if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            assembly_type = cinputs.input_assembly_type(help=True)
        elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            assembly_type = 'NONE'

    # recreate the GAMP config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xgmap.get_gmap_config_file()))

        # recreate the config file
        if OK:
            (OK, error_list) = xgmap.create_gmap_config_file(experiment_id, reference_dataset_id, reference_file, assembly_dataset_id, assembly_type)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_insilico_read_normalization_config_file():
    '''
    Recreate the insilico_read_normalization config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_insilico_read_normalization_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # recreate the insilico_read_normalization config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xtrinity.get_insilico_read_normalization_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xtrinity.create_insilico_read_normalization_config_file(experiment_id, read_dataset_id, read_type, selected_file_list, None)
            elif read_type == 'PE':
                (OK, error_list) = xtrinity.create_insilico_read_normalization_config_file(experiment_id, read_dataset_id, read_type, file_1_list, file_2_list)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_quast_config_file():
    '''
    Recreate the QUAST config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_quast_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the reference dataset identification
    if OK:
        reference_dataset_id = cinputs.input_reference_dataset_id(ssh_client, allowed_none=True, help=True)
        if reference_dataset_id == '':
            reference_dataset_id = 'NONE'
            print('WARNING: The cluster {0} has not reference datasets. NONE is assumed as value.'.format(cluster_name))

    # get the reference file
    if OK:
        if reference_dataset_id.upper() != 'NONE':
            reference_file = cinputs.input_reference_file(ssh_client, reference_dataset_id, help=True)
            if reference_file == '':
                print('WARNING: The reference dataset {0} has not reference files.'.format(reference_dataset_id))
                OK = False
        else:
            reference_file = 'NONE'

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the assembly dataset identification
    if OK:
        assembly_dataset_id = cinputs.input_assembly_dataset_id(ssh_client, experiment_id, help=True)
        if assembly_dataset_id == '':
            print('WARNING: The cluster {0} has not assembly datasets.'.format(cluster_name))
            OK = False

    # get the assembly type
    if OK:
        if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            assembly_type = cinputs.input_assembly_type(help=True)
        elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            assembly_type = 'NONE'

    # recreate the QUAST config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xquast.get_quast_config_file()))

        # recreate the config file
        if OK:
            (OK, error_list) = xquast.create_quast_config_file(experiment_id, reference_dataset_id, reference_file, assembly_dataset_id, assembly_type)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_ref_eval_config_file():
    '''
    Recreate the REF-EVAL config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_ref_eval_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the reference dataset identification
    if OK:
        reference_dataset_id = cinputs.input_reference_dataset_id(ssh_client, allowed_none=False, help=True)
        if reference_dataset_id == '':
            print('WARNING: The cluster {0} has not reference datasets.'.format(cluster_name))
            OK = False

    # get the reference file
    if OK:
        reference_file = cinputs.input_reference_file(ssh_client, reference_dataset_id, help=True)
        if reference_file == '':
            print('WARNING: The reference dataset {0} has not reference files.'.format(reference_dataset_id))
            OK = False

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # get the assembly dataset identification
    if OK:
        assembly_dataset_id = cinputs.input_assembly_dataset_id(ssh_client, experiment_id, help=True)
        if assembly_dataset_id == '':
            print('WARNING: The cluster {0} has not assembly datasets.'.format(cluster_name))
            OK = False

    # get the assembly type
    if OK:
        if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            assembly_type = cinputs.input_assembly_type(help=True)
        elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            assembly_type = 'NONE'

    # recreate the REF-EVAL config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xdetonate.get_ref_eval_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xdetonate.create_ref_eval_config_file(experiment_id, read_dataset_id, read_type, selected_file_list, None, assembly_dataset_id, assembly_type)
            elif read_type == 'PE':
                (OK, error_list) = xdetonate.create_ref_eval_config_file(experiment_id, read_dataset_id, read_type, file_1_list, file_2_list, assembly_dataset_id, assembly_type)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_rnaquast_config_file():
    '''
    Recreate the rnaQUAST config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_rnaquast_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the reference dataset identification
    if OK:
        reference_dataset_id = cinputs.input_reference_dataset_id(ssh_client, allowed_none=True, help=True)
        if reference_dataset_id == '':
            reference_dataset_id = 'NONE'
            print('WARNING: The cluster {0} has not reference datasets. NONE is assumed as value.'.format(cluster_name))

    # get the reference file
    if OK:
        if reference_dataset_id.upper() != 'NONE':
            reference_file = cinputs.input_reference_file(ssh_client, reference_dataset_id, help=True)
            if reference_file == '':
                print('WARNING: The reference dataset {0} has not reference files.'.format(reference_dataset_id))
                OK = False
        else:
            reference_file = 'NONE'

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # get the assembly dataset identification
    if OK:
        assembly_dataset_id = cinputs.input_assembly_dataset_id(ssh_client, experiment_id, help=True)
        if assembly_dataset_id == '':
            print('WARNING: The cluster {0} has not assembly datasets.'.format(cluster_name))
            OK = False

    # get the assembly type
    if OK:
        if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            assembly_type = cinputs.input_assembly_type(help=True)
        elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            assembly_type = 'NONE'

    # recreate the rnaQUAST config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xrnaquast.get_rnaquast_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xrnaquast.create_rnaquast_config_file(experiment_id, reference_dataset_id, reference_file, cluster_read_dir, read_type, selected_file_list, None, assembly_dataset_id, assembly_type)
            elif read_type == 'PE':
                (OK, error_list) = xrnaquast.create_rnaquast_config_file(experiment_id, reference_dataset_id, reference_file, cluster_read_dir, read_type, file_1_list, file_2_list, assembly_dataset_id, assembly_type)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_rsem_eval_config_file():
    '''
    Recreate the RSEM-EVAL config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_ref_eval_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # get the assembly dataset identification
    if OK:
        assembly_dataset_id = cinputs.input_assembly_dataset_id(ssh_client, experiment_id, help=True)
        if assembly_dataset_id == '':
            print('WARNING: The cluster {0} has not assembly datasets.'.format(cluster_name))
            OK = False

    # get the assembly type
    if OK:
        if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            assembly_type = cinputs.input_assembly_type(help=True)
        elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            assembly_type = 'NONE'

    # recreate the RSEM-EVAL config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xdetonate.get_rsem_eval_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xdetonate.create_rsem_eval_config_file(experiment_id, read_dataset_id, read_type, selected_file_list, None, assembly_dataset_id, assembly_type)
            elif read_type == 'PE':
                (OK, error_list) = xdetonate.create_rsem_eval_config_file(experiment_id, read_dataset_id, read_type, file_1_list, file_2_list, assembly_dataset_id, assembly_type)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_soapdenovotrans_config_file():
    '''
    Recreate the SOAPdenovo-Trans application config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_soapdenovotrans_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # recreate the SOAPdenovo-Trans config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xsoapdenovotrans.get_soapdenovotrans_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xsoapdenovotrans.create_soapdenovotrans_config_file(experiment_id, read_dataset_id, read_type, selected_file_list, None)
            elif read_type == 'PE':
                (OK, error_list) = xsoapdenovotrans.create_soapdenovotrans_config_file(experiment_id, read_dataset_id, read_type, file_1_list, file_2_list)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_star_config_file():
    '''
    Recreate the STAR config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_star_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the reference dataset identification
    if OK:
        reference_dataset_id = cinputs.input_reference_dataset_id(ssh_client, allowed_none=False, help=True)
        if reference_dataset_id == '':
            print('ERROR: The cluster {0} has not reference datasets.'.format(cluster_name))
            OK = False

    # get the reference file
    if OK:
        reference_file = cinputs.input_reference_file(ssh_client, reference_dataset_id, help=True)
        if reference_file == '':
            print('ERROR: The reference dataset {0} has not reference files.'.format(reference_dataset_id))
            OK = False

    # get the GTF file
    if OK:
        gtf_file = cinputs.input_gtf_file(ssh_client, reference_dataset_id, help=True)
        if gtf_file == '':
            print('ERROR: The reference dataset {0} has not GTF files.'.format(reference_dataset_id))
            OK = False

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('ERROR: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('ERROR: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('ERROR: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # verify there is only one library
    if OK:
        if read_type == 'SE' and len(selected_file_list) != 1 or read_type == 'PE' and len(file_1_list) != 1:
            print('ERROR: Two or more libraries are selected and only one is allowed.')
            OK = False

    # recreate the STAR config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xstar.get_star_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xstar.create_star_config_file(experiment_id, reference_dataset_id, reference_file, gtf_file, read_dataset_id, read_type, selected_file_list[0], None)
            elif read_type == 'PE':
                (OK, error_list) = xstar.create_star_config_file(experiment_id, reference_dataset_id, reference_file, gtf_file, read_dataset_id, read_type, file_1_list[0], file_2_list[0])
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_transabyss_config_file():
    '''
    Recreate the Trans-ABySS config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_transabyss_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # recreate the Trans-ABySS config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xtransabyss.get_transabyss_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xtransabyss.create_transabyss_config_file(experiment_id, read_dataset_id, read_type, selected_file_list, None)
            elif read_type == 'PE':
                (OK, error_list) = xtransabyss.create_transabyss_config_file(experiment_id, read_dataset_id, read_type, file_1_list, file_2_list)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_transcript_filter_config_file():
    '''
    Recreate the transcript-filter config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_transcript_filter_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the RSEM-EVAL dataset identification
    if OK:
        rsem_eval_dataset_id = cinputs.input_rsem_eval_dataset_id(ssh_client, experiment_id, help=True)
        if rsem_eval_dataset_id == '':
            print('WARNING: The cluster {0} has not RSEM-EVAL datasets.'.format(cluster_name))
            OK = False

    # recreate the transcripts-filter config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xngshelper.get_transcript_filter_config_file()))

        # recreate the config file
        if OK:
            (OK, error_list) = xngshelper.create_transcript_filter_config_file(experiment_id, rsem_eval_dataset_id)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_transcriptome_blastx_config_file():
    '''
    Recreate the transcriptome-blastx config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_transcriptome_blastx_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the database dataset identification
    if OK:
        database_dataset_id = cinputs.input_database_dataset_id(ssh_client, help=True)
        if database_dataset_id == '':
            print('WARNING: The cluster {0} has not any database dataset.'.format(cluster_name))
            OK = False

    # get the protein database name
    if OK:
        protein_database_name = cinputs.input_protein_database_name(ssh_client, database_dataset_id, help=True)
        if protein_database_name == '':
            print('WARNING: The dataset {0} in the cluster {1} has not any protein database.'.format(database_dataset_id, cluster_name))
            OK = False

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the assembly dataset identification
    if OK:
        assembly_dataset_id = cinputs.input_assembly_dataset_id(ssh_client, experiment_id, help=True)
        if assembly_dataset_id == '':
            print('WARNING: The cluster {0} has not assembly datasets.'.format(cluster_name))
            OK = False

    # get the assembly type
    if OK:
        if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            assembly_type = cinputs.input_assembly_type(help=True)
        elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            assembly_type = 'NONE'

    # recreate the transcriptome-blastx config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xngshelper.get_transcriptome_blastx_config_file()))

        # recreate the config file
        if OK:
            (OK, error_list) = xngshelper.create_transcriptome_blastx_config_file(database_dataset_id, protein_database_name, experiment_id, assembly_dataset_id, assembly_type)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_transrate_config_file():
    '''
    Recreate the Transrate config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_transrate_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the reference dataset identification
    if OK:
        reference_dataset_id = cinputs.input_reference_dataset_id(ssh_client, allowed_none=True, help=True)
        if reference_dataset_id == '':
            reference_dataset_id = 'NONE'
            print('WARNING: The cluster {0} has not reference datasets. NONE is assumed as value.'.format(cluster_name))

    # get the reference file
    if OK:
        if reference_dataset_id.upper() != 'NONE':
            reference_file = cinputs.input_reference_file(ssh_client, reference_dataset_id, help=True)
            if reference_file == '':
                print('WARNING: The reference dataset {0} has not reference files.'.format(reference_dataset_id))
                OK = False
        else:
            reference_file = 'NONE'

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # get the assembly dataset identification
    if OK:
        assembly_dataset_id = cinputs.input_assembly_dataset_id(ssh_client, experiment_id, help=True)
        if assembly_dataset_id == '':
            print('WARNING: The cluster {0} has not assembly datasets.'.format(cluster_name))
            OK = False

    # get the assembly type
    if OK:
        if assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            assembly_type = cinputs.input_assembly_type(help=True)
        elif assembly_dataset_id.startswith(xlib.get_transabyss_code()) or assembly_dataset_id.startswith(xlib.get_trinity_code()) or assembly_dataset_id.startswith(xlib.get_star_code()) or assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            assembly_type = 'NONE'

    # recreate the Transrate config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xtransrate.get_transrate_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xtransrate.create_transrate_config_file(experiment_id, reference_dataset_id, reference_file, cluster_read_dir, read_type, selected_file_list, None, assembly_dataset_id, assembly_type)
            elif read_type == 'PE':
                (OK, error_list) = xtransrate.create_transrate_config_file(experiment_id, reference_dataset_id, reference_file, cluster_read_dir, read_type, file_1_list, file_2_list, assembly_dataset_id, assembly_type)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_trimmomatic_config_file():
    '''
    Recreate the Trimmomatic config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_trimmomatic_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # recreate the Trimmomatic config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xtrimmomatic.get_trimmomatic_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xtrimmomatic.create_trimmomatic_config_file(experiment_id, read_dataset_id, read_type, selected_file_list, None)
            elif read_type == 'PE':
                (OK, error_list) = xtrimmomatic.create_trimmomatic_config_file(experiment_id, read_dataset_id, read_type, file_1_list, file_2_list)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_recreate_trinity_config_file():
    '''
    Recreate the Trinity config file.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Recreate config file'.format(xlib.get_trinity_name()))

    # get the cluster name, experiment identification, read dataset identification and the file pattern
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # create the SSH client connection
    if OK:
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        for error in error_list:
            log.write('{0}\n'.format(error))

    # get the experiment identification
    if OK:
        experiment_id = cinputs.input_experiment_id(ssh_client, help=True)
        if experiment_id == '':
            print('WARNING: The cluster {0} has not experiment data.'.format(cluster_name))
            OK = False

    # get the read dataset identification
    if OK:
        read_dataset_id = cinputs.input_read_dataset_id(ssh_client, experiment_id, help=True)
        if read_dataset_id == '':
            print('WARNING: The cluster {0} has not read datasets.'.format(cluster_name))
            OK = False

    # get the file pattern
    if OK:
        file_pattern = cinputs.input_files_pattern('.*')

    # build the cluster read directory path
    if OK:
        cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), experiment_id, read_dataset_id)

    # get the selected file list
    if OK:
        selected_file_list = []
        command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, file_pattern)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                selected_file_list.append(line.rstrip('\n'))
        else:
            print('*** ERROR: Wrong command ---> {0}'.format(command))
        if selected_file_list == []:
            print('WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, file_pattern))
            OK = False

    # get the read type
    if OK:
        read_type = cinputs.input_read_type()

    # get the specific_chars to identify files when the read type is paired 
    if OK:
        if read_type == 'SE':
            specific_chars_1 = None
            specific_chars_2 = None
        elif read_type == 'PE':
            specific_chars_1 = cinputs.input_file_pairing_specific_chars(1, '1')
            specific_chars_2 = cinputs.input_file_pairing_specific_chars(2, '2')

    # get the paired file list when the read type is paired
    if OK:
        if read_type == 'PE':
            (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, specific_chars_1, specific_chars_2)
            if unpaired_file_list != []:
                print('ERROR: There are unpaired files.')
                OK = False

    # recreate the Trinity config file
    if OK:

        # confirm the creation of the config file
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be recreated. The previous files will be lost.'.format(xtrinity.get_trinity_config_file()))

        # recreate the config file
        if OK:
            if read_type == 'SE':
                (OK, error_list) = xtrinity.create_trinity_config_file(experiment_id, read_dataset_id, read_type, selected_file_list, None)
            elif read_type == 'PE':
                (OK, error_list) = xtrinity.create_trinity_config_file(experiment_id, read_dataset_id, read_type, file_1_list, file_2_list)
            if OK:
                print('The file is recreated.')
            else:
                for error in error_list:
                    print(error)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_edit_bioinfo_config_file(app):
    '''
    Edit a bioinfo appliation config file to change the parameters of each process.
    '''

    # initialize the control variable
    OK = True

    # set the bioinfo application name
    if app == xlib.get_busco_code():
        name = xlib.get_busco_name()
    elif app == xlib.get_cd_hit_est_code():
        name = xlib.get_cd_hit_est_name()
    elif app == xlib.get_fastqc_code():
        name = xlib.get_fastqc_name()
    elif app == xlib.get_gmap_code():
        name = xlib.get_gmap_name()
    elif app == xlib.get_insilico_read_normalization_code():
        name = xlib.get_insilico_read_normalization_name()
    elif app == xlib.get_quast_code():
        name = xlib.get_quast_name()
    elif app == xlib.get_ref_eval_code():
        name = xlib.get_ref_eval_name()
    elif app == xlib.get_rnaquast_code():
        name = xlib.get_rnaquast_name()
    elif app == xlib.get_rsem_eval_code():
        name = xlib.get_rsem_eval_name()
    elif app == xlib.get_soapdenovotrans_code():
        name = xlib.get_soapdenovotrans_name()
    elif app == xlib.get_star_code():
        name = xlib.get_star_name()
    elif app == xlib.get_transabyss_code():
        name = xlib.get_transabyss_name()
    elif app == xlib.get_transcript_filter_code():
        name = xlib.get_transcript_filter_name()
    elif app == xlib.get_transcriptome_blastx_code():
        name = xlib.get_transcriptome_blastx_name()
    elif app == xlib.get_transrate_code():
        name = xlib.get_transrate_name()
    elif app == xlib.get_trimmomatic_code():
        name = xlib.get_trimmomatic_name()
    elif app == xlib.get_trinity_code():
        name = xlib.get_trinity_name()

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Edit config file'.format(name))

    # get the config file
    if app == xlib.get_busco_code():
        config_file = xbusco.get_busco_config_file()
    elif app == xlib.get_cd_hit_est_code():
        config_file = xcdhit.get_cd_hit_est_config_file()
    elif app == xlib.get_fastqc_code():
        config_file = xfastqc.get_fastqc_config_file()
    elif app == xlib.get_gmap_code():
        config_file = xgmap.get_gmap_config_file()
    elif app == xlib.get_insilico_read_normalization_code():
        config_file = xtrinity.get_insilico_read_normalization_config_file()
    elif app == xlib.get_quast_code():
        config_file = xquast.get_quast_config_file()
    elif app == xlib.get_ref_eval_code():
        config_file = xdetonate.get_ref_eval_config_file()
    elif app == xlib.get_rnaquast_code():
        config_file = xrnaquast.get_rnaquast_config_file()
    elif app == xlib.get_rsem_eval_code():
        config_file = xdetonate.get_rsem_eval_config_file()
    elif app == xlib.get_soapdenovotrans_code():
        config_file = xsoapdenovotrans.get_soapdenovotrans_config_file()
    elif app == xlib.get_star_code():
        config_file = xstar.get_star_config_file()
    elif app == xlib.get_transabyss_code():
        config_file = xtransabyss.get_transabyss_config_file()
    elif app == xlib.get_transcript_filter_code():
        config_file = xngshelper.get_transcript_filter_config_file()
    elif app == xlib.get_transcriptome_blastx_code():
        config_file = xngshelper.get_transcriptome_blastx_config_file()
    elif app == xlib.get_transrate_code():
        config_file = xtransrate.get_transrate_config_file()
    elif app == xlib.get_trimmomatic_code():
        config_file = xtrimmomatic.get_trimmomatic_config_file()
    elif app == xlib.get_trinity_code():
        config_file = xtrinity.get_trinity_config_file()

    # edit the read transfer config file
    print(xlib.get_separator())
    print('Editing the {0} config file ...'.format(name))
    command = '{0} {1}'.format(xlib.get_editor(), config_file)
    rc = subprocess.call(command, shell=True)
    if rc != 0:
        print('*** ERROR: Return code {0} in command -> {1}'.format(rc, command))
        OK = False

    # validate the config file
    if OK:
        print(xlib.get_separator())
        print('Validating the {0} config file ...'.format(name))
        if app == xlib.get_busco_code():
            (OK, error_list) = xbusco.validate_busco_config_file(strict=False)
        elif app == xlib.get_cd_hit_est_code():
            (OK, error_list) = xcdhit.validate_cd_hit_est_config_file(strict=False)
        elif app == xlib.get_fastqc_code():
            (OK, error_list) = xfastqc.validate_fastqc_config_file(strict=False)
        elif app == xlib.get_gmap_code():
            (OK, error_list) = xgmap.validate_gmap_config_file(strict=False)
        elif app == xlib.get_insilico_read_normalization_code():
            (OK, error_list) = xtrinity.validate_insilico_read_normalization_config_file(strict=False)
        elif app == xlib.get_quast_code():
            (OK, error_list) = xquast.validate_quast_config_file(strict=False)
        elif app == xlib.get_ref_eval_code():
            (OK, error_list) = xdetonate.validate_ref_eval_config_file(strict=False)
        elif app == xlib.get_rnaquast_code():
            (OK, error_list) = xrnaquast.validate_rnaquast_config_file(strict=False)
        elif app == xlib.get_rsem_eval_code():
            (OK, error_list) = xdetonate.validate_rsem_eval_config_file(strict=False)
        elif app == xlib.get_soapdenovotrans_code():
            (OK, error_list) = xsoapdenovotrans.validate_soapdenovotrans_config_file(strict=False)
        elif app == xlib.get_star_code():
            (OK, error_list) = xstar.validate_star_config_file(strict=False)
        elif app == xlib.get_transabyss_code():
            (OK, error_list) = xtransabyss.validate_transabyss_config_file(strict=False)
        elif app == xlib.get_transcript_filter_code():
            (OK, error_list) = xngshelper.validate_transcript_filter_config_file(strict=False)
        elif app == xlib.get_transcriptome_blastx_code():
            (OK, error_list) = xngshelper.validate_transcriptome_blastx_config_file(strict=False)
        elif app == xlib.get_transrate_code():
            (OK, error_list) = xtransrate.validate_transrate_config_file(strict=False)
        elif app == xlib.get_trimmomatic_code():
            (OK, error_list) = xtrimmomatic.validate_trimmomatic_config_file(strict=False)
        elif app == xlib.get_trinity_code():
            (OK, error_list) = xtrinity.validate_trinity_config_file(strict=False)
        if OK:
            print('The config file is OK.')
        else:
            print()
            for error in error_list:
                print(error)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_run_bioinfo_process(app):
    '''
    Run a bioinfo application process with the parameters in the corresponding config file.
    '''

    # initialize the control variable
    OK = True

    # set the bioinfo application name
    if app == xlib.get_busco_code():
        name = xlib.get_busco_name()
    elif app == xlib.get_cd_hit_est_code():
        name = xlib.get_cd_hit_est_name()
    elif app == xlib.get_fastqc_code():
        name = xlib.get_fastqc_name()
    elif app == xlib.get_gmap_code():
        name = xlib.get_gmap_name()
    elif app == xlib.get_insilico_read_normalization_code():
        name = xlib.get_insilico_read_normalization_name()
    elif app == xlib.get_quast_code():
        name = xlib.get_quast_name()
    elif app == xlib.get_ref_eval_code():
        name = xlib.get_ref_eval_name()
    elif app == xlib.get_rnaquast_code():
        name = xlib.get_rnaquast_name()
    elif app == xlib.get_rsem_eval_code():
        name = xlib.get_rsem_eval_name()
    elif app == xlib.get_soapdenovotrans_code():
        name = xlib.get_soapdenovotrans_name()
    elif app == xlib.get_star_code():
        name = xlib.get_star_name()
    elif app == xlib.get_transabyss_code():
        name = xlib.get_transabyss_name()
    elif app == xlib.get_transcript_filter_code():
        name = xlib.get_transcript_filter_name()
    elif app == xlib.get_transcriptome_blastx_code():
        name = xlib.get_transcriptome_blastx_name()
    elif app == xlib.get_transrate_code():
        name = xlib.get_transrate_name()
    elif app == xlib.get_trimmomatic_code():
        name = xlib.get_trimmomatic_name()
    elif app == xlib.get_trinity_code():
        name = xlib.get_trinity_name()

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('{0} - Run process'.format(name))

    # get the cluster name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # confirm the process run
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The {0} process is going to be run.'.format(name))

    # run the process
    if OK:

        # execute the process when it is a BUSCO process
        if app == xlib.get_busco_code():
            devstdout = xlib.DevStdOut(xbusco.run_busco_process.__name__)
            OK = xbusco.run_busco_process(cluster_name, devstdout, function=None)

        # execute the process when it is a CD-HIT-EST process
        elif app == xlib.get_cd_hit_est_code():
            devstdout = xlib.DevStdOut(xcdhit.run_cd_hit_est_process.__name__)
            OK = xcdhit.run_cd_hit_est_process(cluster_name, devstdout, function=None)

        # execute the process when it is a FastQC process
        elif app == xlib.get_fastqc_code():
            devstdout = xlib.DevStdOut(xfastqc.run_fastqc_process.__name__)
            OK = xfastqc.run_fastqc_process(cluster_name, devstdout, function=None)

        # execute the process when it is a GMAP process
        elif app == xlib.get_gmap_code():
            devstdout = xlib.DevStdOut(xgmap.run_gmap_process.__name__)
            OK = xgmap.run_gmap_process(cluster_name, devstdout, function=None)

        # execute the process when it is a insilico_read_normalization process
        elif app == xlib.get_insilico_read_normalization_code():
            devstdout = xlib.DevStdOut(xtrinity.run_insilico_read_normalization_process.__name__)
            OK = xtrinity.run_insilico_read_normalization_process(cluster_name, devstdout, function=None)

        # execute the process when it is a QUAST process
        elif app == xlib.get_quast_code():
            devstdout = xlib.DevStdOut(xquast.run_quast_process.__name__)
            OK = xquast.run_quast_process(cluster_name, devstdout, function=None)

        # execute the process when it is a REF-EVAL process
        elif app == xlib.get_ref_eval_code():
            devstdout = xlib.DevStdOut(xdetonate.run_ref_eval_process.__name__)
            OK = xdetonate.run_ref_eval_process(cluster_name, devstdout, function=None)

        # execute the process when it is a rnaQUAST process
        elif app == xlib.get_rnaquast_code():
            devstdout = xlib.DevStdOut(xrnaquast.run_rnaquast_process.__name__)
            OK = xrnaquast.run_rnaquast_process(cluster_name, devstdout, function=None)

        # execute the process when it is a RSEM-EVAL process
        elif app == xlib.get_rsem_eval_code():
            devstdout = xlib.DevStdOut(xdetonate.run_rsem_eval_process.__name__)
            OK = xdetonate.run_rsem_eval_process(cluster_name, devstdout, function=None)

        # execute the process when it is a SOAPdenovo-Trans process
        elif app == xlib.get_soapdenovotrans_code():
            devstdout = xlib.DevStdOut(xsoapdenovotrans.run_soapdenovotrans_process.__name__)
            OK = xsoapdenovotrans.run_soapdenovotrans_process(cluster_name, devstdout, function=None)

        # execute the process when it is a STAR process
        elif app == xlib.get_star_code():
            devstdout = xlib.DevStdOut(xstar.run_star_process.__name__)
            OK = xstar.run_star_process(cluster_name, devstdout, function=None)

        # execute the process when it is a Trans-ABySS process
        elif app == xlib.get_transabyss_code():
            devstdout = xlib.DevStdOut(xtransabyss.run_transabyss_process.__name__)
            OK = xtransabyss.run_transabyss_process(cluster_name, devstdout, function=None)

        # execute the process when it is a transcripts-filter process
        elif app == xlib.get_transcript_filter_code():
            devstdout = xlib.DevStdOut(xngshelper.run_transcript_filter_process.__name__)
            OK = xngshelper.run_transcript_filter_process(cluster_name, devstdout, function=None)

        # execute the process when it is a transcriptome-blastx process
        elif app == xlib.get_transcriptome_blastx_code():
            devstdout = xlib.DevStdOut(xngshelper.run_transcriptome_blastx_process.__name__)
            OK = xngshelper.run_transcriptome_blastx_process(cluster_name, devstdout, function=None)

        # execute the process when it is a Transrate process
        elif app == xlib.get_transrate_code():
            devstdout = xlib.DevStdOut(xtransrate.run_transrate_process.__name__)
            OK = xtransrate.run_transrate_process(cluster_name, devstdout, function=None)

        # execute the process when it is a Trimmomatic process
        elif app == xlib.get_trimmomatic_code():
            devstdout = xlib.DevStdOut(xtrimmomatic.run_trimmomatic_process.__name__)
            OK = xtrimmomatic.run_trimmomatic_process(cluster_name, devstdout, function=None)

        # execute the process when it is a Trinity process
        elif app == xlib.get_trinity_code():
            devstdout = xlib.DevStdOut(xtrinity.run_trinity_process.__name__)
            OK = xtrinity.run_trinity_process(cluster_name, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains the functions related to forms corresponding BioInfo application menu items in console mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
