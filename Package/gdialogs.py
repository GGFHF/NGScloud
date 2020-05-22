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
This source contains the dialog classes corresponding to the graphical user interface of
the NGScloud software package.
'''

#-------------------------------------------------------------------------------

import os
import PIL.Image
import PIL.ImageTk
import tkinter
import tkinter.font
import tkinter.ttk
import sys

import datetime
import os
import xlib
import xssh

#-------------------------------------------------------------------------------

class DialogTable(tkinter.Toplevel):

    #---------------

    def __init__(self, parent, title_text, window_height, window_width, data_list, data_dict, item_dict, action=None, params=[]):
        '''
        Execute actions correspending to the creation of a "DialogTable" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.title_text = title_text
        self.window_height = window_height
        self.window_width = window_width
        self.data_list = data_list
        self.data_dict = data_dict
        self.item_dict = item_dict
        self.action = action
        self.params = params

        # call the parent init method
        tkinter.Toplevel.__init__(self)

        # create the window of the Dialog Table.
        self.create_window()

        # build the graphical user interface
        self.build_gui()

        # populate the table with data
        self.populate_table()

    #---------------

    def create_window(self):
        '''
        Create the window of "DialogTable".
        '''

        # define the dimensions
        self.minsize(height=self.window_height, width=self.window_width)
        self.maxsize(height=self.window_height, width=self.window_width)
        x = round((self.winfo_screenwidth() - self.window_width) / 2)
        y = round((self.winfo_screenheight() - self.window_height) / 2)
        self.geometry('{}x{}+{}+{}'.format(self.window_width, self.window_height, x, y))

        # set the title
        self.title('{0} - {1} - Table'.format(xlib.get_project_name(), self.title_text))

        # set the icon
        image_app = PIL.Image.open(xlib.get_project_image_file())
        self.photoimage_app = PIL.ImageTk.PhotoImage(image_app)
        self.tk.call('wm', 'iconphoto', self._w, self.photoimage_app)

        # associate this window with the parent window
        self.transient(self.parent)

    #---------------

    def build_gui(self):
        '''
        Build the graphical interface user of "DialogTable".
        '''

        # create "imagetk_close"
        image_close = PIL.Image.open('./image_close.png')
        imagetk_close = PIL.ImageTk.PhotoImage(image_close)  

        # create "frame_toolbar" and register it with the pack geometry manager
        self.frame_toolbar = tkinter.Frame(self, borderwidth=1, relief='raised')
        self.frame_toolbar.pack(side='top', fill='x')

        # create "button_close" and register it with the pack geometry manager
        self.button_close = tkinter.Button(self.frame_toolbar, command=self.close, relief='flat', image=imagetk_close)
        self.button_close.image = imagetk_close
        self.button_close.pack(side='left', padx=2, pady=5)

        # create "treeview" and register it with the pack geometry manager
        self.treeview = tkinter.ttk.Treeview(self)
        self.treeview.pack(side='left', fill='both', expand=True)

        # set columns in Treeview widget
        self.treeview['columns'] = self.data_list
        self.treeview['show'] = 'headings'
        for datum in self.data_list:
            # -- self.treeview.column(datum, width=self.data_dict[datum]['width'])
            if self.data_dict[datum]['aligment'] == 'left':
                aligment = tkinter.W
            elif self.data_dict[datum]['aligment'] == 'centre':
                aligment = tkinter.W + tkinter.E
            elif self.data_dict[datum]['aligment'] == 'right':
                aligment = tkinter.E
            self.treeview.column(datum, minwidth=self.data_dict[datum]['width'], width=self.data_dict[datum]['width'], anchor=aligment, stretch=False)
            self.treeview.heading(datum, text=self.data_dict[datum]['text'])

        # create "scrollbar_x" and register it with the pack geometry manager
        self.scrollbar_x = tkinter.Scrollbar(self.treeview, orient='horizontal', command=self.treeview.xview)
        self.scrollbar_x.pack(side='bottom', fill='x')
        self.treeview.configure(xscrollcommand=self.scrollbar_x.set)
        
        # create "scrollbar_y" and register it with the pack geometry manager
        self.scrollbar_y = tkinter.Scrollbar(self.treeview, orient='vertical', command=self.treeview.yview)
        self.scrollbar_y.pack(side='right', fill='y')
        self.treeview.configure(yscrollcommand=self.scrollbar_y.set)

        # link a handler to events
        self.treeview.bind("<Double-1>", self.double_click)

        # link a handler to interactions between the application and the window manager
        self.protocol('WM_DELETE_WINDOW', self.close)

    #---------------

    def populate_table(self):
        '''
        Populate the Treeview widget with the data of "DialogTable".
        '''

        # insert the items in Treeview widget
        for item_key in sorted(self.item_dict.keys()):
            row_values_list = []
            for datum in self.data_list:
                row_values_list.append(self.item_dict[item_key][datum])
            self.treeview.insert('', 'end', values=row_values_list)

    #---------------

    def double_click(self, event):
        '''
        Manege the action of a dobule click on a table item.
        '''

        # manege the action
        try:
            # get the table item selected
            item = self.treeview.selection()[0]
        except:
            message = 'There is not any action asociated with this table item.'
            OK = tkinter.messagebox.showwarning(self.title(), message)
        else:
            if self.action == 'view_submission_logs':
                run_id = self.treeview.item(item)['values'][0]
                self.view_local_process_log(run_id)
            elif self.action == 'view_result_logs':
                experiment_id = self.treeview.item(item)['values'][0]
                run_id = self.treeview.item(item)['values'][1]
                self.view_log(experiment_id, run_id)
            elif self.action == 'list_directory':
                file_type = self.treeview.item(item)['values'][0]
                file_name = self.treeview.item(item)['values'][1]
                if file_type == 'directory':
                    self.list_directory(file_name)
                else:
                    self.show_file_details(file_name)
            else:
                message = 'There is not any action asociated with this table item.'
                OK = tkinter.messagebox.showwarning(self.title(), message)

    #---------------

    def close(self, event=None):
        '''
        Close the "DialogTable".
        '''

        # delete all widgets and terminate the mainloop
        self.destroy()

    #---------------

    def view_local_process_log(self, run_id):
        '''
        View the log of a local process.
        '''

        # get the log file name and build cluster path
        log_file = '{0}/{1}'.format(xlib.get_log_dir(), run_id)

        # create and show a instance "DialogViewer" to view the log file
        dialog_viewer = DialogViewer(self, log_file, None)
        self.wait_window(dialog_viewer)

    #---------------

    def view_log(self, experiment_id, run_id):
        '''
        View the log of the run identification.
        '''

        # get the cluster name
        cluster_name = self.params[0]

        # get the log file name and build cluster path
        log_file = xlib.get_cluster_log_file()
        cluster_file_path = '{0}/{1}/{2}'.format(xlib.get_cluster_experiment_result_dir(experiment_id), run_id, log_file)

        # create and show a instance "DialogViewer" to view the log file
        dialog_viewer = DialogViewer(self, cluster_file_path, cluster_name)
        self.wait_window(dialog_viewer)

    #---------------

    def list_directory(self, directory_name):
        '''
        View the directory of a dataset.
        '''

        # get the cluster name
        parent_directory = self.params[0]

        # get the SSH client
        ssh_client = self.params[1]

        # get the directory dictionary of directories in the volume
        command = 'ls -la {0}/{1}'.format(parent_directory, directory_name)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            directory_dict = {}
            for line in stdout:
                line = line.rstrip('\n')
                if line.startswith('d') or line.startswith('-'):
                    file_data_list = line.split()
                    file_type = 'directory' if file_data_list[0][0] == 'd' else 'file'
                    permissions = file_data_list[0][1:]
                    links_number = file_data_list[1]
                    owner_name = file_data_list[2]
                    owner_group = file_data_list[3]
                    file_size = file_data_list[4]
                    modification_month = file_data_list[5]
                    modification_day = file_data_list[6]
                    modification_time = file_data_list[7]
                    file_name = file_data_list[8]
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
            dialog_table = DialogTable(self, 'Directory {0}/{1}'.format(parent_directory, directory_name), 400, 600, data_list, data_dict, directory_dict, 'list_directory', ['{0}/{1}'.format(parent_directory, directory_name), ssh_client])
            self.wait_window(dialog_table)

    #---------------

    def show_file_details(self, file_name):
        '''
        View the directory of a dataset.
        '''

        # get the cluster name
        parent_directory = self.params[0]

        # get the SSH client
        ssh_client = self.params[1]

        # get the directory dictionary of directories in the volume
        command = 'ls -la {0}/{1}'.format(parent_directory, file_name)
        (OK, stdout, stderr) = xssh.execute_cluster_command(ssh_client, command)
        if OK:
            file_detail_dict = {}
            for line in stdout:
                line = line.rstrip('\n')
                file_data_list = line.split()
                permissions = file_data_list[0][1:]
                links_number = file_data_list[1]
                owner_name = file_data_list[2]
                owner_group = file_data_list[3]
                day = int(file_data_list[6])
                try:
                    month = 1 + ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Sep', 'Oct', 'Nov', 'Dec'].index(file_data_list[5])
                except:
                    month = 0
                if file_data_list[7].find(':') > -1:
                    year = datetime.datetime.now().year
                    modification_date = '{0:4}-{1:02d}-{2:02d}'.format(year, month, day)
                    modification_time = file_data_list[7]
                else:
                    year = int(file_data_list[7])
                    modification_date = '{0:4}-{1:02}-{2:02}'.format(year, month, day)
                    modification_time = ' '
                file_name = file_data_list[8]
                file_detail_dict[0] = {'data': 'directory', 'value': os.path.dirname(file_name)}
                file_detail_dict[1] = {'data': 'name', 'value': os.path.basename(file_name)}
                file_detail_dict[2] = {'data': 'size', 'value': file_data_list[4]}
                file_detail_dict[3] = {'data': 'permissions', 'value': file_data_list[0][1:]}
                file_detail_dict[4] = {'data': 'modification date', 'value': modification_date}
                file_detail_dict[5] = {'data': 'modification time', 'value': modification_time}
                file_detail_dict[6] = {'data': 'owner group', 'value': file_data_list[3]}
                file_detail_dict[7] = {'data': 'owner name', 'value': file_data_list[2]}

        # verify if there are any nodes running
        if OK:
            if file_detail_dict == {}:
                message = 'There is not any detail.'
                tkinter.messagebox.showwarning('{0} - {1}'.format(xlib.get_project_name(), self.head), message)

        # build the data list
        if OK:
            data_list = ['data', 'value']

        # build the data dictionary
        if OK:
            data_dict = {}
            data_dict['data']= {'text': 'Data', 'width': 120, 'aligment': 'left'}
            data_dict['value'] = {'text': 'Value', 'width': 400, 'aligment': 'left'}

        # create the dialog Table to show the nodes running
        if OK:
            dialog_table = DialogTable(self, 'File {0}/{1}'.format(parent_directory, file_name), 400, 600, data_list, data_dict, file_detail_dict)
            self.wait_window(dialog_table)

    #---------------

