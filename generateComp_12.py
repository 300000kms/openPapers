#!/usr/bin/python
# -*- coding: utf-8 -*-
from qgis.core import QgsProject
from PyQt4.QtCore import QFileInfo, QPointF
from qgis.utils import iface
from qgis.gui import QgsMapCanvas
from PyQt4.QtXml import QDomDocument
import json
import qrcode

root='/media/pablueke/DADES/_encargos/15013 arrels/'

layers={
   'masa':('cartobase/masa_demo_camer_4326.sqlite', 'mdinamica_4326', 'geometry'),
   'parcela':('cartobase/parcela_demo_camer_4326.sqlite', 'pdinamica_4326_r03', 'geometry'),
   'zones':('bases/zones.sqlite', 'zones', 'geometry'),
   'zones2':('bases/zones.sqlite', 'zones', 'geometry'),
   'bounds' : ('data/bounds.sqlite', 'elements', 'geometry') ,
   'divisions' : ('data/bounds.sqlite', 'elementsdiv', 'geometry'),
   'divisions2' : ('data/bounds.sqlite', 'elementsdiv', 'geometry'),
   'districtes' : ('cartobase/districtes.sqlite', 'districtes', 'geometry')
   }

root='/media/pablueke/DADES/_encargos/15013 arrels/'
qptChapter  = 'arrelsAtlas_chapter.qpt'
qptDivision = 'arrelsAtlas_division.qpt'
qptForm = 'arrelsAtlas_form.qpt'

###############################################################################
###############################################################################
###############################################################################

def loadLayer(l):
    desc=layers[l]
    uri = QgsDataSourceURI()
    uri.setDatabase(root+desc[0])
    schema = uri.uri()
    table = desc[1]
    geom_column = desc[2]
    criteria=''
    display_name = l
    uri.setDataSource(schema, table, geom_column, criteria)
    layer= QgsVectorLayer(uri.uri(), display_name, 'spatialite')
    QgsMapLayerRegistry.instance().addMapLayer(layer)
    print 'loaded : ',display_name
    return

def saveProject(name):
    project = QgsProject.instance()
    project.write(QFileInfo(root+name+'.qgs'))
    print project.fileName()
    return

def filter(layerName, criteria):
    desc=layers[layerName]
    l=QgsMapLayerRegistry.instance().mapLayer(mapL[layerName])
    table = desc[1]
    schema=''
    geom_column = desc[2]
    display_name = layerName
    uri = QgsDataSourceURI()
    uri.setDatabase(root+desc[0])
    uri.setDataSource(schema, table, geom_column, criteria)
    l.setDataSource(uri.uri(),  display_name, 'spatialite')
    return

def filterLayer(layerName, criteria):
    lyrs = QgsMapLayerRegistry.instance().mapLayers()
    schema = ''
    for l in lyrs:
        if QgsMapLayerRegistry.instance().mapLayer(l).name() == layerName:

            desc=layers[layerName]
            uri = QgsDataSourceURI()
            uri.setDatabase(root+desc[0])
            schema = ''
            table = desc[1]
            geom_column = desc[2]

            uri.setDataSource(schema, table, geom_column, criteria)

            layer=QgsMapLayerRegistry.instance().mapLayer(l)
            print layer.dataProvider().dataSourceUri()

            layer.dataProvider().setDataSourceUri(uri.uri())
            layer.rendererV2().symbol().setAlpha(1)
            QgsMapLayerRegistry.instance().reloadAllLayers()
            layer.dataProvider().reloadData()
            layer.dataProvider().forceReload()
            layer.triggerRepaint()

            QgsMapCanvas().refresh()
            qgis.utils.iface.mapCanvas().refresh()
            iface.mapCanvas().refresh()
            #layer.setDataSource(uri.uri(),  table, geom_column)


    return

def selectLayer(layerName, criteria):
    for l in lyrs:
        if QgsMapLayerRegistry.instance().mapLayer(l).name() == layerName:
            request = QgsFeatureRequest().setFilterExpression( criteria )
            it = QgsMapLayerRegistry.instance().mapLayer(l).getFeatures( request )
            QgsMapLayerRegistry.instance().mapLayer(l).setSelectedFeatures([s.id() for s in it])
            print list(it)


def mapL():
    mapL={}
    reg = QgsMapLayerRegistry.instance()
    lyrs = reg.mapLayers().keys()
    lyrsName = reg.mapLayers().values()

    for l in lyrsName:
        mapL[l.name()]=l.id()
    return mapL

def makeQR(data,name):
    qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image()
    path = root+'qrcodes/'+name+'.png'
    img.save(root+'qrcodes/'+name+'.png')
    return path

