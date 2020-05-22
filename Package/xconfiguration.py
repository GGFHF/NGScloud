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
This file contains the functions related to the NGScloud configuration used in
both console mode and gui mode.
'''

#-------------------------------------------------------------------------------

import configparser
import os
import sys

import xec2
import xlib

#-------------------------------------------------------------------------------

# Global variables

environment =  ''    # the AWS environment where the processes are run

#-------------------------------------------------------------------------------

def get_environments_file():
    '''
    Get the defined environments file.
    '''

    # assign the defined environments file
    environments_file = '{0}/{1}'.format(xlib.get_config_dir(), 'environments.txt')

    # return the defined environments file
    return environments_file

#-------------------------------------------------------------------------------

def get_environments_list():
    '''
    Get the defined environments list
    '''
    
    # initialize the control variable
    OK = True

    # initialize the environments list
    environments_list = []

    # read the environments file
    try:
        environments_file = get_environments_file()
        with open(environments_file, mode='r', encoding='utf-8') as file_id:
            records = file_id.readlines()
            for record in records:
                environments_list.append(record.strip())
    except:
        pass

    # sort the environments list
    if environments_list != []:
        environments_list.sort()

    # return the environments list
    return environments_list

#-------------------------------------------------------------------------------

def add_environment(environment):
    '''
    Add a new environment in the environments file.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # add environment in the environments file
    try:
        environments_file = get_environments_file()
        if not os.path.exists(os.path.dirname(environments_file)):
            os.makedirs(os.path.dirname(environments_file))
        with open(environments_file, mode='a', encoding='utf-8') as file_id:
            file_id.write('{0}\n'.format(environment.strip()))
    except:
        error_list.append('*** ERROR: The file {0} can not be written.'.format(environments_file))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def create_ngscloud_config_file(user_id, access_key_id, secret_access_key, email):
    '''
    Create the NGScloud config file corresponding to the environment.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # set the default current region and zone names
    region_name = get_default_region_name()
    zone_name = get_default_zone_name()

    # get NGScloud Key
    ngscloud_key = get_ngscloud_key()

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # create the NGScloud config file corresponding to the current environment
    if OK:
        try:
            if not os.path.exists(os.path.dirname(ngscloud_config_file)):
                os.makedirs(os.path.dirname(ngscloud_config_file))
            with open(ngscloud_config_file, mode='w', encoding='utf8') as file_id:
                file_id.write('{0}\n'.format('[global]'))
                file_id.write('{0}\n'.format('default_template = {0}-t2.micro'.format(environment)))
                file_id.write('{0}\n'.format('environment = {0}'.format(environment)))
                file_id.write('{0}\n'.format('current_region = {0}'.format(region_name)))
                file_id.write('{0}\n'.format('current_zone = {0}'.format(zone_name)))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[aws info]'))
                file_id.write('{0}\n'.format('aws_user_id = {0}'.format(user_id)))
                file_id.write('{0}\n'.format('aws_access_key_id = {0}'.format(access_key_id)))
                file_id.write('{0}\n'.format('aws_secret_access_key = {0}'.format(secret_access_key)))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[contact info]'))
                file_id.write('{0}\n'.format('email = {0}'.format(email)))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[key {0}]'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('key_location = {0}/{1}-{2}-{3}.rsa'.format(xlib.get_keypairs_dir(), ngscloud_key, user_id, region_name)))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}]'.format(xlib.get_volume_creator_name())))
                file_id.write('{0}\n'.format('description = t2.micro used only to create volumes'))
                file_id.write('{0}\n'.format('vcpu = 1'))
                file_id.write('{0}\n'.format('memory = 1.000'))
                file_id.write('{0}\n'.format('use = general purpose'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = t2.micro'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = t2.micro'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-c3.large]'.format(environment)))
                file_id.write('{0}\n'.format('description = c3.large - 2 vCPUs - 3.75 GiB - compute optimized'))
                file_id.write('{0}\n'.format('vcpu = 2'))
                file_id.write('{0}\n'.format('memory = 3.750'))
                file_id.write('{0}\n'.format('use = compute optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = c3.large'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = c3.large'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-c3.xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = c3.xlarge - 4 vCPUs - 7.5 GiB - compute optimized'))
                file_id.write('{0}\n'.format('vcpu = 4'))
                file_id.write('{0}\n'.format('memory = 7.500'))
                file_id.write('{0}\n'.format('use = compute optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = c3.xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = c3.xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-c3.2xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = c3.2xlarge - 8 vCPUs - 15 GiB - compute optimized'))
                file_id.write('{0}\n'.format('vcpu = 8'))
                file_id.write('{0}\n'.format('memory = 15.000'))
                file_id.write('{0}\n'.format('use = compute optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = c3.2xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = c3.2xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-c3.4xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = c3.4xlarge - 16 vCPUs - 30 GiB - compute optimized'))
                file_id.write('{0}\n'.format('vcpu = 16'))
                file_id.write('{0}\n'.format('memory = 30.000'))
                file_id.write('{0}\n'.format('use = compute optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = c3.4xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = c3.4xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-c3.8xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = c3.8xlarge - 32 vCPUs - 60 GiB - compute optimized'))
                file_id.write('{0}\n'.format('vcpu = 32'))
                file_id.write('{0}\n'.format('memory = 60.000'))
                file_id.write('{0}\n'.format('use = compute optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = c3.8xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = c3.8xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-m3.medium]'.format(environment)))
                file_id.write('{0}\n'.format('description = m3.medium - 1 vCPU - 3.75 GiB - general purpose'))
                file_id.write('{0}\n'.format('vcpu = 1'))
                file_id.write('{0}\n'.format('memory = 3.750'))
                file_id.write('{0}\n'.format('use = general purpose'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = m3.medium'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = m3.medium'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-m3.large]'.format(environment)))
                file_id.write('{0}\n'.format('description = m3.large - 2 vCPUs - 7.5 GiB - general purpose'))
                file_id.write('{0}\n'.format('vcpu = 2'))
                file_id.write('{0}\n'.format('memory = 7.500'))
                file_id.write('{0}\n'.format('use = general purpose'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = m3.large'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = m3.large'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-m3.xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = m3.xlarge - 4 vCPUs - 15 GiB - general purpose'))
                file_id.write('{0}\n'.format('vcpu = 4'))
                file_id.write('{0}\n'.format('memory = 15.000'))
                file_id.write('{0}\n'.format('use = general purpose'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = m3.xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = m3.xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-m3.2xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = m3.2xlarge - 8 vCPUs - 30 GiB - general purpose'))
                file_id.write('{0}\n'.format('vcpu = 8'))
                file_id.write('{0}\n'.format('memory = 30.000'))
                file_id.write('{0}\n'.format('use = general purpose'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = m3.2xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = m3.2xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-r3.large]'.format(environment)))
                file_id.write('{0}\n'.format('description = r3.large - 2 vCPUs - 15 GiB - memory optimized'))
                file_id.write('{0}\n'.format('vcpu = 2'))
                file_id.write('{0}\n'.format('memory = 15.000'))
                file_id.write('{0}\n'.format('use = memory optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = r3.large'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = r3.large'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-r3.xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = r3.xlarge - 4 vCPUs - 30.5 GiB - memory optimized'))
                file_id.write('{0}\n'.format('vcpu = 4'))
                file_id.write('{0}\n'.format('memory = 30.500'))
                file_id.write('{0}\n'.format('use = memory optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = r3.xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = r3.xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-r3.2xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = r3.2xlarge - 8 vCPUs - 61 GiB - memory optimized'))
                file_id.write('{0}\n'.format('vcpu = 8'))
                file_id.write('{0}\n'.format('memory = 61.000'))
                file_id.write('{0}\n'.format('use = memory optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = r3.2xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = r3.2xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-r3.4xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = r3.4xlarge - 16 vCPUs - 122 GiB - memory optimized'))
                file_id.write('{0}\n'.format('vcpu = 16'))
                file_id.write('{0}\n'.format('memory = 122.000'))
                file_id.write('{0}\n'.format('use = memory optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = r3.4xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = r3.4xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-r3.8xlarge]'.format(environment)))
                file_id.write('{0}\n'.format('description = r3.8xlarge - 32 vCPUs - 244 GiB - memory optimized'))
                file_id.write('{0}\n'.format('vcpu = 32'))
                file_id.write('{0}\n'.format('memory = 244.000'))
                file_id.write('{0}\n'.format('use = memory optimized'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = r3.8xlarge'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = r3.8xlarge'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-t2.micro]'.format(environment)))
                file_id.write('{0}\n'.format('description = t2.micro - 1 vCPU - 1 GiB - general purpose'))
                file_id.write('{0}\n'.format('vcpu = 1'))
                file_id.write('{0}\n'.format('memory = 1.000'))
                file_id.write('{0}\n'.format('use = general purpose'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = t2.micro'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = t2.micro'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-t2.small]'.format(environment)))
                file_id.write('{0}\n'.format('description = t2.small - 1 vCPU - 2 GiB - general purpose'))
                file_id.write('{0}\n'.format('vcpu = 1'))
                file_id.write('{0}\n'.format('memory = 2.000'))
                file_id.write('{0}\n'.format('use = general purpose'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = t2.small'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = t2.small'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[cluster {0}-t2.medium]'.format(environment)))
                file_id.write('{0}\n'.format('description = t2.medium - 2 vCPUs - 4 GiB - general purpose'))
                file_id.write('{0}\n'.format('vcpu = 2'))
                file_id.write('{0}\n'.format('memory = 4.000'))
                file_id.write('{0}\n'.format('use = general purpose'))
                file_id.write('{0}\n'.format('generation = current'))
                file_id.write('{0}\n'.format('keyname = {0}'.format(ngscloud_key)))
                file_id.write('{0}\n'.format('cluster_size = 1'))
                file_id.write('{0}\n'.format('cluster_user = sgeadmin'))
                file_id.write('{0}\n'.format('cluster_shell = bash'))
                file_id.write('{0}\n'.format('master_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('master_instance_type = t2.medium'))
                file_id.write('{0}\n'.format('node_image_id = ami-6b211202'))
                file_id.write('{0}\n'.format('node_instance_type = t2.medium'))
                file_id.write('{0}\n'.format('volumes = '))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[bioinfoapp {0}]'.format(xlib.get_miniconda3_name())))
                file_id.write('{0}\n'.format('version = last'))
                file_id.write('{0}\n'.format('url = https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh'))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[bioinfoapp {0}]'.format(xlib.get_ngshelper_name())))
                file_id.write('{0}\n'.format('version = last'))
                file_id.write('{0}\n'.format('url = https://github.com/GGFHF/NGShelper/archive/master.zip'))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[bioinfoapp {0}]'.format(xlib.get_rnaquast_name())))
                file_id.write('{0}\n'.format('version = 1.5.1'))
                file_id.write('{0}\n'.format('url = http://cab.spbu.ru/files/rnaquast/release1.5.1/rnaQUAST-1.5.1.tar.gz'))
                file_id.write('{0}\n'.format(''))
                file_id.write('{0}\n'.format('[bioinfoapp {0}]'.format(xlib.get_transrate_name())))
                file_id.write('{0}\n'.format('version = 1.0.3'))
                file_id.write('{0}\n'.format('url = https://bintray.com/artifact/download/blahah/generic/transrate-1.0.3-linux-x86_64.tar.gz'))
        except:
            error_list.append('*** ERROR: The file {0} can not be created'.format(ngscloud_config_file))
            OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def update_connection_data(user_id, access_key_id, secret_access_key):
    '''
    Update the user id, access key id and secret access key in the NGScloud
    config file corresponding to the environment.
    '''

    # initialize the control variable
    OK = True

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # get the options dictionary corresponding to the NGScloud config file
    ngscloud_options_dict = xlib.get_option_dict(ngscloud_config_file)

    # update the current region and zone in the options dictionary corresponding to the NGScloud config file
    ngscloud_options_dict['aws info']['aws_user_id'] = user_id
    ngscloud_options_dict['aws info']['aws_access_key_id'] = access_key_id
    ngscloud_options_dict['aws info']['aws_secret_access_key'] = secret_access_key

    # save the options dictionary in the NGScloud config file corresponding to the environment
    (OK, error_list) = save_ngscloud_config_file(ngscloud_options_dict)

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def update_contact_data(email):
    '''
    Update the contact e-mail in the NGScloud config file corresponding to the
    environment.
    '''

    # initialize the control variable
    OK = True

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # get the options dictionary corresponding to the NGScloud config file
    ngscloud_options_dict = xlib.get_option_dict(ngscloud_config_file)

    # update the contact e-mail in the options dictionary corresponding to the NGScloud config file
    ngscloud_options_dict['contact info']['email'] = email

    # save the options dictionary in the NGScloud config file corresponding to the environment
    (OK, error_list) = save_ngscloud_config_file(ngscloud_options_dict)

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def update_region_zone_data(region_name, zone_name):
    '''
    Update the current region and zone names in the NGScloud config file
    corresponding to the environment.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get NGScloud Key
    ngscloud_key = get_ngscloud_key()

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # get the options dictionary corresponding to the NGScloud config file
    ngscloud_options_dict = xlib.get_option_dict(ngscloud_config_file)

    # get the old region and  user identification
    old_region_name = ngscloud_options_dict['global']['current_region']
    user_id = ngscloud_options_dict['aws info']['aws_user_id']

    # get the AMI identification of the new region
    if region_name != old_region_name:
        starcluster_ami_id = xec2.get_starcluster_ami_id(region_name)
        if starcluster_ami_id == xec2.get_unknown_ami_id():
            error_list.append('The AMI {0} is not found in the region {1}. The region and zone are not modified.'.format(xec2.get_starcluster_ami_name(), region_name))
            OK = False

    # update the current region and zone in the options dictionary corresponding to the NGScloud config file
    if OK:
        ngscloud_options_dict['global']['current_region'] = region_name
        ngscloud_options_dict['global']['current_zone'] = zone_name
        ngscloud_options_dict['key NGScloudKey']['key_location'] = '{0}/{1}-{2}-{3}.rsa'.format(xlib.get_keypairs_dir(), ngscloud_key, user_id, region_name)

    # update the master and node image identification and inicialize the asigned volumes in each cluster template
    if OK:
        if region_name != old_region_name:
            template_name_list = get_template_name_list(volume_creator_included=True)
            for template_name in template_name_list:
                ngscloud_options_dict['cluster {}'.format(template_name)]['master_image_id'] = starcluster_ami_id
                ngscloud_options_dict['cluster {}'.format(template_name)]['node_image_id'] = starcluster_ami_id
                ngscloud_options_dict['cluster {}'.format(template_name)]['volumes'] = ''

    # save the options dictionary in the NGScloud config file
    if OK:
        (OK, error_list) = save_ngscloud_config_file(ngscloud_options_dict)

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def link_volume_to_template(template_name, mount_path, volume_name, log, function=None):
    '''
    Include a volume in a cluster template
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('Do not close this window, please wait!\n')

    # get current zone name
    zone_name = get_current_zone_name()

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # get the options dictionary corresponding to the NGScloud config file
    ngscloud_options_dict = xlib.get_option_dict(ngscloud_config_file)

    # get the defined cluster templates list
    if template_name == 'all':
        template_names_list = get_template_name_list(volume_creator_included=False)
    else:
        template_names_list = [template_name]

    
    # get the dictionary of volumes
    volumes_dict = get_volumes_dict()
    
    # define volume section if it is not defined
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('The data of the volume {0} are going to be added ...\n'.format(volume_name))
    if volume_name not in volumes_dict.keys():
        ngscloud_options_dict['volume {0}'.format(volume_name)] = {'volume_id': xec2.get_volume_id(volume_name, zone_name), 'mount_path': mount_path}
        log.write('The data are has been added.\n')
    else:
        if ngscloud_options_dict['volume {0}'.format(volume_name)]['mount_path'] != mount_path:
            log.write('*** ERROR: The mount path of volume {0} was previously assigned to {1}.\n'.format(volume_name, ngscloud_options_dict['volume {0}'.format(volume_name)]['mount_path']))
            OK = False
        else:
            log.write('*** WARNING: The volume data has been previously added.\n')
    
    # add volume to list of the volumes linked to every template in the tamplate list
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        for template_name in template_names_list:
            log.write('The volume {0} is been linked to the cluster template {1} ...\n'.format(volume_name, template_name))
            linked_volumes = ngscloud_options_dict['cluster {0}'.format(template_name)]['volumes']
            linked_volumes_list = xlib.split_literal_to_string_list(linked_volumes)
            if volume_name in linked_volumes_list:
                log.write('*** WARNING: The volume was previously linked.\n')
            else:
                if ngscloud_options_dict['cluster {0}'.format(template_name)]['volumes'] == '':
                    ngscloud_options_dict['cluster {0}'.format(template_name)]['volumes'] = volume_name
                else:
                    linked_volumes_list.append(volume_name)
                    ngscloud_options_dict['cluster {0}'.format(template_name)]['volumes'] = ', '.join(linked_volumes_list)
                log.write('The volume has been linked.\n')

    # save the options dictionary in the NGScloud config file
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('The file {0} is going to be saved ...\n'.format(ngscloud_config_file))
        (OK, error_list) = save_ngscloud_config_file(ngscloud_options_dict)
        if OK:
            log.write('The config file has been saved.\n')
        else:
            for error in error_list:
                log.write(error)

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return (OK, error_list)

#-------------------------------------------------------------------------------

def delink_volume_from_template(template_name, volume_name, log, function=None):
    '''
    Delink a volume from a cluster template
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('Do not close this window, please wait!\n')

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # get the options dictionary corresponding to the NGScloud config file
    ngscloud_options_dict = xlib.get_option_dict(ngscloud_config_file)

    # get the defined cluster templates list
    if template_name == 'all':
        template_names_list = get_template_name_list(volume_creator_included=False)
    else:
        template_names_list = [template_name]
        
    # verify if the volume name exists in the dictionary of linked volumes
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('The config data of the volume {0} is been verified ...\n'.format(volume_name))
    if volume_name in get_volume_names_list():
        log.write('The config data of the volume has been verified.\n')
    else:
        log.write('*** WARNING: There are not config data of this volume.\n')
        OK = False

    # remove the volume from the linked volumes list of every template in the tamplate list
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        for template_name in template_names_list:
            log.write('The volume {0} is being delinked from {1} ...\n'.format(volume_name, template_name))
            linked_volumes = ngscloud_options_dict['cluster {0}'.format(template_name)]['volumes']
            linked_volumes_list = xlib.split_literal_to_string_list(linked_volumes)
            if volume_name in linked_volumes_list:
                linked_volumes_list.remove(volume_name)
                ngscloud_options_dict['cluster {0}'.format(template_name)]['volumes'] = ', '.join(linked_volumes_list)
                log.write('The volume has been delinked.\n')
            else:
                log.write('*** WARNING: The volume was not linked.\n')

    # remove the volume information if it is not linked to any template
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('The links of volume {0} are been reviewed ...\n'.format(volume_name))
        defined_template_names_list = get_template_name_list(volume_creator_included=False)
        linked_template_names_list = []
        for template_name in defined_template_names_list:
            linked_volumes = ngscloud_options_dict['cluster {0}'.format(template_name)]['volumes']
            linked_volumes_list = xlib.split_literal_to_string_list(linked_volumes)
            if volume_name in linked_volumes_list:
                linked_template_names_list.append(template_name)
        if linked_template_names_list == []:
            log.write('The volume {0} has not links. Its configuration data are been removed ...\n'.format(volume_name))
            del ngscloud_options_dict['volume {0}'.format(volume_name)]
            log.write('The figuration data are been removed.\n')
        else:
            log.write('The links has been reviewed. Its has {1} links.\n'.format(volume_name, len(linked_template_names_list)))

    # save the options dictionary in the NGScloud config file
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('The file {0} is going to be saved ...\n'.format(ngscloud_config_file))
        (OK, error_list) = save_ngscloud_config_file(ngscloud_options_dict)
        if OK:
            log.write('The config file has been saved.\n')
        else:
            for error in error_list:
                log.write(error)

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return (OK, error_list)

