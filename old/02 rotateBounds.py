import os
import subprocess as sub

from shapely.geometry import Polygon
from shapely import affinity

import json
import math
import sqlite3
import pyspatialite.dbapi2 as db
import os.path
import shutil

from routes import *


'''
necesitamos una base de origen con columna name y GEOMETRY
requiere folders
data, con las zones.sqlite
_templates, con una copia de base spatialite


SELECT load_extension('libspatialite-2.dll');
SELECT load_extension('mod_spatialite');

conn.enable_load_extension(True)


'''


#version con gdal
def convexHull2():
    query = 'select name , asgeojson(st_convexhull(geometry)) from  elements' #' order by name'
    path = r_db_zones
    p = sub.Popen(['ogrinfo','-al', '-sql', query, path, '-q'], stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    output=output[20:] #elimina el encabezado de la respuesta
    print output
    return output

def convexHull():
    conn = db.connect(r_db_zones)
    c = conn.cursor()
    c.execute('select name , asgeojson(st_convexhull(geometry)) from  elements')
    result =c.fetchall()
    return result


def getAngle(p1,p2):
    segment = (p1, p2)
    tan= (segment[1][0]-segment[0][0])/(segment[1][1]-segment[0][1])
    angle=math.degrees(math.atan(tan))
    return angle

def Bounds(polygon):
    bounds=polygon.bounds
    pol=Polygon([(bounds[0], bounds[1]),(bounds[0], bounds[3]),(bounds[2], bounds[3]),(bounds[2], bounds[1])])
    return pol

def findMinCv(name, polygon):
    bb = polygon.bounds
    ang = 0
    refarea = Bounds(polygon).area
    cc=polygon.centroid
    for p in range(len(polygon.exterior.coords[:])-1):
        angle = getAngle(polygon.exterior.coords[p], polygon.exterior.coords[p+1])
        rPolygon= affinity.rotate(polygon, angle, origin=cc)
        if Bounds(rPolygon).area < refarea:
            ang = angle
            bbx = affinity.rotate(Bounds(rPolygon), (360-angle), origin = cc)
    return (bbx, ang)


def createSqlite():
    if not os.path.exists(r_bounds):
        os.makedirs(r_bounds)

    conn = db.connect(r_db_bounds)
    c = conn.cursor()
    c.execute('select InitSpatialMetaData(1)')
    try:
        c.execute('drop table elements')
        conn.commit()
    except Exception as e:
        print e
    c.execute('CREATE TABLE if not exists elements (name, ang)')
    conn.commit()
    c.execute("select addgeometrycolumn('elements', 'geometry', 25831,'POLYGON', 2)")
    conn.commit()
    c.execute("SELECT CreateSpatialIndex('elements', 'geometry')")
    conn.commit()
    conn.close()

    return

def toSqlite(name, ang, bbx):
    conn = db.connect(r_db_bounds)
    c = conn.cursor()
    c.execute('''insert into elements ( name, ang, geometry ) values ( ?, ?, GeomFromEWKT( ? ) )''', (name, ang, "SRID=25831;"+str(bbx) ) )
    conn.commit()
    conn.close()
    return

if __name__ == '__main__':
    createSqlite()
    rows = convexHull()
    for row in rows:
        name = row[0]
        geom =  json.loads(row[1])
        print '.',
        polygon = Polygon(geom.get('coordinates')[0]) #hacer un test de si verdaderamente es un poligono?
        bbx, ang = findMinCv(name, polygon)
        toSqlite(name, ang, bbx)
