#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

'''
This software has been developed by:

    GI Genética, Fisiología e Historia Forestal
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politécnica de Madrid
    https://github.com/ggfhf/
    http://gfhforestal.com/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

'''
This file contains the classes related to log forms in gui mode.
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
import subprocess

import gdialogs
import xconfiguration
import xec2
import xgzip
import xlib
import xread
import xreference
import xresult
import xssh

#-------------------------------------------------------------------------------

class FormViewSubmissionLogs(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormViewSubmissionLogs" instance.
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
        self.head = 'Logs - View submission logs in the local computer'

        # create the wrappers to track changes in the inputs
        self.wrapper_local_process_text = tkinter.StringVar()
        self.wrapper_local_process_text.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormViewSubmissionLogs".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_name_process_text" and register it with the grid geometry manager
        self.label_local_process_text = tkinter.Label(self, text='Local process')
        self.label_local_process_text.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_local_process_text" and register it with the grid geometry manager
        self.combobox_local_process_text = tkinter.ttk.Combobox(self, width=40, height=4, state='readonly', textvariable=self.wrapper_local_process_text)
        self.combobox_local_process_text.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

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
        self.combobox_local_process_text.bind('<<ComboboxSelected>>', self.combobox_local_process_text_selected_item)

    #---------------

    def combobox_local_process_text_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_local_process_text" has been selected
        '''

        # get the local process identification
        self.local_process_id = xlib.get_local_process_id(self.wrapper_local_process_text.get())

    #---------------

    def execute(self, event=None):
        '''
        Execute the list the submission logs in the local host.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the local process dictionary
        local_process_dict = xlib.get_local_process_dict()

        # build the log dictionary
        if OK:
            log_dict = {}
            if self.wrapper_local_process_text.get() == ' all':
                command = xlib.list_log_files_command('all')
            else:
                command = xlib.list_log_files_command(self.local_process_id)
            output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            for line in output.stdout.split('\n'):
                if line != '':
                    line = os.path.basename(line)
                    run_id = line
                    try:
                        pattern = r'^(.+)\-(.+)\-(.+)\-(.+).txt$'
                        mo = re.search(pattern, line)
                        environment = mo.group(1)
                        local_process_id = mo.group(2).strip()
                        yymmdd = mo.group(3)
                        hhmmss = mo.group(4)
                        process_text = local_process_dict[local_process_id]['text']
                        date = '20{0}-{1}-{2}'.format(yymmdd[:2], yymmdd[2:4], yymmdd[4:])
                        time = '{0}:{1}:{2}'.format(hhmmss[:2], hhmmss[2:4], hhmmss[4:])
                    except:
                        process_text = 'unknown process'
                        date = '0000-00-00'
                        time = '00:00:00'
                    log_dict[run_id] = {'run_id': run_id, 'process_text': process_text, 'date': date, 'time': time}

        # verify if there are any nodes running
        if OK:
            if log_dict == {}:
                message = 'There is not any local process log.'
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # build the data list
        if OK:
            data_list = ['run_id', 'process_text', 'date', 'time']

        # build the data dictionary
        if OK:
            data_dict = {}
            data_dict['run_id'] = {'text': 'Run id', 'width': 300, 'aligment': 'left'}
            data_dict['process_text'] = {'text': 'Process', 'width': 300, 'aligment': 'left'}
            data_dict['date'] = {'text': 'Date', 'width': 80, 'aligment': 'right'}
            data_dict['time'] = {'text': 'Time', 'width': 80, 'aligment': 'right'}

        # create the dialog Table to list the local process logs
        if OK:
            dialog_table = gdialogs.DialogTable(self, 'Local process log', 400, 900, data_list, data_dict, log_dict, 'view_submission_logs')
            self.wait_window(dialog_table)

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormViewSubmissionLogs".
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
        self.populate_combobox_local_process_text()
        self.local_process_id = None

    #---------------

    def populate_combobox_local_process_text(self):
        '''
        Populate data in "combobox_local_process_text".
        '''

        # clear the value selected in the combobox
        self.wrapper_local_process_text.set('')

        # get the local process dictionary
        local_process_dict = xlib.get_local_process_dict()

        # build the local process text list
        local_process_text_list = []
        for local_process_id in local_process_dict.keys():
            local_process_text_list.append(local_process_dict[local_process_id]['text'])

        # add item 'all' to local process text list
        local_process_text_list.append(' all')
        local_process_text_list.sort()

        # load the names of local processes
        self.combobox_local_process_text['values'] = local_process_text_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormViewSubmissionLogs" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_local_process_text.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

class FormViewResultLogs(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormViewResultLogs" instance.
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
        self.head = 'Logs - View result logs in the cluster'

        # create the wrappers to track changes in the inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormViewResultLogs".
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
        self.label_experiment_id = tkinter.Label(self, text='Experiment/process')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*10)
        self.label_fit.grid(row=2, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=2, column=3, padx=(5,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=2, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)

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

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the list the result logs in the cluster.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the run dictionary of the experiment
        if OK:
            # -- command = 'ls {0}/{1}'.format(xlib.get_cluster_result_dir(), self.wrapper_experiment_id.get())
            command = 'cd  {0}/{1}; for list in `ls`; do ls -ld $list | grep -v ^- > /dev/null && echo $list; done;'.format(xlib.get_cluster_result_dir(), self.wrapper_experiment_id.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                result_dataset_dict = {}
                for line in stdout:
                    line = line.rstrip('\n')
                    if line != 'lost+found':
                        result_dataset_id = line
                        try:
                            pattern = r'^(.+)\-(.+)\-(.+)$'
                            mo = re.search(pattern, result_dataset_id)
                            bioinfo_app_code = mo.group(1).strip()
                            yymmdd = mo.group(2)
                            hhmmss = mo.group(3)
                            date = '20{0}-{1}-{2}'.format(yymmdd[:2], yymmdd[2:4], yymmdd[4:])
                            time = '{0}:{1}:{2}'.format(hhmmss[:2], hhmmss[2:4], hhmmss[4:])
                        except:
                            bioinfo_app_code = 'xxx'
                            date = '0000-00-00'
                            time = '00:00:00'
                        if result_dataset_id.startswith(xlib.get_bedtools_code()+'-'):
                            bioinfo_app_name = xlib.get_bedtools_name()
                        elif result_dataset_id.startswith(xlib.get_blastplus_code()+'-'):
                            bioinfo_app_name = xlib.get_blastplus_name()
                        elif result_dataset_id.startswith(xlib.get_bowtie2_code()+'-'):
                            bioinfo_app_name = xlib.get_bowtie2_name()
                        elif result_dataset_id.startswith(xlib.get_busco_code()+'-'):
                            bioinfo_app_name = xlib.get_busco_name()
                        elif result_dataset_id.startswith(xlib.get_cd_hit_code()+'-'):
                            bioinfo_app_name = xlib.get_cd_hit_name()
                        elif result_dataset_id.startswith(xlib.get_cd_hit_est_code()+'-'):
                            bioinfo_app_name = xlib.get_cd_hit_est_name()
                        elif result_dataset_id.startswith(xlib.get_detonate_code()+'-'):
                            bioinfo_app_name = xlib.get_detonate_name()
                        elif result_dataset_id.startswith(xlib.get_emboss_code()+'-'):
                            bioinfo_app_name = xlib.get_emboss_name()
                        elif result_dataset_id.startswith(xlib.get_fastqc_code()+'-'):
                            bioinfo_app_name = xlib.get_fastqc_name()
                        elif result_dataset_id.startswith(xlib.get_gmap_code()+'-'):
                            bioinfo_app_name = xlib.get_gmap_name()
                        elif result_dataset_id.startswith(xlib.get_gmap_gsnap_code()+'-'):
                            bioinfo_app_name = xlib.get_gmap_gsnap_name()
                        elif result_dataset_id.startswith(xlib.get_gzip_code()+'-'):
                            bioinfo_app_name = xlib.get_gzip_name()
                        elif result_dataset_id.startswith(xlib.get_insilico_read_normalization_code()+'-'):
                            bioinfo_app_name = xlib.get_insilico_read_normalization_name()
                        elif result_dataset_id.startswith(xlib.get_miniconda3_code()+'-'):
                            bioinfo_app_name = xlib.get_miniconda3_name()
                        elif result_dataset_id.startswith(xlib.get_ngshelper_code()+'-'):
                            bioinfo_app_name = xlib.get_ngshelper_name()
                        elif result_dataset_id.startswith(xlib.get_quast_code()+'-'):
                            bioinfo_app_name = xlib.get_quast_name()
                        elif result_dataset_id.startswith(xlib.get_r_code()+'-'):
                            bioinfo_app_name = xlib.get_r_name()
                        elif result_dataset_id.startswith(xlib.get_ref_eval_code()+'-'):
                            bioinfo_app_name = xlib.get_ref_eval_name()
                        elif result_dataset_id.startswith(xlib.get_rnaquast_code()+'-'):
                            bioinfo_app_name = xlib.get_rnaquast_name()
                        elif result_dataset_id.startswith(xlib.get_rsem_code()+'-'):
                            bioinfo_app_name = xlib.get_rsem_name()
                        elif result_dataset_id.startswith(xlib.get_rsem_eval_code()+'-'):
                            bioinfo_app_name = xlib.get_rsem_eval_name()
                        elif result_dataset_id.startswith(xlib.get_samtools_code()+'-'):
                            bioinfo_app_name = xlib.get_samtools_name()
                        elif result_dataset_id.startswith(xlib.get_soapdenovotrans_code()+'-'):
                            bioinfo_app_name = xlib.get_soapdenovotrans_name()
                        elif result_dataset_id.startswith(xlib.get_star_code()+'-'):
                            bioinfo_app_name = xlib.get_star_name()
                        elif result_dataset_id.startswith(xlib.get_transabyss_code()+'-'):
                            bioinfo_app_name = xlib.get_transabyss_name()
                        elif result_dataset_id.startswith(xlib.get_transcript_filter_code()+'-'):
                            bioinfo_app_name = xlib.get_transcript_filter_name()
                        elif result_dataset_id.startswith(xlib.get_transcriptome_blastx_code()+'-'):
                            bioinfo_app_name = xlib.get_transcriptome_blastx_name()
                        elif result_dataset_id.startswith(xlib.get_transrate_code()+'-'):
                            bioinfo_app_name = xlib.get_transrate_name()
                        elif result_dataset_id.startswith(xlib.get_trimmomatic_code()+'-'):
                            bioinfo_app_name = xlib.get_trimmomatic_name()
                        elif result_dataset_id.startswith(xlib.get_trinity_code()+'-'):
                            bioinfo_app_name = xlib.get_trinity_name()
                        else:
                            bioinfo_app_name = 'xxx'
                        result_dataset_dict[result_dataset_id] = {'experiment_id': self.wrapper_experiment_id.get(), 'result_dataset_id': result_dataset_id, 'bioinfo_app': bioinfo_app_name, 'date': date, 'time': time}

        # verify if there are any nodes running
        if OK:
            if result_dataset_dict == {}:
                message = 'There is not any run.'
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the data list
        if OK:
            data_list = ['experiment_id', 'result_dataset_id', 'bioinfo_app', 'date', 'time']

        # build the data dictionary
        if OK:
            data_dict = {}
            data_dict['experiment_id']= {'text': 'Experiment id. / Process', 'width': 200, 'aligment': 'left'}
            data_dict['result_dataset_id'] = {'text': 'Result dataset', 'width': 200, 'aligment': 'left'}
            data_dict['bioinfo_app'] = {'text': 'Bioinfo app / Utility', 'width': 200, 'aligment': 'left'}
            data_dict['date'] = {'text': 'Date', 'width': 80, 'aligment': 'right'}
            data_dict['time'] = {'text': 'Time', 'width': 80, 'aligment': 'right'}

        # create the dialog Table to show the nodes running
        if OK:
            dialog_table = gdialogs.DialogTable(self, 'Experiment runs in {0}/{1}'.format(xlib.get_cluster_result_dir(), self.wrapper_experiment_id.get()), 400, 900, data_list, data_dict, result_dataset_dict, 'view_result_logs', [self.wrapper_cluster_name.get()])
            self.wait_window(dialog_table)

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormViewResultLogs".
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

    def populate_combobox_experiment_id(self):
        '''
        Populate data in "combobox_experiment_id".
        '''

        # clear the value selected in the combobox
        self.wrapper_experiment_id.set('')

        # initialize the experiment identification list
        experiment_id_list = []

        # get the experiment identifications
        command = 'ls {0}'.format(xlib.get_cluster_result_dir())
        (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
        if OK:
            for line in stdout:
                line = line.rstrip('\n')
                if line != 'lost+found':
                    experiment_id_list.append(line)

        # verify if there are any experimment identifications
        if experiment_id_list == []:
            message = 'The cluster has not experiment data.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the names of clusters which are running in the combobox
        self.combobox_experiment_id['values'] = experiment_id_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormViewResultLogs" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

   #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('This file contains the classes related to log form in gui mode.')
    sys.exit(0)

#-------------------------------------------------------------------------------