#-------------------------------------------------------------------------------

def review_volume_links(zone_name, log, function=None):
    '''
    Review linked volumes of cluster templates in the NGScloud config file
    corresponding to the environment in order to remove linked volumes which are
    not created currently.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('Do not close this window, please wait!\n')

    # get the NGScloud confign file
    ngscloud_config_file = get_ngscloud_config_file()

    # get the options dictionary corresponding to the NGScloud config file
    ngscloud_options_dict = xlib.get_option_dict(ngscloud_config_file)
    
    # get the dictionary of cluster templates
    templates_dict = get_template_dict()
    
    # get the dictionary of linked volumes from NGScloud config file
    linked_volumes_dict = get_volumes_dict()
    
    # get the dictionary of created volumes from AWS
    created_volumes_dict = xec2.get_created_volume_dict(zone_name)

    # for each linked volume, review if it exists
    log.write('{0}\n'.format(xlib.get_separator()))
    for volume_name in linked_volumes_dict.keys():
        if volume_name not in created_volumes_dict.keys():
            log.write('The configuration data of volume {0} is being erased ...\n'.format(volume_name))
            for template_name in templates_dict.keys():
                linked_volumes = ngscloud_options_dict['cluster {0}'.format(template_name)]['volumes']
                linked_volumes_list = xlib.split_literal_to_string_list(linked_volumes)
                if volume_name in linked_volumes_list:
                    linked_volumes_list.remove(volume_name)
                    ngscloud_options_dict['cluster {0}'.format(template_name)]['volumes'] = ', '.join(linked_volumes_list)
            del ngscloud_options_dict['volume {0}'.format(volume_name)]
            log.write('The configuration data has been erased.\n')

    # save the options dictionary in the NGScloud config file
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('The file {0} is being saved ...\n'.format(ngscloud_config_file))
    (OK, error_list) = save_ngscloud_config_file(ngscloud_options_dict)
    if OK:
        log.write('The config file has been saved.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return (OK, error_list)

#-------------------------------------------------------------------------------

def save_ngscloud_config_file(ngscloud_options_dict):
    '''
    Save the NGScloud config options in the config file corresponding
    to the environment.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the sections list
    sections_list = []
    for section in ngscloud_options_dict.keys():
        sections_list.append(section)
    sections_list.sort()

    # build the section "global"
    section = 'global'
    config[section] = {}
    for k, v in ngscloud_options_dict[section].items():
        config[section][k] = v

    # build the section "aws info"
    section = 'aws info'
    config[section] = {}
    for k, v in ngscloud_options_dict[section].items():
        config[section][k] = v

    # build the section "contact info"
    section = 'contact info'
    config[section] = {}
    for k, v in ngscloud_options_dict[section].items():
        config[section][k] = v

    # build the sections "key *"
    for section in sections_list:
        if section.startswith('key'):
            config[section] = {}
            for k, v in ngscloud_options_dict[section].items():
                config[section][k] = v

    # build the sections "cluster *"
    for section in sections_list:
        if section.startswith('cluster'):
            config[section] = {}
            for k, v in ngscloud_options_dict[section].items():
                config[section][k] = v

    # build the sections "volume *"
    for section in sections_list:
        if section.startswith('volume'):
            config[section] = {}
            for k, v in ngscloud_options_dict[section].items():
                config[section][k] = v

    # build the sections "bioinfoapp *"
    for section in sections_list:
        if section.startswith('bioinfoapp'):
            config[section] = {}
            for k, v in ngscloud_options_dict[section].items():
                config[section][k] = v

    # write the NGScloud config file
    try:
        with open(ngscloud_config_file, mode='w', encoding='utf8') as file_id:
            config.write(file_id)
    except:
        error_list.append('*** ERROR: The file {0} can not be written'.format(ngscloud_config_file))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------
    
