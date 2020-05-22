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
This file contains the functions related to EC2 objetcs used in both console mode and gui mode.
'''
#-------------------------------------------------------------------------------

import configparser
import os
import stat
import sys

import boto3

import xconfiguration
import xlib

#-------------------------------------------------------------------------------

def verify_aws_credentials(aws_access_key_id, aws_secret_access_key):
    '''
    Verify an AWS access key identification and an AWS secret access key
    '''

    # initialize the control variable
    OK = True

    # verify the AWS access key identification and the AWS secret access key   
    try:
        client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')
        response = client.describe_availability_zones()
    except:
        OK = False

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def get_available_region_list():
    '''
    Get a list of the available region names.
    '''

    # initialize the control variable
    OK = True

    # initialize the region names list
    region_names_list = []

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification and the AWS secret access key
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')

    # create a low-level service client
    try: 
        client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')
    except:
        OK = False
    
    # get the region that are currently avaiable
    if OK:
        response = client.describe_regions()

    # add each region name to the region names list
    if OK:
        for region in response['Regions']:
            region_names_list.append(region['RegionName'])

    # sort the region names list
    if OK:
        if region_names_list != []:
            region_names_list.sort()

    # return available region names list
    return region_names_list

#-------------------------------------------------------------------------------

def is_region_available(region_name):
    '''
    Verify if a region name is available
    '''

    # initialize control variable
    available = False

    # get the available region name list
    available_region_names_list = get_available_region_list()

    # find region name in available region names
    available = region_name in available_region_names_list

    # return control variable
    return available

#-------------------------------------------------------------------------------

def get_available_zone_list(region_name):
    '''
    Get a list of the available zone names of a region
    '''

    # initialize the control variable
    OK = True

    # initialize the zone names list
    zone_names_list = []

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification and the AWS secret access key
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')

    # create a low-level service client
    try:
        client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    except:
        OK = False

    # get the region that are currently available in the region name
    if OK:
        response = client.describe_availability_zones()

    # add each zone name to the zone names list
    if OK:
        for zone in response['AvailabilityZones']:
            zone_names_list.append(zone['ZoneName'])

    # sort the zone names list
    if OK:
        if zone_names_list != []:
            zone_names_list.sort()

    # return available zone names list
    return zone_names_list

#-------------------------------------------------------------------------------

def is_zone_available(region_name, zone_name):
    '''
    Verify if a zone name is available in a region name.
    '''

    # initialize control variable
    available = False

    # get the available zone name list of the region name
    available_zone_names_list = get_available_zone_list(region_name)

    # find zone name in available zone names list of the region name
    available = zone_name in available_zone_names_list

    # return control variable
    return available

#-------------------------------------------------------------------------------

def get_keypair_dict(region_name):
    '''
    Get a dictionary of the key pairs that exist in a region.
    '''

    # initialize the control variable
    OK = True

    # initialize the key pairs dictionary
    keypairs_dict = {}

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification and the AWS secret access key
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')

    # create a low-level service client
    try:
        client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    except:
        OK = False
    
    # get the key pairs description
    if OK:
        response = client.describe_key_pairs()

    # get he key pairs list
    if OK:
        keypairs_list = response.get('KeyPairs', [])

    # add data key pairs to the dictionary
    if OK:
        for i in range(len(keypairs_list)):
            keypair_name = keypairs_list[i]['KeyName']
            keypair_fingerprint = keypairs_list[i]['KeyFingerprint']
            keypair_key = keypair_name
            keypairs_dict[keypair_key] = {'keypair_name': keypair_name, 'fingerprint': keypair_fingerprint}

    # return the key pairs dictionary
    return keypairs_dict

#-------------------------------------------------------------------------------

def create_keypairs(region_name):
    '''
    Create all the key pairs of a region.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the key pairs configuration data
    key_sections_dict = xconfiguration.get_key_sections_dict()

    # get the key pairs names list
    keypair_names_list = sorted(key_sections_dict.keys())

    # for each key, delete de key and create a new key and put owner has read permission
    for keypair_name in keypair_names_list:
        keypair_file = key_sections_dict[keypair_name]['key_location']
        (OK, error_list) = delete_keypair(keypair_file, keypair_name, region_name)
        if not OK:
            break
        (OK, error_list) = create_keypair(keypair_file, keypair_name, region_name)
        if not OK:
            break

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def create_keypair(keypair_file, keypair_name, region_name):
    '''
    Create a key pairs in a region.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification and the AWS secret access key
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')

    # create a low-level service client
    try:
        client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    except:
        OK = False

    # create the key pair
    if OK:
        response = client.create_key_pair(KeyName=keypair_name)

    # get the unencrypted PEM encoded RSA private key
    if OK:
        keypair_rsa = response['KeyMaterial']

    # get the key pairs directory
    if OK:
        keypair_dir = os.path.dirname(keypair_file)
        if not os.path.exists(keypair_dir):
            try:
                os.makedirs(keypair_dir)
            except:
                error_list.append('** ERROR: The directory {0} can not be created.'.format(keypair_dir))
                OK = False

    # save the unencrypted PEM encoded RSA private key in a file
    if OK:
        try:
            if os.path.isfile(keypair_file):
                os.chmod(keypair_file, stat.S_IWUSR)
            with open(keypair_file, mode='w', encoding='utf8') as file_id:
                file_id.write('{0}'.format(keypair_rsa))
            os.chmod(keypair_file, stat.S_IRUSR)
        except:
            error_list.append('*** ERROR: The file {0} can not be created'.format(keypair_file))
            OK = False

    # get the SHA-1 digest of the DER encoded private key
    if OK:
        keypair_fingerprint = response['KeyFingerprint']

    # save the SHA-1 digest of the DER encoded private key in a file
    if OK:
        keypair_fingerprint_file = xlib.change_extension(keypair_file, 'fingerprint')
        try:
            if os.path.isfile(keypair_fingerprint_file):
                os.chmod(keypair_fingerprint_file, stat.S_IWUSR)
            with open(keypair_fingerprint_file, mode='w', encoding='utf8') as file_id:
                file_id.write('{0}'.format(keypair_fingerprint))
            os.chmod(keypair_fingerprint_file, stat.S_IRUSR)
        except:
            error_list.append('*** ERROR: The file {0} can not be created'.format(keypair_fingerprint_file))
            OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def delete_keypair(keypair_file, keypair_name, region_name):
    '''
    Delete a key pairs in a region.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification and the AWS secret access key
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')

    # create a low-level service client
    try:
        client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    except:
        OK = False

    # delete the key pair
    if OK:
        response = client.delete_key_pair(KeyName=keypair_name)

    # delete the file that contains the unencrypted PEM encoded RSA private key
    if OK:
        if os.path.isfile(keypair_file):
            try:
                os.chmod(keypair_file, stat.S_IWUSR)
                os.remove(keypair_file)
            except:
                error_list.append('*** WARNING: The file {0} can not be removed.'.format(keypair_file))

    # delete the file that contains the SHA-1 digest of the DER encoded private key
    if OK:
        keypair_fingerprint_file = xlib.change_extension(keypair_file, 'fingerprint')
        if os.path.isfile(keypair_fingerprint_file):
            try:
                os.chmod(keypair_fingerprint_file, stat.S_IWUSR)
                os.remove(keypair_fingerprint_file)
            except:
                error_list.append('*** WARNING: The file {0} can not be removed.'.format(keypair_fingerprint_file))

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_running_cluster_list(volume_creator_included):
    '''
    Get the running cluster list.
    '''

    # initialize the control variable
    OK = True

    # initialize of the running cluster list
    running_cluster_list = []

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the clusters that they are running
    if OK:
        for inst in resource.instances.all():
            # verify that the current instance is running
            if inst.state['Code'] != 48:
                # verify that the instance is the master node
                if inst.tags is not None:
                    for tag in inst.tags:
                        if tag['Key'] == 'Name' and tag['Value'] == 'master':
                            # if the instance has a security group created by StarCluster
                            if inst.security_groups is not None:
                                for security_group in inst.security_groups:
                                    if security_group['GroupName'].startswith('@sc-{0}-'.format(xconfiguration.environment)):
                                        # add the cluster_name to the running cluster list
                                        cluster_name = security_group['GroupName'][4:]
                                        if volume_creator_included or (not volume_creator_included and cluster_name != xlib.get_volume_creator_name()):
                                            running_cluster_list.append(cluster_name)

    # sort the running cluster list
    if OK:
        if running_cluster_list != []:
            running_cluster_list.sort()

    # return the running cluster list
    return running_cluster_list

