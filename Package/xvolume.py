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
This file contains the functions related to the volume operation used in both
console mode and gui mode.
'''
#-------------------------------------------------------------------------------

import os
import sys
import time

import xcluster
import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def create_volume(volume_name, volume_type, volume_size, terminate_indicator, log, function=None):
    '''
    Create a volume in the current zone.
    '''

    # initialize the control variable
    OK = True

    # get the volume creator name
    volume_creator_name = xlib.get_volume_creator_name()

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take a few minutes. Do not close this window, please wait!\n')

    # verify the volume creator is running
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Verifing if volume creator is running ...\n')
        (master_state_code, master_state_name) = xec2.get_node_state(volume_creator_name, 'master')
        if master_state_code == 16:
            log.write('The volume creator is running.\n')
        else:
            log.write('*** WARNING: The volume creator is not running. It will be created.\n')
            (OK, master_state_code, master_state_name) = xcluster.create_cluster(volume_creator_name, volume_creator_name, log, function=None, is_menu_call=False)

    # get the master node identification
    if OK:
        node_id = xec2.get_node_id(volume_creator_name, 'master')
        if node_id == '':
            log.write('*** ERROR: The master identification of the volume creator not has been got.\n')
            OK = False

    # create the SSH client connection
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Connecting SSH client ...\n')
    (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(volume_creator_name, 'master')
    if OK:
        log.write('The SSH client is connected.\n')
    else:
        for error in error_list:
            log.write('{0}\n'.format(error))

    # warn that the requirements are being verified 
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Verifying process requirements ...\n')

    # get current region and zone names
    region_name = xconfiguration.get_current_region_name()
    zone_name = xconfiguration.get_current_zone_name()

    # verify that the zone is available
    if OK:
        if not xec2.is_zone_available(region_name, zone_name):
            log.write('*** ERROR: The zone {0} is not available in the region {1}.\n'.format(zone_name, region_name))
            OK = False

    # verify that the volume is not created
    if OK:
        if xec2.is_volume_created(volume_name, zone_name):
            log.write('*** WARNING: The volume {0} is already created.\n'.format(volume_name))
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # create the volume
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Creating volume {0} ...\n'.format(volume_name))
        (OK, volume_id) = xec2.create_volume(volume_name, volume_type, volume_size)
        if OK:
            log.write('The volume is created with the identification {0}.\n'.format(volume_id))
        else:
            log.write('*** ERROR: The volume is not created.\n')

    # wait for the volume status to be available
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Waiting for the volume state to be available ...\n')
        i = 0
        available_state_timeout = 120
        while True:
            i += 1
            volume_status = xec2.get_volume_state(volume_name, zone_name)
            time.sleep(1)
            if volume_status == 'available':
                log.write('The volume is now available.\n')
                break
            elif i > available_state_timeout:
                log.write('*** The volume is not available after {0} s.\n'.format(available_state_timeout))
                Ok = False
                break

    # set the aws device and get de machine device
    if OK:
        aws_device = '/dev/sdp'
        machine_device = xlib.get_machine_device_file(aws_device)

    # attach the volume to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Attaching volume {0} to node master of volume creator ...\n'.format(volume_name))
        OK = xec2.attach_volume(node_id, volume_id, aws_device)
        if OK:
            log.write('The volume is attached.\n')
        else:
            log.write('*** ERROR: The volume is not attached.\n')

    # wait for the volume attachment to be available
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Waiting for the volume attachment to be available ...\n')
        i = 0
        attachment_timeout = 120
        while True:
            i += 1
            volume_attachments = xec2.get_volume_attachments(volume_name, zone_name)
            if volume_attachments != []:
                log.write('The volume attachment is now available.\n')
                break
            elif i > attachment_timeout:
                log.write('*** ERROR: The volume attachment is not available after {0} s.\n'.format(attachment_timeout))
                Ok = False
                break
            time.sleep(1)

    # wait for the device availability
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Waiting for the availabity of the device {0} ...\n'.format(machine_device))
        i = 0
        format_timeout = 120
        try:
            while True:
                i += 1
                command = 'hdparm -z {0}'.format(machine_device)
                (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
                command = 'lsblk --list --noheadings --output NAME'
                (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
                for line in stdout:
                    if line == os.path.basename(machine_device):
                        log.write('The device is available.\n')
                        raise xlib.BreakAllLoops
                if i > format_timeout:
                    log.write('*** ERROR: The device is not available after {0} s.\n'.format(format_timeout))
                    OK = False
                    break
                time.sleep(1)
        except xlib.BreakAllLoops:
            pass

    # format the volume
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Formating volume {0} to ext4 file system type ...\n'.format(volume_name))
        command = 'mkfs -t ext4 {0} 2>&1; RC=$?; echo "RC=$RC"'.format(machine_device)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if stdout[len(stdout) - 1] == 'RC=0':
            log.write('The volume is formatted.\n')
            OK = True
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))
            OK = False

    # detach the volume to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Detaching volume {0} from node master of volume creator ...\n'.format(volume_name))
        OK = xec2.detach_volume(node_id, volume_id, aws_device)
        if OK:
            log.write('The volume is detached.\n')
        else:
            log.write('*** ERROR: The volume is not detached.\n')

    # terminate volume creator
    if OK:
        if terminate_indicator:
            OK = xcluster.terminate_cluster(volume_creator_name, True, log, function=None, is_menu_call=False)
        else:
            log.write('{0}\n'.format(xlib.get_separator()))
            log.write('You do not indicate to terminate the volume creator.\n')
            log.write('Remember to terminate it when you finish to create the volumes!!!\n')

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

def remove_volume(volume_name, log, function=None):
    '''
    Delete a volume in the current zone.
    '''

    # initialize the control variable
    OK = True

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take a few minutes. Do not close this window, please wait!\n')

    # warn that the requirements are being verified 
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Verifying process requirements ...\n')

    # get current region and zone names
    region_name = xconfiguration.get_current_region_name()
    zone_name = xconfiguration.get_current_zone_name()

    # verify that the zone is available
    if OK:
        if not xec2.is_zone_available(region_name, zone_name):
            log.write('*** ERROR: The zone {0} is not available in the region {1}.\n'.format(zone_name, region_name))
            OK = False

    # verify that the volume is available
    if OK:
        volume_status = xec2.get_volume_state(volume_name, zone_name)
        if volume_status != 'available':
            log.write('*** ERROR: The volume {0} is not available in the zone {1}.\n'.format(volume_name, zone_name))
            OK = False

    # verify that the volume is not linked to any cluster templates
    if OK:
        if volume_name in xconfiguration.get_volume_names_list():
            log.write('*** ERROR: The volume is linked to some cluster templates.\n')
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # delete the volume
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Removing volume {0} ...\n'.format(volume_name))
        OK = xec2.delete_volume(volume_name)
        if OK:
            log.write('The volume is been deleted. It may remain in the deleting state for several minutes.\n')
        else:
            log.write('*** ERROR: The volume is not deleted.\n')

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

def mount_volume(cluster_name, node_name, volume_name, aws_device_file, mounting_path, log, function=None, is_menu_call=True):
    '''
    Mount a volume in a node.
    '''

    # initialize the control variable
    OK = True

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut) and is_menu_call:
        log.write('This process might take a few minutes. Do not close this window, please wait!\n')

    # create the SSH client connection
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Connecting SSH client ...\n')
    (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
    if OK:
        log.write('The SSH client is connected.\n')
    else:
        for error in error_list:
            log.write('{0}\n'.format(error))

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

    # get the zone name of the node
    if OK:
        zone_name = xec2.get_node_zone_name(cluster_name, node_name)

    # get the node identification
    if OK:
        node_id = xec2.get_node_id(cluster_name, node_name)
        if node_id == '':
            log.write('*** ERROR: The {0} identification of the cluster {1} not has been got.\n'.format(node_name, cluster_name))
            OK = False

    # verify the volume is created
    if OK and not xec2.is_volume_created(volume_name, zone_name):
        log.write('*** ERROR: The volume {0} is not created.\n'.format(volume_name))
        OK = False

    # get the volume identification
    if OK:
        volume_id = xec2.get_volume_id(volume_name, zone_name)
        if volume_id == '':
            log.write('*** ERROR: The volume identification of {0} not has been got.\n'.format(volume_name))
            OK = False

    # get de machine device file
    if OK:
        machine_device_file = xlib.get_machine_device_file(aws_device_file)

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # create the directory in the instance
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Creating directory {0} in node {1} of cluster {2} ...\n'.format(mounting_path, node_name, cluster_name))
        command = 'mkdir --parents {0}'.format(mounting_path)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The directory is created.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # attach the volume to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Attaching volume {0} to node {1} of cluster {2} ...\n'.format(volume_name, node_name, cluster_name))
        OK = xec2.attach_volume(node_id, volume_id, aws_device_file)
        if OK:
            log.write('The volume is attached.\n')
        else:
            log.write('*** ERROR: The volume is not attached.\n')

    # mount the volume to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Mounting volume {0} in directory {1} ...\n'.format(volume_name, mounting_path))
        time.sleep(30)
        command = 'mount {0} {1}'.format(machine_device_file, mounting_path)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The volume is mounted.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # close the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut) and is_menu_call:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def unmount_volume(cluster_name, node_name, volume_name, log, function=None, is_menu_call=True):
    '''
    Unmount a volume in a node.
    '''

    # initialize the control variable
    OK = True

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut) and is_menu_call:
        log.write('This process might take a few minutes. Do not close this window, please wait!\n')

    # create the SSH client connection
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Connecting SSH client ...\n')
    (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
    if OK:
        log.write('The SSH client is connected.\n')
    else:
        for error in error_list:
            log.write('{0}\n'.format(error))

    # warn that the requirements are being verified 
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Verifying process requirements ...\n')

    # verify the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name,master_state_code, master_state_name))
            OK = False

    # get the zone name of the node
    if OK:
        zone_name = xec2.get_node_zone_name(cluster_name, node_name)

    # get the node identification
    if OK:
        node_id = xec2.get_node_id(cluster_name, node_name)
        if node_id == '':
            log.write('*** ERROR: The {0} identification of the cluster {1} not has been got.\n'.format(node_name, cluster_name))
            OK = False

    # verify the volume is created
    if OK:
        if not xec2.is_volume_created(volume_name, zone_name):
            log.write('*** ERROR: The volume {0} is not created.\n'.format(volume_name))
            OK = False

    # get AWS file device
    if OK:
        aws_device_file = xec2.get_volume_device_file(cluster_name, node_name, volume_name)
        if aws_device_file == '':
            log.write('*** ERROR: the file device of the volume is not found.\n')
            OK = False

    # get the volume identification
    if OK:
        volume_id = xec2.get_volume_id(volume_name, zone_name)
        if volume_id == '':
            log.write('*** ERROR: The identificaction of volume {0} not has been got.\n'.format(volume_name))
            OK = False

    # get de file device file
    if OK:
        machine_device_file = xlib.get_machine_device_file(aws_device_file)

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # unmount the volume to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Unmounting volume {0} from the device file {1} ...\n'.format(volume_name, machine_device_file))
        command = 'umount {0}'.format(machine_device_file)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The volume is unmounted.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # detach the volume to the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Detaching volume {0} from node {1} of cluster {2} ...\n'.format(volume_name, node_name, cluster_name))
        OK = xec2.detach_volume(node_id, volume_id, aws_device_file)
        if OK:
            log.write('The volume is detached.\n')
        else:
            log.write('*** ERROR: The volume is not detached.\n')

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

if __name__ == '__main__':
     print('This file contains the functions related to the volume operation used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