#-------------------------------------------------------------------------------

class DialogLog(tkinter.Toplevel):

    #---------------

    WINDOW_MIN_HEIGHT = 680
    WINDOW_MIN_WIDTH = 680

    #---------------

    def __init__(self, parent, head='', calling_function=None):
        '''
        Execute actions correspending to the creation a "DialogLog" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.head = head
        self.calling_function = calling_function

        self.is_enabled_button_close = False

        # call the parent init method
        tkinter.Toplevel.__init__(self)

        # create the window of the Dialog Log.
        self.create_window()

        # build the graphical user interface
        self.build_gui()

        # set cursor to show busy status
        self.config(cursor='watch')
        self.update()
        self.text.config(cursor='watch')
        self.text.update()

        # get the local log file
        self.log_file = xlib.get_log_file(self.calling_function)

        # open the local log file
        try:
            if not os.path.exists(os.path.dirname(self.log_file)):
                os.makedirs(os.path.dirname(self.log_file))
            self.log_file_id = open(self.log_file, mode='w', encoding='iso-8859-1')
        except:
            message = '*** ERROR: The file {0} can not be created'.format(self.log_file)
            tkinter.messagebox.showerror('{0} - {1}'.format(xlib.get_project_name(), self.head), message)
            # delete all widgets and terminate the mainloop
            self.destroy()

    #---------------

    def create_window(self):
        '''
        Create the window of "DialogLog".
        '''

        # define the dimensions
        self.minsize(height=self.WINDOW_MIN_HEIGHT, width=self.WINDOW_MIN_WIDTH)
        self.maxsize(height=self.winfo_screenheight(), width=self.winfo_screenwidth())
        x = round((self.winfo_screenwidth() - self.WINDOW_MIN_WIDTH) / 2)
        y = round((self.winfo_screenheight() - self.WINDOW_MIN_HEIGHT) / 2)
        self.geometry('{}x{}+{}+{}'.format(self.WINDOW_MIN_WIDTH, self.WINDOW_MIN_HEIGHT, x, y))

        # set the title
        self.title('{0} - {1} - Log'.format(xlib.get_project_name(), self.head))

        # set the icon
        image_app = PIL.Image.open(xlib.get_project_image_file())
        self.photoimage_app = PIL.ImageTk.PhotoImage(image_app)
        self.tk.call('wm', 'iconphoto', self._w, self.photoimage_app)

        # associate this window with the parent window
        self.transient(self.parent)

    #---------------

    def build_gui(self):
        '''
        Build the graphical interface user of "DialogLog".
        '''

        # create "imagetk_close"
        image_close = PIL.Image.open('./image_close.png')
        imagetk_close = PIL.ImageTk.PhotoImage(image_close)  

        # create "frame_toolbar" and register it with the grid geometry manager
        self.frame_toolbar = tkinter.Frame(self, borderwidth=1, relief='raised')
        self.frame_toolbar.pack(side='top', fill='x')

        # create "button_close" and register it with the pack geometry manager
        self.button_close = tkinter.Button(self.frame_toolbar, command=self.close, relief='flat', image=imagetk_close, state='disabled')
        self.button_close.image = imagetk_close
        self.button_close.pack(side='left', padx=2, pady=5)

        # create "text" and register it with the grid geometry manager
        self.text = tkinter.Text(self, wrap='none', state='disabled')
        self.text.pack(expand=True, fill='both')

        # create "scrollbar_x" and register it with the pack geometry manager
        self.scrollbar_x = tkinter.Scrollbar(self.text, orient='horizontal', command=self.text.xview)
        self.scrollbar_x.pack(side='bottom', fill='x')
        self.text.configure(xscrollcommand=self.scrollbar_x.set)
        
        # create "scrollbar_y" and register it with the pack geometry manager
        self.scrollbar_y = tkinter.Scrollbar(self.text, orient='vertical', command=self.text.yview)
        self.scrollbar_y.pack(side='right', fill='y')
        self.text.configure(yscrollcommand=self.scrollbar_y.set)

        # link a handler to interactions between the application and the window manager
        self.protocol('WM_DELETE_WINDOW', self.close)

    #---------------

    def close(self, event=None):
        '''
        Close "DialogLog".
        '''

        # close the local log file
        self.log_file_id.close()

        # delete all widgets and terminate the mainloop
        if self.is_enabled_button_close:
            self.destroy()

    #---------------

    def enable_button_close(self):
        '''
        Enable "button_close".
        '''

        # set cursor to show normal status
        self.config(cursor='')
        self.update()
        self.text.config(cursor='')
        self.text.update()

        # set state "normal" to "button_close"
        self.button_close['state'] = 'normal'
        self.is_enabled_button_close = True

    #---------------

    def write(self, message=''):
        '''
        Add a message in the widget "text" and in the log file.
        '''

        # write the message in widget "text" 
        self.text.configure(state='normal')
        self.text.insert('end', message)
        self.text.see('end')
        self.text.update()
        self.text.configure(state='disabled')

        # write in the log file
        self.log_file_id.write(message)
        self.log_file_id.flush()
        os.fsync(self.log_file_id.fileno())

    #---------------

    def get_log_file(self):
        '''
        Get the current log file name
        '''

        return self.log_file

    #---------------

#-------------------------------------------------------------------------------

class DialogViewer(tkinter.Toplevel):

    #---------------

    WINDOW_MIN_HEIGHT = 650
    WINDOW_MIN_WIDTH = 800

    #---------------

    def __init__(self, parent, file_path, cluster_name=None):
        '''
        Execute actions correspending to the creation of a "DialogViewer" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.file_path = file_path
        self.cluster_name = cluster_name

        # call the parent init method
        tkinter.Toplevel.__init__(self)

        # create the window of the Dialog Viewer.
        self.create_window()

        # build the graphical user interface
        self.build_gui()

        self.open_file()

    #---------------

    def create_window(self):
        '''
        Create the window of "DialogViewer".
        '''

        # define the dimensions
        self.minsize(height=self.WINDOW_MIN_HEIGHT, width=self.WINDOW_MIN_WIDTH)
        self.maxsize(height=self.winfo_screenheight(), width=self.winfo_screenwidth())
        x = round((self.winfo_screenwidth() - self.WINDOW_MIN_WIDTH) / 2)
        y = round((self.winfo_screenheight() - self.WINDOW_MIN_HEIGHT) / 2)
        self.geometry('{}x{}+{}+{}'.format(self.WINDOW_MIN_WIDTH, self.WINDOW_MIN_HEIGHT, x, y))

        # set the title
        self.title('{0} - View - {1}'.format(xlib.get_project_name(), self.file_path))

        # set the icon
        image_app = PIL.Image.open(xlib.get_project_image_file())
        self.photoimage_app = PIL.ImageTk.PhotoImage(image_app)
        self.tk.call('wm', 'iconphoto', self._w, self.photoimage_app)

        # associate this window with the parent window
        self.transient(self.parent)

    #---------------

    def build_gui(self):
        '''
        Build the graphical interface user of "DialogViewer".
        '''

        # create "imagetk_close"
        image_close = PIL.Image.open('./image_close.png')
        imagetk_close = PIL.ImageTk.PhotoImage(image_close)  

        # create "imagetk_refresh"
        image_refresh = PIL.Image.open('./image_refresh.png')
        imagetk_refresh = PIL.ImageTk.PhotoImage(image_refresh)  

        # create "frame_toolbar" and register it with the grid geometry manager
        self.frame_toolbar = tkinter.Frame(self, borderwidth=1, relief='raised')
        self.frame_toolbar.pack(side='top', fill='x')

        # create "button_close" and register it with the pack geometry manager
        self.button_close = tkinter.Button(self.frame_toolbar, command=self.close, relief='flat', image=imagetk_close)
        self.button_close.image = imagetk_close
        self.button_close.pack(side='left', padx=2, pady=5)

        # create "separator" and register it with the pack geometry manager
        self.separator = tkinter.ttk.Separator(self.frame_toolbar, orient='vertical')
        self.separator.pack(side='left', fill='y', padx=2, pady=2)

        # create "button_refresh" and register it with the pack geometry manager
        self.button_refresh = tkinter.Button(self.frame_toolbar, command=self.open_file, relief='flat', image=imagetk_refresh)
        self.button_refresh.image = imagetk_refresh
        self.button_refresh.pack(side='left', padx=2, pady=5)

        # create "text" and register it with the grid geometry manager
        self.text = tkinter.Text(self, wrap='none', state='disabled')
        self.text.pack(expand='yes', fill='both')

        # create "scrollbar_x" and register it with the pack geometry manager
        self.scrollbar_x = tkinter.Scrollbar(self.text, orient='horizontal', command=self.text.xview)
        self.scrollbar_x.pack(side='bottom', fill='x')
        self.text.configure(xscrollcommand=self.scrollbar_x.set)
        
        # create "scrollbar_y" and register it with the pack geometry manager
        self.scrollbar_y = tkinter.Scrollbar(self.text, orient='vertical', command=self.text.yview)
        self.scrollbar_y.pack(side='right', fill='y')
        self.text.configure(yscrollcommand=self.scrollbar_y.set)

        # link a handler to events
        self.bind('<Alt-F4>', self.close)

        # link a handler to interactions between the application and the window manager
        self.protocol('WM_DELETE_WINDOW', self.close)

    #---------------

    def open_file(self):
        '''
        Open a config file in "DialogViewer".
        '''

        # set cursor to show busy status
        self.config(cursor='watch')
        self.update()
        self.text.config(cursor='watch')
        self.text.update()

        # initialize the control variable
        OK = True

        # when the file is in the local computer
        if self.cluster_name == None:

            local_file_path = self.file_path

        # when the file is in a cluster
        else:

            # create the SSH transport connection
            if OK:
                (OK, error_list, ssh_transport) = xssh.create_ssh_transport_connection(self.cluster_name, 'master')
                if not OK:
                    message = ''
                    for error in error_list:
                        message = '{0}{1}\n'.format(message, error) 
                    tkinter.messagebox.showerror(self.title(), message)

            # create the SFTP client 
            if OK:
                sftp_client = xssh.create_sftp_client(ssh_transport)

            # create the local path
            if not os.path.exists(xlib.get_temp_dir()):
                os.makedirs(xlib.get_temp_dir())

            # get the log file name and build local and cluster paths
            if OK:
                local_file_path = '{0}/{1}'.format(xlib.get_temp_dir(), os.path.basename(self.file_path))

            # download the log file from the cluster
            if OK:
                OK = xssh.get_file(sftp_client, self.file_path, local_file_path)
                if not OK:
                    message = 'The log file {0} could not be downloaded.'.format(self.file_path)
                    tkinter.messagebox.showerror(self.title(), message)

            # close the SSH transport connection
            xssh.close_ssh_transport_connection(ssh_transport)


        # load the file content in "text"
        if OK:
            self.text.configure(state='normal')
            self.text.delete('1.0', 'end')
            try:
                with open(local_file_path) as local_file_id:
                    self.text.insert('1.0', local_file_id.read())
            except:
                tkinter.messagebox.showerror('{0} - Open'.format(xlib.get_project_name()), 'The file {0} can not be opened.'.format(local_file_path))
            else:
                self.text.configure(state='disable')

        # set cursor to show normal status
        self.config(cursor='')
        self.update()
        self.text.config(cursor='')
        self.text.update()

    #---------------

    def close(self, event=None):
        '''
        Close "DialogViewer".
        '''

        # deletes all widgets and terminate the mainloop
        self.destroy()

    #---------------

