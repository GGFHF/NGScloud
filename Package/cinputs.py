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
This file contains the general functions to data inputs in mode console.
'''

#-------------------------------------------------------------------------------

import os
import re
import sys

import xconfiguration
import xcluster
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def input_code(code_text, code_list):
    '''
    Input a selected code from a code list.
    '''

    # initialize the code
    code = ''

    # convert codes to lowercase letters
    for i in range(len(code_list)):
        code_list[i] = code_list[i].lower()

    # get the code list text
    code_list_text = str(code_list).strip('[]').replace('\'','')
    code_list_text = code_list_text.replace(',', ' or')

    # input and validate the code
    while code == '':
        code = input('{0} ({1})?: '.format(code_text, code_list_text)).lower()
        if code not in code_list:
            print('*** ERROR: {0} is not {1}.'.format(code, code_list_text))
            code = ''

    # return the code
    return code

#-------------------------------------------------------------------------------

def input_access_key_id(default_access_key_id):
    '''
    Input the access key identification.
    '''

    # initialize the access key identification
    access_key_id = ''

    # input and validate the access key identification
    while access_key_id == '':
        if default_access_key_id != '':
            access_key_id = input('Enter the AWS access key id [{0}]: '.format(default_access_key_id))
            if access_key_id == '':
                access_key_id = default_access_key_id
        else:
            access_key_id = input('Enter the AWS access key id: ')

    # return the access key identification
    return access_key_id

#-------------------------------------------------------------------------------

def input_secret_access_key(default_secret_access_key):
    '''
    Input the secret access key.
    '''

    # initialize the secret access key
    secret_access_key = ''

    # input and validate the secret access key
    while secret_access_key == '':
        if default_secret_access_key != '':
            secret_access_key = input('Enter the AWS secret access key [{0}]: '.format(default_secret_access_key[:5] + '*****' + default_secret_access_key[len(default_secret_access_key)-5:]))
            if secret_access_key == '':
                secret_access_key = default_secret_access_key
        else:
            secret_access_key = input('Enter the AWS secret access key: ')

    # return the secret access key
    return secret_access_key

#-------------------------------------------------------------------------------

def input_user_id(default_user_id):
    '''
    Input the user identification.
    '''

    # initialize the user identification
    user_id = ''

    # input and validate the user identification
    while user_id == '':
        if default_user_id != '':
            user_id = input('Enter the AWS user id [{0}]: '.format(default_user_id))
            if user_id == '':
                user_id = default_user_id
        else:
            user_id = input('Enter the AWS user id: ')

    # return the user identification
    return user_id

#-------------------------------------------------------------------------------

def input_email(default_email):
    '''
    Input the contact e-mail address.
    '''

    # initialize the contact e-mail address
    email = ''

    # input and validate the contact e-mail address
    while email == '':
        if default_email != '':
            email = input('Enter the contact e-mail [{0}]: '.format(default_email))
            if email == '':
                email = default_email
            elif not xlib.is_valid_email_address(email):
                print('*** ERROR: {0} is not a valid e-mail address.'.format(email))
                email = ''
        else:
            email = input('Enter the contact e-mail: ')

    # return the contact e-mail address
    return email

#-------------------------------------------------------------------------------

def input_region_name(default_region_name, help):
    '''
    Input the region name.
    '''

    # initialize the control variable
    OK = True

    # initialize the region name
    region_name = ''

    # get the available region name list
    if help:
        available_region_names_list = xec2.get_available_region_list()
        if available_region_names_list == []:
            OK = False

    # verify that the default region name is available
    if OK and help:
        if default_region_name not in available_region_names_list:
            default_region_name = ''

    # print the available region names
    if OK and help:
        print('Available region names: {0} ...'.format(str(available_region_names_list).strip('[]').replace('\'','')))

    # input and validate the region name
    if OK:
        while region_name == '':
            if help:
                if default_region_name != '':
                    region_name = input('... Enter the region name [{0}]: '.format(default_region_name))
                else:
                    region_name = input('... Enter the region name: ')
                if region_name == '':
                    region_name = default_region_name
                elif region_name not in available_region_names_list:
                    print('*** ERROR: {0} is not available.'.format(region_name))
                    region_name = ''
            else:
                if default_region_name != '':
                    region_name = input('Enter the region name [{0}]: '.format(default_region_name))
                else:
                    region_name = input('Enter the region name: ')
                if region_name == '':
                    region_name = default_region_name

    # return the region name
    return region_name

#-------------------------------------------------------------------------------

def input_zone_name(region_name, default_zone_name, help):
    '''
    Input the zone name.
    '''

    # initialize the control variable
    OK = True

    # initialize the zone name
    zone_name = ''

    # get the available zone name list of the region
    if help:
        available_zone_names_list = xec2.get_available_zone_list(region_name)
        if available_zone_names_list == []:
            OK = False

    # verify that the default zone name is available
    if OK and help:
        if default_zone_name not in available_zone_names_list:
            default_zone_name = ''

    # print the available zone names
    if OK and help:
        print('Available zone names: {0} ... '.format(str(available_zone_names_list).strip('[]').replace('\'','')))

    # input and validate the zone name
    if OK:
        while zone_name == '':
            if help:
                if default_zone_name != '':
                    zone_name = input('... Enter the zone name [{0}]: '.format(default_zone_name))
                else:
                    zone_name = input('... Enter the zone name: ')
                if zone_name == '':
                    zone_name = default_zone_name
                elif zone_name not in available_zone_names_list:
                    print('*** ERROR: {0} is not available.'.format(zone_name))
                    zone_name = ''
            else:
                if default_zone_name != '':
                    zone_name = input('Enter the zone name [{0}]: '.format(default_zone_name))
                else:
                    zone_name = input('Enter the zone name: ')
                if zone_name == '':
                    zone_name = default_zone_name

    # return the zone name
    return zone_name

#-------------------------------------------------------------------------------

def input_template_name(volume_creator_included, help, is_all_possible):
    '''
    Input the cluster template name.
    '''

    # initialize the control variable
    OK = True

    # initialize the template name
    template_name = ''

    # get the cluster template dictionary and the template names list
    if help:
        template_dict = xconfiguration.get_template_dict()
        template_name_list = xconfiguration.get_template_name_list(volume_creator_included)
        if template_name_list == []:
            OK = False

    # print the defined templates
    if OK and help:
        # set data width
        template_width = 30
        description_width = 80
        # set line template
        line_template = '{0:' + str(template_width) + '} {1:' + str(description_width) + '}'
        # print header
        print('Defined cluster templates:')
        print()
        print(line_template.format('Template name', 'Description'))
        print(line_template.format('=' * template_width, '=' * description_width))
        # print detail lines
        for defined_template_name in template_name_list:
            description = '{0}'.format(template_dict[defined_template_name]['description'])
            print(line_template.format(defined_template_name, description))
        if is_all_possible:
            template_name_list.append('all')
            print(line_template.format('all', 'all the cluster templates'))
        print()

    # input and validate the template name
    if OK:
        while template_name == '':
            if help:
                template_name = input('... Enter the template name: ')
                if template_name not in template_name_list:
                    print('*** ERROR: {0} is not defined.'.format(template_name))
                    template_name = ''
            else:
                template_name = input('Enter the template name: ')

    # return the template name
    return template_name

#-------------------------------------------------------------------------------

def input_cluster_name(volume_creator_included, help):
    '''
    Input the cluster name.
    '''

    # initialize the control variable
    OK = True

    # initialize the default cluster name
    default_cluster_name = ''

    # initialize the cluster name
    cluster_name = ''

    # get the running cluster list
    if help:
        clusters_running_list = xec2.get_running_cluster_list(volume_creator_included)
        if clusters_running_list == []:
            OK = False
        elif len(clusters_running_list) == 1:
            default_cluster_name = clusters_running_list[0]

    # print the running clusters
    if OK and help:
        print('Running clusters: {0} ...'.format(str(clusters_running_list).strip('[]').replace('\'','')))

    # input and validate the cluster name
    if OK:
        while cluster_name == '':
            if help:
                if default_cluster_name != '':
                    cluster_name = input('... Enter the cluster name [{0}]: '.format(default_cluster_name))
                else:
                    cluster_name = input('... Enter the cluster name: ')
                if cluster_name == '':
                    cluster_name = default_cluster_name
                elif cluster_name not in clusters_running_list:
                    print('*** ERROR: {0} is not running.'.format(cluster_name))
                    cluster_name = ''
            else:
                cluster_name = input('Enter the cluster name: ')

    # return the cluster name
    return cluster_name

#-------------------------------------------------------------------------------

def input_node_name(cluster_name, new, is_master_valid, help):
    '''
    Input the node name.
    '''

    # initialize the control variable
    OK = True

    # initialize the node name
    node_name = ''

    # get the running node list
    running_node_name_list = xec2.get_cluster_node_list(cluster_name)

    # get the valid node list
    valid_node_name_list = running_node_name_list
    if not is_master_valid:
        if valid_node_name_list.remove('master') == []:
            OK = False

    # print the running nodes
    if OK:
        if help:
            print('Running nodes: {0} ...'.format(str(valid_node_name_list).strip('[]').replace('\'','')))

    # input and validate the node name
    if OK:
        while node_name == '':
            if help:
                node_name = input('... Enter the node name: ')
            else:
                node_name = input('Enter the node name: ')

            if not is_master_valid and node_name == 'master':
                print('*** ERROR: master is not a node name valid.')
                node_name = ''
            elif not node_name.isalnum() or not node_name[0].isalpha():
                print('*** ERROR: {0} is not an alphanumeric string or the first character is not alphabetic'.format(node_name))
                node_name = ''
            elif new and node_name in running_node_name_list:
                print('*** ERROR: {0} is already running..'.format(node_name))
                node_name = ''
            elif not new and node_name not in running_node_name_list:
                print('*** ERROR: {0} is not running.'.format(node_name))
                node_name = ''

    # return the node name
    return node_name

#-------------------------------------------------------------------------------

def input_volume_name(zone_name, template_name, help, help_type):
    '''
    Input the volume name.
    '''

    # initialize the control variable
    OK = True

    # initialize the volume name
    volume_name = ''

    # get the available volume list
    if help:
        if help_type == 'created' or template_name == 'all':
            volume_names_list = xec2.get_created_volume_name_list(zone_name)
        elif help_type == 'linked':
            volume_names_list = xconfiguration.get_linked_volumes_list(template_name)
        if volume_names_list == [] or volume_names_list == ['']:
            OK = False

    # print the available volumes
    if OK and help:
        print('Available volumes: {0} ...'.format(str(volume_names_list).strip('[]').replace('\'','')))

    # input and validate the volume name
    if OK:
        while volume_name == '':
            if help:
                volume_name = input('... Enter the volume name: ')
                if volume_name not in volume_names_list:
                    print('*** ERROR: {0} is not available.'.format(volume_name))
                    volume_name = ''
            else:
                volume_name = input('Enter the volume name: ')

    # return the volume name
    return volume_name


#-------------------------------------------------------------------------------

def input_volume_type():
    '''
    Input the volume type.
    '''

    # initialize the control variable
    OK = True

    # initialize the volume type and the default volume type
    volume_type = ''
    default_volume_type = 'standard'

    # get the volume type list
    volume_type_list = xec2.get_volume_type_id_list()

    # print the available volumes
    if OK and help:
        print('Volume types: {0} ...'.format(str(volume_type_list).strip('[]').replace('\'','')))

    # input and validate the volume type
    if OK:
        while volume_type == '':
            if help:
                volume_type = input('... Enter the volume name [{0}]: '.format(default_volume_type))
                if volume_type == '':
                    volume_type = default_volume_type
                if volume_type not in volume_type_list:
                    print('*** ERROR: {0} is not a volume type.'.format(volume_type))
                    volume_type = ''
            else:
                volume_type = input('Enter the volume type: ')

    # return the volume name
    return volume_type

#-------------------------------------------------------------------------------

def input_volume_size(volume_type):
    '''
    Input the volume size name.
    '''

    # initialize the volume size
    volume_size = 0

    # get the volume type dictinary
    volume_type_dict = xec2.get_volume_type_dict()

    # get the minimum and maximum size of the volume type
    minimum_size = volume_type_dict[volume_type]['minimum_size']
    maximum_size = volume_type_dict[volume_type]['maximum_size']

    # input and validate the volume name
    while volume_size < minimum_size or volume_size > maximum_size:
        try:
            volume_size_text = input('Enter the volume size (in GiB, integer between {0} and {1}): '.format(minimum_size, maximum_size))
            volume_size = int(volume_size_text)
        except:
            print('ERROR: {0} is not bwtween {1} and {2}'.format(volume_size_text, minimum_size, maximum_size))
            volume_size = 0
        else:
            if volume_size < minimum_size or volume_size > maximum_size:
                print('ERROR: {0} is not bwtween {1} and {2}'.format(volume_size_text, minimum_size, maximum_size))

   # return the volume size
    return volume_size

#-------------------------------------------------------------------------------

def input_device_file(node_name, volume_name):
    '''
    Input the node device file where the volume is going to be attached.
    '''

    # initialize the device file pattern, the default device file and the device file
    device_file_pattern = '/dev/sd[f-o]'
    default_device_file = '/dev/sdf'
    device_file = ''

    # input and validate the device file
    while device_file == '':
        device_file = input('Enter the device file of {0} where {1} is going to be attached [{2}]: '.format(node_name, volume_name, default_device_file))
        if device_file == '':
            device_file = default_device_file
        elif not xlib.is_device_file(device_file, device_file_pattern):
            print('***ERROR: The device file must have a pattern {0}'.format(device_file_pattern))
            device_file = ''

   # return the defice file
    return device_file

#-------------------------------------------------------------------------------

def input_terminate_indicator():
    '''
    Input the anwser about if it is necessary to terminate the volume creator.
    '''

    # initialize the terminate indicator
    terminate_indicator = ''

    # input and validate the terminate indicator
    while terminate_indicator == '':
        terminate_indicator = input('Is necessary to terminate the volume creator (Y/N)?: ').upper()
        if terminate_indicator not in ['Y', 'N']:
            print('*** ERROR: {0} is not Y or N.'.format(terminate_indicator))
            terminate_indicator = ''

    # return the terminate indicator
    return True if terminate_indicator == 'Y' else False

#-------------------------------------------------------------------------------

def input_local_dir(files_type):
    '''
    Input a local directory path.
    '''

    # initialize the local directory path
    local_dir = ''

    # set the input message text
    if files_type == 'reference':
        message_text = 'Enter the local directory where the reference files are: '
    if files_type == 'database':
        message_text = 'Enter the local directory where the built database files are: '
    elif files_type == 'read':
        message_text = 'Enter the local directory where the read files are: '
    elif files_type == 'result':
        message_text = 'Enter the local directory where the result files will be download: '

    # input and validate the local directory path
    while local_dir == '':
        local_dir = input(message_text)
        # if not xlib.is_path_valid(directoy_path):
        if not xlib.existing_dir(local_dir):
            print('***ERROR: The directory {0} does not exist.'.format(local_dir))
            local_dir = ''

   # return the mounting path
    return local_dir

#-------------------------------------------------------------------------------

def input_cluster_directory(files_type):
    '''
    Input a local directory path.
    '''

    # initialize the local directory path
    directoy_path = ''

    # set the input message text
    if files_type == 'reference':
        message_text = 'Enter the subdirectory /references where the references will be upload: '
    elif files_type == 'database':
        message_text = 'Enter the subdirectory /databases where the references will be upload: '

    # input and validate the local directory path
    while directoy_path == '':
        directoy_path = input(message_text)
        if not xlib.is_valid_path(directoy_path):
            print('***ERROR: The directory {0} does not valid.'.format(directoy_path))
            directoy_path = ''

   # return the mounting path
    return directoy_path

#-------------------------------------------------------------------------------

def input_mounting_path(node_name, device_file):
    '''
    Input the node directory path where the device file is going to be mounted.
    '''

    # initialize the mounting path
    mounting_path = ''

    # input and validate the mounting path
    while mounting_path == '':
        mounting_path = input('Enter the absolute directory path in {0} where {1} is going to be mounted: '.format(node_name, device_file))
        if not xlib.is_absolute_path(mounting_path, 'linux'):
            print('***ERROR: {0} is not an absolute path.'.format(mounting_path))
            mounting_path = ''

   # return the mounting path
    return mounting_path

#-------------------------------------------------------------------------------

def input_mounting_point():
    '''
    Input the mounting point of a volume in the cluster templates.
    '''

    # get mounting points list
    mounting_points_list = xlib.get_mounting_point_list()

    # print the available volumes
    if help:
        print('Available mounting points: {0} ...'.format(str(mounting_points_list).strip('[]').replace('\'','')))

    # initialize the mounting poing
    mounting_point = ''

    # input and validate the mounting poing
    while mounting_point == '':
        mounting_point = input('... Enter the mounting point: ')
        if mounting_point not in mounting_points_list:
            print('*** ERROR: {0} is not valid.'.format(mounting_point))
            mounting_point = ''

   # return the mounting point
    return mounting_point

#-------------------------------------------------------------------------------

def input_reference_dataset_id(ssh_client, allowed_none, help):
    '''
    Input the reference dataset identification in the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the reference dataset identification
    reference_dataset_id = ''

    # initialize the reference dataset identification list
    reference_dataset_id_list = []

    # get the reference dataset identifications
    if help:
        command = 'ls {0}'.format(xlib.get_cluster_reference_dir())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    reference_dataset_id_list.append(line)

    # print the reference identifications in the clusters
    if OK and help:
        if reference_dataset_id_list != []:
            print('Reference dataset ids existing in the cluster: {0} ...'.format(str(reference_dataset_id_list).strip('[]').replace('\'','')))
        else:
            OK = False

    # input and validate the reference dataset identification
    if OK:
        if allowed_none == True:
            reference_dataset_id_list.append('NONE')
        while reference_dataset_id == '':
            if help:
                if allowed_none == True:
                    reference_dataset_id = input('... Enter the reference dataset id or NONE: ')
                else:
                    reference_dataset_id = input('... Enter the reference dataset id: ')
                if reference_dataset_id not in reference_dataset_id_list:
                    print('*** ERROR: {0} does not exist.'.format(reference_dataset_id))
                    reference_dataset_id = ''
            else:
                reference_dataset_id = input('Enter the reference dataset id: ')
                if not reference_dataset_id.isidentifier():
                    print('*** ERROR: The reference id has some non-alphanumeric characters.')
                    reference_dataset_id = ''

    # return the reference dataset identification
    return reference_dataset_id

