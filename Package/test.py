#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

import boto3
import configparser
import re
import sys

import cbioinfoapp
import ccloud
import cdataset
import cinputs
import clib
import clog
import cmenu
import gbioinfoapp
import gcloud
import gdataset
import gdialogs
import glog
import gmain
import NGScloud
import xbioinfoapp
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
import xread
import xreference
import xresult
import xrnaquast
import xsoapdenovotrans
import xstar
import xssh
import xtransabyss
import xtransrate
import xtrimmomatic
import xtrinity
import xvolume

#-------------------------------------------------------------------------------

def main(argv):

    xconfiguration.environment = 'test'
    xconfiguration.set_environment_variables()

    xcluster.open_terminal(cluster_name='test-t2.micro', node_name='master')

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv[1:])
    sys.exit(0)

#-------------------------------------------------------------------------------