def get_default_region_name():
    '''
    Get the region name by default.
    '''

    return 'us-east-1'

#-------------------------------------------------------------------------------
    
def get_default_zone_name():
    '''
    Get the region name by default.
    '''

    return 'us-east-1c'

#-------------------------------------------------------------------------------

def get_basic_aws_data():
    '''
    Get the connection data to AWS: access the user identification, the key
    identification and the secret access key from NGScloud config file.
    '''

    # create class to parse the config file
    config = configparser.ConfigParser()

    # read the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()
    config.read(ngscloud_config_file)

    # get the connection data from NGScloud config file
    user_id= config.get('aws info', 'aws_user_id', fallback='')
    access_key_id = config.get('aws info', 'aws_access_key_id', fallback='')
    secret_access_key = config.get('aws info', 'aws_secret_access_key', fallback='')

    # return the connection data
    return (user_id, access_key_id, secret_access_key)

#-------------------------------------------------------------------------------

def get_contact_data():
    '''
    Get the access the contact e-mail from NGScloud config file.
    '''

    # create class to parse the config file
    config = configparser.ConfigParser()

    # read the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()
    config.read(ngscloud_config_file)

    # get the contact e-mail data from the NGScloud config file
    email = config.get('contact info', 'email', fallback='')

    # return the contact e-mail
    return email

