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
This source contains the class Main corresponding to the graphical user interface of
the NGScloud software package.
'''

#-------------------------------------------------------------------------------

import os
import PIL.Image
import PIL.ImageTk
import tkinter
import tkinter.messagebox
import tkinter.ttk
import sys
import threading
import webbrowser

import gbioinfoapp
import gcloud
import gdataset
import gdialogs
import glog
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
import xquast
import xsoapdenovotrans
import xstar
import xread
import xreference
import xresult
import xrnaquast
import xtransabyss
import xtransrate
import xtrimmomatic
import xtrinity
import xvolume

#-------------------------------------------------------------------------------

class Main(tkinter.Tk):

    #---------------

    if sys.platform.startswith('linux'):
        WINDOW_HEIGHT = 590
        WINDOW_WIDTH = 750
    elif sys.platform.startswith('darwin'):
        WINDOW_HEIGHT = 650
        WINDOW_WIDTH = 850
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        WINDOW_HEIGHT = 585
        WINDOW_WIDTH = 780

    #---------------

    def __init__(self):
        '''
        Execute actions correspending to the creation of a "Main" instance.
        '''

        # call the init method of the parent class
        tkinter.Tk.__init__(self)

        # initialize the forms dictionary
        self.forms_dict = {}

        # create the window
        self.create_window()

        # build the graphical user interface
        self.build_gui()

        # create "form_welcome" and register it in "container" with the grid geometry manager
        self.form_welcome = FormWelcome(self.container, self)
        self.form_welcome.grid(row=0, column=0, sticky='nsew')

        # add "form_welcome" in the forms dictionary
        self.forms_dict['form_welcome'] = self.form_welcome

        # create and register "form_set_environment" in "container" with the grid geometry manager
        self.form_set_environment = gcloud.FormSetEnvironment(self.container, self)
        self.form_set_environment.grid(row=0, column=0, sticky='nsew')

        # set "form_set_environment" as current form and add it in the forms dictionary
        self.current_form = 'form_set_environment'
        self.forms_dict[self.current_form] = self.form_set_environment

        # raise "form_set_environment" to front
        self.form_set_environment.tkraise()

    #---------------

    def create_window(self):
        '''
        Create the window of "Main".
        '''

        # define the dimensions
        x = round((self.winfo_screenwidth() - self.WINDOW_WIDTH) / 2)
        y = round((self.winfo_screenheight() - self.WINDOW_HEIGHT) / 2)
        self.geometry('{}x{}+{}+{}'.format(self.WINDOW_WIDTH, self.WINDOW_HEIGHT, x, y))
        self.minsize(height=self.WINDOW_HEIGHT, width=self.WINDOW_WIDTH)
        self.maxsize(height=self.WINDOW_HEIGHT, width=self.WINDOW_WIDTH)

        # set the title
        self.title(xlib.get_project_name())

        # set the icon
        image_app = PIL.Image.open(xlib.get_project_image_file())
        self.photoimage_app = PIL.ImageTk.PhotoImage(image_app)
        self.tk.call('wm', 'iconphoto', self._w, self.photoimage_app)

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "Main".
        '''

        # create "imagetk_exit"
        image_exit = PIL.Image.open('./image_exit.png')
        imagetk_exit = PIL.ImageTk.PhotoImage(image_exit)  

        # create "initial_menu_bar"
        self.initial_menu_bar = tkinter.Menu(self)

        # create "initial_menu_system" and add its menu items
        self.initial_menu_system = tkinter.Menu(self.initial_menu_bar, tearoff=0)
        self.initial_menu_system.add_command(label='Exit', command=self.exit, accelerator='Alt+F4', compound='left', image=imagetk_exit)

        # link "initial_menu_system" to "initial_menu_bar"
        self.initial_menu_bar.add_cascade(label='System', menu=self.initial_menu_system)

        # create "menu_help" add add its menu items
        self.initial_menu_help = tkinter.Menu(self.initial_menu_bar, tearoff=0)
        self.initial_menu_help.add_command(label='View help', command=self.open_help, accelerator='F1')
        self.initial_menu_help.add_separator()
        self.initial_menu_help.add_command(label='About...', command=self.show_dialog_about)

        # link "menu_help" with "menu_bar"
        self.initial_menu_bar.add_cascade(label='Help', menu=self.initial_menu_help)

        #  assign "initial_menu_bar" as the window menu
        self.config(menu=self.initial_menu_bar)

        # create "frame_toolbar" and register it in "Main" with the grid geometry manager
        self.frame_toolbar = tkinter.Frame(self, borderwidth=1, relief='raised')
        self.frame_toolbar.grid(row=0, column=0, sticky='ew')

        # create and register "button_exit" in "frame_toolbar" with the pack geometry manager
        self.button_exit = tkinter.Button(self.frame_toolbar, command=self.exit, relief='flat', image=imagetk_exit)
        self.button_exit.image = imagetk_exit
        self.button_exit.pack(side='left', padx=2, pady=5)

        # create "frame_information" and register it in "Main" with the grid geometry manager
        self.frame_information = tkinter.Frame(self, borderwidth=1, relief='raised')
        self.frame_information.grid(row=1, column=0, sticky='ew')

        # create "label_environment_text" and register it in "frame_information" with the pack geometry manager
        self.label_environment_text = tkinter.Label(self.frame_information, text='Environment:')
        self.label_environment_text.pack(side='left', padx=(5,0))

        # create "label_environment_value" and register it in "frame_information" with the pack geometry manager
        self.label_environment_value = tkinter.Label(self.frame_information, text='', foreground='dark olive green')
        self.label_environment_value.pack(side='left', padx=(0,5))

        # create "label_region_text" and register it in "frame_information" with the pack geometry manager
        self.label_region_text = tkinter.Label(self.frame_information, text='Region:')
        self.label_region_text.pack(side='left', padx=(5,0))

        # create "label_region_value" and register it in "frame_information" with the pack geometry manager
        self.label_region_value = tkinter.Label(self.frame_information, text='', foreground='dark olive green')
        self.label_region_value.pack(side='left', padx=(0,0))

        # create "label_zone_text" and register it in "frame_information" with the pack geometry manager
        self.label_zone_text = tkinter.Label(self.frame_information, text='Zone:')
        self.label_zone_text.pack(side='left', padx=(5,0))

        # create "label_zone_value" and register it in "frame_information" with the pack geometry manager
        self.label_zone_value = tkinter.Label(self.frame_information, text='', foreground='dark olive green')
        self.label_zone_value.pack(side='left', padx=(0,0))

        # create "label_process" and register it in "frame_information" with the pack geometry manager
        self.label_process = tkinter.Label(self.frame_information, text='')
        self.label_process.pack(side='right', padx=(0,10))

        # create "container" and register it in "Main" with the grid geometry manager
        self.container = tkinter.Frame(self)
        self.container.grid(row=2, column=0, sticky='nsew')

        # link a handler to events
        self.bind('<F1>', self.open_help)
        self.bind('<Alt-F4>', self.exit)

        # link a handler to interactions between the application and the window manager
        self.protocol('WM_DELETE_WINDOW', self.exit)

    #---------------

    def build_full_menu(self):
        '''
        Build the full menu of "Main".
        '''

        # create "imagetk_exit"
        image_exit = PIL.Image.open('./image_exit.png')
        imagetk_exit = PIL.ImageTk.PhotoImage(image_exit)  

        # create "menu_bar"
        self.menu_bar = tkinter.Menu(self)

        # create "menu_system" and add its menu items and links with "menu_configuration" and "menu_security"
        self.menu_system = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_system.add_command(label='Exit', command=self.exit, accelerator='Alt+F4', compound='left', image=imagetk_exit)

        # link "menu_system" to "menu_bar"
        self.menu_bar.add_cascade(label='System', menu=self.menu_system)

        # create "menu_configuration" and add its menu items
        self.menu_configuration = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_configuration.add_command(label='Recreate NGScloud config file', command=self.recreate_ngscloud_config_file)
        self.menu_configuration.add_command(label='View NGScloud config file', command=self.view_ngscloud_config_file)
        self.menu_configuration.add_separator()
        self.menu_configuration.add_command(label='List cluster templates', command=self.list_templates)
        self.menu_configuration.add_separator()
        self.menu_configuration.add_command(label='Update connection data and contact e-mail', command=self.update_connection_data)
        self.menu_configuration.add_command(label='Update region and zone', command=self.update_region_zone)
        self.menu_configuration.add_separator()
        self.menu_configuration.add_command(label='Link volume in a cluster template', command=self.link_volume_to_template)
        self.menu_configuration.add_command(label='Delink volume in a cluster template', command=self.delink_volume_from_template)
        self.menu_configuration.add_command(label='Review volumes linked to cluster templates', command=self.review_volume_links)

        # create "menu_security" and add its menu items
        self.menu_security = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_security.add_command(label='List key pairs', command=self.list_keypairs)
        self.menu_security.add_separator()
        self.menu_security.add_command(label='Create key pairs', command=self.create_keypairs)
        self.menu_security.add_separator()
        self.menu_security.add_command(label='List cluster security groups', command=self.warn_unavailable_process)
        self.menu_security.add_separator()
        self.menu_security.add_command(label='Force removal of a cluster security group', command=self.warn_unavailable_process)

        # create "menu_cluster_operation" add add its menu items
        self.menu_cluster_operation = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_cluster_operation.add_command(label='List clusters', command=self.list_clusters)
        self.menu_cluster_operation.add_separator()
        self.menu_cluster_operation.add_command(label='Create cluster', command=self.create_cluster)
        self.menu_cluster_operation.add_command(label='Stop cluster', command=self.stop_cluster)
        self.menu_cluster_operation.add_command(label='Restart cluster', command=self.restart_cluster)
        self.menu_cluster_operation.add_command(label='Terminate cluster', command=self.terminate_cluster)
        self.menu_cluster_operation.add_separator()
        self.menu_cluster_operation.add_command(label='Force termination of a cluster', command=self.force_cluster_termination)
        self.menu_cluster_operation.add_separator()
        self.menu_cluster_operation.add_command(label='Show cluster composition', command=self.show_cluster_composing)
        self.menu_cluster_operation.add_separator()
        self.menu_cluster_operation.add_command(label='Show status of batch jobs', command=self.show_status_batch_jobs)
        self.menu_cluster_operation.add_command(label='Kill batch job', command=self.kill_batch_job)

        # create "menu_node_operation" add add its menu items
        self.menu_node_operation = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_node_operation.add_command(label='List nodes', command=self.list_nodes)
        self.menu_node_operation.add_separator()
        self.menu_node_operation.add_command(label='Add node in a cluster', command=self.add_node)
        self.menu_node_operation.add_command(label='Remove node in acluster', command=self.remove_node)

        # create "menu_volume_operation" add add its menu items
        self.menu_volume_operation = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_volume_operation.add_command(label='List volumes', command=self.list_volumes)
        self.menu_volume_operation.add_separator()
        self.menu_volume_operation.add_command(label='Create volume', command=self.create_volume)
        self.menu_volume_operation.add_command(label='Remove volume', command=self.remove_volume)
        self.menu_volume_operation.add_separator()
        self.menu_volume_operation.add_command(label='Terminate volume creator', command=self.terminate_volume_creator)
        self.menu_volume_operation.add_separator()
        self.menu_volume_operation.add_command(label='Mount volume in a node', command=self.mount_volume)
        self.menu_volume_operation.add_command(label='Unmount volume in a node', command=self.unmount_volume)

        # create "menu_bioinfo_software_setup" add add its menu items
        self.menu_bioinfo_software_setup = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_bioinfo_software_setup.add_command(label='{0} (Python & Bioconda environments)'.format(xlib.get_miniconda3_name()), command=self.setup_miniconda3)
        self.menu_bioinfo_software_setup.add_separator()
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_blastplus_name(), command=self.setup_blastplus)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_busco_name(), command=self.setup_busco)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_cd_hit_name(), command=self.setup_cd_hit)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_detonate_name(), command=self.setup_detonate)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_fastqc_name(), command=self.setup_fastqc)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_gmap_gsnap_name(), command=self.setup_gmap_gsnap)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_ngshelper_name(), command=self.setup_ngshelper)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_quast_name(), command=self.setup_quast)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_rnaquast_name(), command=self.setup_rnaquast)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_soapdenovotrans_name(), command=self.setup_soapdenovotrans)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_star_name(), command=self.setup_star)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_transabyss_name(), command=self.setup_transabyss)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_transrate_name(), command=self.setup_transrate)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_trimmomatic_name(), command=self.setup_trimmomatic)
        self.menu_bioinfo_software_setup.add_command(label=xlib.get_trinity_name(), command=self.setup_trinity)
        # -- self.menu_bioinfo_software_setup.add_separator()
        # -- self.menu_bioinfo_software_setup.add_command(label='{0} & analysis packages'.format(xlib.get_r_name()), command=self.setup_r)

        # create "menu_cloud_control" and add its menu items
        self.menu_cloud_control = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_cloud_control.add_command(label='Set environment', command=self.set_environment)
        self.menu_cloud_control.add_separator()
        self.menu_cloud_control.add_cascade(label='Configuration', menu=self.menu_configuration)
        self.menu_cloud_control.add_cascade(label='Security', menu=self.menu_security)
        self.menu_cloud_control.add_separator()
        self.menu_cloud_control.add_cascade(label='Cluster operation', menu=self.menu_cluster_operation)
        self.menu_cloud_control.add_cascade(label='Node operation', menu=self.menu_node_operation)
        self.menu_cloud_control.add_cascade(label='Volume operation', menu=self.menu_volume_operation)
        self.menu_cloud_control.add_separator()
        self.menu_cloud_control.add_cascade(label='Bioinfo software setup', menu=self.menu_bioinfo_software_setup)
        self.menu_cloud_control.add_separator()
        self.menu_cloud_control.add_command(label='Open a terminal', command=self.open_terminal)

        # link "menu_cloud_control" with "menu_bar"
        self.menu_bar.add_cascade(label='Cloud control', menu=self.menu_cloud_control)

        # create "menu_fastqc" and add its menu items
        self.menu_fastqc = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_fastqc.add_command(label='Recreate config file', command=self.recreate_fastqc_config_file)
        self.menu_fastqc.add_command(label='Edit config file', command=self.edit_fastqc_config_file)
        self.menu_fastqc.add_separator()
        self.menu_fastqc.add_command(label='Run read quality process', command=self.run_fastqc_process)
        self.menu_fastqc.add_separator()
        self.menu_fastqc.add_command(label='List runs and view logs', command=self.view_fastqc_run_logs)

        # create "menu_read_quality" and add its menu items
        self.menu_read_quality = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_read_quality.add_cascade(label='{0}'.format(xlib.get_fastqc_name()), menu=self.menu_fastqc)

        # create "menu_trimmomatic" and add its menu items
        self.menu_trimmomatic = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_trimmomatic.add_command(label='Recreate config file', command=self.recreate_trimmomatic_config_file)
        self.menu_trimmomatic.add_command(label='Edit config file', command=self.edit_trimmomatic_config_file)
        self.menu_trimmomatic.add_separator()
        self.menu_trimmomatic.add_command(label='Run trimming process', command=self.run_trimmomatic_process)
        self.menu_trimmomatic.add_separator()
        self.menu_trimmomatic.add_command(label='List runs and view logs', command=self.view_trimmomatic_run_logs)

        # create "menu_trimming" and add its menu items
        self.menu_trimming = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_trimming.add_cascade(label='{0}'.format(xlib.get_trimmomatic_name()), menu=self.menu_trimmomatic)

        # create "menu_insilico_read_normalization" and add its menu items
        self.menu_insilico_read_normalization = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_insilico_read_normalization.add_command(label='Recreate config file', command=self.recreate_insilico_read_normalization_config_file)
        self.menu_insilico_read_normalization.add_command(label='Edit config file', command=self.edit_insilico_read_normalization_config_file)
        self.menu_insilico_read_normalization.add_separator()
        self.menu_insilico_read_normalization.add_command(label='Run normalization process', command=self.run_insilico_read_normalization_process)
        self.menu_insilico_read_normalization.add_separator()
        self.menu_insilico_read_normalization.add_command(label='List runs and view logs', command=self.view_insilico_read_normalization_run_logs)

        # create "menu_digital_normalization" and add its menu items
        self.menu_digital_normalization = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_digital_normalization.add_cascade(label='{0} ({1} package)'.format(xlib.get_insilico_read_normalization_name(), xlib.get_trinity_name()), menu=self.menu_insilico_read_normalization)

        # create "menu_soapdenovotrans" and add its menu items
        self.menu_soapdenovotrans = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_soapdenovotrans.add_command(label='Recreate config file', command=self.recreate_soapdenovotrans_config_file)
        self.menu_soapdenovotrans.add_command(label='Edit config file', command=self.edit_soapdenovotrans_config_file)
        self.menu_soapdenovotrans.add_separator()
        self.menu_soapdenovotrans.add_command(label='Run assembly process', command=self.run_soapdenovotrans_process)
        self.menu_soapdenovotrans.add_separator()
        self.menu_soapdenovotrans.add_command(label='List runs and view logs', command=self.view_soapdenovotrans_run_logs)

        # create "menu_transabyss" and add its menu items
        self.menu_transabyss = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_transabyss.add_command(label='Recreate config file', command=self.recreate_transabyss_config_file)
        self.menu_transabyss.add_command(label='Edit config file', command=self.edit_transabyss_config_file)
        self.menu_transabyss.add_separator()
        self.menu_transabyss.add_command(label='Run assembly process', command=self.run_transabyss_process)
        self.menu_transabyss.add_separator()
        self.menu_transabyss.add_command(label='List runs and view logs', command=self.view_transabyss_run_logs)

        # create "menu_trinity" and add its menu items
        self.menu_trinity = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_trinity.add_command(label='Recreate config file', command=self.recreate_trinity_config_file)
        self.menu_trinity.add_command(label='Edit config file', command=self.edit_trinity_config_file)
        self.menu_trinity.add_separator()
        self.menu_trinity.add_command(label='Run assembly process', command=self.run_trinity_process)
        self.menu_trinity.add_separator()
        self.menu_trinity.add_command(label='List runs and view logs', command=self.view_trinity_run_logs)

        # create "menu_denovo_assembly" and add its menu items
        self.menu_denovo_assembly = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_denovo_assembly.add_cascade(label=xlib.get_soapdenovotrans_name(), menu=self.menu_soapdenovotrans)
        self.menu_denovo_assembly.add_cascade(label=xlib.get_transabyss_name(), menu=self.menu_transabyss)
        self.menu_denovo_assembly.add_cascade(label=xlib.get_trinity_name(), menu=self.menu_trinity)

        # create "menu_star" and add its menu items
        self.menu_star = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_star.add_command(label='Recreate config file', command=self.recreate_star_config_file)
        self.menu_star.add_command(label='Edit config file', command=self.edit_star_config_file)
        self.menu_star.add_separator()
        self.menu_star.add_command(label='Run assembly process', command=self.run_star_process)
        self.menu_star.add_separator()
        self.menu_star.add_command(label='List runs and view logs', command=self.view_star_run_logs)

        # create "menu_reference_based_assembly" add add its menu items
        self.menu_reference_based_assembly = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_reference_based_assembly.add_cascade(label=xlib.get_star_name(), menu=self.menu_star)

        # create "menu_busco" and add its menu items
        self.menu_busco = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_busco.add_command(label='Recreate config file', command=self.recreate_busco_config_file)
        self.menu_busco.add_command(label='Edit config file', command=self.edit_busco_config_file)
        self.menu_busco.add_separator()
        self.menu_busco.add_command(label='Run assembly assessment process', command=self.run_busco_process)
        self.menu_busco.add_separator()
        self.menu_busco.add_command(label='List runs and view logs', command=self.view_busco_run_logs)

        # create "menu_gmap" and add its menu items
        self.menu_gmap = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_gmap.add_command(label='Recreate config file', command=self.recreate_gmap_config_file)
        self.menu_gmap.add_command(label='Edit config file', command=self.edit_gmap_config_file)
        self.menu_gmap.add_separator()
        self.menu_gmap.add_command(label='Run assembly assessment process', command=self.run_gmap_process)
        self.menu_gmap.add_separator()
        self.menu_gmap.add_command(label='List runs and view logs', command=self.view_gmap_run_logs)

        # create "menu_quast" and add its menu items
        self.menu_quast = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_quast.add_command(label='Recreate config file', command=self.recreate_quast_config_file)
        self.menu_quast.add_command(label='Edit config file', command=self.edit_quast_config_file)
        self.menu_quast.add_separator()
        self.menu_quast.add_command(label='Run assembly assessment process', command=self.run_quast_process)
        self.menu_quast.add_separator()
        self.menu_quast.add_command(label='List runs and view logs', command=self.view_quast_run_logs)

        # create "menu_rnaquast" and add its menu items
        self.menu_rnaquast = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_rnaquast.add_command(label='Recreate config file', command=self.recreate_rnaquast_config_file)
        self.menu_rnaquast.add_command(label='Edit config file', command=self.edit_rnaquast_config_file)
        self.menu_rnaquast.add_separator()
        self.menu_rnaquast.add_command(label='Run assembly assessment process', command=self.run_rnaquast_process)
        self.menu_rnaquast.add_separator()
        self.menu_rnaquast.add_command(label='List runs and view logs', command=self.view_rnaquast_run_logs)

        # create "menu_rsem_eval" and add its menu items
        self.menu_rsem_eval = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_rsem_eval.add_command(label='Recreate config file', command=self.recreate_rsem_eval_config_file)
        self.menu_rsem_eval.add_command(label='Edit config file', command=self.edit_rsem_eval_config_file)
        self.menu_rsem_eval.add_separator()
        self.menu_rsem_eval.add_command(label='Run assembly assessment process', command=self.run_rsem_eval_process)
        self.menu_rsem_eval.add_separator()
        self.menu_rsem_eval.add_command(label='List runs and view logs', command=self.view_rsem_eval_run_logs)

        # create "menu_ref_eval" and add its menu items
        self.menu_ref_eval = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_ref_eval.add_command(label='Recreate config file', command=self.recreate_ref_eval_config_file)
        self.menu_ref_eval.add_command(label='Edit config file', command=self.edit_ref_eval_config_file)
        self.menu_ref_eval.add_separator()
        self.menu_ref_eval.add_command(label='Run assembly assessment process', command=self.run_ref_eval_process)
        self.menu_ref_eval.add_separator()
        self.menu_ref_eval.add_command(label='List runs and view logs', command=self.view_ref_eval_run_logs)

        # create "menu_transrate" and add its menu items
        self.menu_transrate = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_transrate.add_command(label='Recreate config file', command=self.recreate_transrate_config_file)
        self.menu_transrate.add_command(label='Edit config file', command=self.edit_transrate_config_file)
        self.menu_transrate.add_separator()
        self.menu_transrate.add_command(label='Run assembly assessment process', command=self.run_transrate_process)
        self.menu_transrate.add_separator()
        self.menu_transrate.add_command(label='List runs and view logs', command=self.view_transrate_run_logs)

        # create "menu_assembly_assessment" and add its menu items
        self.menu_assembly_assessment = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_assembly_assessment.add_cascade(label=xlib.get_busco_name(), menu=self.menu_busco)
        self.menu_assembly_assessment.add_cascade(label='{0} ({1} package)'.format(xlib.get_gmap_name(), xlib.get_gmap_gsnap_name()), menu=self.menu_gmap)
        self.menu_assembly_assessment.add_cascade(label=xlib.get_quast_name(), menu=self.menu_quast)
        self.menu_assembly_assessment.add_cascade(label=xlib.get_rnaquast_name(), menu=self.menu_rnaquast)
        self.menu_assembly_assessment.add_cascade(label='{0} ({1} package)'.format(xlib.get_rsem_eval_name(), xlib.get_detonate_name()), menu=self.menu_rsem_eval)
        self.menu_assembly_assessment.add_cascade(label=xlib.get_transrate_name(), menu=self.menu_transrate)

        # create "menu_cd_hit_est" and add its menu items
        self.menu_cd_hit_est = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_cd_hit_est.add_command(label='Recreate config file', command=self.recreate_cd_hit_est_config_file)
        self.menu_cd_hit_est.add_command(label='Edit config file', command=self.edit_cd_hit_est_config_file)
        self.menu_cd_hit_est.add_separator()
        self.menu_cd_hit_est.add_command(label='Run transcriptome filtering process', command=self.run_cd_hit_est_process)
        self.menu_cd_hit_est.add_separator()
        self.menu_cd_hit_est.add_command(label='List runs and view logs', command=self.view_cd_hit_est_run_logs)

        # create "menu_transcript_filter" and add its menu items
        self.menu_transcript_filter = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_transcript_filter.add_command(label='Recreate config file', command=self.recreate_transcript_filter_config_file)
        self.menu_transcript_filter.add_command(label='Edit config file', command=self.edit_transcript_filter_config_file)
        self.menu_transcript_filter.add_separator()
        self.menu_transcript_filter.add_command(label='Run transcriptome filtering process', command=self.run_transcript_filter_process)
        self.menu_transcript_filter.add_separator()
        self.menu_transcript_filter.add_command(label='List runs and view logs', command=self.view_transcript_filter_run_logs)

        # create "menu_transcriptome_filtering" and add its menu items
        self.menu_transcriptome_filtering = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_transcriptome_filtering.add_cascade(label='{0} ({1} package)'.format(xlib.get_cd_hit_est_name(), xlib.get_cd_hit_name()), menu=self.menu_cd_hit_est)
        self.menu_transcriptome_filtering.add_cascade(label='{0} ({1} package)'.format(xlib.get_transcript_filter_name(), xlib.get_ngshelper_name()), menu=self.menu_transcript_filter)

        # create "menu_transcriptome_blastx" and add its menu items
        self.menu_transcriptome_blastx = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_transcriptome_blastx.add_command(label='Recreate config file', command=self.recreate_transcriptome_blastx_config_file)
        self.menu_transcriptome_blastx.add_command(label='Edit config file', command=self.edit_transcriptome_blastx_config_file)
        self.menu_transcriptome_blastx.add_separator()
        self.menu_transcriptome_blastx.add_command(label='Run annotation process', command=self.run_transcriptome_blastx_process)
        self.menu_transcriptome_blastx.add_separator()
        self.menu_transcriptome_blastx.add_command(label='List runs and view logs', command=self.view_transcriptome_blastx_run_logs)

        # create "menu_annotation" and add its menu items
        self.menu_annotation = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_annotation.add_cascade(label='{0} ({1} package)'.format(xlib.get_transcriptome_blastx_name(), xlib.get_ngshelper_name()), menu=self.menu_transcriptome_blastx)

        # create "menu_rnaseq" add add its menu items
        self.menu_rnaseq = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_rnaseq.add_cascade(label='Read quality', menu=self.menu_read_quality)
        self.menu_rnaseq.add_cascade(label='Trimming', menu=self.menu_trimming)
        self.menu_rnaseq.add_cascade(label='Digital normalization', menu=self.menu_digital_normalization)
        self.menu_rnaseq.add_separator()
        self.menu_rnaseq.add_cascade(label='De novo assembly', menu=self.menu_denovo_assembly)
        self.menu_rnaseq.add_cascade(label='Reference-based assembly', menu=self.menu_reference_based_assembly)
        self.menu_rnaseq.add_separator()
        self.menu_rnaseq.add_cascade(label='Assembly quality and transcript quantification', menu=self.menu_assembly_assessment)
        self.menu_rnaseq.add_cascade(label='Transcriptome filtering', menu=self.menu_transcriptome_filtering)
        self.menu_rnaseq.add_separator()
        self.menu_rnaseq.add_cascade(label='Annotation', menu=self.menu_annotation)

        # link "menu_rnaseq" with "menu_bar"
        self.menu_bar.add_cascade(label='RNA-seq', menu=self.menu_rnaseq)

        # create "menu_reference_file_transfer" add add its menu items
        self.menu_reference_file_transfer = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_reference_file_transfer.add_command(label='Recreate config file', command=self.recreate_reference_transfer_config_file)
        self.menu_reference_file_transfer.add_command(label='Edit config file', command=self.edit_reference_transfer_config_file)
        self.menu_reference_file_transfer.add_separator()
        self.menu_reference_file_transfer.add_command(label='Upload dataset to a cluster', command=self.upload_reference_dataset)

        # create "menu_reference_file_compression_decompression" add add its menu items
        self.menu_reference_file_compression_decompression = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_reference_file_compression_decompression.add_command(label='Recreate config file', command=self.recreate_reference_gzip_config_file)
        self.menu_reference_file_compression_decompression.add_command(label='Edit config file', command=self.edit_reference_gzip_config_file)
        self.menu_reference_file_compression_decompression.add_separator()
        self.menu_reference_file_compression_decompression.add_command(label='Run compression/decompression process', command=self.run_reference_gzip_process)

        # create "menu_database_file_transfer" add add its menu items
        self.menu_database_file_transfer = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_database_file_transfer.add_command(label='Recreate config file', command=self.recreate_database_transfer_config_file)
        self.menu_database_file_transfer.add_command(label='Edit config file', command=self.edit_database_transfer_config_file)
        self.menu_database_file_transfer.add_separator()
        self.menu_database_file_transfer.add_command(label='Upload dataset to a cluster', command=self.upload_database_dataset)

        # create "menu_database_file_compression_decompression" add add its menu items
        self.menu_database_file_compression_decompression = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_database_file_compression_decompression.add_command(label='Recreate config file', command=self.recreate_database_gzip_config_file)
        self.menu_database_file_compression_decompression.add_command(label='Edit config file', command=self.edit_database_gzip_config_file)
        self.menu_database_file_compression_decompression.add_separator()
        self.menu_database_file_compression_decompression.add_command(label='Run compression/decompression process', command=self.run_database_gzip_process)

        # create "menu_read_file_transfer" add add its menu items
        self.menu_read_file_transfer = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_read_file_transfer.add_command(label='Recreate config file', command=self.recreate_read_transfer_config_file)
        self.menu_read_file_transfer.add_command(label='Edit config file', command=self.edit_read_transfer_config_file)
        self.menu_read_file_transfer.add_separator()
        self.menu_read_file_transfer.add_command(label='Upload dataset to a cluster', command=self.upload_read_dataset)

        # create "menu_read_file_compression_decompression" add add its menu items
        self.menu_read_file_compression_decompression = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_read_file_compression_decompression.add_command(label='Recreate config file', command=self.recreate_read_gzip_config_file)
        self.menu_read_file_compression_decompression.add_command(label='Edit config file', command=self.edit_read_gzip_config_file)
        self.menu_read_file_compression_decompression.add_separator()
        self.menu_read_file_compression_decompression.add_command(label='Run compression/decompression process', command=self.run_read_gzip_process)

        # create "menu_result_file_transfer" add add its menu items
        self.menu_result_file_transfer = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_result_file_transfer.add_command(label='Recreate config file', command=self.recreate_result_transfer_config_file)
        self.menu_result_file_transfer.add_command(label='Edit config file', command=self.edit_result_transfer_config_file)
        self.menu_result_file_transfer.add_separator()
        self.menu_result_file_transfer.add_command(label='Download dataset from a cluster', command=self.download_result_dataset)

        # create "menu_result_file_compression_decompression" add add its menu items
        self.menu_result_file_compression_decompression = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_result_file_compression_decompression.add_command(label='Recreate config file', command=self.recreate_result_gzip_config_file)
        self.menu_result_file_compression_decompression.add_command(label='Edit config file', command=self.edit_result_gzip_config_file)
        self.menu_result_file_compression_decompression.add_separator()
        self.menu_result_file_compression_decompression.add_command(label='Run compression/decompression process', command=self.run_result_gzip_process)

        # create "menu_datasets" add add its menu items
        self.menu_datasets = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_datasets.add_command(label='List dataset', command=self.list_dataset)
        self.menu_datasets.add_separator()
        self.menu_datasets.add_cascade(label='Reference dataset file transfer', menu=self.menu_reference_file_transfer)
        self.menu_datasets.add_cascade(label='Reference dataset file compression/decompression', menu=self.menu_reference_file_compression_decompression)
        self.menu_datasets.add_command(label='Remove reference dataset', command=self.remove_reference_dataset)
        self.menu_datasets.add_separator()
        self.menu_datasets.add_cascade(label='Database file transfer', menu=self.menu_database_file_transfer)
        self.menu_datasets.add_cascade(label='Database file compression/decompression', menu=self.menu_database_file_compression_decompression)
        self.menu_datasets.add_command(label='Remove database', command=self.remove_database_dataset)
        self.menu_datasets.add_separator()
        self.menu_datasets.add_cascade(label='Read dataset file transfer', menu=self.menu_read_file_transfer)
        self.menu_datasets.add_cascade(label='Read dataset file compression/decompression', menu=self.menu_read_file_compression_decompression)
        self.menu_datasets.add_command(label='Remove read dataset', command=self.remove_read_dataset)
        self.menu_datasets.add_separator()
        self.menu_datasets.add_cascade(label='Result dataset file transfer', menu=self.menu_result_file_transfer)
        self.menu_datasets.add_cascade(label='Result dataset file compression/decompression', menu=self.menu_result_file_compression_decompression)
        self.menu_datasets.add_command(label='Remove result dataset', command=self.remove_result_dataset)
        self.menu_datasets.add_separator()
        self.menu_datasets.add_command(label='Remove experiment', command=self.remove_experiment)

        # link "menu_datasets" with "menu_bar"
        self.menu_bar.add_cascade(label='Datasets', menu=self.menu_datasets)

        # create "menu_logs" add add its menu items
        self.menu_logs = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_logs.add_command(label='View submission logs in the local computer', command=self.view_submission_logs)
        self.menu_logs.add_separator()
        self.menu_logs.add_command(label='View result logs in the cluster', command=self.view_result_logs)

        # link "menu_logs" with "menu_bar"
        self.menu_bar.add_cascade(label='Logs', menu=self.menu_logs)

        # create "menu_help" add add its menu items
        self.menu_help = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_help.add_command(label='View help', command=self.open_help, accelerator='F1')
        self.menu_help.add_separator()
        self.menu_help.add_command(label='About...', command=self.show_dialog_about)

        # link "menu_help" with "menu_bar"
        self.menu_bar.add_cascade(label='Help', menu=self.menu_help)

        #  assign "menu_bar" as the window menu
        self.config(menu=self.menu_bar)

    #---------------

    def exit(self, event=None):
        '''
        Exit the application.
        '''

        message = 'Are you sure to exit NGscloud?'
        if tkinter.messagebox.askyesno('{0} - Exit'.format(xlib.get_project_name()), message):
            self.destroy()

    #---------------

    def set_environment(self, event=None):
        '''
        Set the configuration corresponding to an environment.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_set_environment" in "container" with the grid geometry manager
        form_set_environment = gcloud.FormSetEnvironment(self.container, self)
        form_set_environment.grid(row=0, column=0, sticky='nsew')

        # set "form_set_environment" as current form and add it in the forms dictionary
        self.current_form = 'form_set_environment'
        self.forms_dict[self.current_form] = form_set_environment

        # raise "form_recreate_ngscloud_config_file" to front
        form_set_environment.tkraise()

    #---------------

    def recreate_ngscloud_config_file(self, event=None):
        '''
        Recreate the NGScloud config file corresponding to the environment.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_ngscloud_config_file" in "container" with the grid geometry manager
        form_recreate_ngscloud_config_file = gcloud.FormRecreateNGScloudConfigFile(self.container, self)
        form_recreate_ngscloud_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_ngscloud_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_create_ngscloud_config_file'
        self.forms_dict[self.current_form] = form_recreate_ngscloud_config_file

        # raise "form_recreate_ngscloud_config_file" to front
        form_recreate_ngscloud_config_file.tkraise()

    #---------------

    def view_ngscloud_config_file(self, event=None):
        '''
        List the NGScloud config file corresponding to the environment.
        '''

        # close the current form
        self.close_current_form()

        # get the NGScloud config file
        ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

        # create and show a instance DialogViewer to view the NGScloud config file
        dialog_viewer = gdialogs.DialogViewer(self, ngscloud_config_file)
        self.wait_window(dialog_viewer)

    #---------------

    def list_templates(self, event=None):
        '''
        List the characteristics of the cluster templates.
        '''

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Node operation - List cluster templates'

        # get the cluster template dictionary and the template name list
        template_dict = xconfiguration.get_template_dict()
        template_name_list = xconfiguration.get_template_name_list(volume_creator_included=False)

        # verify if there are any cluster template defined
        if template_dict == {}:
            message = 'There is not any cluster template defined.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), head), message)
            return

        # build the data list
        data_list = ['template_name', 'master_instance_type', 'vcpu', 'memory', 'use', 'generation']

        # build the data dictionary
        data_dict = {}
        data_dict['template_name'] = {'text': 'Template', 'width': 130, 'aligment': 'left'}
        data_dict['master_instance_type'] = {'text': 'Instance type', 'width': 130, 'aligment': 'left'}
        data_dict['vcpu'] = {'text': 'vCPUs', 'width': 50, 'aligment': 'right'}
        data_dict['memory'] = {'text': 'Memory (GiB)', 'width': 100, 'aligment': 'right'}
        data_dict['use'] = {'text': 'Use', 'width': 170, 'aligment': 'left'}
        data_dict['generation'] = {'text': 'Generation', 'width': 100, 'aligment': 'left'}

        # create the dialog Table to show the nodes running
        dialog_table = gdialogs.DialogTable(self, head, 400, 900, data_list, data_dict, template_dict)
        self.wait_window(dialog_table)

        # show warnings about characteristics and pricing
        message = 'You can consult the characteristics of the EC2 intance types in:\n\n'
        message += 'https://aws.amazon.com/ec2/instance-types/\n\n'
        message += 'and the EC2 pricing is detailed in:\n\n'
        message += 'https://aws.amazon.com/ec2/pricing/'
        tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def update_connection_data(self, event=None):
        '''
        Update the user id, access key id,  secret access key and contact e-mail address
        in the NGScloud config file corresponding to the environment.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_update_connection_data" in "container" with the grid geometry manager
        form_update_connection_data = gcloud.FormUpdateConnectionData(self.container, self)
        form_update_connection_data.grid(row=0, column=0, sticky='nsew')

        # set "form_create_update_connection_data" as current form and add it in the forms dictionary
        self.current_form = 'form_create_update_connection_data'
        self.forms_dict[self.current_form] = form_update_connection_data

        # raise "form_update_connection_data" to front
        form_update_connection_data.tkraise()

    #---------------

    def update_region_zone(self, event=None):
        '''
        Update the current region and zone names in the NGScloud config file
        corresponding to the environment.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_update_region_zone" in "container" with the grid geometry manager
        form_update_region_zone = gcloud.FormUpdateRegionZone(self.container, self)
        form_update_region_zone.grid(row=0, column=0, sticky='nsew')

        # set "form_update_region_zone" as current form and add it in the forms dictionary
        self.current_form = 'form_update_region_zone'
        self.forms_dict[self.current_form] = form_update_region_zone

        # raise "form_update_region_zone" to front
        form_update_region_zone.tkraise()

    #---------------

    def link_volume_to_template(self, event=None):
        '''
        Link a volume to a cluster template
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_link_volume_to_template" in "container" with the grid geometry manager
        form_link_volume_to_template = gcloud.FormLinkVolumeToTemplate(self.container, self)
        form_link_volume_to_template.grid(row=0, column=0, sticky='nsew')

        # set "form_link_volume_to_template" as current form and add it in the forms dictionary
        self.current_form = 'form_link_volume_to_template'
        self.forms_dict[self.current_form] = form_link_volume_to_template

        # raise "form_link_volume_to_template" to front
        form_link_volume_to_template.tkraise()

    #---------------

    def delink_volume_from_template(self, event=None):
        '''
        Delink a volume from a cluster template
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_delink_volume_to_template" in "container" with the grid geometry manager
        form_delink_volume_to_template = gcloud.FormDelinkVolumeFromTemplate(self.container, self)
        form_delink_volume_to_template.grid(row=0, column=0, sticky='nsew')

        # set "form_delink_volume_to_template" as current form and add it in the forms dictionary
        self.current_form = 'form_delink_volume_to_template'
        self.forms_dict[self.current_form] = form_delink_volume_to_template

        # raise "form_delink_volume_to_template" to front
        form_delink_volume_to_template.tkraise()

    #---------------

    def review_volume_links(self, event=None):
        '''
        Review linked volumes of cluster templates in order to remove linked volumes
        that do not currently exist.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Configuration - Review volumes linked to cluster templates'

        # get the NGScloud confign file
        ngscloud_config_file = xconfiguration.get_ngscloud_config_file()

        # verify if there are any volumes linked
        if xconfiguration.get_volumes_dict() == {}:
            message = 'There is not any volume linked.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), head), message)
            return

        # confirm the review of volumes links
        message = 'The file {0} is going to be reviewed in order to remove volumes linked which are not currently created in the zone {1}.\n\nAre you sure to continue?'.format(ngscloud_config_file, xconfiguration.get_current_zone_name())
        OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), head), message)

        # review volumen link
        if OK:
            dialog_log = gdialogs.DialogLog(self, head, xconfiguration.review_volume_links.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xconfiguration.review_volume_links, args=(xconfiguration.get_current_zone_name(), dialog_log, lambda: dialog_log.enable_button_close())).start()

    #---------------

    def list_keypairs(self, event=None):
        '''
        List the key pairs of a region.
        '''

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Security -  List key pairs'

        # get key pair dictionary
        keypairs_dict = xec2.get_keypair_dict(xconfiguration.get_current_region_name())

        # verify if there are any key pairs createdview_ngscloud_config_file
        if keypairs_dict == {}:
            message = 'There is not any key pair created in region {0}.'.format(xconfiguration.get_current_region_name())
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), head), message)
            return

        # build the data list
        data_list = ['keypair_name', 'fingerprint']

        # build the data dictionary
        data_dict = {}
        data_dict['keypair_name'] = {'text': 'Key Pair Name', 'width': 250, 'aligment': 'left'}
        data_dict['fingerprint'] = {'text': 'Fingerprint', 'width': 590, 'aligment': 'left'}

        # create the dialog Table to show the volumes created
        dialog_table = gdialogs.DialogTable(self, '{0} in region {1}'.format(head, xconfiguration.get_current_region_name()), 400, 900, data_list, data_dict, keypairs_dict)
        self.wait_window(dialog_table)

    #---------------

    def create_keypairs(self, event=None):
        '''
        Create all the key pairs of a region.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Security - Create key pairs'

        # confirm the creation of the key pairs
        message = 'The key pairs of the region {0} are going to be created.\n\nAre you sure to continue?'.format(xconfiguration.get_current_region_name())
        OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), head), message)

        # create key pairs
        if OK:
            (OK, error_list) = xec2.create_keypairs(xconfiguration.get_current_region_name())
            if OK:
                message = 'The key pairs and their corresponding local files of the region {0} file are created.'.format(xconfiguration.get_current_region_name())
                tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
            else:
                message = ''
                for error in error_list:
                    message = '{0}{1}\n'.format(message, error) 
                tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def list_clusters(self, event=None):
        '''
        List clusters.
        '''

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Cluster operation - List clusters'

        # list clusters
        dialog_log = gdialogs.DialogLog(self, head, xcluster.list_clusters.__name__)
        threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
        threading.Thread(target=xcluster.list_clusters, args=(dialog_log, lambda: dialog_log.enable_button_close())).start()

    #---------------

    def create_cluster(self, event=None):
        '''
        Create a cluster from a template name.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_create_cluster" in "container" with the grid geometry manager
        form_create_cluster = gcloud.FormCreateCluster(self.container, self)
        form_create_cluster.grid(row=0, column=0, sticky='nsew')

        # set "form_create_cluster" as current form and add it in the forms dictionary
        self.current_form = 'form_create_cluster'
        self.forms_dict[self.current_form] = form_create_cluster

        # raise "form_create_cluster" to front
        form_create_cluster.tkraise()

    #---------------

    def stop_cluster(self, event=None):
        '''
        Stop, but not terminate, a cluster.Then it must be restarted.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_stop_cluster" in "container" with the grid geometry manager
        form_stop_cluster = gcloud.FormStopCluster(self.container, self)
        form_stop_cluster.grid(row=0, column=0, sticky='nsew')

        # set "form_stop_cluster" as current form and add it in the forms dictionary
        self.current_form = 'form_stop_cluster'
        self.forms_dict[self.current_form] = form_stop_cluster

        # raise "form_stop_cluster" to front
        form_stop_cluster.tkraise()

    #---------------

    def restart_cluster(self, event=None):
        '''
        Restart a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_restart_cluster" in "container" with the grid geometry manager
        form_restart_cluster = gcloud.FormRestartCluster(self.container, self)
        form_restart_cluster.grid(row=0, column=0, sticky='nsew')

        # set "form_restart_cluster" as current form and add it in the forms dictionary
        self.current_form = 'form_restart_cluster'
        self.forms_dict[self.current_form] = form_restart_cluster

        # raise "form_restart_cluster" to front
        form_restart_cluster.tkraise()

    #---------------

    def terminate_cluster(self, event=None):
        '''
        Terminate a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_terminate_cluster" in "container" with the grid geometry manager
        form_terminate_cluster = gcloud.FormTerminateCluster(self.container, self, force=False)
        form_terminate_cluster.grid(row=0, column=0, sticky='nsew')

        # set "form_terminate_cluster" as current form and add it in the forms dictionary
        self.current_form = 'form_terminate_cluster'
        self.forms_dict[self.current_form] = form_terminate_cluster

        # raise "form_terminate_cluster" to front
        form_terminate_cluster.tkraise()

    #---------------

    def force_cluster_termination(self, event=None):
        '''
        Force the termination of a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_force_cluster_termination" in "container" with the grid geometry manager
        form_force_cluster_termination = gcloud.FormTerminateCluster(self.container, self, force=True)
        form_force_cluster_termination.grid(row=0, column=0, sticky='nsew')

        # set "form_force_cluster_termination" as current form and add it in the forms dictionary
        self.current_form = 'form_force_cluster_termination'
        self.forms_dict[self.current_form] = form_force_cluster_termination

        # raise "form_force_cluster_termination" to front
        form_force_cluster_termination.tkraise()

    #---------------

    def show_cluster_composing(self, event=None):
        '''
        Show cluster information of every node: OS, CPU number and memory.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_show_cluster_composing" in "container" with the grid geometry manager
        form_show_cluster_composing = gcloud.FormShowClusterComposing(self.container, self)
        form_show_cluster_composing.grid(row=0, column=0, sticky='nsew')

        # set "form_show_cluster_composing" as current form and add it in the forms dictionary
        self.current_form = 'form_show_cluster_composing'
        self.forms_dict[self.current_form] = form_show_cluster_composing

        # raise "form_show_cluster_composing" to front
        form_show_cluster_composing.tkraise()

    #---------------

    def show_status_batch_jobs(self, event=None):
        '''
        Show the status of batch jobs in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_show_status_batch_jobs" in "container" with the grid geometry manager
        form_show_status_batch_jobs = gcloud.FormShowStatusBatchJobs(self.container, self)
        form_show_status_batch_jobs.grid(row=0, column=0, sticky='nsew')

        # set "form_show_status_batch_jobs" as current form and add it in the forms dictionary
        self.current_form = 'form_show_status_batch_jobs'
        self.forms_dict[self.current_form] = form_show_status_batch_jobs

        # raise "form_show_status_batch_jobs" to front
        form_show_status_batch_jobs.tkraise()

    #---------------

    def kill_batch_job(self, event=None):
        '''
        Kill a batch job in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_kill_batch_job" in "container" with the grid geometry manager
        form_kill_batch_job = gcloud.FormKillBatchJob(self.container, self)
        form_kill_batch_job.grid(row=0, column=0, sticky='nsew')

        # set "form_kill_batch_job" as current form and add it in the forms dictionary
        self.current_form = 'form_kill_batch_job'
        self.forms_dict[self.current_form] = form_kill_batch_job

        # raise "form_kill_batch_job" to front
        form_kill_batch_job.tkraise()

    #---------------

    def list_nodes(self, event=None):
        '''
        List nodes running.
        '''

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Node operation - List nodes'

        # get the node dictionary
        node_dict = xec2.get_node_dict()

        # verify if there are any nodes running
        if node_dict == {}:
            message = 'There is not any node running.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), head), message)
            return

        # build the data list
        data_list = ['security_group_name', 'zone_name', 'node_name', 'node_id', 'state']

        # build the data dictionary
        data_dict = {}
        data_dict['security_group_name'] = {'text': 'Security Group Name', 'width': 200, 'aligment': 'left'}
        data_dict['zone_name'] = {'text': 'Zone', 'width': 100, 'aligment': 'left'}
        data_dict['node_name'] = {'text': 'Node Name', 'width': 200, 'aligment': 'left'}
        data_dict['node_id'] = {'text': 'Node Id', 'width': 190, 'aligment': 'left'}
        data_dict['state'] = {'text': 'State', 'width': 150, 'aligment': 'left'}

        # create the dialog Table to show the nodes running
        dialog_table = gdialogs.DialogTable(self, head, 400, 900, data_list, data_dict, node_dict)
        self.wait_window(dialog_table)

    #---------------

    def add_node(self, event=None):
        '''
        Add a node in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_add_node" in "container" with the grid geometry manager
        form_add_node = gcloud.FormAddNode(self.container, self)
        form_add_node.grid(row=0, column=0, sticky='nsew')

        # set "form_add_node" as current form and add it in the forms dictionary
        self.current_form = 'form_add_node'
        self.forms_dict[self.current_form] = form_add_node

        # raise "form_add_node" to front
        form_add_node.tkraise()

    #---------------

    def remove_node(self, event=None):
        '''
        Remove a node in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_remove_node" in "container" with the grid geometry manager
        form_remove_node = gcloud.FormRemoveNode(self.container, self)
        form_remove_node.grid(row=0, column=0, sticky='nsew')

        # set "form_remove_node" as current form and add it in the forms dictionary
        self.current_form = 'form_remove_node'
        self.forms_dict[self.current_form] = form_remove_node

        # raise "form_remove_node" to front
        form_remove_node.tkraise()

    #---------------

    def list_volumes(self, event=None):
        '''
        List volumes created.
        '''

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Volume operation - List volumes'

        # get the volume dictionary
        volumes_dict = xec2.get_volume_dict()

        # verify if there are any volumes created
        if volumes_dict == {}:
            message = 'There is not any volume created.'
            tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), head), message)
            return

        # build the data list
        data_list = ['zone_name', 'volume_name', 'volume_id', 'size', 'state', 'attachments_number']

        # build the data dictionary
        data_dict = {}
        data_dict['zone_name'] = {'text': 'Zone', 'width': 100, 'aligment': 'left'}
        data_dict['volume_name'] = {'text': 'Volume Name', 'width': 200, 'aligment': 'left'}
        data_dict['volume_id'] = {'text': 'Volume Id', 'width': 210, 'aligment': 'left'}
        data_dict['size'] = {'text': 'Size (GiB)', 'width': 75, 'aligment': 'right'}
        data_dict['state'] = {'text': 'State', 'width': 100, 'aligment': 'left'}
        data_dict['attachments_number'] = {'text': 'Attachments', 'width': 110, 'aligment': 'right'}

        # create the dialog Table to show the volumes created
        dialog_table = gdialogs.DialogTable(self, head, 400, 900, data_list, data_dict, volumes_dict)
        self.wait_window(dialog_table)

    #---------------

    def create_volume(self, event=None):
        '''
        Create a volume in the current zone.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_create_volume" in "container" with the grid geometry manager
        form_create_volume = gcloud.FormCreateVolume(self.container, self)
        form_create_volume.grid(row=0, column=0, sticky='nsew')

        # set "form_create_volume" as current form and add it in the forms dictionary
        self.current_form = 'form_create_volume'
        self.forms_dict[self.current_form] = form_create_volume

        # raise "form_create_volume" to front
        form_create_volume.tkraise()

    #---------------

    def remove_volume(self, event=None):
        '''
        Remove a volume in the current zone.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_remove_volume" in "container" with the grid geometry manager
        form_remove_volume = gcloud.FormRemoveVolume(self.container, self)
        form_remove_volume.grid(row=0, column=0, sticky='nsew')

        # set "form_remove_volume" as current form and add it in the forms dictionary
        self.current_form = 'form_remove_volume'
        self.forms_dict[self.current_form] = form_remove_volume

        # raise "form_remove_volume" to front
        form_remove_volume.tkraise()

    #---------------

    def terminate_volume_creator(self, event=None):
        '''
        Terminate de volume creator of the current zone.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Volume operation - Terminate volume creator'

        # confirm the review of volumes links
        message = 'The volume creator is going to be terminated.\n\nAre you sure to continue?'
        OK = tkinter.messagebox.askyesno('{0} - {1}'.format(xlib.get_project_name(), head), message)

        # review volumen link
        if OK:
            dialog_log = gdialogs.DialogLog(self, head, xcluster.terminate_cluster.__name__)
            threading.Thread(target=self.wait_window, args=(dialog_log,)).start()
            threading.Thread(target=xcluster.terminate_cluster, args=(xlib.get_volume_creator_name(), True, dialog_log, lambda: dialog_log.enable_button_close())).start()

    #---------------

    def mount_volume(self, event=None):
        '''
        Mount a volume in a node.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_mount_volume" in "container" with the grid geometry manager
        form_mount_volume = gcloud.FormMountVolume(self.container, self)
        form_mount_volume.grid(row=0, column=0, sticky='nsew')

        # set "form_mount_volume" as current form and add it in the forms dictionary
        self.current_form = 'form_mount_volume'
        self.forms_dict[self.current_form] = form_mount_volume

        # raise "form_mount_volume" to front
        form_mount_volume.tkraise()

    #---------------

    def unmount_volume(self, event=None):
        '''
        Unmount a volume in a node.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_unmount_volume" in "container" with the grid geometry manager
        form_unmount_volume = gcloud.FormUnmountVolume(self.container, self)
        form_unmount_volume.grid(row=0, column=0, sticky='nsew')

        # set "form_unmount_volume" as current form and add it in the forms dictionary
        self.current_form = 'form_unmount_volume'
        self.forms_dict[self.current_form] = form_unmount_volume

        # raise "form_unmount_volume" to front
        form_unmount_volume.tkraise()

    #---------------

    def setup_miniconda3(self, event=None):
        '''
        Set up the Miniconda3 in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_miniconda3" in "container" with the grid geometry manager
        form_setup_miniconda3 = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_miniconda3_code())
        form_setup_miniconda3.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_miniconda3" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_miniconda3'
        self.forms_dict[self.current_form] = form_setup_miniconda3

        # raise "form_setup_miniconda3" to front
        form_setup_miniconda3.tkraise()

    #---------------

    def setup_blastplus(self, event=None):
        '''
        Set up the BLAST+ in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_blastplus" in "container" with the grid geometry manager
        form_setup_blastplus = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_blastplus_code())
        form_setup_blastplus.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_blastplus" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_blastplus'
        self.forms_dict[self.current_form] = form_setup_blastplus

        # raise "form_setup_blastplus" to front
        form_setup_blastplus.tkraise()

    #---------------

    def setup_busco(self, event=None):
        '''
        Set up the BUSCO in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_busco" in "container" with the grid geometry manager
        form_setup_busco = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_busco_code())
        form_setup_busco.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_busco" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_busco'
        self.forms_dict[self.current_form] = form_setup_busco

        # raise "form_setup_busco" to front
        form_setup_busco.tkraise()

    #---------------

    def setup_cd_hit(self, event=None):
        '''
        Set up the CD-HIT in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_cd_hit" in "container" with the grid geometry manager
        form_setup_cd_hit = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_cd_hit_code())
        form_setup_cd_hit.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_cd_hit" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_cd_hit'
        self.forms_dict[self.current_form] = form_setup_cd_hit

        # raise "form_setup_cd_hit" to front
        form_setup_cd_hit.tkraise()

    #---------------

    def setup_detonate(self, event=None):
        '''
        Set up the DETONATE in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_detonate" in "container" with the grid geometry manager
        form_setup_detonate = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_detonate_code())
        form_setup_detonate.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_detonate" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_detonate'
        self.forms_dict[self.current_form] = form_setup_detonate

        # raise "form_setup_detonate" to front
        form_setup_detonate.tkraise()

    #---------------

    def setup_fastqc(self, event=None):
        '''
        Set up the FastQC software in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_fastqc" in "container" with the grid geometry manager
        form_setup_fastqc = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_fastqc_code())
        form_setup_fastqc.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_fastqc" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_fastqc'
        self.forms_dict[self.current_form] = form_setup_fastqc

        # raise "form_setup_fastqc" to front
        form_setup_fastqc.tkraise()

    #---------------

    def setup_gmap_gsnap(self, event=None):
        '''
        Set up the GMAP-GSNAP in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_gmap_gsnap" in "container" with the grid geometry manager
        form_setup_gmap_gsnap = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_gmap_gsnap_code())
        form_setup_gmap_gsnap.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_gmap_gsnap" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_gmap_gsnap'
        self.forms_dict[self.current_form] = form_setup_gmap_gsnap

        # raise "form_setup_gmap_gsnap" to front
        form_setup_gmap_gsnap.tkraise()

    #---------------

    def setup_ngshelper(self, event=None):
        '''
        Set up the NGShelper in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_ngshelper" in "container" with the grid geometry manager
        form_setup_ngshelper = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_ngshelper_code())
        form_setup_ngshelper.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_ngshelper" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_ngshelper'
        self.forms_dict[self.current_form] = form_setup_ngshelper

        # raise "form_setup_ngshelper" to front
        form_setup_ngshelper.tkraise()

    #---------------

    def setup_quast(self, event=None):
        '''
        Set up the QUAST in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_quast" in "container" with the grid geometry manager
        form_setup_quast = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_quast_code())
        form_setup_quast.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_quast" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_quast'
        self.forms_dict[self.current_form] = form_setup_quast

        # raise "form_setup_quast" to front
        form_setup_quast.tkraise()

    #---------------

    def setup_rnaquast(self, event=None):
        '''
        Set up the rnaQUAST in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_rnaquast" in "container" with the grid geometry manager
        form_setup_rnaquast = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_rnaquast_code())
        form_setup_rnaquast.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_rnaquast" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_rnaquast'
        self.forms_dict[self.current_form] = form_setup_rnaquast

        # raise "form_setup_rnaquast" to front
        form_setup_rnaquast.tkraise()

    #---------------

    def setup_soapdenovotrans(self, event=None):
        '''
        Set up the SOAPdenovo-Trans software in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_soapdenovotrans" in "container" with the grid geometry manager
        form_setup_soapdenovotrans = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_soapdenovotrans_code())
        form_setup_soapdenovotrans.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_soapdenovotrans" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_soapdenovotrans'
        self.forms_dict[self.current_form] = form_setup_soapdenovotrans

        # raise "form_setup_bioinfoapp" to front
        form_setup_soapdenovotrans.tkraise()

    #---------------

    def setup_star(self, event=None):
        '''
        Set up the STAR in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_star" in "container" with the grid geometry manager
        form_setup_star = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_star_code())
        form_setup_star.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_star" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_star'
        self.forms_dict[self.current_form] = form_setup_star

        # raise "form_setup_star" to front
        form_setup_star.tkraise()

    #---------------

    def setup_transabyss(self, event=None):
        '''
        Set up the Trans-ABySS in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_transabyss" in "container" with the grid geometry manager
        form_setup_transabyss = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_transabyss_code())
        form_setup_transabyss.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_transabyss" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_transabyss'
        self.forms_dict[self.current_form] = form_setup_transabyss

        # raise "form_setup_transabyss" to front
        form_setup_transabyss.tkraise()

    #---------------

    def setup_transrate(self, event=None):
        '''
        Set up the Transrate in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_transrate" in "container" with the grid geometry manager
        form_setup_transrate = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_transrate_code())
        form_setup_transrate.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_transrate" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_transrate'
        self.forms_dict[self.current_form] = form_setup_transrate

        # raise "form_setup_transrate" to front
        form_setup_transrate.tkraise()

    #---------------

    def setup_trimmomatic(self, event=None):
        '''
        Set up the Trimmomatic software in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_trimmomatic" in "container" with the grid geometry manager
        form_setup_trimmomatic = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_trimmomatic_code())
        form_setup_trimmomatic.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_trimmomatic" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_trimmomatic'
        self.forms_dict[self.current_form] = form_setup_trimmomatic

        # raise "form_create_cluster" to front
        form_setup_trimmomatic.tkraise()

    #---------------

    def setup_trinity(self, event=None):
        '''
        Set up the Trinity in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_trinity" in "container" with the grid geometry manager
        form_setup_trinity = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_trinity_code())
        form_setup_trinity.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_trinity" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_trinity'
        self.forms_dict[self.current_form] = form_setup_trinity

        # raise "form_setup_trinity" to front
        form_setup_trinity.tkraise()

    #---------------

    def setup_r(self, event=None):
        '''
        Set up the R in the cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_setup_r" in "container" with the grid geometry manager
        form_setup_r = gbioinfoapp.FormSetupBioinfoApp(self.container, self, app=xlib.get_r_code())
        form_setup_r.grid(row=0, column=0, sticky='nsew')

        # set "form_setup_r" as current form and add it in the forms dictionary
        self.current_form = 'form_setup_r'
        self.forms_dict[self.current_form] = form_setup_r

        # raise "form_setup_r" to front
        form_setup_r.tkraise()

    #---------------

    def open_terminal(self, event=None):
        '''
        Open a terminal windows of a node cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_open_terminal" in "container" with the grid geometry manager
        form_open_terminal = gcloud.FormOpenTerminal(self.container, self)
        form_open_terminal.grid(row=0, column=0, sticky='nsew')

        # set "form_open_terminal" as current form and add it in the forms dictionary
        self.current_form = 'form_open_terminal'
        self.forms_dict[self.current_form] = form_open_terminal

        # raise "form_open_terminal" to front
        form_open_terminal.tkraise()

    #---------------

    def recreate_fastqc_config_file(self, event=None):
        '''
        Recreate the FastQC config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_fastqc_config_file" in "container" with the grid geometry manager
        form_recreate_fastqc_config_file = gbioinfoapp.FormRecreateFastQCConfigFile(self.container, self)
        form_recreate_fastqc_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_fastqc_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_fastqc_config_file'
        self.forms_dict[self.current_form] = form_recreate_fastqc_config_file

        # raise "form_recreate_fastqc_config_file" to front
        form_recreate_fastqc_config_file.tkraise()

    #---------------

    def edit_fastqc_config_file(self, event=None):
        '''
        Edit the FastQC config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_fastqc_name())

        # edit the FastQC config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xfastqc.get_fastqc_config_file())
        self.wait_window(dialog_editor)

        # validate the FastQC config file
        (OK, error_list) = xfastqc.validate_fastqc_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_fastqc_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_fastqc_process(self, event=None):
        '''
        Run a FastQC process corresponding to the options in FastQC config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_fastqc_process" in "container" with the grid geometry manager
        form_run_fastqc_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_fastqc_code())
        form_run_fastqc_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_fastqc_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_fastqc_process'
        self.forms_dict[self.current_form] = form_run_fastqc_process

        # raise "form_run_fastqc_process" to front
        form_run_fastqc_process.tkraise()

    #---------------

    def view_fastqc_run_logs(self, event=None):
        '''
        List the FastQC process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_fastqc_run_logs" in "container" with the grid geometry manager
        form_view_fastqc_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_fastqc_code())
        form_view_fastqc_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_fastqc_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_fastqc_run_logs'
        self.forms_dict[self.current_form] = form_view_fastqc_run_logs

        # raise "form_view_fastqc_run_logs" to front
        form_view_fastqc_run_logs.tkraise()

    #---------------

    def recreate_trimmomatic_config_file(self, event=None):
        '''
        Recreate the Trimmomatic config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_trimmomatic_config_file" in "container" with the grid geometry manager
        form_recreate_trimmomatic_config_file = gbioinfoapp.FormRecreateTrimmomaticConfigFile(self.container, self)
        form_recreate_trimmomatic_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_trimmomatic_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_trimmomatic_config_file'
        self.forms_dict[self.current_form] = form_recreate_trimmomatic_config_file

        # raise "form_recreate_trimmomatic_config_file" to front
        form_recreate_trimmomatic_config_file.tkraise()

    #---------------

    def edit_trimmomatic_config_file(self, event=None):
        '''
        Edit the Trimmomatic config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_trimmomatic_name())

        # edit the Trimmomatic config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xtrimmomatic.get_trimmomatic_config_file())
        self.wait_window(dialog_editor)

        # validate the Trimmomatic config file
        (OK, error_list) = xtrimmomatic.validate_trimmomatic_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_trimmomatic_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_trimmomatic_process(self, event=None):
        '''
        Run a Trimmomatic process corresponding to the options in Trimmomatic config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_trimmomatic_process" in "container" with the grid geometry manager
        form_run_trimmomatic_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_trimmomatic_code())
        form_run_trimmomatic_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_trimmomatic_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_trimmomatic_process'
        self.forms_dict[self.current_form] = form_run_trimmomatic_process

        # raise "form_run_trimmomatic_process" to front
        form_run_trimmomatic_process.tkraise()

    #---------------

    def view_trimmomatic_run_logs(self, event=None):
        '''
        List the Trimmomatic process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_trimmomatic_run_logs" in "container" with the grid geometry manager
        form_view_trimmomatic_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_trimmomatic_code())
        form_view_trimmomatic_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_trimmomatic_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'view_trimmomatic_run_logs'
        self.forms_dict[self.current_form] = form_view_trimmomatic_run_logs

        # raise "form_view_trimmomatic_run_logs" to front
        form_view_trimmomatic_run_logs.tkraise()

    #---------------

    def recreate_insilico_read_normalization_config_file(self, event=None):
        '''
        Create the insilico_read_normalization config file with the default options. It is necessary
        update the options in process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_insilico_read_normalization_config_file" in "container" with the grid geometry manager
        form_recreate_insilico_read_normalization_config_file = gbioinfoapp.FormRecreateInsilicoReadNormalizationConfigFile(self.container, self)
        form_recreate_insilico_read_normalization_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_insilico_read_normalization_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_insilico_read_normalization_config_file'
        self.forms_dict[self.current_form] = form_recreate_insilico_read_normalization_config_file

        # raise "form_recreate_insilico_read_normalization_config_file" to front
        form_recreate_insilico_read_normalization_config_file.tkraise()

    #---------------

    def edit_insilico_read_normalization_config_file(self, event=None):
        '''
        Edit the insilico_read_normalization config file to change the parameters of process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_insilico_read_normalization_name())

        # edit the insilico_read_normalization config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xtrinity.get_insilico_read_normalization_config_file())
        self.wait_window(dialog_editor)

        # validate the insilico_read_normalization config file
        (OK, error_list) = xtrinity.validate_insilico_read_normalization_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_insilico_read_normalization_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_insilico_read_normalization_process(self, event=None):
        '''
        Run a insilico_read_normalization process corresponding to the options in insilico_read_normalization config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_insilico_read_normalization_process" in "container" with the grid geometry manager
        form_run_insilico_read_normalization_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_insilico_read_normalization_code())
        form_run_insilico_read_normalization_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_insilico_read_normalization_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_insilico_read_normalization_process'
        self.forms_dict[self.current_form] = form_run_insilico_read_normalization_process

        # raise "form_run_insilico_read_normalization_process" to front
        form_run_insilico_read_normalization_process.tkraise()

    #---------------

    def view_insilico_read_normalization_run_logs(self, event=None):
        '''
        List the insilico_read_normalization process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_insilico_read_normalization_run_logs" in "container" with the grid geometry manager
        form_view_insilico_read_normalization_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_insilico_read_normalization_code())
        form_view_insilico_read_normalization_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_insilico_read_normalization_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_insilico_read_normalization_run_logs'
        self.forms_dict[self.current_form] = form_view_insilico_read_normalization_run_logs

        # raise "form_view_insilico_read_normalization_run_logs" to front
        form_view_insilico_read_normalization_run_logs.tkraise()

    #---------------

    def recreate_soapdenovotrans_config_file(self, event=None):
        '''
        Recreate the SOAPdenovo-Trans config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_soapdenovotrans_config_file" in "container" with the grid geometry manager
        form_recreate_soapdenovotrans_config_file = gbioinfoapp.FormRecreateSoapdenovoTransConfigFile(self.container, self)
        form_recreate_soapdenovotrans_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_soapdenovotrans_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_soapdenovotrans_config_file'
        self.forms_dict[self.current_form] = form_recreate_soapdenovotrans_config_file

        # raise "form_recreate_soapdenovotrans_config_file" to front
        form_recreate_soapdenovotrans_config_file.tkraise()

    #---------------

    def edit_soapdenovotrans_config_file(self, event=None):
        '''
        Edit the SOAPdenovo-Trans config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_soapdenovotrans_name())

        # edit the SOAPdenovo-Trans config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xsoapdenovotrans.get_soapdenovotrans_config_file())
        self.wait_window(dialog_editor)

        # validate the SOAPdenovo-Trans config file
        (OK, error_list) = xsoapdenovotrans.validate_soapdenovotrans_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_soapdenovotrans_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_soapdenovotrans_process(self, event=None):
        '''
        Run a SOAPdenovo-Trans process corresponding to the options in SOAPdenovo-Trans config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_soapdenovotrans_process" in "container" with the grid geometry manager
        form_run_soapdenovotrans_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_soapdenovotrans_code())
        form_run_soapdenovotrans_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_soapdenovotrans_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_soapdenovotrans_process'
        self.forms_dict[self.current_form] = form_run_soapdenovotrans_process

        # raise "form_run_soapdenovotrans_process" to front
        form_run_soapdenovotrans_process.tkraise()

    #---------------

    def view_soapdenovotrans_run_logs(self, event=None):
        '''
        List the SOAPdenovo-Trans process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_soapdenovotrans_run_logs" in "container" with the grid geometry manager
        form_view_soapdenovotrans_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_soapdenovotrans_code())
        form_view_soapdenovotrans_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_soapdenovotrans_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_soapdenovotrans_run_logs'
        self.forms_dict[self.current_form] = form_view_soapdenovotrans_run_logs

        # raise "form_view_soapdenovotrans_run_logs" to front
        form_view_soapdenovotrans_run_logs.tkraise()

    #---------------

    def recreate_transabyss_config_file(self, event=None):
        '''
        Recreate the Trans-ABySS config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_transabyss_config_file" in "container" with the grid geometry manager
        form_recreate_transabyss_config_file = gbioinfoapp.FormRecreateTransAbyssConfigFile(self.container, self)
        form_recreate_transabyss_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_transabyss_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_transabyss_config_file'
        self.forms_dict[self.current_form] = form_recreate_transabyss_config_file

        # raise "form_recreate_transabyss_config_file" to front
        form_recreate_transabyss_config_file.tkraise()

    #---------------

    def edit_transabyss_config_file(self, event=None):
        '''
        Edit the Trans-ABySS config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_transabyss_name())

        # edit the Trans-ABySS config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xtransabyss.get_transabyss_config_file())
        self.wait_window(dialog_editor)

        # validate the Trans-ABySS config file
        (OK, error_list) = xtransabyss.validate_transabyss_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_transabyss_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_transabyss_process(self, event=None):
        '''
        Run a Trans-ABySS process corresponding to the options in Trans-ABySS config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_transabyss_process" in "container" with the grid geometry manager
        form_run_transabyss_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_transabyss_code())
        form_run_transabyss_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_transabyss_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_transabyss_process'
        self.forms_dict[self.current_form] = form_run_transabyss_process

        # raise "form_run_transabyss_process" to front
        form_run_transabyss_process.tkraise()

    #---------------

    def view_transabyss_run_logs(self, event=None):
        '''
        List the Trans-ABySS process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_transabyss_run_logs" in "container" with the grid geometry manager
        form_view_transabyss_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_transabyss_code())
        form_view_transabyss_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_transabyss_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_transabyss_run_logs'
        self.forms_dict[self.current_form] = form_view_transabyss_run_logs

        # raise "form_view_transabyss_run_logs" to front
        form_view_transabyss_run_logs.tkraise()

    #---------------

    def recreate_trinity_config_file(self, event=None):
        '''
        Create the Trinity config file with the default options. It is necessary
        update the options in process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_trinity_config_file" in "container" with the grid geometry manager
        form_recreate_trinity_config_file = gbioinfoapp.FormRecreateTrinityConfigFile(self.container, self)
        form_recreate_trinity_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_trinity_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_trinity_config_file'
        self.forms_dict[self.current_form] = form_recreate_trinity_config_file

        # raise "form_recreate_trinity_config_file" to front
        form_recreate_trinity_config_file.tkraise()

    #---------------

    def edit_trinity_config_file(self, event=None):
        '''
        Edit the Trinity config file to change the parameters of process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_trinity_name())

        # edit the Trinity config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xtrinity.get_trinity_config_file())
        self.wait_window(dialog_editor)

        # validate the Trinity config file
        (OK, error_list) = xtrinity.validate_trinity_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_trinity_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_trinity_process(self, event=None):
        '''
        Run a Trinity process corresponding to the options in Trinity config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_trinity_process" in "container" with the grid geometry manager
        form_run_trinity_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_trinity_code())
        form_run_trinity_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_trinity_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_trinity_process'
        self.forms_dict[self.current_form] = form_run_trinity_process

        # raise "form_run_trinity_process" to front
        form_run_trinity_process.tkraise()

    #---------------

    def view_trinity_run_logs(self, event=None):
        '''
        List the Trinity process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_trinity_run_logs" in "container" with the grid geometry manager
        form_view_trinity_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_trinity_code())
        form_view_trinity_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_trinity_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_trinity_run_logs'
        self.forms_dict[self.current_form] = form_view_trinity_run_logs

        # raise "form_view_trinity_run_logs" to front
        form_view_trinity_run_logs.tkraise()

    #---------------

    def recreate_star_config_file(self, event=None):
        '''
        Recreate the STAR config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_star_config_file" in "container" with the grid geometry manager
        form_recreate_star_config_file = gbioinfoapp.FormRecreateSTARConfigFile(self.container, self)
        form_recreate_star_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_star_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_star_config_file'
        self.forms_dict[self.current_form] = form_recreate_star_config_file

        # raise "form_recreate_star_config_file" to front
        form_recreate_star_config_file.tkraise()

    #---------------

    def edit_star_config_file(self, event=None):
        '''
        Edit the STAR config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_star_name())

        # edit the STAR config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xstar.get_star_config_file())
        self.wait_window(dialog_editor)

        # validate the STAR config file
        (OK, error_list) = xstar.validate_star_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_star_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_star_process(self, event=None):
        '''
        Run a STAR process corresponding to the options in STAR config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_star_process" in "container" with the grid geometry manager
        form_run_star_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_star_code())
        form_run_star_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_star_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_star_process'
        self.forms_dict[self.current_form] = form_run_star_process

        # raise "form_run_star_process" to front
        form_run_star_process.tkraise()

    #---------------

    def view_star_run_logs(self, event=None):
        '''
        List the STAR process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_star_run_logs" in "container" with the grid geometry manager
        form_view_star_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_star_code())
        form_view_star_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_star_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_star_run_logs'
        self.forms_dict[self.current_form] = form_view_star_run_logs

        # raise "form_view_star_run_logs" to front
        form_view_star_run_logs.tkraise()

    #---------------

    def recreate_busco_config_file(self, event=None):
        '''
        Recreate the BUSCO config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_busco_config_file" in "container" with the grid geometry manager
        form_recreate_busco_config_file = gbioinfoapp.FormRecreateBuscoConfigFile(self.container, self)
        form_recreate_busco_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_busco_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_busco_config_file'
        self.forms_dict[self.current_form] = form_recreate_busco_config_file

        # raise "form_recreate_busco_config_file" to front
        form_recreate_busco_config_file.tkraise()

    #---------------

    def edit_busco_config_file(self, event=None):
        '''
        Edit the BUSCO config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_busco_name())

        # edit the BUSCO config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xbusco.get_busco_config_file())
        self.wait_window(dialog_editor)

        # validate the BUSCO config file
        (OK, error_list) = xbusco.validate_busco_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_busco_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_busco_process(self, event=None):
        '''
        Run a BUSCO process corresponding to the options in BUSCO config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_busco_process" in "container" with the grid geometry manager
        form_run_busco_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_busco_code())
        form_run_busco_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_busco_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_busco_process'
        self.forms_dict[self.current_form] = form_run_busco_process

        # raise "form_run_busco_process" to front
        form_run_busco_process.tkraise()

    #---------------

    def view_busco_run_logs(self, event=None):
        '''
        List the BUSCO process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_busco_run_logs" in "container" with the grid geometry manager
        form_view_busco_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_busco_code())
        form_view_busco_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_busco_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'view_busco_run_logs'
        self.forms_dict[self.current_form] = form_view_busco_run_logs

        # raise "form_view_busco_run_logs" to front
        form_view_busco_run_logs.tkraise()

    #---------------

    def recreate_gmap_config_file(self, event=None):
        '''
        Recreate the GMAP config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_gmap_config_file" in "container" with the grid geometry manager
        form_recreate_gmap_config_file = gbioinfoapp.FormRecreateGmapConfigFile(self.container, self)
        form_recreate_gmap_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_gmap_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_gmap_config_file'
        self.forms_dict[self.current_form] = form_recreate_gmap_config_file

        # raise "form_recreate_gmap_config_file" to front
        form_recreate_gmap_config_file.tkraise()

    #---------------

    def edit_gmap_config_file(self, event=None):
        '''
        Edit the GMAP config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_gmap_name())

        # edit the GMAP config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xgmap.get_gmap_config_file())
        self.wait_window(dialog_editor)

        # validate the GMAP config file
        (OK, error_list) = xgmap.validate_gmap_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_gmap_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_gmap_process(self, event=None):
        '''
        Run a GMAP process corresponding to the options in GMAP config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_gmap_process" in "container" with the grid geometry manager
        form_run_gmap_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_gmap_code())
        form_run_gmap_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_gmap_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_gmap_process'
        self.forms_dict[self.current_form] = form_run_gmap_process

        # raise "form_run_gmap_process" to front
        form_run_gmap_process.tkraise()

    #---------------

    def view_gmap_run_logs(self, event=None):
        '''
        List the GMAP process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_gmap_run_logs" in "container" with the grid geometry manager
        form_view_gmap_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_gmap_code())
        form_view_gmap_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_gmap_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'view_gmap_run_logs'
        self.forms_dict[self.current_form] = form_view_gmap_run_logs

        # raise "form_view_gmap_run_logs" to front
        form_view_gmap_run_logs.tkraise()

    #---------------

    def recreate_quast_config_file(self, event=None):
        '''
        Recreate the QUAST config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_quast_config_file" in "container" with the grid geometry manager
        form_recreate_quast_config_file = gbioinfoapp.FormRecreateQuastConfigFile(self.container, self)
        form_recreate_quast_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_quast_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_quast_config_file'
        self.forms_dict[self.current_form] = form_recreate_quast_config_file

        # raise "form_recreate_quast_config_file" to front
        form_recreate_quast_config_file.tkraise()

    #---------------

    def edit_quast_config_file(self, event=None):
        '''
        Edit the QUAST config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_quast_name())

        # edit the QUAST config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xquast.get_quast_config_file())
        self.wait_window(dialog_editor)

        # validate the QUAST config file
        (OK, error_list) = xquast.validate_quast_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_quast_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_quast_process(self, event=None):
        '''
        Run a QUAST process corresponding to the options in QUAST config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_quast_process" in "container" with the grid geometry manager
        form_run_quast_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_quast_code())
        form_run_quast_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_quast_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_quast_process'
        self.forms_dict[self.current_form] = form_run_quast_process

        # raise "form_run_quast_process" to front
        form_run_quast_process.tkraise()

    #---------------

    def view_quast_run_logs(self, event=None):
        '''
        List the QUAST process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_quast_run_logs" in "container" with the grid geometry manager
        form_view_quast_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_quast_code())
        form_view_quast_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_quast_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'view_quast_run_logs'
        self.forms_dict[self.current_form] = form_view_quast_run_logs

        # raise "form_view_quast_run_logs" to front
        form_view_quast_run_logs.tkraise()

    #---------------

    def recreate_rnaquast_config_file(self, event=None):
        '''
        Recreate the rnaQUAST config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_rnaquast_config_file" in "container" with the grid geometry manager
        form_recreate_rnaquast_config_file = gbioinfoapp.FormRecreateRnaQuastConfigFile(self.container, self)
        form_recreate_rnaquast_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_rnaquast_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_rnaquast_config_file'
        self.forms_dict[self.current_form] = form_recreate_rnaquast_config_file

        # raise "form_recreate_rnaquast_config_file" to front
        form_recreate_rnaquast_config_file.tkraise()

    #---------------

    def edit_rnaquast_config_file(self, event=None):
        '''
        Edit the rnaQUAST config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_rnaquast_name())

        # edit the rnaQUAST config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xrnaquast.get_rnaquast_config_file())
        self.wait_window(dialog_editor)

        # validate the rnaQUAST config file
        (OK, error_list) = xrnaquast.validate_rnaquast_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_rnaquast_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_rnaquast_process(self, event=None):
        '''
        Run a rnaQUAST process corresponding to the options in rnaQUAST config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_rnaquast_process" in "container" with the grid geometry manager
        form_run_rnaquast_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_rnaquast_code())
        form_run_rnaquast_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_rnaquast_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_rnaquast_process'
        self.forms_dict[self.current_form] = form_run_rnaquast_process

        # raise "form_run_rnaquast_process" to front
        form_run_rnaquast_process.tkraise()

    #---------------

    def view_rnaquast_run_logs(self, event=None):
        '''
        List the rnaQUAST process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_rnaquast_run_logs" in "container" with the grid geometry manager
        form_view_rnaquast_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_rnaquast_code())
        form_view_rnaquast_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_rnaquast_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'view_rnaquast_run_logs'
        self.forms_dict[self.current_form] = form_view_rnaquast_run_logs

        # raise "form_view_rnaquast_run_logs" to front
        form_view_rnaquast_run_logs.tkraise()

    #---------------

    def recreate_rsem_eval_config_file(self, event=None):
        '''
        Create the RSEM-EVAL config file with the default options. It is necessary
        update the options in process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_rsem_eval_config_file" in "container" with the grid geometry manager
        form_recreate_rsem_eval_config_file = gbioinfoapp.FormRecreateRsemEvalConfigFile(self.container, self)
        form_recreate_rsem_eval_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_rsem_eval_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_rsem_eval_config_file'
        self.forms_dict[self.current_form] = form_recreate_rsem_eval_config_file

        # raise "form_recreate_rsem_eval_config_file" to front
        form_recreate_rsem_eval_config_file.tkraise()

    #---------------

    def edit_rsem_eval_config_file(self, event=None):
        '''
        Edit the RSEM-EVAL config file to change the parameters of process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_rsem_eval_name())

        # edit the RSEM-EVAL config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xdetonate.get_rsem_eval_config_file())
        self.wait_window(dialog_editor)

        # validate the RSEM-EVAL config file
        (OK, error_list) = xdetonate.validate_rsem_eval_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_rsem_eval_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_rsem_eval_process(self, event=None):
        '''
        Run a RSEM-EVAL process corresponding to the options in RSEM-EVAL config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_rsem_eval_process" in "container" with the grid geometry manager
        form_run_rsem_eval_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_rsem_eval_code())
        form_run_rsem_eval_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_rsem_eval_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_rsem_eval_process'
        self.forms_dict[self.current_form] = form_run_rsem_eval_process

        # raise "form_run_rsem_eval_process" to front
        form_run_rsem_eval_process.tkraise()

    #---------------

    def view_rsem_eval_run_logs(self, event=None):
        '''
        List the RSEM-EVAL process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_rsem_eval_run_logs" in "container" with the grid geometry manager
        form_view_rsem_eval_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_rsem_eval_code())
        form_view_rsem_eval_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_rsem_eval_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_rsem_eval_run_logs'
        self.forms_dict[self.current_form] = form_view_rsem_eval_run_logs

        # raise "form_view_rsem_eval_run_logs" to front
        form_view_rsem_eval_run_logs.tkraise()

    #---------------

    def recreate_ref_eval_config_file(self, event=None):
        '''
        Create the REF-EVAL config file with the default options. It is necessary
        update the options in process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_ref_eval_config_file" in "container" with the grid geometry manager
        form_recreate_ref_eval_config_file = gbioinfoapp.FormRecreateRefEvalConfigFile(self.container, self)
        form_recreate_ref_eval_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_ref_eval_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_ref_eval_config_file'
        self.forms_dict[self.current_form] = form_recreate_ref_eval_config_file

        # raise "form_recreate_ref_eval_config_file" to front
        form_recreate_ref_eval_config_file.tkraise()

    #---------------

    def edit_ref_eval_config_file(self, event=None):
        '''
        Edit the REF-EVAL config file to change the parameters of process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_ref_eval_name())

        # edit the RSEM-EVAL config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xdetonate.get_ref_eval_config_file())
        self.wait_window(dialog_editor)

        # validate the RSEM-EVAL config file
        (OK, error_list) = xdetonate.validate_ref_eval_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_ref_eval_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_ref_eval_process(self, event=None):
        '''
        Run a REF-EVAL process corresponding to the options in REF-EVAL config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_ref_eval_process" in "container" with the grid geometry manager
        form_run_ref_eval_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_ref_eval_code())
        form_run_ref_eval_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_ref_eval_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_ref_eval_process'
        self.forms_dict[self.current_form] = form_run_ref_eval_process

        # raise "form_run_ref_eval_process" to front
        form_run_ref_eval_process.tkraise()

    #---------------

    def view_ref_eval_run_logs(self, event=None):
        '''
        List the REF-EVAL process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_ref_eval_run_logs" in "container" with the grid geometry manager
        form_view_ref_eval_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_ref_eval_code())
        form_view_ref_eval_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_ref_eval_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_ref_eval_run_logs'
        self.forms_dict[self.current_form] = form_view_ref_eval_run_logs

        # raise "form_view_ref_eval_run_logs" to front
        form_view_ref_eval_run_logs.tkraise()

    #---------------

    def recreate_transrate_config_file(self, event=None):
        '''
        Recreate the Transrate config file with the default options. It is necessary
        update the options in each process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_transrate_config_file" in "container" with the grid geometry manager
        form_recreate_transrate_config_file = gbioinfoapp.FormRecreateTransrateConfigFile(self.container, self)
        form_recreate_transrate_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_transrate_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_transrate_config_file'
        self.forms_dict[self.current_form] = form_recreate_transrate_config_file

        # raise "form_recreate_transrate_config_file" to front
        form_recreate_transrate_config_file.tkraise()

    #---------------

    def edit_transrate_config_file(self, event=None):
        '''
        Edit the Transrate config file to change the parameters of each process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_transrate_name())

        # edit the Transrate config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xtransrate.get_transrate_config_file())
        self.wait_window(dialog_editor)

        # validate the Transrate config file
        (OK, error_list) = xtransrate.validate_transrate_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_transrate_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_transrate_process(self, event=None):
        '''
        Run a Transrate process corresponding to the options in Transrate config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_transrate_process" in "container" with the grid geometry manager
        form_run_transrate_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_transrate_code())
        form_run_transrate_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_transrate_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_transrate_process'
        self.forms_dict[self.current_form] = form_run_transrate_process

        # raise "form_run_transrate_process" to front
        form_run_transrate_process.tkraise()

    #---------------

    def view_transrate_run_logs(self, event=None):
        '''
        List the Transrate process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_transrate_run_logs" in "container" with the grid geometry manager
        form_view_transrate_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_transrate_code())
        form_view_transrate_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_transrate_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'view_transrate_run_logs'
        self.forms_dict[self.current_form] = form_view_transrate_run_logs

        # raise "form_view_transrate_run_logs" to front
        form_view_transrate_run_logs.tkraise()

    #---------------

    def recreate_cd_hit_est_config_file(self, event=None):
        '''
        Create the CD-HIT-EST config file with the default options. It is necessary
        update the options in process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_cd_hit_est_config_file" in "container" with the grid geometry manager
        form_cd_hit_est_eval_config_file = gbioinfoapp.FormRecreateCdHitEstConfigFile(self.container, self)
        form_cd_hit_est_eval_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_cd_hit_est_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_cd_hit_est_config_file'
        self.forms_dict[self.current_form] = form_cd_hit_est_eval_config_file

        # raise "form_recreate_cd_hit_est_config_file" to front
        form_cd_hit_est_eval_config_file.tkraise()

    #---------------

    def edit_cd_hit_est_config_file(self, event=None):
        '''
        Edit the CD-HIT-EST config file to change the parameters of process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_cd_hit_est_name())

        # edit the CD-HIT-EST config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xcdhit.get_cd_hit_est_config_file())
        self.wait_window(dialog_editor)

        # validate the CD-HIT-EST config file
        (OK, error_list) = xcdhit.validate_cd_hit_est_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_cd_hit_est_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_cd_hit_est_process(self, event=None):
        '''
        Run a CD-HIT-EST process corresponding to the options in CD-HIT-EST config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_cd_hit_est_process" in "container" with the grid geometry manager
        form_run_cd_hit_est_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_cd_hit_est_code())
        form_run_cd_hit_est_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_cd_hit_est_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_cd_hit_est_process'
        self.forms_dict[self.current_form] = form_run_cd_hit_est_process

        # raise "form_run_cd_hit_est_process" to front
        form_run_cd_hit_est_process.tkraise()

    #---------------

    def view_cd_hit_est_run_logs(self, event=None):
        '''
        List the CD-HIT-EST process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_cd_hit_est_run_logs" in "container" with the grid geometry manager
        form_view_cd_hit_est_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_cd_hit_est_code())
        form_view_cd_hit_est_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_cd_hit_est_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_cd_hit_est_run_logs'
        self.forms_dict[self.current_form] = form_view_cd_hit_est_run_logs

        # raise "form_view_cd_hit_est_run_logs" to front
        form_view_cd_hit_est_run_logs.tkraise()

    #---------------

    def recreate_transcript_filter_config_file(self, event=None):
        '''
        Create the transcripts-filter config file with the default options. It is necessary
        update the options in process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_transcript_filter_config_file" in "container" with the grid geometry manager
        form_transcript_filter_eval_config_file = gbioinfoapp.FormRecreateTranscriptFilterConfigFile(self.container, self)
        form_transcript_filter_eval_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_transcript_filter_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_transcript_filter_config_file'
        self.forms_dict[self.current_form] = form_transcript_filter_eval_config_file

        # raise "form_recreate_transcript_filter_config_file" to front
        form_transcript_filter_eval_config_file.tkraise()

    #---------------

    def edit_transcript_filter_config_file(self, event=None):
        '''
        Edit the transcripts-filter config file to change the parameters of process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_transcript_filter_name())

        # edit the transcripts-filter config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xngshelper.get_transcript_filter_config_file())
        self.wait_window(dialog_editor)

        # validate the transcripts-filter config file
        (OK, error_list) = xngshelper.validate_transcript_filter_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_transcript_filter_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_transcript_filter_process(self, event=None):
        '''
        Run a transcripts-filter process corresponding to the options in transcripts-filter config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_transcript_filter_process" in "container" with the grid geometry manager
        form_run_transcript_filter_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_transcript_filter_code())
        form_run_transcript_filter_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_transcript_filter_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_transcript_filter_process'
        self.forms_dict[self.current_form] = form_run_transcript_filter_process

        # raise "form_run_transcript_filter_process" to front
        form_run_transcript_filter_process.tkraise()

    #---------------

    def view_transcript_filter_run_logs(self, event=None):
        '''
        List the transcripts-filter process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_transcript_filter_run_logs" in "container" with the grid geometry manager
        form_view_transcript_filter_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_transcript_filter_code())
        form_view_transcript_filter_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_transcript_filter_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_transcript_filter_run_logs'
        self.forms_dict[self.current_form] = form_view_transcript_filter_run_logs

        # raise "form_view_transcript_filter_run_logs" to front
        form_view_transcript_filter_run_logs.tkraise()

    #---------------

    def recreate_transcriptome_blastx_config_file(self, event=None):
        '''
        Create the transcriptome-blastx config file with the default options. It is necessary
        update the options in process run.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_transcriptome_blastx_config_file" in "container" with the grid geometry manager
        form_transcriptome_blastx_eval_config_file = gbioinfoapp.FormRecreateTranscriptomeBlastxConfigFile(self.container, self)
        form_transcriptome_blastx_eval_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_transcriptome_blastx_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_transcriptome_blastx_config_file'
        self.forms_dict[self.current_form] = form_transcriptome_blastx_eval_config_file

        # raise "form_recreate_transcriptome_blastx_config_file" to front
        form_transcriptome_blastx_eval_config_file.tkraise()

    #---------------

    def edit_transcriptome_blastx_config_file(self, event=None):
        '''
        Edit the transcriptome-blastx config file to change the parameters of process run.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = '{0} - Edit config file'.format(xlib.get_transcriptome_blastx_name())

        # edit the transcripts-filter config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xngshelper.get_transcriptome_blastx_config_file())
        self.wait_window(dialog_editor)

        # validate the transcripts-filter config file
        (OK, error_list) = xngshelper.validate_transcriptome_blastx_config_file(strict=False)
        if OK:
            message = 'The {0} config file is OK.'.format(xlib.get_transcriptome_blastx_name())
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_transcriptome_blastx_process(self, event=None):
        '''
        Run a transcriptome-blastx process corresponding to the options in RSEM-EVAL config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_transcriptome_blastx_process" in "container" with the grid geometry manager
        form_run_transcriptome_blastx_process = gbioinfoapp.FormRunBioinfoProcess(self.container, self, app=xlib.get_transcriptome_blastx_code())
        form_run_transcriptome_blastx_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_transcriptome_blastx_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_transcriptome_blastx_process'
        self.forms_dict[self.current_form] = form_run_transcriptome_blastx_process

        # raise "form_run_transcriptome_blastx_process" to front
        form_run_transcriptome_blastx_process.tkraise()

    #---------------

    def view_transcriptome_blastx_run_logs(self, event=None):
        '''
        List the transcriptome-blastx process runs and view run logs.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_transcriptome_blastx_run_logs" in "container" with the grid geometry manager
        form_view_transcriptome_blastx_run_logs = gbioinfoapp.FormListBioinfoRuns(self.container, self, app=xlib.get_transcriptome_blastx_code())
        form_view_transcriptome_blastx_run_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_transcriptome_blastx_run_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_transcriptome_blastx_run_logs'
        self.forms_dict[self.current_form] = form_view_transcriptome_blastx_run_logs

        # raise "form_view_transcriptome_blastx_run_logs" to front
        form_view_transcriptome_blastx_run_logs.tkraise()

    #---------------

    def list_dataset(self, event=None):
        '''
        List datasets showing data of its directories and files.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_list_dataset" in "container" with the grid geometry manager
        form_list_dataset = gdataset.FormListDataset(self.container, self)
        form_list_dataset.grid(row=0, column=0, sticky='nsew')

        # set "form_list_dataset" as current form and add it in the forms dictionary
        self.current_form = 'form_list_dataset'
        self.forms_dict[self.current_form] = form_list_dataset

        # raise "form_list_dataset" to front
        form_list_dataset.tkraise()

    #---------------

    def recreate_reference_transfer_config_file(self, event=None):
        '''
        Recreate the reference transfer config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_reference_transfer_config_file" in "container" with the grid geometry manager
        form_recreate_reference_transfer_config_file = gdataset.FormRecreateReferenceTransferConfigFile(self.container, self)
        form_recreate_reference_transfer_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_reference_transfer_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_reference_transfer_config_file'
        self.forms_dict[self.current_form] = form_recreate_reference_transfer_config_file

        # raise "form_recreate_reference_transfer_config_file" to front
        form_recreate_reference_transfer_config_file.tkraise()

    #---------------

    def edit_reference_transfer_config_file(self, event=None):
        '''
        Edit the reference transfer config file to change the parameters of each transfer.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Reference dataset file transfer - Edit config file'

        # edit the reference transfer config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xreference.get_reference_transfer_config_file())
        self.wait_window(dialog_editor)

        # validate the reference transfer config file
        (OK, error_list) = xreference.validate_reference_transfer_config_file(strict=False)
        if OK:
            message = 'The reference transfer config file is OK.'
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def upload_reference_dataset(self, event=None):
        '''
       Upload a reference dataset to a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_upload_reference_dataset" in "container" with the grid geometry manager
        form_upload_reference_dataset = gdataset.FormUploadReferenceDataSet(self.container, self)
        form_upload_reference_dataset.grid(row=0, column=0, sticky='nsew')

        # set "form_upload_reference_dataset" as current form and add it in the forms dictionary
        self.current_form = 'form_upload_reference_dataset'
        self.forms_dict[self.current_form] = form_upload_reference_dataset

        # raise "form_upload_reference_dataset" to front
        form_upload_reference_dataset.tkraise()

    #---------------

    def recreate_reference_gzip_config_file(self, event=None):
        '''
       Recreate the reference file compression/decompression config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_reference_gzip_config_file" in "container" with the grid geometry manager
        form_recreate_reference_gzip_config_file = gdataset.FormRecreateReferenceGzipConfigFile(self.container, self)
        form_recreate_reference_gzip_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_reference_gzip_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_reference_gzip_config_file'
        self.forms_dict[self.current_form] = form_recreate_reference_gzip_config_file

        # raise "form_recreate_reference_gzip_config_file" to front
        form_recreate_reference_gzip_config_file.tkraise()

    #---------------

    def edit_reference_gzip_config_file(self, event=None):
        '''
       Edit the reference file compression/decompression config file.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Reference dataset file compression/decompression - Edit config file'

        # edit the reference gzip config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xgzip.get_gzip_config_file('reference'))
        self.wait_window(dialog_editor)

        # validate the reference gzip config file
        (OK, error_list) = xgzip.validate_gzip_config_file('reference', strict=False)
        if OK:
            message = 'The reference gzip config file is OK.'
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_reference_gzip_process(self, event=None):
        '''
        Compress/decompress reference dataset files in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_reference_gzip_process" in "container" with the grid geometry manager
        form_run_reference_gzip_process = gdataset.FormRunGzipProcess(self.container, self, 'reference')
        form_run_reference_gzip_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_reference_gzip_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_reference_gzip_process'
        self.forms_dict[self.current_form] = form_run_reference_gzip_process

        # raise "form_run_reference_gzip_process" to front
        form_run_reference_gzip_process.tkraise()

    #---------------

    def remove_reference_dataset(self, event=None):
        '''
       Remove the reference dataset in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_remove_reference_dataset" in "container" with the grid geometry manager
        form_remove_reference_dataset = gdataset.FormRemoveDataSet(self.container, self, 'reference')
        form_remove_reference_dataset.grid(row=0, column=0, sticky='nsew')

        # set "form_remove_reference_dataset" as current form and add it in the forms dictionary
        self.current_form = 'form_remove_reference_dataset'
        self.forms_dict[self.current_form] = form_remove_reference_dataset

        # raise "form_remove_reference_dataset" to front
        form_remove_reference_dataset.tkraise()

    #---------------

    def recreate_database_transfer_config_file(self, event=None):
        '''
        Recreate the database transfer config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_database_transfer_config_file" in "container" with the grid geometry manager
        form_recreate_database_transfer_config_file = gdataset.FormRecreateDatabaseTransferConfigFile(self.container, self)
        form_recreate_database_transfer_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_database_transfer_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_database_transfer_config_file'
        self.forms_dict[self.current_form] = form_recreate_database_transfer_config_file

        # raise "form_recreate_database_transfer_config_file" to front
        form_recreate_database_transfer_config_file.tkraise()

    #---------------

    def edit_database_transfer_config_file(self, event=None):
        '''
        Edit the database transfer config file to change the parameters of each transfer.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Database file transfer - Edit config file'

        # edit the database transfer config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xdatabase.get_database_transfer_config_file())
        self.wait_window(dialog_editor)

        # validate the database transfer config file
        (OK, error_list) = xdatabase.validate_database_transfer_config_file(strict=False)
        if OK:
            message = 'The database transfer config file is OK.'
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def upload_database_dataset(self, event=None):
        '''
       Upload a database dataset to a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_upload_database_dataset" in "container" with the grid geometry manager
        form_upload_database_dataset = gdataset.FormUploadDatabaseDataSet(self.container, self)
        form_upload_database_dataset.grid(row=0, column=0, sticky='nsew')

        # set "form_upload_database_dataset" as current form and add it in the forms dictionary
        self.current_form = 'form_upload_database_dataset'
        self.forms_dict[self.current_form] = form_upload_database_dataset

        # raise "form_upload_database_dataset" to front
        form_upload_database_dataset.tkraise()

    #---------------

    def recreate_database_gzip_config_file(self, event=None):
        '''
       Recreate the database file compression/decompression config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_database_gzip_config_file" in "container" with the grid geometry manager
        form_recreate_database_gzip_config_file = gdataset.FormRecreateDatabaseGzipConfigFile(self.container, self)
        form_recreate_database_gzip_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_database_gzip_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_database_gzip_config_file'
        self.forms_dict[self.current_form] = form_recreate_database_gzip_config_file

        # raise "form_recreate_database_gzip_config_file" to front
        form_recreate_database_gzip_config_file.tkraise()

    #---------------

    def edit_database_gzip_config_file(self, event=None):
        '''
       Edit the database file compression/decompression config file.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Database file compression/decompression - Edit config file'

        # edit the database gzip config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xgzip.get_gzip_config_file('database'))
        self.wait_window(dialog_editor)

        # validate the database gzip config file
        (OK, error_list) = xgzip.validate_gzip_config_file('database', strict=False)
        if OK:
            message = 'The database gzip config file is OK.'
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_database_gzip_process(self, event=None):
        '''
        Compress/decompress database dataset files in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_database_gzip_process" in "container" with the grid geometry manager
        form_run_database_gzip_process = gdataset.FormRunGzipProcess(self.container, self, 'database')
        form_run_database_gzip_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_database_gzip_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_database_gzip_process'
        self.forms_dict[self.current_form] = form_run_database_gzip_process

        # raise "form_run_database_gzip_process" to front
        form_run_database_gzip_process.tkraise()

    #---------------

    def remove_database_dataset(self, event=None):
        '''
       Remove the database dataset in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_remove_database_dataset" in "container" with the grid geometry manager
        form_remove_database_dataset = gdataset.FormRemoveDatabaseDataSet(self.container, self)
        form_remove_database_dataset.grid(row=0, column=0, sticky='nsew')

        # set "form_remove_database_dataset" as current form and add it in the forms dictionary
        self.current_form = 'form_remove_database_dataset'
        self.forms_dict[self.current_form] = form_remove_database_dataset

        # raise "form_remove_database_dataset" to front
        form_remove_database_dataset.tkraise()

    #---------------

    def recreate_read_transfer_config_file(self, event=None):
        '''
        Recreate the read transfer config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_read_transfer_config_file" in "container" with the grid geometry manager
        form_recreate_read_transfer_config_file = gdataset.FormRecreateReadTransferConfigFile(self.container, self)
        form_recreate_read_transfer_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_read_transfer_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_read_transfer_config_file'
        self.forms_dict[self.current_form] = form_recreate_read_transfer_config_file

        # raise "form_recreate_read_transfer_config_file" to front
        form_recreate_read_transfer_config_file.tkraise()

    #---------------

    def edit_read_transfer_config_file(self, event=None):
        '''
        Edit the read transfer config file to change the parameters of each transfer.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Read dataset file transfer - Edit config file'

        # edit the read transfer config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xread.get_read_transfer_config_file())
        self.wait_window(dialog_editor)

        # validate the read transfer config file
        (OK, error_list) = xread.validate_read_transfer_config_file(strict=False)
        if OK:
            message = 'The read transfer config file is OK.'
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def upload_read_dataset(self, event=None):
        '''
       Upload a read dataset to a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_upload_read_dataset" in "container" with the grid geometry manager
        form_upload_read_dataset = gdataset.FormUploadReadDataSet(self.container, self)
        form_upload_read_dataset.grid(row=0, column=0, sticky='nsew')

        # set "form_upload_read_dataset" as current form and add it in the forms dictionary
        self.current_form = 'form_upload_read_dataset'
        self.forms_dict[self.current_form] = form_upload_read_dataset

        # raise "form_upload_read_dataset" to front
        form_upload_read_dataset.tkraise()

    #---------------

    def recreate_read_gzip_config_file(self, event=None):
        '''
       Recreate the read file compression/decompression config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_read_gzip_config_file" in "container" with the grid geometry manager
        form_recreate_read_gzip_config_file = gdataset.FormRecreateReadGzipConfigFile(self.container, self)
        form_recreate_read_gzip_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_read_gzip_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_read_gzip_config_file'
        self.forms_dict[self.current_form] = form_recreate_read_gzip_config_file

        # raise "form_recreate_read_gzip_config_file" to front
        form_recreate_read_gzip_config_file.tkraise()

    #---------------

    def edit_read_gzip_config_file(self, event=None):
        '''
       Edit the read file compression/decompression config file.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Read dataset file compression/decompression - Edit config file'

        # edit the read gzip config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xgzip.get_gzip_config_file('read'))
        self.wait_window(dialog_editor)

        # validate the read gzip config file
        (OK, error_list) = xgzip.validate_gzip_config_file('read', strict=False)
        if OK:
            message = 'The read gzip config file is OK.'
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_read_gzip_process(self, event=None):
        '''
        Compress/decompress read dataset files in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_run_read_gzip_process" in "container" with the grid geometry manager
        form_run_read_gzip_process = gdataset.FormRunGzipProcess(self.container, self, 'read')
        form_run_read_gzip_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_read_gzip_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_read_gzip_process'
        self.forms_dict[self.current_form] = form_run_read_gzip_process

        # raise "form_run_read_gzip_process" to front
        form_run_read_gzip_process.tkraise()

    #---------------

    def remove_read_dataset(self, event=None):
        '''
       Remove a read dataset in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_remove_read_dataset" in "container" with the grid geometry manager
        form_remove_read_dataset = gdataset.FormRemoveDataSet(self.container, self, 'read')
        form_remove_read_dataset.grid(row=0, column=0, sticky='nsew')

        # set "form_remove_read_dataset" as current form and add it in the forms dictionary
        self.current_form = 'form_remove_read_dataset'
        self.forms_dict[self.current_form] = form_remove_read_dataset

        # raise "form_remove_read_dataset" to front
        form_remove_read_dataset.tkraise()

    #---------------

    def recreate_result_transfer_config_file(self, event=None):
        '''
        Recreate the result transfer config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_result_transfer_config_file" in "container" with the grid geometry manager
        form_recreate_result_transfer_config_file = gdataset.FormRecreateResultTransferConfigFile(self.container, self)
        form_recreate_result_transfer_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_result_transfer_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_result_transfer_config_file'
        self.forms_dict[self.current_form] = form_recreate_result_transfer_config_file

        # raise "form_recreate_result_transfer_config_file" to front
        form_recreate_result_transfer_config_file.tkraise()

    #---------------

    def edit_result_transfer_config_file(self, event=None):
        '''
        Edit the result transfer config file of a run to change the parameters of each transfer.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Result dataset file transfer - Edit config file'

        # edit the result transfer config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xresult.get_result_transfer_config_file())
        self.wait_window(dialog_editor)

        # validate the result transfer config file
        (OK, error_list) = xresult.validate_result_transfer_config_file(strict=False)
        if OK:
            message = 'The result transfer config file is OK.'
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def download_result_dataset(self, event=None):
        '''
        Download a result dataset from a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_download_result_dataset" in "container" with the grid geometry manager
        form_download_result_dataset = gdataset.FormDownloadResultDataSet(self.container, self)
        form_download_result_dataset.grid(row=0, column=0, sticky='nsew')

        # set "form_download_result_dataset" as current form and add it in the forms dictionary
        self.current_form = 'form_download_result_dataset'
        self.forms_dict[self.current_form] = form_download_result_dataset

        # raise "form_download_result_dataset" to front
        form_download_result_dataset.tkraise()

    #---------------

    def recreate_result_gzip_config_file(self, event=None):
        '''
       Recreate the result file compression/decompression config file.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_recreate_result_gzip_config_file" in "container" with the grid geometry manager
        form_recreate_result_gzip_config_file = gdataset.FormRecreateResultGzipConfigFile(self.container, self)
        form_recreate_result_gzip_config_file.grid(row=0, column=0, sticky='nsew')

        # set "form_recreate_result_file_compression_decompression_config_file" as current form and add it in the forms dictionary
        self.current_form = 'form_recreate_result_gzip_config_file'
        self.forms_dict[self.current_form] = form_recreate_result_gzip_config_file

        # raise "form_recreate_result_gzip_config_file" to front
        form_recreate_result_gzip_config_file.tkraise()

    #---------------

    def edit_result_gzip_config_file(self, event=None):
        '''
       Edit the result file compression/decompression config file.
        '''

        # initialize the control variable
        OK = True

        # close the current form
        self.close_current_form()

        # set the head
        head = 'Result dataset file compression/decompression - Edit config file'

        # edit the result gzip config file using "DialogEditor" 
        dialog_editor = gdialogs.DialogEditor(self, xgzip.get_gzip_config_file('result'))
        self.wait_window(dialog_editor)

        # validate the result gzip config file
        (OK, error_list) = xgzip.validate_gzip_config_file('result', strict=False)
        if OK:
            message = 'The result gzip config file is OK.'
            tkinter.messagebox.showinfo('{0} - {1}'.format(xlib.get_project_name(), head), message)
        else:
            message = 'Validate result:\n\n'
            for error in error_list:
                message = '{0}{1}\n'.format(message, error) 
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), head), message)

    #---------------

    def run_result_gzip_process(self, event=None):
        '''
        Compress/decompress result dataset files in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_result_result_gzip_process" in "container" with the grid geometry manager
        form_run_result_gzip_process = gdataset.FormRunGzipProcess(self.container, self, 'result')
        form_run_result_gzip_process.grid(row=0, column=0, sticky='nsew')

        # set "form_run_result_gzip_process" as current form and add it in the forms dictionary
        self.current_form = 'form_run_result_gzip_process'
        self.forms_dict[self.current_form] = form_run_result_gzip_process

        # raise "form_run_result_gzip_process" to front
        form_run_result_gzip_process.tkraise()

    #---------------

    def remove_result_dataset(self, event=None):
        '''
       Remove a run result dataset in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_remove_result_dataset" in "container" with the grid geometry manager
        form_remove_result_dataset = gdataset.FormRemoveDataSet(self.container, self, 'result')
        form_remove_result_dataset.grid(row=0, column=0, sticky='nsew')

        # set "form_remove_result_dataset" as current form and add it in the forms dictionary
        self.current_form = 'form_remove_result_dataset'
        self.forms_dict[self.current_form] = form_remove_result_dataset

        # raise "form_remove_result_dataset" to front
        form_remove_result_dataset.tkraise()

    #---------------

    def remove_experiment(self, event=None):
        '''
       Remove all datasets of an experiment in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_remove_experiment_datasets" in "container" with the grid geometry manager
        form_remove_experiment_datasets = gdataset.FormRemoveDataSet(self.container, self, 'experiment')
        form_remove_experiment_datasets.grid(row=0, column=0, sticky='nsew')

        # set "form_remove_experiment_datasets" as current form and add it in the forms dictionary
        self.current_form = 'form_remove_experiment_datasets'
        self.forms_dict[self.current_form] = form_remove_experiment_datasets

        # raise "form_remove_experiment_datasets" to front
        form_remove_experiment_datasets.tkraise()

    #---------------

    def view_submission_logs(self, event=None):
        '''
        List logs of process submission in local computer.
        '''

        # close the current form
        self.close_current_form()

        # create and register "form_view_submission_logs" in container with the grid geometry manager
        form_view_submission_logs = glog.FormViewSubmissionLogs(self.container, self)
        form_view_submission_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_submission_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_submission_logs'
        self.forms_dict[self.current_form] = form_view_submission_logs

        # raise "form_view_submission_logs" to front
        form_view_submission_logs.tkraise()

    #---------------

    def view_result_logs(self, event=None):
        '''
        List logs of results in a cluster.
        '''

        # close the current form
        self.close_current_form()

        # create and register "view_result_logs" in container with the grid geometry manager
        form_view_result_logs = glog.FormViewResultLogs(self.container, self)
        form_view_result_logs.grid(row=0, column=0, sticky='nsew')

        # set "form_view_result_logs" as current form and add it in the forms dictionary
        self.current_form = 'form_view_result_logs'
        self.forms_dict[self.current_form] = form_view_result_logs

        # raise "form_view_result_logs" to front
        form_view_result_logs.tkraise()

    #---------------

    def open_help(self, event=None):
        '''
        Open the help file.
        '''

        try:
            manual = os.path.abspath(xlib.get_project_manual_file())
            webbrowser.open_new('file://{0}'.format(manual))
        except:
            message = 'The document {0}\n is not available.'.format(manual)
            tkinter.messagebox.showerror('{0} - Open help'.format(xlib.get_project_name()), message)

    #---------------

    def show_dialog_about(self, event=None):
        '''
        Show the application information.
        '''

        dialog_about = gdialogs.DialogAbout(self)
        self.wait_window(dialog_about)

    #---------------

    def close_current_form(self, event=None):
        '''
        Close the current form.
        '''

        # clear the label of the current process name
        self.label_process['text'] = ''

        # destroy the current form
        if self.current_form != 'form_welcome':
            self.forms_dict[self.current_form].destroy()
            self.forms_dict['form_welcome'].tkraise()

    #---------------

    def warn_unavailable_process(self, event=None):

        message = 'This process is been built.\nIt is coming soon!'
        tkinter.messagebox.showwarning('{0}'.format(xlib.get_project_name()), message)

   #---------------