#-------------------------------------------------------------------------------

def input_reference_file(ssh_client, reference_dataset_id, help):
    '''
    Input the reference file of a reference dataset in the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the reference file
    reference_file = ''

    # initialize the reference file list
    reference_file_list = []

    # get the reference files of the reference dataset identification
    if help:
        command = 'find {0} -maxdepth 1 -type f'.format(xlib.get_cluster_reference_dataset_dir(reference_dataset_id))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found' and line.lower().find('gtf') == -1:
                    reference_file_list.append(os.path.basename(line))

    # print the reference files in the clusters
    if OK and help:
        if reference_file_list != []:
            print('Reference files existing in the reference dataset: {0} ...'.format(str(reference_file_list).strip('[]').replace('\'','')))
        else:
            OK = False

    # input and validate the reference file
    if OK:
        while reference_file == '':
            if help:
                reference_file = input('... Enter the reference file: ')
                if reference_file not in reference_file_list:
                    print('*** ERROR: {0} does not exist.'.format(reference_file))
                    reference_file = ''
            else:
                reference_file = input('Enter the reference file: ')
                if not reference_file.isidentifier():
                    print('*** ERROR: The reference file has some non-alphanumeric characters.')
                    reference_file = ''

    # return the reference dataset identification
    return reference_file

#-------------------------------------------------------------------------------

def input_gtf_file(ssh_client, reference_dataset_id, help):
    '''
    Input the GTF file of a reference dataset in the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the GTF file
    gtf_file = ''

    # initialize the GTF file list
    gtf_file_list = []

    # get the GTF files of the reference dataset identification
    if help:
        command = 'find {0} -maxdepth 1 -type f'.format(xlib.get_cluster_reference_dataset_dir(reference_dataset_id))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found' and line.lower().find('gtf') > -1:
                    gtf_file_list.append(os.path.basename(line))

    # print the GTF files in the clusters
    if OK and help:
        if gtf_file_list != []:
            print('GTF files existing in the reference dataset: {0} ...'.format(str(gtf_file_list).strip('[]').replace('\'','')))
        else:
            OK = False

    # input and validate the GTF file
    if OK:
        while gtf_file == '':
            if help:
                gtf_file = input('... Enter the GTF file: ')
                if gtf_file not in gtf_file_list:
                    print('*** ERROR: {0} does not exist.'.format(gtf_file))
                    gtf_file = ''
            else:
                gtf_file = input('Enter the GTF file: ')
                if not gtf_file.isidentifier():
                    print('*** ERROR: The GTF file has some non-alphanumeric characters.')
                    gtf_file = ''

    # return the GTF dataset identification
    return gtf_file