#-------------------------------------------------------------------------------

def get_key_sections_dict():
    '''
    Get the key sections data dictionary from the NGScloud config file
    corresponding to the environment.
    '''

    # initialize the key sections data dictionary
    key_sections_dict = {}
    
    # create class to parse the config files
    config = configparser.ConfigParser()

    # read the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()
    config.read(ngscloud_config_file)

    # get the sections list
    sections_list = []
    for section in config.sections():
        sections_list.append(section)
    sections_list.sort()

    # build the key sections data dictionary
    for section in sections_list:
        section_type = 'key'
        if section.startswith(section_type):
            key_section_name = section[len(section_type) + 1:]
            key_sections_dict[key_section_name] = {}
            for k, v in config[section].items():
                key_sections_dict[key_section_name][k] = v

    # return the key sections data dictionary
    return key_sections_dict

#-------------------------------------------------------------------------------

def get_template_dict():
    '''
    Get the cluster templates data dictionary from the NGScloud config file
    corresponding to the environment.
    '''

    # initialize the key sections data dictionary
    template_dict = {}
    
    # create class to parse the config files
    config = configparser.ConfigParser()

    # read the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()
    config.read(ngscloud_config_file)

    # get the sections list
    sections_list = []
    for section in config.sections():
        sections_list.append(section)
    sections_list.sort()

    # build the cluster template data dictionary
    for section in sections_list:
        section_type = 'cluster'
        if section.startswith(section_type):
            key_section_name = section[len(section_type) + 1:]
            template_dict[key_section_name] = {}
            template_dict[key_section_name]['template_name'] = key_section_name
            for k, v in config[section].items():
                template_dict[key_section_name][k] = v

    # return the cluster templates  data dictionary
    return template_dict

