#!/usr/bin/env python
# -*- coding: utf8
import os
import routes


path = routes.r_proj
folders = ['data_in', 'bounds', 'cartobase', 'img', 'in', 'out', 'pdf', 'qrcodes', 'zones']


def createFolder(folder):
    dir_exists = os.path.isdir(folder)
    if dir_exists is False:
        os.makedirs(folder)
        print '>>> created folder :', folder
    return

createFolder(path)
for f in folders:
    createFolder(path+f)