#-------------------------------------------------------------------------------

def get_node_dict():
    '''
    Get a dictionary of nodes with their node id, node_name, security group name,
    zone name, State code and state name.
    '''

    # initialize the control variable
    OK = True

    # initialize the node dictionary
    node_dict = {}

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # get data of instances running
    if OK:
        for inst in resource.instances.all():
            security_group_name = inst.security_groups[0]['GroupName'] if inst.security_groups != [] else ' '
            node_id = inst.instance_id
            zone_name = inst.placement['AvailabilityZone']
            for tag in inst.tags:
                if tag['Key'] == 'Name':
                    node_name = tag['Value']
            state_code = inst.state['Code']
            state_name = inst.state['Name']
            state = '{0} ({1})'.format(state_code, state_name)
            node_key = '{0}-{1}-{2}-{3}'.format(security_group_name, zone_name, node_name, node_id)
            node_dict[node_key] = {'security_group_name': security_group_name, 'zone_name': zone_name, 'node_name': node_name, 'node_id': node_id, 'state_code': state_code, 'state_name': state_name, 'state': state}

    # return the node dictionary
    return node_dict

#-------------------------------------------------------------------------------

def get_cluster_node_list(cluster_name):
    '''
    Get the node name list of a cluster.
    '''

    # initialize the control variable
    OK = True

    # initialize of the cluster node list
    cluster_node_list = []

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the node between the running instances
    if OK:
        for inst in resource.instances.all():
            # if the instance is not terminated:
            if  inst.state['Code'] != 48:
                # verify than the current instance belongs to the cluster
                security_group_found = False
                if inst.security_groups is not None:
                    for security_group in inst.security_groups:
                        if security_group['GroupName'] == '@sc-{0}'.format(cluster_name):
                            security_group_found = True
                # if verification is OK, add node name to cluster node list
                if security_group_found:
                    if inst.tags is not None:
                        for tag in inst.tags:
                            if tag['Key'] == 'Name':
                                cluster_node_list.append(tag['Value'])
                                break

    # sort the cluster node list
    if OK:
        if cluster_node_list != []:
            cluster_node_list.sort()

    # return the cluster node list
    return cluster_node_list