#-------------------------------------------------------------------------------

def get_template_name_list(volume_creator_included):
    '''
    Get the template name list from the NGScloud config file corresponding
    to the environment.
    '''

    # initialize the template name list
    template_name_list = []
    
    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # build the key sections data dictionary
    for section in config.sections():
        section_type = 'cluster'
        if section.startswith(section_type):
            template_name = section[len(section_type) + 1:]
            if volume_creator_included or (not volume_creator_included and template_name != xlib.get_volume_creator_name()):
                template_name_list.append(template_name)

    # sort the template name list
    if template_name_list != []:
        template_name_list.sort()

    # return the template name list
    return template_name_list

#-------------------------------------------------------------------------------

def get_volumes_dict():
    '''
    Get the volumes data dictionary from the NGScloud config file
    corresponding to the environment.
    '''

    # initialize the key sections data dictionary
    volumes_dict = {}
    
    # create class to parse the config files
    config = configparser.ConfigParser()

    # read the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()
    config.read(ngscloud_config_file)

    # get the sections list
    sections_list = []
    for section in config.sections():
        sections_list.append(section)
    sections_list.sort()

    # build the volumes data dictionary
    for section in sections_list:
        section_type = 'volume'
        if section.startswith(section_type):
            key_section_name = section[len(section_type) + 1:]
            volumes_dict[key_section_name] = {}
            for k, v in config[section].items():
                volumes_dict[key_section_name][k] = v

    # return the volumes data dictionary
    return volumes_dict

