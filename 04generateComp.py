#!/usr/bin/python
# -*- coding: utf-8 -*-
from qgis.core import QgsProject
from PyQt4.QtCore import QFileInfo, QPointF
from qgis.utils import iface
from qgis.gui import QgsMapCanvas
from PyQt4.QtXml import QDomDocument
from PyQt4.QtGui import QPainter, QImage
from PyQt4.QtCore import QSizeF, QSize, QRect, QRectF
import json
import qrcode

#root = '/media/pablueke/DADES/_encargos/15013 arrels/_reus/'
#root = '/home/pablo/Documents/_sync/17037 arrels_reus/project_reus/'

#root = '/media/pablueke/CE0A39130A38FA53/_sync/17037 arrels_reus/project_mataro/'
#project = u'Recompte Mataró 2017'

#root = '/media/pablueke/CE0A39130A38FA53/_sync/17037 arrels_reus/project_tarragona/'
#project = u'Recompte Tarragona 2017'

root = '/media/pablueke/CE0A39130A38FA53/_sync/17037 arrels_reus/project_barcelona/'
root= '/mnt/data/_sync/17037 arrels/project_barcelona/'

project = u'Cens Barcelona 2018'

layers={
   'zones':('zones/zones.sqlite', 'elements', 'geometry'),
   'zones2':('zones/zones.sqlite', 'elements', 'geometry'),
   'bounds' : ('bounds/bounds.sqlite', 'elements', 'geometry') ,
   'divisions' : ('bounds/bounds.sqlite', 'elementsdiv', 'geometry'),
   'divisions2' : ('bounds/bounds.sqlite', 'elementsdiv', 'geometry'),
   'districtes' : ('zones/districtes.sqlite', 'elements', 'geometry')
   }

qptChapter  = 'arrelsAtlas_chapter.qpt'
qptDivision = 'arrelsAtlas_division.qpt'
qptForm     = 'arrelsAtlas_form.qpt'

###############################################################################
###############################################################################

def printRaster(composition, nameFile):
    global pag
    dpi = composition.printResolution()
    dpmm = dpi / 25.4
    dpmm = dpi / 50
    width = int(dpmm * composition.paperWidth())
    height = int(dpmm * composition.paperHeight())

    # create output image and initialize it
    image = QImage(QSize(width, height), QImage.Format_ARGB32)
    image.setDotsPerMeterX(dpmm * 1000)
    image.setDotsPerMeterY(dpmm * 1000)
    image.fill(0)

    # render the composition
    imagePainter = QPainter(image)
    #sourceArea = QRectF(0, 0, composition.paperWidth(), composition.paperHeight())
    #targetArea = QRectF(0, 0, width, height)
    composition.renderPage(imagePainter,0)
    #composition.render(imagePainter, targetArea, sourceArea)
    imagePainter.end()

    image.save(root+'out/'+str(pag).zfill(3)+'_'+nameFile+'.png', "png")
    pag += 1
    return


def saveProject(name):
    project = QgsProject.instance()
    project.write(QFileInfo(root+name+'.qgs'))
    return


def filter(layerName, criteria):
    desc=layers[layerName]
    l=QgsMapLayerRegistry.instance().mapLayer(mapL[layerName])
    l.setSubsetString(criteria)
    return


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


def featureFields(b):
    result =[a.name() for a in b.fields()]
    return result


