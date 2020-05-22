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
This file contains the functions related to forms corresponding to Cloud Control
menu items in console mode.
'''

#-------------------------------------------------------------------------------

import os
import sys

import cinputs
import clib
import xbusco
import xcdhit
import xcluster
import xconfiguration
import xdatabase
import xdetonate
import xec2
import xfastqc
import xgmap
import xgzip
import xlib
import xngshelper
import xnode
import xquast
import xread
import xreference
import xresult
import xrnaquast
import xsoapdenovotrans
import xssh
import xstar
import xtransabyss
import xtransrate
import xtrimmomatic
import xtrinity
import xvolume

#-------------------------------------------------------------------------------

def form_set_environment():
    '''
    Set the environment.
    '''

    # print headers
    clib.clear_screen()
    clib.print_headers_without_environment('Set environment')
    # -- print('function name: {0}'.format(sys._getframe().f_code.co_name))

    # initialize the environment and the input environment
    xconfiguration.environment = ''
    environment = ''

    # get the current environments list
    environments_list = xconfiguration.get_environments_list()

    # print the available region names
    if environments_list != []:
        print('Current environments list: {0} ...'.format(str(environments_list).strip('[]').replace('\'', '')))
        input_text = '... Enter the environment name: '
    else:
        print('Currently there is not any environment recorded.')
        input_text = 'Enter a new environment name: '

    # input and validate the environment
    while xconfiguration.environment == '':
        xconfiguration.environment = input(input_text)
        if xconfiguration.environment not in environments_list:
            print(xlib.get_separator())
            anwser = input('{0} is not a recorded environment. Do you like to record it? (Y/N): '.format(xconfiguration.environment))
            if anwser not in ['Y', 'y']:
                xconfiguration.environment = ''
            else:
                (OK, error_list) = xconfiguration.add_environment(xconfiguration.environment)
                if not OK:
                    for error in error_list:
                        print(error)
                    raise xlib.ProgramException('C002')

    # check if it is necesary to create the NGScloud config file corresponding to the environment
    if not xconfiguration.is_ngscloud_config_file_created():

        print(xlib.get_separator())
        print('Creating the config files ...')

        # create the NGScloud config file
        form_create_ngscloud_config_file(is_menu_call=False)

        # create the key pairs directory
        if not os.path.exists(xlib.get_keypairs_dir()):
            os.makedirs(xlib.get_keypairs_dir())

        # create the BUSCO config file
        (OK, error_list) = xbusco.create_busco_config_file()

        # create the CD-HIT-EST config file
        (OK, error_list) = xcdhit.create_cd_hit_est_config_file()

        # create the FastQC config file
        (OK, error_list) = xfastqc.create_fastqc_config_file()

        # create the GMAP config file
        (OK, error_list) = xgmap.create_gmap_config_file()

        # create the insilico_read_normalization config file
        (OK, error_list) = xtrinity.create_insilico_read_normalization_config_file()

        # create the QUAST config file
        (OK, error_list) = xquast.create_quast_config_file()

        # create the REF-EVAL config file
        (OK, error_list) = xdetonate.create_ref_eval_config_file()

        # create the rnaQUAST config file
        (OK, error_list) = xrnaquast.create_rnaquast_config_file()

        # create the RSEM-EVAL config file
        (OK, error_list) = xdetonate.create_rsem_eval_config_file()

        # create the SOAPdenovo-Trans config file
        (OK, error_list) = xsoapdenovotrans.create_soapdenovotrans_config_file()

        # create the STAR config file
        (OK, error_list) = xstar.create_star_config_file()

        # create the Trans-ABySS config file
        (OK, error_list) = xtransabyss.create_transabyss_config_file()

        # create the transcript-filter config file
        (OK, error_list) = xngshelper.create_transcript_filter_config_file()

        # create the transcriptome-blastx config file
        (OK, error_list) = xngshelper.create_transcriptome_blastx_config_file()

        # create the Transrate config file
        (OK, error_list) = xtransrate.create_transrate_config_file()

        # create the Trimmomatic config file
        (OK, error_list) = xtrimmomatic.create_trimmomatic_config_file()

        # create the Trinity config file
        (OK, error_list) = xtrinity.create_trinity_config_file()

        # create the transfer config files
        (OK, error_list) = xreference.create_reference_transfer_config_file()
        (OK, error_list) = xdatabase.create_database_transfer_config_file()
        (OK, error_list) = xread.create_read_transfer_config_file()
        (OK, error_list) = xresult.create_result_transfer_config_file(status='uncompressed')

        # create the gzip config files
        (OK, error_list) = xgzip.create_gzip_config_file(dataset_type='reference')
        (OK, error_list) = xgzip.create_gzip_config_file(dataset_type='database')
        (OK, error_list) = xgzip.create_gzip_config_file(dataset_type='read')
        (OK, error_list) = xgzip.create_gzip_config_file(dataset_type='result')

    # set the environment variables corresponding to the NGScloud config file, the AWS access key identification,
    # AWS secret access key and the current region name
    print(xlib.get_separator())
    print('Setting the environment variables ...')
    xconfiguration.set_environment_variables()
    print('The environment variables are set.')

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_create_ngscloud_config_file(is_menu_call):
    '''
    Create the NGScloud config file corresponding to the environment.
    '''

    # initialize the control variable
    OK = True

    # print the header
    if is_menu_call:
        clib.clear_screen()
        clib.print_headers_with_environment('Configuration - Recreate TransciptomeCloud config file')

    # get current region and zone names
    region_name = xconfiguration.get_current_region_name()
    zone_name = xconfiguration.get_current_zone_name()

    # get basic AWS data and contact e-mail address from NGScloud config file
    (user_id, access_key_id, secret_access_key) = xconfiguration.get_basic_aws_data()
    email = xconfiguration.get_contact_data()

    # confirm or change the AWS data and contact e-mail address
    print(xlib.get_separator())
    user_id = cinputs.input_user_id(user_id)
    access_key_id = cinputs.input_access_key_id(access_key_id)
    secret_access_key = cinputs.input_secret_access_key(secret_access_key)
    email = cinputs.input_email(email)

    # verify the AWS access key identification and the AWS secret access key   
    print(xlib.get_separator())
    print('Verifying the AWS access key identification and the AWS secret access key')
    OK = xec2.verify_aws_credentials(access_key_id, secret_access_key)
    if OK:
        print('The credentials are OK.')
    else:
        print('ERROR: The credentials are wrong. Please review your access key identification and secret access key in the AWS web.')
        if not is_menu_call:
            raise xlib.ProgramException('EXIT')

    # confirm the creation of the NGScloud config file
    if OK:
        if is_menu_call:
            print(xlib.get_separator())
            OK = clib.confirm_action('The {0} config file is going to be created. The previous files will be lost.'.format(xlib.get_project_name()))

    # create the NGScloud config file corresponding to the environment
    if OK:
        print(xlib.get_separator())
        print('The file {0} is being created ...'.format(xconfiguration.get_ngscloud_config_file()))
        (OK, error_list) = xconfiguration.create_ngscloud_config_file(user_id, access_key_id, secret_access_key, email)
        if OK:
            print('The config file is created with default values.')
            print()
            print('You can modify the conection data and contact e-mail address in:')
            print('    "Cloud control" -> "Configuration" -> "Update connection data and contact e-mail"')
            print('The assigned region and zone are {0} and {1}, respectively. You can modify them in:'.format(xconfiguration.get_default_region_name(), xconfiguration.get_default_zone_name()))
            print('    "Cloud control" -> "Configuration" -> "Update region and zone data"')
        else:
            for error in error_list:
                print(error)
            raise xlib.ProgramException('C001')

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_view_ngscloud_config_file():
    '''
    List the NGScloud config file corresponding to the environment.
    '''

    # initialize the control variable
    OK = True

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # view the file
    text = 'Configuration - View TransciptomeCloud config file'
    OK = clib.view_file(ngscloud_config_file, text)

    # show continuation message 
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_list_templates():
    '''
    List the characteristics of the cluster templates.
    '''

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Configuration - List cluster templates')

    # get the cluster template dictionary and the template name list
    template_dict = xconfiguration.get_template_dict()
    template_name_list = xconfiguration.get_template_name_list(volume_creator_included=False)

    # list cluster templates
    print(xlib.get_separator())
    if template_name_list == []:
        print('WARNING: There is not any cluster template defined.')
    else:
        # set data width
        template_width = 30
        instance_type_width = 13
        vcpu_width = 5
        memory_width = 12
        use_width = 17
        generation_width = 10
        # set line template
        line_template = '{0:' + str(template_width) + '}   {1:' + str(instance_type_width) + '}   {2:>' + str(vcpu_width) + '}   {3:>' + str(memory_width) + '}   {4:' + str(use_width) + '}   {5:' + str(generation_width) + '}'
        # print header
        print(line_template.format('Template name', 'Instance type', 'vCPUs', 'Memory (GiB)', 'Use', 'Generation'))
        print(line_template.format('=' * template_width, '=' * instance_type_width, '=' * vcpu_width, '=' * memory_width, '=' * use_width, '=' * generation_width))
        # print detail lines
        for template_name in template_name_list:
            instance_type = template_dict[template_name]['master_instance_type']
            vcpu = template_dict[template_name]['vcpu']
            memory = template_dict[template_name]['memory']
            use = template_dict[template_name]['use']
            generation = template_dict[template_name]['generation'] 
            print(line_template.format(template_name, instance_type, vcpu, memory, use, generation))

    # show warnings about characteristics and pricing
    print(xlib.get_separator())
    print('You can consult the characteristics of the EC2 intance types in:')
    print('    https://aws.amazon.com/ec2/instance-types/')
    print('and the EC2 pricing is detailed in:')
    print('    https://aws.amazon.com/ec2/pricing/')

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_update_connection_data():
    '''
    Update the user id, access key id,  secret access key and contact e-mail address
    in the NGScloud config file corresponding to the environment.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Configuration - Update connection data')

    # get basic AWS data and contact e-mail address from NGScloud config file
    (user_id, access_key_id, secret_access_key) = xconfiguration.get_basic_aws_data()
    email = xconfiguration.get_contact_data()

    # input the new AWS data and the contact e-mail address
    print(xlib.get_separator())
    user_id = cinputs.input_user_id(user_id)
    access_key_id = cinputs.input_access_key_id(access_key_id)
    secret_access_key = cinputs.input_secret_access_key(secret_access_key)
    email = cinputs.input_email(email)

    # verify the AWS access key identification and the AWS secret access key   
    print(xlib.get_separator())
    print('Verifying the AWS access key identification and the AWS secret access key')
    OK = xec2.verify_aws_credentials(access_key_id, secret_access_key)
    if OK:
        print('The credentials are OK.')
    else:
        print('ERROR: The credentials are wrong. Please review your access key identification and secret access key in the AWS web.')

    # get the NGScloud config file
    if OK:
        ngscloud_config_file = xconfiguration.get_ngscloud_config_file()
    
    # confirm the connection data update in the NGScloud config file
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be update with the new connection data.'.format(ngscloud_config_file))

    # save the options dictionary in the NGScloud config file
    if OK:
        print(xlib.get_separator())
        print('The file {0} is being update with the new connection data ...'.format(ngscloud_config_file))
        (OK, error_list) = xconfiguration.update_connection_data(user_id, access_key_id, secret_access_key)
        if OK:
            (OK, error_list) = xconfiguration.update_contact_data(email)
        if OK:
            print('The config file has been update.')
        else:
            for error in error_list:
                print(error)
            raise xlib.ProgramException('C001')

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_update_region_zone():
    '''
    Update the current region and zone names in the NGScloud config file
    corresponding to the envoronment.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Configuration - Update region and zone')

    # input new current region and zone
    print(xlib.get_separator())
    region_name = cinputs.input_region_name(region_name, help=True)
    zone_name = cinputs.input_zone_name(region_name, zone_name, help=True)
  
    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()
  
    # confirm the region and zone update in the NGScloud config file
    print(xlib.get_separator())
    OK = clib.confirm_action('The file {0} is going to be update with the new region and zone.'.format(ngscloud_config_file))

    # save the options dictionary in the NGScloud config file
    if OK:
        print(xlib.get_separator())
        print('The file {0} is being update with the new region and zone ...'.format(ngscloud_config_file))
        (OK, error_list) = xconfiguration.update_region_zone_data(region_name, zone_name)
        if OK:
            print('The config file has been update.')
        else:
            for error in error_list:
                print(error)
            raise xlib.ProgramException('C001')

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_link_volume_to_template():
    '''
    Link a volume to a cluster template
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Configuration - Link volume in a cluster template')

    # get current zone name
    zone_name = xconfiguration.get_current_zone_name()

    # get the template name, the mount path and the volume name
    print(xlib.get_separator())
    template_name = cinputs.input_template_name(volume_creator_included=False, help=True, is_all_possible=True)
    mount_path = cinputs.input_mounting_point()
    volume_name = cinputs.input_volume_name(zone_name, template_name='', help=True, help_type='created')

    # verify there is a input volume
    if volume_name == '':
        print(xlib.get_separator())
        print('*** WARNING: There is not any volume created in the zone {0}.'.format(zone_name))
        OK = False

    # confirm the exclusion of the volume
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The volume {0} is going to be linked from the cluster template {1}.'.format(volume_name, template_name))

    # link a volume in a cluster template
    if OK:
        print(xlib.get_separator())
        print('The volume {0} is being linked from the cluster template {1}.'.format(volume_name, template_name))
        devstdout = xlib.DevStdOut(xconfiguration.link_volume_to_template.__name__)
        (OK, error_list) = xconfiguration.link_volume_to_template(template_name, mount_path, volume_name, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_delink_volume_from_template():
    '''
    Delink a volume from a cluster template
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Configuration - Delink volume in a cluster template')

    # get current zone name
    zone_name = xconfiguration.get_current_zone_name()

    # get the template name and the volume name
    print(xlib.get_separator())
    template_name = cinputs.input_template_name(volume_creator_included=False, help=True, is_all_possible=True)
    volume_name = cinputs.input_volume_name(zone_name, template_name, help=True, help_type='linked')
 
    # verify there is some volume linked to the cluster template
    if volume_name == '':
        print(xlib.get_separator())
        print('*** WARNING: There is not any volume linked to the cluster template.')
        OK = False
 
    # confirm the exclusion of the volume
    if OK:
        print(xlib.get_separator())
        if template_name == 'all':
            OK = clib.confirm_action('The volume {0} is going to be delinked from every template.'.format(volume_name))
        else:
            OK = clib.confirm_action('The volume {0} is going to be delinked from the template {0}.'.format(volume_name, template_name))

    # delink a volume in a cluster template
    if OK:
        print(xlib.get_separator())
        print('The volume {0} is being delinked from the cluster template {1}.'.format(volume_name, template_name))
        devstdout = xlib.DevStdOut(xconfiguration.delink_volume_from_template.__name__)
        (OK, error_list) = xconfiguration.delink_volume_from_template(template_name, volume_name, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_review_volume_links():
    '''
    Review linked volumes of cluster templates in order to remove linked volumes
    that do not currently exist.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Configuration - Review volumes linked to cluster templates')

    # get current zone name
    zone_name = xconfiguration.get_current_zone_name()

    # get the NGScloud confign file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # verify if there are any volumes linked
    if xconfiguration.get_volumes_dict() == {}:
        print(xlib.get_separator())
        print('WARNING: There is not any volume linked.')
        OK = False
 
    # confirm the review of volumes links
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The file {0} is going to be reviewed in order to remove volumes linked which are not currently created in the zone {1}.'.format(ngscloud_config_file, zone_name))

    # review volumen link
    if OK:
        devstdout = xlib.DevStdOut(xconfiguration.review_volume_links.__name__)
        (OK, error_list) = xconfiguration.review_volume_links(zone_name, devstdout, function=None)

    # show continuation message or exit of application
    print(xlib.get_separator())
    if not OK and error_list != []:
        raise xlib.ProgramException('C001')
    else:
        input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_list_keypairs():
    '''
    List the key pairs of a region.
    '''

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Security - List key pairs')

    # get the key pair dictionary and the keypair names list
    keypairs_dict = xec2.get_keypair_dict(region_name)
    keypair_keys_list = sorted(keypairs_dict.keys())
 
    # list keypairs
    print(xlib.get_separator())
    if keypair_keys_list == []:
        print('WARNING: There is not any keypair created in the region {0}.'.format(region_name))
    else:
        # set data width
        keypair_name_width = 25
        fingerprint_width = 59
        # set line template
        line_template = '{0:' + str(keypair_name_width) + '}   {1:' + str(fingerprint_width) + '}'
        # print header
        print(line_template.format('Key Pair Name', 'Fingerprint'))
        print(line_template.format('=' * keypair_name_width, '=' * fingerprint_width))
        # print detail lines
        for keypair_key in keypair_keys_list:
            keypair_name = keypairs_dict[keypair_key]['keypair_name']
            fingerprint = keypairs_dict[keypair_key]['fingerprint']
            print(line_template.format(keypair_name, fingerprint))

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_create_keypairs():
    '''
    Create the key pairs of a region.
    '''

    # initialize the control variable
    OK = True

    # print the header and get the cluster name
    clib.clear_screen()
    clib.print_headers_with_environment('Security - Create key pairs')

    # get current region name
    region_name = xconfiguration.get_current_region_name()

    # confirm the creation of the key pairs
    print(xlib.get_separator())
    OK = clib.confirm_action('The key pairs of the region {0} are going to be created.'.format(region_name))

    # create key pairs
    if OK:
        print(xlib.get_separator())
        print('The key pairs of the region {0} are been created ...'.format(region_name))
        (OK, error_list) = xec2.create_keypairs(region_name)
        if OK:
            print('The key pairs and their corresponding local files have been created.')
        else:
            for error in error_list:
                print(error)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_list_clusters():
    '''
    List clusters.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Cluster operation - List clusters')

    # list clusters
    devstdout = xlib.DevStdOut(xcluster.list_clusters.__name__)
    OK = xcluster.list_clusters(devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_create_cluster():
    '''
    Create a cluster from a template name.
    '''

    # initialize the control variable
    OK = True

    # initialize the state variables
    master_state_code = ''
    master_state_name = ''

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Cluster operation - Create cluster')

    # show sites related to EBS volumes
    print(xlib.get_separator())
    print('You can consult the characteristics of the EC2 intance types in:')
    print('    https://aws.amazon.com/ec2/instance-types/')
    print('and the EC2 pricing is detailed in:')
    print('    https://aws.amazon.com/ec2/pricing/')
    print()

    # get the template name and set the cluster name
    print(xlib.get_separator())
    template_name = cinputs.input_template_name(volume_creator_included=False, help=True, is_all_possible=False)
    cluster_name = template_name

    # confirm the creation of the cluster
    print(xlib.get_separator())
    OK = clib.confirm_action('The cluster is going to be created.')

    # create the cluster
    if OK:
        devstdout = xlib.DevStdOut(xcluster.create_cluster.__name__)
        (OK, master_state_code, master_state_name) = xcluster.create_cluster(template_name, cluster_name, devstdout, function=None, is_menu_call=True)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_stop_cluster():
    '''
    Stop, but not terminate, a cluster.Then it must be restarted.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Cluster operation - Stop cluster')

    # get the cluster name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # confirm the stop of the cluster
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The cluster is going to be stopped, not terminated. Then it must be restarted.')

    # stop the cluster
    if OK:
        devstdout = xlib.DevStdOut(xcluster.stop_cluster.__name__)
        OK = xcluster.stop_cluster(cluster_name, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_restart_cluster():
    '''
    Restart a cluster.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Cluster operation - Restart cluster')

    # get the cluster name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # confirm the restarting of the cluster
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The cluster is going to be restarted.')

    # stop the cluster
    if OK:
        devstdout = xlib.DevStdOut(xcluster.restart_cluster.__name__)
        OK = xcluster.restart_cluster(cluster_name, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_terminate_cluster(force):
    '''
    Terminate a cluster.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    if not force:
        clib.print_headers_with_environment('Cluster operation - Terminate cluster')
    else:
        clib.print_headers_with_environment('Cluster operation - Force termination of a cluster')

    # get the cluster name that must be terminated
    print(xlib.get_separator())
    if not force:
        if xec2.get_running_cluster_list(volume_creator_included=False) == []:
            print('WARNING: There is not any running cluster.')
            OK = False
        else:
            cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)
    else:
        cluster_name = cinputs.input_template_name(volume_creator_included=False, help=False, is_all_possible=False)

    # confirm the termination of the cluster
    if OK:
        print(xlib.get_separator())
        if not force:
            OK = clib.confirm_action('The cluster is going to be terminated.')
        else:
            OK = clib.confirm_action('The cluster is going to be forced to terminate.')

    # terminate the cluster
    if OK:
        devstdout = xlib.DevStdOut(xcluster.terminate_cluster.__name__)
        OK = xcluster.terminate_cluster(cluster_name, force, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_show_cluster_composing():
    '''
    Show cluster information of every node: OS, CPU number and memory.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Cluster operation - Show cluster composing')

    # get the cluster name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) == []:
        print('WARNING: There is not any running cluster.')
        OK = False
    else:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)

    # show the status of batch jobs
    if OK:
        devstdout = xlib.DevStdOut(xcluster.show_cluster_composing.__name__)
        xcluster.show_cluster_composing(cluster_name, devstdout, function=None)

    # show continuation message
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_show_status_batch_jobs():
    '''
    Show the status of batch jobs in the cluster.
    '''

    # initialize the control variable
    OK = True

    # initialize the list of identification of the batch jobs
    batch_job_id_list = []

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Cluster operation - Show status batch jobs')

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
            print(error)

    # get the batch job dictionary
    if help:
        (OK, error_list, batch_job_dict) = xcluster.get_batch_job_dict(ssh_client)

    # build the list of identifications of the batch jobs
    if OK and help:
        for job_id in batch_job_dict.keys():
            batch_job_id_list.append(job_id)
        if batch_job_id_list != []:
            batch_job_id_list.sort()
        else:
            print('WARNING: There is not any batch job.')
            OK = False

    # print the batch jobs
    if OK and help:
        print(xlib.get_separator())
        # set data width
        job_id_width = 6
        job_name_width = 10
        state_width = 15
        start_date_width = 10
        start_time_width = 10
        # set line template
        line_template = '{0:' + str(job_id_width) + '} {1:' + str(job_name_width) + '} {2:' + str(state_width) + '} {3:' + str(start_date_width) + '} {4:' + str(start_time_width) + '}'
        # print header
        print(line_template.format('Job id', 'Job name', 'State', 'Start date', 'Start time'))
        print(line_template.format('=' * job_id_width, '=' * job_name_width, '=' * state_width, '=' * start_date_width, '=' * start_time_width))
        # print detail lines
        for job_id in batch_job_id_list:
            job_name = batch_job_dict[job_id]['job_name']
            state = batch_job_dict[job_id]['state']
            start_date = batch_job_dict[job_id]['start_date']
            start_time = batch_job_dict[job_id]['start_time']
            print(line_template.format(job_id, job_name, state, start_date, start_time))

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_kill_batch_job():
    '''
    Kill a batch job in the cluster.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Cluster operation - Kill batch job')

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
            print(error)

    # get the batch job identificaction
    if OK:
        batch_job_id = cinputs.input_batch_job_id(ssh_client, help=True)
        if batch_job_id == '':
            print('WARNING: There is not any batch job.')
            OK = False

    # confirm the kill of the batch job
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The batch job {0} is going to be killed.'.format(batch_job_id))

    # kill the batch job
    if OK:
        devstdout = xlib.DevStdOut(xcluster.kill_batch_job.__name__)
        xcluster.kill_batch_job(cluster_name, batch_job_id, devstdout, function=None)

    # close the SSH client connection
    if OK:
        xssh.close_ssh_client_connection(ssh_client)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_list_nodes():
    '''
    List nodes running.
    '''

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Node operation - List nodes')

    # get the node dictionary and node key list
    node_dict = xec2.get_node_dict()
    node_key_list = sorted(node_dict.keys())

    # list nodes
    print(xlib.get_separator())
    if node_key_list == []:
        print('WARNING: There is not any node running.')
    else:
        # set data width
        security_group_name_width = 28
        zone_name_width = 20
        node_name_width = 20
        node_id_width = 19
        state_width = 20
        # set line template
        line_template = '{0:' + str(security_group_name_width) + '}   {1:' + str(zone_name_width) + '}   {2:' + str(node_name_width) + '}   {3:' + str(node_id_width) + '}   {4:' + str(state_width) + '}'
        # print header
        print(line_template.format('Security Group', 'Zone', 'Node Name', 'Node Id', 'State'))
        print(line_template.format('=' * security_group_name_width, '=' * zone_name_width, '=' * node_name_width, '=' * node_id_width, '=' * state_width))
        # print detail lines
        for node_key in node_key_list:
            security_group_name = node_dict[node_key]['security_group_name']
            zone_name = node_dict[node_key]['zone_name']
            node_name = node_dict[node_key]['node_name']
            node_id = node_dict[node_key]['node_id'] 
            state = node_dict[node_key]['state']
            print(line_template.format(security_group_name, zone_name, node_name, node_id, state))

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_add_node():
    '''
    Add a node in a cluster.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Node operation - Add node in a cluster')

    # get the cluster name and node name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) != []:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)
        if len(xec2.get_cluster_node_list(cluster_name)) >= xec2.get_max_node_number():
            print('WARNING: The maximum number ({0}) of instances is already running.'.format(xec2.get_max_node_number()))
            OK = False
        else:
            node_name = cinputs.input_node_name(cluster_name, new=True, is_master_valid=False, help=True)
    else:
        print('WARNING: There is not any running cluster.')
        OK = False

    # confirm the addition of the node in the cluster
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The node is going to be added.')

    # add node in cluster
    if OK:
        devstdout = xlib.DevStdOut(xnode.add_node.__name__)
        xnode.add_node(cluster_name, node_name, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_remove_node():
    '''
    Remove a node in a cluster.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Node operation - Remove node in a cluster')

    # get the cluster name and node name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) != []:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)
        node_name = cinputs.input_node_name(cluster_name, new=False, is_master_valid=False, help=True)
        if node_name == []:
            print('WARNING: There is not any running node besides the master.')
            OK = False
    else:
        print('WARNING: There is not any running cluster.')
        OK = False

    # confirm the removal of the node in the cluster
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The node is going to be removed.')

    # remove node
    if OK:
        devstdout = xlib.DevStdOut(xnode.remove_node.__name__)
        xnode.remove_node(cluster_name, node_name, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_list_volumes():
    '''
    List volumes created.
    '''

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Volume operation - List volumes')

    # get the volume dictionary and volume key list
    volumes_dict = xec2.get_volume_dict()
    volume_keys_list = sorted(volumes_dict.keys())

    # list volume
    print(xlib.get_separator())
    if volume_keys_list == []:
        print('WARNING: There is not any volume created.')
    else:
        # set data width
        zone_name_width = 20
        volume_name_width = 20
        volume_id_width = 21
        size_width = 10
        state_width = 10
        attachments_number_width = 11
        # set line template
        line_template = '{0:' + str(zone_name_width) + '}   {1:' + str(volume_name_width) + '}   {2:' + str(volume_id_width) + '}   {3:' + str(size_width) + '}   {4:' + str(state_width) + '}   {5:' + str(attachments_number_width) + '}'
        # print header
        print(line_template.format('Zone', 'Volume Name', 'Volume Id', 'Size (GiB)', 'State', 'Attachments'))
        print(line_template.format('=' * zone_name_width, '=' * volume_name_width, '=' * volume_id_width, '=' * size_width, '=' * state_width, '=' * attachments_number_width))
        # print detail lines
        for volume_key in volume_keys_list:
            zone_name = volumes_dict[volume_key]['zone_name']
            volume_name = volumes_dict[volume_key]['volume_name'] 
            volume_id = volumes_dict[volume_key]['volume_id']
            size = volumes_dict[volume_key]['size']
            state = volumes_dict[volume_key]['state']
            attachments_number = volumes_dict[volume_key]['attachments_number']
            print(line_template.format(zone_name, volume_name, volume_id, size, state, attachments_number))

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_create_volume():
    '''
    Create a volume in the current zone.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Volume operation - Create volume')

    # get current zone name
    zone_name = xconfiguration.get_current_zone_name()

    # show sites related to EBS volumes
    print(xlib.get_separator())
    print('You can consult the characteristics of the EBS volumes in:')
    print('    https://aws.amazon.com/ebs/details/')
    print('and the EBS pricing is detailed in:')
    print('    https://aws.amazon.com/ebs/pricing/')

    # get the cluster name, node name, volume name, volume type and volume size
    print(xlib.get_separator())
    volume_name = cinputs.input_volume_name(zone_name, template_name='', help=False, help_type='created')
    volume_type = cinputs.input_volume_type()
    volume_size = cinputs.input_volume_size(volume_type)
    terminate_indicator = cinputs.input_terminate_indicator()

    # confirm the creation of the volume
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The volume is going to be created.')

    # create the volume
    if OK:
        devstdout = xlib.DevStdOut(xvolume.create_volume.__name__)
        OK = xvolume.create_volume(volume_name, volume_type, volume_size, terminate_indicator, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_remove_volume():
    '''
    Remove a volume in the current zone.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Volume operation - Remove volume')

    # get current zone name
    zone_name = xconfiguration.get_current_zone_name()

    # get the volume name
    print(xlib.get_separator())
    volume_name = cinputs.input_volume_name(zone_name, template_name='', help=True, help_type='created')

    # confirm the removal of the volume
    print(xlib.get_separator())
    OK = clib.confirm_action('The volume is going to be removed.')

    # remove the volume
    if OK:
        devstdout = xlib.DevStdOut(xvolume.remove_volume.__name__)
        OK = xvolume.remove_volume(volume_name, devstdout, function=None)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_terminate_volume_creator():
    '''
    Terminate de volume creator of the current zone.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Volume operation - Terminate volume creator')

    # confirm the termination of the volume creator
    print(xlib.get_separator())
    OK = clib.confirm_action('The volume creator is going to be terminated.')

    # terminate the volume creator
    if OK:
        devstdout = xlib.DevStdOut(xcluster.terminate_cluster.__name__)
        xcluster.terminate_cluster(xlib.get_volume_creator_name(), True, devstdout, function=None, is_menu_call=False)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_mount_volume():
    '''
    Mount a volume in a node.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Volume operation - Mount volume in a node')

    # get current zone name
    zone_name = xconfiguration.get_current_zone_name()

    # get the cluster name and node name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) != []:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)
        node_name = cinputs.input_node_name(cluster_name, new=False, is_master_valid=True, help=True)
    else:
        print('WARNING: There is not any running cluster.')
        OK = False

    # get the volume name, AWS device file and directory path
    if OK:
        volume_name = cinputs.input_volume_name(zone_name, template_name='', help=True, help_type='created')
        aws_device_file = cinputs.input_device_file(node_name, volume_name)
        mounting_path = cinputs.input_mounting_path(node_name, aws_device_file)

    # confirm the mounting of the volume
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The volume is going to be mounted.')

    # mount the volume in the node
    if OK:
        devstdout = xlib.DevStdOut(xvolume.mount_volume.__name__)
        xvolume.mount_volume(cluster_name, node_name, volume_name, aws_device_file, mounting_path, devstdout, function=None, is_menu_call=True)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_unmount_volume():
    '''
    Unmount a volume in a node.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Volume operation - Unmount volume in a node')

    # get current zone name
    zone_name = xconfiguration.get_current_zone_name()

    # get the cluster name and node name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) != []:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)
        node_name = cinputs.input_node_name(cluster_name, new=False, is_master_valid=True, help=True)
    else:
        print('WARNING: There is not any running cluster.')
        OK = False

    # get the volume name
    if OK:
        volume_name = cinputs.input_volume_name(zone_name, template_name='', help=False, help_type='created')

    # confirm the unmounting of the volume
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The volume is going to be unmounted.')

    # unmount the volume in the node
    if OK:
        devstdout = xlib.DevStdOut(xvolume.unmount_volume.__name__)
        xvolume.unmount_volume(cluster_name, node_name, volume_name, devstdout, function=None, is_menu_call=True)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

def form_open_terminal():
    '''
    Open a terminal windows of a cluster node.
    '''

    # initialize the control variable
    OK = True

    # print the header
    clib.clear_screen()
    clib.print_headers_with_environment('Cloud control - Open a terminal')

    # get the cluster name and node name
    print(xlib.get_separator())
    if xec2.get_running_cluster_list(volume_creator_included=False) != []:
        cluster_name = cinputs.input_cluster_name(volume_creator_included=False, help=True)
        node_name = cinputs.input_node_name(cluster_name, new=False, is_master_valid=True, help=True)
    else:
        print('WARNING: There is not any running cluster.')
        OK = False

    # confirm the terminal opening
    if OK:
        print(xlib.get_separator())
        OK = clib.confirm_action('The terminal is going to be opened using StarCluster.')

    # open de terminal
    if OK:
        xcluster.open_terminal(cluster_name, node_name)

    # show continuation message 
    print(xlib.get_separator())
    input('Press [Intro] to continue ...')

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains the functions related to forms corresponding to Cloud Control menu items in console mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