#-------------------------------------------------------------------------------

def get_volume_names_list():
    '''
    Get the list of the volume names from the NGScloud config file
    corresponding to the environment.
    '''

    # get the volume names list
    volume_names_list = get_volumes_dict().keys()

    # return the volume names list
    return sorted(volume_names_list)

#-------------------------------------------------------------------------------

def get_linked_volumes_list(template_name):
    '''
    Get the list of volumes linked to a cluster template from the NGScloud
    config file corresponding to the environment.
    '''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the linked volumes of the template name
    linked_volumes = config.get('cluster {0}'.format(template_name), 'volumes', fallback='')

    # get the linked volumes list
    linked_volumes_list = xlib.split_literal_to_string_list(linked_volumes)

    # return the linked volumes list
    return linked_volumes_list

#-------------------------------------------------------------------------------

def get_current_region_name():
    '''
    Get the current region name from the NGScloud config file corresponding
    to the environment.
    '''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the current region name
    current_region_name = config.get('global', 'current_region', fallback='')

    # return  the current region name
    return current_region_name

#-------------------------------------------------------------------------------

def get_current_zone_name():
    '''
    Get the current zone name from the NGScloud config file corresponding to
    the environment.
    '''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the current zone name
    current_zone_name = config.get('global', 'current_zone', fallback='')

    # return  the current zone name
    return current_zone_name

