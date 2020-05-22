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
This file contains the classes related to BioInfo application forms in gui mode.
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
import xbioinfoapp
import xbusco
import xcdhit
import xdatabase
import xdetonate
import xec2
import xfastqc
import xgmap
import xlib
import xngshelper
import xquast
import xread
import xreference
import xresult
import xrnaquast
import xsoapdenovotrans
import xssh
import xstar
import xtransabyss
import xtransrate
import xtrimmomatic
import xtrinity

#-------------------------------------------------------------------------------

class FormSetupBioinfoApp(tkinter.Frame):

    #---------------

    def __init__(self, parent, main, app):
        '''
        Execute actions correspending to the creation of a "FormSetupBioinfoApp" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main
        self.app_code = app

        # set the software name
        if self.app_code == xlib.get_bedtools_code():
            self.app_name = xlib.get_bedtools_name()
        elif self.app_code == xlib.get_blastplus_code():
            self.app_name = xlib.get_blastplus_name()
        elif self.app_code == xlib.get_bowtie2_code():
            self.app_name = xlib.get_bowtie2_name()
        elif self.app_code == xlib.get_busco_code():
            self.app_name = xlib.get_busco_name()
        elif self.app_code == xlib.get_cd_hit_code():
            self.app_name = xlib.get_cd_hit_name()
        elif self.app_code == xlib.get_detonate_code():
            self.app_name = xlib.get_detonate_name()
        elif self.app_code == xlib.get_emboss_code():
            self.app_name = xlib.get_emboss_name()
        elif self.app_code == xlib.get_fastqc_code():
            self.app_name = xlib.get_fastqc_name()
        elif self.app_code == xlib.get_gmap_gsnap_code():
            self.app_name = xlib.get_gmap_gsnap_name()
        elif self.app_code == xlib.get_miniconda3_code():
            self.app_name = xlib.get_miniconda3_name()
        elif self.app_code == xlib.get_ngshelper_code():
            self.app_name = xlib.get_ngshelper_name()
        elif self.app_code == xlib.get_quast_code():
            self.app_name = xlib.get_quast_name()
        elif self.app_code == xlib.get_r_code():
            self.app_name = xlib.get_r_name()
        elif self.app_code == xlib.get_rnaquast_code():
            self.app_name = xlib.get_rnaquast_name()
        elif self.app_code == xlib.get_rsem_code():
            self.app_name = xlib.get_rsem_name()
        elif self.app_code == xlib.get_samtools_code():
            self.app_name = xlib.get_samtools_name()
        elif self.app_code == xlib.get_soapdenovotrans_code():
            self.app_name = xlib.get_soapdenovotrans_name()
        elif self.app_code == xlib.get_star_code():
            self.app_name = xlib.get_star_name()
        elif self.app_code == xlib.get_transabyss_code():
            self.app_name = xlib.get_transabyss_name()
        elif self.app_code == xlib.get_transrate_code():
            self.app_name = xlib.get_transrate_name()
        elif self.app_code == xlib.get_trimmomatic_code():
            self.app_name = xlib.get_trimmomatic_name()
        elif self.app_code == xlib.get_trinity_code():
            self.app_name = xlib.get_trinity_name()

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Set up software'.format(self.app_name)

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
        Build the graphical user interface of "FormSetupBioinfoApp".
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
        Execute the app set up process.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the software set up
        if OK:
            if self.app_code == xlib.get_miniconda3_code():
                message = '{0} (Python & Bioconda environments) is going to be set up in the cluster {1}. All Bioconda packages previously set up will be lost and they must be reinstalled.\n\nAre you sure to continue?'.format(self.app_name, self.wrapper_cluster_name.get())
            elif self.app_code == xlib.get_r_code():
                message = '{0} and analysis packages are going to be set up in the cluster {1}. The previous version will be lost, if it exists.\n\nAre you sure to continue?'.format(self.app_name, self.wrapper_cluster_name.get())
            elif self.app_code in [xlib.get_ngshelper_code(), xlib.get_rnaquast_code(), xlib.get_transrate_code()]:
                message = '{0} software is going to be set up in the cluster {1}. The previous version will be lost, if it exists.\n\nAre you sure to continue?'.format(self.app_name, self.wrapper_cluster_name.get())
            else:
                message = 'The {0} Bioconda package is going to be set up in the cluster {1}. The previous version will be lost, if it exists.\n\nAre you sure to continue?'.format(self.app_name, self.wrapper_cluster_name.get())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # set up the software
        if OK:

            # set up the BEDTools software
            if self.app_code == xlib.get_bedtools_code():
                package_code_list = [xlib.get_bedtools_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the BLAST+ software
            elif self.app_code == xlib.get_blastplus_code():
                package_code_list = [xlib.get_blastplus_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the Bowtie2 software
            elif self.app_code == xlib.get_bowtie2_code():
                package_code_list = [xlib.get_bowtie2_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the BUSCO software
            elif self.app_code == xlib.get_busco_code():
                package_code_list = [xlib.get_busco_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the CD-HIT software
            elif self.app_code == xlib.get_cd_hit_code():
                package_code_list = [xlib.get_cd_hit_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the DETONATE software
            elif self.app_code == xlib.get_detonate_code():
                package_code_list = [xlib.get_detonate_bioconda_code(), xlib.get_bowtie2_bioconda_code(), xlib.get_rsem_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the EMBOSS software
            elif self.app_code == xlib.get_emboss_code():
                package_code_list = [xlib.get_emboss_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the FastQC software
            elif self.app_code == xlib.get_fastqc_code():
                package_code_list = [xlib.get_fastqc_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the GMAP-GSNAP software
            elif self.app_code == xlib.get_gmap_gsnap_code():
                package_code_list = [xlib.get_gmap_gsnap_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the Miniconda3 software
            elif self.app_code == xlib.get_miniconda3_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_miniconda3.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_miniconda3, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the NGShelper software
            elif self.app_code == xlib.get_ngshelper_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xngshelper.setup_ngshelper.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xngshelper.setup_ngshelper, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the QUAST software
            elif self.app_code == xlib.get_quast_code():
                package_code_list = [xlib.get_quast_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up R and analysis packages
            elif self.app_code == xlib.get_r_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_r.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_r, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the rnaQUAST software
            elif self.app_code == xlib.get_rnaquast_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xrnaquast.setup_rnaquast.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xrnaquast.setup_rnaquast, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the RSEM software
            elif self.app_code == xlib.get_rsem_code():
                package_code_list = [xlib.get_rsem_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the SAMtools software
            if self.app_code == xlib.get_samtools_code():
                package_code_list = [xlib.get_samtools_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the SOAPdenovo-Trans software
            elif self.app_code == xlib.get_soapdenovotrans_code():
                package_code_list = [xlib.get_soapdenovotrans_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the STAR software
            elif self.app_code == xlib.get_star_code():
                package_code_list = [xlib.get_star_bioconda_code(), xlib.get_trinity_bioconda_code(), xlib.get_bowtie2_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the Trans-ABySS software
            elif self.app_code == xlib.get_transabyss_code():
                package_code_list = [xlib.get_transabyss_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the Transrate software
            elif self.app_code == xlib.get_transrate_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xtransrate.setup_transrate.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xtransrate.setup_transrate, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the Trimmomatic software
            elif self.app_code == xlib.get_trimmomatic_code():
                package_code_list = [xlib.get_trimmomatic_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # set up the Trinity software
            elif self.app_code == xlib.get_trinity_code():
                package_code_list = [xlib.get_trinity_bioconda_code(), xlib.get_bowtie2_bioconda_code()]
                dialog_log = gdialogs.DialogLog(self, self.head, xbioinfoapp.setup_bioconda_package_list.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbioinfoapp.setup_bioconda_package_list, args=(self.app_code, self.app_name, package_code_list, self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormSetupBioInfoApp".
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
        Validate the content of each input of "FormSetupBioinfoApp" and do the actions linked to its value
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

class FormRecreateBuscoConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateBuscoConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_busco_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_assembly_dataset = tkinter.StringVar()
        self.wrapper_assembly_dataset.trace('w', self.validate_inputs)
        self.wrapper_assembly_type = tkinter.StringVar()
        self.wrapper_assembly_type.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateBuscoConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_assembly_dataset" and register it with the grid geometry manager
        self.label_assembly_dataset = tkinter.Label(self, text='Assembly dataset')
        self.label_assembly_dataset.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_assembly_dataset" and register it with the grid geometry manager
        self.combobox_assembly_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_assembly_dataset)
        self.combobox_assembly_dataset.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_assembly_type" and register it with the grid geometry manager
        self.label_assembly_type = tkinter.Label(self, text='Assembly type')
        self.label_assembly_type.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_assembly_type" and register it with the grid geometry manager
        self.combobox_assembly_type = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_assembly_type)
        self.combobox_assembly_type.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=4, column=2, padx=(0,0), pady=(55,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=4, column=3, padx=(0,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=4, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_assembly_dataset.bind('<<ComboboxSelected>>', self.combobox_assembly_dataset_selected_item)
        self.combobox_assembly_type.bind('<<ComboboxSelected>>', self.combobox_assembly_type_selected_item)

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

        # clear data in "combobox_assembly_dataset"
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')

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

        # load data in "combobox_assembly_dataset"
        self.populate_combobox_assembly_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_assembly_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_dataset" has been selected
        '''

        # get the assembly dataset identification
        (OK, error_list, self.assembly_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_assembly_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

        # load data in "combobox_assembly_type"
        if self.assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            self.combobox_assembly_type['values'] = ['CONTIGS', 'SCAFFOLDS']
            self.wrapper_assembly_type.set('')
            self.combobox_assembly_type['state'] = 'normal'
        elif self.assembly_dataset_id.startswith(xlib.get_transabyss_code()) or self.assembly_dataset_id.startswith(xlib.get_trinity_code()) or self.assembly_dataset_id.startswith(xlib.get_star_code()) or self.assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or self.assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            self.combobox_assembly_type['values'] = ['NONE']
            self.wrapper_assembly_type.set('NONE')
            self.combobox_assembly_type['state'] = 'disabled'

    #---------------

    def combobox_assembly_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_type" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the creation of the BUSCO config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xbusco.get_busco_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the BUSCO config file
        if OK:
            (OK, error_list) = xbusco.create_busco_config_file(self.wrapper_experiment_id.get(), self.assembly_dataset_id, self.wrapper_assembly_type.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the BUSCO config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xbusco.get_busco_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xbusco.validate_busco_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_busco_name())
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
        Close "FormRecreateBuscoConfigFile".
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
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')
        self.assembly_dataset_id = None
        self.combobox_assembly_type['values'] = []
        self.wrapper_assembly_type.set('')
        self.combobox_assembly_type['state'] = 'disabled'

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

    def populate_combobox_assembly_dataset(self):
        '''
        Populate data in "combobox_assembly_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_assembly_dataset.set('')

        # get the list of the assembly dataset names
        app_list = [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]
        (OK, error_list, assembly_dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the assembly dataset names in the combobox
        self.combobox_assembly_dataset['values'] = sorted(assembly_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateBuscoConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != ''  and self.wrapper_assembly_dataset.get() != '' and self.wrapper_assembly_type != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateCdHitEstConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateCdHitEstConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_cd_hit_est_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_assembly_dataset = tkinter.StringVar()
        self.wrapper_assembly_dataset.trace('w', self.validate_inputs)
        self.wrapper_assembly_type = tkinter.StringVar()
        self.wrapper_assembly_type.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateCdHitEstConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_assembly_dataset" and register it with the grid geometry manager
        self.label_assembly_dataset = tkinter.Label(self, text='Assembly dataset')
        self.label_assembly_dataset.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_assembly_dataset" and register it with the grid geometry manager
        self.combobox_assembly_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_assembly_dataset)
        self.combobox_assembly_dataset.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_assembly_type" and register it with the grid geometry manager
        self.label_assembly_type = tkinter.Label(self, text='Assembly type')
        self.label_assembly_type.grid(row=3, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_assembly_type" and register it with the grid geometry manager
        self.combobox_assembly_type = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_assembly_type)
        self.combobox_assembly_type.grid(row=3, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=4, column=2, padx=(0,0), pady=(55,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=4, column=3, padx=(0,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=4, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_assembly_dataset.bind('<<ComboboxSelected>>', self.combobox_assembly_dataset_selected_item)
        self.combobox_assembly_type.bind('<<ComboboxSelected>>', self.combobox_assembly_type_selected_item)

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

        # clear data in "combobox_assembly_dataset"
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')

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

        # load data in "combobox_assembly_dataset"
        self.populate_combobox_assembly_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_assembly_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_dataset" has been selected
        '''

        # get the assembly_dataset dataset identification
        (OK, error_list, self.assembly_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_assembly_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

        # load data in "combobox_assembly_type"
        if self.assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            self.combobox_assembly_type['values'] = ['CONTIGS', 'SCAFFOLDS']
            self.wrapper_assembly_type.set('')
            self.combobox_assembly_type['state'] = 'normal'
        elif self.assembly_dataset_id.startswith(xlib.get_transabyss_code()) or self.assembly_dataset_id.startswith(xlib.get_trinity_code()) or self.assembly_dataset_id.startswith(xlib.get_star_code()) or self.assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or self.assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            self.combobox_assembly_type['values'] = ['NONE']
            self.wrapper_assembly_type.set('NONE')
            self.combobox_assembly_type['state'] = 'disabled'

    #---------------

    def combobox_assembly_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_type" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the creation of the CD-HIT-EST config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xcdhit.get_cd_hit_est_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the CD-HIT-EST config file
        if OK:
            (OK, error_list) = xcdhit.create_cd_hit_est_config_file(self.wrapper_experiment_id.get(), self.assembly_dataset_id, self.wrapper_assembly_type.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the CD-HIT-EST config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xcdhit.get_cd_hit_est_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xcdhit.validate_cd_hit_est_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_cd_hit_est_name())
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
        Close "FormRecreateCdHitEstConfigFile".
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
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')
        self.assembly_dataset_id = None
        self.combobox_assembly_type['values'] = []
        self.wrapper_assembly_type.set('')
        self.combobox_assembly_type['state'] = 'disabled'

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
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_assembly_dataset(self):
        '''
        Populate data in "combobox_assembly_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_assembly_dataset.set('')

        # get the list of the assembly_dataset dataset names
        app_list = [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]
        (OK, error_list, assembly_dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the assembly dataset names in the combobox
        self.combobox_assembly_dataset['values'] = sorted(assembly_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateCdHitEstConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_assembly_dataset.get() != '' and self.wrapper_assembly_type.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateFastQCConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateFastQCConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected and read dataset identification
        self.cluster_name_ant = None
        self.read_dataset_id = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_fastqc_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
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
        Build the graphical user interface of "FormRecreateFastQCConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(45,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(45,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

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
        self.label_fit = tkinter.Label(self, text=' '*10)
        self.label_fit.grid(row=5, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=5, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=5, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
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

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

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
        self.populate_combobox_read_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_read_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read dataset identification
        (OK, error_list, self.read_dataset_id) = xread.get_read_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_read_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # confirm the creation of the FastQC config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xfastqc.get_fastqc_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the FastQC config file
        if OK:
            (OK, error_list) = xfastqc.create_fastqc_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, selected_file_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the FastQC config file corresponding to the environment
        if OK:
            
            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xfastqc.get_fastqc_config_file())
            self.wait_window(dialog_editor)
            
            # validate the config file
            (OK, error_list) = xfastqc.validate_fastqc_config_file(strict=False)
            if OK:
                message = 'The {0} transfer config file is OK.'.format(xlib.get_fastqc_name())
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
        Close "FormRecreateFastQCConfigFile".
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
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
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

    def populate_combobox_experiment_id(self):
        '''
        Populate data in "combobox_experiment_id".
        '''

        # clear the value selected in the combobox
        self.wrapper_experiment_id.set('')

        # initialize the experiment identifications list
        experiment_ids_list = []

        # get the experiment identifications
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

    def populate_combobox_read_dataset(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_dataset.set('')

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateFastQCConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '':
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

class FormRecreateGmapConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateGmapConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_gmap_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_reference_dataset = tkinter.StringVar()
        self.wrapper_reference_dataset.trace('w', self.validate_inputs)
        self.wrapper_reference_file = tkinter.StringVar()
        self.wrapper_reference_file.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_assembly_dataset = tkinter.StringVar()
        self.wrapper_assembly_dataset.trace('w', self.validate_inputs)
        self.wrapper_assembly_type = tkinter.StringVar()
        self.wrapper_assembly_type.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateGmapConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_reference_dataset" and register it with the grid geometry manager
        self.label_reference_dataset = tkinter.Label(self, text='Reference dataset')
        self.label_reference_dataset.grid(row=1, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_reference_dataset" and register it with the grid geometry manager
        self.combobox_reference_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_dataset)
        self.combobox_reference_dataset.grid(row=1, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_reference_file" and register it with the grid geometry manager
        self.label_reference_file = tkinter.Label(self, text='Reference file')
        self.label_reference_file.grid(row=2, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_reference_file" and register it with the grid geometry manager
        self.combobox_reference_file = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_file)
        self.combobox_reference_file.grid(row=2, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=3, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=3, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_assembly_dataset" and register it with the grid geometry manager
        self.label_assembly_dataset = tkinter.Label(self, text='Assembly dataset')
        self.label_assembly_dataset.grid(row=4, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_assembly_dataset" and register it with the grid geometry manager
        self.combobox_assembly_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_assembly_dataset)
        self.combobox_assembly_dataset.grid(row=4, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_assembly_type" and register it with the grid geometry manager
        self.label_assembly_type = tkinter.Label(self, text='Assembly type')
        self.label_assembly_type.grid(row=5, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_assembly_type" and register it with the grid geometry manager
        self.combobox_assembly_type = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_assembly_type)
        self.combobox_assembly_type.grid(row=5, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=6, column=2, padx=(0,0), pady=(40,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=6, column=3, padx=(0,5), pady=(40,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=6, column=4, padx=(5,5), pady=(40,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_reference_dataset.bind('<<ComboboxSelected>>', self.combobox_reference_dataset_selected_item)
        self.combobox_reference_file.bind('<<ComboboxSelected>>', self.combobox_reference_file_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_assembly_dataset.bind('<<ComboboxSelected>>', self.combobox_assembly_dataset_selected_item)
        self.combobox_assembly_type.bind('<<ComboboxSelected>>', self.combobox_assembly_type_selected_item)

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

        # clear data in "combobox_reference_file"
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # clear data in "combobox_assembly_dataset"
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_dataset" has been selected
        '''

        # load data in "combobox_reference_file"
        self.populate_combobox_reference_file()

    #---------------

    def combobox_reference_file_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_file" has been selected
        '''

        pass

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_assembly_dataset"
        self.populate_combobox_assembly_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_assembly_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_dataset" has been selected
        '''

        # get the assembly_dataset dataset identification
        (OK, error_list, self.assembly_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_assembly_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

        # load data in "combobox_assembly_type"
        if self.assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            self.combobox_assembly_type['values'] = ['CONTIGS', 'SCAFFOLDS']
            self.wrapper_assembly_type.set('')
            self.combobox_assembly_type['state'] = 'normal'
        elif self.assembly_dataset_id.startswith(xlib.get_transabyss_code()) or self.assembly_dataset_id.startswith(xlib.get_trinity_code()) or self.assembly_dataset_id.startswith(xlib.get_star_code()) or self.assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or self.assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            self.combobox_assembly_type['values'] = ['NONE']
            self.wrapper_assembly_type.set('NONE')
            self.combobox_assembly_type['state'] = 'disabled'

    #---------------

    def combobox_assembly_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_type" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the creation of the GMAP config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xgmap.get_gmap_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the GMAP config file
        if OK:
            (OK, error_list) = xgmap.create_gmap_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.assembly_dataset_id, self.wrapper_assembly_type.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the GMAP config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xgmap.get_gmap_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xgmap.validate_gmap_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_gmap_name())
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
        Close "FormRecreateGmapConfigFile".
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
        self.combobox_reference_dataset['values'] = []
        self.wrapper_reference_dataset.set('')
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')
        self.assembly_dataset_id = None
        self.combobox_assembly_type['values'] = []
        self.wrapper_assembly_type.set('')
        self.combobox_assembly_type['state'] = 'disabled'

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

    def populate_combobox_reference_dataset(self):
        '''
        Populate data in "combobox_reference_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_dataset.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_dataset_name_list) = xreference.get_reference_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the reference dataset names in the combobox
        self.combobox_reference_dataset['values'] = sorted(reference_dataset_name_list)

    #---------------

    def populate_combobox_reference_file(self):
        '''
        Populate data in "combobox_reference_file".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_file.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_file_name_list) = xreference.get_reference_file_name_list(self.wrapper_cluster_name.get(), self.wrapper_reference_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the reference dataset names in the combobox
        self.combobox_reference_file['values'] = sorted(reference_file_name_list)

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
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_assembly_dataset(self):
        '''
        Populate data in "combobox_assembly_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_assembly_dataset.set('')

        # get the list of the assembly_dataset dataset names
        app_list = [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]
        (OK, error_list, assembly_dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the assembly dataset names in the combobox
        self.combobox_assembly_dataset['values'] = sorted(assembly_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateGmapConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_reference_dataset.get() != '' and self.wrapper_reference_file.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_assembly_dataset.get() != '' and self.wrapper_assembly_type.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateInsilicoReadNormalizationConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateInsilicoReadNormalizationConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected, read dataset identification and read type
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_insilico_read_normalization_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateInsilicoReadNormalizationConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=2, column=0, padx=(15,5), pady=(43,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=2, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=3, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=3, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=5, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=5, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=6, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=6, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=7, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=7, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=8, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=8, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=8, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)

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

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

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

        # load data in "combobox_read_dataset"
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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state']='normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state']='normal'

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # confirm the creation of the insilico_read_normalization config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xtrinity.get_insilico_read_normalization_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the insilico_read_normalization config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xtrinity.create_insilico_read_normalization_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, selected_file_list, None)
            elif self.read_type == 'PE':
                (OK, error_list) = xtrinity.create_insilico_read_normalization_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, file_1_list, file_2_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the insilico_read_normalization config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xtrinity.get_insilico_read_normalization_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xtrinity.validate_insilico_read_normalization_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_insilico_read_normalization_name())
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
        Close "FormRecreateInsilicoReadNormalizationConfigFile".
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
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

    def populate_combobox_read_dataset(self):
        '''
        Populate data in "combobox_read_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_dataset.set('')

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateInsilicoReadNormalizationConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != ''):
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

class FormRecreateQuastConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateQuastConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_quast_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_reference_dataset = tkinter.StringVar()
        self.wrapper_reference_dataset.trace('w', self.validate_inputs)
        self.wrapper_reference_file = tkinter.StringVar()
        self.wrapper_reference_file.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_assembly_dataset = tkinter.StringVar()
        self.wrapper_assembly_dataset.trace('w', self.validate_inputs)
        self.wrapper_assembly_type = tkinter.StringVar()
        self.wrapper_assembly_type.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateQuastConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_reference_dataset" and register it with the grid geometry manager
        self.label_reference_dataset = tkinter.Label(self, text='Reference dataset')
        self.label_reference_dataset.grid(row=1, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_reference_dataset" and register it with the grid geometry manager
        self.combobox_reference_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_dataset)
        self.combobox_reference_dataset.grid(row=1, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_reference_file" and register it with the grid geometry manager
        self.label_reference_file = tkinter.Label(self, text='Reference file')
        self.label_reference_file.grid(row=2, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_reference_file" and register it with the grid geometry manager
        self.combobox_reference_file = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_file)
        self.combobox_reference_file.grid(row=2, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=3, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=3, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_assembly_dataset" and register it with the grid geometry manager
        self.label_assembly_dataset = tkinter.Label(self, text='Assembly dataset')
        self.label_assembly_dataset.grid(row=4, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_assembly_dataset" and register it with the grid geometry manager
        self.combobox_assembly_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_assembly_dataset)
        self.combobox_assembly_dataset.grid(row=4, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_assembly_type" and register it with the grid geometry manager
        self.label_assembly_type = tkinter.Label(self, text='Assembly type')
        self.label_assembly_type.grid(row=5, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_assembly_type" and register it with the grid geometry manager
        self.combobox_assembly_type = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_assembly_type)
        self.combobox_assembly_type.grid(row=5, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=6, column=2, padx=(0,0), pady=(40,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=6, column=3, padx=(0,5), pady=(40,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=6, column=4, padx=(5,5), pady=(40,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_reference_dataset.bind('<<ComboboxSelected>>', self.combobox_reference_dataset_selected_item)
        self.combobox_reference_file.bind('<<ComboboxSelected>>', self.combobox_reference_file_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_assembly_dataset.bind('<<ComboboxSelected>>', self.combobox_assembly_dataset_selected_item)
        self.combobox_assembly_type.bind('<<ComboboxSelected>>', self.combobox_assembly_type_selected_item)

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

        # clear data in "combobox_reference_file"
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # clear data in "combobox_assembly_dataset"
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_dataset" has been selected
        '''

        # load data in "combobox_reference_file"
        if self.wrapper_reference_dataset.get() == 'NONE':
            self.combobox_reference_file['values'] = ['NONE']
            self.wrapper_reference_file.set('NONE')
        else:
            self.populate_combobox_reference_file()

    #---------------

    def combobox_reference_file_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_file" has been selected
        '''

        pass

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_assembly_dataset"
        self.populate_combobox_assembly_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_assembly_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_dataset" has been selected
        '''

        # get the assembly_dataset dataset identification
        (OK, error_list, self.assembly_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_assembly_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

        # load data in "combobox_assembly_type"
        if self.assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            self.combobox_assembly_type['values'] = ['CONTIGS', 'SCAFFOLDS']
            self.wrapper_assembly_type.set('')
            self.combobox_assembly_type['state'] = 'normal'
        elif self.assembly_dataset_id.startswith(xlib.get_transabyss_code()) or self.assembly_dataset_id.startswith(xlib.get_trinity_code()) or self.assembly_dataset_id.startswith(xlib.get_star_code()) or self.assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or self.assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            self.combobox_assembly_type['values'] = ['NONE']
            self.wrapper_assembly_type.set('NONE')
            self.combobox_assembly_type['state'] = 'disabled'

    #---------------

    def combobox_assembly_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_type" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the creation of the QUAST config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xquast.get_quast_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the QUAST config file
        if OK:
            (OK, error_list) = xquast.create_quast_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.assembly_dataset_id, self.wrapper_assembly_type.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the QUAST config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xquast.get_quast_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xquast.validate_quast_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_quast_name())
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
        Close "FormRecreateQuastConfigFile".
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
        self.combobox_reference_dataset['values'] = []
        self.wrapper_reference_dataset.set('')
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')
        self.assembly_dataset_id = None
        self.combobox_assembly_type['values'] = []
        self.wrapper_assembly_type.set('')
        self.combobox_assembly_type['state'] = 'disabled'

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

    def populate_combobox_reference_dataset(self):
        '''
        Populate data in "combobox_reference_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_dataset.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_dataset_name_list) = xreference.get_reference_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)
        reference_dataset_name_list.append('NONE')

        # load the reference dataset names in the combobox
        self.combobox_reference_dataset['values'] = sorted(reference_dataset_name_list)

    #---------------

    def populate_combobox_reference_file(self):
        '''
        Populate data in "combobox_reference_file".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_file.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_file_name_list) = xreference.get_reference_file_name_list(self.wrapper_cluster_name.get(), self.wrapper_reference_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the reference dataset names in the combobox
        self.combobox_reference_file['values'] = sorted(reference_file_name_list)

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
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_assembly_dataset(self):
        '''
        Populate data in "combobox_assembly_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_assembly_dataset.set('')

        # get the list of the assembly_dataset dataset names
        app_list = [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]
        (OK, error_list, assembly_dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the assembly dataset names in the combobox
        self.combobox_assembly_dataset['values'] = sorted(assembly_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateQuastConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_reference_dataset.get() != '' and self.wrapper_reference_file.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_assembly_dataset.get() != '' and self.wrapper_assembly_type.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateRefEvalConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateRefEvaltConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_ref_eval_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_reference_dataset = tkinter.StringVar()
        self.wrapper_reference_dataset.trace('w', self.validate_inputs)
        self.wrapper_reference_file = tkinter.StringVar()
        self.wrapper_reference_file.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)
        self.wrapper_assembly_dataset = tkinter.StringVar()
        self.wrapper_assembly_dataset.trace('w', self.validate_inputs)
        self.wrapper_assembly_type = tkinter.StringVar()
        self.wrapper_assembly_type.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateRefEvaltConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(30,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(30,5), sticky='w')

        # create "label_reference_dataset" and register it with the grid geometry manager
        self.label_reference_dataset = tkinter.Label(self, text='Reference dataset')
        self.label_reference_dataset.grid(row=1, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_reference_dataset" and register it with the grid geometry manager
        self.combobox_reference_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_dataset)
        self.combobox_reference_dataset.grid(row=1, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_reference_file" and register it with the grid geometry manager
        self.label_reference_file = tkinter.Label(self, text='Reference file')
        self.label_reference_file.grid(row=2, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_reference_file" and register it with the grid geometry manager
        self.combobox_reference_file = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_file)
        self.combobox_reference_file.grid(row=2, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=3, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=3, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=4, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=4, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=5, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=5, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=5, column=2, columnspan=3, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=6, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=6, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=7, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=7, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=8, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=8, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_assembly_dataset" and register it with the grid geometry manager
        self.label_assembly_dataset = tkinter.Label(self, text='Assembly dataset')
        self.label_assembly_dataset.grid(row=9, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_assembly_dataset" and register it with the grid geometry manager
        self.combobox_assembly_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_assembly_dataset)
        self.combobox_assembly_dataset.grid(row=9, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_assembly_type" and register it with the grid geometry manager
        self.label_assembly_type = tkinter.Label(self, text='Assembly type')
        self.label_assembly_type.grid(row=10, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_assembly_type" and register it with the grid geometry manager
        self.combobox_assembly_type = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_assembly_type)
        self.combobox_assembly_type.grid(row=10, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=11, column=2, padx=(0,0), pady=(15,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=11, column=3, padx=(0,5), pady=(15,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=11, column=4, padx=(5,5), pady=(15,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_reference_dataset.bind('<<ComboboxSelected>>', self.combobox_reference_dataset_selected_item)
        self.combobox_reference_file.bind('<<ComboboxSelected>>', self.combobox_reference_file_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)
        self.combobox_assembly_dataset.bind('<<ComboboxSelected>>', self.combobox_assembly_dataset_selected_item)
        self.combobox_assembly_type.bind('<<ComboboxSelected>>', self.combobox_assembly_type_selected_item)

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

        # clear data in "combobox_reference_file"
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

        # clear data in "combobox_assembly_dataset"
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_dataset" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_reference_file"
        if self.wrapper_reference_dataset.get() == 'NONE':
            self.combobox_reference_file['values'] = ['NONE']
            self.wrapper_reference_file.set('NONE')
        else:
            self.populate_combobox_reference_file()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_file_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_file" has been selected
        '''

        pass

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_read_dataset"
        self.populate_combobox_read_dataset()

        # load data in "combobox_assembly_dataset"
        self.populate_combobox_assembly_dataset()

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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state'] = 'normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state'] = 'normal'

    #---------------

    def combobox_assembly_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_dataset" has been selected
        '''

        # get the assembly dataset identification
        (OK, error_list, self.assembly_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_assembly_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

        # load data in "combobox_assembly_type"
        if self.assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            self.combobox_assembly_type['values'] = ['CONTIGS', 'SCAFFOLDS']
            self.wrapper_assembly_type.set('')
            self.combobox_assembly_type['state'] = 'normal'
        elif self.assembly_dataset_id.startswith(xlib.get_transabyss_code()) or self.assembly_dataset_id.startswith(xlib.get_trinity_code()) or self.assembly_dataset_id.startswith(xlib.get_star_code()) or self.assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or self.assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            self.combobox_assembly_type['values'] = ['NONE']
            self.wrapper_assembly_type.set('NONE')
            self.combobox_assembly_type['state'] = 'disabled'

    #---------------

    def combobox_assembly_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_type" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # confirm the creation of the REF-EVAL config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xdetonate.get_ref_eval_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the REF-EVAL config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xdetonate.create_ref_eval_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.read_dataset_id, self.read_type, selected_file_list, None, self.assembly_dataset_id, self.wrapper_assembly_type.get())
            elif self.read_type == 'PE':
                (OK, error_list) = xdetonate.create_ref_eval_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.read_dataset_id, self.read_type, file_1_list, file_2_list, self.assembly_dataset_id, self.wrapper_assembly_type.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the REF-EVAL config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xdetonate.get_ref_eval_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xdetonate.validate_ref_eval_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_ref_eval_name())
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
        Close "FormRecreateRefEvaltConfigFile".
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
        self.combobox_reference_dataset['values'] = []
        self.wrapper_reference_dataset.set('')
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')
        self.assembly_dataset_id = None
        self.combobox_assembly_type['values'] = []
        self.wrapper_assembly_type.set('')
        self.combobox_assembly_type['state'] = 'disabled'

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

    def populate_combobox_reference_dataset(self):
        '''
        Populate data in "combobox_reference_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_dataset.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_dataset_name_list) = xreference.get_reference_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)
        reference_dataset_name_list.append('NONE')

        # load the reference dataset names in the combobox
        self.combobox_reference_dataset['values'] = sorted(reference_dataset_name_list)

    #---------------

    def populate_combobox_reference_file(self):
        '''
        Populate data in "combobox_reference_file".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_file.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_file_name_list) = xreference.get_reference_file_name_list(self.wrapper_cluster_name.get(), self.wrapper_reference_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the reference dataset names in the combobox
        self.combobox_reference_file['values'] = sorted(reference_file_name_list)

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def populate_combobox_assembly_dataset(self):
        '''
        Populate data in "combobox_assembly_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_assembly_dataset.set('')

        # get the list of the assembly dataset names
        app_list = [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]
        (OK, error_list, assembly_dataset_name_list) = xresult.get_assembly_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the assembly dataset names in the combobox
        self.combobox_assembly_dataset['values'] = sorted(assembly_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateRefEvaltConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_reference_dataset.get() != '' and self.wrapper_reference_file.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != '') and self.wrapper_assembly_dataset.get() != '':
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
            self.label_file_pattern_warning['text'] = 'Invalid pattern.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'A pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateRnaQuastConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateRnaQuastConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_rnaquast_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_reference_dataset = tkinter.StringVar()
        self.wrapper_reference_dataset.trace('w', self.validate_inputs)
        self.wrapper_reference_file = tkinter.StringVar()
        self.wrapper_reference_file.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)
        self.wrapper_assembly_dataset = tkinter.StringVar()
        self.wrapper_assembly_dataset.trace('w', self.validate_inputs)
        self.wrapper_assembly_type = tkinter.StringVar()
        self.wrapper_assembly_type.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateRnaQuastConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(30,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(30,5), sticky='w')

        # create "label_reference_dataset" and register it with the grid geometry manager
        self.label_reference_dataset = tkinter.Label(self, text='Reference dataset')
        self.label_reference_dataset.grid(row=1, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_reference_dataset" and register it with the grid geometry manager
        self.combobox_reference_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_dataset)
        self.combobox_reference_dataset.grid(row=1, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_reference_file" and register it with the grid geometry manager
        self.label_reference_file = tkinter.Label(self, text='Reference file')
        self.label_reference_file.grid(row=2, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_reference_file" and register it with the grid geometry manager
        self.combobox_reference_file = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_file)
        self.combobox_reference_file.grid(row=2, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=3, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=3, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=4, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=4, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=5, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=5, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=5, column=2, columnspan=3, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=6, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=6, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=7, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=7, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=8, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=8, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_assembly_dataset" and register it with the grid geometry manager
        self.label_assembly_dataset = tkinter.Label(self, text='Assembly dataset')
        self.label_assembly_dataset.grid(row=9, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_assembly_dataset" and register it with the grid geometry manager
        self.combobox_assembly_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_assembly_dataset)
        self.combobox_assembly_dataset.grid(row=9, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_assembly_type" and register it with the grid geometry manager
        self.label_assembly_type = tkinter.Label(self, text='Assembly type')
        self.label_assembly_type.grid(row=10, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_assembly_type" and register it with the grid geometry manager
        self.combobox_assembly_type = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_assembly_type)
        self.combobox_assembly_type.grid(row=10, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=11, column=2, padx=(0,0), pady=(15,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=11, column=3, padx=(0,5), pady=(15,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=11, column=4, padx=(5,5), pady=(15,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_reference_dataset.bind('<<ComboboxSelected>>', self.combobox_reference_dataset_selected_item)
        self.combobox_reference_file.bind('<<ComboboxSelected>>', self.combobox_reference_file_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)
        self.combobox_assembly_dataset.bind('<<ComboboxSelected>>', self.combobox_assembly_dataset_selected_item)
        self.combobox_assembly_type.bind('<<ComboboxSelected>>', self.combobox_assembly_type_selected_item)

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

        # clear data in "combobox_reference_file"
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

        # clear data in "combobox_assembly_dataset"
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_dataset" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_reference_file"
        if self.wrapper_reference_dataset.get() == 'NONE':
            self.combobox_reference_file['values'] = ['NONE']
            self.wrapper_reference_file.set('NONE')
        else:
            self.populate_combobox_reference_file()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_file_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_file" has been selected
        '''

        pass

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_read_dataset"
        self.populate_combobox_read_dataset()

        # load data in "combobox_assembly_dataset"
        self.populate_combobox_assembly_dataset()

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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state'] = 'normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state'] = 'normal'

    #---------------

    def combobox_assembly_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_dataset" has been selected
        '''

        # get the assembly dataset identification
        (OK, error_list, self.assembly_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_assembly_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

        # load data in "combobox_assembly_type"
        if self.assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            self.combobox_assembly_type['values'] = ['CONTIGS', 'SCAFFOLDS']
            self.wrapper_assembly_type.set('')
            self.combobox_assembly_type['state'] = 'normal'
        elif self.assembly_dataset_id.startswith(xlib.get_transabyss_code()) or self.assembly_dataset_id.startswith(xlib.get_trinity_code()) or self.assembly_dataset_id.startswith(xlib.get_star_code()) or self.assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or self.assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            self.combobox_assembly_type['values'] = ['NONE']
            self.wrapper_assembly_type.set('NONE')
            self.combobox_assembly_type['state'] = 'disabled'

    #---------------

    def combobox_assembly_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_type" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # confirm the creation of the rnaQUAST config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xrnaquast.get_rnaquast_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the rnaQUAST config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xrnaquast.create_rnaquast_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.read_dataset_id, self.read_type, selected_file_list, None, self.assembly_dataset_id, self.wrapper_assembly_type.get())
            elif self.read_type == 'PE':
                (OK, error_list) = xrnaquast.create_rnaquast_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.read_dataset_id, self.read_type, file_1_list, file_2_list, self.assembly_dataset_id, self.wrapper_assembly_type.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the rnaQUAST config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xrnaquast.get_rnaquast_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xrnaquast.validate_rnaquast_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_rnaquast_name())
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
        Close "FormRecreateRnaQuastConfigFile".
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
        self.combobox_reference_dataset['values'] = []
        self.wrapper_reference_dataset.set('')
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')
        self.assembly_dataset_id = None
        self.combobox_assembly_type['values'] = []
        self.wrapper_assembly_type.set('')
        self.combobox_assembly_type['state'] = 'disabled'

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

    def populate_combobox_reference_dataset(self):
        '''
        Populate data in "combobox_reference_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_dataset.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_dataset_name_list) = xreference.get_reference_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)
        reference_dataset_name_list.append('NONE')

        # load the reference dataset names in the combobox
        self.combobox_reference_dataset['values'] = sorted(reference_dataset_name_list)

    #---------------

    def populate_combobox_reference_file(self):
        '''
        Populate data in "combobox_reference_file".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_file.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_file_name_list) = xreference.get_reference_file_name_list(self.wrapper_cluster_name.get(), self.wrapper_reference_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the reference dataset names in the combobox
        self.combobox_reference_file['values'] = sorted(reference_file_name_list)

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def populate_combobox_assembly_dataset(self):
        '''
        Populate data in "combobox_assembly_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_assembly_dataset.set('')

        # get the list of the assembly dataset names
        app_list = [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]
        (OK, error_list, assembly_dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the assembly dataset names in the combobox
        self.combobox_assembly_dataset['values'] = sorted(assembly_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateRnaQuastConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_reference_dataset.get() != '' and self.wrapper_reference_file.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != '') and self.wrapper_assembly_dataset.get() != '':
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
            self.label_file_pattern_warning['text'] = 'Invalid pattern.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'A pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateRsemEvalConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateRsemEvalConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_rsem_eval_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)
        self.wrapper_assembly_dataset = tkinter.StringVar()
        self.wrapper_assembly_dataset.trace('w', self.validate_inputs)
        self.wrapper_assembly_type = tkinter.StringVar()
        self.wrapper_assembly_type.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateRsemEvalConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(50,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(50,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(20,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=2, column=0, padx=(15,5), pady=(20,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=2, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=3, column=0, padx=(15,5), pady=(20,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=3, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=3, column=2, columnspan=3, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=4, column=0, padx=(15,5), pady=(20,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=4, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=5, column=0, padx=(15,5), pady=(20,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=5, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=6, column=0, padx=(15,5), pady=(20,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=6, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_assembly_dataset" and register it with the grid geometry manager
        self.label_assembly_dataset = tkinter.Label(self, text='Assembly dataset')
        self.label_assembly_dataset.grid(row=7, column=0, padx=(15,5), pady=(20,5), sticky='e')

        # create "combobox_assembly_dataset" and register it with the grid geometry manager
        self.combobox_assembly_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_assembly_dataset)
        self.combobox_assembly_dataset.grid(row=7, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_assembly_type" and register it with the grid geometry manager
        self.label_assembly_type = tkinter.Label(self, text='Assembly type')
        self.label_assembly_type.grid(row=8, column=0, padx=(15,5), pady=(20,5), sticky='e')

        # create "combobox_assembly_type" and register it with the grid geometry manager
        self.combobox_assembly_type = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_assembly_type)
        self.combobox_assembly_type.grid(row=8, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=9, column=2, padx=(0,0), pady=(20,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=9, column=3, padx=(0,5), pady=(20,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=9, column=4, padx=(5,5), pady=(20,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)
        self.combobox_assembly_dataset.bind('<<ComboboxSelected>>', self.combobox_assembly_dataset_selected_item)
        self.combobox_assembly_type.bind('<<ComboboxSelected>>', self.combobox_assembly_type_selected_item)

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

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

        # clear data in "combobox_assembly_dataset"
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')

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

        # load data in "combobox_read_dataset"
        self.populate_combobox_read_dataset()

        # load data in "combobox_assembly_dataset"
        self.populate_combobox_assembly_dataset()

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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state'] = 'normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state'] = 'normal'

    #---------------

    def combobox_assembly_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_dataset" has been selected
        '''

        # get the assembly dataset identification
        (OK, error_list, self.assembly_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_assembly_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

        # load data in "combobox_assembly_type"
        if self.assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            self.combobox_assembly_type['values'] = ['CONTIGS', 'SCAFFOLDS']
            self.wrapper_assembly_type.set('')
            self.combobox_assembly_type['state'] = 'normal'
        elif self.assembly_dataset_id.startswith(xlib.get_transabyss_code()) or self.assembly_dataset_id.startswith(xlib.get_trinity_code()) or self.assembly_dataset_id.startswith(xlib.get_star_code()) or self.assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or self.assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            self.combobox_assembly_type['values'] = ['NONE']
            self.wrapper_assembly_type.set('NONE')
            self.combobox_assembly_type['state'] = 'disabled'

    #---------------

    def combobox_assembly_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_type" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # confirm the creation of the RSEM-EVAL config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xdetonate.get_rsem_eval_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the RSEM-EVAL config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xdetonate.create_rsem_eval_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, selected_file_list, None, self.assembly_dataset_id, self.wrapper_assembly_type.get())
            elif self.read_type == 'PE':
                (OK, error_list) = xdetonate.create_rsem_eval_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, file_1_list, file_2_list, self.assembly_dataset_id, self.wrapper_assembly_type.get())                 
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the RSEM-EVAL config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xdetonate.get_rsem_eval_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xdetonate.validate_rsem_eval_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_rsem_eval_name())
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
        Close "FormRecreateRsemEvalConfigFile".
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
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')
        self.assembly_dataset_id = None
        self.combobox_assembly_type['values'] = []
        self.wrapper_assembly_type.set('')
        self.combobox_assembly_type['state'] = 'disabled'

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def populate_combobox_assembly_dataset(self):
        '''
        Populate data in "combobox_assembly_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_assembly_dataset.set('')

        # get the list of the assembly dataset names
        app_list = [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]
        (OK, error_list, assembly_dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the assembly dataset names in the combobox
        self.combobox_assembly_dataset['values'] = sorted(assembly_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateRsemEvalConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != '') and self.wrapper_assembly_dataset.get() != '':
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
            self.label_file_pattern_warning['text'] = 'Invalid pattern.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'A pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateSoapdenovoTransConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateSoapdenovoTransConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected, read dataset identification and read type
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_soapdenovotrans_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateSoapdenovoTransConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=2, column=0, padx=(15,5), pady=(43,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=2, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=3, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=3, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=5, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=5, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=6, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=6, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=7, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=7, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=8, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=8, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=8, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)

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

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

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

        # load data in "combobox_read_dataset"
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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state']='normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state']='normal'

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # confirm the creation of the SOAPdenovo-Trans config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xsoapdenovotrans.get_soapdenovotrans_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the SOAPdenovo-Trans config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xsoapdenovotrans.create_soapdenovotrans_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, selected_file_list, None)
            elif self.read_type == 'PE':
                (OK, error_list) = xsoapdenovotrans.create_soapdenovotrans_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, file_1_list, file_2_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the SOAPdenovo-Trans config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xsoapdenovotrans.get_soapdenovotrans_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xsoapdenovotrans.validate_soapdenovotrans_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_soapdenovotrans_name())
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
        Close "FormRecreateSoapdenovoTransConfigFile".
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
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

    def populate_combobox_read_dataset(self):
        '''
        Populate data in "combobox_read_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_dataset.set('')

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateSoapdenovoTransConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != ''):
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

class FormRecreateSTARConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateSTARConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_star_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_reference_dataset = tkinter.StringVar()
        self.wrapper_reference_dataset.trace('w', self.validate_inputs)
        self.wrapper_reference_file = tkinter.StringVar()
        self.wrapper_reference_file.trace('w', self.validate_inputs)
        self.wrapper_gtf_file = tkinter.StringVar()
        self.wrapper_gtf_file.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateSTARConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(50,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(50,5), sticky='w')

        # create "label_reference_dataset" and register it with the grid geometry manager
        self.label_reference_dataset = tkinter.Label(self, text='Reference dataset')
        self.label_reference_dataset.grid(row=1, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_reference_dataset" and register it with the grid geometry manager
        self.combobox_reference_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_dataset)
        self.combobox_reference_dataset.grid(row=1, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_reference_file" and register it with the grid geometry manager
        self.label_reference_file = tkinter.Label(self, text='Reference file')
        self.label_reference_file.grid(row=2, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_reference_file" and register it with the grid geometry manager
        self.combobox_reference_file = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_file)
        self.combobox_reference_file.grid(row=2, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_gtf_file" and register it with the grid geometry manager
        self.label_gtf_file = tkinter.Label(self, text='GTF file')
        self.label_gtf_file.grid(row=3, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_gtf_file" and register it with the grid geometry manager
        self.combobox_gtf_file = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_gtf_file)
        self.combobox_gtf_file.grid(row=3, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=4, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=4, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=5, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=5, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=6, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=6, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=6, column=2, columnspan=3, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=7, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=7, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=8, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=8, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=9, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=9, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=10, column=2, padx=(0,0), pady=(15,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=10, column=3, padx=(0,5), pady=(15,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=10, column=4, padx=(5,5), pady=(15,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_reference_dataset.bind('<<ComboboxSelected>>', self.combobox_reference_dataset_selected_item)
        self.combobox_reference_file.bind('<<ComboboxSelected>>', self.combobox_reference_file_selected_item)
        self.combobox_gtf_file.bind('<<ComboboxSelected>>', self.combobox_gtf_file_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)

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

        # clear data in "combobox_reference_file"
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')

        # clear data in "combobox_gtf_file"
        self.combobox_gtf_file['values'] = []
        self.wrapper_gtf_file.set('')

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_dataset" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_reference_file"
        self.populate_combobox_reference_file()

        # load data in "combobox_gtf_file"
        self.populate_combobox_gtf_file()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_file_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_file" has been selected
        '''

        pass

    #---------------

    def combobox_gtf_file_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_gtf_file" has been selected
        '''

        pass

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_read_dataset"
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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state'] = 'normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state'] = 'normal'

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # verify there is only one library
        if OK:
            if self.read_type == 'SE' and len(selected_file_list) != 1 or self.read_type == 'PE' and len(file_1_list) != 1:
                message = 'ERROR: Two or more libraries are selected and only one is allowed.'
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                OK = False

        # confirm the creation of the STAR config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xstar.get_star_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the STAR config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xstar.create_star_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.wrapper_gtf_file.get(), self.read_dataset_id, self.read_type, selected_file_list[0], None)
            elif self.read_type == 'PE':
                (OK, error_list) = xstar.create_star_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.wrapper_gtf_file.get(), self.read_dataset_id, self.read_type, file_1_list[0], file_2_list[0])
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the STAR config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xstar.get_star_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xstar.validate_star_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_star_name())
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
        Close "FormRecreateSTARConfigFile".
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
        self.combobox_reference_dataset['values'] = []
        self.wrapper_reference_dataset.set('')
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')
        self.combobox_gtf_file['values'] = []
        self.wrapper_gtf_file.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'

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

    def populate_combobox_reference_dataset(self):
        '''
        Populate data in "combobox_reference_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_dataset.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_dataset_name_list) = xreference.get_reference_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the reference dataset names in the combobox
        self.combobox_reference_dataset['values'] = sorted(reference_dataset_name_list)

    #---------------

    def populate_combobox_reference_file(self):
        '''
        Populate data in "combobox_reference_file".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_file.set('')

        # get the list of the reference file names
        (OK, error_list, reference_file_name_list) = xreference.get_reference_file_name_list(self.wrapper_cluster_name.get(), self.wrapper_reference_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the reference file names in the combobox
        self.combobox_reference_file['values'] = sorted(reference_file_name_list)

    #---------------

    def populate_combobox_gtf_file(self):
        '''
        Populate data in "combobox_gtf_file".
        '''

        # clear the value selected in the combobox
        self.wrapper_gtf_file.set('')

        # get the list of the GTF file names
        (OK, error_list, gtf_file_name_list) = xreference.get_reference_file_name_list(self.wrapper_cluster_name.get(), self.wrapper_reference_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the GTF file names in the combobox
        self.combobox_gtf_file['values'] = sorted(gtf_file_name_list)

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateSTARConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_reference_dataset.get() != '' and self.wrapper_reference_file.get() != '' and self.wrapper_gtf_file.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != ''):
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
            self.label_file_pattern_warning['text'] = 'Invalid pattern.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'A pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateTransAbyssConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateTransAbyssConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected, read dataset identification and read type
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_transabyss_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateTransAbyssConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=2, column=0, padx=(15,5), pady=(43,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=2, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=3, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=3, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=5, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=5, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=6, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=6, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=7, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=7, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=8, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=8, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=8, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)

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

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

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

        # load data in "combobox_read_dataset"
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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state']='normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state']='normal'

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # confirm the creation of the Trans-ABySS config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xtransabyss.get_transabyss_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the Trans-ABySS config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xtransabyss.create_transabyss_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, selected_file_list, None)
            elif self.read_type == 'PE':
                (OK, error_list) = xtransabyss.create_transabyss_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, file_1_list, file_2_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the Trans-ABySS config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xtransabyss.get_transabyss_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xtransabyss.validate_transabyss_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_transabyss_name())
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
        Close "FormRecreateTransAbyssConfigFile".
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
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

    def populate_combobox_read_dataset(self):
        '''
        Populate data in "combobox_read_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_dataset.set('')

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateTransAbyssConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != ''):
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

class FormRecreateTranscriptFilterConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateTranscriptFilterConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_transcript_filter_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_rsem_eval_dataset = tkinter.StringVar()
        self.wrapper_rsem_eval_dataset.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateTranscriptFilterConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_rsem_eval_dataset" and register it with the grid geometry manager
        self.label_rsem_eval_dataset = tkinter.Label(self, text='RSEM-EVAL dataset')
        self.label_rsem_eval_dataset.grid(row=2, column=0, padx=(15,5), pady=(55,5), sticky='e')

        # create "combobox_rsem_eval_dataset" and register it with the grid geometry manager
        self.combobox_rsem_eval_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_rsem_eval_dataset)
        self.combobox_rsem_eval_dataset.grid(row=2, column=1, padx=(5,5), pady=(55,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=3, column=2, padx=(0,0), pady=(55,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=3, column=3, padx=(0,5), pady=(55,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=3, column=4, padx=(5,5), pady=(55,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_rsem_eval_dataset.bind('<<ComboboxSelected>>', self.combobox_rsem_eval_dataset_selected_item)

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

        # clear data in "combobox_rsem_eval_dataset"
        self.combobox_rsem_eval_dataset['values'] = []
        self.wrapper_rsem_eval_dataset.set('')

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

        # load data in "combobox_rsem_eval_dataset"
        self.populate_combobox_rsem_eval_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_rsem_eval_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_rsem_eval_dataset" has been selected
        '''

        # get the RSEM-EVAL dataset identification
        (OK, error_list, self.rsem_eval_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_rsem_eval_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the creation of the transcript-filter config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xngshelper.get_transcript_filter_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the transcript-filter config file
        if OK:
            (OK, error_list) = xngshelper.create_transcript_filter_config_file(self.wrapper_experiment_id.get(),  self.rsem_eval_dataset_id)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the transcript-filter config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xngshelper.get_transcript_filter_config_file())
            self.wait_window(dialog_editor)

            # validate the transcript-filter config file
            (OK, error_list) = xngshelper.validate_transcript_filter_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_transcript_filter_name())
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
        Close "FormRecreateTranscriptFilterConfigFile".
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
        self.combobox_rsem_eval_dataset['values'] = []
        self.wrapper_rsem_eval_dataset.set('')
        self.rsem_eval_dataset_id = None

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
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_rsem_eval_dataset(self):
        '''
        Populate data in "combobox_rsem_eval_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_rsem_eval_dataset.set('')

        # get the list of the RSEM-EVAL dataset names
        app_list = [xlib.get_rsem_eval_code()]
        (OK, error_list, rsem_eval_dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the RSEM-EVAL dataset names in the combobox
        self.combobox_rsem_eval_dataset['values'] = sorted(rsem_eval_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateTranscriptFilterConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_rsem_eval_dataset.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateTranscriptomeBlastxConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateTranscriptomeBlastxConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_transcriptome_blastx_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_database_dataset = tkinter.StringVar()
        self.wrapper_database_dataset.trace('w', self.validate_inputs)
        self.wrapper_protein_database_name = tkinter.StringVar()
        self.wrapper_protein_database_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_assembly_dataset = tkinter.StringVar()
        self.wrapper_assembly_dataset.trace('w', self.validate_inputs)
        self.wrapper_assembly_type = tkinter.StringVar()
        self.wrapper_assembly_type.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateTranscriptomeBlastxConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(75,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(75,5), sticky='w')

        # create "label_database_dataset" and register it with the grid geometry manager
        self.label_database_dataset = tkinter.Label(self, text='Database dataset')
        self.label_database_dataset.grid(row=1, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_database_dataset" and register it with the grid geometry manager
        self.combobox_database_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_database_dataset)
        self.combobox_database_dataset.grid(row=1, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_protein_database_name" and register it with the grid geometry manager
        self.label_protein_database_name = tkinter.Label(self, text='Protein database')
        self.label_protein_database_name.grid(row=2, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_protein_database_name" and register it with the grid geometry manager
        self.combobox_protein_database_name = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_protein_database_name)
        self.combobox_protein_database_name.grid(row=2, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=3, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=3, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_assembly_dataset" and register it with the grid geometry manager
        self.label_assembly_dataset = tkinter.Label(self, text='Assembly dataset')
        self.label_assembly_dataset.grid(row=4, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_assembly_dataset" and register it with the grid geometry manager
        self.combobox_assembly_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_assembly_dataset)
        self.combobox_assembly_dataset.grid(row=4, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_assembly_type" and register it with the grid geometry manager
        self.label_assembly_type = tkinter.Label(self, text='Assembly type')
        self.label_assembly_type.grid(row=5, column=0, padx=(15,5), pady=(40,5), sticky='e')

        # create "combobox_assembly_type" and register it with the grid geometry manager
        self.combobox_assembly_type = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_assembly_type)
        self.combobox_assembly_type.grid(row=5, column=1, padx=(5,5), pady=(40,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=6, column=2, padx=(0,0), pady=(40,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=6, column=3, padx=(0,5), pady=(40,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=6, column=4, padx=(5,5), pady=(40,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_database_dataset.bind('<<ComboboxSelected>>', self.combobox_database_dataset_selected_item)
        self.combobox_protein_database_name.bind('<<ComboboxSelected>>', self.combobox_protein_database_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_assembly_dataset.bind('<<ComboboxSelected>>', self.combobox_assembly_dataset_selected_item)
        self.combobox_assembly_type.bind('<<ComboboxSelected>>', self.combobox_assembly_type_selected_item)

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

        # clear data in "combobox_protein_database_name"
        self.combobox_protein_database_name['values'] = []
        self.wrapper_protein_database_name.set('')

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # clear data in "combobox_assembly_dataset"
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_database_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_database_dataset" has been selected
        '''

        # load data in "combobox_protein_database_name"
        self.populate_combobox_protein_database_name()

    #---------------

    def combobox_protein_database_name_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_protein_database_name" has been selected
        '''

        pass

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_assembly_dataset"
        self.populate_combobox_assembly_dataset()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_assembly_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_dataset" has been selected
        '''

        # get the assembly_dataset dataset identification
        (OK, error_list, self.assembly_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_assembly_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

        # load data in "combobox_assembly_type"
        if self.assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            self.combobox_assembly_type['values'] = ['CONTIGS', 'SCAFFOLDS']
            self.wrapper_assembly_type.set('')
            self.combobox_assembly_type['state'] = 'normal'
        elif self.assembly_dataset_id.startswith(xlib.get_transabyss_code()) or self.assembly_dataset_id.startswith(xlib.get_trinity_code()) or self.assembly_dataset_id.startswith(xlib.get_star_code()) or self.assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or self.assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            self.combobox_assembly_type['values'] = ['NONE']
            self.wrapper_assembly_type.set('NONE')
            self.combobox_assembly_type['state'] = 'disabled'

    #---------------

    def combobox_assembly_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_type" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the creation of the transcriptome-blastx config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xngshelper.get_transcriptome_blastx_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the transcriptome-blastx config file
        if OK:
            (OK, error_list) = xngshelper.create_transcriptome_blastx_config_file(self.wrapper_database_dataset.get(), self.wrapper_protein_database_name.get(), self.wrapper_experiment_id.get(), self.assembly_dataset_id, self.wrapper_assembly_type.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the transcriptome-blastx config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xngshelper.get_transcriptome_blastx_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xngshelper.validate_transcriptome_blastx_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_transcriptome_blastx_name())
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
        Close "FormRecreateTranscriptomeBlastxConfigFile".
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
        self.combobox_protein_database_name['values'] = []
        self.wrapper_protein_database_name.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')
        self.assembly_dataset_id = None
        self.combobox_assembly_type['values'] = []
        self.wrapper_assembly_type.set('')
        self.combobox_assembly_type['state'] = 'disabled'

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

        # get the list of the database dataset names
        (OK, error_list, database_dataset_name_list) = xdatabase.get_database_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the database dataset names in the combobox
        self.combobox_database_dataset['values'] = sorted(database_dataset_name_list)

    #---------------

    def populate_combobox_protein_database_name(self):
        '''
        Populate data in "combobox_protein_database_name".
        '''

        # clear the value selected in the combobox
        self.wrapper_protein_database_name.set('')

        # get the list of the database file names
        (OK, error_list, database_file_name_list) = xdatabase.get_database_file_name_list(self.wrapper_cluster_name.get(), self.wrapper_database_dataset.get(), file_type='.*phr', passed_connection=True, ssh_client=self.ssh_client)

        # get the list of the database dataset names
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

        # load the database dataset names in the combobox
        self.combobox_protein_database_name['values'] = sorted(protein_database_name_list)

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
            message = 'The cluster {0} has not experiment data.'.format(self.wrapper_cluster_name.get())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            return

        # load the experiment identifications in the combobox
        self.combobox_experiment_id['values'] = sorted(experiment_id_list)

    #---------------

    def populate_combobox_assembly_dataset(self):
        '''
        Populate data in "combobox_assembly_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_assembly_dataset.set('')

        # get the list of the assembly_dataset dataset names
        app_list = [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]
        (OK, error_list, assembly_dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the assembly dataset names in the combobox
        self.combobox_assembly_dataset['values'] = sorted(assembly_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateTranscriptomeBlastxConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_database_dataset.get() != '' and self.wrapper_protein_database_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_assembly_dataset.get() != '' and self.wrapper_assembly_type.get() != '':
            self.button_execute['state'] = 'enable'
        else:
            self.button_execute['state'] = 'disabled'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateTransrateConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateTransrateConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_transrate_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_reference_dataset = tkinter.StringVar()
        self.wrapper_reference_dataset.trace('w', self.validate_inputs)
        self.wrapper_reference_file = tkinter.StringVar()
        self.wrapper_reference_file.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)
        self.wrapper_assembly_dataset = tkinter.StringVar()
        self.wrapper_assembly_dataset.trace('w', self.validate_inputs)
        self.wrapper_assembly_type = tkinter.StringVar()
        self.wrapper_assembly_type.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateTransrateConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(30,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(30,5), sticky='w')

        # create "label_reference_dataset" and register it with the grid geometry manager
        self.label_reference_dataset = tkinter.Label(self, text='Reference dataset')
        self.label_reference_dataset.grid(row=1, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_reference_dataset" and register it with the grid geometry manager
        self.combobox_reference_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_dataset)
        self.combobox_reference_dataset.grid(row=1, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_reference_file" and register it with the grid geometry manager
        self.label_reference_file = tkinter.Label(self, text='Reference file')
        self.label_reference_file.grid(row=2, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_reference_file" and register it with the grid geometry manager
        self.combobox_reference_file = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_reference_file)
        self.combobox_reference_file.grid(row=2, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=3, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=3, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=4, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=4, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=5, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=5, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=5, column=2, columnspan=3, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=6, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=6, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=7, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=7, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=8, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=8, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_assembly_dataset" and register it with the grid geometry manager
        self.label_assembly_dataset = tkinter.Label(self, text='Assembly dataset')
        self.label_assembly_dataset.grid(row=9, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_assembly_dataset" and register it with the grid geometry manager
        self.combobox_assembly_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_assembly_dataset)
        self.combobox_assembly_dataset.grid(row=9, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_assembly_type" and register it with the grid geometry manager
        self.label_assembly_type = tkinter.Label(self, text='Assembly type')
        self.label_assembly_type.grid(row=10, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_assembly_type" and register it with the grid geometry manager
        self.combobox_assembly_type = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_assembly_type)
        self.combobox_assembly_type.grid(row=10, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=11, column=2, padx=(0,0), pady=(15,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=11, column=3, padx=(0,5), pady=(15,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=11, column=4, padx=(5,5), pady=(15,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_reference_dataset.bind('<<ComboboxSelected>>', self.combobox_reference_dataset_selected_item)
        self.combobox_reference_file.bind('<<ComboboxSelected>>', self.combobox_reference_file_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)
        self.combobox_assembly_dataset.bind('<<ComboboxSelected>>', self.combobox_assembly_dataset_selected_item)
        self.combobox_assembly_type.bind('<<ComboboxSelected>>', self.combobox_assembly_type_selected_item)

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

        # clear data in "combobox_reference_file"
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')

        # load data in "combobox_experiment_id"
        self.populate_combobox_experiment_id()

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

        # clear data in "combobox_assembly_dataset"
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_dataset" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_reference_file"
        if self.wrapper_reference_dataset.get() == 'NONE':
            self.combobox_reference_file['values'] = ['NONE']
            self.wrapper_reference_file.set('NONE')
        else:
            self.populate_combobox_reference_file()

        # set cursor to show normal status
        self.main.config(cursor='')
        self.main.update()

    #---------------

    def combobox_reference_file_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_reference_file" has been selected
        '''

        pass

    #---------------

    def combobox_experiment_id_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_experiment_id" has been selected
        '''

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # load data in "combobox_read_dataset"
        self.populate_combobox_read_dataset()

        # load data in "combobox_assembly_dataset"
        self.populate_combobox_assembly_dataset()

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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state'] = 'normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state'] = 'normal'

    #---------------

    def combobox_assembly_dataset_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_dataset" has been selected
        '''

        # get the assembly dataset identification
        (OK, error_list, self.assembly_dataset_id) = xresult.get_result_dataset_id(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), self.wrapper_assembly_dataset.get(), status='uncompressed', passed_connection=True, ssh_client=self.ssh_client)

        # load data in "combobox_assembly_type"
        if self.assembly_dataset_id.startswith(xlib.get_soapdenovotrans_code()):
            self.combobox_assembly_type['values'] = ['CONTIGS', 'SCAFFOLDS']
            self.wrapper_assembly_type.set('')
            self.combobox_assembly_type['state'] = 'normal'
        elif self.assembly_dataset_id.startswith(xlib.get_transabyss_code()) or self.assembly_dataset_id.startswith(xlib.get_trinity_code()) or self.assembly_dataset_id.startswith(xlib.get_star_code()) or self.assembly_dataset_id.startswith(xlib.get_cd_hit_est_code()) or self.assembly_dataset_id.startswith(xlib.get_transcript_filter_code()):
            self.combobox_assembly_type['values'] = ['NONE']
            self.wrapper_assembly_type.set('NONE')
            self.combobox_assembly_type['state'] = 'disabled'

    #---------------

    def combobox_assembly_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_assembly_type" has been selected
        '''

        pass

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # confirm the creation of the Transrate config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xtransrate.get_transrate_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the Transrate config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xtransrate.create_transrate_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.read_dataset_id, self.read_type, selected_file_list, None, self.assembly_dataset_id, self.wrapper_assembly_type.get())
            elif self.read_type == 'PE':
                (OK, error_list) = xtransrate.create_transrate_config_file(self.wrapper_experiment_id.get(), self.wrapper_reference_dataset.get(), self.wrapper_reference_file.get(), self.read_dataset_id, self.read_type, file_1_list, file_2_list, self.assembly_dataset_id, self.wrapper_assembly_type.get())
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the Transrate config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xtransrate.get_transrate_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xtransrate.validate_transrate_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_transrate_name())
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
        Close "FormRecreateTransrateConfigFile".
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
        self.combobox_reference_dataset['values'] = []
        self.wrapper_reference_dataset.set('')
        self.combobox_reference_file['values'] = []
        self.wrapper_reference_file.set('')
        self.combobox_experiment_id['values'] = []
        self.wrapper_experiment_id.set('')
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'
        self.combobox_assembly_dataset['values'] = []
        self.wrapper_assembly_dataset.set('')
        self.assembly_dataset_id = None
        self.combobox_assembly_type['values'] = []
        self.wrapper_assembly_type.set('')
        self.combobox_assembly_type['state'] = 'disabled'

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

    def populate_combobox_reference_dataset(self):
        '''
        Populate data in "combobox_reference_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_dataset.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_dataset_name_list) = xreference.get_reference_dataset_name_list(self.wrapper_cluster_name.get(), passed_connection=True, ssh_client=self.ssh_client)
        reference_dataset_name_list.append('NONE')

        # load the reference dataset names in the combobox
        self.combobox_reference_dataset['values'] = sorted(reference_dataset_name_list)

    #---------------

    def populate_combobox_reference_file(self):
        '''
        Populate data in "combobox_reference_file".
        '''

        # clear the value selected in the combobox
        self.wrapper_reference_file.set('')

        # get the list of the reference dataset names
        (OK, error_list, reference_file_name_list) = xreference.get_reference_file_name_list(self.wrapper_cluster_name.get(), self.wrapper_reference_dataset.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the reference dataset names in the combobox
        self.combobox_reference_file['values'] = sorted(reference_file_name_list)

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def populate_combobox_assembly_dataset(self):
        '''
        Populate data in "combobox_assembly_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_assembly_dataset.set('')

        # get the list of the assembly dataset names
        app_list = [xlib.get_soapdenovotrans_code(), xlib.get_transabyss_code(), xlib.get_trinity_code(), xlib.get_star_code(), xlib.get_cd_hit_est_code(), xlib.get_transcript_filter_code()]
        (OK, error_list, assembly_dataset_name_list) = xresult.get_result_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), 'uncompressed', app_list, passed_connection=True, ssh_client=self.ssh_client)

        # load the assembly dataset names in the combobox
        self.combobox_assembly_dataset['values'] = sorted(assembly_dataset_name_list)

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateTransrateConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_reference_dataset.get() != '' and self.wrapper_reference_file.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != '') and self.wrapper_assembly_dataset.get() != '':
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
            self.label_file_pattern_warning['text'] = 'Invalid pattern.'
            self.label_file_pattern_warning['foreground'] = 'red'
            OK = False
        else:
            self.label_file_pattern_warning['text'] = 'A pattern of regular expression.'
            self.label_file_pattern_warning['foreground'] = 'black'

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormRecreateTrimmomaticConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateTrimmomaticConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected, read dataset identification and read type
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_trimmomatic_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateTrimmomaticConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=2, column=0, padx=(15,5), pady=(43,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=2, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=3, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=3, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=5, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=5, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=6, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=6, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=7, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=7, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=8, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=8, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=8, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)

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

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

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

        # load data in "combobox_read_dataset"
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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state']='normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state']='normal'

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # confirm the creation of the Trimmomatic config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xtrimmomatic.get_trimmomatic_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the Trimmomatic config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xtrimmomatic.create_trimmomatic_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, selected_file_list, None)
            elif self.read_type == 'PE':
                (OK, error_list) = xtrimmomatic.create_trimmomatic_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, file_1_list, file_2_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the Trimmomatic config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xtrimmomatic.get_trimmomatic_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xtrimmomatic.validate_trimmomatic_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_trimmomatic_name())
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
        Close "FormRecreateTrimmomaticConfigFile".
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
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

    def populate_combobox_read_dataset(self):
        '''
        Populate data in "combobox_read_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_dataset.set('')

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateTrimmomaticConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != ''):
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

class FormRecreateTrinityConfigFile(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormRecreateTrinityConfigFile" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # initialize the cluster name previously selected, read dataset identification and read type
        self.cluster_name_ant = None

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Recreate config file'.format(xlib.get_trinity_name())

        # create the wrappers to track changes in inputs
        self.wrapper_cluster_name = tkinter.StringVar()
        self.wrapper_cluster_name.trace('w', self.validate_inputs)
        self.wrapper_experiment_id = tkinter.StringVar()
        self.wrapper_experiment_id.trace('w', self.validate_inputs)
        self.wrapper_read_dataset = tkinter.StringVar()
        self.wrapper_read_dataset.trace('w', self.validate_inputs)
        self.wrapper_file_pattern = tkinter.StringVar()
        self.wrapper_file_pattern.trace('w', self.validate_inputs)
        self.wrapper_read_type = tkinter.StringVar()
        self.wrapper_read_type.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_1 = tkinter.StringVar()
        self.wrapper_specific_chars_1.trace('w', self.validate_inputs)
        self.wrapper_specific_chars_2 = tkinter.StringVar()
        self.wrapper_specific_chars_2.trace('w', self.validate_inputs)

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
        Build the graphical user interface of "FormRecreateTrinityConfigFile".
        '''

        # assign the text to the label of the current process name
        self.main.label_process['text'] = self.head

        # create "label_cluster_name" and register it with the grid geometry manager
        self.label_cluster_name = tkinter.Label(self, text='Cluster name')
        self.label_cluster_name.grid(row=0, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_cluster_name" and register it with the grid geometry manager
        self.combobox_cluster_name = tkinter.ttk.Combobox(self, width=20, height=4, state='readonly', textvariable=self.wrapper_cluster_name)
        self.combobox_cluster_name.grid(row=0, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_experiment_id" and register it with the grid geometry manager
        self.label_experiment_id = tkinter.Label(self, text='Experiment id.')
        self.label_experiment_id.grid(row=1, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "combobox_experiment_id" and register it with the grid geometry manager
        self.combobox_experiment_id = tkinter.ttk.Combobox(self, width=30, height=4, state='readonly', textvariable=self.wrapper_experiment_id)
        self.combobox_experiment_id.grid(row=1, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_read_dataset" and register it with the grid geometry manager
        self.label_read_dataset = tkinter.Label(self, text='Read dataset')
        self.label_read_dataset.grid(row=2, column=0, padx=(15,5), pady=(43,5), sticky='e')

        # create "combobox_read_dataset" and register it with the grid geometry manager
        self.combobox_read_dataset = tkinter.ttk.Combobox(self, width=45, height=4, state='readonly', textvariable=self.wrapper_read_dataset)
        self.combobox_read_dataset.grid(row=2, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern" and register it with the grid geometry manager
        self.label_file_pattern = tkinter.Label(self, text='File pattern')
        self.label_file_pattern.grid(row=3, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_file_pattern" and register it with the grid geometry manager
        self.entry_file_pattern = tkinter.Entry(self, textvariable=self.wrapper_file_pattern, width=30, validatecommand=self.validate_inputs)
        self.entry_file_pattern.grid(row=3, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_file_pattern_warning" and register it with the grid geometry manager
        self.label_file_pattern_warning = tkinter.Label(self, text='')
        self.label_file_pattern_warning.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_read_type" and register it with the grid geometry manager
        self.label_read_type = tkinter.Label(self, text='Read type')
        self.label_read_type.grid(row=5, column=0, padx=(15,5), pady=(15,5), sticky='e')

        # create "combobox_read_type" and register it with the grid geometry manager
        self.combobox_read_type = tkinter.ttk.Combobox(self, width=15, height=4, state='readonly', textvariable=self.wrapper_read_type)
        self.combobox_read_type.grid(row=5, column=1, padx=(5,5), pady=(15,5), sticky='w')

        # create "label_specific_chars_1" and register it with the grid geometry manager
        self.label_specific_chars_1 = tkinter.Label(self, text='File #1 specific chars')
        self.label_specific_chars_1.grid(row=6, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_1" and register it with the grid geometry manager
        self.entry_specific_chars_1 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_1, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_1.grid(row=6, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_specific_chars_2" and register it with the grid geometry manager
        self.label_specific_chars_2 = tkinter.Label(self, text='File #2 specific chars')
        self.label_specific_chars_2.grid(row=7, column=0, padx=(15,5), pady=(35,5), sticky='e')

        # create "entry_specific_chars_2" and register it with the grid geometry manager
        self.entry_specific_chars_2 = tkinter.Entry(self, textvariable=self.wrapper_specific_chars_2, width=30, validatecommand=self.validate_inputs)
        self.entry_specific_chars_2.grid(row=7, column=1, padx=(5,5), pady=(35,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=8, column=2, padx=(0,0), pady=(25,5), sticky='e')

        # create "button_execute" and register it with the grid geometry manager
        self.button_execute = tkinter.ttk.Button(self, text='Execute', command=self.execute, state='disabled')
        self.button_execute.grid(row=8, column=3, padx=(0,5), pady=(25,5), sticky='e')

        # create "button_close" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', command=self.close)
        self.button_close.grid(row=8, column=4, padx=(5,5), pady=(25,5), sticky='w')

        # link a handler to events
        self.combobox_cluster_name.bind('<<ComboboxSelected>>', self.combobox_cluster_name_selected_item)
        self.combobox_experiment_id.bind('<<ComboboxSelected>>', self.combobox_experiment_id_selected_item)
        self.combobox_read_dataset.bind('<<ComboboxSelected>>', self.combobox_read_dataset_selected_item)
        self.combobox_read_type.bind('<<ComboboxSelected>>', self.combobox_read_type_selected_item)

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

        # clear data in "combobox_read_dataset"
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')

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

        # load data in "combobox_read_dataset"
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

    def combobox_read_type_selected_item(self, event=None):
        '''
        Process the event when an item of "combobox_read_type" has been selected
        '''

        # get the read type code
        if self.wrapper_read_type.get() == 'Single-end':
            self.read_type = 'SE'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.read_type = 'PE'

        # enable or disable the specific chars entries
        if self.wrapper_read_type.get() == 'Single-end':
            self.wrapper_specific_chars_1.set('')
            self.entry_specific_chars_1['state'] = 'disabled'
            self.wrapper_specific_chars_2.set('')
            self.entry_specific_chars_2['state'] = 'disabled'
        elif self.wrapper_read_type.get() == 'Paired-end':
            self.wrapper_specific_chars_1.set('1')
            self.entry_specific_chars_1['state']='normal'
            self.wrapper_specific_chars_2.set('2')
            self.entry_specific_chars_2['state']='normal'

    #---------------

    def execute(self, event=None):
        '''
        Execute the creation of the config file.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the cluster read directory path
        if OK:
            cluster_read_dir = '{0}/{1}/{2}'.format(xlib.get_cluster_read_dir(), self.wrapper_experiment_id.get(), self.read_dataset_id)

        # get the selected file list
        if OK:
            selected_file_list = []
            command = 'cd {0}; find . -type f -regex "./{1}"'.format(cluster_read_dir, self.wrapper_file_pattern.get())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                for line in stdout:
                    selected_file_list.append(line.rstrip('\n'))
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            if selected_file_list == []:
                message = 'WARNING: There are not files in the cluster directory {0} with the pattern {1}'.format(cluster_read_dir, self.wrapper_file_pattern.get())
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the paired file list when the read type is paired-end
        if OK:
            if self.read_type == 'PE':
                (file_1_list, file_2_list, unpaired_file_list) = xlib.pair_files(selected_file_list, self.wrapper_specific_chars_1.get(), self.wrapper_specific_chars_2.get())
                if unpaired_file_list != []:
                    message = 'ERROR: There are unpaired files.'
                    tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
                    OK = False

        # confirm the creation of the Trinity config file
        if OK:
            message = 'The file {0} is going to be recreated. The previous file will be lost.\n\nAre you sure to continue?'.format(xtrinity.get_trinity_config_file())
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # recreate the Trinity config file
        if OK:
            if self.read_type == 'SE':
                (OK, error_list) = xtrinity.create_trinity_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, selected_file_list, None)
            elif self.read_type == 'PE':
                (OK, error_list) = xtrinity.create_trinity_config_file(self.wrapper_experiment_id.get(), self.read_dataset_id, self.read_type, file_1_list, file_2_list)
            if not OK:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # edit the Trinity config file
        if OK:

            # edit the config file using "DialogEditor" 
            dialog_editor = gdialogs.DialogEditor(self, xtrinity.get_trinity_config_file())
            self.wait_window(dialog_editor)

            # validate the config file
            (OK, error_list) = xtrinity.validate_trinity_config_file(strict=False)
            if OK:
                message = 'The {0} config file is OK.'.format(xlib.get_trinity_name())
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
        Close "FormRecreateTrinityConfigFile".
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
        self.combobox_read_dataset['values'] = []
        self.wrapper_read_dataset.set('')
        self.read_dataset_id = None
        self.wrapper_file_pattern.set('.*')
        self.populate_combobox_read_type()
        self.read_type = None
        self.wrapper_specific_chars_1.set('')
        self.entry_specific_chars_1['state'] = 'disabled'
        self.wrapper_specific_chars_2.set('')
        self.entry_specific_chars_2['state'] = 'disabled'

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
        command = 'ls {0}'.format(xlib.get_cluster_read_dir())
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

    def populate_combobox_read_dataset(self):
        '''
        Populate data in "combobox_read_dataset".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_dataset.set('')

        # get the list of the read dataset names
        (OK, error_list, read_dataset_name_list) = xread.get_read_dataset_name_list(self.wrapper_cluster_name.get(), self.wrapper_experiment_id.get(), passed_connection=True, ssh_client=self.ssh_client)

        # load the list of the read dataset names in the combobox
        self.combobox_read_dataset['values'] = read_dataset_name_list

    #---------------

    def populate_combobox_read_type(self):
        '''
        Populate data in "combobox_read_type".
        '''

        # clear the value selected in the combobox
        self.wrapper_read_type.set('')

        # load the list of the read dataset names in the combobox
        self.combobox_read_type['values'] =['Single-end', 'Paired-end']

    #---------------

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormRecreateTrinityConfigFile" and do the actions linked to its value
        '''

        # initialize the control variable
        OK = True

        # validate the content of "entry_file_pattern"
        if not self.validate_entry_file_pattern():
            OK = False

        # verify if "button_execute" has to be enabled or disabled
        if self.wrapper_cluster_name.get() != '' and self.wrapper_experiment_id.get() != '' and self.wrapper_read_dataset.get() != '' and self.wrapper_file_pattern.get() != '' and (self.read_type == 'SE' or self.read_type == 'PE' and self.wrapper_specific_chars_1.get() != '' and  self.wrapper_specific_chars_2.get() != ''):
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

class FormRunBioinfoProcess(tkinter.Frame):

    #---------------

    def __init__(self, parent, main, app):
        '''
        Execute actions correspending to the creation of a "FormRunBioinfoProcess" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main
        self.app = app

        # set the name
        if self.app == xlib.get_busco_code():
            self.name = xlib.get_busco_name()
        elif self.app == xlib.get_cd_hit_est_code():
            self.name = xlib.get_cd_hit_est_name()
        elif self.app == xlib.get_fastqc_code():
            self.name = xlib.get_fastqc_name()
        elif self.app == xlib.get_gmap_code():
            self.name = xlib.get_gmap_name()
        elif self.app == xlib.get_insilico_read_normalization_code():
            self.name = xlib.get_insilico_read_normalization_name()
        elif self.app == xlib.get_quast_code():
            self.name = xlib.get_quast_name()
        elif self.app == xlib.get_ref_eval_code():
            self.name = xlib.get_ref_eval_name()
        elif self.app == xlib.get_rnaquast_code():
            self.name = xlib.get_rnaquast_name()
        elif self.app == xlib.get_rsem_eval_code():
            self.name = xlib.get_rsem_eval_name()
        elif self.app == xlib.get_soapdenovotrans_code():
            self.name = xlib.get_soapdenovotrans_name()
        elif self.app == xlib.get_star_code():
            self.name = xlib.get_star_name()
        elif self.app == xlib.get_transabyss_code():
            self.name = xlib.get_transabyss_name()
        elif self.app == xlib.get_transcript_filter_code():
            self.name = xlib.get_transcript_filter_name()
        elif self.app == xlib.get_transcriptome_blastx_code():
            self.name = xlib.get_transcriptome_blastx_name()
        elif self.app == xlib.get_transrate_code():
            self.name = xlib.get_transrate_name()
        elif self.app == xlib.get_trimmomatic_code():
            self.name = xlib.get_trimmomatic_name()
        elif self.app == xlib.get_trinity_code():
            self.name = xlib.get_trinity_name()

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - Run process'.format(self.name)

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
        Build the graphical user interface of "FormRunBioinfoProcess".
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
        Run bioinfo process.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # confirm the process run
        if OK:
            message = 'The {0} process is going to be run.\n\nAre you sure to continue?'.format(self.name)
            OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # execute the process
        if OK:

            # execute the process when it is a BUSCO process
            if self.app == xlib.get_busco_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xbusco.run_busco_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xbusco.run_busco_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a CD-HIT-EST process
            elif self.app == xlib.get_cd_hit_est_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xcdhit.run_cd_hit_est_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xcdhit.run_cd_hit_est_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a FastQC process
            elif self.app == xlib.get_fastqc_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xfastqc.run_fastqc_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xfastqc.run_fastqc_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a GMAP process
            elif self.app == xlib.get_gmap_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xgmap.run_gmap_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xgmap.run_gmap_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a insilico_read_normalization process
            elif self.app == xlib.get_insilico_read_normalization_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xtrinity.run_insilico_read_normalization_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xtrinity.run_insilico_read_normalization_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a QUAST process
            elif self.app == xlib.get_quast_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xquast.run_quast_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xquast.run_quast_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a REF-EVAL process
            elif self.app == xlib.get_ref_eval_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xdetonate.run_ref_eval_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xdetonate.run_ref_eval_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a rnaQUAST process
            elif self.app == xlib.get_rnaquast_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xrnaquast.run_rnaquast_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xrnaquast.run_rnaquast_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a RSEM-EVAL process
            elif self.app == xlib.get_rsem_eval_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xdetonate.run_rsem_eval_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xdetonate.run_rsem_eval_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a SOAPdenovo-Trans process
            elif self.app == xlib.get_soapdenovotrans_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xsoapdenovotrans.run_soapdenovotrans_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xsoapdenovotrans.run_soapdenovotrans_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a STAR process
            elif self.app == xlib.get_star_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xstar.run_star_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xstar.run_star_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a Trans-ABySS process
            elif self.app == xlib.get_transabyss_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xtransabyss.run_transabyss_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xtransabyss.run_transabyss_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a transcript-filter process
            elif self.app == xlib.get_transcript_filter_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xngshelper.run_transcript_filter_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xngshelper.run_transcript_filter_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a transcriptome_blastx process
            elif self.app == xlib.get_transcriptome_blastx_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xngshelper.run_transcriptome_blastx_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xngshelper.run_transcriptome_blastx_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a Transrate process
            elif self.app == xlib.get_transrate_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xtransrate.run_transrate_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xtransrate.run_transrate_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a Trimmomatic process
            elif self.app == xlib.get_trimmomatic_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xtrimmomatic.run_trimmomatic_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xtrimmomatic.run_trimmomatic_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

            # execute the process when it is a Trinity process
            elif self.app == xlib.get_trinity_code():
                dialog_log = gdialogs.DialogLog(self, self.head, xtrinity.run_trinity_process.__name__)
                threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
                threading.Thread(target=xtrinity.run_trinity_process, args=(self.wrapper_cluster_name.get(), dialog_log, lambda: dialog_log.enable_button_close())).start()

        # close the form
        if OK:
            self.close()

    #---------------

    def close(self, event=None):
        '''
        Close "FormRunProcess".
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
        Validate the content of each input of "FormRunBioinfoProcess" and do the actions linked to its value
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

class FormListBioinfoRuns(tkinter.Frame):

    #---------------

    def __init__(self, parent, main, app):
        '''
        Execute actions correspending to the creation of a "FormListBioinfoRuns" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main
        self.app = app

        # set the software name
        if self.app == xlib.get_busco_code():
            self.name = xlib.get_busco_name()
        elif self.app == xlib.get_cd_hit_est_code():
            self.name = xlib.get_cd_hit_est_name()
        elif self.app == xlib.get_fastqc_code():
            self.name = xlib.get_fastqc_name()
        elif self.app == xlib.get_gmap_code():
            self.name = xlib.get_gmap_name()
        elif self.app == xlib.get_insilico_read_normalization_code():
            self.name = xlib.get_insilico_read_normalization_name()
        elif self.app == xlib.get_quast_code():
            self.name = xlib.get_quast_name()
        elif self.app == xlib.get_ref_eval_code():
            self.name = xlib.get_ref_eval_name()
        elif self.app == xlib.get_rnaquast_code():
            self.name = xlib.get_rnaquast_name()
        elif self.app == xlib.get_rsem_eval_code():
            self.name = xlib.get_rsem_eval_name()
        elif self.app == xlib.get_soapdenovotrans_code():
            self.name = xlib.get_soapdenovotrans_name()
        elif self.app == xlib.get_star_code():
            self.name = xlib.get_star_name()
        elif self.app == xlib.get_transabyss_code():
            self.name = xlib.get_transabyss_name()
        elif self.app == xlib.get_transcript_filter_code():
            self.name = xlib.get_transcript_filter_name()
        elif self.app == xlib.get_transcriptome_blastx_code():
            self.name = xlib.get_transcriptome_blastx_name()
        elif self.app == xlib.get_transrate_code():
            self.name = xlib.get_transrate_name()
        elif self.app == xlib.get_trimmomatic_code():
            self.name = xlib.get_trimmomatic_name()
        elif self.app == xlib.get_trinity_code():
            self.name = xlib.get_trinity_name()

        # set cursor to show busy status
        self.main.config(cursor='watch')
        self.main.update()

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # assign the text of the "head"
        self.head = '{0} - List runs and view logs'.format(self.name)

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
        Build the graphical user interface of "FormListBioinfoRuns".
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
        Execute the list the runs of an experiment.
        '''

        # validate inputs
        OK = self.validate_inputs()
        if not OK:
            message = 'Some input values are not OK.'
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # get the runs list of the bioinfo software
        if OK:
            command = 'find {0} -maxdepth 2 -type d'.format(xlib.get_cluster_result_dir())
            (OK, stdout, stderr) = xssh.execute_cluster_command(self.ssh_client, command)
            if OK:
                run_ids_dict = {}
                for line in stdout:
                    line = line.rstrip('\n')
                    basename = os.path.basename(line)
                    if os.path.basename(line).startswith(self.app):
                        experiment_id = os.path.basename(os.path.dirname(line))
                        run_id = basename
                        run_ids_dict[run_id] = {'experiment_id': experiment_id, 'run_id': run_id, 'bioinfo_app': self.name}
            else:
                message = '*** ERROR: Wrong command ---> {0}'.format(command)
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # verify if there are any nodes running
        if OK:
            if run_ids_dict == {}:
                message = 'There is not any run.'
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the data list
        if OK:
            data_list = ['experiment_id', 'run_id', 'bioinfo_app']

        # build the data dictionary
        if OK:
            data_dict = {}
            data_dict['experiment_id']= {'text': 'Experiment id', 'width': 400, 'aligment': 'left'}
            data_dict['run_id'] = {'text': 'Run id', 'width': 230, 'aligment': 'left'}
            data_dict['bioinfo_app'] = {'text': 'Bioinfo app', 'width': 170, 'aligment': 'left'}

        # create the dialog Table to show the nodes running
        if OK:
            dialog_table = gdialogs.DialogTable(self, '{0} run list'.format(self.name), 400, 900, data_list, data_dict, run_ids_dict, 'view_log', [self.wrapper_cluster_name.get()])
            self.wait_window(dialog_table)

    #---------------

    def close(self, event=None):
        '''
        Close "FormListBioinfoRuns".
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

    def validate_inputs(self, *args):
        '''
        Validate the content of each input of "FormListBioinfoRuns" and do the actions linked to its value
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

if __name__ == '__main__':
    print('This file contains the classes related to BioInfo application forms in gui mode.')
    sys.exit(0)

#-------------------------------------------------------------------------------
