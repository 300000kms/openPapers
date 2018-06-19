#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""genera el archivo de zonas listo
        para ser utilizado
        el objetivo es asociar a cada zona un distrito
        cada uno de los dos datasets debe de detenr una tabla llamada elements
        y  un id y un name
"""

import json
import math
import sqlite3
import pyspatialite.dbapi2 as db
import os.path
import shutil
from routes import *


def addDistricte(table):
    conn = db.connect(r_db_zones)
    c = conn.cursor()
    try:
        c.execute('alter table '+table+' add column d_id')
    except Exception as e:
        print e
    try:
        c.execute('alter table '+table+' add column d_name')
    except Exception as e:
        print e
    conn.commit()
    conn.close()
    return


def updateFields():
    for dbase in [r_db_zones, r_db_districtes]:
        conn = db.connect(dbase)
        c = conn.cursor()
        c.execute('update elements set id = cast(id as text)')
        c.execute('update elements set name = cast(name as text)')
        conn.commit()
        conn.close()
    return


def updateGeomFields():
    for dbase in [r_db_zones, r_db_districtes]:
        print dbase
        conn = db.connect(dbase)
        c = conn.cursor()
        try:
            c.execute("select AddGeometryColumn('elements', 'geom_25831', 25831, 'POLYGON')")
            conn.commit()
        except:
            print '*'
        c.execute('update elements set geom_25831 = st_transform("geometry", 25831)')
        conn.commit()
        conn.close()
    return


def intersectData():
    conn = db.connect(r_db_zones)
    c = conn.cursor()
    c.execute("attach database '"+r_db_districtes+"' as a")
    c.execute(  'update elements set d_id = '\
                '(select cast(a.id as text) from a.elements as a '\
                'where st_intersects(st_centroid(elements.geom_25831), a.geom_25831))')
    c.execute(  'update elements set d_name = '\
                '(select cast(a.name as text) from a.elements as a '\
                'where st_intersects(st_centroid(elements.geom_25831), a.geom_25831))')
    conn.commit()
    conn.close()
    return

if __name__ == '__main__':

    updateFields()
    updateGeomFields()
    addDistricte('elements')
    intersectData()