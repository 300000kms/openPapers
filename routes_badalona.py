#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""rutes generals
"""
'''
zonesDB  = 'zones.sqlite' #el nombre de la tabla tambien debe ser zones
boundsDB = 'bounds_2.sqlite'
rootBase='bases'
rootData ='data'
rootTemp ='_templates'
project = '/home/pablo/Documents/_sync/17037 arrels_reus/project_reus/'

todo: load conf from json file
'''
#r_proj = '/home/pablo/Documents/_sync/17037 arrels_reus/project_reus/'
#r_proj = '/media/pablueke/CE0A39130A38FA53/_sync/17037 arrels_reus/project_tarragona/'
#r_proj = '/media/pablueke/CE0A39130A38FA53/_sync/17037 arrels_reus/project_mataro/'

import os
root = '/'.join( os.getcwd().split('/')[0:-1] )

city = 'badalona'

################################################################
project = 'project_'+city
r_proj = root+'/'+project+'/'

r_zones = r_proj+'zones/'
r_bases = r_proj+'bases/'
r_bounds = r_proj+'bounds/'
r_templates = r_proj+'templates/'
r_temp = r_proj+'temp/'
r_datain = r_proj+'data_in/'
r_out = r_proj+'out/'

r_db_zones  = r_zones+'zones.sqlite'
r_db_districtes  = r_zones+'districtes.sqlite'
r_db_bounds = r_bounds+'bounds.sqlite'

SRID = 25831