def mkChapter(b):
    """
    b es un bound
    """

    filter('zones', '"name" = \''+b.attribute('name')+'\'' )#cuidado si el valor es integer o string
    filter('zones2', '"name" = \''+b.attribute('name')+'\'' )#cuidado si el valor es integer o string
    filter('divisions', '"name" = \''+b.attribute('name')+'\'' )
    filter('divisions2', '"name" = \''+b.attribute('name')+'\'' )

    # seleccionamos la zona
    zz = Lz.getFeatures(QgsFeatureRequest(QgsExpression('"name" = \''+b.attribute('name')+'\''))) #cuidado si el valor es integer o string
    zz = [x for x in zz]

    # escogemos el distrito correspondiente a la zona
    #print zz[0].attribute('d_name')
    filter('districtes', '"name" = \''+unicode(zz[0].attribute('d_name'))+'\'' )
    #print '"name" = \''+unicode(zz[0].attribute('d_name'))+'\''

    global currentDistrict
    currentDistrict = unicode(zz[0].attribute('d_id'))
    #coje la geometria del distriro
    distri = QgsMapLayerRegistry.instance().mapLayer(mapL['districtes'])
    gd= [d for d in distri.getFeatures()][0]

    canvas = QgsMapCanvas()
    ## leer los templates al inicio y cargarlos como variables
    document = QDomDocument()
    document.setContent(template_content_chapter)
    #ms = canvas.mapSettings()

    ms=iface.mapCanvas().mapRenderer()
    #ms.setLayerSet(QgsMapLayerRegistry.instance().mapLayers().keys())

    composition = QgsComposition(ms)
    composition.loadFromTemplate(document, {})

    ##
    map_item = composition.getComposerItemById('mapa')
    map_item.setMapCanvas(canvas)

    ## map_item.setRotation(-b.attributes()[1])########
    bounds = (b.geometry()).boundingBox()
    map_item.zoomToExtent(bounds)

    layerSet = QgsProject.instance().visibilityPresetCollection().presetVisibleLayers(u'chapter_big')
    map_item.setLayerSet (layerSet)

    ##
    map_item_distri = composition.getComposerItemById('mapDistrito')
    map_item_distri.setMapCanvas(canvas)
    map_item_distri.zoomToExtent(gd.geometry().boundingBox())

    layerSet = QgsProject.instance().visibilityPresetCollection().presetVisibleLayers(u'chapter_small')
    map_item_distri.setLayerSet(layerSet)

    ##title
    ti = composition.getComposerItemById('project')
    ti.setText(project)

    ##zona
    zo = composition.getComposerItemById('zona')
    zo.setText(str(b.attribute('id')))

    ##barrio y distrito
    distrito = composition.getComposerItemById('distrito')
    #distrito.setText(unicode(zz[0].attribute('name'))+' | '+unicode(zz[0].attribute('d_name')))
    distrito.setText('districte : '+ unicode(zz[0].attribute('d_name')))
    print zz[0].attributes()
    barrio = composition.getComposerItemById('barrio')
    #barrio.setText(zz[0].attribute('name'))#+' | '+str(zz[0].attributes()[4])) #ojo!
    fields = [e.name() for e in zz[0].fields().toList()]
    if 'b_name' in fields:
        barrio.setText('barri : '+zz[0].attribute('b_name'))
    else:
        barrio.setText('barri : '+zz[0].attribute('name'))

    composition.refreshItems()

    #print b.attributes()

    #print [a.name() for a in b.fields()]

    image_name = str(b.attribute('id'))+'_'+currentDistrict

    #composition.exportAsPDF(image_name+'.pdf')
    #print 'save : ',image_name+'.png'
    #image = composition.printPageAsRaster(0)
    #image.save(image_name+'.png','png')

    printRaster(composition, image_name)

    ##filter('zones', '"name" = ""' )
    filter('divisions', '' )
    filter('divisions2', '' )
    filter('districtes', '' )
    return


