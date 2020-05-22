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
This file contains the functions related to the node operation used in both console
mode and gui mode.
'''
#-------------------------------------------------------------------------------

import os
import subprocess
import sys

import xconfiguration
import xec2
import xlib
import xssh

#-------------------------------------------------------------------------------

def add_node(cluster_name, node_name, log, function=None):
    '''
    Add a node in a cluster.
    '''

    # initialize the control variable
    OK = True

    # warn that the requirements are being verified 
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Verifying process requirements ...\n')

    # verify the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # verify the node is not running
    if OK:
        pass

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # add node
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Adding node {0} in cluster {1} using StarCluster ...\n'.format(node_name, cluster_name))
        log.write('\n')
        command = '{0} addnode {1} --alias={2}'.format(xlib.get_starcluster(), cluster_name, node_name)
        rc = xlib.run_command(command, log)
        log.write('\n')
        if rc == 0:
            log.write('The node is added.\n')
        else:
            log.write('*** ERROR: Return code {0} in command -> {1}\n'.format(rc, command))
            OK = False

    # install infraestructure software in the node
    if OK:
        OK = install_node_infrastructure_software(cluster_name, node_name, log)

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

def remove_node(cluster_name, node_name, log, function=None):
    '''
    Remove a node in a cluster.
    '''

    # initialize the control variable
    OK = True

    # warn that the requirements are being verified 
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Verifying process requirements ...\n')

    # verify the master is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # verify the node is running
    if OK:
        pass

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # remove node
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Removing node {0} in cluster {1} using StarCluster ...\n'.format(node_name, cluster_name))
        log.write('\n')
        command = '{0} removenode --confirm {1} --alias={2}'.format(xlib.get_starcluster(), cluster_name, node_name)
        rc = xlib.run_command(command, log)
        log.write('\n')
        if rc == 0:
            log.write('The node is removed.\n')
        else:
            log.write('*** ERROR: Return code {0} in command -> {1}\n'.format(rc, command))
            OK = False

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

def install_node_infrastructure_software(cluster_name, node_name, log):
    '''
    Install infraestructure software in a node.
    '''

    # initialize the control variable
    OK = True

    # get the infrastructure software installation script path in local compute
    local_script_path = get_infrastructure_software_installation_script()

    # set the infrastructure software installation script path in node
    node_script_path = './{0}'.format(os.path.basename(local_script_path))

    # set the infrastructure software installation log path in node
    node_log_path = node_script_path[:node_script_path.find('.sh')] + '.log'

    # build the infrastructure software installation script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Building the infrastructure software installation script {0} ...\n'.format(local_script_path
                                                                                              ))
        (OK, error_list) = build_infrastructure_software_installation_script(cluster_name)
        if OK:
            log.write('The file is built.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH client to node {0} ...\n'.format(node_name))
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, node_name)
        if OK:
            log.write('The SSH client is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SSH transport connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SSH transport to node {0} ...\n'.format(node_name))
        (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(cluster_name, node_name)
        if OK:
            log.write('The SSH transport is connected.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # create the SFTP client 
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Connecting the SFTP client to node {0} ...\n'.format(node_name))
        sftp_client = xssh.create_sftp_client(ssh_transport)
        log.write('The SFTP client is connected.\n')

    # upload the infraestructe software installation script to the node
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Uploading the infraestructe software installation script to the node {0} ...\n'.format(node_name))
        (OK, error_list) = xssh.put_file(sftp_client, local_script_path, node_script_path)
        if OK:
            log.write('The file is uploaded.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # set run permision to the infraestructe software installation script in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Setting on the run permision ...\n')
        command = 'chmod u+x {0}'.format(node_script_path)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The run permision is set.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # submit the infraestructe software installation script
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Submitting the infraestructe software installation script in the node {0} ...\n'.format(node_name))
        command = '{0} &>{1} &'.format(node_script_path, node_log_path)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            log.write('The script is submitted.\n')
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

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def install_node_infrastructure_software_ant(cluster_name, node_name, log):
    '''
    Install infrastructure software in a node.
    '''

    # initialize the control variable
    OK = True

    # create the SSH client connection
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Connecting the SSH client in node {0} ...\n'.format(node_name))
    (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, node_name)
    if OK:
        log.write('The SSH client is connected.\n')
    else:
        for error in error_list:
            log.write('{0}\n'.format(error))

    # update file /etc/apt/sources.list
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Updating the file /etc/apt/sources.list in node {0} ...\n'.format(node_name))
        command = 'sed -i "s/us-east-1\.ec2\.archive\.ubuntu\.com/old-releases\.ubuntu\.com/g" /etc/apt/sources.list'
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        log.write('command: {0}\n'.format(command))
        log.write('OK: {0}\n'.format(OK))
        log.write('stdout: {0}\n'.format(stdout))
        log.write('stderr: {0}\n'.format(stderr))
        OK = True
    if OK:
        command = 'sed -i "s/security\.ubuntu\.com/old-releases\.ubuntu\.com/g" /etc/apt/sources.list'
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        log.write('command: {0}\n'.format(command))
        log.write('OK: {0}\n'.format(OK))
        log.write('stdout: {0}\n'.format(stdout))
        log.write('stderr: {0}\n'.format(stderr))
        OK = True
    if OK:
        command = 'export DEBIAN_FRONTEND=noninteractive; apt-get update'
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        log.write('command: {0}\n'.format(command))
        log.write('OK: {0}\n'.format(OK))
        log.write('stdout: {0}\n'.format(stdout))
        log.write('stderr: {0}\n'.format(stderr))
        OK = True
    if OK:
        log.write('The file is updated.\n')
    else:
        log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # install libtbb2
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Installing the package libtbb2 in node {0} (it can be a very slow process, please be patient) ...\n'.format(node_name))
        command = 'export DEBIAN_FRONTEND=noninteractive; apt-get --assume-yes --force-yes install libtbb2'
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        log.write('command: {0}\n'.format(command))
        log.write('OK: {0}\n'.format(OK))
        log.write('stdout: {0}\n'.format(stdout))
        log.write('stderr: {0}\n'.format(stderr))
        OK = True
        if OK:
            log.write('The package is installed.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    ## install OpenJDK8
    #if OK:
    #    log.write('{0}\n'.format(xlib.get_separator()))
    #    log.write('Installing the package OpenJDK8 in node {0} (it can be a very slow process, please be patient) ...\n'.format(node_name))
    #    command = 'echo "deb http://ppa.launchpad.net/openjdk-r/ppa/ubuntu trusty main" | tee /etc/apt/sources.list.d/openjdk-r.list'
    #    (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    #    log.write('command: {0}\n'.format(command))
    #    log.write('OK: {0}\n'.format(OK))
    #    log.write('stdout: {0}\n'.format(stdout))
    #    log.write('stderr: {0}\n'.format(stderr))
    #    OK = True
    #if OK:
    #    command = 'echo "deb-src http://ppa.launchpad.net/openjdk-r/ppa/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/openjdk-r.list'
    #    (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    #    log.write('command: {0}\n'.format(command))
    #    log.write('OK: {0}\n'.format(OK))
    #    log.write('stdout: {0}\n'.format(stdout))
    #    log.write('stderr: {0}\n'.format(stderr))
    #    OK = True
    #if OK:
    #    #command = 'export DEBIAN_FRONTEND=noninteractive; apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886'
    #    command = 'export DEBIAN_FRONTEND=noninteractive; apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EB9B1D8886F44E2A'
    #    (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    #    log.write('command: {0}\n'.format(command))
    #    log.write('OK: {0}\n'.format(OK))
    #    log.write('stdout: {0}\n'.format(stdout))
    #    log.write('stderr: {0}\n'.format(stderr))
    #    OK = True
    #if OK:
    #    command = 'export DEBIAN_FRONTEND=noninteractive; apt-get update'
    #    (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    #    log.write('command: {0}\n'.format(command))
    #    log.write('OK: {0}\n'.format(OK))
    #    log.write('stdout: {0}\n'.format(stdout))
    #    log.write('stderr: {0}\n'.format(stderr))
    #    OK = True
    #if OK:
    #    command = 'export DEBIAN_FRONTEND=noninteractive; apt-get --assume-yes --force-yes install openjdk-8-jdk'
    #    (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    #    log.write('command: {0}\n'.format(command))
    #    log.write('OK: {0}\n'.format(OK))
    #    log.write('stdout: {0}\n'.format(stdout))
    #    log.write('stderr: {0}\n'.format(stderr))
    #    OK = True
    #if OK:
    #    command = 'export DEBIAN_FRONTEND=noninteractive; update-java-alternatives --set java-1.8.0-openjdk-amd64'
    #    (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    #    log.write('command: {0}\n'.format(command))
    #    log.write('OK: {0}\n'.format(OK))
    #    log.write('stdout: {0}\n'.format(stdout))
    #    log.write('stderr: {0}\n'.format(stderr))
    #    OK = True
    #if OK:
    #    log.write('OpenJDK8 is installed.\n')
    #else:
    #    log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # install Oracle Java 8
    # -- if OK:
    # --     log.write('{0}\n'.format(xlib.get_separator()))
    # --     log.write('Installing Oracle Java 8 in node {0} (it can be a very slow process, please be patient) ...\n'.format(node_name))
    # --     command = 'echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee /etc/apt/sources.list.d/webupd8team-java.list'
    # --     (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    # --     log.write('command: {0}\n'.format(command))
    # --     log.write('OK: {0}\n'.format(OK))
    # --     log.write('stdout: {0}\n'.format(stdout))
    # --     log.write('stderr: {0}\n'.format(stderr))
    # --     OK = True
    # -- if OK:
    # --     command = 'echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list'
    # --     (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    # --     log.write('command: {0}\n'.format(command))
    # --     log.write('OK: {0}\n'.format(OK))
    # --     log.write('stdout: {0}\n'.format(stdout))
    # --     log.write('stderr: {0}\n'.format(stderr))
    # --     OK = True
    # -- if OK:
    # --     command = 'export DEBIAN_FRONTEND=noninteractive; apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886'
    # --     (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    # --     log.write('command: {0}\n'.format(command))
    # --     log.write('OK: {0}\n'.format(OK))
    # --     log.write('stdout: {0}\n'.format(stdout))
    # --     log.write('stderr: {0}\n'.format(stderr))
    # --     OK = True
    # -- if OK:
    # --     command = 'export DEBIAN_FRONTEND=noninteractive; apt-get update'
    # --     (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    # --     log.write('command: {0}\n'.format(command))
    # --     log.write('OK: {0}\n'.format(OK))
    # --     log.write('stdout: {0}\n'.format(stdout))
    # --     log.write('stderr: {0}\n'.format(stderr))
    # --     OK = True
    # -- if OK:
    # --     command = 'echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections'
    # --     (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    # --     log.write('command: {0}\n'.format(command))
    # --     log.write('OK: {0}\n'.format(OK))
    # --     log.write('stdout: {0}\n'.format(stdout))
    # --     log.write('stderr: {0}\n'.format(stderr))
    # --     OK = True
    # -- if OK:
    # --     command = 'export DEBIAN_FRONTEND=noninteractive; apt-get --assume-yes --force-yes install openjdk-8-jdk'
    # --     (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
    # --     log.write('command: {0}\n'.format(command))
    # --     log.write('OK: {0}\n'.format(OK))
    # --     log.write('stdout: {0}\n'.format(stdout))
    # --     log.write('stderr: {0}\n'.format(stderr))
    # --     OK = True
    # -- if OK:
    # --     log.write('Java 8 is installed.\n')
    # -- else:
    # --     log.write('*** ERROR: Wrong command ---> {0}\n'.format(command))

    # close the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing the SSH client connection ...\n')
        xssh.close_ssh_client_connection(ssh_client)
        log.write('The connection is closed.\n')

    # return the control variable
    return OK

#-------------------------------------------------------------------------------

def build_infrastructure_software_installation_script(cluster_name):
    '''
    Build the infrastructure software installation script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # get infrastructure software installation script path
    infrastructure_software_installation_script = get_infrastructure_software_installation_script()

    # write the infrastructure software installation script
    try:
        if not os.path.exists(os.path.dirname(infrastructure_software_installation_script)):
            os.makedirs(os.path.dirname(infrastructure_software_installation_script))
        with open(infrastructure_software_installation_script, mode='w', encoding='utf8', newline='\n') as file_id:
            file_id.write('{0}\n'.format('#!/bin/bash'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('export DEBIAN_FRONTEND=noninteractive'))
            file_id.write('{0}\n'.format('SEP="#########################################"'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function init'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    INIT_DATETIME=`date --utc +%s`'))
            file_id.write('{0}\n'.format('    FORMATTED_INIT_DATETIME=`date --date="@$INIT_DATETIME" "+%Y-%m-%d %H:%M:%S"`'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Script started in node $HOSTNAME of cluster {0} at $FORMATTED_INIT_DATETIME UTC."'.format(cluster_name)))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function fix_source_list'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Fixing file /etc/apt/sources.list ..."'))
            file_id.write('{0}\n'.format('    sed -i "s/us-east-1.ec2.archive.ubuntu.com/old-releases.ubuntu.com/g" /etc/apt/sources.list'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error sed $RC; fi'))
            file_id.write('{0}\n'.format('    sed -i "s/security.ubuntu.com/old-releases.ubuntu\.com/g" /etc/apt/sources.list'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error sed $RC; fi'))
            file_id.write('{0}\n'.format('    apt-get update'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error apt-get $RC; fi'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    echo "The file is fixed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_libtbb2'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing the package libtbb2 ..."'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    apt-get --assume-yes install libtbb2'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error apt-get $RC; fi'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
            file_id.write('{0}\n'.format('}'))
            file_id.write('{0}\n'.format('#-------------------------------------------------------------------------------'))
            file_id.write('{0}\n'.format('function install_mailutils'))
            file_id.write('{0}\n'.format('{'))
            file_id.write('{0}\n'.format('    echo "$SEP"'))
            file_id.write('{0}\n'.format('    echo "Installing the package mailutils ..."'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    HOST_IP=`curl checkip.amazonaws.com`'))
            file_id.write('{0}\n'.format('    HOST_IP2=`echo "${HOST_IP//./-}"`'))
            file_id.write('{0}\n'.format('    HOST_ADDRESS="ec2-${HOST_IP2}-compute-1.amazonaws.com"'))
            file_id.write('{0}\n'.format('    echo "HOST_IP: $HOST_IP   HOST_ADDRESS: $HOST_ADDRESS"'))
            file_id.write('{0}\n'.format('    debconf-set-selections <<< "postfix postfix/mailname string $HOST_ADDRESS"'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error debconf-set-selections $RC; fi'))
            file_id.write('{0}\n'.format('    debconf-set-selections <<< "postfix postfix/main_mailer_type string \'Internet Site\'"'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error debconf-set-selections $RC; fi'))
            file_id.write('{0}\n'.format('    apt-get --assume-yes install mailutils'))
            file_id.write('{0}\n'.format('    RC=$?'))
            file_id.write('{0}\n'.format('    if [ $RC -ne 0 ]; then manage_error apt-get $RC; fi'))
            file_id.write('{0}\n'.format('    echo'))
            file_id.write('{0}\n'.format('    echo "The package is installed."'))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: Infrastructure software installation"'.format(xlib.get_project_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The infrastructure software installation in node $HOSTNAME of cluster {0} ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(cluster_name)))
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
            file_id.write('{0}\n'.format('    SUBJECT="{0}: Infrastructure software installation"'.format(xlib.get_project_name())))
            file_id.write('{0}\n'.format('    MESSAGE="The infrastructure software installation in node $HOSTNAME of cluster {0} ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION).<br/><br/>Regards,<br/>GI Genetica, Fisiologia e Historia Forestal<br/>Dpto. Sistemas y Recursos Naturales<br/>ETSI Montes, Forestal y del Medio Natural<br/>Universidad Politecnica de Madrid<br/>https://github.com/ggfhf/"'.format(cluster_name)))
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
            file_id.write('{0}\n'.format('fix_source_list'))
            file_id.write('{0}\n'.format('install_libtbb2'))
            file_id.write('{0}\n'.format('install_mailutils'))
            file_id.write('{0}\n'.format('end'))
    except:
        error_list.append('*** ERROR: The file {0} can not be created'.format(infrastructure_software_installation_script))
        OK = False

    # return the control variable and the error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def get_infrastructure_software_installation_script():
    '''
    Get the infrastructure software installation script path in the local computer.
    '''

    # assign infrastructure software installation script path
    infrastructure_software_installation_script = '{0}/{1}'.format(xlib.get_temp_dir(), 'infrastructure_software_installation.sh')

    # return the infrastructure software installation script path
    return infrastructure_software_installation_script

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains the functions related to the node operation used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