#-------------------------------------------------------------------------------

def input_database_dataset_id(ssh_client, help):
    '''
    Input the database dataset identification in the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the database dataset identification
    database_dataset_id = ''

    # initialize the database dataset identification list
    database_dataset_id_list = []

    # get the database dataset identifications
    if help:
        command = 'ls {0}'.format(xlib.get_cluster_database_dir())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    database_dataset_id_list.append(line)

    # print the database identifications in the clusters
    if OK and help:
        if database_dataset_id_list != []:
            print('Database ids existing in the cluster: {0} ...'.format(str(database_dataset_id_list).strip('[]').replace('\'','')))
        else:
            OK = False

    # input and validate the database dataset identification
    if OK:
        while database_dataset_id == '':
            if help:
                database_dataset_id = input('... Enter the database id: ')
                if database_dataset_id not in database_dataset_id_list:
                    print('*** ERROR: {0} does not exist.'.format(database_dataset_id))
                    database_dataset_id = ''
            else:
                database_dataset_id = input('Enter the database id: ')
                if not database_dataset_id.isidentifier():
                    print('*** ERROR: The database id has some non-alphanumeric characters.')
                    database_dataset_id = ''

    # return the database dataset identification
    return database_dataset_id

#-------------------------------------------------------------------------------

def input_protein_database_name(ssh_client, database_dataset_id, help):
    '''
    Input the protein database name of a database dataset in the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the database file names
    protein_database_name = ''

    # initialize the database file list
    database_file_name_list = []

    # get the list of the database file names
    if help:
        command = 'ls {0}/*phr'.format(xlib.get_cluster_database_dataset_dir(database_dataset_id))
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    database_file_name_list.append(os.path.basename(line))
            if database_file_name_list == []:
                OK = False

    # get the list of the database dataset names
    if OK and help:
        protein_database_name_list = []
        pattern = re.compile('^.*[0-9][0-9]$')
        for database_file_name in database_file_name_list:
            file_name, file_extension = os.path.splitext(database_file_name)
            if pattern.match(file_name):
                database_name = file_name[:-3]
            else:
                database_name = file_name
            if database_name not in protein_database_name_list:
                protein_database_name_list.append(database_name)

    # print the database name in the dataset
    if OK and help:
        print('Protein databases existing in the dataset: {0} ...'.format(str(protein_database_name_list).strip('[]').replace('\'','')))

    # input and validate the protein database name
    if OK:
        while protein_database_name == '':
            if help:
                protein_database_name = input('... Enter the protein database: ')
                if protein_database_name not in protein_database_name_list:
                    print('*** ERROR: {0} does not exist.'.format(protein_database_name))
                    protein_database_name = ''
            else:
                protein_database_name = input('Enter the protein database: ')

    # return the protein database name
    return protein_database_name

