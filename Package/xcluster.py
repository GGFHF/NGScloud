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
This source contains the functions related to the cluster operation used in
both console mode and gui mode.
'''
#-------------------------------------------------------------------------------

import re
import subprocess
import sys

import xconfiguration
import xec2
import xlib
import xnode
import xssh

#-------------------------------------------------------------------------------

def list_clusters(log, function=None):
    '''
    List clusters.
    '''

    # initialize the control variable
    OK = True

    # get current region
    region_name = xconfiguration.get_current_region_name()

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take a few minutes. Do not close this window, please wait!\n')

    # warn that the requirements are being verified 
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Verifying process requirements ...\n')

    # verify if there are some running clusters
    if xec2.get_running_cluster_list(volume_creator_included=True) == []:
        log.write('WARNING: There is not any running cluster.\n')
        OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # list clusters
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Listing clusters using StarCluster ...\n')
        log.write('\n')
        command = '{0} --region={1} listclusters'.format(xlib.get_starcluster(), region_name)
        rc = xlib.run_command(command, log)
        if rc != 0:
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

def create_cluster(template_name, cluster_name, log, function=None, is_menu_call=True):
    '''
    Create a cluster from a template name.
    '''

    # initialize the control variable
    OK = True

    # initialize the state variables
    master_state_code = ''
    master_state_name = ''

    # get current region and zone names
    region_name = xconfiguration.get_current_region_name()
    zone_name = xconfiguration.get_current_zone_name()

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut) and is_menu_call:
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # warn that the requirements are being verified 
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Verifying process requirements ...\n')

    # verify that the cluster is defined in the NGScloud config file
    if OK:
        if not xconfiguration.is_template_defined(template_name):
            log.write('*** ERROR: The cluster {0} is not defined in the {1} config file.\n'.format(cluster_name, xlib.get_project_name()))
            OK = False

    # verify that the master is not running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 48 and master_state_code != -1:
            log.write('*** WARNING: The cluster {0} is already created. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # verify that the zone is available
    if OK:
        if not xec2.is_zone_available(region_name, zone_name):
            log.write('*** ERROR: The zone name {0} is not available.\n'.format(zone_name))
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # create the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        if cluster_name == xlib.get_volume_creator_name():
            log.write('Creating the volume creator using StarCluster ...\n')
        else:
            log.write('Creating the cluster {0} using StarCluster ...\n'.format(cluster_name))
        log.write('\n')
        if template_name == xlib.get_volume_creator_name():
            command = '{0} --region={1} start --availability-zone={2} --cluster-template={3} --disable-queue {4}'.format(xlib.get_starcluster(), region_name, zone_name, template_name, cluster_name)
        else:
            command = '{0} --region={1} start --availability-zone={2} --cluster-template={3} {4}'.format(xlib.get_starcluster(), region_name, zone_name, template_name, cluster_name)
        rc = xlib.run_command(command, log)
        log.write('\n')
        if rc == 0:
            (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
            if cluster_name == xlib.get_volume_creator_name():
                log.write('The volume creator is created.\n')
            else:
                log.write('The cluster is created.\n')
        else:
            log.write('*** ERROR: Return code {0} in command -> {1}\n'.format(rc, command))
            OK = False

    # install infraestructure software in every node of the cluster
    if OK:
        if cluster_name != xlib.get_volume_creator_name():
            cluster_node_list = xec2.get_cluster_node_list(cluster_name)
            for node_name in cluster_node_list:
                OK = xnode.install_node_infrastructure_software(cluster_name, node_name, log)

    # warn that the log window can be closed
    if not isinstance(log, xlib.DevStdOut) and is_menu_call:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('You can close this window now.\n')

    # execute final function
    if function is not None:
        function()

    # return the control variable and the state
    return (OK, master_state_code, master_state_name)

#-------------------------------------------------------------------------------

def stop_cluster(cluster_name, log, function=None):
    '''
    Stop, but not terminate, a cluster.Then it must be restarted.
    '''

    # initialize the control variable
    OK = True

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take a few minutes. Do not close this window, please wait!\n')

    # warn that the requirements are being verified 
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Verifying process requirements ...\n')

    # verify the cluster is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # stop the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Stopping cluster {0} using StarCluster ...\n'.format(cluster_name))
        log.write('\n')
        command = '{0} stop --confirm {1}'.format(xlib.get_starcluster(), cluster_name)
        rc = xlib.run_command(command, log)
        log.write('\n')
        if rc == 0:
            log.write('The cluster is stopping.\n')
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

def restart_cluster(cluster_name, log, function=None):
    '''
    Restart a cluster.
    '''

    # initialize the control variable
    OK = True

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut):
        log.write('This process might take several minutes. Do not close this window, please wait!\n')

    # warn that the requirements are being verified 
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Verifying process requirements ...\n')

    # verify the master is stopped
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if master_state_code != 80:
            log.write('*** ERROR: The cluster {0} is not stopped. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # restart the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Restarting cluster {0} using StarCluster ...\n'.format(cluster_name))
        log.write('\n')
        command = '{0} start --no-create {1}'.format(xlib.get_starcluster(), cluster_name)
        rc = xlib.run_command(command, log)
        log.write('\n')
        if rc == 0:
            log.write('The cluster is restarted.\n')
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

def terminate_cluster(cluster_name, force, log, function=None, is_menu_call=True):
    '''
    Terminate a cluster.
    '''

    # initialize the control variable
    OK = True

    # get current region
    region_name = xconfiguration.get_current_region_name()

    # warn that the log window must not be closed
    if not isinstance(log, xlib.DevStdOut) and is_menu_call:
        log.write('This process might take a few minutes. Do not close this window, please wait!\n')

    # warn that the requirements are being verified 
    log.write('{0}\n'.format(xlib.get_separator()))
    log.write('Verifying process requirements ...\n')

    # verify the cluster is running
    if OK:
        (master_state_code, master_state_name) = xec2.get_node_state(cluster_name, 'master')
        if not force and master_state_code != 16:
            log.write('*** ERROR: The cluster {0} is not running. Its state is {1} ({2}).\n'.format(cluster_name, master_state_code, master_state_name))
            OK = False

    # warn that the requirements are OK 
    if OK:
        log.write('Process requirements are OK.\n')

    # terminate cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        if cluster_name == xlib.get_volume_creator_name():
            log.write('Terminating the volume creator using StarCluster ...\n')
        else:
            log.write('Terminating the cluster {0} using StarCluster ...\n'.format(cluster_name))
        log.write('\n')
        if not force:
            command = '{0} --region={1} terminate --confirm {2}'.format(xlib.get_starcluster(), region_name, cluster_name)
        else:
            command = '{0} --region={1} terminate --force --confirm {2}'.format(xlib.get_starcluster(), region_name, cluster_name)
        rc = xlib.run_command(command, log)
        log.write('\n')
        if rc == 0:
            if cluster_name == xlib.get_volume_creator_name():
                log.write('The volume creator is terminated.\n')
            else:
                log.write('The cluster is terminated.\n')
        else:
            log.write('*** ERROR: Return code {0} in command -> {1}\n'.format(rc, command))
            OK = False

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

def show_cluster_composing(cluster_name, log, function=None):
    '''
    Show cluster information of every node: OS, CPU number and memory. 
    '''

    # initialize the control variable
    OK = True

    # create the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Establishing connection with cluster {0} ...\n'.format(cluster_name))
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if OK:
            log.write('The connection is established.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # show the cluster composing
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        sge_env = get_sge_env()
        command = '{0}; qhost'.format(sge_env)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            if len(stdout) > 0:
                for line in stdout:
                    log.write('{0}\n'.format(line))
            else:
                log.write('Cluster composing not found.\n')
        else:
            log.write('*** ERROR: Wrong command ---> {0}.\n'.format(command))

    # close the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing connection with cluster {0} ...\n'.format(cluster_name))
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

def kill_batch_job(cluster_name, job_id, log, function=None):
    '''
    Kill a batch job in the cluster.
    '''

    # initialize the control variable
    OK = True

    # create the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Establishing connection with cluster {0} ...\n'.format(cluster_name))
        (OK, error_list, ssh_client) = xssh.create_ssh_client_connection(cluster_name, 'master')
        if OK:
            log.write('The connection is established.\n')
        else:
            for error in error_list:
                log.write('{0}\n'.format(error))

    # kill the job in the cluster
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        sge_env = get_sge_env()
        command = '{0}; qdel {1}'.format(sge_env, job_id)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            if len(stdout) > 0:
                for line in stdout:
                    log.write('{0}\n'.format(line))
            else:
                log.write('The job is been killed.\n')
            if len(stderr) > 0:
                for line in stderr:
                    log.write('{0}\n'.format(line))
        else:
            log.write('*** ERROR: Wrong command ---> {0}.\n'.format(command))

    # close the SSH client connection
    if OK:
        log.write('{0}\n'.format(xlib.get_separator()))
        log.write('Closing connection with cluster {0} ...\n'.format(cluster_name))
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

def get_batch_job_dict(ssh_client):
    '''
    Get a dictionary with the batch jobs in the cluster.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # initialize the dictionary of the batch jobs
    batch_job_dict = {}

    # list the jobs running in the cluster and load the dictionary
    if OK:
        sge_env = get_sge_env()
        command = '{0}; qstat'.format(sge_env)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            if len(stdout) > 0:
                i = 0
                for line in stdout:
                    if i >= 2:
                        try:
                            line_pattern = r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.+)$'
                            mo = re.search(line_pattern, line.strip())
                            job_id = mo.group(1).strip()
                            priority = mo.group(2).strip()
                            job_name = mo.group(3).strip()
                            user = mo.group(4).strip()
                            state_id = mo.group(5).strip()
                            if state_id == 'd':
                                state_name = 'deletion'
                            elif state_id == 'E':
                                state_name = 'error'
                            elif state_id == 'h':
                                state_name = 'hold'
                            elif state_id == 'r':
                                state_name = 'running'
                            elif state_id == 'R':
                                state_name = 'restarted'
                            elif state_id in ['s', 'S']:
                                state_name = 'suspended'
                            elif state_id == 't':
                                state_name = 'transfering'
                            elif state_id == 'T':
                                state_name = 'thresold'
                            elif state_id in ['w', 'qw']:
                                state_name = 'waiting'
                            else:
                                state_name = 'xxx'
                            state = '{0} ({1})'.format(state_id, state_name)
                            mm_dd_yyyy = mo.group(6).strip()
                            start_date = '{0}-{1}-{2}'.format(mm_dd_yyyy[6:], mm_dd_yyyy[:2], mm_dd_yyyy[3:5])
                            start_time = mo.group(7).strip()
                            batch_job_dict[job_id] = {'job_id': job_id, 'priority': priority, 'job_name': job_name, 'user': user, 'state_id': state_id, 'state_name': state_name, 'state': state, 'start_date': start_date, 'start_time': start_time}
                        except:
                            pass
                    i += 1
        else:
            error_list.append('*** ERROR: Wrong command ---> {0}.\n'.format(command))

    # return the control variable, error list and dictionary of the batch jobs
    return (OK, error_list, batch_job_dict)

