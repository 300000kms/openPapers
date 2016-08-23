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

'''
necesitamos una base de origen con columna name y GEOMETRY
requiere folders
data, con las zones.sqlite
_templates, con una copia de base spatialite
'''

zonesDB  = 'zones.sqlite' #el nombre de la tabla tambien debe ser zones
boundsDB = 'bounds_2.sqlite'
rootBase='bases'
rootData ='data'
rootTemp ='_templates'

def convexHull():
    query = 'select name , asgeojson(st_convexhull(GEOMETRY)) from  zones' #' order by name'
    #query= 'select asgeojson(st_convexhull(GEOMETRY)) from  zones'
    path = rootBase+'/'+zonesDB
    p = sub.Popen(['ogrinfo','-al', '-sql', query, path, '-q'], stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    output=output[20:] #elimina el encabezado de la respuesta
    return output

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
            #bbx = affinity.rotate(Bounds(rPolygon), (angle), origin = cc)
    return (bbx, ang)

'''
def createSqlite2():
    query= 'CREATE TABLE if not exists elements (name, ang, geometry)'
    #query= 'select asgeojson(st_convexhull(GEOMETRY)) from  zones'
    path= rootBase+'/bounds.sqlite'
    p = sub.Popen(['ogrinfo','-al', '-sql', query, path, ], stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    print output, errors
    return



def createSqlite():
    if not os.path.exists(rootData):
        os.makedirs(rootData)

    conn = db.connect(rootData+'/'+boundsDB)

    c = conn.cursor()
    c.execute('CREATE TABLE if not exists elements (name, ang)')
    conn.commit()

    c.execute('select initspatialmetadata()')
    c.execute('select addgeometrycolumn("elements", "geometry", 25831, "POLYGON", 2)')
    conn.commit()
    conn.close()
    return
'''

def createSqlite2():

    if not os.path.exists(rootData):
        os.makedirs(rootData)

    if os.path.isfile('rootData'+'/'+boundsDB) == False:
        shutil.copy(rootTemp+'/template.sqlite', rootData+'/'+boundsDB)
        conn = db.connect(rootData+'/'+boundsDB)
        c = conn.cursor()
        c.execute('CREATE TABLE if not exists elements (name, ang)')
        conn.commit()
        c.execute('select addgeometrycolumn("elements", "geometry", 25831, "POLYGON", 2)')
        conn.commit()
        c.execute("SELECT CreateSpatialIndex('elements', 'geometry')")
        conn.commit()
        conn.close()

    return

def toSqlite(name, ang, bbx):
    conn = db.connect(rootData+'/'+boundsDB)
    c = conn.cursor()
    #print bbx
    #print '''insert into elements ( name, ang, geometry ) values ( %s, %s, GeomFromEWKT( %s ) )''' %(name, ang, str(bbx) )
    c.execute('''insert into elements ( name, ang, geometry ) values ( ?, ?, GeomFromEWKT( ? ) )''', (name, ang, "SRID=25831;"+str(bbx) ) )
    #print('insert into elements ( name, ang, geometry ) values ( '+str(name)+', '+str(ang)+', GeomFromEWKT( "'+str(bbx)+'" ) )' )
    conn.commit()
    conn.close()
    return

if __name__ == '__main__':
    createSqlite2()
    rows = convexHull().split('\n\n') #esta operacion falla en caso de que el campo name contenga un \n
    for r in range(0,len(rows)):
        name = rows[r].split('\n')[1].split(' = ')[1] if len(rows[r].split('\n'))>1 else None
        geom =  json.loads(rows[r].split('\n')[2].split(' = ')[1]) if len(rows[r].split('\n'))>2 else ''
        print '.',
        if len(rows[r].split('\n'))>2:
            polygon = Polygon(geom.get('coordinates')[0])
            bbx, ang = findMinCv(name, polygon)
            toSqlite(name, ang, bbx)
            print '*',
        else:
            print 'error on ', name