#-------------------------------------------------------------------------------

def get_keypair_file():
    '''
    Get the path of the key pair file to the current region from the NGScloud
    config file corresponding to the environment.
    '''

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # get the options dictionary
    ngscloud_options_dict = xlib.get_option_dict(ngscloud_config_file)

    # get the key pair file
    keypair_file = ngscloud_options_dict['key NGScloudKey']['key_location']

    # return the key pair file
    return keypair_file

#-------------------------------------------------------------------------------

def get_bioinfo_app_data(bioinfo_app_name):
    '''
    Get the data of a bioinfo application from the NGScloud
    config file corresponding to the environment.
    '''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # read the NGScloud config file
    config.read(ngscloud_config_file)

    # get the data
    bioinfo_app_version = config.get('bioinfoapp {0}'.format(bioinfo_app_name), 'version', fallback='')
    bioinfo_app_url = config.get('bioinfoapp {0}'.format(bioinfo_app_name), 'url', fallback='')

    # return the data
    return (bioinfo_app_version, bioinfo_app_url)

#-------------------------------------------------------------------------------

def is_template_defined(template_name):
    '''
    Check if a template name is defined in the NGScloud config file corresponding
    to the environment.
    '''

    # initialize of the control variable
    found = False

    # find the template definition
    if template_name in get_template_name_list(volume_creator_included=True):
        found = True

    # return the control variable
    return found