#-------------------------------------------------------------------------------

def open_terminal(cluster_name, node_name):
    '''
    Open a terminal window in a node of the cluster.
    '''

    # set the command to start the terminal window and run ssh script
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        terminal_window_command = 'x-terminal-emulator -e ./sshnode.sh {0} {1} {2}'.format(xconfiguration.environment, cluster_name, node_name).split()
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        terminal_window_command = 'cmd.exe /c start .\sshnode.bat {0} {1} {2}'.format(xconfiguration.environment, cluster_name, node_name).split()

    # open the new terminal
    process = subprocess.Popen(terminal_window_command)

#-------------------------------------------------------------------------------

def get_sge_env():
    '''
    Get the SGE environment in the cluster (see /etc/profile.d/sge.sh in the cluster).
    '''

    # set SGE environment
    sge_env = 'export SGE_ROOT="/opt/sge6";'
    sge_env += 'export SGE_CELL="default";'
    sge_env += 'export SGE_CLUSTER_NAME="starcluster";'
    sge_env += 'export SGE_QMASTER_PORT="63231";'
    sge_env += 'export SGE_EXECD_PORT="63232";'
    sge_env += 'export MANTYPE="man";'
    sge_env += 'export MANPATH="$MANPATH:$SGE_ROOT/man";'
    sge_env += 'export PATH="$PATH:$SGE_ROOT/bin/linux-x64";'
    sge_env += 'export ROOTPATH="$ROOTPATH:$SGE_ROOT/bin/linux-x64";'
    sge_env += 'export LDPATH="$LDPATH:$SGE_ROOT/lib/linux-x64";'
    sge_env += 'export DRMAA_LIBRARY_PATH="$SGE_ROOT/lib/linux-x64/libdrmaa.so"'

    # return SGE environment
    return sge_env

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This file contains the functions related to the cluster operation used in both console mode and gui mode.')
     sys.exit(0)

#-------------------------------------------------------------------------------