#-------------------------------------------------------------------------------

def get_node_id(cluster_name, node_name):
    '''
    Get the node identification. All instances with the node name corresponding
    to the cluster_name are analized until one of them is not terminated.
    '''

    # initialize the control variable
    OK = True

    # initialize of the node identification
    node_id = ''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the node between the running instances
    if OK:
        for inst in resource.instances.all():
            # if the instance is not terminated:
            if  inst.state['Code'] != 48:
                # verify than the current instance belongs to the cluster
                security_group_found = False
                if inst.security_groups is not None:
                    for security_group in inst.security_groups:
                        if security_group['GroupName'] == '@sc-{0}'.format(cluster_name):
                            security_group_found = True
                # verify that the current instance has the node name
                node_name_found = False
                if inst.tags is not None:
                    for tag in inst.tags:
                        if tag['Key'] == 'Name' and tag['Value'] == node_name:
                            node_name_found = True
                # if verifications are OK, get the node identification
                if security_group_found and node_name_found:
                    node_id = inst.instance_id
                    break

    # return the node identification
    return node_id

#-------------------------------------------------------------------------------

def get_node_state(cluster_name, node_name):
    '''
    Get the state of a node. All instances with the node name corresponding
    to the cluster name are analized until one of them is not terminated.
    '''

    # initialize the control variable
    OK = True

    # initialize of the node state
    node_state_code = -1
    node_state_name = 'non-existent'

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the node between the running instances
    if OK:
        for inst in resource.instances.all():
            # if the instance is not terminated:
            if  inst.state['Code'] != 48:
                # verify than the current instance belongs to the cluster
                security_group_found = False
                if inst.security_groups is not None:
                    for security_group in inst.security_groups:
                        if security_group['GroupName'] == '@sc-{0}'.format(cluster_name):
                            security_group_found = True
                # verify that the current instance has the node name
                node_name_found = False
                if inst.tags is not None:
                    for tag in inst.tags:
                        if tag['Key'] == 'Name' and tag['Value'] == node_name:
                            node_name_found = True
                # if verifications are OK, get the node state
                if security_group_found and node_name_found:
                    node_state_code = inst.state['Code']
                    node_state_name = inst.state['Name']
                    break

    # return the node state
    return (node_state_code, node_state_name)

