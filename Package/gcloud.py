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
This file contains the classes related to forms corresponding to Cloud Control
menu items in gui mode.
'''

#-------------------------------------------------------------------------------

import os
import PIL.Image
import PIL.ImageTk
import sys
import threading
import tkinter
import tkinter.filedialog
import tkinter.ttk

import gdialogs
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
import xrnaquast
import xsoapdenovotrans
import xssh
import xstar
import xread
import xreference
import xresult
import xtransabyss
import xtransrate
import xtrimmomatic
import xtrinity
import xvolume

#-------------------------------------------------------------------------------

class FormSetEnvironment(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormSetEnvironment" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Set environment'

        # create the wrappers to track changes in inputs
        self.wrapper_environment = tkinter.StringVar()
        self.wrapper_environment.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormSetEnvironment".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_instructions" and register it with the grid geometry manager
        self.label_instructions = tkinter.Label(self, text='Select an environment or type a new one:')
        self.label_instructions.grid(row=0, column=0, columnspan=2, padx=(15,5), pady=(75,5), sticky='w')

        # create "label_environment" and register it with the grid geometry manager
        self.label_environment = tkinter.Label(self, text='Environment')
        self.label_environment.grid(row=1, column=0, padx=(15,5), pady=(25,5), sticky='e')

        # create "combobox_environment" and register it with the grid geometry manager
        self.combobox_environment = tkinter.ttk.Combobox(self, width=40, height=4, state='normal', textvariable=self.wrapper_environment)
        self.combobox_environment.grid(row=1, column=1, padx=(5,5), pady=(25,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*25)
        self.label_fit.grid(row=2, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=2, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_exit" and register it with the grid geometry manager
        self.button_exit = tkinter.ttk.Button(self, text='Exit', command=self.exit)
        self.button_exit.grid(row=2, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_environment.bind('<<ComboboxSelected>>', self.combobox_environment_selected_item)

    #---------------

    def combobox_environment_selected_item(self, event=None):
        '''
        Process the event when an environment item has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Set the environment.
        '''

        # if the environment is new, verify it is right
        if self.wrapper_environment.get() not in xconfiguration.get_environments_list():
            message = '{0} is not an environment recorded. Do you like to record it?'.format(self.wrapper_environment.get())
            OK = tkinter.messagebox.askyesno('{0} - Exit'.format(xlib.get_project_name()), message)
            if not OK:
                return

        # set the current environment
        xconfiguration.environment = self.wrapper_environment.get()

        # record the curren environment if it is not recorded
        if xconfiguration.environment not in xconfiguration.get_environments_list():
            (OK, error_list) = xconfiguration.add_environment(xconfiguration.environment)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                raise xlib.ProgramException('C002')

        # check if it is necesary to create the NGScloud config file corresponding to the environment
        if not xconfiguration.is_ngscloud_config_file_created():

            # clear the label of the current process name
            self.main.label_process['text'] = ''

            # close the current form
            self.main.close_current_form()

            # create and register "form_create_config_files" in "container" of "Main with the grid geometry manager
            form_create_config_files = FormCreateConfigFiles(self.main.container, self.main)
            form_create_config_files.grid(row=0, column=0, sticky='nsew')

            # set "form_create_config_files" as current form and add it in the forms dictionary
            self.main.current_form = 'form_create_config_files'
            self.main.forms_dict[self.main.current_form] = form_create_config_files

            # raise "form_create_config_files" to front
            form_create_config_files.tkraise()

        # in case of the config file of the environment is created
        else:

            # set the environment variables corresponding to the NGScloud config file, the AWS access key identification, AWS secret access key and the current region name
            xconfiguration.set_environment_variables()

            # set the current region, zone and environment in the corresponding widgets of "frame_information"
            self.main.label_region_value['text'] = xconfiguration.get_current_region_name()
            self.main.label_zone_value['text'] = xconfiguration.get_current_zone_name()
            self.main.label_environment_value['text'] = xconfiguration.environment

            # clear the label of the current process name
            self.main.label_process['text'] = ''

            # build the full menu of the application
            self.main.build_full_menu()

            # close the current form
            self.main.close_current_form()

    #---------------

    def exit(self, event=None):
        '''
        Exit the application.
        '''

        # initialize the control variable
        OK = True

        # confirm the exit of NGScloud
        message = 'Are you sure to exit {0}?'.format(xlib.get_project_name())
        OK = tkinter.messagebox.askyesno('{0} - Exit'.format(xlib.get_project_name()), message)

        # exit NGScloud
        if OK:
            # destroy "FormStart"
            self.destroy()
            # destroy "Main"
            self.main.destroy()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_environment()

    #---------------

    def populate_combobox_environment(self):
        '''
        Populate data in "combobox_environment".
        '''

        # clear the value selected in the combobox
        #self.wrapper_environment.set('')

        # verify if there are any running clusters
        if xconfiguration.get_environments_list() == []:
            message = 'There is not any environment recorded. You have to type a new one.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_environment['values'] = xconfiguration.get_environments_list()

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormSetEnvironment" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_continue" has to be enabled or disabled
        if self.wrapper_environment.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormCreateConfigFiles(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormCreateConfigFiles" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Create config files'

        # create the wrappers to track changes in inputs
        self.wrapper_user_id = tkinter.StringVar()
        self.wrapper_user_id.trace('w', self.validate_inputs)
        self.wrapper_access_key_id = tkinter.StringVar()
        self.wrapper_access_key_id.trace('w', self.validate_inputs)
        self.wrapper_secret_access_key = tkinter.StringVar()
        self.wrapper_secret_access_key.trace('w', self.validate_inputs)
        self.wrapper_email = tkinter.StringVar()
        self.wrapper_email.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormCreateConfigFiles".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_user_id" and register it with the grid geometry manager
        self.label_user_id = tkinter.Label(self, text='User id')
        self.label_user_id.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "entry_user_id" and register it with the grid geometry manager
        self.entry_user_id = tkinter.Entry(self, textvariable=self.wrapper_user_id, width=15, validatecommand=self.validate_inputs)
        self.entry_user_id.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_access_key_id" and register it with the grid geometry manager
        self.label_access_key_id = tkinter.Label(self, text='Access key id')
        self.label_access_key_id.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_access_key_id" and register it with the grid geometry manager
        self.entry_access_key_id = tkinter.Entry(self, textvariable=self.wrapper_access_key_id, width=25, validatecommand=self.validate_inputs)
        self.entry_access_key_id.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_secret_access_key" and register it with the grid geometry manager
        self.label_secret_access_key = tkinter.Label(self, text='Secret access key')
        self.label_secret_access_key.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_secret_access_key" and register it with the grid geometry manager
        self.entry_secret_access_key = tkinter.Entry(self, textvariable=self.wrapper_secret_access_key, width=50, validatecommand=self.validate_inputs)
        self.entry_secret_access_key.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_email" and register it with the grid geometry manager
        self.label_email = tkinter.Label(self, text='Contact e-mail')
        self.label_email.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_email" and register it with the grid geometry manager
        self.entry_email = tkinter.Entry(self, textvariable=self.wrapper_email, width=50, validatecommand=self.validate_inputs)
        self.entry_email.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_email_warning" and register it with the grid geometry manager
        self.label_email_warning = tkinter.Label(self, text='')
        self.label_email_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*1)
        self.label_fit.grid(row=5, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_create" and register it with the grid geometry manager
        self.button_create = tkinter.ttk.Button(self, text='Create', command=self.create, state='disabled')
        self.button_create.grid(row=5, column=3, padx=(5,5), pady=(25,5), sticky='e')

        # create "button_exit" and register it with the grid geometry manager
        self.button_exit = tkinter.ttk.Button(self, text='Exit', command=self.exit)
        self.button_exit.grid(row=5, column=4, padx=(5,5), pady=(25,5), sticky='w')

    #---------------

    def create(self, event=None):
        '''
        Create the config files.
        '''

        # initialize the control variable
        OK = True

        # verify the AWS access key identification and the AWS secret access key   
        OK = xec2.verify_aws_credentials(self.wrapper_access_key_id.get(), self.wrapper_secret_access_key.get())
        if not OK:
            message = 'ERROR: The credentials are wrong. Please review your access key identification and secret access key in the AWS web.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # create the NGScloud config file corresponding to the environment
        if OK:
            (OK, error_list) = xconfiguration.create_ngscloud_config_file(self.wrapper_user_id.get(), self.wrapper_access_key_id.get(), self.wrapper_secret_access_key.get(), self.wrapper_email.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                raise xlib.ProgramException('C001')

        # create the key pairs directory
        if OK:
            if not os.path.exists(xlib.get_keypairs_dir()):
                os.makedirs(xlib.get_keypairs_dir())

        # create the config files
        if OK:

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
            (OK, error_list) = xngshelper.create_transcriptome_blastx_config_file()

            # create the transcriptome-blastx config file
            (OK, error_list) = xngshelper.create_transcript_filter_config_file()

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

        # show the creation message
        if OK:
            message = 'The config files are created with default values.'
            tkinter.messagebox.showinfo('{0} - Start'.format(xlib.get_project_name()), message)

        # set the environment variables corresponding to the NGScloud config file
        if OK:
            xconfiguration.set_environment_variables()

        # set the current region, zone and environment in the corresponding widgets of "frame_information"
        if OK:
            self.main.label_region_value['text'] = xconfiguration.get_current_region_name()
            self.main.label_zone_value['text'] = xconfiguration.get_current_zone_name()
            self.main.label_environment_value['text'] = xconfiguration.environment

        # clear the label of the current process name
        if OK:
            self.main.label_process['text'] = ''

        # build the full menu of the application
        if OK:
            self.main.build_full_menu()

        # close the current form
        if OK:
            self.main.close_current_form()

    #---------------

    def exit(self, event=None):
        '''
        Exit the application.
        '''

        # initialize the control variable
        OK = True

        # confirm the exit of NGScloud
        message = 'Are you sure to exit {0}?'.format(xlib.get_project_name())
        OK = tkinter.messagebox.askyesno('{0} - Exit'.format(xlib.get_project_name()), message)

        # exit NGScloud
        if OK:
            # destroy "FormStart"
            self.destroy()
            # destroy "Main"
            self.main.destroy()

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormCreateConfigFiles" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_email"
        if not self.validate_entry_email():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_user_id.get() != '' and self.wrapper_access_key_id.get() != '' and self.wrapper_secret_access_key.get() != '' and self.wrapper_email.get() != '':
            self.button_create['state'] = 'enable'
        else:
            self.button_create['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_email(self):
        '''
        Validate the content of "entry_email"
        '''

        # initialize the control variable
        OK = True

        # verify if the e-mail address in "entry_email" is valid
        if not xlib.is_email_address_valid(self.wrapper_email.get()):
            self.label_email_warning['text'] = 'The e-mail address is not OK.'
            self.label_email_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_email_warning['text'] = ''
            self.label_email_warning['foreground'] = 'black'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormRecreateNGScloudConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateNGScloudConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Configuration - Recreate TransciptomeCloud config file'

        # create the wrappers to track changes in inputs
        self.wrapper_user_id = tkinter.StringVar()
        self.wrapper_user_id.trace('w', self.validate_inputs)
        self.wrapper_access_key_id = tkinter.StringVar()
        self.wrapper_access_key_id.trace('w', self.validate_inputs)
        self.wrapper_secret_access_key = tkinter.StringVar()
        self.wrapper_secret_access_key.trace('w', self.validate_inputs)
        self.wrapper_email = tkinter.StringVar()
        self.wrapper_email.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial value to inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormRecreateNGScloudConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_user_id" and register it with the grid geometry manager
        self.label_user_id = tkinter.Label(self, text='User id')
        self.label_user_id.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "entry_user_id" and register it with the grid geometry manager
        self.entry_user_id = tkinter.Entry(self, textvariable=self.wrapper_user_id, width=15, validatecommand=self.validate_inputs)
        self.entry_user_id.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_access_key_id" and register it with the grid geometry manager
        self.label_access_key_id = tkinter.Label(self, text='Access key id')
        self.label_access_key_id.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_access_key_id" and register it with the grid geometry manager
        self.entry_access_key_id = tkinter.Entry(self, textvariable=self.wrapper_access_key_id, width=25, validatecommand=self.validate_inputs)
        self.entry_access_key_id.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_secret_access_key" and register it with the grid geometry manager
        self.label_secret_access_key = tkinter.Label(self, text='Secret access key')
        self.label_secret_access_key.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_secret_access_key" and register it with the grid geometry manager
        self.entry_secret_access_key = tkinter.Entry(self, textvariable=self.wrapper_secret_access_key, width=50, validatecommand=self.validate_inputs)
        self.entry_secret_access_key.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_email" and register it with the grid geometry manager
        self.label_email = tkinter.Label(self, text='Contact e-mail')
        self.label_email.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_email" and register it with the grid geometry manager
        self.entry_email = tkinter.Entry(self, textvariable=self.wrapper_email, width=50, validatecommand=self.validate_inputs)
        self.entry_email.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_email_warning" and register it with the grid geometry manager
        self.label_email_warning = tkinter.Label(self, text='')
        self.label_email_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*1)
        self.label_fit.grid(row=5, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=5, column=3, padx=(5,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=5, column=4, padx=(5,5), pady=(25,5), sticky='w')

    #---------------

    def execute(self, event=None):
        '''
        Execute the recreation of the NGScloud config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the recreation of the NGScloud config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xconfiguration.get_ngscloud_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the NGScloud config file corresponding to the environment
        if OK:
            (OK, error_list) = xconfiguration.create_ngscloud_config_file(self.wrapper_user_id.get(), self.wrapper_access_key_id.get(), self.wrapper_secret_access_key.get(), self.wrapper_email.get())
            if OK:
                message = 'The file {0} is created with default values.'.format(xconfiguration.get_ngscloud_config_file())
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # set the current region and zone in the corresponding widgets of "frame_information"
        if OK:
            self.main.label_region_value['text'] = xconfiguration.get_current_region_name()
            self.main.label_zone_value['text'] = xconfiguration.get_current_zone_name()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateNGScloudConfigFile".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # get basic AWS data and contact e-mail address from NGScloud config file
        (user_id, access_key_id, secret_access_key) = xconfiguration.get_basic_aws_data()
        email = xconfiguration.get_contact_data()

        # load initial data in inputs
        self.wrapper_user_id.set(user_id)
        self.wrapper_access_key_id.set(access_key_id)
        self.wrapper_secret_access_key.set(secret_access_key)
        self.wrapper_email.set(email)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateNGScloudConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_email"
        if not self.validate_entry_email():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_user_id.get() != '' and self.wrapper_access_key_id.get() != '' and self.wrapper_secret_access_key.get() != '' and self.wrapper_email.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_email(self):
        '''
        Validate the content of "entry_email"
        '''

        # initialize the control variable
        OK = True

        # verify if the e-mail address in "entry_email" is valid
        if not xlib.is_email_address_valid(self.wrapper_email.get()):
            self.label_email_warning['text'] = 'The e-mail address is not OK.'
            self.label_email_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_email_warning['text'] = ''
            self.label_email_warning['foreground'] = 'black'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormUpdateConnectionData(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormUpdateConnectionData" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Configuration - Update connection data and contact e-mail'

        # create the wrappers to track changes in inputs
        self.wrapper_user_id = tkinter.StringVar()
        self.wrapper_user_id.trace('w', self.validate_inputs)
        self.wrapper_access_key_id = tkinter.StringVar()
        self.wrapper_access_key_id.trace('w', self.validate_inputs)
        self.wrapper_secret_access_key = tkinter.StringVar()
        self.wrapper_secret_access_key.trace('w', self.validate_inputs)
        self.wrapper_email = tkinter.StringVar()
        self.wrapper_email.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial value to inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormUpdateConnectionData".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_user_id" and register it with the grid geometry manager
        self.label_user_id = tkinter.Label(self, text='User id')
        self.label_user_id.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "entry_user_id" and register it with the grid geometry manager
        self.entry_user_id = tkinter.Entry(self, textvariable=self.wrapper_user_id, width=15, validatecommand=self.validate_inputs)
        self.entry_user_id.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_access_key_id" and register it with the grid geometry manager
        self.label_access_key_id = tkinter.Label(self, text='Access key id')
        self.label_access_key_id.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_access_key_id" and register it with the grid geometry manager
        self.entry_access_key_id = tkinter.Entry(self, textvariable=self.wrapper_access_key_id, width=25, validatecommand=self.validate_inputs)
        self.entry_access_key_id.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_secret_access_key" and register it with the grid geometry manager
        self.label_secret_access_key = tkinter.Label(self, text='Secret access key')
        self.label_secret_access_key.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_secret_access_key" and register it with the grid geometry manager
        self.entry_secret_access_key = tkinter.Entry(self, textvariable=self.wrapper_secret_access_key, width=50, validatecommand=self.validate_inputs)
        self.entry_secret_access_key.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_email" and register it with the grid geometry manager
        self.label_email = tkinter.Label(self, text='Contact e-mail')
        self.label_email.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_email" and register it with the grid geometry manager
        self.entry_email = tkinter.Entry(self, textvariable=self.wrapper_email, width=50, validatecommand=self.validate_inputs)
        self.entry_email.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_email_warning" and register it with the grid geometry manager
        self.label_email_warning = tkinter.Label(self, text='')
        self.label_email_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*1)
        self.label_fit.grid(row=5, column=2, padx=(0,0), pady=(55,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=5, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=5, column=4, padx=(5,5), pady=(55,5), sticky='w')

    #---------------

    def execute(self, event=None):
        '''
        Execute the update of the connection data in the NGScloud config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # verify the AWS access key identification and the AWS secret access key
        if OK:
            OK = xec2.verify_aws_credentials(self.wrapper_access_key_id.get(), self.wrapper_secret_access_key.get())
            if not OK:
                message = 'ERROR: The credentials are wrong. Please review your access key identification and secret access key in the AWS web.'
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the NGScloud config file
        if OK:
            ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

        # confirm the connection data update in the NGScloud config file
        if OK:
            message = 'The file {0} is going to be update with the new connection data.\n\nAre you sure to continue?'.format(ngscloud_config_file)
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # update the connection data in the NGScloud config file corresponding to the environment
        if OK:
            (OK, error_list) = xconfiguration.update_connection_data(self.wrapper_user_id.get(), self.wrapper_access_key_id.get(), self.wrapper_secret_access_key.get())
            if OK:
                (OK, error_list) = xconfiguration.update_contact_data(self.wrapper_email.get())
            if OK:
                message = 'The file {0} has been updated.'.format(ngscloud_config_file)
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                raise xlib.ProgramException('C001')

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormUpdateConnectionData".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''
        # get basic AWS data and contact e-mail address from NGScloud config file
        (user_id, access_key_id, secret_access_key) = xconfiguration.get_basic_aws_data()
        email = xconfiguration.get_contact_data()

        # load initial data in inputs
        self.wrapper_user_id.set(user_id)
        self.wrapper_access_key_id.set(access_key_id)
        self.wrapper_secret_access_key.set(secret_access_key)
        self.wrapper_email.set(email)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormUpdateConnectionData" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_email"
        if not self.validate_entry_email():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_user_id.get() != '' and self.wrapper_access_key_id.get() != '' and self.wrapper_secret_access_key.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_email(self):
        '''
        Validate the content of "entry_email"
        '''

        # initialize the control variable
        OK = True

        # verify if the e-mail address in "entry_email" is valid
        if not xlib.is_email_address_valid(self.wrapper_email.get()):
            self.label_email_warning['text'] = 'The e-mail address is not OK.'
            self.label_email_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_email_warning['text'] = ''
            self.label_email_warning['foreground'] = 'black'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormUpdateRegionZone(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormUpdateRegionZone" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Configuration - Update region and zone'

        # set the region name and zone name
        self.region_name = None
        self.zone_name = None

        # create the wrappers to track changes in inputs
        self.wrapper_region_name = tkinter.StringVar()
        self.wrapper_region_name.trace('w', self.validate_inputs)
        self.wrapper_zone_name = tkinter.StringVar()
        self.wrapper_zone_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormUpdateRegionZone".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_region_name" and register it with the grid geometry manager
        self.label_region_name = tkinter.Label(self, text='Region name')
        self.label_region_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_region_name" and register it with the grid geometry manager
        self.combobox_region_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_region_name)
        self.combobox_region_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_zone_name" and register it with the grid geometry manager
        self.label_zone_name = tkinter.Label(self, text='Zone name')
        self.label_zone_name.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_zone_name" and register it with the grid geometry manager
        self.combobox_zone_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_zone_name)
        self.combobox_zone_name.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*65)
        self.label_fit.grid(row=2, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=2, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=2, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_region_name.bind('<<ComboboxSelected>>', self.combobox_region_name_selected_item)
        self.combobox_zone_name.bind('<<ComboboxSelected>>', self.combobox_zone_name_selected_item)

    #---------------

    def combobox_region_name_selected_item(self, parent, event=None):
        '''
        Process the event when a region name item has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_zone_name"
        self.populate_combobox_zone_name()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_zone_name_selected_item(self, parent, event=None):
        '''
        Process the event when a region name item has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the update of the region and zone in the NGScloud config file.
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the NGScloud config file
        if OK:
            ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

        # confirm the region and zone update in the NGScloud config file
        if OK:
            message = 'The file {0} is going to be update with the new the new region and zone.\n\nAre you sure to continue?'.format(ngscloud_config_file)
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # update the connection data in the NGScloud config file corresponding to the environment
        if OK:
            (OK, error_list) = xconfiguration.update_region_zone_data(self.wrapper_region_name.get(), self.wrapper_zone_name.get())
            if OK:
                message = 'The file {0} has been updated.'.format(ngscloud_config_file)
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # set the current region and zone in the corresponding widgets of "frame_information"
        if OK:
            self.main.label_region_value['text'] = xconfiguration.get_current_region_name()
            self.main.label_zone_value['text'] = xconfiguration.get_current_zone_name()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormUpdateRegionZone".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_region_name()

    #---------------

    def populate_combobox_region_name(self):
        '''
        Populate data in "combobox_region_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_region_name.set('')

        # load the region names list in the combobox
        self.combobox_region_name['values'] = xec2.get_available_region_list()

    #---------------

    def populate_combobox_zone_name(self):
        '''
        Populate data in "combobox_zone_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_zone_name.set('')

        # load the region name list in the combobox
        self.combobox_zone_name['values'] = xec2.get_available_zone_list(self.wrapper_region_name.get())

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormUpdateRegionZone" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_region_name.get() != '' and self.wrapper_zone_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormLinkVolumeToTemplate(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormLinkVolumeToTemplate" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Configuration - Link volume in a cluster template'

        # create the wrappers to track changes in inputs
        self.wrapper_template_name = tkinter.StringVar()
        self.wrapper_template_name.trace('w', self.validate_inputs)
        self.wrapper_mounting_point = tkinter.StringVar()
        self.wrapper_mounting_point.trace('w', self.validate_inputs)
        self.wrapper_volume_name = tkinter.StringVar()
        self.wrapper_volume_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormLinkVolumeToTemplate".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_template_name" and register it with the grid geometry manager
        self.label_template_name = tkinter.Label(self, text='Template name')
        self.label_template_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_template_name" and register it with the grid geometry manager
        self.combobox_template_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_template_name)
        self.combobox_template_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_mounting_point" and register it with the grid geometry manager
        self.label_mounting_point = tkinter.Label(self, text='Mounting point')
        self.label_mounting_point.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_mounting_point" and register it with the grid geometry manager
        self.combobox_mounting_point = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_mounting_point)
        self.combobox_mounting_point.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_volume_name" and register it with the grid geometry manager
        self.label_volume_name = tkinter.Label(self, text='Volume name')
        self.label_volume_name.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_volume_name" and register it with the grid geometry manager
        self.combobox_volume_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_volume_name)
        self.combobox_volume_name.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*20)
        self.label_fit.grid(row=3, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=3, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=3, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_template_name.bind('<<ComboboxSelected>>', self.combobox_template_name_selected_item)
        self.combobox_mounting_point.bind('<<ComboboxSelected>>', self.combobox_mounting_point_selected_item)
        self.combobox_volume_name.bind('<<ComboboxSelected>>', self.combobox_volume_name_selected_item)

    #---------------

    def combobox_template_name_selected_item(self, event=None):
        '''
        Process the event when a template name item has been selected
        '''

        pass

    #---------------

    def combobox_mounting_point_selected_item(self, event=None):
        '''
        Process the event when a template name item has been selected
        '''

        pass

    #---------------

    def combobox_volume_name_selected_item(self, event=None):
        '''
        Process the event when a volume name item has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the link of the volume to the cluster template.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the NGScloud config file
        if OK:
            ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

        # confirm the region and zone update in the NGScloud config file
        if OK:
            message = 'The file {0} is going to be update linking the volume {1} to the cluster template {2}.\n\nAre you sure to continue?'.format(ngscloud_config_file, self.wrapper_volume_name.get(), self.wrapper_template_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # link the volume to the cluster template in the NGScloud config file corresponding to the environment
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xconfiguration.link_volume_to_template.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xconfiguration.link_volume_to_template, args=(self.wrapper_template_name.get(), self.wrapper_mounting_point.get(), self.wrapper_volume_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormLinkVolumeToTemplate".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_template_name()
        self.populate_combobox_mounting_point()
        self.populate_combobox_volume_name()

    #---------------

    def populate_combobox_template_name(self):
        '''
        Populate data in "combobox_template_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_template_name.set('')

        # get the template names list
        template_name_list = xconfiguration.get_template_name_list(volume_creator_included=False)
        template_name_list.sort()

        # add item 'all' to template name list
        template_name_list = ['all'] + template_name_list

        # load the template names list in the combobox
        self.combobox_template_name['values'] = template_name_list

    #---------------

    def populate_combobox_mounting_point(self):
        '''
        Populate data in "combobox_mounting_point".
        '''

        # clear the value selected in the combobox
        self.wrapper_mounting_point.set('')

        # load the mounting points list in the combobox
        self.combobox_mounting_point['values'] = xlib.get_mounting_point_list()

    #---------------

    def populate_combobox_volume_name(self):
        '''
        Populate data in "combobox_volume_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_volume_name.set('')

        # get current zone name
        zone_name = xconfiguration.get_current_zone_name()

        # verify if there are any linked volumes
        created_volume_name_list = xec2.get_created_volume_name_list(zone_name)
        if created_volume_name_list == []:
            message = 'There is not any volume created in the zone {0}.'.format(zone_name)
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the volume names list in the combobox
        self.combobox_volume_name['values'] = created_volume_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormLinkVolumeToTemplate" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_template_name.get() != '' and self.wrapper_mounting_point.get() != '' and self.wrapper_volume_name.get()!= '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormDelinkVolumeFromTemplate(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormDelinkVolumeFromTemplate" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Configuration - Delink volume in a cluster template'

        # create the wrappers to track changes in inputs
        self.wrapper_template_name = tkinter.StringVar()
        self.wrapper_template_name.trace('w', self.validate_inputs)
        self.wrapper_volume_name = tkinter.StringVar()
        self.wrapper_volume_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormDelinkVolumeFromTemplate".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_template_name" and register it with the grid geometry manager
        self.label_template_name = tkinter.Label(self, text='Template name')
        self.label_template_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_template_name" and register it with the grid geometry manager
        self.combobox_template_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_template_name)
        self.combobox_template_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_volume_name" and register it with the grid geometry manager
        self.label_volume_name = tkinter.Label(self, text='Volume name')
        self.label_volume_name.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_volume_name" and register it with the grid geometry manager
        self.combobox_volume_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_volume_name)
        self.combobox_volume_name.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*20)
        self.label_fit.grid(row=2, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=2, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=2, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_template_name.bind('<<ComboboxSelected>>', self.combobox_template_name_selected_item)
        self.combobox_volume_name.bind('<<ComboboxSelected>>', self.combobox_volume_name_selected_item)

    #---------------

    def combobox_template_name_selected_item(self, event=None):
        '''
        Process the event when a template name item has been selected
        '''

        # load data in "combobox_volume_name"
        self.populate_combobox_volume_name()

    #---------------

    def combobox_volume_name_selected_item(self, event=None):
        '''
        Process the event when a volume name item has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the delink of the volume from the cluster template.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the NGScloud config file
        if OK:
            ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

        # confirm the region and zone update in the NGScloud config file
        if OK:
            message = 'The file {0} is going to be update delinking the volume {1} from the cluster template {2}.\n\nAre you sure to continue?'.format(ngscloud_config_file, self.wrapper_volume_name.get(), self.wrapper_template_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # delink the volume from the cluster template in the NGScloud config file corresponding to the environment
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xconfiguration.delink_volume_from_template.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xconfiguration.delink_volume_from_template, args=(self.wrapper_template_name.get(), self.wrapper_volume_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormDelinkVolumeFromTemplate".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_template_name()

    #---------------

    def populate_combobox_template_name(self):
        '''
        Populate data in "combobox_template_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_template_name.set('')

        # get the template names list
        template_name_list = xconfiguration.get_template_name_list(volume_creator_included=False)
        template_name_list.sort()

        # add item 'all' to template name list
        template_name_list = ['all'] + template_name_list

        # load the template names list in the combobox
        self.combobox_template_name['values'] = template_name_list

    #---------------

    def populate_combobox_volume_name(self):
        '''
        Populate data in "combobox_volume_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_volume_name.set('')

        # get current zone name
        zone_name = xconfiguration.get_current_zone_name()

        # verify if there are any linked volumes
        if xec2.get_created_volume_name_list(zone_name) == []:
            message = 'There is not any volume created in the zone {0}.'.format(zone_name)
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the volume names list in the combobox
        if self.wrapper_template_name.get() == 'all':
            self.combobox_volume_name['values'] = xconfiguration.get_volume_names_list()
        else:
            self.combobox_volume_name['values'] = xconfiguration.get_linked_volumes_list(self.wrapper_template_name.get())

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormDelinkVolumeFromTemplate" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_template_name.get() != '' and self.wrapper_volume_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormCreateCluster(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormCreateCluster" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Cluster operation - Create cluster'

        # get the cluster template dictionary and the template names list
        self.template_dict = xconfiguration.get_template_dict()
        self.template_name_list = xconfiguration.get_template_name_list(volume_creator_included=False)

        # create the wrappers to track changes in inputs
        self.wrapper_template_name = tkinter.StringVar()
        self.wrapper_template_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

        # show warnings about characteristics and pricing
        message = 'You can consult the characteristics of the EC2 intance types in:\n\n'
        message += 'https://aws.amazon.com/ec2/instance-types/\n\n'
        message += 'and the EC2 pricing is detailed in:\n\n'
        message += 'https://aws.amazon.com/ec2/pricing/'
        tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormCreateCluster".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_template_name" and register it with the grid geometry manager
        self.label_template_name = tkinter.Label(self, text='Template name')
        self.label_template_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_template_name" and register it with the grid geometry manager
        self.combobox_template_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_template_name)
        self.combobox_template_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_template_name_warning" and register it with the grid geometry manager
        self.label_template_name_warning = tkinter.Label(self, text='')
        self.label_template_name_warning.grid(row=1, column=1, columnspan=3, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*20)
        self.label_fit.grid(row=2, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=2, column=3, padx=(5,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=2, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_template_name.bind('<<ComboboxSelected>>', self.combobox_template_name_selected_item)

    #---------------

    def combobox_template_name_selected_item(self, event=None):
        '''
        Process the event when a template name item has been selected
        '''

        # show the description template in the template name warning
        self.label_template_name_warning['text'] = self.template_dict[self.wrapper_template_name.get()]['description']

    #---------------

    def execute(self, event=None):
        '''
        Execute the cluster creation process.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the creation of the cluster
        if OK:
            message = 'The cluster with template name {0} is going to be created.\n\nAre you sure to continue?\n\n'.format(self.wrapper_template_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # create the cluster
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xcluster.create_cluster.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xcluster.create_cluster, args=(self.wrapper_template_name.get(), self.wrapper_template_name.get(), dialog_log, lambda: dialog_log.enable_button_close(), True)).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormCreateCluster".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_template_name()

    #---------------

    def populate_combobox_template_name(self):
        '''
        Populate data in "combobox_template_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_template_name.set('')

        # load the template names list in the combobox
        self.combobox_template_name['values'] = self.template_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormCreateCluster" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_template_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormStopCluster(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormStopCluster" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Cluster operation - Stop cluster'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormStopCluster".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*25)
        self.label_fit.grid(row=1, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=1, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=1, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the stop of the cluster.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the stop of the cluster
        if OK:
            message = 'The cluster {0} is going to be stopped, not terminated. Then it must be restarted.\n\nAre you sure to continue?'.format(self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # stop the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xcluster.stop_cluster.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xcluster.stop_cluster, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormStopCluster".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormStopCluster" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRestartCluster(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRestartCluster" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Cluster operation - Restart cluster'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormRestartCluster".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*25)
        self.label_fit.grid(row=1, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=1, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=1, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the restarting of the cluster.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the restarting of the cluster
        if OK:
            message = 'The cluster {0} is going to be restarted.\n\nAre you sure to continue?'.format(self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # restart the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xcluster.restart_cluster.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xcluster.restart_cluster, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRestartCluster".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRestartCluster" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormTerminateCluster(tkinter.Frame):

    #---------------

    def __init__(self, parent, main, force):
        '''
        Execute actions correspending to the creation of a "FormTerminateCluster" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main
        self.force = force

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Cluster operation - {0}'.format('Terminate cluster' if not self.force else 'Force termination of a cluster')

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormTerminateCluster".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name' if not self.force else 'Template name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*20)
        self.label_fit.grid(row=1, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=1, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=1, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the cluster termination process.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the termination of the cluster
        if OK:
            message = 'The cluster {0} is going to be terminated.\n\nAre you sure to continue?'.format(self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # terminate the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xcluster.terminate_cluster.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xcluster.terminate_cluster, args=(self.wrapper_cluster_name.get(), self.force, dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormTerminateCluster".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        if not self.force:
            running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
            if running_cluster_list == []:
                self.combobox_cluster_name['values'] = []
                message = 'There is not any running cluster.'
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                return

        # load the names of clusters which are running in the combobox
        if not self.force:
            self.combobox_cluster_name['values'] = running_cluster_list
        else:
            self.combobox_cluster_name['values'] = xconfiguration.get_template_name_list(volume_creator_included=False)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormTerminateCluster" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormShowClusterComposing(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormShowClusterComposing" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Cluster operation - Show cluster composing'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormShowClusterComposing".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*25)
        self.label_fit.grid(row=1, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=1, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=1, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the show of cluster information of every node: OS, CPU number and memory.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # show the status of batch jobs in the cluster
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xcluster.show_cluster_composing.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xcluster.show_cluster_composing, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormShowClusterComposing".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormShowClusterComposing" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormShowStatusBatchJobs(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormShowStatusBatchJobs" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Cluster operation - Show status of batch jobs'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormShowStatusBatchJobs".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*25)
        self.label_fit.grid(row=1, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=1, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=1, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # verify if the cluster name selected is different to the previous cluster name
        if self.wrapper_cluster_name.get() != self.cluster_name_ant:

            # close SSH client connection
            if self.cluster_name_ant is not None:
                xssh.close_ssh_client_connection(self.ssh_client)

            # create the SSH client connection
            (OK, error_list, self.ssh_client) = xssh.create_ssh_client_connection(self.wrapper_cluster_name.get(), 'master')
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                self.close()

            # save current cluster name as previous cluster name
            self.cluster_name_ant = self.wrapper_cluster_name.get()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def execute(self, event=None):
        '''
        Execute the show of the status of batch jobs in the cluster.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the batch job dictionary
        if OK:
            (OK, error_list, batch_job_dict) = xcluster.get_batch_job_dict(self.ssh_client)

        # verify if there are any batch jobs
        if OK:
            if batch_job_dict == {}:
                message = 'There is not any batch job.'
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # build the data list
        if OK:
            data_list = ['job_id', 'job_name', 'state', 'start_date', 'start_time']

        # build the data dictionary
        if OK:
            data_dict = {}
            data_dict['job_id'] = {'text': 'Job id', 'width': 50, 'aligment': 'right'}
            data_dict['job_name'] = {'text': 'Job name', 'width': 100, 'aligment': 'left'}
            data_dict['state'] = {'text': 'State', 'width': 150, 'aligment': 'left'}
            data_dict['start_date'] = {'text': 'Start date', 'width': 100, 'aligment': 'right'}
            data_dict['start_time'] = {'text': 'Start time', 'width': 100, 'aligment': 'right'}

        # create the dialog Table to show the nodes running
        if OK:
            dialog_table = gdialogs.DialogTable(self, self.head, 400, 900, data_list, data_dict, batch_job_dict)
            self.wait_window(dialog_table)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormShowStatusBatchJobs".
        '''

        # close SSH client connection
        if self.cluster_name_ant is not None:
            xssh.close_ssh_client_connection(self.ssh_client)

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormShowStatusBatchJobs" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormKillBatchJob(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormKillBatchJob" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Cluster operation - Kill batch job'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_job = tkinter.StringVar()
        self.wrapper_job.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormKillBatchJob".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_job" and register it with the grid geometry manager
        self.label_job = tkinter.Label(self, text='Job')
        self.label_job.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_job" and register it with the grid geometry manager
        self.combobox_job = tkinter.ttk.Combobox(self, width=50, height=4, state='readonly', textvariable=self.wrapper_job)
        self.combobox_job.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=2, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=2, column=3, padx=(5,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=2, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_job.bind('<<ComboboxSelected>>', self.combobox_job_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # verify if the cluster name selected is different to the previous cluster name
        if self.wrapper_cluster_name.get() != self.cluster_name_ant:

            # close SSH client connection
            if self.cluster_name_ant is not None:
                xssh.close_ssh_client_connection(self.ssh_client)

            # create the SSH client connection
            (OK, error_list, self.ssh_client) = xssh.create_ssh_client_connection(self.wrapper_cluster_name.get(), 'master')
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                self.close()

            # save current cluster name as previous cluster name
            self.cluster_name_ant = self.wrapper_cluster_name.get()

        # load data in "combobox_job"
        self.populate_combobox_job()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_job_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_job" has been selected
        '''

        try:
            self.job_id = int(self.wrapper_job.get()[0:3])
        except:
            self.job_id = 0

    #---------------

    def execute(self, event=None):
        '''
        Execute the removal of a node in a cluster.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the removal of the volume in the node
        if OK:
            message = 'The batch job {0} is going to be killed in the cluster {1}.\n\nAre you sure to continue?'.format(self.wrapper_job.get(), self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # remove the volume and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xcluster.kill_batch_job.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xcluster.kill_batch_job, args=(self.wrapper_cluster_name.get(), self.job_id, dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormKillBatchJob".
        '''

        # close SSH client connection
        if self.cluster_name_ant is not None:
            xssh.close_ssh_client_connection(self.ssh_client)

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()
        self.combobox_job['values'] = []
        self.wrapper_job.set('')

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox_cluster_name
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_job(self):
        '''
        Populate data in "combobox_job".
        '''

        # clear the value selected in the combobox
        self.wrapper_job.set('')

        # get the batch job dictionary
        (OK, error_list, batch_job_dict) = xcluster.get_batch_job_dict(self.ssh_client)
        if batch_job_dict == {}:
            message = 'There is not any batch job.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # build the list of batch jobs
        batch_job_id_list = []
        for job_id in batch_job_dict.keys():
            job_name = batch_job_dict[job_id]['job_name']
            state_name = batch_job_dict[job_id]['state_name']
            start_date = batch_job_dict[job_id]['start_date']
            start_time = batch_job_dict[job_id]['start_time']
            batch_job_id_list.append('{0:>3} ({1}; started at: {2} {3}; state: {4})'.format(job_id, job_name, start_date, start_time, state_name))
        batch_job_id_list.sort()

        # load the names of cluster nodes created in the combobox
        self.combobox_job['values'] = batch_job_id_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormKillBatchJob" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_job.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormAddNode(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormAddNode" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Node operation - Add node in a cluster'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_node_name = tkinter.StringVar()
        self.wrapper_node_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # initialize the cluster node list
        self.cluster_node_list = []

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormAddNode".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_node_name" and register it with the grid geometry manager
        self.label_node_name = tkinter.Label(self, text='Node name')
        self.label_node_name.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_node_name" and register it with the grid geometry manager
        self.entry_node_name = tkinter.Entry(self, textvariable=self.wrapper_node_name, width=40, validatecommand=self.validate_inputs)
        self.entry_node_name.grid(row=1, column=1, padx=(5,5), pady=(60,5), sticky='w')

        # create "label_node_name_warning" and register it with the grid geometry manager
        self.label_node_name_warning = tkinter.Label(self, text='')
        self.label_node_name_warning.grid(row=2, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*25)
        self.label_fit.grid(row=3, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=3, column=3, padx=(5,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=3, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        # get the cluster node list
        self.cluster_node_list = xec2.get_cluster_node_list(self.wrapper_cluster_name.get())

    #---------------

    def execute(self, event=None):
        '''
        Execute the detetion moval of a node in a cluster.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the addition of the volume in the node
        if OK:
            message = 'The node {0} is going to be added in the cluster {1}.\n\nAre you sure to continue?'.format(self.wrapper_node_name.get(), self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # add the node
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xnode.add_node.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xnode.add_node, args=(self.wrapper_cluster_name.get(), self.wrapper_node_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormAddNode".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()
        self.wrapper_node_name.set('')

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox_node_name
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormAddNode" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "combobox_cluster_name"
        if not self.validate_combobox_cluster_name():
            OK = False

        # validate the content of "entry_node_name"
        if not self.validate_entry_node_name():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_node_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_combobox_cluster_name(self):
        '''
        Validate the content of "combobox_cluster_name"
        '''

        # initialize the control variable
        OK = True

        # verify if the maximum number of instances is already running
        if len(self.cluster_node_list) >= xec2.get_max_node_number():
            message = 'The maximum number ({0}) of instances is already running.'.format(xec2.get_max_node_number())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            OK = False

        # return the control variable
        return OK

    #---------------

    def validate_entry_node_name(self):
        '''
        Validate the content of "entry_node_name"
        '''

        # initialize the control variable
        OK = True

        # verify if the node name is valid
        if self.wrapper_node_name.get() == 'master':
            self.label_node_name_warning['text'] = 'The name master cannot be used.'
            self.label_node_name_warning['foreground'] = 'red'
            OK = False
        elif self.wrapper_node_name.get() != '' and not self.wrapper_node_name.get().isalnum():
            self.label_node_name_warning['text'] = 'It is not an alphanumeric string'.format(self.wrapper_node_name.get())
            self.label_node_name_warning['foreground'] = 'red'
            OK = False
        elif self.wrapper_node_name.get() != '' and not self.wrapper_node_name.get()[0].isalpha():
            self.label_node_name_warning['text'] = 'The first character is not alphabetic'.format(self.wrapper_node_name.get())
            self.label_node_name_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_node_name_warning['text'] = ''
            self.label_node_name_warning['foreground'] = 'black'

        # verify if the a node with the node name is instances is already running
        if OK:
            if self.wrapper_node_name.get() in self.cluster_node_list:
                message = 'The {0} is already running.'.format(self.wrapper_node_name.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRemoveNode(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRemoveNode" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Node operation - Remove node in a cluster'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_node_name = tkinter.StringVar()
        self.wrapper_node_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormRemoveNode".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_node_name" and register it with the grid geometry manager
        self.label_node_name = tkinter.Label(self, text='Node name')
        self.label_node_name.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_node_name" and register it with the grid geometry manager
        self.combobox_node_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_node_name)
        self.combobox_node_name.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=3, column=2, padx=(0,0), pady=(55,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=3, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=3, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_node_name.bind('<<ComboboxSelected>>', self.combobox_node_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_node_name"
        self.populate_combobox_node_name()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_node_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the removal of a node in a cluster.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the removal of the volume in the node
        if OK:
            message = 'The node {0} is going to be removed in the cluster {1}.\n\nAre you sure to continue?'.format(self.wrapper_node_name.get(), self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # remove the volume and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xnode.remove_node.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xnode.remove_node, args=(self.wrapper_cluster_name.get(), self.wrapper_node_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRemoveNode".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()
        self.combobox_node_name['values'] = []
        self.wrapper_node_name.set('')

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox_cluster_name
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_node_name(self):
        '''
        Populate data in "combobox_node_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_node_name.set('')

        # get cluster node list
        cluster_node_list = xec2.get_cluster_node_list(self.wrapper_cluster_name.get())

        # remove master in cluster node list
        cluster_node_list.remove('master')

        # verify if there are some nodes besides master
        if cluster_node_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running node besides the master.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of cluster nodes created in the combobox
        self.combobox_node_name['values'] = cluster_node_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRemoveNode" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_node_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormCreateVolume(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormCreateVolume" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Volume operation - Create volume'

        # get the volume type dictinary
        self.volume_type_dict = xec2.get_volume_type_dict()

        # create the wrappers to track changes in inputs
        self.wrapper_volume_name = tkinter.StringVar()
        self.wrapper_volume_name.trace('w', self.validate_inputs)
        self.wrapper_volume_type_text = tkinter.StringVar()
        self.wrapper_volume_type_text.trace('w', self.validate_inputs)
        self.wrapper_volume_size = tkinter.StringVar()
        self.wrapper_volume_size.trace('w', self.validate_inputs)
        self.wrapper_terminate_indicator = tkinter.IntVar()
        self.wrapper_terminate_indicator.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

        # show warnings about characteristics and pricing
        message = 'You can consult the characteristics of the EBS volumes in:\n\n'
        message += 'https://aws.amazon.com/ebs/details/\n\n'
        message += 'and the EBS pricing is detailed in:\n\n'
        message += '    https://aws.amazon.com/ebs/pricing/'
        tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormCreateVolume".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_volume_name" and register it with the grid geometry manager
        self.label_volume_name = tkinter.Label(self, text='Volume name')
        self.label_volume_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "entry_volume_name" and register it with the grid geometry manager
        self.entry_volume_name = tkinter.Entry(self, textvariable=self.wrapper_volume_name, width=40, validatecommand=self.validate_inputs)
        self.entry_volume_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_volume_type_text" and register it with the grid geometry manager
        self.label_volume_type_text = tkinter.Label(self, text='Volume type')
        self.label_volume_type_text.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_volume_type_text" and register it with the grid geometry manager
        self.combobox_volume_type_text = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_volume_type_text)
        self.combobox_volume_type_text.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_volume_size" and register it with the grid geometry manager
        self.label_volume_size = tkinter.Label(self, text='Volume size (in GiB)')
        self.label_volume_size.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_volume_size" and register it with the grid geometry manager
        self.entry_volume_size = tkinter.Entry(self, textvariable=self.wrapper_volume_size, width=10, validatecommand=self.validate_inputs)
        self.entry_volume_size.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_volume_size_warning" and register it with the grid geometry manager
        self.label_volume_size_warning = tkinter.Label(self, text='')
        self.label_volume_size_warning.grid(row=3, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "checkbutton_terminate_indicator" and register it with the grid geometry manager
        self.checkbutton_terminate_indicator = tkinter.ttk.Checkbutton(self, text='Terminate volume creator?', variable=self.wrapper_terminate_indicator)
        self.checkbutton_terminate_indicator.grid(row=4, column=1, columnspan=2, padx=(5,5), pady=(25,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*15)
        self.label_fit.grid(row=5, column=2, padx=(0,0), pady=(55,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=5, column=3, padx=(0,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=5, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_volume_type_text.bind('<<ComboboxSelected>>', self.combobox_volume_type_text_selected_item)

    #---------------

    def combobox_volume_type_text_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_volume_type_text" has been selected
        '''

        # get the volume type identification
        self.volume_type_id = xec2.get_volume_type_id(self.wrapper_volume_type_text.get())

        # get the minimum and maximun size of the volume type
        self.minimum_size = self.volume_type_dict[self.volume_type_id]['minimum_size']
        self.maximum_size = self.volume_type_dict[self.volume_type_id]['maximum_size']

        # set the minimum value in volume size "entry_volume_size"
        self.wrapper_volume_size.set(self.minimum_size)

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the volume in the currrent zone.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the creation of the cluster
        if OK:
            message = 'The volume {0} is going to be created.\n\nAre you sure to continue?'.format(self.wrapper_volume_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # create the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xvolume.create_volume.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xvolume.create_volume, args=(self.wrapper_volume_name.get(), self.volume_type_id, int(self.wrapper_volume_size.get()), self.wrapper_terminate_indicator.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormCreateVolume".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.wrapper_volume_name.set('')
        self.populate_combobox_volume_type_text()
        self.wrapper_volume_type_text.set('standard HDD')
        self.volume_type_id = xec2.get_volume_type_id(self.wrapper_volume_type_text.get())
        self.minimum_size = self.volume_type_dict[self.volume_type_id]['minimum_size']
        self.maximum_size = self.volume_type_dict[self.volume_type_id]['maximum_size']
        self.wrapper_volume_size.set(self.minimum_size)
        self.wrapper_volume_size.set(1)
        self.wrapper_terminate_indicator.set(1)

    #---------------

    def populate_combobox_volume_type_text(self):
        '''
        Populate data in "combobox_volume_type_text".
        '''

        # clear the value selected in the combobox
        self.wrapper_volume_type_text.set('')

        # load the volume types in the combobox
        self.combobox_volume_type_text['values'] = xec2.get_volume_type_text_list()

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormCreateVolume" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_volume_size"
        if not self.validate_entry_volume_size():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_volume_name.get() != '' and self.wrapper_volume_type_text.get() != '' and self.wrapper_volume_size.get() != '' and self.wrapper_terminate_indicator.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_volume_size(self):
        '''
        Validate the content of "entry_volume_size"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_volume_size" an integer value and it is  greater or equal than the minimum value size
        try:
            volume_size = int(self.wrapper_volume_size.get())
        except:
            self.label_volume_size_warning['text'] = 'It is not an integer number.'
            self.label_volume_size_warning['foreground'] = 'red'
            OK = False
        else:
            if volume_size < self.minimum_size or volume_size > self.maximum_size:
                self.label_volume_size_warning['text'] = 'It must be between {0} and {1}'.format(self.minimum_size, self.maximum_size)
                self.label_volume_size_warning['foreground'] = 'red'
                OK = False
            else:
                self.label_volume_size_warning['text'] = 'It must be between {0} and {1}'.format(self.minimum_size, self.maximum_size)
                self.label_volume_size_warning['foreground'] = 'black'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormRemoveVolume(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRemoveVolume" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Volume operation - Remove volume'

        # create the wrappers to track changes in the inputs
        self.wrapper_volume_name = tkinter.StringVar()
        self.wrapper_volume_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormRemoveVolume".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_volume_name" and register it with the grid geometry manager
        self.label_volume_name = tkinter.Label(self, text='Volume name')
        self.label_volume_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_volume_name" and register it with the grid geometry manager
        self.combobox_volume_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_volume_name)
        self.combobox_volume_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*25)
        self.label_fit.grid(row=1, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=1, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=1, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_volume_name.bind('<<ComboboxSelected>>', self.combobox_volume_name_selected_item)

    #---------------

    def combobox_volume_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the read file transfer process.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the removal of the volume
        if OK:
            message = 'The volume {0} is going to be removed.\n\nAre you sure to continue?'.format(self.wrapper_volume_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # remove the volume and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xvolume.remove_volume.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xvolume.remove_volume, args=(self.wrapper_volume_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRemoveVolume".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_volume_name()

    #---------------

    def populate_combobox_volume_name(self):
        '''
        Populate data in "combobox_volume_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_volume_name.set('')

        # get the current zone name
        zone_name = xconfiguration.get_current_zone_name()

        # get the volume name list
        volume_names_list = xec2.get_created_volume_name_list(zone_name)

        # verify if there are any volumes created
        if volume_names_list == []:
            self.combobox_volume_name['values'] = []
            message = 'There is not any volume created.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_volume_name['values'] = volume_names_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRemoveVolume" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_volume_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormMountVolume(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormMountVolume" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Volume operation - Mount volume in a node'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_node_name = tkinter.StringVar()
        self.wrapper_node_name.trace('w', self.validate_inputs)
        self.wrapper_volume_name = tkinter.StringVar()
        self.wrapper_volume_name.trace('w', self.validate_inputs)
        self.wrapper_aws_device_file = tkinter.StringVar()
        self.wrapper_aws_device_file.trace('w', self.validate_inputs)
        self.wrapper_mounting_path = tkinter.StringVar()
        self.wrapper_mounting_path.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormMountVolume".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(65,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(65,5), sticky='w')

        # create "label_node_name" and register it with the grid geometry manager
        self.label_node_name = tkinter.Label(self, text='Node name')
        self.label_node_name.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_node_name" and register it with the grid geometry manager
        self.combobox_node_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_node_name)
        self.combobox_node_name.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_volume_name" and register it with the grid geometry manager
        self.label_volume_name = tkinter.Label(self, text='Volume name')
        self.label_volume_name.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_volume_name" and register it with the grid geometry manager
        self.combobox_volume_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_volume_name)
        self.combobox_volume_name.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_aws_device_file" and register it with the grid geometry manager
        self.label_aws_device_file = tkinter.Label(self, text='Device file')
        self.label_aws_device_file.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_aws_device_file" and register it with the grid geometry manager
        self.entry_aws_device_file = tkinter.Entry(self, textvariable=self.wrapper_aws_device_file, width=40, validatecommand=self.validate_inputs)
        self.entry_aws_device_file.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_aws_device_file_warning" and register it with the grid geometry manager
        self.label_aws_device_file_warning = tkinter.Label(self, text='')
        self.label_aws_device_file_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_mounting_path" and register it with the grid geometry manager
        self.label_mounting_path = tkinter.Label(self, text='Mounting path')
        self.label_mounting_path.grid(row=5, column=0, padx=(15,5), pady=(25,5), sticky='e')

        # create "entry_mounting_path" and register it with the grid geometry manager
        self.entry_mounting_path = tkinter.Entry(self, textvariable=self.wrapper_mounting_path, width=40, validatecommand=self.validate_inputs)
        self.entry_mounting_path.grid(row=5, column=1, padx=(5,5), pady=(25,5), sticky='w')

        # create "label_mounting_path_warning" and register it with the grid geometry manager
        self.label_mounting_path_warning = tkinter.Label(self, text='')
        self.label_mounting_path_warning.grid(row=6, column=1, padx=(5,5), pady=(0,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*20)
        self.label_fit.grid(row=7, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=7, column=3, padx=(5,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=7, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_node_name.bind('<<ComboboxSelected>>', self.combobox_node_name_selected_item)
        self.combobox_volume_name.bind('<<ComboboxSelected>>', self.combobox_volume_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_node_name"
        self.populate_combobox_node_name()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_node_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def combobox_volume_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the mounting of a volume in a node.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the mounting of the volume in the node
        if OK:
            message = 'The volume {0} is going to be mounted in the node {1}.\n\nAre you sure to continue?'.format(self.wrapper_volume_name.get(), self.wrapper_node_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # terminate the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xvolume.mount_volume.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xvolume.mount_volume, args=(self.wrapper_cluster_name.get(), self.wrapper_node_name.get(), self.wrapper_volume_name.get(), self.wrapper_aws_device_file.get(), self.entry_mounting_path.get(), dialog_log, lambda: dialog_log.enable_button_close(), True)).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormMountVolume".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()
        self.combobox_node_name['values'] = []
        self.wrapper_node_name.set('')
        self.populate_combobox_volume_name()
        self.wrapper_aws_device_file.set('/dev/sdf')
        self.wrapper_mounting_path.set('')

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_node_name(self):
        '''
        Populate data in "combobox_node_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_node_name.set('')

        # load the names of cluster nodes created in the combobox
        self.combobox_node_name['values'] = xec2.get_cluster_node_list(self.wrapper_cluster_name.get())

    #---------------

    def populate_combobox_volume_name(self):
        '''
        Populate data in "combobox_volume_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_volume_name.set('')

        # get current zone name
        zone_name = xconfiguration.get_current_zone_name()

        # verify if there are any linked volumes
        if xec2.get_created_volume_name_list(zone_name) == []:
            message = 'There is not any volume created in the zone {0}.'.format(zone_name)
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the volume names list in the combobox
        self.combobox_volume_name['values'] = xec2.get_created_volume_name_list(zone_name)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormMountVolume" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_aws_device_file"
        if not self.validate_entry_aws_device_file():
            OK = False

        # validate the content of "self.entry_mounting_path"
        if not self.validate_entry_mounting_path():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_node_name.get() != '' and self.wrapper_volume_name.get() != '' and self.wrapper_aws_device_file.get() != '' and self.entry_mounting_path.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_aws_device_file(self):
        '''
        Validate the content of "entry_aws_device_file"
        '''

        # initialize the control variable
        OK = True

        # initialize the device file pattern
        device_file_pattern = '/dev/sd[f-o]'

        # verify that "entry_aws_device_file" value is valid
        if not xlib.is_device_file(self.wrapper_aws_device_file.get(), device_file_pattern):
            self.label_aws_device_file_warning['text'] = 'It must have a pattern {0}.'.format(device_file_pattern)
            self.label_aws_device_file_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_aws_device_file_warning['text'] = ''
            self.label_aws_device_file_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

    def validate_entry_mounting_path(self):
        '''
        Validate the content of "entry_mounting_path"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_mounting_path" value is an absolute path
        if not xlib.is_absolute_path(self.entry_mounting_path.get(), 'linux'):
            self.label_mounting_path_warning['text'] = 'It must be a Linux absolute path.'
            self.label_mounting_path_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_mounting_path_warning['text'] = ''
            self.label_mounting_path_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormUnmountVolume(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormUnmountVolume" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Volume operation - Unmount volume in a node'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_node_name = tkinter.StringVar()
        self.wrapper_node_name.trace('w', self.validate_inputs)
        self.wrapper_volume_name = tkinter.StringVar()
        self.wrapper_volume_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormUnmountVolume".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_node_name" and register it with the grid geometry manager
        self.label_node_name = tkinter.Label(self, text='Node name')
        self.label_node_name.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_node_name" and register it with the grid geometry manager
        self.combobox_node_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_node_name)
        self.combobox_node_name.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_volume_name" and register it with the grid geometry manager
        self.label_volume_name = tkinter.Label(self, text='Volume name')
        self.label_volume_name.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_volume_name" and register it with the grid geometry manager
        self.combobox_volume_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_volume_name)
        self.combobox_volume_name.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*25)
        self.label_fit.grid(row=3, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=3, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=3, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_node_name.bind('<<ComboboxSelected>>', self.combobox_node_name_selected_item)
        self.combobox_volume_name.bind('<<ComboboxSelected>>', self.combobox_volume_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_node_name"
        self.populate_combobox_node_name()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_node_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def combobox_volume_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the unmounting of a volume in a node.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the unmounting of the volume in the node
        if OK:
            message = 'The volume {0} is going to be unmounted in the node {1}.\n\nAre you sure to continue?'.format(self.wrapper_volume_name.get(), self.wrapper_node_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # terminate the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xvolume.unmount_volume.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xvolume.unmount_volume, args=(self.wrapper_cluster_name.get(), self.wrapper_node_name.get(), self.wrapper_volume_name.get(), dialog_log, lambda: dialog_log.enable_button_close(), True)).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormUnmountVolume".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()
        self.combobox_node_name['values'] = []
        self.wrapper_node_name.set('')
        self.populate_combobox_volume_name()

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_node_name(self):
        '''
        Populate data in "combobox_node_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_node_name.set('')

        # load the names of cluster nodes created in the combobox
        self.combobox_node_name['values'] = xec2.get_cluster_node_list(self.wrapper_cluster_name.get())

    #---------------

    def populate_combobox_volume_name(self):
        '''
        Populate data in "combobox_volume_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_volume_name.set('')

        # get current zone name
        zone_name = xconfiguration.get_current_zone_name()

        # verify if there are any volumes linked
        if xec2.get_created_volume_name_list(zone_name) == []:
            message = 'There is not any volume created in the zone {0}.'.format(zone_name)
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the volume names list in the combobox
        self.combobox_volume_name['values'] = xec2.get_created_volume_name_list(zone_name)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormUnmountVolume" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_node_name.get() != '' and self.wrapper_volume_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormOpenTerminal(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormOpenTerminal" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = 'Cluster opeation - Open a terminal'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_node_name = tkinter.StringVar()
        self.wrapper_node_name.trace('w', self.validate_inputs)

        # build the graphical user interface
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormOpenTerminal".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_node_name" and register it with the grid geometry manager
        self.label_node_name = tkinter.Label(self, text='Node name')
        self.label_node_name.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_node_name" and register it with the grid geometry manager
        self.combobox_node_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_node_name)
        self.combobox_node_name.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*25)
        self.label_fit.grid(row=3, column=2, padx=(0,0), pady=(55,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=3, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=3, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_node_name.bind('<<ComboboxSelected>>', self.combobox_node_name_selected_item)

    #---------------

    def combobox_cluster_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_node_name"
        self.populate_combobox_node_name()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_node_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_cluster_name" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the opening of window of a node cluster.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the opening of a windows terminal of a node cluster
        if OK:
            message = 'A terminal window of the node {0} in the cluster {1} is going to be opened.\n\nAre you sure to continue?'.format(self.wrapper_node_name.get(), self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # open the terminal windows
        if OK:
            xcluster.open_terminal(self.wrapper_cluster_name.get(), self.wrapper_node_name.get())

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormOpenTerminal".
        '''

        # clear the label of the current process name
        self.main.label_process['text'] = ''

        # close the current form
        self.main.close_current_form()

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load initial data in inputs
        self.populate_combobox_cluster_name()
        self.combobox_node_name['values'] = []
        self.wrapper_node_name.set('')

    #---------------

    def populate_combobox_cluster_name(self):
        '''
        Populate data in "combobox_cluster_name".
        '''

        # clear the value selected in the combobox_node_name
        self.wrapper_cluster_name.set('')

        # verify if there are some running clusters
        running_cluster_list = xec2.get_running_cluster_list(volume_creator_included=False)
        if running_cluster_list == []:
            self.combobox_cluster_name['values'] = []
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_node_name(self):
        '''
        Populate data in "combobox_node_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_node_name.set('')

        # load the names of cluster nodes created in the combobox
        self.combobox_node_name['values'] = xec2.get_cluster_node_list(self.wrapper_cluster_name.get())

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormOpenTerminal" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_node_name.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('This file contains the classes related to forms corresponding to Cloud Control menu items in gui mode.')
    sys.exit(0)

#-------------------------------------------------------------------------------