#-------------------------------------------------------------------------------

def is_ngscloud_config_file_created():
    '''
    Check if the NGScloud config file corresponding to the environment is created.
    '''

    # initialize the found variable
    found = True

    # check if NGScloud config file is created
    if not os.path.isfile(get_ngscloud_config_file()):
        found = False

    # return the found variable
    return found

#-------------------------------------------------------------------------------

def set_environment_variables():
    '''
    Set the environment variables corresponding to the NGScloud config file
    corresponding to the environment: the AWS access key identification, AWS
    secret access key and the current region name
    '''

    # create class to parse the config files
    config = configparser.ConfigParser()

    # get the NGScloud config file
    ngscloud_config_file = get_ngscloud_config_file()

    # set environment variable TRANCRIPTOMECLOUD_CONFIG_FILE
    os.environ['NGSCLOUD_CONFIG_FILE'] = ngscloud_config_file

#-------------------------------------------------------------------------------

def get_ngscloud_config_file():
    '''
    Get the path of the NGScloud config file corresponding to the environment.
    '''

    # assign the NGScloud config file
    ngscloud_config_file = '{0}/{1}-{2}'.format(xlib.get_config_dir(), environment, 'ngscloud-config.txt')

    # return the NGScloud config file
    return ngscloud_config_file

#-------------------------------------------------------------------------------

def get_ngscloud_key():
    '''
    Get the code of the NGScloud key.
    '''

    return 'NGScloudKey'

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains the functions related to the NGScloud configuration used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