#-------------------------------------------------------------------------------

class FormWelcome(tkinter.Frame):

    #---------------

    def __init__(self, parent, main):
        '''
        Execute actions correspending to the creation of a "FormWelcome" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.main = main

        # call the init method of the parent class
        tkinter.Frame.__init__(self, self.parent)

        # build the graphical user interface
        self.build_gui()

    #---------------

    def build_gui(self):
        '''
        Build the graphical user interface of "FormWelcome".
        '''

        # create "image_perrault"
        image_perrault = PIL.Image.open('./image_perrault_unai.jpg')
        image_perrault.thumbnail((self.main.WINDOW_WIDTH,self.main.WINDOW_HEIGHT), PIL.Image.ANTIALIAS)

        # create "photoimage_perrault"
        self.photoimage_perrault = PIL.ImageTk.PhotoImage(image_perrault)  

        # create "canvas_photoimage_perrault" and register it with the grid geometry manager
        self.canvas_photoimage_perrault = tkinter.Canvas(self, width=self.main.WINDOW_WIDTH, height=self.main.WINDOW_HEIGHT)
        self.canvas_photoimage_perrault.create_image(round(self.main.WINDOW_WIDTH / 2), round(self.main.WINDOW_HEIGHT / 2 - 45), image=self.photoimage_perrault, anchor='center')
        if sys.platform.startswith('linux'):
            x_coordinate = 10
            y_coordinate = self.main.WINDOW_HEIGHT - 100
        elif sys.platform.startswith('darwin'):
            x_coordinate = 10
            y_coordinate = self.main.WINDOW_HEIGHT - 85
        elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
            x_coordinate = 10
            y_coordinate = self.main.WINDOW_HEIGHT - 70
        self.canvas_photoimage_perrault.create_text(x_coordinate, y_coordinate, anchor='w', text = 'Puente de Perrault also known as "DNA Bridge" (Madrid, Spain)') 
        self.canvas_photoimage_perrault.pack(side='left', fill='both', expand=True)

    #---------------

    def close(self, event=None):
        '''
        Close "FormWelcome".
        '''

        # close the current form
        self.main.close_current_form()

   #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('This file contains the class Main corresponding to the graphical user interface of the NGScloud software package.')
    sys.exit(0)

#-------------------------------------------------------------------------------