#-------------------------------------------------------------------------------

def input_experiment_id(ssh_client, help):
    '''
    Input the experiment identification of the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the experiment identification
    experiment_id = ''

    # initialize the experiment identification list
    experiment_id_list = []

    # get the experiment identifications
    if help:
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    experiment_id_list.append(line)

    # print the experiment identifications in the clusters
    if OK and help:
        if experiment_id_list != []:
            print('Experiment ids existing in the cluster: {0} ...'.format(str(experiment_id_list).strip('[]').replace('\'','')))
        else:
            OK = False

    # input and validate the experiment identification
    if OK:
        while experiment_id == '':
            if help:
                experiment_id = input('... Enter the experiment id: ')
                if experiment_id not in experiment_id_list:
                    print('*** ERROR: {0} does not exist.'.format(experiment_id))
                    experiment_id = ''
            else:
                experiment_id = input('Enter the experiment id: ')
                if not experiment_id.isidentifier():
                    print('*** ERROR: The experiment id has some non-alphanumeric characters.')
                    experiment_id = ''

    # return the experiment identification
    return experiment_id

#-------------------------------------------------------------------------------

def input_read_dataset_id(ssh_client, experiment_id, help):
    '''
    Input the read dataset identification of an experimient in the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the read dataset identification
    read_dataset_id = ''

    # initialize the read dataset identification list
    read_dataset_id_list = []

    # get the read dataset identifications of the experiment
    if help:
        command = 'ls {0}/{1}'.format(xlib.get_cluster_read_dir(), experiment_id)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                read_dataset_id_list.append(line.rstrip('\n'))

    # print the read dataset identifications in the experiment
    if OK and help:
        if read_dataset_id_list != []:
            print('Read dataset ids existing in the experiment: {0} ...'.format(str(read_dataset_id_list).strip('[]').replace('\'','')))
        else:
            OK = False

    # input and validate the read dataset identification
    if OK:
        while read_dataset_id == '':
            if help:
                read_dataset_id = input('... Enter the read dataset id: ')
                if read_dataset_id not in read_dataset_id_list:
                    print('*** ERROR: {0} does not exist.'.format(read_dataset_id))
                    read_dataset_id = ''
            else:
                read_dataset_id = input('Enter the read dataset id: ')

    # return the read dataset identification
    return read_dataset_id