#-------------------------------------------------------------------------------

def get_node_zone_name(cluster_name, node_name):
    '''
    Get the zone name of a node. All instances with the node name corresponding
    to the cluster name are analized until one of them is not terminated.
    '''

    # initialize the control variable
    OK = True

    # initialize of the node zone name
    node_zone_name = ''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the node between the running instances
    if OK:
        for inst in resource.instances.all():
            # if the instance is not terminated:
            if  inst.state['Code'] != 48:
                # verify than the current instance belongs to the cluster
                security_group_found = False
                if inst.security_groups is not None:
                    for security_group in inst.security_groups:
                        if security_group['GroupName'] == ('@sc-'+cluster_name):
                            security_group_found = True
                # verify that the current instance has the node name
                node_name_found = False
                if inst.tags is not None:
                    for tag in inst.tags:
                        if tag['Key'] == 'Name' and tag['Value'] == node_name:
                            node_name_found = True
                # if verifications are OK, get node zone name
                if  security_group_found and node_name_found:
                    node_zone_name = inst.placement['AvailabilityZone']
                    break

    # return the node zone name
    return node_zone_name

#-------------------------------------------------------------------------------

def get_node_public_dns_name(cluster_name, node_name):
    '''
    Get the public DNS name of a node. All instances with the node name corresponding
    to the cluster_name are analized until one of them is not terminated.
    '''

    # initialize the control variable
    OK = True

    # initialize of the public DNS name
    public_dns_name = ''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the node between the running instances
    if OK:
        for inst in resource.instances.all():
            # if the instance is not terminated:
            if  inst.state['Code'] != 48:
                # verify than the current instance belongs to the cluster
                security_group_found = False
                if inst.security_groups is not None:
                    for security_group in inst.security_groups:
                        if security_group['GroupName'] == ('@sc-'+cluster_name):
                            security_group_found = True
                # verify that the current instance has the node name
                node_name_found = False
                if inst.tags is not None:
                    for tag in inst.tags:
                        if tag['Key'] == 'Name' and tag['Value'] == node_name:
                            node_name_found = True
                # if verifications are OK and the instance is not terminate, get the public DNS name
                if security_group_found and node_name_found:
                    public_dns_name = inst.public_dns_name
                    break

    # return the public DNS name
    return public_dns_name

#-------------------------------------------------------------------------------

def get_max_node_number():
    '''
    Get the maximum node number.
    '''

    return 20

#-------------------------------------------------------------------------------

def get_volume_type_dict():
    '''
    Get the volume type dictionary.
    '''

    # build the volume type dictionary
    volume_type_dict = {}
    volume_type_dict['standard']= {'text': 'standard HDD', 'minimum_size':1, 'maximum_size':1024}
    volume_type_dict['sc1']= {'text': 'cold HDD', 'minimum_size':500, 'maximum_size':16384}
    volume_type_dict['st1']= {'text': 'throughput optimized HDD', 'minimum_size':500, 'maximum_size':16384}
    volume_type_dict['gp2']= {'text': 'general purpose SSD', 'minimum_size':1, 'maximum_size':16384}
    volume_type_dict['io1']= {'text': 'provisioned IOPS SSD', 'minimum_size':1, 'maximum_size':16384}

    # return the volume type dictionary
    return volume_type_dict

