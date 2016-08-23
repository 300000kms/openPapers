#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
este código divide cada zona del archivo bounds.sqlite en un rectángulo óptimo y rotado de la proporcion deseada con escala aproximada a la indicada

necesitamos en la cartpeta data el archivo bounds.sqlite
se le añadira la tabala elementsdiv que contiene las subdivisiones
las que intersecan con el poligono de origen
'''

import os
import subprocess as sub
from shapely.geometry import Polygon, box
from shapely import affinity
from shapely.ops import cascaded_union
from shapely.ops import unary_union

import json
import math
import sqlite3
import pyspatialite.dbapi2 as db

from shapely.geometry import mapping, shape

#tamaño del papel
pA=[190,190] #x,y en milímetros

#escala del dibujo
sc = float(0.002) #(1/1000)

#directorio
rootBase='bases/'
#dirrectorio donde se encuentran los datos
rootData ='data/bounds.sqlite'

###############################################################################

#get figuras
def getB():
    conn = db.connect(rootData)
    c = conn.cursor()
    c.execute('''select name, ang, asgeojson(geometry) from elements''')
    results = c.fetchall()
    resultsCl = []
    for r in results:
        name = r[0]
        ang  = float(r[1])
        geom = shape(json.loads(r[2]))
        resultsCl.append([name, ang, geom])

    conn.commit()
    conn.close()
    #devuelve una lista de poligonos (name, ang, geom)
    return resultsCl

#devuelve la posicion del valor mayor de una lista
def bigger(lista):
    r=0
    for e in range(len(lista)):
        if abs(lista[e])>abs(lista[r]):
            r=e
    return r

## devuelve la orientacion
## asimilando la orientacion de la vinyeta final
def gO(s):
    print s
    cc=s[2].centroid
    rP= affinity.rotate(s[2], s[1], origin=cc)
    bn= rP.bounds
    x=bn[2]-bn[0]
    y=bn[3]-bn[1]
    #en caso de que la proporcion no sea cuadrada esto importa
    if max([x,y])==max(pA): #aquí antes utilizaba la funciona bigger, porque?
        return s[1]
    else:
        print '--------------'
        return s[1]+90 #devuleve el angulo normal o +90##########################################

#obtiene el ancho de un polígono
def getW(pol):
    bn= pol.bounds
    x=bn[0]-bn[2]
    return abs(x)

#obtiene el alto de un polígono
def getH(pol):
    bn= pol.bounds
    y=bn[1]-bn[3]
    return abs(y)


def divide(lX, lY, rP,w):
    x = getW(rP) #el ancho
    y = getH(rP) #el altro
    ox, oy = rP.bounds[0], rP.bounds[1] #coje el origen del cuadrado
    rrx=int(x/lX) if w == 'x' else int(x/lX)+1
    rry=int(y/lY) if w == 'y' else int(y/lY)+1
    rectangles = []
    for rx in range(rrx):
        for ry in range(rry):
            #print rx, ry
            bbox= (ox+rx*lX, oy+ry*lY, ox+(rx+1)*lX, oy+(ry+1)*lY)
            #print 'rect : ',bbox
            rect = box(bbox[0], bbox[1],bbox[2],bbox[3] )
            rectangles.append([rect, rx, ry])

    return rectangles


def createSqlite():

    conn = db.connect(rootData)
    c = conn.cursor()

    c.execute('CREATE TABLE if not exists elementsdiv (name, ang, x, y)')
    conn.commit()

    c.execute('select addgeometrycolumn("elementsdiv", "geometry", 25831, "POLYGON", 2)')
    conn.commit()

    c.execute("SELECT CreateSpatialIndex('elementsdiv', 'geometry')")
    conn.commit()

    conn.close()
    return


def takeZona(n):
    conn = db.connect(rootBase+'zones.sqlite')
    c = conn.cursor()
    print n
    c.execute('''SELECT asgeojson(geometry) from zones where name is ?''', (str(n),) )
    result = c.fetchone()
    conn.commit()
    conn.close()
    print result[0]
    r =shape(json.loads(result[0]))
    #devuelve el poligono
    return r

def saveR(rectangles, A, cc, n):
    zona = takeZona(n)
    polis =[]
    for r in rectangles:
        polis.append(r[0])

    union = affinity.rotate(cascaded_union(polis), -A, origin=cc)
    dx = union.centroid.x-cc.x
    dy = union.centroid.y-cc.y
    print 'translate : ',dx, dy
    data2save=()
    for r in rectangles:
        rotated=affinity.rotate(r[0], -A, origin=cc)
        translated = affinity.translate(rotated, -dx, -dy)
        #verificar si interseca
        print zona.intersects(translated)
        if zona.intersects(translated):
            data = (n, A, r[1], r[2], "SRID=25831;"+str(translated))
            data2save += (data,)
        #print data
    conn = db.connect(rootData)
    c = conn.cursor()
    c.executemany('''insert into elementsdiv ( name, ang, x, y, geometry ) values ( ?, ?, ?,?, GeomFromEWKT( ? ) )''', data2save )
    conn.commit()
    conn.close()

    return

def getTiles(s):
    #se realizaran dos dvisiones con diferencia de rotación de 90º
    #o = gO(s)
    A= s[1] # el angulo de orientacion
    cc=s[2].centroid # el centro de giro
    rP= affinity.rotate(s[2], A, origin=cc) #el polígono rotado

    x = getW(rP) #el ancho
    y = getH(rP) #el altro

    #print (x/pA[0]/1000/sc), (y/pA[1]/1000/sc)
    divX=int(x/pA[0]/1000/sc) ############redondear a la alza??????????????????
    divY=int(y/pA[1]/1000/sc)

    if divX==0:
        divX=1

    if divY==0:
        divY=1

    #print 'divisores   : ',divX, divY
    #print 'diferencias : ',(x/pA[0]/1000/sc)-divX, (y/pA[1]/1000/sc)-divY
    diffX = x-((x/pA[0]/1000/sc)-divX)*x
    diffY = y-((y/pA[1]/1000/sc)-divY)*y

    #print 'diff        : ', diffX, diffY

    #aqui a lo mejor está mal y lo tengo que cambiar
    if diffX < diffY:
        #tomar como divsiror la x
        lX = x/divX #corregir aqui , que a veces divX es 0!///////////////////////////////////////////
        lY = pA[1]*lX/pA[0] #proporcion
        rectangles = divide(lX, lY, rP,'x') #enviar a funcion divisora
        saveR(rectangles, A, cc, s[0])

    elif diffX >= diffY:
        lY = y/divY #proporcion
        lX = pA[0]*lY/pA[1]
        rectangles = divide(lX, lY, rP,'y')
        saveR(rectangles, A, cc, s[0])

    return

if __name__ == '__main__':
    createSqlite()
    #vobtenemos los poligonos a dividir
    sh = getB()
    for s in sh:
        print s
        #coje cada polígono y devuelve un listado de polígonos resultado de la división
        div = getTiles(s)