def mkDiv(b,  z):

    angle = b.attribute('ang')
    #esto visulamente es correcto
    ##pero me fastidia la lectira posterior porque no dejo rastro de esta manipulacion
    ##para el escaneo posterio deberia de modificar el orden de los bounds en el qr y en el pie de pagina
    if angle > 45:
        angle = angle-90
    elif angle < -45:
        angle = angle+90

    sql = '"name" = \''+b.attribute('name')+'\''
    sql += ' AND "x" = '+str(b.attribute('x'))
    sql += ' AND "y" = '+str(b.attribute('y'))

    filter('divisions', sql)
    sql2='"name" = \''+b.attribute('name')+'\''
    filter('divisions2', sql2)

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

    layerSet = QgsProject.instance().visibilityPresetCollection().presetVisibleLayers(u'division_big')
    map_item.setLayerSet(layerSet)
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
    layerSet = QgsProject.instance().visibilityPresetCollection().presetVisibleLayers(u'division_small')
    map_item2.setLayerSet(layerSet)

    #cuidado que aqu´i se lia con valor integer o string
    zz = Lz.getFeatures(QgsFeatureRequest(QgsExpression('"name" = \''+b.attribute('name')+'\'')))
    zz = [x for x in zz]
    z = zz[0].geometry()
    map_item2.zoomToExtent(z.boundingBox())
    map_item2.setMapCanvas(canvas)

    ##barrio y distrito
    distrito = composition.getComposerItemById('distrito')
    #distrito.setText(zz[0].attribute('name')+' | '+unicode(zz[0].attribute('d_name')))
    distrito.setText('districte : '+unicode(zz[0].attribute('d_name')))

    barrio = composition.getComposerItemById('barrio')

    fields = [e.name() for e in zz[0].fields().toList()]
    if 'b_name' in fields:
        barrio.setText('barri : '+zz[0].attribute('b_name'))
    else:
        barrio.setText('barri : '+zz[0].attribute('name'))

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
    zo.setText(str(b.attribute('id')))

    ##cbarres
    cbarres = composition.getComposerItemById('cbarres')
    #cbarres.setText(str(b.attributes()[0])+','+str(b.attributes()[1])+','+str(b.attributes()[2]))
    ##+en la division incorporar tamben el id de la zona
    cbarres.setText('*'+str(b.attribute('id'))+','+str(b.attribute('x'))+','+str(b.attribute('y'))+'*')
    #print str(b.attributes()[0])+','+str(b.attributes()[2])+' '+str(b.attributes()[3])

    #qrcode
    name = str(b.attribute('id'))+'_'+str(b.attribute('x'))+'_'+str(b.attribute('y'))

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

    image_name = str(b.attribute('id'))+'_'+str(b.id())+'_'+currentDistrict
    #composition.exportAsPDF(image_name+'.pdf')
    #image = composition.printPageAsRaster(0)
    #image.save(image_name+'.png','png')

    printRaster(composition, image_name)

    return

def mkForm(b):
    print b.attributes()
    #name = b.attribute('name')+'_'+str(b.attribute('x'))+'_'+str(b.attribute('y'))
    name = str(b.attribute('id'))+'_'+str(b.attribute('x'))+'_'+str(b.attribute('y'))
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

    ##title
    ti = composition.getComposerItemById('project')
    ti.setText(project)

    ##zona
    zo = composition.getComposerItemById('zona')
    zo.setText(str(b.attribute('id')))

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
    cbarres.setText('*'+str(b.attribute('id'))+','+str(b.attribute('x'))+','+str(b.attribute('y'))+'*')

    #print ('*'+b.attribute('name')+','+str(b.attribute('x'))+','+str(b.attribute('y'))+'*')
    ##guarda
    composition.refreshItems()
    image_name = str(b.attribute('id'))+'_'+str(b.id())+'_form'+'_'+currentDistrict
    #composition.exportAsPDF(image_name+'.pdf')
    #image = composition.printPageAsRaster(0)
    #image.save(image_name+'.png','png')

    printRaster(composition, image_name)
    return


def showLayers():
    reg = QgsMapLayerRegistry.instance()
    for l in reg.mapLayers().values():
        print l.id()
    return


###########################################################################
###########################################################################

template_path = root+qptChapter
template_file = file(template_path)
template_content_chapter = template_file.read()
template_file.close()

mapL=mapL()

Lz = QgsMapLayerRegistry.instance().mapLayer(mapL['zones'])
Lb = QgsMapLayerRegistry.instance().mapLayer(mapL['bounds'])
Ld = QgsMapLayerRegistry.instance().mapLayer(mapL['divisions'])

#print Lb.attributeList()
#print Lb.attributeDisplayName(1)

Lzf = [a.name() for a in Lz.pendingFields()]
Lbf = [a.name() for a in Lb.pendingFields()]
Ldf = [a.name() for a in Ld.pendingFields()]

###########################################################################

#print (z.name() for z in Lz.fields())
currentDistrict = ''
x=0
pag=1
for b in Lb.getFeatures():
    print '>>>> chapter: ',
    print b.attributes()
    if x>=0 and x < 10000000:  #and b.attributes()[0] > 324: #para provocar una salida rapida , dejar 2000
        mkChapter(b)
        exp = QgsExpression('name = \''+b.attribute('name')+'\'')
        z = b.geometry()
        request = QgsFeatureRequest(exp)
        for d in Ld.getFeatures(request):
            print '>>>> division: ',
            print d.attributes()
            mkDiv(d, z)
            #mkForm(d)
            #print None+'i'
    x+=1

print 'fi'