#-------------------------------------------------------------------------------

def get_volume_type_id_list():
    '''
    Get the volume type identification list.
    '''

    # get the dictionary of the volume types
    volume_type_dict = get_volume_type_dict()

    # get the volume type list
    volume_type_list = volume_type_dict.keys()

    # return the volume type list
    return sorted(volume_type_list)

#-------------------------------------------------------------------------------

def get_volume_type_text_list():
    '''
    Get the volume type text list.
    '''

    # get the dictionary of the volume types
    volume_type_dict = get_volume_type_dict()

    # initialize the volume type text list
    volume_type_text_list = []

    # build search the volume type text list
    for volume_type_id in volume_type_dict.keys():
        volume_type_text_list.append(volume_type_dict[volume_type_id]['text'])

    # return the volume type text list
    return sorted(volume_type_text_list)

#-------------------------------------------------------------------------------

def get_volume_type_id(volume_type_text):
    '''
    Get the volume type identification from the volume type text.
    '''

    # initialize the control variable
    volume_type_id_found = None

    # get the dictionary of the volume types
    volume_type_dict = get_volume_type_dict()

    # search the volume type identification
    for volume_type_id in volume_type_dict.keys():
        if volume_type_dict[volume_type_id]['text'] == volume_type_text:
            volume_type_id_found = volume_type_id
            break

    # return the volume type identification
    return volume_type_id_found

#-------------------------------------------------------------------------------