#-------------------------------------------------------------------------------

def input_read_type():
    '''
    Input the read type of the reads files.
    '''

    # initialize the read type
    read_type = ''

    # input and validate the read type
    while read_type == '':
        read_type = input('Read type (SE/PE)?: ').upper()
        if read_type not in ['SE', 'PE']:
            print('*** ERROR: {0} is not SE or PE.'.format(read_type))
            read_type = ''

    # return the read type
    return read_type

#-------------------------------------------------------------------------------

def input_result_dataset_id(status, ssh_client, experiment_id, help):
    '''
    Input the result dataset identification of an experimient in the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the result dataset identification
    result_dataset_id = ''

    # initialize the result dataset list
    result_dataset_id_list = []

    # get the result dataset identifications of the experiment
    if help:
        if status == 'uncompressed':
            command = 'cd {0}/{1}; for list in `ls`; do ls -ld $list | grep -v ^- > /dev/null && echo $list; done;'.format(xlib.get_cluster_result_dir(), experiment_id)
        elif status == 'compressed':
            command = 'cd {0}/{1}; for list in `ls`; do ls -ld $list | grep -v ^d > /dev/null && echo $list; done;'.format(xlib.get_cluster_result_dir(), experiment_id)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                result_dataset_id_list.append(line.rstrip('\n'))

    # print the result dataset identifications in the clusters
    if OK and help:
        if result_dataset_id_list != []:
            print('Result dataset ids existing in the experiment: {0} ...'.format(str(result_dataset_id_list).strip('[]').replace('\'','')))
        else:
            OK = False

    # input and validate the result dataset identification
    if OK:
        while result_dataset_id == '':
            if help:
                result_dataset_id = input('... Enter the result dataset id: ')
                if result_dataset_id not in result_dataset_id_list:
                    print('*** ERROR: {0} does not exist.'.format(result_dataset_id))
                    result_dataset_id = ''
            else:
                result_dataset_id = input('Enter the result dataset id: ')

    # return the result dataset identification
    return result_dataset_id

#-------------------------------------------------------------------------------

def input_rsem_eval_dataset_id(ssh_client, experiment_id, help):
    '''
    Input the RSEM-EVAL dataset identification of an experimient in the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the RSEM-EVAL dataset identification
    rsem_eval_dataset_id = ''

    # initialize the RSEM-EVAL dataset list
    rsem_eval_dataset_id_list = []

    # get the RSEM-EVAL dataset identifications of the experiment
    if help:
        command = 'cd {0}/{1}; for list in `ls`; do ls -ld $list | grep -v ^- > /dev/null && echo $list; done;'.format(xlib.get_cluster_result_dir(), experiment_id)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                if line.startswith(xlib.get_rsem_eval_code()):
                    rsem_eval_dataset_id_list.append(line.rstrip('\n'))

    # print the RSEM-EVAL dataset identifications in the clusters
    if OK and help:
        if rsem_eval_dataset_id_list != []:
            print('RSEM-EVAL dataset ids existing in the experiment: {0} ...'.format(str(rsem_eval_dataset_id_list).strip('[]').replace('\'','')))
        else:
            OK = False

    # input and validate the RSEM-EVAL dataset identification
    if OK:
        while rsem_eval_dataset_id == '':
            if help:
                rsem_eval_dataset_id = input('... Enter the RSEM-EVAL dataset id: ')
                if rsem_eval_dataset_id not in rsem_eval_dataset_id_list:
                    print('*** ERROR: {0} does not exist.'.format(rsem_eval_dataset_id))
                    rsem_eval_dataset_id = ''
            else:
                rsem_eval_dataset_id = input('Enter the RSEM-EVAL dataset id: ')

    # return the RSEM-EVAL dataset identification
    return rsem_eval_dataset_id

