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
This source start NGScloud both console mode and gui mode.
'''
#-------------------------------------------------------------------------------

import optparse
import sys

import ccloud
import clib
import cmenu
import gmain
import xlib

#-------------------------------------------------------------------------------

def main(argv):
    '''
    Main line of the program.
    '''

    # verify the operating system.
    if not sys.platform.startswith('linux') and not sys.platform.startswith('darwin') and not sys.platform.startswith('win32') and not sys.platform.startswith('cygwin'):
        print('*** ERROR: The {1} OS is not supported.'.format(sys.platform))
        sys.exit(1)

    # verify the Python version.
    if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
        pass
    else:
        print('A Python version equal or greater than 3.5 is required.')
        sys.exit(1)

    # verify if Boto3 is set up
    try:
        import boto3
    except:
        print('*** ERROR: The library boto3 is not installed.')
        print('Please, review how to set up Boto3 in the manual.')
        sys.exit(1)

    # verify if Paramiko is set up
    try:
        import paramiko
    except:
        print('*** ERROR: The library paramiko is not installed.')
        print('Please, review how to set up Paramiko in the manual.')
        sys.exit(1)

    # verify if Paramiko is set up
    try:
        import paramiko
    except:
        print('*** ERROR: The library paramiko is not installed.')
        print('Please, review how to set up Paramiko in the manual.')
        sys.exit(1)

    # get and verify the options
    parser = build_parser()
    (options, args) = parser.parse_args()
    verify_options(options)

    # verify if the required graphical libraries are setup
    if options.mode == 'gui' or options.mode is None:

        # verify if the library PIL.Image is set up
        try:
            import tkinter
        except:
            print('*** ERROR: The library tkinter is not installed.')
            print('Please, review how to set up Tkinter in the manual.')
            sys.exit(1)

        # verify if the library PIL.Image is set up
        try:
            import PIL.Image
        except:
            print('*** ERROR: The library PIL.Image is not installed.')
            print('Please, review how to set up PIL.Image in the manual.')
            sys.exit(1)

        # verify if the library PIL.ImageTk is set up
        try:
            import PIL.ImageTk
        except:
            print('*** ERROR: The library PIL.ImageTk is not installed.')
            print('Please, review how to set up PIL.ImageTk in the manual.')
            sys.exit(1)

    # import required application libraries
    import ccloud
    import cmenu
    import gmain
    import xlib

    # verify if StarCluster is set up
    command = '{0} --version'.format(xlib.get_starcluster())
    devstdout = xlib.DevStdOut('starcluster_version', print_stdout=False)
    rc = xlib.run_command(command, devstdout)
    if rc != 0:
        print('*** ERROR: The cluster-computing toolkit StarCluster 0.95.6 is not installed or excecution permissions have not set.')
        print('Please, review how to set up in the manual.')
        sys.exit(1)
    else:
        with open(devstdout.get_log_file(), 'r') as log_command:
            version_found = False
            for line in log_command:
                if line.startswith('0.95.6'):
                    version_found = True
            if not version_found:
                print('*** ERROR: The cluster-computing toolkit StarCluster 0.95.6 is not installed or excecution permissions have not set.')
                print('Please, review how to set up in the manual.')
                sys.exit(1)

    # start the user interface depending on the mode
    if options.mode == 'gui' or options.mode is None:
        main = gmain.Main()
        main.mainloop()
    else:
        ccloud.form_set_environment()
        cmenu.build_menu_main()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available options.
    '''

    # create the parser and add options
    parser = optparse.OptionParser()
    parser.add_option('-e', '--env', dest='environment', help='Environment name')
    parser.add_option('-m', '--mode', dest='mode', help='Mode (console or gui)')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def verify_options(options):
    '''
    Verity the input options data.
    '''

    # initialize the control variable
    OK = True

    # verify mode
    if options.mode is not None and options.mode not in ['console', 'gui']:
        print('*** ERROR: The mode must be console or gui.')
        OK = False

    # control if there are any errors
    if not OK:
        raise xlib.ProgramException('P001')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
