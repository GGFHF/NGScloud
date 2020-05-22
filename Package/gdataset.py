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
This file contains the classes related to datasets forms in gui mode.
'''

#-------------------------------------------------------------------------------

import os
import PIL.Image
import PIL.ImageTk
import re
import sys
import threading
import tkinter
import tkinter.ttk

import gdialogs
import xdatabase
import xec2
import xgzip
import xlib
import xread
import xreference
import xresult
import xssh

#-------------------------------------------------------------------------------

class FormListDataset(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormListDataset" instance.
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
        self.head = 'Datasets - List dataset'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_volume = tkinter.StringVar()
        self.wrapper_volume.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormListDataset".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_volume" and register it with the grid geometry manager
        self.label_volume = tkinter.Label(self, text='Volume')
        self.label_volume.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_volume" and register it with the grid geometry manager
        self.combobox_volume = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_volume)
        self.combobox_volume.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

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
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_volume.bind('<<ComboboxSelected>>', self.combobox_volume_selected_item)

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

        # load data in "combobox_volume"
        self.populate_combobox_volume()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_volume_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_volume" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the list the processes of an experiment.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the directory dictionary of directories in the volume
        if OK:
            command = 'ls -la /{0}'.format(self.wrapper_volume.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                directory_dict = {}
                for line in stdout:
                    line = line.rstrip('\n')
                    if line.startswith('d') or line.startswith('-'):
                        directory_data_list = line.split()
                        file_type = 'directory' if directory_data_list[0][0] == 'd' else 'file'
                        permissions = directory_data_list[0][1:]
                        links_number = directory_data_list[1]
                        owner_name = directory_data_list[2]
                        owner_group = directory_data_list[3]
                        file_size = directory_data_list[4]
                        modification_month = directory_data_list[5]
                        modification_day = directory_data_list[6]
                        modification_time = directory_data_list[7]
                        file_name = directory_data_list[8]
                        if file_name not in ['.', '..', 'lost+found']:
                            key = '{0}-{1}'.format(file_type, file_name)
                            directory_dict[key] = {'file_type': file_type, 'permissions': permissions, 'links_number': links_number, 'owner_name': owner_name, 'owner_group': owner_group, 'file_size': file_size, 'modification_month': modification_month, 'modification_day': modification_day, 'modification_time': modification_time, 'file_name': file_name}

        # verify if there are any nodes running
        if OK:
            if directory_dict == {}:
                message = 'There is not any file.'
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the data list
        if OK:
            data_list = ['file_type', 'file_name']

        # build the data dictionary
        if OK:
            data_dict = {}
            data_dict['file_type']= {'text': 'Type', 'width': 120, 'aligment': 'left'}
            data_dict['file_name'] = {'text': 'Name', 'width': 400, 'aligment': 'left'}

        # create the dialog Table to show the nodes running
        if OK:
            dialog_table = gdialogs.DialogTable(self, 'Directory /{0}'.format(self.wrapper_volume.get()), 400, 600, data_list, data_dict, directory_dict, 'list_directory', ['/{0}'.format(self.wrapper_volume.get()), self.ssh_client])
            self.wait_window(dialog_table)

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormListDataset".
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
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_volume(self):
        '''
        Populate data in "combobox_volume".
        '''

        # clear the value selected in the combobox
        self.wrapper_volume.set('')

        # initialize the experiment identification list
        volume_list = []

        # get the experiment identifications
        command = 'ls /'
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line in ['references', 'databases', 'reads', 'results']:
                    volume_list.append(line)

        # verify if there are any experimment identifications
        if volume_list == []:
            message = 'The cluster has not any volume attached.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_volume['values'] = volume_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormListDataset" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_volume.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormRecreateReferenceTransferConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateReferenceTransferConfigFile" instance.
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
        self.head = 'Reference dataset file transfer - Recreate config file'

        # create the wrappers to track changes in inputs
        self.wrapper_local_dir = tkinter.StringVar()
        self.wrapper_local_dir.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_reference_dataset = tkinter.StringVar()
        self.wrapper_reference_dataset.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateReferenceTransferConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "image_open_folder"
        image_open_folder = PIL.Image.open('./image_open_folder.png')
        imagetk_open_folder = PIL.ImageTk.PhotoImage(image_open_folder)  

        # create "label_local_dir" and register it with the grid geometry manager
        self.label_local_dir = tkinter.Label(self, text='Local directory')
        self.label_local_dir.grid(row=0, column=0, padx=(5,5), pady=(75,5), sticky='e')

        # create "entry_local_dir" and register it with the grid geometry manager
        self.entry_local_dir = tkinter.Entry(self, textvariable=self.wrapper_local_dir, width=48, validatecommand=self.validate_inputs)
        self.entry_local_dir.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "button_select_dir" and register it with the grid geometry manager
        self.button_select_dir = tkinter.ttk.Button(self, image=imagetk_open_folder, command=self.select_dir)
        self.button_select_dir.image = imagetk_open_folder
        self.button_select_dir.grid(row=0, column=2, padx=(5,0), pady=(75,5), sticky='w')

        # create "label_local_dir_warning" and register it with the grid geometry manager
        self.label_local_dir_warning = tkinter.Label(self, text='')
        self.label_local_dir_warning.grid(row=1, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=2, column=0, padx=(5,5), pady=(25,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=20, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=2, column=1, padx=(5,5), pady=(25,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=3, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_reference_dataset" and register it with the grid geometry manager
        self.label_reference_dataset = tkinter.Label(self, text='Reference dataset')
        self.label_reference_dataset.grid(row=4, column=0, padx=(5,5), pady=(25,5), sticky='e')

        # create "entry_reference_dataset" and register it with the grid geometry manager
        self.entry_reference_dataset = tkinter.Entry(self, textvariable=self.wrapper_reference_dataset, width=48, validatecommand=self.validate_inputs)
        self.entry_reference_dataset.grid(row=4, column=1, padx=(5,5), pady=(25,5), sticky='w')

        # create "label_reference_dataset_warning" and register it with the grid geometry manager
        self.label_reference_dataset_warning = tkinter.Label(self, text='')
        self.label_reference_dataset_warning.grid(row=5, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*1)
        self.label_fit.grid(row=6, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=6, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=6, column=4, padx=(5,5), pady=(25,5), sticky='w')

    #---------------

    def select_dir(self, event=None):
        '''
        Select a directory and assign it to "entry_local_dir".
        '''

        # select the directory
        directory = tkinter.filedialog.askdirectory(parent=self, initialdir=".", title='Please select a directory')

        # assign the directory to "entry_local_dir"
        if directory != '':
            self.wrapper_local_dir.set(directory)

    #---------------

    def execute(self, event=None):
        '''
        Execute the recreation of the reference transfer config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the seleted files list
        if OK:
            selected_file_list = []
            for file in os.listdir(self.wrapper_local_dir.get()):
                if os.path.isfile(os.path.join(self.wrapper_local_dir.get(), file)) and re.match(self.wrapper_file_pattern.get(), file):
                    selected_file_list.append(file)
            if selected_file_list == []:
                message = '*** ERROR: There are not files in the directory {0} with the pattern {1}'.format(self.wrapper_local_dir.get(), self.wrapper_file_pattern.get())
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # confirm the creation of the reference transfer config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xreference.get_reference_transfer_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the reference transfer config file corresponding to the environment
        if OK:
            (OK, error_list) = xreference.create_reference_transfer_config_file(os.path.normpath(self.wrapper_local_dir.get()), selected_file_list, self.wrapper_reference_dataset.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the reference transfer config file corresponding to the environment
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xreference.get_reference_transfer_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xreference.validate_reference_transfer_config_file(strict=False)
            if OK:
                message = 'The reference dataset transfer config file is OK.'
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = 'Validate result:\n\n'
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateReferenceTransferConfigFile".
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
        self.wrapper_local_dir.set('')
        self.wrapper_file_pattern.set('.*')
        self.wrapper_reference_dataset.set('')

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateReferenceTransferConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_local_dir"
        if not self.validate_entry_local_dir():
            OK = False

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # validate the content of "entry_cluster_dir"
        if not self.validate_entry_cluster_dir():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_local_dir.get() != '' and self.wrapper_file_pattern.get() and  self.wrapper_reference_dataset.get():
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_local_dir(self):
        '''
        Validate the content of "entry_local_dir"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_local_dir" value is a directory
        if not xlib.existing_dir(self.wrapper_local_dir.get()):
            self.label_local_dir_warning['text'] = 'It must be a existing directory path.'
            self.label_local_dir_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_local_dir_warning['text'] = ''
            self.label_local_dir_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

    def validate_entry_file_pattern(self):
        '''
        Validate the content of "entry_file_pattern"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_file_pattern" value is a valid pattern of regular expression
        try:
            re.compile(self.wrapper_file_pattern.get())
        except:
            self.label_file_pattern_warning['text'] = 'It is not a valid pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'It is a pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

    def validate_entry_cluster_dir(self):
        '''
        Validate the content of "entry_cluster_dir"
        '''

        # initialize the control variable
        OK = True

        # get the cluster reference directory
        cluster_reference_dir = xlib.get_cluster_reference_dir()

        # verify that "entry_cluster_dir" value is a valid directory path
        if not xlib.is_relative_path(self.wrapper_reference_dataset.get()):
            self.label_reference_dataset_warning['text'] = 'It is not a valid relative.'
            self.label_reference_dataset_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_reference_dataset_warning['text'] = 'It is or will be a subdirectory of {0}.'.format(cluster_reference_dir)
            self.label_reference_dataset_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormUploadReferenceDataSet(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormUploadReferenceDataSet" instance.
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
        self.head = 'Reference dataset file transfer - Upload dataset to a cluster'

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
        Build the graphical user interface of "FormUploadReferenceDataSet".
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
        Execute the reference file transfer process.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the upload of the read files to the cluster
        if OK:
            message = 'The reference files are going to be uploaded to {0}.\n\nAre you sure to continue?\n\nCAUTION: before a transfer process, the config file should be updated.'.format(self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # upload the read files to the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xreference.upload_reference_dataset.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xreference.upload_reference_dataset, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormUploadReferenceDataSet".
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
        Validate the content of each input of "FormUploadReferenceDataSet" and do the actions linked to its value
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

class FormRecreateDatabaseTransferConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateDatabaseTransferConfigFile" instance.
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
        self.head = 'Database file transfer - Recreate config file'

        # create the wrappers to track changes in inputs
        self.wrapper_local_dir = tkinter.StringVar()
        self.wrapper_local_dir.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_database_dataset = tkinter.StringVar()
        self.wrapper_database_dataset.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateDatabaseTransferConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "image_open_folder"
        image_open_folder = PIL.Image.open('./image_open_folder.png')
        imagetk_open_folder = PIL.ImageTk.PhotoImage(image_open_folder)  

        # create "label_local_dir" and register it with the grid geometry manager
        self.label_local_dir = tkinter.Label(self, text='Local directory')
        self.label_local_dir.grid(row=0, column=0, padx=(5,5), pady=(75,5), sticky='e')

        # create "entry_local_dir" and register it with the grid geometry manager
        self.entry_local_dir = tkinter.Entry(self, textvariable=self.wrapper_local_dir, width=48, validatecommand=self.validate_inputs)
        self.entry_local_dir.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "button_select_dir" and register it with the grid geometry manager
        self.button_select_dir = tkinter.ttk.Button(self, image=imagetk_open_folder, command=self.select_dir)
        self.button_select_dir.image = imagetk_open_folder
        self.button_select_dir.grid(row=0, column=2, padx=(5,0), pady=(75,5), sticky='w')

        # create "label_local_dir_warning" and register it with the grid geometry manager
        self.label_local_dir_warning = tkinter.Label(self, text='')
        self.label_local_dir_warning.grid(row=1, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=2, column=0, padx=(5,5), pady=(25,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=20, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=2, column=1, padx=(5,5), pady=(25,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=3, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_database_dataset" and register it with the grid geometry manager
        self.label_database_dataset = tkinter.Label(self, text='Database')
        self.label_database_dataset.grid(row=4, column=0, padx=(5,5), pady=(25,5), sticky='e')

        # create "entry_database_dataset" and register it with the grid geometry manager
        self.entry_database_dataset = tkinter.Entry(self, textvariable=self.wrapper_database_dataset, width=48, validatecommand=self.validate_inputs)
        self.entry_database_dataset.grid(row=4, column=1, padx=(5,5), pady=(25,5), sticky='w')

        # create "label_database_dataset_warning" and register it with the grid geometry manager
        self.label_database_dataset_warning = tkinter.Label(self, text='')
        self.label_database_dataset_warning.grid(row=5, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*1)
        self.label_fit.grid(row=6, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=6, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=6, column=4, padx=(5,5), pady=(25,5), sticky='w')

    #---------------

    def select_dir(self, event=None):
        '''
        Select a directory and assign it to "entry_local_dir".
        '''

        # select the directory
        directory = tkinter.filedialog.askdirectory(parent=self, initialdir=".", title='Please select a directory')

        # assign the directory to "entry_local_dir"
        if directory != '':
            self.wrapper_local_dir.set(directory)

    #---------------

    def execute(self, event=None):
        '''
        Execute the recreation of the database transfer config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the seleted files list
        if OK:
            selected_file_list = []
            for file in os.listdir(self.wrapper_local_dir.get()):
                if os.path.isfile(os.path.join(self.wrapper_local_dir.get(), file)) and re.match(self.wrapper_file_pattern.get(), file):
                    selected_file_list.append(file)
            if selected_file_list == []:
                message = '*** ERROR: There are not files in the directory {0} with the pattern {1}'.format(self.wrapper_local_dir.get(), self.wrapper_file_pattern.get())
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # confirm the creation of the database transfer config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xdatabase.get_database_transfer_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the database transfer config file corresponding to the environment
        if OK:
            (OK, error_list) = xdatabase.create_database_transfer_config_file(os.path.normpath(self.wrapper_local_dir.get()), selected_file_list, self.wrapper_database_dataset.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the database transfer config file corresponding to the environment
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xdatabase.get_database_transfer_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xdatabase.validate_database_transfer_config_file(strict=False)
            if OK:
                message = 'The database transfer config file is OK.'
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = 'Validate result:\n\n'
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateDatabaseTransferConfigFile".
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
        self.wrapper_local_dir.set('')
        self.wrapper_file_pattern.set('.*')
        self.wrapper_database_dataset.set('')

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateDatabaseTransferConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_local_dir"
        if not self.validate_entry_local_dir():
            OK = False

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # validate the content of "entry_cluster_dir"
        if not self.validate_entry_cluster_dir():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_local_dir.get() != '' and self.wrapper_file_pattern.get() and  self.wrapper_database_dataset.get():
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_local_dir(self):
        '''
        Validate the content of "entry_local_dir"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_local_dir" value is a directory
        if not xlib.existing_dir(self.wrapper_local_dir.get()):
            self.label_local_dir_warning['text'] = 'It must be a existing directory path.'
            self.label_local_dir_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_local_dir_warning['text'] = ''
            self.label_local_dir_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

    def validate_entry_file_pattern(self):
        '''
        Validate the content of "entry_file_pattern"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_file_pattern" value is a valid pattern of regular expression
        try:
            re.compile(self.wrapper_file_pattern.get())
        except:
            self.label_file_pattern_warning['text'] = 'It is not a valid pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'It is a pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

    def validate_entry_cluster_dir(self):
        '''
        Validate the content of "entry_cluster_dir"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_cluster_dir" value is a valid directory path
        if not xlib.is_relative_path(self.wrapper_database_dataset.get()):
            self.label_database_dataset_warning['text'] = 'It is not a valid relative.'
            self.label_database_dataset_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_database_dataset_warning['text'] = 'It is or will be a subdirectory of {0}.'.format(xlib.get_cluster_database_dir())
            self.label_database_dataset_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormUploadDatabaseDataSet(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormUploadDatabaseDataSet" instance.
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
        self.head = 'Database file transfer - Upload dataset to a cluster'

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
        Build the graphical user interface of "FormUploadDatabaseDataSet".
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
        Execute the database file transfer process.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the upload of the read files to the cluster
        if OK:
            message = 'The database files are going to be uploaded to {0}.\n\nAre you sure to continue?\n\nCAUTION: before a transfer process, the config file should be updated.'.format(self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # upload the read files to the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xdatabase.upload_database_dataset.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xdatabase.upload_database_dataset, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormUploadDatabaseDataSet".
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
        Validate the content of each input of "FormUploadDatabaseDataSet" and do the actions linked to its value
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

class FormRecreateReadTransferConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateReadTransferConfigFile" instance.
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
        self.head = 'Read dataset file transfer - Recreate config file'

        # create the wrappers to track changes in inputs
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_local_dir = tkinter.StringVar()
        self.wrapper_local_dir.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateReadTransferConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "image_open_folder"
        image_open_folder = PIL.Image.open('./image_open_folder.png')
        imagetk_open_folder = PIL.ImageTk.PhotoImage(image_open_folder)  

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id')
        self.label_experiment_id.grid(row=0, column=0, padx=(5,5), pady=(75,5), sticky='e')

        # create "entry_experiment_id" and register it with the grid geometry manager
        self.entry_experiment_id = tkinter.Entry(self, textvariable=self.wrapper_experiment_id, width=30, validatecommand=self.validate_inputs)
        self.entry_experiment_id.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_experiment_id_warning" and register it with the grid geometry manager
        self.label_experiment_id_warning = tkinter.Label(self, text='')
        self.label_experiment_id_warning.grid(row=1, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_local_dir" and register it with the grid geometry manager
        self.label_local_dir = tkinter.Label(self, text='Local directory')
        self.label_local_dir.grid(row=2, column=0, padx=(5,5), pady=(25,5), sticky='e')

        # create "entry_local_dir" and register it with the grid geometry manager
        self.entry_local_dir = tkinter.Entry(self, textvariable=self.wrapper_local_dir, width=50, validatecommand=self.validate_inputs)
        self.entry_local_dir.grid(row=2, column=1, padx=(5,5), pady=(25,5), sticky='w')

        # create "button_select_dir" and register it with the grid geometry manager
        self.button_select_dir = tkinter.ttk.Button(self, image=imagetk_open_folder, command=self.select_dir)
        self.button_select_dir.image = imagetk_open_folder
        self.button_select_dir.grid(row=2, column=2, padx=(5,0), pady=(25,5), sticky='w')

        # create "label_local_dir_warning" and register it with the grid geometry manager
        self.label_local_dir_warning = tkinter.Label(self, text='')
        self.label_local_dir_warning.grid(row=3, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=4, column=0, padx=(5,5), pady=(25,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=4, column=1, padx=(5,5), pady=(25,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=5, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*1)
        self.label_fit.grid(row=6, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=6, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=6, column=4, padx=(5,5), pady=(25,5), sticky='w')

    #---------------

    def select_dir(self, event=None):
        '''
        Select a directory and assign it to "entry_local_dir".
        '''

        # select the directory
        directory = tkinter.filedialog.askdirectory(parent=self, initialdir=".", title='Please select a directory')

        # assign the directory to "entry_local_dir"
        if directory != '':
            self.wrapper_local_dir.set(directory)

    #---------------

    def execute(self, event=None):
        '''
        Execute the recreation of the read transfer config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the seleted files list
        if OK:
            selected_file_list = []
            for file in os.listdir(self.wrapper_local_dir.get()):
                if os.path.isfile(os.path.join(self.wrapper_local_dir.get(), file)) and re.match(self.wrapper_file_pattern.get(), file):
                    selected_file_list.append(file)
            if selected_file_list == []:
                message = '*** ERROR: There are not files in the directory {0} with the pattern {1}'.format(self.wrapper_local_dir.get(), self.wrapper_file_pattern.get())
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # confirm the creation of the read transfer config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xread.get_read_transfer_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the read transfer config file corresponding to the environment
        if OK:
            (OK, error_list) = xread.create_read_transfer_config_file(self.wrapper_experiment_id.get(), os.path.normpath(self.wrapper_local_dir.get()), selected_file_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the read transfer config file corresponding to the environment
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xread.get_read_transfer_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xread.validate_read_transfer_config_file(strict=False)
            if OK:
                message = 'The read dataset transfer config file is OK.'
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = 'Validate result:\n\n'
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateReadTransferConfigFile".
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
        self.wrapper_experiment_id.set('')
        self.wrapper_local_dir.set('')
        self.wrapper_file_pattern.set('.*')

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateReadTransferConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_experiment_id"
        if not self.validate_entry_experiment_id():
            OK = False

        # validate the content of "entry_local_dir"
        if not self.validate_entry_local_dir():
            OK = False

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_local_dir.get() != '' and self.wrapper_file_pattern.get() and  self.wrapper_experiment_id.get():
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_experiment_id(self):
        '''
        Validate the content of "entry_experiment_id"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_experiment_id" value is a valid directory path
        if not self.wrapper_experiment_id.get().isidentifier():
            self.label_experiment_id_warning['text'] = 'It must have alphanumeric characters.'
            self.label_experiment_id_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_experiment_id_warning['text'] = ''
            self.label_experiment_id_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

    def validate_entry_local_dir(self):
        '''
        Validate the content of "entry_local_dir"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_local_dir" value is a directory
        if not xlib.existing_dir(self.wrapper_local_dir.get()):
            self.label_local_dir_warning['text'] = 'It must be a existing directory path.'
            self.label_local_dir_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_local_dir_warning['text'] = ''
            self.label_local_dir_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

    def validate_entry_file_pattern(self):
        '''
        Validate the content of "entry_file_pattern"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_file_pattern" value is a valid pattern of regular expression
        try:
            re.compile(self.wrapper_file_pattern.get())
        except:
            self.label_file_pattern_warning['text'] = 'It is not a valid pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'It is a pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormUploadReadDataSet(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormUploadReadDataSet" instance.
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
        self.head = 'Read dataset file transfer - Upload dataset to a cluster'

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
        Build the graphical user interface of "FormUploadReadDataSet".
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
        Execute the read file transfer process.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the upload of the read files to the cluster
        if OK:
            message = 'The read files are going to be uploaded to {0}.\n\nAre you sure to continue?\n\nCAUTION: before a transfer process, the config file should be updated.'.format(self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # upload the read files to the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xread.upload_read_dataset.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xread.upload_read_dataset, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormUploadReadDataSet".
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
        Validate the content of each input of "FormUploadReadDataSet" and do the actions linked to its value
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

class FormRecreateResultTransferConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateResultTransferConfigFile" instance.
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
        self.head = 'Result dataset file transfer - Recreate config file'

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_status = tkinter.StringVar()
        self.wrapper_status.trace('w', self.validate_inputs)
        self.wrapper_result_dataset = tkinter.StringVar()
        self.wrapper_result_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_local_dir = tkinter.StringVar()
        self.wrapper_local_dir.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateResultTransferConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "image_open_folder"
        image_open_folder = PIL.Image.open('./image_open_folder.png')
        imagetk_open_folder = PIL.ImageTk.PhotoImage(image_open_folder)  

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(5,5), pady=(45,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(5,5), pady=(35,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_status" and register it with the grid geometry manager
        self.label_status = tkinter.Label(self, text='Status')
        self.label_status.grid(row=2, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_status" and register it with the grid geometry manager
        self.combobox_status = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_status)
        self.combobox_status.grid(row=2, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_result_dataset" and register it with the grid geometry manager
        self.label_result_dataset = tkinter.Label(self, text='Result dataset')
        self.label_result_dataset.grid(row=3, column=0, padx=(5,5), pady=(35,5), sticky='e')

        # create "combobox_result_dataset" and register it with the grid geometry manager
        self.combobox_result_dataset = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_result_dataset)
        self.combobox_result_dataset.grid(row=3, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=4, column=0, padx=(5,5), pady=(35,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=4, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=5, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_local_dir" and register it with the grid geometry manager
        self.label_local_dir = tkinter.Label(self, text='Local directory')
        self.label_local_dir.grid(row=6, column=0, padx=(5,5), pady=(15,5), sticky='e')

        # create "entry_local_dir" and register it with the grid geometry manager
        self.entry_local_dir = tkinter.Entry(self, textvariable=self.wrapper_local_dir, width=50, validatecommand=self.validate_inputs)
        self.entry_local_dir.grid(row=6, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "button_select_dir" and register it with the grid geometry manager
        self.button_select_dir = tkinter.ttk.Button(self, image=imagetk_open_folder, command=self.select_dir)
        self.button_select_dir.image = imagetk_open_folder
        self.button_select_dir.grid(row=6, column=2, padx=(5,0), pady=(15,5), sticky='w')

        # create "label_local_dir_warning" and register it with the grid geometry manager
        self.label_local_dir_warning = tkinter.Label(self, text='')
        self.label_local_dir_warning.grid(row=7, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*1)
        self.label_fit.grid(row=8, column=2, padx=(0,0), pady=(15,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=8, column=3, padx=(0,5), pady=(15,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=8, column=4, padx=(5,5), pady=(15,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_status.bind('<<ComboboxSelected>>', self.combobox_status_selected_item)
        self.combobox_result_dataset.bind('<<ComboboxSelected>>', self.combobox_result_dataset_selected_item)

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

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # initialize the following inputs
        self.combobox_status['values'] = []
        self.wrapper_status.set('')
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.wrapper_file_pattern.set(' ')
        self.entry_file_pattern['state'] = 'disabled'

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # load data in "combobox_status"
        self.populate_combobox_status()

        # initialize the following inputs
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.wrapper_file_pattern.set(' ')
        self.entry_file_pattern['state'] = 'disabled'

    #---------------

    def combobox_status_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_status" has been selected
        '''

        # load data in "combobox_result_dataset"
        self.populate_combobox_result_dataset()

        # initialize the following inputs
        if self.wrapper_status.get() == 'uncompressed':
            self.wrapper_file_pattern.set('.*')
            self.entry_file_pattern['state'] = 'normal'
        elif self.wrapper_status.get() == 'compressed':
            self.wrapper_file_pattern.set(' ')
            self.entry_file_pattern['state'] = 'disabled'

    #---------------

    def combobox_result_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_result_dataset" has been selected
        '''

        pass

    #---------------

    def select_dir(self, event=None):
        '''
        Select a directory and assign it to "entry_local_dir".
        '''

        # select the directory
        directory = tkinter.filedialog.askdirectory(parent=self, initialdir=".", title='Please select a directory')

        # assign the directory to "entry_local_dir"
        if directory != '':
            self.wrapper_local_dir.set(directory)

    #---------------

    def execute(self, event=None):
        '''
        Execute the recreation of the result transfer config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the selected file list
        if OK:
            if self.wrapper_status.get() == 'uncompressed':
                selected_file_list = []
                cluster_result_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_result_dir(), self.wrapper_experiment_id.get(), self.wrapper_result_dataset.get())
                command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_result_dir, self.wrapper_file_pattern.get())
                (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
                if OK:
                    for line in stdout:
                        selected_file_list.append(line.rstrip('\n'))
                else:
                    message = '*** ERROR: Wrong command ---> {0}'.format(command)
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    return
                if selected_file_list == []:
                    message = '*** ERROR: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_result_dir, self.wrapper_file_pattern.get())
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            elif self.wrapper_status.get() == 'compressed':
                selected_file_list = [None]

        # confirm the creation of the result transfer config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xresult.get_result_transfer_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the result transfer config file
        if OK:
            (OK, error_list) = xresult.create_result_transfer_config_file(self.wrapper_experiment_id.get(), self.wrapper_result_dataset.get(), self.wrapper_status.get(), selected_file_list, os.path.normpath(self.wrapper_local_dir.get()))
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the result transfer config file corresponding to the environment
        if OK:

            # edit the result transfer config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xresult.get_result_transfer_config_file())
            self.wait_window(dialog_editor)

            # validate the result transfer config file
            (OK, error_list) = xresult.validate_result_transfer_config_file(strict=False)
            if OK:
                message = 'The result dataset transfer config file is OK.'
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = 'Validate result:\n\n'
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateResultTransferConfigFile".
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
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_status['values'] = []
        self.wrapper_status.set('')
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.wrapper_file_pattern.set('')
        self.entry_file_pattern['state'] = 'disabled'
        self.wrapper_local_dir.set('')

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
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_experiment_id(self):
        '''
        Populate data in "combobox_experiment_id".
        '''

        # clear the value selected in the combobox
        self.wrapper_experiment_id.set('')

        # initialize the experiment identifications list
        experiment_ids_list = []

        # get the experiment identifications
        command = 'ls {0}'.format(xlib.get_cluster_result_dir())
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    experiment_ids_list.append(line)

        # verify if there are any experimment identifications
        if experiment_ids_list == []:
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_ids_list)

    #---------------

    def populate_combobox_status(self):
        '''
        Populate data in "combobox_action".
        '''

        # clear the value selected in the combobox
        self.wrapper_status.set('')

        # load the list of the status codes in the combobox
        self.combobox_status['values'] = ['compressed', 'uncompressed']

    #---------------

    def populate_combobox_result_dataset(self):
        '''
        Populate data in "combobox_result_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_result_dataset.set('')

        # initialize the result dataset list
        result_dataset_list = []

        # get the result dataset list of the experiments
        if self.wrapper_status.get() == 'uncompressed':
            command = 'cd  {0}/{1}; for list in `ls`; do ls -ld $list | grep -v ^- > /dev/null && echo $list; done;'.format(xlib.get_cluster_result_dir(), self.wrapper_experiment_id.get())
        elif self.wrapper_status.get() == 'compressed':
            command = 'cd {0}/{1}; for list in `ls`; do ls -ld $list | grep -v ^d > /dev/null && echo $list; done;'.format(xlib.get_cluster_result_dir(), self.wrapper_experiment_id.get())
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                result_dataset_list.append(line.rstrip('\n'))

        # verify if there are any experimment identifications
        if result_dataset_list == []:
            message = 'There is not any run of the experiment {0}.'.format(self.wrapper_experiment_id.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the run identifications in the combobox
        self.combobox_result_dataset['values'] = sorted(result_dataset_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateResultTransferConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # validate the content of "entry_local_dir"
        if not self.validate_entry_local_dir():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_status.get() != '' and self.wrapper_result_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and self.wrapper_local_dir.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_file_pattern(self):
        '''
        Validate the content of "entry_file_pattern"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_file_pattern" value is a valid pattern of regular expression
        try:
            re.compile(self.wrapper_file_pattern.get())
        except:
            self.label_file_pattern_warning['text'] = 'It is not a valid pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'It is a pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

    def validate_entry_local_dir(self):
        '''
        Validate the content of "entry_local_dir"
        '''

        # initialize the control variable
        OK = True

        # -- self.wrapper_local_dir.set(os.path.normpath(self.wrapper_local_dir.get()))

        # verify that "entry_local_dir" value is a directory
        if not xlib.existing_dir(self.wrapper_local_dir.get()):
            self.label_local_dir_warning['text'] = 'It must be a existing directory path.'
            self.label_local_dir_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_local_dir_warning['text'] = ''
            self.label_local_dir_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormDownloadResultDataSet(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormDownloadResultDataSet" instance.
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
        self.head = 'Result dataset file transfer - Download dataset from a cluster'

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
        Build the graphical user interface of "FormDownloadResultDataSet".
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
        Execute the read file transfer process.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the download of the result files from the cluster
        if OK:
            message = 'The result files are going to be downloaded from {0}.\n\nAre you sure to continue?\n\nCAUTION: before a transfer process, the config file should be updated.'.format(self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # download the result files from the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xresult.download_result_dataset.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xresult.download_result_dataset, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormDownloadResultDataSet".
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
        Validate the content of each input of "FormDownloadResultDataSet" and do the actions linked to its value
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

class FormRecreateReferenceGzipConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateReferenceGzipConfigFile" instance.
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
 
        # assign the text of the "head"
        self.head = 'Reference dataset file compression/decompression - Recreate config file'

        # get dataset directories
        self.cluster_reference_dir = xlib.get_cluster_reference_dir()
        self.cluster_read_dir = xlib.get_cluster_read_dir()
        self.cluster_result_dir = xlib.get_cluster_result_dir()

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_action = tkinter.StringVar()
        self.wrapper_action.trace('w', self.validate_inputs)
        self.wrapper_reference_dataset = tkinter.StringVar()
        self.wrapper_reference_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateReferenceGzipConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_action" and register it with the grid geometry manager
        self.label_action = tkinter.Label(self, text='Action')
        self.label_action.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_action" and register it with the grid geometry manager
        self.combobox_action = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_action)
        self.combobox_action.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_reference_dataset" and register it with the grid geometry manager
        self.label_reference_dataset = tkinter.Label(self, text='Reference dataset')
        self.label_reference_dataset.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_reference_dataset" and register it with the grid geometry manager
        self.combobox_reference_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_dataset)
        self.combobox_reference_dataset.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*15)
        self.label_fit.grid(row=5, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=5, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=5, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_action.bind('<<ComboboxSelected>>', self.combobox_action_selected_item)
        self.combobox_reference_dataset.bind('<<ComboboxSelected>>', self.combobox_reference_dataset_selected_item)

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

        # load data in "combobox_reference_dataset"
        self.populate_combobox_reference_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_action_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_action" has been selected
        '''

        if self.wrapper_action.get() == 'compress':
            self.wrapper_file_pattern.set('.*')
        elif self.wrapper_action.get() == 'decompress':
            self.wrapper_file_pattern.set('.*gz')

    #---------------

    def combobox_reference_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_dataset" has been selected
        '''

        # get the reference dataset identification
        (OK, error_list, self.reference_dataset_id) = xreference.get_reference_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_reference_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the gzip config file.
        '''

        # file count of the files compressed or decompressed
        count = 0

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the dataset directory
        if OK:
            dataset_dir = xlib.get_cluster_reference_dataset_dir(self.reference_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(dataset_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the dataset directory {0} with the pattern {1}'.format(dataset_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # confirm the creation of the compress/decompress config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xgzip.get_gzip_config_file('reference'))
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the reference dataset compress/decompress config file
        if OK:
            (OK, error_list) = xgzip.create_gzip_config_file(self.wrapper_action.get(), 'reference', None, self.reference_dataset_id, selected_file_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the reference dataset compress/decompress config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xgzip.get_gzip_config_file('reference'))
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xgzip.validate_gzip_config_file('reference', strict=False)
            if OK:
                message = 'The reference dataset gzip config file is OK.'
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = 'Validate result:\n\n'
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateReferenceGzipConfigFile".
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
        self.populate_combobox_action()
        self.combobox_reference_dataset['values'] = []
        self.wrapper_reference_dataset.set('')
        self.reference_dataset_id = None
        self.wrapper_file_pattern.set('.*')

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
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_action(self):
        '''
        Populate data in "combobox_action".
        '''

        # clear the value selected in the combobox
        self.wrapper_action.set('')

        # load the list of the action codes in the combobox
        self.combobox_action['values'] = ['compress', 'decompress']

    #---------------

    def populate_combobox_experiment_id(self):
        '''
        Populate data in "combobox_experiment_id".
        '''

        # clear the value selected in the combobox
        self.wrapper_experiment_id.set('')

        # initialize the experiment identification list
        experiment_id_list = []

        # get the experiment identifications
        command = 'ls {0}'.format(self.cluster_read_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    experiment_id_list.append(line)

        # verify if there are any experimment identifications
        if experiment_id_list == []:
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_reference_dataset(self):
        '''
        Populate data in "combobox_reference_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_dataset.set('')

        # initialize the dataset list
        dataset_list = []

        # get the list of the read dataset names
        (OK, error_list, dataset_name_list) = xreference.get_reference_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the set names in the combobox
        self.combobox_reference_dataset['values'] = dataset_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateReferenceGzipConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_action.get() != '' and self.wrapper_reference_dataset.get() != '' and self.wrapper_file_pattern.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_file_pattern(self):
        '''
        Validate the content of "entry_file_pattern"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_file_pattern" value is a valid pattern of regular expression
        try:
            re.compile(self.wrapper_file_pattern.get())
        except:
            self.label_file_pattern_warning['text'] = 'It is not a valid pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'It is a pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateDatabaseGzipConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateDatabaseGzipConfigFile" instance.
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
 
        # assign the text of the "head"
        self.head = 'Database file compression/decompression - Recreate config file'

        # get dataset directories
        self.cluster_database_dir = xlib.get_cluster_database_dir()
        self.cluster_read_dir = xlib.get_cluster_read_dir()
        self.cluster_result_dir = xlib.get_cluster_result_dir()

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_action = tkinter.StringVar()
        self.wrapper_action.trace('w', self.validate_inputs)
        self.wrapper_database_dataset = tkinter.StringVar()
        self.wrapper_database_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateDatabaseGzipConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_action" and register it with the grid geometry manager
        self.label_action = tkinter.Label(self, text='Action')
        self.label_action.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_action" and register it with the grid geometry manager
        self.combobox_action = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_action)
        self.combobox_action.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_database_dataset" and register it with the grid geometry manager
        self.label_database_dataset = tkinter.Label(self, text='Database')
        self.label_database_dataset.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_database_dataset" and register it with the grid geometry manager
        self.combobox_database_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_database_dataset)
        self.combobox_database_dataset.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*15)
        self.label_fit.grid(row=5, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=5, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=5, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_action.bind('<<ComboboxSelected>>', self.combobox_action_selected_item)
        self.combobox_database_dataset.bind('<<ComboboxSelected>>', self.combobox_database_dataset_selected_item)

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

        # load data in "combobox_database_dataset"
        self.populate_combobox_database_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_action_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_action" has been selected
        '''

        if self.wrapper_action.get() == 'compress':
            self.wrapper_file_pattern.set('.*')
        elif self.wrapper_action.get() == 'decompress':
            self.wrapper_file_pattern.set('.*gz')

    #---------------

    def combobox_database_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_database_dataset" has been selected
        '''

        # get the database dataset identification
        (OK, error_list, self.database_dataset_id) = xdatabase.get_database_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_database_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the gzip config file.
        '''

        # file count of the files compressed or decompressed
        count = 0

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the dataset directory
        if OK:
            dataset_dir = xlib.get_cluster_database_dataset_dir(self.database_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(dataset_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the dataset directory {0} with the pattern {1}'.format(dataset_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # confirm the creation of the compress/decompress config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xgzip.get_gzip_config_file('database'))
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the database dataset compress/decompress config file
        if OK:
            (OK, error_list) = xgzip.create_gzip_config_file(self.wrapper_action.get(), 'database', None, self.database_dataset_id, selected_file_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the database dataset compress/decompress config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xgzip.get_gzip_config_file('database'))
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xgzip.validate_gzip_config_file('database', strict=False)
            if OK:
                message = 'The database dataset gzip config file is OK.'
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = 'Validate result:\n\n'
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateDatabaseGzipConfigFile".
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
        self.populate_combobox_action()
        self.combobox_database_dataset['values'] = []
        self.wrapper_database_dataset.set('')
        self.database_dataset_id = None
        self.wrapper_file_pattern.set('.*')

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
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_action(self):
        '''
        Populate data in "combobox_action".
        '''

        # clear the value selected in the combobox
        self.wrapper_action.set('')

        # load the list of the action codes in the combobox
        self.combobox_action['values'] = ['compress', 'decompress']

    #---------------

    def populate_combobox_experiment_id(self):
        '''
        Populate data in "combobox_experiment_id".
        '''

        # clear the value selected in the combobox
        self.wrapper_experiment_id.set('')

        # initialize the experiment identification list
        experiment_id_list = []

        # get the experiment identifications
        command = 'ls {0}'.format(self.cluster_read_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    experiment_id_list.append(line)

        # verify if there are any experimment identifications
        if experiment_id_list == []:
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_database_dataset(self):
        '''
        Populate data in "combobox_database_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_database_dataset.set('')

        # initialize the dataset list
        dataset_list = []

        # get the list of the read dataset names
        (OK, error_list, dataset_name_list) = xdatabase.get_database_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the set names in the combobox
        self.combobox_database_dataset['values'] = dataset_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateDatabaseGzipConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_action.get() != '' and self.wrapper_database_dataset.get() != '' and self.wrapper_file_pattern.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_file_pattern(self):
        '''
        Validate the content of "entry_file_pattern"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_file_pattern" value is a valid pattern of regular expression
        try:
            re.compile(self.wrapper_file_pattern.get())
        except:
            self.label_file_pattern_warning['text'] = 'It is not a valid pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'It is a pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateReadGzipConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateReadGzipConfigFile" instance.
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
 
        # assign the text of the "head"
        self.head = 'Read dataset file compression/decompression - Recreate config file'

        # get dataset directories
        self.cluster_reference_dir = xlib.get_cluster_reference_dir()
        self.cluster_read_dir = xlib.get_cluster_read_dir()
        self.cluster_result_dir = xlib.get_cluster_result_dir()

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_action = tkinter.StringVar()
        self.wrapper_action.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateReadGzipConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_action" and register it with the grid geometry manager
        self.label_action = tkinter.Label(self, text='Action')
        self.label_action.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_action" and register it with the grid geometry manager
        self.combobox_action = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_action)
        self.combobox_action.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=4, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=4, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=5, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*15)
        self.label_fit.grid(row=6, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=6, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=6, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_action.bind('<<ComboboxSelected>>', self.combobox_action_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)

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

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_action_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_action" has been selected
        '''

        if self.wrapper_action.get() == 'compress':
            self.wrapper_file_pattern.set('.*')
        elif self.wrapper_action.get() == 'decompress':
            self.wrapper_file_pattern.set('.*gz')

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_run_set"
        self.populate_combobox_read_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_read_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_dataset" has been selected
        '''

        # get the read dataset identification
        (OK, error_list, self.read_dataset_id) = xread.get_read_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_read_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the gzip config file.
        '''

        # file count of the files compressed or decompressed
        count = 0

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the dataset directory
        if OK:
            dataset_dir = xlib.get_cluster_experiment_read_dataset_dir(self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(dataset_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the dataset directory {0} with the pattern {1}'.format(dataset_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # confirm the creation of the compress/decompress config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xgzip.get_gzip_config_file('read'))
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the read dataset compress/decompress config file
        if OK:
            (OK, error_list) = xgzip.create_gzip_config_file(self.wrapper_action.get(), 'read', self.wrapper_experiment_id.get(), self.read_dataset_id, selected_file_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the read dataset compress/decompress config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xgzip.get_gzip_config_file('read'))
            self.wait_window(dialog_editor)

            # validate config file
            (OK, error_list) = xgzip.validate_gzip_config_file('read', strict=False)
            if OK:
                message = 'The read dataset gzip config file is OK.'
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = 'Validate result:\n\n'
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateReadGzipConfigFile".
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
        self.populate_combobox_action()
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')

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
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_action(self):
        '''
        Populate data in "combobox_action".
        '''

        # clear the value selected in the combobox
        self.wrapper_action.set('')

        # load the list of the action codes in the combobox
        self.combobox_action['values'] = ['compress', 'decompress']

    #---------------

    def populate_combobox_experiment_id(self):
        '''
        Populate data in "combobox_experiment_id".
        '''

        # clear the value selected in the combobox
        self.wrapper_experiment_id.set('')

        # initialize the experiment identification list
        experiment_id_list = []

        # get the experiment identifications
        command = 'ls {0}'.format(self.cluster_read_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    experiment_id_list.append(line)

        # verify if there are any experimment identifications
        if experiment_id_list == []:
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_read_dataset(self):
        '''
        Populate data in "combobox_read_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_dataset.set('')

        # initialize the dataset list
        dataset_list = []

        # get the list of the read dataset names
        (OK, error_list, dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the set names in the combobox
        self.combobox_read_dataset['values'] = dataset_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateReadGzipConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_action.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'
  
        # return the control variable
        return OK

    #---------------

    def validate_entry_file_pattern(self):
        '''
        Validate the content of "entry_file_pattern"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_file_pattern" value is a valid pattern of regular expression
        try:
            re.compile(self.wrapper_file_pattern.get())
        except:
            self.label_file_pattern_warning['text'] = 'It is not a valid pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'It is a pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateResultGzipConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateResultGzipConfigFile" instance.
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
        self.head = 'Result dataset file compression/decompression - Recreate config file'

        # get dataset directories
        self.cluster_reference_dir = xlib.get_cluster_reference_dir()
        self.cluster_read_dir = xlib.get_cluster_read_dir()
        self.cluster_result_dir = xlib.get_cluster_result_dir()

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_whole = tkinter.StringVar()
        self.wrapper_whole.trace('w', self.validate_inputs)
        self.wrapper_action = tkinter.StringVar()
        self.wrapper_action.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_result_dataset = tkinter.StringVar()
        self.wrapper_result_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateResultGzipConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_whole" and register it with the grid geometry manager
        self.label_whole = tkinter.Label(self, text='Whole dataset?')
        self.label_whole.grid(row=1, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_whole" and register it with the grid geometry manager
        self.combobox_whole = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_whole)
        self.combobox_whole.grid(row=1, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_action" and register it with the grid geometry manager
        self.label_action = tkinter.Label(self, text='Action')
        self.label_action.grid(row=2, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_action" and register it with the grid geometry manager
        self.combobox_action = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_action)
        self.combobox_action.grid(row=2, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=3, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=3, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_result_dataset" and register it with the grid geometry manager
        self.label_result_dataset = tkinter.Label(self, text='Result dataset')
        self.label_result_dataset.grid(row=4, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_result_dataset" and register it with the grid geometry manager
        self.combobox_result_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_result_dataset)
        self.combobox_result_dataset.grid(row=4, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=5, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=5, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=6, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*15)
        self.label_fit.grid(row=7, column=2, padx=(0,0), pady=(15,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=7, column=3, padx=(0,5), pady=(15,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=7, column=4, padx=(5,5), pady=(15,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_whole.bind('<<ComboboxSelected>>', self.combobox_whole_selected_item)
        self.combobox_action.bind('<<ComboboxSelected>>', self.combobox_action_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_result_dataset.bind('<<ComboboxSelected>>', self.combobox_result_dataset_selected_item)

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

        # load data in "combobox_whole"
        self.populate_combobox_whole()

        # initialize the following inputs
        self.combobox_action['values'] = []
        self.wrapper_action.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.result_dataset_id = None
        self.wrapper_file_pattern.set(' ')
        self.entry_file_pattern['state'] = 'disabled'

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_whole_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_whole" has been selected
        '''

        # load data in "combobox_action"
        self.populate_combobox_action()

        # initialize the following inputs
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.result_dataset_id = None
        self.wrapper_file_pattern.set(' ')
        self.entry_file_pattern['state'] = 'disabled'

    #---------------

    def combobox_action_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_action" has been selected
        '''

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # set the status
        if self.combobox_whole.get() == 'whole dataset' and self.combobox_action.get() == 'decompress':
            self.status = 'compressed'
        else:
            self.status = 'uncompressed'

        # initialize the following inputs
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.result_dataset_id = None
        if self.combobox_whole.get() == 'selected files':
            if self.combobox_action.get() == 'compress':
                self.wrapper_file_pattern.set('.*')
            elif self.combobox_action.get() == 'decompress':
                self.wrapper_file_pattern.set('.*gz')
            self.entry_file_pattern['state'] = 'normal'
        elif self.combobox_whole.get() == 'whole dataset':
            self.wrapper_file_pattern.set(' ')
            self.entry_file_pattern['state'] = 'disabled'

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_result_dataset"
        self.populate_combobox_result_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_result_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_result_dataset" has been selected
        '''

        # get the result dataset identification
        (OK, error_list, self.result_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_result_dataset.get(), self.status, passed_connection=True, ssh_client=self.ssh_client)

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the gzip config file.
        '''

        # file count of the files compressed or decompressed
        count = 0

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the dataset directory
        if OK:
            dataset_dir = xlib. get_cluster_experiment_result_dataset_dir(self.wrapper_experiment_id.get(), self.result_dataset_id)

        # get the selected file list
        if OK:
            if self.combobox_whole.get() == 'selected files':
                selected_file_list = []
                command = 'cd {0}; find . -type f -regex "./{1}"'.format(dataset_dir, self.wrapper_file_pattern.get())
                (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
                if OK:
                    for line in stdout:
                        selected_file_list.append(line.rstrip('\n'))
                else:
                    message = '*** ERROR: Wrong command ---> {0}'.format(command)
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                if selected_file_list == []:
                    message = 'WARNING: There are not files in the dataset directory {0} with the pattern {1}'.format(dataset_dir, self.wrapper_file_pattern.get())
                    tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False
            elif self.combobox_whole.get() == 'whole dataset':
                selected_file_list = [None]

        # confirm the creation of the compress/decompress config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xgzip.get_gzip_config_file('result'))
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the result dataset compress/decompress config file
        if OK:
            dataset_type = 'result' if self.combobox_whole.get() == 'selected files' else 'whole-result'
            (OK, error_list) = xgzip.create_gzip_config_file(self.wrapper_action.get(), dataset_type, self.wrapper_experiment_id.get(), self.result_dataset_id, selected_file_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the result dataset compress/decompress config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xgzip.get_gzip_config_file('result'))
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xgzip.validate_gzip_config_file('result', strict=False)
            if OK:
                message = 'The result dataset gzip config file is OK.'
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = 'Validate result:\n\n'
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateResultGzipConfigFile".
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
        self.combobox_whole['values'] = []
        self.wrapper_whole.set('')
        self.combobox_action['values'] = []
        self.wrapper_action.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.result_dataset_id = None
        self.wrapper_file_pattern.set(' ')
        self.entry_file_pattern['state'] = 'disabled'

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
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_whole(self):
        '''
        Populate data in "combobox_whole".
        '''

        # clear the value selected in the combobox
        self.wrapper_whole.set('')

        # load the list of the action codes in the combobox
        self.combobox_whole['values'] = ['whole dataset', 'selected files']

    #---------------

    def populate_combobox_action(self):
        '''
        Populate data in "combobox_action".
        '''

        # clear the value selected in the combobox
        self.wrapper_action.set('')

        # load the list of the action codes in the combobox
        self.combobox_action['values'] = ['compress', 'decompress']

    #---------------

    def populate_combobox_experiment_id(self):
        '''
        Populate data in "combobox_experiment_id".
        '''

        # clear the value selected in the combobox
        self.wrapper_experiment_id.set('')

        # initialize the experiment identification list
        experiment_id_list = []

        # get the experiment identifications
        command = 'ls {0}'.format(self.cluster_result_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    experiment_id_list.append(line)

        # verify if there are any experimment identifications
        if experiment_id_list == []:
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_result_dataset(self):
        '''
        Populate data in "combobox_result_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_result_dataset.set('')

        # initialize the dataset list
        dataset_list = []

        # get the list of the read dataset names
        app_list = [xlib.get_all_applications_selected_code()]
        (OK, error_list, dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.status, app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the set names in the combobox
        self.combobox_result_dataset['values'] = dataset_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateResultGzipConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_whole.get() != '' and self.wrapper_action.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_result_dataset.get() != '' and self.wrapper_file_pattern.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

    def validate_entry_file_pattern(self):
        '''
        Validate the content of "entry_file_pattern"
        '''

        # initialize the control variable
        OK = True

        # verify that "entry_file_pattern" value is a valid pattern of regular expression
        try:
            re.compile(self.wrapper_file_pattern.get())
        except:
            self.label_file_pattern_warning['text'] = 'It is not a valid pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'It is a pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateWholeResultGzipConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateWholeResultGzipConfigFile" instance.
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
        self.head = 'Whole result dataset file compression/decompression - Recreate config file'

        # get dataset directories
        self.cluster_reference_dir = xlib.get_cluster_reference_dir()
        self.cluster_read_dir = xlib.get_cluster_read_dir()
        self.cluster_result_dir = xlib.get_cluster_result_dir()

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_action = tkinter.StringVar()
        self.wrapper_action.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_result_dataset = tkinter.StringVar()
        self.wrapper_result_dataset.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateWholeResultGzipConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_action" and register it with the grid geometry manager
        self.label_action = tkinter.Label(self, text='Action')
        self.label_action.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_action" and register it with the grid geometry manager
        self.combobox_action = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_action)
        self.combobox_action.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_result_dataset" and register it with the grid geometry manager
        self.label_result_dataset = tkinter.Label(self, text='Result dataset')
        self.label_result_dataset.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_result_dataset" and register it with the grid geometry manager
        self.combobox_result_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_result_dataset)
        self.combobox_result_dataset.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*15)
        self.label_fit.grid(row=4, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=4, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=4, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_action.bind('<<ComboboxSelected>>', self.combobox_action_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_result_dataset.bind('<<ComboboxSelected>>', self.combobox_result_dataset_selected_item)

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

        # load data in "combobox_action"
        self.populate_combobox_action()

        # initialize the following inputs
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.result_dataset_id = None

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_action_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_action" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # set the status of the datasets
        if self.wrapper_action.get() == 'compress':
            self.status = 'uncompressed'
        elif self.wrapper_action.get() == 'decompress':
            self.status = 'compressed'

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # initialize the following inputs
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.result_dataset_id = None

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_dataset"
        self.populate_combobox_result_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_result_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_result_dataset" has been selected
        '''

        # get the result dataset identification
        (OK, error_list, self.result_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_result_dataset.get(), self.status, passed_connection=True, ssh_client=self.ssh_client)

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the gzip config file.
        '''

        # file count of the files compressed or decompressed
        count = 0

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the dataset directory
        if OK:
            dataset_dir = xlib.get_cluster_experiment_result_dataset_dir(self.wrapper_experiment_id.get(), self.result_dataset_id)

        # confirm the creation of the compress/decompress config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xgzip.get_gzip_config_file('whole-result'))
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the whole result dataset compress/decompress config file
        if OK:
            (OK, error_list) = xgzip.create_gzip_config_file(self.wrapper_action.get(), 'whole-result', self.wrapper_experiment_id.get(), self.result_dataset_id, [None])
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the whole result dataset compress/decompress config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xgzip.get_gzip_config_file('whole-result'))
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xgzip.validate_gzip_config_file('whole-result', strict=False)
            if OK:
                message = 'The whole result dataset gzip config file is OK.'
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = 'Validate result:\n\n'
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # close the form
        self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRecreateWholeResultGzipConfigFile".
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
        self.combobox_action['values'] = []
        self.wrapper_action.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_result_dataset['values'] = []
        self.wrapper_result_dataset.set('')
        self.result_dataset_id = None

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
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_action(self):
        '''
        Populate data in "combobox_action".
        '''

        # clear the value selected in the combobox
        self.wrapper_action.set('')

        # load the list of the action codes in the combobox
        self.combobox_action['values'] = ['compress', 'decompress']

    #---------------

    def populate_combobox_experiment_id(self):
        '''
        Populate data in "combobox_experiment_id".
        '''

        # clear the value selected in the combobox
        self.wrapper_experiment_id.set('')

        # initialize the experiment identification list
        experiment_id_list = []

        # get the experiment identifications
        command = 'ls {0}'.format(self.cluster_result_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    experiment_id_list.append(line)

        # verify if there are any experimment identifications
        if experiment_id_list == []:
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_result_dataset(self):
        '''
        Populate data in "combobox_result_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_result_dataset.set('')

        # initialize the dataset list
        dataset_list = []

        # get the list of the read dataset names
        app_list = [xlib.get_all_applications_selected_code()]
        (OK, error_list, dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.status, app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the set names in the combobox
        self.combobox_result_dataset['values'] = dataset_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateWholeResultGzipConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_action.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_result_dataset.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRunGzipProcess(tkinter.Frame):

    #---------------

    def __init__(self, parent, main, dataset_type):
        '''
        Execute actions correspending to the creation of a "FormRunGzipProcess" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main
        self.dataset_type = dataset_type

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        if self.dataset_type == 'reference':
            self.head = 'Reference dataset file compression/decompression - Run process'
        elif self.dataset_type == 'database':
            self.head = 'Database file compression/decompression - Run process'
        elif self.dataset_type == 'read':
            self.head = 'Read dataset file compression/decompression - Run process'
        elif self.dataset_type == 'result':
            self.head = 'Result dataset file compression/decompression - Run process'
        elif self.dataset_type == 'whole-result':
            self.head = 'Whole result dataset compression/decompression - Run process'
        
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
        Build the graphical user interface of "FormRunGzipProcess".
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
        Execute the file compression/decompression.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the download of the result files from the cluster
        if OK:
            message = 'The files are going to be compressed/decompressed in {0}.\n\nAre you sure to continue?\n\nCAUTION: before a compression/decompression process, the config file should be updated.'.format(self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # download the result files from the cluster and initialize inputs
        if OK:
            dialog_log = gdialogs.DialogLog(self, self.head, xgzip.run_gzip_process.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xgzip.run_gzip_process, args=(self.wrapper_cluster_name.get(), self.dataset_type, dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRunGzipProcess".
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
        Validate the content of each input of "FormRunGzipProcess" and do the actions linked to its value
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

class FormRemoveDataSet(tkinter.Frame):

    #---------------

    def __init__(self, parent, main, dataset_type):
        '''
        Execute actions correspending to the creation of a "FormRemoveDataSet" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main
        self.dataset_type = dataset_type

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, parent)

        # assign the text of the "head"
        if self.dataset_type in ['reference', 'read', 'result']:
            self.head = 'Datasets - Remove {0} dataset'.format(dataset_type)
        elif self.dataset_type == 'database':
            self.head = 'Datasets - Remove database'
        elif self.dataset_type == 'experiment':
            self.head = 'Datasets - Remove experiment'

        # get dataset directories
        self.cluster_reference_dir = xlib.get_cluster_reference_dir()
        self.cluster_read_dir = xlib.get_cluster_read_dir()
        self.cluster_result_dir = xlib.get_cluster_result_dir()

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        if self.dataset_type == 'read' or self.dataset_type == 'result' or self.dataset_type == 'experiment':
            self.wrapper_experiment_id = tkinter.StringVar()
            self.wrapper_experiment_id.trace('w', self.validate_inputs)
        if self.dataset_type == 'reference' or self.dataset_type == 'read' or self.dataset_type == 'result':
            self.wrapper_dataset = tkinter.StringVar()
            self.wrapper_dataset.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRemoveDataSet".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        if self.dataset_type == 'read' or self.dataset_type == 'result' or self.dataset_type == 'experiment':
            self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
            self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        if self.dataset_type == 'read' or self.dataset_type == 'result' or self.dataset_type == 'experiment':
            self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
            self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_dataset" and register it with the grid geometry manager
        if self.dataset_type == 'reference' or self.dataset_type == 'read' or self.dataset_type == 'result':
            self.label_dataset = tkinter.Label(self, text='Dataset')
            self.label_dataset.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_dataset" and register it with the grid geometry manager
        if self.dataset_type == 'reference' or self.dataset_type == 'read' or self.dataset_type == 'result':
            self.combobox_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_dataset)
            self.combobox_dataset.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*15)
        self.label_fit.grid(row=3, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=3, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=3, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        if self.dataset_type == 'read' or self.dataset_type == 'result' or self.dataset_type == 'experiment':
            self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        if self.dataset_type == 'reference' or self.dataset_type == 'read' or self.dataset_type == 'result':
            self.combobox_dataset.bind('<<ComboboxSelected>>', self.combobox_dataset_selected_item)

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

        # load data in "combobox_experiment_id" or "combobox_dataset"
        if self.dataset_type == 'reference':
            self.populate_combobox_dataset()
        elif self.dataset_type  == 'read' or self.dataset_type  == 'result' or self.dataset_type  == 'experiment':
            self.populate_combobox_experiment_id()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_run_set"
        if self.dataset_type  == 'reference' or self.dataset_type  == 'read' or self.dataset_type  == 'result':
            self.populate_combobox_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_dataset" has been selected
        '''

        # get the read dataset identification
        if self.dataset_type == 'reference':
            (OK, error_list, self.dataset_id) = xreference.get_reference_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)
        elif self.dataset_type == 'read':
            (OK, error_list, self.dataset_id) = xread.get_read_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)
        elif self.dataset_type == 'result':
            (OK, error_list, self.dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

    #---------------

    def execute(self, event=None):
        '''
        View the log of the run identification.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the removal of the dataset
        if OK:
            if self.dataset_type == 'reference' or  self.dataset_type == 'read' or  self.dataset_type == 'result':
                message = 'The dataset {0} is going to be irreversibly removed.\n\nAre you sure to continue?\n\nCAUTION: This action can NOT be undone.'.format(self.wrapper_dataset.get())
            elif self.dataset_type == 'experiment':
                message = 'Every read and run result dataset of the experiment {0} is going to be irreversibly removed.\n\nAre you sure to continue?\n\nCAUTION: This action can NOT be undone.'.format(self.wrapper_experiment_id.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # remove the dataset
        if OK:
            if self.dataset_type == 'reference':
                command = 'rm -fr {0}/{1}'.format(self.cluster_reference_dir, self.dataset_id)
                (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
                if OK:
                    message = 'The dataset {0} is removed.'.format(self.wrapper_dataset.get())
                    tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                else:
                    message = '*** ERROR: Wrong command ---> {0}'.format(command)
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    self.close()
            elif self.dataset_type == 'read':
                command = 'rm -fr {0}/{1}/{2}'.format(self.cluster_read_dir, self.wrapper_experiment_id.get(), self.dataset_id)
                (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
                if OK:
                    message = 'The dataset {0} is removed.'.format(self.wrapper_dataset.get())
                    tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                else:
                    message = '*** ERROR: Wrong command ---> {0}'.format(command)
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    self.close()
            elif self.dataset_type == 'result':
                command = 'rm -fr {0}/{1}/{2}'.format(self.cluster_result_dir, self.wrapper_experiment_id.get(), self.dataset_id)
                (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
                if OK:
                    message = 'The dataset {0} is removed.'.format(self.wrapper_dataset.get())
                    tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                else:
                    message = '*** ERROR: Wrong command ---> {0}'.format(command)
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    self.close()
            elif self.dataset_type == 'experiment':
                command = 'rm -fr {0}/{1}'.format(self.cluster_result_dir, self.wrapper_experiment_id.get())
                (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
                if OK:
                    command = 'rm -fr {0}/{1}'.format(self.cluster_read_dir, self.wrapper_experiment_id.get())
                    (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
                if OK:
                    message = 'The datasets of experiment {0} are removed.'.format(self.wrapper_experiment_id.get())
                    tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                else:
                    message = '*** ERROR: Wrong command ---> {0}'.format(command)
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    self.close()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRemoveDataSet".
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
        if self.dataset_type == 'read' or self.dataset_type == 'result' or self.dataset_type == 'experiment':
            self.combobox_experiment_id['values'] = []
            self.wrapper_experiment_id.set('')
        if self.dataset_type == 'reference' or self.dataset_type == 'read' or self.dataset_type == 'result':
            self.combobox_dataset['values'] = []
            self.wrapper_dataset.set('')
            self.dataset_id = None

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
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_experiment_id(self):
        '''
        Populate data in "combobox_experiment_id".
        '''

        # clear the value selected in the combobox
        self.wrapper_experiment_id.set('')

        # initialize the experiment identification list
        experiment_id_list = []

        # get the experiment identifications
        if self.dataset_type == 'read':
            command = 'ls {0}'.format(self.cluster_read_dir)
        elif self.dataset_type == 'result':
            command = 'ls {0}'.format(self.cluster_result_dir)
        elif self.dataset_type == 'experiment':
            command = 'ls {0}'.format(self.cluster_read_dir)
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    experiment_id_list.append(line)

        # verify if there are any experimment identifications
        if experiment_id_list == []:
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_dataset(self):
        '''
        Populate data in "combobox_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_dataset.set('')

        # initialize the dataset list
        dataset_list = []

        # get the list of the read dataset names
        if self.dataset_type == 'reference':
            (OK, error_list, dataset_name_list) = xreference.get_reference_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)
        elif self.dataset_type == 'read':
            (OK, error_list, dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)
        elif self.dataset_type == 'result':
            app_list = [xlib.get_all_applications_selected_code()]
            (OK, error_list, dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the set names in the combobox
        self.combobox_dataset['values'] = dataset_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRemoveDataSet" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.dataset_type == 'reference':
            if self.wrapper_cluster_name.get() != '' and self.wrapper_dataset.get() != '':
                self.button_execute['state'] = 'enable'
            else:
                self.button_execute['state'] = 'disabled'
        elif self.dataset_type == 'read' or self.dataset_type == 'result':
            if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_dataset.get() != '':
                self.button_execute['state'] = 'enable'
            else:
                self.button_execute['state'] = 'disabled'
        elif self.dataset_type == 'experiment':
            if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '':
                self.button_execute['state'] = 'enable'
            else:
                self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormRemoveDatabaseDataSet(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRemoveDatabaseDataSet" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, parent)

        # assign the text of the "head"
        self.head = 'Datasets - Remove database'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_database_dataset = tkinter.StringVar()
        self.wrapper_database_dataset.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRemoveDatabaseDataSet".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_database_dataset" and register it with the grid geometry manager
        self.label_database_dataset = tkinter.Label(self, text='Database')
        self.label_database_dataset.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_database_dataset" and register it with the grid geometry manager
        self.combobox_database_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_database_dataset)
        self.combobox_database_dataset.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*15)
        self.label_fit.grid(row=3, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=3, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=3, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_database_dataset.bind('<<ComboboxSelected>>', self.combobox_database_dataset_selected_item)

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

        # load data in "combobox_database_dataset"
            self.populate_combobox_database_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_database_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_database_dataset" has been selected
        '''

        # get the database dataset identification
        (OK, error_list, self.database_dataset_id) = xdatabase.get_database_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_database_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

    #---------------

    def execute(self, event=None):
        '''
        View the log of the run identification.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the removal of the database dataset
        if OK:
            message = 'The database {0} is going to be irreversibly removed.\n\nAre you sure to continue?\n\nCAUTION: This action can NOT be undone.'.format(self.wrapper_database_dataset.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # remove the database dataset
        if OK:
            command = 'rm -fr {0}/{1}'.format(xlib.get_cluster_database_dir(), self.database_dataset_id)
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                message = 'The database {0} is removed.'.format(self.wrapper_database_dataset.get())
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                self.close()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRemoveDatabaseDataSet".
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
        self.combobox_database_dataset['values'] = []
        self.wrapper_database_dataset.set('')
        self.database_dataset_id = None

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
            message = 'There is not any running cluster.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_cluster_name['values'] = running_cluster_list

    #---------------

    def populate_combobox_database_dataset(self):
        '''
        Populate data in "combobox_database_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_database_dataset.set('')

        # get the list of the read dataset names
        (OK, error_list, database_dataset_name_list) = xdatabase.get_database_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the set names in the combobox
        self.combobox_database_dataset['values'] = database_dataset_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRemoveDatabaseDataSet" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_database_dataset.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('This file contains the classes related to datasets forms in gui mode.')
    sys.exit(0)

#-------------------------------------------------------------------------------