#-------------------------------------------------------------------------------

def input_assembly_dataset_id(ssh_client, experiment_id, help):
    '''
    Input the assembly dataset identification of an experimient in the cluster connected by a ssh client.
    '''

    # initialize the control variable
    OK = True

    # initialize the assembly dataset identification
    assembly_dataset_id = ''

    # initialize the result dataset list
    assembly_dataset_id_list = []

    # get the assembly dataset identifications of the experiment
    if help:
        command = 'ls {0}/{1}'.format(xlib.get_cluster_result_dir(), experiment_id)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            for line in stdout:
                if line.startswith(xlib.get_soapdenovotrans_code()) or line.startswith(xlib.get_transabyss_code()) or line.startswith(xlib.get_trinity_code()) or line.startswith(xlib.get_star_code()) or line.startswith(xlib.get_cd_hit_est_code()) or line.startswith(xlib.get_transcript_filter_code()):
                    assembly_dataset_id_list.append(line.rstrip('\n'))

    # print the result dataset identifications in the clusters
    if OK and help:
        if assembly_dataset_id_list != []:
            print('Assembly dataset ids existing in the experiment: {0} ...'.format(str(assembly_dataset_id_list).strip('[]').replace('\'','')))
        else:
            OK = False

    # input and validate the result dataset identification
    if OK:
        while assembly_dataset_id == '':
            if help:
                assembly_dataset_id = input('... Enter the assembly dataset id: ')
                if assembly_dataset_id not in assembly_dataset_id_list:
                    print('*** ERROR: {0} does not exist.'.format(assembly_dataset_id))
                    assembly_dataset_id = ''
            else:
                assembly_dataset_id = input('Enter the assembly dataset id: ')

    # return the result dataset identification
    return assembly_dataset_id