#-------------------------------------------------------------------------------

class DialogEditor(tkinter.Toplevel):

    #---------------

    WINDOW_MIN_HEIGHT = 650
    WINDOW_MIN_WIDTH = 800

    #---------------

    def __init__(self, parent, file_path):
        '''
        Execute actions correspending to the creation of a "DialogEditor" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent
        self.file_path = file_path

        # call the parent init method
        tkinter.Toplevel.__init__(self)

        # create the window of the Dialog Editor.
        self.create_window()

        # build the graphical user interface
        self.build_gui()

        self.open_file()

    #---------------

    def create_window(self):
        '''
        Create the window of "DialogEditor".
        '''

        # define the dimensions
        self.minsize(height=self.WINDOW_MIN_HEIGHT, width=self.WINDOW_MIN_WIDTH)
        self.maxsize(height=self.winfo_screenheight(), width=self.winfo_screenwidth())
        x = round((self.winfo_screenwidth() - self.WINDOW_MIN_WIDTH) / 2)
        y = round((self.winfo_screenheight() - self.WINDOW_MIN_HEIGHT) / 2)
        self.geometry('{}x{}+{}+{}'.format(self.WINDOW_MIN_WIDTH, self.WINDOW_MIN_HEIGHT, x, y))

        # set the title
        self.title('{0} - Edit - {1}'.format(xlib.get_project_name(), self.file_path))

        # set the icon
        image_app = PIL.Image.open(xlib.get_project_image_file())
        self.photoimage_app = PIL.ImageTk.PhotoImage(image_app)
        self.tk.call('wm', 'iconphoto', self._w, self.photoimage_app)

        # associate this window with the parent window
        self.transient(self.parent)

    #---------------

    def build_gui(self):
        '''
        Build the graphical interface user of "DialogEditor".
        '''

        # create "imagetk_close"
        image_close = PIL.Image.open('./image_close.png')
        imagetk_close = PIL.ImageTk.PhotoImage(image_close)  

        # create "imagetk_save"
        image_save = PIL.Image.open('./image_save.png')
        imagetk_save = PIL.ImageTk.PhotoImage(image_save)  

        # create "imagetk_undo"
        image_undo = PIL.Image.open('./image_undo.gif')
        imagetk_undo = PIL.ImageTk.PhotoImage(image_undo)  

        # create "imagetk_redo"
        image_redo = PIL.Image.open('./image_redo.gif')
        imagetk_redo = PIL.ImageTk.PhotoImage(image_redo)

        # create "imagetk_cut"
        image_cut = PIL.Image.open('./image_cut.gif')
        imagetk_cut = PIL.ImageTk.PhotoImage(image_cut)

        # create "imagetk_copy"
        image_copy = PIL.Image.open('./image_copy.gif')
        imagetk_copy = PIL.ImageTk.PhotoImage(image_copy)

        # create "imagetk_paste"
        image_paste = PIL.Image.open('./image_paste.gif')
        imagetk_paste = PIL.ImageTk.PhotoImage(image_paste)

        # create "frame_toolbar" and register it with the grid geometry manager
        self.frame_toolbar = tkinter.Frame(self, borderwidth=1, relief='raised')
        self.frame_toolbar.pack(side='top', fill='x')

        # create "button_close" and register it with the pack geometry manager
        self.button_close = tkinter.Button(self.frame_toolbar, command=self.close, relief='flat', image=imagetk_close)
        self.button_close.image = imagetk_close
        self.button_close.pack(side='left', padx=2, pady=5)

        # create "separator_1" and register it with the pack geometry manager
        self.separator_1 = tkinter.ttk.Separator(self.frame_toolbar, orient='vertical')
        self.separator_1.pack(side='left', fill='y', padx=2, pady=2)

        # create "button_save" and register it with the pack geometry manager
        self.button_save = tkinter.Button(self.frame_toolbar, command=self.save, relief='flat', image=imagetk_save)
        self.button_save.image = imagetk_save
        self.button_save.pack(side='left', padx=2, pady=5)

        # create "separator_2" and register it with the pack geometry manager
        self.separator_2 = tkinter.ttk.Separator(self.frame_toolbar, orient='vertical')
        self.separator_2.pack(side='left', fill='y', padx=2, pady=2)

        # create "button_undo" and register it with the pack geometry manager
        self.button_undo = tkinter.Button(self.frame_toolbar, command=self.undo, relief='flat', image=imagetk_undo)
        self.button_undo.image = imagetk_undo
        self.button_undo.pack(side='left', padx=2, pady=5)

        # create "button_redo" and register it with the pack geometry manager
        self.button_redo = tkinter.Button(self.frame_toolbar, command=self.redo, relief='flat', image=imagetk_redo)
        self.button_redo.image = imagetk_redo
        self.button_redo.pack(side='left', padx=2, pady=5)

        # create "separator_3" and register it with the pack geometry manager
        self.separator_3 = tkinter.ttk.Separator(self.frame_toolbar, orient='vertical')
        self.separator_3.pack(side='left', fill='y', padx=2, pady=2)

        # create "button_cut" and register it with the pack geometry manager
        self.button_cut = tkinter.Button(self.frame_toolbar, command=self.cut, relief='flat', image=imagetk_cut)
        self.button_cut.image = imagetk_cut
        self.button_cut.pack(side='left', padx=2, pady=5)

        # create "button_copy" and register it with the pack geometry manager
        self.button_copy = tkinter.Button(self.frame_toolbar, command=self.copy, relief='flat', image=imagetk_copy)
        self.button_copy.image = imagetk_copy
        self.button_copy.pack(side='left', padx=2, pady=5)

        # create "button_paste" and register it with the pack geometry manager
        self.button_paste = tkinter.Button(self.frame_toolbar, command=self.paste, relief='flat', image=imagetk_paste)
        self.button_paste.image = imagetk_paste
        self.button_paste.pack(side='left', padx=2, pady=5)

        # create "text" and register it with the grid geometry manager
        self.text = tkinter.Text(self, wrap='none', undo=True)
        self.text.pack(expand='yes', fill='both')

        # create "scrollbar_x" and register it with the pack geometry manager
        self.scrollbar_x = tkinter.Scrollbar(self.text, orient='horizontal', command=self.text.xview)
        self.scrollbar_x.pack(side='bottom', fill='x')
        self.text.configure(xscrollcommand=self.scrollbar_x.set)
        
        # create "scrollbar_y" and register it with the pack geometry manager
        self.scrollbar_y = tkinter.Scrollbar(self.text, orient='vertical', command=self.text.yview)
        self.scrollbar_y.pack(side='right', fill='y')
        self.text.configure(yscrollcommand=self.scrollbar_y.set)

        # create "menu_popup" add add its menu items
        self.menu_popup = tkinter.Menu(self.text)
        self.menu_popup.add_command(label='Undo', command=self.undo, underline=0)
        self.menu_popup.add_command(label='Redo', command=self.redo, underline=0)
        self.menu_popup.add_separator()
        self.menu_popup.add_command(label='Cut', command=self.cut, underline=0)
        self.menu_popup.add_command(label='Copy', command=self.copy, underline=1)
        self.menu_popup.add_command(label='Paste', command=self.paste, underline=0)

        # link a handler to events
        self.bind('<Alt-F4>', self.close)
        # -- self.bind('<Control-c>', self.copy)
        # -- self.bind('<Control-C>', self.copy)
        self.bind('<Control-s>', self.save)
        self.bind('<Control-S>', self.save)
        # -- self.bind('<Control-v>', self.paste)
        # -- self.bind('<Control-V>', self.paste)
        # -- self.bind('<Control-x>', self.copy)
        # -- self.bind('<Control-X>', self.copy)
        self.bind('<Control-y>', self.redo)
        self.bind('<Control-Y>', self.redo)
        self.bind('<Control-z>', self.undo)
        self.bind('<Control-Z>', self.undo)
        self.text.bind('<Button-3>', self.show_menu_popup)

        # link a handler to interactions between the application and the window manager
        self.protocol('WM_DELETE_WINDOW', self.close)

    #---------------

    def open_file(self):
        '''
        Open a config file in "DialogEditor".
        '''

        self.text.delete('1.0', 'end')
        try:
            with open(self.file_path) as id_config_file:
                self.text.insert('1.0', id_config_file.read())
        except:
            tkinter.messagebox.showerror('{0} - Open'.format(xlib.get_project_name()), 'The file {0} can not be opened.'.format(self.file_path))
        else:
            self.text.edit_modified(False)

    #---------------

    def close(self, event=None):
        '''
        Close "DialogEditor".
        '''

        if self.text.edit_modified():
            if tkinter.messagebox.askyesno('{0} - Close'.format(xlib.get_project_name()), 'The file {0} has been modified. Do you save it?'.format(self.file_path)):
                self.save()

        # delete all widgets and terminate the mainloop
        self.destroy()

    #---------------

    def save(self, event=None):
        '''
        Save the file opened in "DialogEditor".
        '''

        try:
            document = self.text.get('1.0', 'end')
            with open(self.file_path, 'w') as id_config_file:
                id_config_file.write(document)
        except IOError:
            tkinter.messagebox.showwarning('{0} - Save'.formar(xlib.get_project_name()), 'The file {0} can not be saved.'.format(config_file))
        else:
            self.text.edit_modified(False)

    #---------------

    def undo(self, event=None):
        '''
        Undo the last change.
        '''

        self.text.event_generate('<<Undo>>')

        return 'break'

    #---------------

    def redo(self, event=None):
        '''
        Redo the last change.
        '''

        self.text.event_generate("<<Redo>>")

        return 'break'

    #---------------

    def cut(self, event=None):
        '''
        Cut the selected text and put in the clipboard.
        '''

        self.text.event_generate('<<Cut>>')

        return 'break'

    #---------------

    def copy(self, event=None):
        '''
        Copy the selected text in the clipboard.
        '''

        self.text.event_generate('<<Copy>>')

        return 'break'

    #---------------

    def paste(self, event=None):
        '''
        Paste the text from the clipboard.
        '''

        self.text.event_generate('<<Paste>>')

        return 'break'

    #---------------

    def show_menu_popup(self, event=None):
        '''
        Show the popup menu.
        '''

        self.menu_popup.tk_popup(event.x_root, event.y_root)

    #---------------

#-------------------------------------------------------------------------------

class DialogAbout(tkinter.Toplevel):

    #---------------

    WINDOW_HEIGHT = 300
    WINDOW_WIDTH = 525

    #---------------

    def __init__(self, parent):
        '''
        Execute actions correspending to the creation of a "DialogAbout" instance.
        '''

        # save initial parameters in instance variables
        self.parent = parent

        # call the parent init method
        tkinter.Toplevel.__init__(self)

        # create the window of the Dialog About.
        self.create_window()

        # build the graphical user interface
        self.build_gui()

    #---------------

    def create_window(self):
        '''
        Create the window of "DialogAbout".
        '''

        # define the dimensions
        self.minsize(height=self.WINDOW_HEIGHT, width=self.WINDOW_WIDTH)
        self.maxsize(height=self.WINDOW_HEIGHT, width=self.WINDOW_WIDTH)
        x = round((self.winfo_screenwidth() - self.WINDOW_WIDTH) / 2)
        y = round((self.winfo_screenheight() - self.WINDOW_HEIGHT) / 2)
        self.geometry('{}x{}+{}+{}'.format(self.WINDOW_WIDTH, self.WINDOW_HEIGHT, x, y))

        # set the title
        self.title('{0} - About'.format(xlib.get_project_name()))

        # set the icon
        image_app = PIL.Image.open(xlib.get_project_image_file())
        self.photoimage_app = PIL.ImageTk.PhotoImage(image_app)
        self.tk.call('wm', 'iconphoto', self._w, self.photoimage_app)

        # associate this window with the parent window
        self.transient(self.parent)

    #---------------

    def build_gui(self):
        '''
        Build the graphical interface user of "DialogAbout".
        '''

        # create "label_proyect" and register it with the grid geometry manager
        self.label_proyect = tkinter.Label(self, text='{0} v{1}'.format(xlib.get_project_name(), xlib.get_project_version()), font=tkinter.font.Font(size=10, weight='bold'))
        self.label_proyect.grid(row=0, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "canvas_photoimage_app" and register it with the grid geometry manager
        self.canvas_photoimage_app = tkinter.Canvas(self)
        self.canvas_photoimage_app.create_image(128/2, 128/2, image=self.parent.photoimage_app)
        self.canvas_photoimage_app.config(width=128, height=128)
        self.canvas_photoimage_app.grid(row=1, column=0, rowspan=6, padx=(5,5), pady=(40,5), sticky='nsew')

        # create "label_group" and register it with the grid geometry manager
        self.label_group = tkinter.Label(self, text='GI Genética, Fisiología e Historia Forestal')
        self.label_group.grid(row=1, column=1, padx=(5,5), pady=(20,5), sticky='w')

        # create "label_department" and register it with the grid geometry manager
        self.label_department = tkinter.Label(self, text='Dpto. Sistemas y Recursos Naturales')
        self.label_department.grid(row=2, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_school" and register it with the grid geometry manager
        self.label_school = tkinter.Label(self, text='ETSI Montes, Forestal y del Medio Natural')
        self.label_school.grid(row=3, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_university" and register it with the grid geometry manager
        self.label_university = tkinter.Label(self, text='Universidad Politécnica de Madrid')
        self.label_university.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_www1" and register it with the grid geometry manager
        self.label_www1 = tkinter.Label(self, text='http://gfhforestal.com/')
        self.label_www1.grid(row=5, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_www2" and register it with the grid geometry manager
        self.label_www2 = tkinter.Label(self, text='https://github.com/ggfhf/')
        self.label_www2.grid(row=6, column=1, padx=(5,5), pady=(5,5), sticky='w')

        # create "label_fit" and register it with the grid geometry manager
        self.label_fit = tkinter.Label(self, text=' '*5)
        self.label_fit.grid(row=7, column=2, padx=(0,0), pady=(20,5), sticky='e')

        # create "label_separator" and register it with the grid geometry manager
        self.button_close = tkinter.ttk.Button(self, text='Close', underline=0, command=self.close)
        self.button_close.grid(row=7, column=3, padx=(5,5), pady=(20,5), sticky='e')

        # link a handler to events
        self.bind('<Alt-c>', (lambda evento: self.button_close.invoke()))
        self.bind('<Alt-C>', (lambda evento: self.button_close.invoke()))
        self.bind('<KP_Enter>', (lambda evento: self.button_close.invoke()))
        self.bind('<Return>', (lambda evento: self.button_close.invoke()))

        # link a handler to interactions between the application and the window manager
        self.protocol('WM_DELETE_WINDOW', self.close)

        # set the focus in "button_close"
        self.button_close.focus_set()

    #---------------

    def close(self):
        '''
        Close "DialogAbout".
        '''

        # delete all widgets and terminate the mainloop
        self.destroy()

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('This file contains the dialog classes corresponding to the graphical user interface of the NGScloud software package.')
    sys.exit(0)

#-------------------------------------------------------------------------------
