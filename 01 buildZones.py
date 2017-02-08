#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    genera el archivo de zonas listo
        para ser utilizado
        el objetivo es asociar a cada zona un distrito
        cada uno de los dos datasets debe de detenr una tabla llamada elements
        y  un id y un name
    descargar el callejero de http://www.cartociudad.es/portal/
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
    '''
    se asegura que todo está en formato txt y sin caracteres especiales
    '''
    for dbase in [r_db_zones, r_db_districtes]:
        print dbase
        conn = db.connect(dbase)
        c = conn.cursor()
        #c.execute('update elements set id   = replace(cast(id as text), \':\', \'_\' ) '')
        c.execute('update elements set id   = replace( replace(  replace( cast(  id as text), \':\', \'_\' ),\'\'\'\' ,\'_\' ),\'/\' ,\'_\' ) ')
        #c.execute('update elements set name = cast(name as text)')
        c.execute('update elements set name  = replace( replace( replace( cast(name as text), \':\', \'_\' ),\'\'\'\' ,\'_\' ),\'/\' ,\'_\' )  ')
        conn.commit()
        conn.close()
    return


def updateGeomFields():
    for dbase in [r_db_zones, r_db_districtes]:
        print dbase
        conn = db.connect(dbase)
        c = conn.cursor()
        c.execute('''create table temp as select id, name, st_transform(geometry, 25831) as geometry from elements ''')
        conn.commit()
        c.execute('''drop table elements''')
        conn.commit()
        c.execute('''alter table temp rename to elements''')
        conn.commit()
        c.execute('''select RecoverGeometryColumn('elements', 'geometry', 25831, 'POLYGON')''')
        conn.commit()
        c.execute('''select CreateSpatialIndex ('elements', 'geometry')''')
        conn.commit()
        c.execute('''vacuum''')
        conn.commit()
        conn.close()
    return


def intersectData():
    conn = db.connect(r_db_zones)
    c = conn.cursor()
    c.execute("attach database '"+r_db_districtes+"' as a")
    c.execute(  'update elements set d_id = '\
                '(select cast(a.id as text) from a.elements as a '\
                'where st_intersects(pointonsurface(elements.geometry), a.geometry))')
    c.execute(  'update elements set d_name = '\
                '(select cast(a.name as text) from a.elements as a '\
                'where st_intersects(pointonsurface(elements.geometry), a.geometry))')
    conn.commit()
    conn.close()
    return

if __name__ == '__main__':


    updateFields()
    updateGeomFields()


    addDistricte('elements')
    intersectData()