#-------------------------------------------------------------------------------

def input_assembly_type(help):
    '''
    Input the assembly type
    '''

    # get assembly type list
    assembly_type_list = ['CONTIGS', 'SCAFFOLDS']

    # print the assembly types
    if help:
        print('Available assembly types: {0} ...'.format(str(assembly_type_list).strip('[]').replace('\'','')))

    # initialize the assembly type
    assembly_type = ''

    # input and validate the mounting poing
    while assembly_type == '':
        if help:
            assembly_type = input('... Enter the assembly type: ')
            if assembly_type not in assembly_type_list:
                print('*** ERROR: {0} is not valid.'.format(assembly_type))
                assembly_type = ''
        else:
            assembly_type = input('Enter the assembly type: ')

   # return the assembly type
    return assembly_type

#-------------------------------------------------------------------------------

def input_files_pattern(default_file_pattern):
    '''
    Input a file pattern.
    '''

    # initialize the file pattern
    file_pattern = ''

    # input and validate the file pattern
    while file_pattern == '':
        if default_file_pattern != '':
            file_pattern = input('Enter a file pattern [{0}]: '.format(default_file_pattern))
            if file_pattern == '':
                file_pattern = default_file_pattern
        else:
            file_pattern = input('Enter a file pattern: ')
        try:
            re.compile(file_pattern)
        except:
            print('Invalid pattern. It must be a valid regular expression.')
            file_pattern = ''

   # return the file pattern
    return file_pattern