def mkChapter(b):
    #print b.attributes()
    filter('zones', '"name" = '+str(b.attributes()[0])+'' )
    filter('zones2', '"name" = '+str(b.attributes()[0])+'' )
    filter('divisions', '"name" = "'+str(b.attributes()[0])+'"' )
    filter('divisions2', '"name" = "'+str(b.attributes()[0])+'"' )

    #cuidado que aqu´i se lia con valor integer o string
    zz = Lz.getFeatures(QgsFeatureRequest(QgsExpression('"name" = '+str(b.attributes()[0])+'')))
    zz = [x for x in zz]
    filter('districtes', '"c_distri" = "'+str(zz[0].attributes()[2])+'"' )

    #coje la geometria del distriro
    distri = QgsMapLayerRegistry.instance().mapLayer(mapL['districtes'])
    gd= [d for d in distri.getFeatures()][0]

    canvas = QgsMapCanvas()
    template_path = root+qptChapter

    template_file = file(template_path)
    template_content = template_file.read()
    template_file.close()
    document = QDomDocument()
    document.setContent(template_content)
    #ms = canvas.mapSettings()
    ms=iface.mapCanvas().mapRenderer()
    #ms.setLayerSet(QgsMapLayerRegistry.instance().mapLayers().keys())
    composition = QgsComposition(ms)
    composition.loadFromTemplate(document, {})

    ##
    map_item = composition.getComposerItemById('mapa')
    map_item.setMapCanvas(canvas)
    #map_item.setRotation(-b.attributes()[1])########
    bounds = (b.geometry()).boundingBox()
    map_item.zoomToExtent(bounds)

    ##
    map_item_distri = composition.getComposerItemById('mapDistrito')
    map_item_distri.setMapCanvas(canvas)
    map_item_distri.zoomToExtent(gd.geometry().boundingBox())

    ##zona
    zo = composition.getComposerItemById('zona')
    zo.setText(str(b.attributes()[0]))

    ##barrio y distrito
    distrito = composition.getComposerItemById('distrito')
    distrito.setText(zz[0].attributes()[3]+' | '+zz[0].attributes()[2])
    barrio = composition.getComposerItemById('barrio')
    barrio.setText(zz[0].attributes()[4]+' | '+zz[0].attributes()[5])

    composition.refreshItems()
    composition.exportAsPDF(root+'output/'+str(b.attributes()[0]).zfill(4)+'.pdf')

    #filter('zones', '"name" = ""' )
    filter('divisions', '' )
    filter('divisions2', '' )
    filter('districtes', '' )
    return


def mkDiv(b,  z):
    angle = b.attributes()[1]
    #esto visulamente es correcto
    ##pero me fastidia la lectira posterior porque no dejo rastro de esta manipulacion
    ##para el escaneo posterio deberia de modificar el orden de los bounds en el qr y en el pie de pagina
    if angle > 45:
        angle = angle-90
    elif angle < -45:
        angle = angle+90

    sql = '"name" = "'+str(b.attributes()[0])+'"'
    sql += ' AND "x" = '+str(b.attributes()[2])#.rstrip('L')
    sql += ' AND "y" = '+str(b.attributes()[3])#.rstrip('L')

    filter('divisions', sql)

    canvas = QgsMapCanvas()
    template_path = root+qptDivision
    template_file = file(template_path)
    template_content = template_file.read()
    template_file.close()
    document = QDomDocument()
    document.setContent(template_content)
    #ms = canvas.mapSettings()
    ms=iface.mapCanvas().mapRenderer()
    #ms.setLayerSet(QgsMapLayerRegistry.instance().mapLayers().keys())
    composition = QgsComposition(ms)
    composition.loadFromTemplate(document, {})

    ##mapa principal
    map_item = composition.getComposerItemById('mapa')
    map_item.setMapCanvas(canvas)
    #map_item.setRotation(-b.attributes()[1]-90)########
    map_item.setRotation(-angle)########
    cc = b.geometry().centroid().asPoint()
    coordsDesc = str(b.geometry().exportToWkt())[10:][:-2].split(', ')
    #print coordsDesc
    #b.geometry().rotate(-b.attributes()[1]-90, cc)###################################################

    b.geometry().rotate(-angle, cc)
    #print angle
    #print str(b.geometry().exportToWkt())[10:][:-2].split(', ')
    ##print b.geometry().exportToWkt()
    ##print b.geometry().asPolygon()

    rBound = b.geometry().boundingBox()
    map_item.zoomToExtent(rBound)
    #print str(rBound.geometry().exportToWkt())[10:][:-2].split(', ')

    ##mapa 2
    map_item2 = composition.getComposerItemById('minimapa')
    #cuidado que aqu´i se lia con valor integer o string
    zz = Lz.getFeatures(QgsFeatureRequest(QgsExpression('"name" = '+str(b.attributes()[0])+'')))
    zz = [x for x in zz]
    z = zz[0].geometry()
    map_item2.zoomToExtent(z.boundingBox())
    map_item2.setMapCanvas(canvas)


    ##barrio y distrito
    distrito = composition.getComposerItemById('distrito')
    distrito.setText(zz[0].attributes()[3]+' | '+zz[0].attributes()[2])
    barrio = composition.getComposerItemById('barrio')
    barrio.setText(zz[0].attributes()[4]+' | '+zz[0].attributes()[5])

    ##anotacion coordenadas
    #coordsDesc = str(b.geometry().exportToWkt())[10:][:-2].split(', ')
    coordsDesc = [c.split(' ') for c in coordsDesc]
    #print coordsDesc

    coords = composition.getComposerItemById('coordenadas')
    coords.setText(' aX: '+str(round(float(coordsDesc[0][0]),0))+ \
                   ' ay: '+str(round(float(coordsDesc[0][1]),0))+ \
                   ' bX: '+str(round(float(coordsDesc[1][0]),0))+ \
                   ' by: '+str(round(float(coordsDesc[1][1]),0))+ \
                   ' cX: '+str(round(float(coordsDesc[2][0]),0))+ \
                   ' cy: '+str(round(float(coordsDesc[2][1]),0))+ \
                   ' dX: '+str(round(float(coordsDesc[3][0]),0))+ \
                   ' dy: '+str(round(float(coordsDesc[3][1]),0))
                   )

    ##zona
    zo = composition.getComposerItemById('zona')
    zo.setText(str(b.attributes()[0]))

    ##cbarres
    cbarres = composition.getComposerItemById('cbarres')
    #cbarres.setText(str(b.attributes()[0])+','+str(b.attributes()[1])+','+str(b.attributes()[2]))
    cbarres.setText('*'+str(b.attributes()[0])+','+str(b.attributes()[2])+','+str(b.attributes()[3])+'*')
    print ('*'+str(b.attributes()[0])+','+str(b.attributes()[2])+','+str(b.attributes()[3])+'*')
    #print str(b.attributes()[0])+','+str(b.attributes()[2])+' '+str(b.attributes()[3])

    #qrcode
    name = str(b.attributes()[0])+'_'+str(b.attributes()[2])+'_'+str(b.attributes()[3])
    qr = composition.getComposerItemById('qrcode')
    data =  name+' '+ \
            str(round(float(coordsDesc[0][0]),3))+' '+ \
            str(round(float(coordsDesc[0][1]),3))+', '+ \
            str(round(float(coordsDesc[1][0]),3))+' '+ \
            str(round(float(coordsDesc[1][1]),3))+', '+ \
            str(round(float(coordsDesc[2][0]),3))+' '+ \
            str(round(float(coordsDesc[2][1]),3))+', '+ \
            str(round(float(coordsDesc[3][0]),3))+' '+ \
            str(round(float(coordsDesc[3][1]),3))

    qrpath = makeQR(data,name)
    qr.setPicturePath(qrpath)

    #pagina
    pagina = composition.getComposerItemById('pagina')
    pagina.setText(name)

    #norte
    norte = composition.getComposerItemById('norte')
    norte.setRotation(angle)

    composition.refreshItems()
    composition.exportAsPDF(root+'output/'+str(b.attributes()[0]).zfill(4)+'_'+str(b.id()).zfill(4)+'.pdf')

    return

