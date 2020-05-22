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
This file contains the functions related to the SOAPdenovo-Trans menus in console mode.
'''
#-------------------------------------------------------------------------------

import sys

import cbioinfoapp
import ccloud
import cdataset
import clib
import clog
import xlib

#-------------------------------------------------------------------------------

def build_menu_main():
    '''
    Build the menu Main.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Main')

        # print the menu options
        print('Options:')
        print()
        print('    1. Cloud control')
        print('    2. RNA-seq')
        print('    3. Datasets')
        print('    4. Logs')
        print()
        print('    X. Exit NGScloud')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_cloud_control()
        elif option == '2':
            build_menu_rnaseq()
        elif option == '3':
            build_menu_datasets()
        elif option == '4':
            build_menu_logs()
        elif option == 'X':
            sure = ''
            print('')
            while sure not in ['Y', 'N']:
                sure = input('Are you sure to exit NGScloud (y or n)?: ').upper()
            if sure == 'Y':
                break

#-------------------------------------------------------------------------------

def build_menu_cloud_control():
    '''
    Build the menu Cloud control.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Cloud control')

        # print the menu options
        print('Options:')
        print()
        print('    1. Set environment')
        print()
        print('    2. Configuration')
        print('    3. Security')
        print()
        print('    4. Cluster operation')
        print('    5. Node operation')
        print('    6. Volume operation')
        print()
        print('    7. Bioinfo software setup')
        print()
        print('    8. Open a terminal')
        print()
        print('    X. Return to menu Main')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            ccloud.form_set_environment()
        elif option == '2':
            build_menu_configuration()
        elif option == '3':
            build_menu_security()
        elif option == '4':
            build_menu_cluster_operation()
        elif option == '5':
            build_menu_node_operation()
        elif option == '6':
            build_menu_volume_operation()
        elif option == '7':
            build_menu_bioinfo_software_setup()
        elif option == '8':
            ccloud.form_open_terminal()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_configuration():
    '''
    Build the menu Configuration.
    '''


    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Configuration')

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate NGScloud config file')
        print('    2. View NGScloud config file')
        print()
        print('    3. List cluster templates')
        print()
        print('    4. Update connection data and contact e-mail')
        print('    5. Update region and zone')
        print()
        print('    6. Link volume in a cluster template')
        print('    7. Delink volume in a cluster template')
        print('    8. Review volumes linked to cluster templates')
        print()
        print('    X. Return to menu Cloud control')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            ccloud.form_create_ngscloud_config_file(is_menu_call=True)
        elif option == '2':
            ccloud.form_view_ngscloud_config_file()
        elif option == '3':
            ccloud.form_list_templates()
        elif option == '4':
            ccloud.form_update_connection_data()
        elif option == '5':
            ccloud.form_update_region_zone()
        elif option == '6':
            ccloud.form_link_volume_to_template()
        elif option == '7':
            ccloud.form_delink_volume_from_template()
        elif option == '8':
            ccloud.form_review_volume_links()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_security():
    '''
    Build the menu Security.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Security')

        # print the menu options
        print('Options:')
        print()
        print('    1. List key pairs')
        print('    2. Create key pairs')
        print()
        print('    3. List cluster security groups (coming soon!)')
        print('    4. Force removal of a cluster security group (coming soon!)')
        print()
        print('    X. Return to menu Cloud control')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            ccloud.form_list_keypairs()
        elif option == '2':
            ccloud.form_create_keypairs()
        elif option == '3':
            pass
        elif option == '3':
            pass
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_cluster_operation():
    '''
    Build the menu Cluster operation.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Cluster operation')

        # print the menu options
        print('Options:')
        print()
        print('    1. List clusters')
        print()
        print('    2. Create cluster')
        print('    3. Stop cluster')
        print('    4. Restart cluster')
        print('    5. Terminate cluster')
        print()
        print('    6. Force termination of a cluster')
        print()
        print('    7. Show cluster composition')
        print()
        print('    8. Show status of batch jobs')
        print('    9. Kill batch job')
        print()
        print('    X. Return to menu Cloud Control')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            ccloud.form_list_clusters()
        elif option == '2':
            ccloud.form_create_cluster()
        elif option == '3':
            ccloud.form_stop_cluster()
        elif option == '4':
            ccloud.form_restart_cluster()
        elif option == '5':
            ccloud.form_terminate_cluster(force=False)
        elif option == '6':
            ccloud.form_terminate_cluster(force=True)
        elif option == '7':
            ccloud.form_show_cluster_composing()
        elif option == '8':
            ccloud.form_show_status_batch_jobs()
        elif option == '9':
            ccloud.form_kill_batch_job()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_node_operation():
    '''
    Build the menu Node operation.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Node operation')

        # print the menu options
        print('Options:')
        print()
        print('    1. List nodes')
        print()
        print('    2. Add node in a cluster')
        print('    3. Remove node in a cluster')
        print()
        print('    X. Return to menu Cloud Control')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            ccloud.form_list_nodes()
        elif option == '2':
            ccloud.form_add_node()
        elif option == '3':
            ccloud.form_remove_node()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_volume_operation():
    '''
    Build the menu Volume operation.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Volume operation')

        # print the menu options
        print('Options:')
        print()
        print('    1. List volumes')
        print()
        print('    2. Create volume')
        print('    3. Remove volume')
        print()
        print('    4. Terminate volume creator')
        print()
        print('    5. Mount volume in a node')
        print('    6. Unmount volume in a node')
        print()
        print('    X. Return to menu Cloud Control')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            ccloud.form_list_volumes()
        elif option == '2':
            ccloud.form_create_volume()
        elif option == '3':
            ccloud.form_remove_volume()
        elif option == '4':
            ccloud.form_terminate_volume_creator()
        elif option == '5':
            ccloud.form_mount_volume()
        elif option == '6':
            ccloud.form_unmount_volume()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_bioinfo_software_setup():
    '''
    Build the menu Bioinfo software setup.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Bioinfo software setup')

        # print the menu options
        print('Options:')
        print()
        print('    1. {0} (Python & Bioconda environments'.format(xlib.get_miniconda3_name()))
        print()
        print('    2. {0}'.format(xlib.get_blastplus_name()))
        print('    3. {0}'.format(xlib.get_busco_name()))
        print('    4. {0}'.format(xlib.get_cd_hit_name()))
        print('    5. {0}'.format(xlib.get_detonate_name()))
        print('    6. {0}'.format(xlib.get_fastqc_name()))
        print('    7. {0}'.format(xlib.get_gmap_gsnap_name()))
        print('    8. {0}'.format(xlib.get_ngshelper_name()))
        print('    9. {0}'.format(xlib.get_quast_name()))
        print('    A. {0}'.format(xlib.get_rnaquast_name()))
        print('    B. {0}'.format(xlib.get_soapdenovotrans_name()))
        print('    C. {0}'.format(xlib.get_star_name()))
        print('    D. {0}'.format(xlib.get_transabyss_name()))
        print('    E. {0}'.format(xlib.get_transrate_name()))
        print('    F. {0}'.format(xlib.get_trimmomatic_name()))
        print('    G. {0}'.format(xlib.get_trinity_name()))
        # -- print()
        # -- print('    H. {0} & analysis packages'.format(xlib.get_r_name()))
        print()
        print('    X. Return to menu Cloud Control')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_miniconda3_code())
        elif option == '2':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_blastplus_code())
        elif option == '3':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_busco_code())
        elif option == '4':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_cd_hit_code())
        elif option == '5':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_detonate_code())
        elif option == '6':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_fastqc_code())
        elif option == '7':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_gmap_gsnap_code())
        elif option == '8':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_ngshelper_code())
        elif option == '9':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_quast_code())
        elif option == 'A':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_rnaquast_code())
        elif option == 'B':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_soapdenovotrans_code())
        elif option == 'C':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_star_code())
        elif option == 'D':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_transabyss_code())
        elif option == 'E':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_transrate_code())
        elif option == 'F':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_trimmomatic_code())
        elif option == 'G':
            cbioinfoapp.form_setup_bioinfo_app(xlib.get_trinity_code())
        # -- elif option == 'H':
        # --     cbioinfoapp.form_setup_bioinfo_app(xlib.get_r_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_rnaseq():
    '''
    Build the menu RNA-seq.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('RNA-seq')

        # print the menu options
        print('Options:')
        print()
        print('    1. Read quality')
        print('    2. Trimming')
        print('    3. Digital normalization')
        print()
        print('    4. De novo assembly')
        print('    5. Reference-based assembly')
        print()
        print('    6. Assembly quality and transcript quantification')
        print('    7. Transcriptome filtering')
        print()
        print('    8. Annotation')
        print()
        print('    X. Return to menu Main')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_read_quality()
        elif option == '2':
            build_menu_trimming()
        elif option == '3':
            build_menu_digital_normalization()
        elif option == '4':
            build_menu_denovo_assembly()
        elif option == '5':
            build_menu_reference_based_assembly()
        elif option == '6':
            build_menu_assembly_assessment()
        elif option == '7':
            build_menu_transcriptome_filtering()
        elif option == '8':
            build_menu_annotation()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_read_quality():
    '''
    Build the menu Read quality.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Read quality')

        # print the menu options
        print('Options:')
        print()
        print('    1. {0}'.format(xlib.get_fastqc_name()))
        print()
        print('    X. Return to menu RNA-seq')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_fastqc()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_fastqc():
    '''
    Build the menu FastQC.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_fastqc_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run read quality process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Quality assessment')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_fastqc_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_fastqc_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_fastqc_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_trimming():
    '''
    Build the menu Trimming.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Trimming')

        # print the menu options
        print('Options:')
        print()
        print('    1. {0}'.format(xlib.get_trimmomatic_name()))
        print()
        print('    X. Return to menu RNA-seq')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_trimmomatic()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_trimmomatic():
    '''
    Build the menu Trimmomatic.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_trimmomatic_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run trimming process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Trimming')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_trimmomatic_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_trimmomatic_code())
        elif option == '3':
             cbioinfoapp.form_run_bioinfo_process(xlib.get_trimmomatic_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_digital_normalization():
    '''
    Build the menu Digital normalization.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Digital normalization')

        # print the menu options
        print('Options:')
        print()
        print('    1. {0} ({1} package)'.format(xlib.get_insilico_read_normalization_name(), xlib.get_trinity_name()))
        print()
        print('    X. Return to menu RNA-seq')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_insilico_read_normalization()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_insilico_read_normalization():
    '''
    Build the menu insilico_read_normalization (Trinity package).
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('{0} ({1} package)'.format(xlib.get_insilico_read_normalization_name(), xlib.get_trinity_name()))

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run digital normalization process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Digital normalization')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_insilico_read_normalization_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_insilico_read_normalization_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_insilico_read_normalization_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_denovo_assembly():
    '''
    Build the menu De novo assembly.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('De novo assembly')

        # print the menu options
        print('Options:')
        print()
        print('    1. {0}'.format(xlib.get_soapdenovotrans_name()))
        print('    2. {0}'.format(xlib.get_transabyss_name()))
        print('    3. {0}'.format(xlib.get_trinity_name()))
        print()
        print('    X. Return to menu RNA-seq')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_soapdenovotrans()
        elif option == '2':
            build_menu_transabyss()
        elif option == '3':
            build_menu_trinity()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_soapdenovotrans():
    '''
    Build the menu SOAPdenovo-Trans.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_soapdenovotrans_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu De novo assembly')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_soapdenovotrans_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_soapdenovotrans_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_soapdenovotrans_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_transabyss():
    '''
    Build the menu Trans-ABySS.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_transabyss_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu De novo assembly')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_transabyss_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_transabyss_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_transabyss_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_trinity():
    '''
    Build the menu Trinity.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_trinity_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu De novo assembly')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_trinity_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_trinity_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_trinity_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_reference_based_assembly():
    '''
    Build the menu Reference-based assembly.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Reference-based assembly')

        # print the menu options
        print('Options:')
        print()
        print('    1. {0}'.format(xlib.get_star_name()))
        print()
        print('    X. Return to menu RNA-seq')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_star()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_star():
    '''
    Build the menu STAR.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_star_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu De novo assembly')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_star_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_star_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_star_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_assembly_assessment():
    '''
    Build the menu Assembly quality and transcript quantification.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Assembly quality and transcript quantification')

        # print the menu options
        print('Options:')
        print()
        print('    1. {0}'.format(xlib.get_busco_name()))
        print('    2. {0} ({1} package)'.format(xlib.get_gmap_name(), xlib.get_gmap_gsnap_name()))
        print('    3. {0}'.format(xlib.get_quast_name()))
        print('    4. {0}'.format(xlib.get_rnaquast_name()))
        print('    5. {0} ({1} package)'.format(xlib.get_rsem_eval_name(), xlib.get_detonate_name()))
        print('    6. {0}'.format(xlib.get_transrate_name()))
        print()
        print('    X. Return to menu RNA-seq')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_busco()
        elif option == '2':
            build_menu_gmap()
        elif option == '3':
            build_menu_quast()
        if option == '4':
            build_menu_rnaquast()
        elif option == '5':
            build_menu_rsem_eval()
        elif option == '6':
            build_menu_transrate()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_busco():
    '''
    Build the menu BUSCO.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_busco_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly assessment process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Assembly quality and transcript quantification')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_busco_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_busco_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_busco_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_gmap():
    '''
    Build the menu GMAP.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('{0} ({1} package)'.format(xlib.get_gmap_name(), xlib.get_gmap_gsnap_name()))

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly assessment process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Assembly quality and transcript quantification')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_gmap_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_gmap_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_gmap_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_quast():
    '''
    Build the menu QUAST.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_quast_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly assessment process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Assembly quality and transcript quantification')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_quast_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_quast_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_quast_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_rnaquast():
    '''
    Build the menu rnaQUAST.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_rnaquast_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly assessment process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Assembly quality and transcript quantification')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_rnaquast_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_rnaquast_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_rnaquast_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_rsem_eval():
    '''
    Build the menu RSEM-EVAL (reference-free evaluation of DETONATE package).
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('{0} ({1} package)'.format(xlib.get_rsem_eval_name(), xlib.get_detonate_name()))

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly assessment process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Assembly quality and transcript quantification')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_rsem_eval_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_rsem_eval_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_rsem_eval_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_ref_eval():
    '''
    Build the menu REF-EVAL (toolkit of reference-based measures of DETONATE package).
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('{0} ({1} package)'.format(xlib.get_ref_eval_name(), xlib.get_detonate_name()))

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly assessment process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Assembly quality and transcript quantification')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_ref_eval_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_ref_eval_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_ref_eval_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_transrate():
    '''
    Build the menu Transrate.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment(xlib.get_transrate_name())

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run assembly assessment process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Assembly quality and transcript quantification')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_transrate_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_transrate_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_transrate_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_transcriptome_filtering():
    '''
    Build the menu Trnascriptome filtering.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Transcriptome filtering')

        # print the menu options
        print('Options:')
        print()
        print('    1. {0} ({1} package)'.format(xlib.get_cd_hit_est_name(), xlib.get_cd_hit_name()))
        print('    2. {0} ({1} package)'.format(xlib.get_transcript_filter_name(), xlib.get_ngshelper_name()))
        print()
        print('    X. Return to menu RNA-seq')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_cd_hit_est()
        elif option == '2':
            build_menu_transcript_filter()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_cd_hit_est():
    '''
    Build the menu CD-HIT-EST.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('{0} ({1} package)'.format(xlib.get_cd_hit_est_name(), xlib.get_cd_hit_name()))

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run transcriptome filtering process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Transcriptome filtering')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_cd_hit_est_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_cd_hit_est_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_cd_hit_est_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_transcript_filter():
    '''
    Build the menu transcript-filter (NGShelper package).
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('{0} ({1} package)'.format(xlib.get_transcript_filter_name(), xlib.get_ngshelper_name()))

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run transcriptome filtering process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Transcriptome filtering')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_transcript_filter_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_transcript_filter_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_transcript_filter_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_annotation():
    '''
    Build the menu Annotation.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Annotation')

        # print the menu options
        print('Options:')
        print()
        print('    1. {0} ({1} package)'.format(xlib.get_transcriptome_blastx_name(), xlib.get_ngshelper_name()))
        print()
        print('    X. Return to menu RNA-seq')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            build_menu_transcriptome_blastx()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_transcriptome_blastx():
    '''
    Build the menu CD-HIT-EST.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('{0} ({1} package)'.format(xlib.get_transcriptome_blastx_name(), xlib.get_ngshelper_name()))

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run annotation process')
        print('       (CAUTION: before running a process, the config file should be updated)')
        print()
        print('    X. Return to menu Annotation')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cbioinfoapp.form_recreate_transcriptome_blastx_config_file()
        elif option == '2':
            cbioinfoapp.form_edit_bioinfo_config_file(xlib.get_transcriptome_blastx_code())
        elif option == '3':
            cbioinfoapp.form_run_bioinfo_process(xlib.get_transcriptome_blastx_code())
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_datasets():
    '''
    Build the menu Datasets.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Datasets')

        # print the menu options
        print('Options:')
        print()
        print('    1. List dataset (coming soon!)')
        print()
        print('    2. Reference dataset file transfer')
        print('    3. Reference dataset file compression/decompression')
        print('    4. Remove reference dataset')
        print()
        print('    5. Database file transfer')
        print('    6. Database file compression/decompression')
        print('    7. Remove database')
        print()
        print('    8. Read dataset file transfer')
        print('    9. Read dataset file compression/decompression')
        print('    A. Remove read dataset')
        print()
        print('    B. Result dataset file transfer')
        print('    C. Result dataset file compression/decompression')
        print('    D. Remove result dataset')
        print()
        print('    E. Remove experiment')
        print()
        print('    X. Return to menu Main')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            pass
        elif option == '2':
            build_menu_reference_file_transfer()
        elif option == '3':
            build_menu_reference_file_compression_decompression()
        elif option == '4':
            cdataset.form_remove_reference_dataset()
        elif option == '5':
            build_menu_database_file_transfer()
        elif option == '6':
            build_menu_database_file_compression_decompression()
        elif option == '7':
            cdataset.form_remove_database_dataset()
        elif option == '8':
            build_menu_read_file_transfer()
        elif option == '9':
            build_menu_read_file_compression_decompression()
        elif option == 'A':
            cdataset.form_remove_read_dataset()
        elif option == 'B':
            build_menu_result_file_transfer()
        elif option == 'C':
            build_menu_result_file_compression_decompression()
        elif option == 'D':
            cdataset.form_remove_result_dataset()
        elif option == 'E':
            cdataset.form_remove_experiment()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_reference_file_transfer():
    '''
    Build the menu Reference dataset file transfer.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Reference dataset file transfer')

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Upload dataset to a cluster')
        print('       (CAUTION: before running a upload process, the corresponding config file should be updated)')
        print()
        print('    X. Return to menu Datasets')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cdataset.form_recreate_reference_transfer_config_file()
        elif option == '2':
            cdataset.form_edit_reference_transfer_config_file()
        elif option == '3':
            cdataset.form_upload_reference_dataset()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_reference_file_compression_decompression():
    '''
    Build the menu Reference dataset file compression/decompression.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Reference dataset file compression/decompression')

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run compression/decompression process')
        print('       (CAUTION: before running a compression/decompression process,')
        print('                 the corresponding config file should be updated)')
        print()
        print('    X. Return to menu Datasets')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cdataset.form_recreate_reference_gzip_config_file()
        elif option == '2':
            cdataset.form_edit_reference_gzip_config_file()
        elif option == '3':
            cdataset.form_run_reference_gzip_process()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_database_file_transfer():
    '''
    Build the menu Database file transfer.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Database file transfer')

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Upload dataset to a cluster')
        print('       (CAUTION: before running a upload process, the corresponding config file should be updated)')
        print()
        print('    X. Return to menu Datasets')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cdataset.form_recreate_database_transfer_config_file()
        elif option == '2':
            cdataset.form_edit_database_transfer_config_file()
        elif option == '3':
            cdataset.form_upload_database_dataset()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_database_file_compression_decompression():
    '''
    Build the menu Database file compression/decompression.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Database file compression/decompression')

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run compression/decompression process')
        print('       (CAUTION: before running a compression/decompression process,')
        print('                 the corresponding config file should be updated)')
        print()
        print('    X. Return to menu Datasets')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cdataset.form_recreate_database_gzip_config_file()
        elif option == '2':
            cdataset.form_edit_database_gzip_config_file()
        elif option == '3':
            cdataset.form_run_database_gzip_process()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_read_file_transfer():
    '''
    Build the menu Read dataset file transfer.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Read dataset file transfer')

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Upload dataset to a cluster')
        print('       (CAUTION: before running a upload process, the corresponding config file should be updated)')
        print()
        print('    X. Return to menu Datasets')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cdataset.form_recreate_read_transfer_config_file()
        elif option == '2':
            cdataset.form_edit_read_transfer_config_file()
        elif option == '3':
            cdataset.form_upload_read_dataset()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_read_file_compression_decompression():
    '''
    Build the menu Read dataset file compression/decompression.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Read dataset file compression/decompression')

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run compression/decompression process')
        print('       (CAUTION: before running a compression/decompression process,')
        print('                 the corresponding config file should be updated)')
        print()
        print('    X. Return to menu Datasets')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cdataset.form_recreate_read_gzip_config_file()
        elif option == '2':
            cdataset.form_edit_read_gzip_config_file()
        elif option == '3':
            cdataset.form_run_read_gzip_process()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_result_file_transfer():
    '''
    Build the menu Result dataset file transfer.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Result dataset file transfer')

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Download dataset from a cluster')
        print('       (CAUTION: before running a download process, the corresponding config file should be updated)')
        print()
        print('    X. Return to menu Datasets')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cdataset.form_recreate_result_transfer_config_file()
        elif option == '2':
            cdataset.form_edit_result_transfer_config_file()
        elif option == '3':
            cdataset.form_download_result_dataset()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_result_file_compression_decompression():
    '''
    Build the menu Result dataset file compression/decompression.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Result dataset file compression/decompression')

        # print the menu options
        print('Options:')
        print()
        print('    1. Recreate config file')
        print('    2. Edit config file')
        print()
        print('    3. Run compression/decompression process')
        print('       (CAUTION: before running a compression/decompression process,')
        print('                 the corresponding config file should be updated)')
        print()
        print('    X. Return to menu Datasets')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            cdataset.form_recreate_result_gzip_config_file()
        elif option == '2':
            cdataset.form_edit_result_gzip_config_file()
        elif option == '3':
            cdataset.form_run_result_gzip_process()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

def build_menu_logs():
    '''
    Build the menu Logs.
    '''

    while True:

        # print headers
        clib.clear_screen()
        clib.print_headers_with_environment('Cluster logs')

        # print the menu options
        print('Options:')
        print()
        print('    1. List submission logs in the local computer (coming soon!)')
        print('    2. View a submission log in the local computer (coming soon!)')
        print()
        print('    3. List result logs in the cluster')
        print('    4. View a result log in the cluster')
        print()
        print('    X. Return to menu Logs')
        print()

        # get the selected option
        option = input('Input the selected option: ').upper()

        # process the selected option
        if option == '1':
            pass
        elif option == '2':
            pass
        elif option == '3':
            clog.form_list_cluster_experiment_processes()
        elif option == '4':
            clog.form_view_cluster_experiment_process_log()
        elif option == 'X':
            break

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains the functions related to the SOAPdenovo-Trans menus in console mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