#-------------------------------------------------------------------------------

def input_file_pairing_specific_chars(file_order, default_specific_chars):
    '''
    Input specific characteres used to identify file 1 or file 2 when the read type is paired.
    '''

    # initialize the specific characters
    specific_chars = ''

    # input and validate the file specific characters
    while specific_chars == '':
        if default_specific_chars != '':
            specific_chars = input('Enter file #{0} specific chars [{1}]: '.format(file_order, default_specific_chars))
            if specific_chars == '':
                specific_chars = default_specific_chars
        else:
            specific_chars = input('Enter file #{0} specific chars: '.format(file_order))

   # return the specific characters
    return specific_chars

#-------------------------------------------------------------------------------

def input_batch_job_id(ssh_client, help):
    '''
    Input the batch job identification.
    '''

    # initialize the control variable
    OK = True

    # initialize the list of identification of the batch jobs
    batch_job_id_list = []

    # initialize the batch job identification
    batch_job_id = ''

    # get the batch job dictionary and the batch job identification list
    if help:
        (OK, error_list, batch_job_dict) = xcluster.get_batch_job_dict(ssh_client)

    # build the list of identifications of the batch jobs
    if OK and help:
        for job_id in batch_job_dict.keys():
            batch_job_id_list.append(job_id)
        if batch_job_id_list != []:
            batch_job_id_list.sort()
        else:
            OK = False

    # print the batch jobs
    if OK and help:
        # set data width
        job_id_width = 6
        job_name_width = 10
        state_width = 15
        start_date_width = 10
        start_time_width = 10
        # set line template
        line_template = '{0:' + str(job_id_width) + '} {1:' + str(job_name_width) + '} {2:' + str(state_width) + '} {3:' + str(start_date_width) + '} {4:' + str(start_time_width) + '}'
        # print header
        print('Batch jobs:')
        print()
        print(line_template.format('Job id', 'Job name', 'State', 'Start date', 'Start time'))
        print(line_template.format('=' * job_id_width, '=' * job_name_width, '=' * state_width, '=' * start_date_width, '=' * start_time_width))
        # print detail lines
        for job_id in batch_job_id_list:
            job_name = batch_job_dict[job_id]['job_name']
            state = batch_job_dict[job_id]['state']
            start_date = batch_job_dict[job_id]['start_date']
            start_time = batch_job_dict[job_id]['start_time']
            print(line_template.format(job_id, job_name, state, start_date, start_time))
        print()

    # input and validate the batch job identification
    if OK:
        while batch_job_id == '':
            if help:
                batch_job_id = input('... Enter the batch job id: ')
                if batch_job_id not in batch_job_id_list:
                    print('*** ERROR: {0} is not an id of a batch job.'.format(batch_job_id))
                    batch_job_id = ''
            else:
                template_name = input('Enter the batch job id: ')

    # return the batch job identification
    return batch_job_id

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains the general functions to data inputs in mode console.')
     sys.exit(0)

#-------------------------------------------------------------------------------
