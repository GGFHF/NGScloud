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
This source contains general functions and classes used in NGScloud
software package used in both console mode and gui mode.
'''

#-------------------------------------------------------------------------------

import configparser
import datetime
import os
import re
import subprocess
import sys
import tkinter

import xconfiguration

#-------------------------------------------------------------------------------
    
def get_project_code():
    '''
    Get the project name.
    '''

    return 'ngscloud'

#-------------------------------------------------------------------------------
    
def get_project_name():
    '''
    Get the project name.
    '''

    return 'NGScloud'

#-------------------------------------------------------------------------------

def get_project_version():
    '''
    Get the project name.
    '''

    return '0.94'

#-------------------------------------------------------------------------------
    
def get_project_manual_file():
    '''
    Get the project name.
    '''

    return './NGScloud-manual.pdf'

#-------------------------------------------------------------------------------
    
def get_project_image_file():
    '''
    Get the project name.
    '''

    return './image_NGScloud.png'

#-------------------------------------------------------------------------------

def get_starcluster():
    '''
    Get the script to run StarCluster corresponding to the Operating System.
    '''

    # assign the StarCluster script
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        starcluster = './starcluster.sh'
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        starcluster = '.\starcluster.bat'

    # return the StarCluster script
    return starcluster

#-------------------------------------------------------------------------------

def get_editor():
    '''
    Get the editor depending on the Operating System.
    '''

    # assign the editor
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        editor = 'nano'
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        editor = 'notepad'

    # return the editor
    return editor

#-------------------------------------------------------------------------------

def get_volume_creator_name():
    '''
    Get the template name of the volume creator.
    '''

    # set the template name of the volume creator
    volume_creator_name = '{0}-volume-creator'.format(xconfiguration.environment)

    # return the template name of the volume creator
    return volume_creator_name

#-------------------------------------------------------------------------------

def get_all_applications_selected_code():
    '''
    Get the code that means all applications.
    '''

    return 'all_applications_selected'

#-------------------------------------------------------------------------------

def get_bedtools_code():
    '''
    Get the BEDTools code used to identify its processes.
    '''

    return 'bedtools'

#-------------------------------------------------------------------------------

def get_bedtools_name():
    '''
    Get the BEDTools name used to title.
    '''

    return 'BEDtools'

#-------------------------------------------------------------------------------

def get_bedtools_bioconda_code():
    '''
    Get the BEDTools code used to identify the Bioconda package.
    '''

    return 'bedtools'

#-------------------------------------------------------------------------------

def get_bioconda_code():
    '''
    Get the Bioconda code used to identify its processes.
    '''

    return 'bioconda'

#-------------------------------------------------------------------------------

def get_bioconda_name():
    '''
    Get the Bioconda name used to title.
    '''

    return 'Bioconda'

#-------------------------------------------------------------------------------

def get_blastplus_code():
    '''
    Get the BLAST+ code used to identify its processes.
    '''

    return 'blast'

#-------------------------------------------------------------------------------

def get_blastplus_name():
    '''
    Get the BLAST+ name used to title.
    '''

    return 'BLAST+'

#-------------------------------------------------------------------------------

def get_blastplus_bioconda_code():
    '''
    Get the BLAST+ code used to identify the Bioconda package.
    '''

    return 'blast'

#-------------------------------------------------------------------------------

def get_bowtie2_code():
    '''
    Get the Bowtie2 code used to identify its processes.
    '''

    return 'bowtie2'

#-------------------------------------------------------------------------------

def get_bowtie2_name():
    '''
    Get the Bowtie2 name used to title.
    '''

    return 'Bowtie2'

#-------------------------------------------------------------------------------

def get_bowtie2_bioconda_code():
    '''
    Get the Bowtie2 code used to identify the Bioconda package.
    '''

    return 'bowtie2'

#-------------------------------------------------------------------------------

def get_busco_code():
    '''
    Get the BUSCO code used to identify its processes.
    '''

    return 'busco'

#-------------------------------------------------------------------------------

def get_busco_name():
    '''
    Get the BUSCO name used to title.
    '''

    return 'BUSCO'

#-------------------------------------------------------------------------------

def get_busco_bioconda_code():
    '''
    Get the BUSCO code used to identify the Bioconda package.
    '''

    return 'busco'

#-------------------------------------------------------------------------------

def get_cd_hit_code():
    '''
    Get the CD-HIT code used to identify its processes.
    '''

    return 'cdhit'

#-------------------------------------------------------------------------------

def get_cd_hit_name():
    '''
    Get the CD-HIT name used to title.
    '''

    return 'CD-HIT'

#-------------------------------------------------------------------------------

def get_cd_hit_bioconda_code():
    '''
    Get the CD-HIT code used to identify the Bioconda package.
    '''

    return 'cd-hit'

#-------------------------------------------------------------------------------

def get_cd_hit_est_code():
    '''
    Get the CD-HIT-EST code used to identify its processes.
    '''

    return 'cdhitest'

#-------------------------------------------------------------------------------

def get_cd_hit_est_name():
    '''
    Get the CD-HIT-EST name used to title.
    '''

    return 'CD-HIT-EST'

#-------------------------------------------------------------------------------

def get_conda_code():
    '''
    Get the Conda code used to identify its processes.
    '''

    return 'conda'

#-------------------------------------------------------------------------------

def get_conda_name():
    '''
    Get the Conda name used to title.
    '''

    return 'Conda'

#-------------------------------------------------------------------------------

def get_detonate_code():
    '''
    Get the DETONATE code used to identify its processes.
    '''

    return 'detonate'

#-------------------------------------------------------------------------------

def get_detonate_name():
    '''
    Get the DETONATE name used to title.
    '''

    return 'DETONATE'

#-------------------------------------------------------------------------------

def get_detonate_bioconda_code():
    '''
    Get the DETONATE code used to identify the Bioconda package.
    '''

    return 'detonate'

#-------------------------------------------------------------------------------

def get_emboss_code():
    '''
    Get the EMBOSS code used to identify its processes.
    '''

    return 'emboss'

#-------------------------------------------------------------------------------

def get_emboss_name():
    '''
    Get the EMBOSS name used to title.
    '''

    return 'EMBOSS'

#-------------------------------------------------------------------------------

def get_emboss_bioconda_code():
    '''
    Get the EMBOSS code used to identify the Bioconda package
    '''

    return 'emboss'

#-------------------------------------------------------------------------------

def get_fastqc_code():
    '''
    Get the FastQC code used to identify its processes.
    '''

    return 'fastqc'

#-------------------------------------------------------------------------------

def get_fastqc_name():
    '''
    Get the FastQC name used to title.
    '''

    return 'FastQC'

#-------------------------------------------------------------------------------

def get_fastqc_bioconda_code():
    '''
    Get the FastQC code used to identify the Bioconda package.
    '''

    return 'fastqc'

#-------------------------------------------------------------------------------

def get_gmap_gsnap_code():
    '''
    Get the GMAP-GSNAP code used to identify its processes.
    '''

    return 'gmap_gsnap'

#-------------------------------------------------------------------------------

def get_gmap_gsnap_name():
    '''
    Get the GMAP-GSNAP name used to title.
    '''

    return 'GMAP-GSNAP'

#-------------------------------------------------------------------------------

def get_gmap_gsnap_bioconda_code():
    '''
    Get the GMAP-GSNAP code used to identify the Bioconda package.
    '''

    return 'gmap'

#-------------------------------------------------------------------------------

def get_gmap_code():
    '''
    Get the GMAP code used to identify its processes.
    '''

    return 'gmap'

#-------------------------------------------------------------------------------

def get_gmap_name():
    '''
    Get the GMAP name used to title.
    '''

    return 'GMAP'

#-------------------------------------------------------------------------------

def get_gzip_code():
    '''
    Get the gzip code used to identify its processes.
    '''

    return 'gzip'

#-------------------------------------------------------------------------------

def get_gzip_name():
    '''
    Get the gzip name used to title.
    '''

    return 'gzip'

#-------------------------------------------------------------------------------

def get_insilico_read_normalization_code():
    '''
    Get the insilico_read_normalization (Trinity package) code used to identify its
    processes.
    '''

    return 'insreadnor'

#-------------------------------------------------------------------------------

def get_insilico_read_normalization_name():
    '''
    Get the insilico_read_normalization (Trinity package) name used to title.
    '''

    return 'insilico_read_normalization'

#-------------------------------------------------------------------------------

def get_miniconda3_code():
    '''
    Get the Miniconda3 code used to identify its processes.
    '''

    return 'miniconda3'

#-------------------------------------------------------------------------------

def get_miniconda3_name():
    '''
    Get the Miniconda3 name used to title.
    '''

    return 'Miniconda3'

#-------------------------------------------------------------------------------

def get_ngshelper_code():
    '''
    Get the NGShelper code used to identify its processes.
    '''

    return 'ngshelper'

#-------------------------------------------------------------------------------

def get_ngshelper_name():
    '''
    Get the NGShelper name used to title.
    '''

    return 'NGShelper'

#-------------------------------------------------------------------------------

def get_quast_code():
    '''
    Get the QUAST code used to identify process.
    '''

    return 'quast'

#-------------------------------------------------------------------------------

def get_quast_name():
    '''
    Get the QUAST name used to title.
    '''

    return 'QUAST'

#-------------------------------------------------------------------------------

def get_quast_bioconda_code():
    '''
    Get the QUAST code used to identify the Bioconda package.
    '''

    return 'quast'

#-------------------------------------------------------------------------------

def get_r_code():
    '''
    Get the R code used to identify its processes.
    '''

    return 'r'

#-------------------------------------------------------------------------------

def get_r_name():
    '''
    Get the R name used to title.
    '''

    return 'R'

#-------------------------------------------------------------------------------

def get_ref_eval_code():
    '''
    Get the REF-EVAL (DETONATE package) code used to identify its processes.
    '''

    return 'refeval'

#-------------------------------------------------------------------------------

def get_ref_eval_name():
    '''
    Get the REF-EVAL (DETONATE package) name used to title.
    '''

    return 'REF-EVAL'

#-------------------------------------------------------------------------------

def get_rnaquast_code():
    '''
    Get the rnaQUAST code used to identify its processes.
    '''

    return 'rnaquast'

#-------------------------------------------------------------------------------

def get_rnaquast_name():
    '''
    Get the rnaQUAST name used to title.
    '''

    return 'rnaQUAST'

#-------------------------------------------------------------------------------

def get_rsem_code():
    '''
    Get the RSEM code used to identify its processes.
    '''

    return 'rsem'

#-------------------------------------------------------------------------------

def get_rsem_name():
    '''
    Get the RSEM name used to title.
    '''

    return 'RSEM'

#-------------------------------------------------------------------------------

def get_rsem_bioconda_code():
    '''
    Get the RSEM code used to identify the Bioconda package.
    '''

    return 'rsem'

#-------------------------------------------------------------------------------

def get_rsem_eval_code():
    '''
    Get the RSEM-EVAL (DETONATE package) code used to identify its processes.
    '''

    return 'rsemeval'

#-------------------------------------------------------------------------------

def get_rsem_eval_name():
    '''
    Get the RSEM-EVAL (DETONATE package) name used to title.
    '''

    return 'RSEM-EVAL'

#-------------------------------------------------------------------------------

def get_samtools_code():
    '''
    Get the BEDTools code used to identify its processes.
    '''

    return 'samtools'

#-------------------------------------------------------------------------------

def get_samtools_name():
    '''
    Get the BEDTools name used to title.
    '''

    return 'SAMtools'

#-------------------------------------------------------------------------------

def get_samtools_bioconda_code():
    '''
    Get the BEDTools code used to identify the Bioconda package.
    '''

    return 'samtools'

#-------------------------------------------------------------------------------

def get_soapdenovotrans_code():
    '''
    Get the SOAPdenovo-Trans code used to identify its processes.
    '''

    return 'sdnt'

#-------------------------------------------------------------------------------

def get_soapdenovotrans_name():
    '''
    Get the SOAPdenovo-Trans name used to title.
    '''

    return 'SOAPdenovo-Trans'

#-------------------------------------------------------------------------------

def get_soapdenovotrans_bioconda_code():
    '''
    Get the SOAPdenovo-Trans code used to identify the Bioconda package.
    '''

    return 'soapdenovo-trans'

#-------------------------------------------------------------------------------

def get_star_code():
    '''
    Get the STAR code used to identify its processes.
    '''

    return 'star'

#-------------------------------------------------------------------------------

def get_star_name():
    '''
    Get the STAR name used to title.
    '''

    return 'STAR'

#-------------------------------------------------------------------------------

def get_star_bioconda_code():
    '''
    Get the STAR code used to identify the Bioconda package.
    '''

    return 'star'

#-------------------------------------------------------------------------------

def get_transabyss_code():
    '''
    Get the Trans-ABySS code used to identify its processes.
    '''

    return 'transabyss'

#-------------------------------------------------------------------------------

def get_transabyss_name():
    '''
    Get the Trans-ABySS name used to title.
    '''

    return 'Trans-ABySS'

#-------------------------------------------------------------------------------

def get_transabyss_bioconda_code():
    '''
    Get the Trans-ABySS code used to the Bioconda package.
    '''

    return 'transabyss'

#-------------------------------------------------------------------------------

def get_transcript_filter_code():
    '''
    Get the transcripts-filter (NGShelper package) code used to identify its
    processes.
    '''

    return 'transfil'

#-------------------------------------------------------------------------------

def get_transcript_filter_name():
    '''
    Get the transcripts-filter (NGShelper package) name used to title.
    '''

    return 'transcript-filter'

#-------------------------------------------------------------------------------

def get_transcriptome_blastx_code():
    '''
    Get the transcriptome-blastx (NGShelper package) code used to identify its
    processes.
    '''

    return 'transbastx'

#-------------------------------------------------------------------------------

def get_transcriptome_blastx_name():
    '''
    Get the transcriptome-blastx (NGShelper package) name used to title.
    '''

    return 'transcriptome-blastx'

#-------------------------------------------------------------------------------

def get_transrate_code():
    '''
    Get the Transrate  code used to identify its processes.
    '''

    return 'transrate'

#-------------------------------------------------------------------------------

def get_transrate_name():
    '''
    Get the FastQC name used to title.
    '''

    return 'Transrate'

#-------------------------------------------------------------------------------

def get_trimmomatic_code():
    '''
    Get the Trimmomatic code used to identify its processes.
    '''

    return 'trimmo'

#-------------------------------------------------------------------------------

def get_trimmomatic_name():
    '''
    Get the FastQC name used to title.
    '''

    return 'Trimmomatic'

#-------------------------------------------------------------------------------

def get_trimmomatic_bioconda_code():
    '''
    Get the Trimmomatic code used to the Bioconda package.
    '''

    return 'trimmomatic'

#-------------------------------------------------------------------------------

def get_trinity_code():
    '''
    Get the Trinity code used to identify its processes.
    '''

    return 'trinity'

#-------------------------------------------------------------------------------

def get_trinity_name():
    '''
    Get the Trinity name used to title.
    '''

    return 'Trinity'

#-------------------------------------------------------------------------------

def get_trinity_bioconda_code():
    '''
    Get the Trinity code used to the Bioconda package.
    '''

    return 'trinity'

#-------------------------------------------------------------------------------

def get_config_dir():
    '''
    Get the configuration directory in the local computer.
    '''

    return './config'

#-------------------------------------------------------------------------------

def get_keypairs_dir():
    '''
    Get the key pairs directory in the local computer.
    '''

    return './keypairs'

#-------------------------------------------------------------------------------

def get_temp_dir():
    '''
    Get the temporal directory in the local computer.
    '''

    return './temp'

#-------------------------------------------------------------------------------

def get_log_dir():
    '''
    Get the temporal directory in the local computer.
    '''

    return './logs'

#-------------------------------------------------------------------------------

def get_log_file(function_name=None):
    '''
    Get the log file name of in the local computer.
    '''
    # set the log file name
    now = datetime.datetime.now()
    date = datetime.datetime.strftime(now, '%y%m%d')
    time = datetime.datetime.strftime(now, '%H%M%S')
    if function_name is not None:
        log_file_name = '{0}/{1}-{2}-{3}-{4}.txt'.format(get_log_dir(), xconfiguration.environment, function_name, date, time)
    else:
        log_file_name = '{0}/{1}-x-{2}-{3}.txt'.format(get_log_dir(), xconfiguration.environment, date, time)

    # return the log file name
    return log_file_name

#-------------------------------------------------------------------------------

def list_log_files_command(local_process_id):
    '''
    Get the command to list log files in the local computer depending on the Operating System.
    '''
    # get log dir
    log_dir = get_log_dir()

    # assign the command
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        if local_process_id == 'all':
            command = 'ls {0}/{1}-*.txt'.format(log_dir, xconfiguration.environment)
        else:
            command = 'ls {0}/{1}-{2}-*.txt'.format(log_dir, xconfiguration.environment, local_process_id)
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        log_dir = log_dir.replace('/','\\')
        if local_process_id == 'all':
            command = 'dir /B {0}\{1}-*.txt'.format(log_dir, xconfiguration.environment)
        else:
            command = 'dir /B {0}\{1}-{2}-*.txt'.format(log_dir, xconfiguration.environment, local_process_id)

    # return the command
    return command

#-------------------------------------------------------------------------------

def get_local_process_dict():
    '''
    Get the local process dictionary.
    '''

    # build the local process dictionary
    local_process_dict = {}
    local_process_dict['add_node']= {'text': 'Add node in a cluster'}
    local_process_dict['create_cluster']= {'text': 'Create cluster'}
    local_process_dict['create_volume']= {'text': 'Create volume'}
    local_process_dict['delink_volume_from_template']= {'text': 'Delink volume in a cluster template'}
    local_process_dict['download_result_dataset']= {'text': 'Download result dataset from a cluster'}
    local_process_dict['kill_batch_job']= {'text': 'Kill batch job'}
    local_process_dict['link_volume_to_template']= {'text': 'Link volume in a cluster template'}
    local_process_dict['list_clusters']= {'text': 'List clusters'}
    local_process_dict['mount_volume']= {'text': 'Mount volume in a node'}
    local_process_dict['remove_node']= {'text': 'Remove node in a cluster'}
    local_process_dict['remove_volume']= {'text': 'Remove volume'}
    local_process_dict['replicate_volume']= {'text': 'Replicate volume to another zone'}
    local_process_dict['resize_volume']= {'text': 'Resize volume'}
    local_process_dict['restart_cluster']= {'text': 'Restart cluster'}
    local_process_dict['review_volume_links']= {'text': 'Review volumes linked to cluster templates'}
    local_process_dict['run_busco_process']= {'text': 'Run {0} process'.format(get_busco_name())}
    local_process_dict['run_cd_hit_est_process']= {'text': 'Run {0} process'.format(get_cd_hit_est_name())}
    local_process_dict['run_fastqc_process']= {'text': 'Run {0} process'.format(get_fastqc_name())}
    local_process_dict['run_gmap_process']= {'text': 'Run {0} process'.format(get_gmap_name())}
    local_process_dict['run_gzip_process']= {'text': 'Run compression/decompression process'}
    local_process_dict['run_insilico_read_normalization_process']= {'text': 'Run {0} process'.format(get_insilico_read_normalization_name())}
    local_process_dict['run_quast_process']= {'text': 'Run {0} process'.format(get_quast_name())}
    local_process_dict['run_ref_eval_process']= {'text': 'Run {0} process'.format(get_ref_eval_name())}
    local_process_dict['run_rnaquast_process']= {'text': 'Run {0} process'.format(get_rnaquast_name())}
    local_process_dict['run_rsem_eval_process']= {'text': 'Run {0} process'.format(get_rsem_eval_name())}
    local_process_dict['run_soapdenovotrans_process']= {'text': 'Run {0} process'.format(get_soapdenovotrans_name())}
    local_process_dict['run_star_process']= {'text': 'Run {0} process'.format(get_star_name())}
    local_process_dict['run_transabyss_process']= {'text': 'Run {0} process'.format(get_transabyss_name())}
    local_process_dict['run_transcript_filter_process']= {'text': 'Run {0} process'.format(get_transcript_filter_name())}
    local_process_dict['run_transcriptome_blastx_process']= {'text': 'Run {0} process'.format(get_transcriptome_blastx_name())}
    local_process_dict['run_transrate_process']= {'text': 'Run {0} process'.format(get_transrate_name())}
    local_process_dict['run_trimmomatic_process']= {'text': 'Run {0} process'.format(get_trimmomatic_name())}
    local_process_dict['run_trinity_process']= {'text': 'Run {0} process'.format(get_trinity_name())}
    local_process_dict['setup_bioconda_package_list']= {'text': 'Set up Bioconda package list'}
    local_process_dict['setup_conda_package_list']= {'text': 'Set up Conda package list'}
    local_process_dict['setup_miniconda3']= {'text': 'Set up {0}'.format(get_miniconda3_name())}
    local_process_dict['setup_ngshelper']= {'text': 'Set up {0}'.format(get_ngshelper_name())}
    local_process_dict['setup_r']= {'text': 'Set up {0}'.format(get_r_name())}
    local_process_dict['setup_rnaquast']= {'text': 'Set up {0}'.format(get_rnaquast_name())}
    local_process_dict['setup_transrate']= {'text': 'Set up {0}'.format(get_transrate_name())}
    local_process_dict['show_cluster_composing']= {'text': 'Show cluster composing'}
    local_process_dict['show_status_batch_jobs']= {'text': 'Show status of batch jobs'}
    local_process_dict['stop_cluster']= {'text': 'Stop cluster'}
    local_process_dict['terminate_cluster']= {'text': 'Terminate cluster'}
    local_process_dict['terminate_volume_creator']= {'text': 'Terminate volume creator'}
    local_process_dict['unmount_volume']= {'text': 'Unmount volume in a node'}
    local_process_dict['upload_database_dataset']= {'text': 'Upload database dataset to a cluster'}
    local_process_dict['upload_read_dataset']= {'text': 'Upload read dataset to a cluster'}
    local_process_dict['upload_reference_dataset']= {'text': 'Upload reference dataset to a cluster'}

    # return the local process dictionary
    return local_process_dict

#-------------------------------------------------------------------------------

def get_local_process_id(local_process_text):
    '''
    Get the local process identification from the local process text.
    '''

    # initialize the control variable
    local_process_id_found = None

    # get the dictionary of the local processes
    local_process_dict = get_local_process_dict()

    # search the local process identification
    for local_process_id in local_process_dict.keys():
        if local_process_dict[local_process_id]['text'] == local_process_text:
            local_process_id_found = local_process_id
            break

    # return the local process identification
    return local_process_id_found

#-------------------------------------------------------------------------------

def get_cluster_app_dir():
    '''
    Get the aplication directory in the cluster.
    '''

    return '/apps'

#-------------------------------------------------------------------------------

def get_cluster_reference_dir():
    '''
    Get the reference directory in the cluster.
    '''

    return '/references'

#-------------------------------------------------------------------------------

def get_cluster_reference_dataset_dir(reference_dataset_id):
    '''
    Get the directory of a reference dataset in the cluster.
    '''

    # set the reference directory in the cluster
    cluster_reference_dataset_dir = '{0}/{1}'.format(get_cluster_reference_dir(), reference_dataset_id)

    # return the reference directory in the cluster
    return cluster_reference_dataset_dir

#-------------------------------------------------------------------------------

def get_cluster_reference_file(reference_dataset_id, file_name):
    '''
    Get the reference file path of a reference dataset in the cluster.
    '''

    # set the path of the reference file
    cluster_reference_file = '{0}/{1}'.format(get_cluster_reference_dataset_dir(reference_dataset_id), os.path.basename(file_name))

    # return the path of the reference file
    return cluster_reference_file

#-------------------------------------------------------------------------------

def get_cluster_database_dir():
    '''
    Get the database directory in the cluster.
    '''

    return '/databases'

#-------------------------------------------------------------------------------

def get_cluster_database_dataset_dir(database_dataset_id):
    '''
    Get the directory of a database dataset in the cluster.
    '''

    # set the database directory in the cluster
    cluster_database_dataset_dir = '{0}/{1}'.format(get_cluster_database_dir(), database_dataset_id)

    # return the database directory in the cluster
    return cluster_database_dataset_dir

#-------------------------------------------------------------------------------

def get_cluster_database_file(database_dataset_id, file_name):
    '''
    Get the database file path of a database dataset in the cluster.
    '''

    # set the path of the database file
    cluster_database_file = '{0}/{1}'.format(get_cluster_database_dataset_dir(database_dataset_id), os.path.basename(file_name))

    # return the path of the database file
    return cluster_database_file

#-------------------------------------------------------------------------------

def get_cluster_read_dir():
    '''
    Get the read directory in the cluster.
    '''

    return '/reads'

#-------------------------------------------------------------------------------

def get_uploaded_read_dataset_name():
    '''
    Get the name of the row read dataset in the cluster.
    '''

    return 'uploaded-reads'

#-------------------------------------------------------------------------------

def get_cluster_experiment_read_dataset_dir(experiment_id, read_dataset_id):
    '''
    Get the directory of a experiment read dataset in the cluster.
    '''

    # set the experiment read directory in the cluster
    cluster_experiment_read_dataset_dir = '{0}/{1}/{2}'.format(get_cluster_read_dir(), experiment_id, read_dataset_id)

    # return the experiment read directory in the cluster
    return cluster_experiment_read_dataset_dir

#-------------------------------------------------------------------------------

def get_cluster_read_file(experiment_id, read_dataset_id, file_name):
    '''
    Get the read file path of an experiment read dataset in the cluster.
    '''

    # set the path of the read file
    cluster_read_file = '{0}/{1}'.format(get_cluster_experiment_read_dataset_dir(experiment_id, read_dataset_id), os.path.basename(file_name))

    # return the path of the read file
    return cluster_read_file

#-------------------------------------------------------------------------------

def get_cluster_result_dir():
    '''
    Get the result directory in the cluster.
    '''

    return '/results'

#-------------------------------------------------------------------------------

def get_cluster_experiment_result_dir(experiment_id):
    '''
    Get the directory of run result datasets in the cluster.
    '''

    # set the run result directory in the cluster
    cluster_experiment_results_dir = '{0}/{1}'.format(get_cluster_result_dir(), experiment_id)

    # return the run result directory in the cluster
    return cluster_experiment_results_dir

#-------------------------------------------------------------------------------

def get_cluster_experiment_result_dataset_dir(experiment_id, result_dataset_id):
    '''
    Get the directory of an experiment result dataset in the cluster.
    '''

    # set the experiment result dataset directory in the cluster
    cluster_experiment_result_dataset_dir = '{0}/{1}/{2}'.format(get_cluster_result_dir(), experiment_id, result_dataset_id)

    # return the experiment result dataset directory in the cluster
    return cluster_experiment_result_dataset_dir

#-------------------------------------------------------------------------------

def get_cluster_current_run_dir(experiment_id, process):
    '''
    Get the run directory of a bioinfo process in the cluster.
    '''

    # set the run identificacion
    now = datetime.datetime.now()
    date = datetime.datetime.strftime(now, '%y%m%d')
    time = datetime.datetime.strftime(now, '%H%M%S')
    run_id = '{0}-{1}-{2}'.format(process, date, time)

    # set the run directory in the cluster
    cluster_current_run_dir = get_cluster_experiment_result_dir(experiment_id) + '/' + run_id

    # return the run directory in the cluster
    return cluster_current_run_dir

#-------------------------------------------------------------------------------

def get_mounting_point_list():
    '''
    Get the available mounting point list.
    '''

    return [get_cluster_app_dir(), get_cluster_database_dir(), get_cluster_read_dir(), get_cluster_reference_dir(), get_cluster_result_dir()]

#-------------------------------------------------------------------------------

def get_cluster_log_file():
    '''
    Get the log file name of an experiment run in the cluster.
    '''

    return 'log.txt'

#-------------------------------------------------------------------------------

def change_extension(path, new_extension):
    '''Change the file extension.'''

    # get the path with the new extension
    i = path.rfind('.')
    if i >= 0:
        new_path = path[:i + 1] + new_extension
    else:
        new_path = path + new_extension

    # return the path with new extension
    return new_path

#-------------------------------------------------------------------------------

def existing_dir(dir):
    '''
    Verify if a directory exists.
    '''

    # normalize the directory path depending on the operating system
    dir = os.path.normpath(dir)

    # get the current directory and its parent directory
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)

    # if the opeating system is Linux or Mac OS X:
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        if dir.startswith('/'):
            pass
        elif dir == ('.'):
            dir = current_dir
        elif dir.startswith('./'):
            dir = '{0}/{1}'.format(current_dir, os.path.basename(dir[2:]))
        elif dir.startswith('../'):
            dir = '{0}/{1}'.format(parent_dir, os.path.basename(dir[3:]))
        else:
            dir = '{0}/{1}'.format(current_dir, os.path.basename(dir))

    # if the opeating system is Windows or Windows/Cygwin
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        if dir[1:3] == (':\\'):
            pass
        elif dir == ('.'):
            dir = current_dir
        elif dir.startswith('.\\'):
            dir = '{0}\{1}'.format(current_dir, os.path.basename(dir[2:]))
        elif dir.startswith('..\\'):
            dir = '{0}\{1}'.format(parent_dir, os.path.basename(dir[3:]))
        else:
            dir = '{0}\{1}'.format(current_dir, os.path.basename(dir))

    # return the verification of valid directory
    return os.path.isdir(dir)

#-------------------------------------------------------------------------------

def is_valid_path(path, operating_system=sys.platform):
    '''
    Verify if a path is a valid path.
    '''

    # initialize control variable
    valid = False

    # verify if the path is valid
    if operating_system.startswith('linux') or operating_system.startswith('darwin'):
        # -- valid = re.match('^(/.+)(/.+)*/?$', path)
        valid = True
    elif operating_system.startswith('win32') or operating_system.startswith('cygwin'):
        valid = True

    # return control variable
    return valid

#-------------------------------------------------------------------------------

def is_absolute_path(path, operating_system=sys.platform):
    '''
    Verify if a path is a absolute path.
    '''

    # initialize control variable
    valid = False

    # verify if the path is absolute
    if operating_system.startswith('linux') or operating_system.startswith('darwin'):
        if path != '':
            # -- valid = is_path_valid(path) and path[0] == '/'
            valid = True
    elif operating_system.startswith('win32') or operating_system.startswith('cygwin'):
        valid = True

    # return control variable
    return valid

#-------------------------------------------------------------------------------

def is_relative_path(path, operating_system=sys.platform):
    '''
    Verify if a path is a relative path.
    '''

    # initialize control variable
    valid = False

    # verify if the path is valid
    if operating_system.startswith('linux') or operating_system.startswith('darwin'):
        valid = True
    elif operating_system.startswith('win32') or operating_system.startswith('cygwin'):
        valid = True

    # return control variable
    return valid

#-------------------------------------------------------------------------------

def is_device_file(path, device_pattern):
    '''
    Verify if a path is a valid device file, e.g. /dev/sdf.
    '''

    # initialize control variable
    valid = False

    # build the complete pattern
    pattern = '^{0}$'.format(device_pattern)

    # verify if path is a valid device file
    valid = re.match(pattern, path)

    # return control variable
    return valid

#-------------------------------------------------------------------------------

def get_machine_device_file(aws_device_file):
    '''
    Get de machine device from AWS device
    E.g. /dev/sdb1 -> /dev/xvdb1.
    '''

    # determine the machine device file
    machine_device_file = aws_device_file[0:5] + 'xv' + aws_device_file[6:]

    # return the machine device file
    return machine_device_file

#-------------------------------------------------------------------------------

def is_email_address_valid(email):
    '''
    Verify if an e-mail address is valid.
    '''

    # initialize control variable
    valid = False

    # build the complete pattern
    pattern = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'

    # verify if the e-mail address is valid
    valid = re.match(pattern, email)

    # return control variable
    return valid

#-------------------------------------------------------------------------------

def get_option_dict(config_file):
    '''
    Get a dictionary with the options retrieved from a configuration file.
    '''

    # initialize the options dictionary
    option_dict = {}

    # create class to parse the configuration files
    config = configparser.ConfigParser()

    # read the configuration file
    config.read(config_file)

    # build the dictionary
    for section in config.sections():
        # get the keys dictionary
        keys_dict = option_dict.get(section, {})
        # for each key in the section
        for key in config[section]:
            # get the value of the key
            value = config.get(section, key, fallback='')
            # add a new enter in the keys dictionary
            keys_dict[key] = get_option_value(value)
        # update the section with its keys dictionary
        option_dict[section] = keys_dict

    # return the options dictionary
    return option_dict

#-------------------------------------------------------------------------------

def get_option_value(option):
    '''
    Remove comments ans spaces from an option retrieve from a configuration file.
    '''

    # Remove comments
    position = option.find('#')
    if position == -1:
        value = option
    else:
        value = option[:position]

    # Remove comments
    value = value.strip()

    # return the value without comments and spaces
    return value

#-------------------------------------------------------------------------------

def split_literal_to_integer_list(literal):
    '''
    Split a string literal in a integer value list which are separated by comma.
    '''
  
    # initialize the string values list and the interger values list
    strings_list = []
    integers_list = []
    
    # split the string literal in a string values list
    strings_list = split_literal_to_string_list(literal)

    # convert each value from string to integer
    for i in range(len(strings_list)):
        try:
            integers_list.append(int(strings_list[i]))
        except:
            integers_list = []
            break

    # return the integer values list
    return integers_list

#-------------------------------------------------------------------------------

def split_literal_to_float_list(literal):
    '''
    Split a string literal in a float value list which are separated by comma.
    '''
  
    # initialize the string values list and the float values list
    strings_list = []
    float_list = []
    
    # split the string literal in a string values list
    strings_list = split_literal_to_string_list(literal)

    # convert each value from string to float
    for i in range(len(strings_list)):
        try:
            float_list.append(float(strings_list[i]))
        except:
            float_list = []
            break

    # return the float values list
    return float_list

#-------------------------------------------------------------------------------

def split_literal_to_string_list(literal):
    '''
    Split a string literal in a string value list which are separated by comma.
    '''
  
    # initialize the string values list
    string_list = []

    # split the string literal in a string values list
    string_list = literal.split(',')

    # remove the leading and trailing whitespaces in each value
    for i in range(len(string_list)):
        string_list[i] = string_list[i].strip()

    # return the string values list
    return string_list

#-------------------------------------------------------------------------------

def pair_files(file_name_list, specific_chars_1, specific_chars_2):
    '''
    ...
    '''

    # initialize the file lists
    file_name_1_list = []
    file_name_2_list = []
    unpaired_file_name_list = []

    # for each file name, append it to the corresponding list
    for file_name in file_name_list:
        if file_name.find(specific_chars_1) >= 0:
            file_name_1_list.append(file_name)
        elif  file_name.find(specific_chars_2) >= 0:
            file_name_2_list.append(file_name)
        else:
            unpaired_file_name_list.append(file_name)
    file_name_1_list.sort()
    file_name_2_list.sort()

    # verify the file pairing
    review_file_name_1_list = []
    review_file_name_2_list = []
    index_1 = 0
    index_2 = 0
    while index_1 < len(file_name_1_list) or index_2 < len(file_name_2_list):
        if index_1 < len(file_name_1_list):
            file_name_1 = file_name_1_list[index_1]
            short_file_name_1 = file_name_1.replace(specific_chars_1, '')
        if index_2 < len(file_name_2_list):
            file_name_2 = file_name_2_list[index_2]
            short_file_name_2 = file_name_2.replace(specific_chars_2, '')
        if short_file_name_1 == short_file_name_2:
            review_file_name_1_list.append(file_name_1)
            index_1 += 1
            review_file_name_2_list.append(file_name_2)
            index_2 += 1
        elif short_file_name_1 < short_file_name_2:
            unpaired_file_name_list.append(file_name_1)
            index_1 += 1
        elif short_file_name_1 > short_file_name_2:
            unpaired_file_name_list.append(file_name_2)
            index_2 += 1

    # return the file lists
    return (review_file_name_1_list, review_file_name_2_list, unpaired_file_name_list)

#-------------------------------------------------------------------------------

def run_command(command, log):
    '''
    Run a Bash shell command and redirect stdout and stderr to log.
    '''

    # run the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(process.stdout.readline, b''):
        # replace non-ASCII caracters by one blank space
        line = re.sub(b'[^\x00-\x7F]+', b' ', line)
        # control return code and new line characters
        if not isinstance(log, DevStdOut):
            line = re.sub(b'\r\n', b'\r', line)
            line = re.sub(b'\r', b'\r\n', line)
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            pass
        elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
            line = re.sub(b'\r\n', b'\r', line)
            line = re.sub(b'\r', b'\r\n', line)
        # create a string from the bytes literal
        line = line.decode('utf-8')
        # write the line in log
        log.write('{0}'.format(line))
    rc = process.wait()

    # return the return code of the command run
    return rc

#-------------------------------------------------------------------------------

def get_separator():
    '''
    Get the separation line between process steps.
    '''

    return '**************************************************'

#-------------------------------------------------------------------------------

class DevStdOut(object):
    '''
    This class is used when it is necessary write in sys.stdout and in a log file
    '''

    #---------------

    def __init__(self, calling_function=None, print_stdout=True):
        '''
        Execute actions correspending to the creation of a "DevStdOut" instance.
        '''

        # save initial parameters in instance variables
        self.calling_function = calling_function
        self.print_stdout = print_stdout

        # get the local log file
        self.log_file = get_log_file(self.calling_function)

        # open the local log file
        try:
            if not os.path.exists(os.path.dirname(self.log_file)):
                os.makedirs(os.path.dirname(self.log_file))
            self.log_file_id = open(self.log_file, mode='w', encoding='iso-8859-1')
        except:
            print('*** ERROR: The file {0} can not be created'.format(self.log_file))

    #---------------

    def write(self, message):
        '''
        Write the message in sys.stadout and in the log file
        '''

        # write in sys.stdout
        if self.print_stdout:
            sys.stdout.write(message)

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

    def __del__(self):
        '''
        Execute actions correspending to the object removal.
        '''

        # close the local log file
        self.log_file_id.close()

    #---------------

#-------------------------------------------------------------------------------

class DevNull(object):
    '''
    This class is used when it is necessary do not write a output
    '''

    #---------------

    def write(self, *_):
        '''
        Do not write anything.
        '''

        pass

    #---------------

#-------------------------------------------------------------------------------
 
class ProgramException(Exception):
    '''
    This class controls various exceptions that can occur in the execution of the application.
    '''

   #---------------

    def __init__(self, code_exception, param1='', param2='', param3=''):
        '''
        Execute actions correspending to the creation of an instance to manage a passed exception.
        ''' 

        if code_exception == 'C001':
            print('*** ERROR {0}: The application do not work if config files are not OK.'.format(code_exception), file=sys.stderr)
            sys.exit(1)
        elif code_exception == 'C002':
            print('*** ERROR {0}: The application do not work if the environment file is not OK.'.format(code_exception), file=sys.stderr)
            sys.exit(1)
        elif code_exception == 'EXIT':
            sys.exit(0)
        elif code_exception == 'P001':
            print('*** ERROR {0}: This program has parameters with invalid values.'.format(code_exception), file=sys.stderr)
            sys.exit(1)
        elif code_exception == 'S001':
            print('*** ERROR {0}: There are libraries are not installed.'.format(code_exception, param1), file=sys.stderr)
            sys.exit(1)
        elif code_exception == 'S002':
            print('*** ERROR {0}: There is infrastructure software not installed.'.format(code_exception), file=sys.stderr)
            sys.exit(1)
        else:
            print('*** ERROR {0}: This exception is not managed.'.format(code_exception), file=sys.stderr)
            sys.exit(1)

   #---------------

#-------------------------------------------------------------------------------

class BreakAllLoops(Exception):
    '''
    This class is used to break out of nested loops
    '''

    pass

#-------------------------------------------------------------------------------

if __name__ == '__main__':
     print('This source contains general functions and classes used in {0} software package used in both console mode and gui mode.'.format(get_project_name()))
     sys.exit(0)

#-------------------------------------------------------------------------------