def create_volume(volume_name, volume_type, volume_size, iops=0):
    '''
    Create a volume in the current zone.
    '''

    # initialize the control variable
    OK = True

    # initialize the volume identificacion
    volume_id = None

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region and zone names
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')
    current_zone_name = config.get('global', 'current_zone', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a low-level service client
    if OK:
        client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # create the volume
    if OK:
        try:
            if iops > 0:
                response = client.create_volume(DryRun=False, Size=volume_size, AvailabilityZone=current_zone_name, VolumeType=volume_type, Iops=iops, Encrypted=False)
            else:
                response = client.create_volume(DryRun=False, Size=volume_size, AvailabilityZone=current_zone_name, VolumeType=volume_type, Encrypted=False)
        except:
            OK = False

    # get the volume identificaction
    if OK:
        volume_id = response['VolumeId']

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # create a specific resource for the created volume
    if OK:
        volume = resource.Volume(response['VolumeId']) 

    # set the volume name
    if OK:
        response = volume.create_tags(DryRun=False, Tags=[{'Key': 'Name', 'Value': volume_name}])

    # return the control variable and the volume identificatgion
    return (OK, volume_id)

#-------------------------------------------------------------------------------

def delete_volume(volume_name):
    '''
    Delete a volume in the current zone.
    '''

    # initialize the control variable
    OK = True

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region and zone names
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')
    current_zone_name = config.get('global', 'current_zone', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # get the volume identification
    volume_id = get_volume_id(volume_name, current_zone_name)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # create a specific resource for the volume to be deleted
    if OK:
        volume = resource.Volume(volume_id) 

    # delete the volume
    if OK:
        try:
            response = volume.delete(DryRun=False)
        except:
            OK = False

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def get_volume_dict():
    '''
    Get a dictionary of volumes with their node_name, volume id, volume name,
    volume size, volume state, attachments and attchments number.
    '''

    # initialize the control variable
    OK = True

    # initialize the node dictionary
    volumes_dict = {}

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # get data of volumes created
    if OK:
        for vol in resource.volumes.all():
            volume_id = vol.volume_id
            zone_name = vol.availability_zone
            if vol.tags is None:
                volume_name = ' '
            else:
                for tag in vol.tags:
                    if tag['Key'] == 'Name':
                        volume_name = tag['Value']
            size = vol.size
            state = vol.state
            attachments = vol.attachments
            attachments_number = len(attachments)
            volume_key = '{0}-{1}-{2}'.format(zone_name, volume_name, volume_id)
            volumes_dict[volume_key] = {'zone_name': zone_name, 'volume_name': volume_name, 'volume_id': volume_id, 'size': size, 'state': state, 'attachments': attachments, 'attachments_number': attachments_number}

    # return the volumes dictionary
    return volumes_dict

#-------------------------------------------------------------------------------

def get_created_volume_dict(zone_name):
    '''
    Get the dictionary of volumes created in a zone.
    '''

    # initialize the control variable
    OK = True

    # initialize the volumes dictionary
    created_volume_dict = {}

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the volume identification
    if OK:
        for vol in resource.volumes.all():
            if vol.availability_zone==zone_name and vol.tags is not None:
                for tag in vol.tags:
                    if tag['Key'] == 'Name':
                        created_volume_dict[tag['Value']] = {'Id': vol.volume_id}
                        break

    # return the volumes dictionary
    return created_volume_dict

#-------------------------------------------------------------------------------

def get_created_volume_name_list(zone_name):
    '''
    Get a created volume name list in a zone.
    '''

    # initialize the control variable
    OK = True

    # initialize the available volume names list
    available_volume_names_list = []

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the available volumes
    if OK:
        for vol in resource.volumes.all():
            if vol.tags is not None:
                for tag in vol.tags:
                    if tag['Key'] == 'Name':
                        if tag['Value'] != '' and vol.availability_zone==zone_name:
                            available_volume_names_list.append(tag['Value'])

    # sort the available volume names list
    if OK:
        available_volume_names_list.sort()

    # return the available volume names list
    return available_volume_names_list

#-------------------------------------------------------------------------------

def get_noattached_volume_name_list(zone_name):
    '''
    Get a available volume name list in a zone, not attached to any node.
    '''

    # initialize the control variable
    OK = True

    # initialize the available volume names list
    available_volume_names_list = []

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the available volumes
    if OK:
        for vol in resource.volumes.all():
            if vol.tags is not None:
                for tag in vol.tags:
                    if tag['Key'] == 'Name':
                        if tag['Value'] != '' and vol.availability_zone==zone_name and vol.attachments == []:
                            available_volume_names_list.append(tag['Value'])

    # sort the available volume names list
    if OK:
        available_volume_names_list.sort()

    # return the available volume names list
    return available_volume_names_list

#-------------------------------------------------------------------------------

def is_volume_created(volume_name, zone_name):
    '''
    Check if a volume is created in a zone.
    '''

    # initialize the control variable
    OK = True

    # initialize the found variable
    found = False

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the volume
    if OK:
        try:
            for vol in resource.volumes.all():
                if vol.tags is not None:
                    for tag in vol.tags:
                        if tag['Key'] == 'Name' and tag['Value'] == volume_name and vol.availability_zone==zone_name:
                            found = True
                            raise xlib.BreakAllLoops
        except xlib.BreakAllLoops:
            pass

    # return the control variable
    return found

#-------------------------------------------------------------------------------

def get_volume_id(volume_name, zone_name):
    '''
    Get the volume identitation in a zone.
    '''

    # initialize the control variable
    OK = True

    # initialize volume identification
    volume_id = ''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the volume identification
    if OK:
        try:
            for vol in resource.volumes.all():
              if vol.tags is not None:
                  for tag in vol.tags:
                        if tag['Key'] == 'Name':
                            if tag['Value'] == volume_name and vol.availability_zone==zone_name:
                                volume_id = vol.volume_id
                                raise xlib.BreakAllLoops
        except xlib.BreakAllLoops:
            pass

    # return the volume identification
    return volume_id

#-------------------------------------------------------------------------------

def get_volume_state(volume_name, zone_name):
    '''
    Get the volume state in a zone.
    '''

    # initialize the control variable
    OK = True

    # initialize volume state
    volume_state = ''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the volume state
    if OK:
        try:
            for volume in resource.volumes.all():
              if volume.tags is not None:
                  for tag in volume.tags:
                        if tag['Key'] == 'Name':
                            if tag['Value'] == volume_name and volume.availability_zone==zone_name:
                                volume_state = volume.state
                                raise xlib.BreakAllLoops
        except xlib.BreakAllLoops:
            pass

    # return the volume state
    return volume_state

#-------------------------------------------------------------------------------

def get_volume_attachments(volume_name, zone_name):
    '''
    Get the volume attachments in a zone.
    '''

    # initialize the control variable
    OK = True

    # initialize volume identification
    volume_attachments = []

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # find the volume
    if OK:
        try:
            for vol in resource.volumes.all():
              if vol.tags is not None:
                  for tag in vol.tags:
                        if tag['Key'] == 'Name':
                            if tag['Value'] == volume_name and vol.availability_zone==zone_name:
                                volume_attachments = vol.attachments
                                raise xlib.BreakAllLoops
        except xlib.BreakAllLoops:
            pass

    # return the volume attachments
    return volume_attachments

#-------------------------------------------------------------------------------

def get_volume_device_file(cluster_name, node_name, volume_name):
    '''
    Get the device file where a volume is attached a cluster node.
    '''

    # initialize the control variable
    OK = True

    # initialize the device file
    device_file = ''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # get node identification
    if OK:
        node_id = get_node_id(cluster_name, node_name)

    # get the zone name of the node
    if OK:
        node_zone_name = get_node_zone_name(cluster_name, node_name)

    # find the device file
    if OK:
        try:
            for vol in resource.volumes.all():
              if vol.tags is not None:
                  for tag in vol.tags:
                        if tag['Key'] == 'Name':
                            if tag['Value'] == volume_name and vol.availability_zone==node_zone_name:
                                volume_attachments = vol.attachments
                                if volume_attachments is not None:
                                    for volume_attachment in volume_attachments:
                                        if volume_attachment['InstanceId'] == node_id:
                                            device_file = volume_attachment['Device']
                                            raise xlib.BreakAllLoops
        except xlib.BreakAllLoops:
            pass

    # return the device file
    return device_file

#-------------------------------------------------------------------------------

def attach_volume(node_id, volume_id, aws_device_file):
    '''
    Attach a volumen in the device file of a node. 
    '''

    # initialize the control variable
    OK = True

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # get the instance corresponding to the node
    if OK:
        instance = resource.Instance(node_id)

    # attch the volume
    if OK:
        #try:
        response = instance.attach_volume(DryRun=False, VolumeId=volume_id, Device=aws_device_file)
        #except:
        #    OK = False

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def detach_volume(node_id, volume_id, aws_device_file):
    '''
    Detach a volumen in a node. 
    '''

    # initialize the control variable
    OK = True

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification, the AWS secret access key and the current region name
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')
    current_region_name = config.get('global', 'current_region', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=current_region_name)

    # get the instance corresponding to the node
    if OK:
        instance = resource.Instance(node_id)

    # detach the volume
    if OK:
        try:
            response = instance.detach_volume(DryRun=False, VolumeId=volume_id, Device=aws_device_file, Force=False)
        except:
            OK = False

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def get_starcluster_ami_id(region_name):
    '''
    Get the StarCluster AMI identification correponding a region.
    '''

    # initialize the control variable
    OK = True

    # initialize the starcluster AMI identification
    starcluster_ami_id = get_unknown_ami_id()

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the AWS access key identification and the AWS secret access key
    aws_access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    aws_secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')

    # verify the AWS access key identification and the AWS secret access key   
    OK = verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    # create a resource service client
    if OK:
        resource = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    # get data of AMI created
    if OK:
        starcluster_ami_name = get_starcluster_ami_name()
        for ima in resource.images.all():
            if ima.name is not None: 
                if ima.name == starcluster_ami_name:
                    starcluster_ami_id = ima.image_id
                    break

    # return the starcluster AMI identification
    return starcluster_ami_id

#-------------------------------------------------------------------------------

def get_starcluster_ami_name():
    '''
    Get the name of a unknown AMI.
    '''

    return 'starcluster-base-ubuntu-13.04-x86_64-hvm'

#-------------------------------------------------------------------------------

def get_unknown_ami_id():
    '''
    Get the name of a unknown AMI.
    '''

    return 'ami-unknown'

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains the functions related to EC2 objetcs used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