def mkForm(b):
    name = str(b.attributes()[0])+'_'+str(b.attributes()[2])+'_'+str(b.attributes()[3])

    ## genera una hoja
    canvas = QgsMapCanvas()
    template_path = root+qptForm
    template_file = file(template_path)
    template_content = template_file.read()
    template_file.close()
    document = QDomDocument()
    document.setContent(template_content)
    #ms = canvas.mapSettings()
    ms=iface.mapCanvas().mapRenderer()
    #ms.setLayerSet(QgsMapLayerRegistry.instance().mapLayers().keys())
    composition = QgsComposition(ms)
    composition.loadFromTemplate(document, {})

    ##zona
    zo = composition.getComposerItemById('zona')
    zo.setText(str(b.attributes()[0]))

    ##pagina
    zo = composition.getComposerItemById('pagina')
    zo.setText(name)

    #qrcode
    qr = composition.getComposerItemById('qrcode')
    data =  name
    qrpath = makeQR(data,name)
    qr.setPicturePath(qrpath)

    ##cbarres
    cbarres = composition.getComposerItemById('cbarres')
    cbarres.setText('*'+str(b.attributes()[0])+','+str(b.attributes()[2])+','+str(b.attributes()[3])+'*')

    ##guarda
    composition.refreshItems()
    composition.exportAsPDF(root+'output/'+str(b.attributes()[0]).zfill(4)+'_'+str(b.id()).zfill(4)+'_form.pdf')

    return

###########################################################################
###########################################################################
###########################################################################
###########################################################################

reg = QgsMapLayerRegistry.instance()
for l in reg.mapLayers().values():
    print l.id()

mapL=mapL()

Lz = QgsMapLayerRegistry.instance().mapLayer(mapL['zones'])
Lb = QgsMapLayerRegistry.instance().mapLayer(mapL['bounds'])
Ld = QgsMapLayerRegistry.instance().mapLayer(mapL['divisions'])

###########################################################################

#print (z.name() for z in Lz.fields())

x=0
for b in Lb.getFeatures():
    if x>99 and x < 2000: #para provocar una salida rapida , dejar 2000

        mkChapter(b)

        exp = QgsExpression('name = '+str(b.attributes()[0]))
        z = b.geometry()
        request = QgsFeatureRequest(exp)

        for d in Ld.getFeatures(request):
            #print d.attributes()
            print '.',
            ## lanza division
            mkDiv(d, z)
            mkForm(d)


        print '------------', b.id(),x
    x+=1
print 'fi'

