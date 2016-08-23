# -*- coding: utf-8 -*-
'''
https://github.com/primetang/qrtools
sudo apt-get install libzbar-dev

[sudo] pip install pypng
[sudo] pip install zbar
[sudo] pip install pillow
[sudo] pip install qrtools


-------------------


http://www.gdal.org/gdalwarp.html
http://www.gdal.org/gdal_translate.html

'''

import math
import pyqrcode
import cv2
import numpy as np
import qrtools
import sys
import os
import zbar
import ezodf
import sqlite3
import pyspatialite.dbapi2 as pysp
import scipy.misc
import scipy.signal

imageDebug = True
scanFolder = 'scan/'
zones = '../bases/zones.sqlite' ## table zones
subzones = '../data/bounds.sqlite' ## table elemenst div
ods = 'results/results.ods'

# marker image for page one
PAGE_MARKER = 'img/la4.png'
# size of virtual page
# pix que debria hacer la zona correctamente escaneada
PAGE_SIZE = (775, 1131) ##
PAGE_SIZE = (1550, 2262) ##
# color to check if black
# values less than the color threshold is considered black
COLOR_THRESHOLD = 50
# size of circles to check for
CIRC_SIZE = (32, 32)
# distance between four points when checking inside the circle
DIST_X, DIST_Y = map(lambda x: x * (3.0 / 8.0), CIRC_SIZE)


##detectar els triangles
def detect(imatge,objecte,restriccio):
    """requereix haver importat numpy as np.
    El tamany de l'objecte sempre ha de ser mes petit que la imatge.
    restriccio ha de ser un numero entre 0-255 , com més alt més exigeixes que s'assemblin.
    """

    TF = np.fft.fftn
    TFs = np.fft.fftshift
    iTF = np.fft.ifftn
    iTFs = np.fft.ifftshift

    tamany_i = np.shape(imatge)
    tamany_o = np.shape(objecte)

    triangle = np.zeros((tamany_i))
    triangle[0:tamany_o[0],0:tamany_o[1]] = objecte[:,:]

    TFimatge = TFs(TF(imatge))
    TFtriangle = TFs(TF(triangle))
    arg = TFimatge*np.conj(TFtriangle)/np.abs(TFtriangle)

    corrp = np.abs(iTF(iTFs(arg)))
    corrp = np.uint8(255*(corrp/(np.max(corrp) if np.max(corrp) != 0 else 1 )))

    mask = np.double(corrp>restriccio)
    bins = corrp*mask

    TFbins = TFs(TF(bins))
    res = np.abs(iTF(iTFs(TFbins*TFtriangle)))
    return np.abs(res)

def find_corners(im,quadrat=150,maxim=20):
    """150 es valid per a una imatge de 3507x2480 """

    a=im[:quadrat,:quadrat]
    b=im[:quadrat,-quadrat:]
    c=im[-quadrat:,:quadrat]
    d=im[-quadrat:,-quadrat:]

    for ax in range(np.shape(a)[1]):
        sumx=np.sum(a[:,ax])
        if sumx>maxim :
            break

    for ay in range(np.shape(a)[0]):
        sumy=np.sum(a[ay,:])
        if sumy>maxim :
            break

    for bx in range(np.shape(b)[1]):
        sumx = np.sum(b[:, np.shape(b)[1]-1-bx])
        if sumx > maxim:
            break
    bx=np.shape(im)[1]-bx

    for by in range(np.shape(b)[0]):
        sumy = np.sum(b[by, :])
        if sumy > maxim:
            break


    for cx in range(np.shape(c)[1]):
        sumx = np.sum(c[:, cx])
        if sumx > maxim:
            break

    for cy in range(np.shape(c)[0]):
        sumy = np.sum(c[np.shape(c)[1]-1-cy, :])
        if sumy > maxim:
            break
    cy=np.shape(im)[0]-cy


    for dx in range(np.shape(d)[1]):
        sumx = np.sum(d[:, np.shape(d)[1]-1-dx])
        if sumx > maxim:
            break
    dx=np.shape(im)[1]-dx

    for dy in range(np.shape(d)[0]):
        sumy = np.sum(d[np.shape(d)[1]-1-dy, :])
        if sumy > maxim:
            break
    dy=np.shape(im)[0]-dy

    return (ax,ay),(bx,by),(cx,cy),(dx,dy)


##contraste
def otsu(img):
    """
    Threshold image using otsu algorithm
    returns modified image object
    """
    ##modificar el blur segun la resolucion de escaneo
    blur = cv2.GaussianBlur(img,(1,1),0)
    ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return th3

def thresholding(img):
    """
    Threshold image using adaptive gaussian algorithm
    returns modified image object
    """
    ret,th1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    return th1
    return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)

def show_img(img, window='image'):
    """
    Show image file in a window
    """
    cv2.imshow(window, img)
    cv2.waitKey(0)

def save_img(img, name, folder=''):
    """
    save image object to file
    """
    if imageDebug == False:
        return
    if folder == '':
        cv2.imwrite('process/'+name,img)
    else:
        cv2.imwrite(folder+name,img)
    return

def isPixel(img, x, y):
    """
    check if pixel is black
    """
    isPixel = img.item(y, x) < COLOR_THRESHOLD
    return isPixel

def distance(x1, y1, x2, y2):
    """
    retrieve distance between two points
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def isFilled(img, coors):
    """
    count filled pixels
    """
    lenf =0
    coor1 = coors[0]
    coor4 = coors[3]
    for x in range(coor1[0], coor4[0]):
        for y in range(coor1[1], coor4[1]):
            isP = isPixel(img, x, y)
            #print x, y, isP
            lenf += 1 if isP == True else 0

    return lenf

def rotate_180(img):
    rows,cols = img.shape
    M = cv2.getRotationMatrix2D((cols/2, rows/2),180,1)
    dst = cv2.warpAffine(img,M,(cols, rows))

    return dst

def scale(img):
    height, width = img.shape[:2]
    res = cv2.resize(img,(2*width, 2*height), interpolation = cv2.INTER_CUBIC)
    return

def qrdecode(img):
    qr = qrtools.QR()
    qr.decode(img)
    return qr.data

def cbardecode(img):
    return

def getZone(zona):
    sql = """SELECT aswkt("GEOMETRY") FROM  "zones" where name like  %s """ %(zona)
    conn = pysp.connect('../bases/zones.sqlite')
    c = conn.cursor()
    c.execute(sql)
    result = c.fetchone()
    conn.close()
    ##todo solucionar incidencia no hi ha geom

    return result[0]

def addcoords(img, coords):
    '''

    '''
    #img = cv2.imread(fname)
    page =coords.split(' ')[0]
    h, w = img.shape[:2]
    h=str(h)
    w=str(w)
    print coords
    name , nx, ny= page.split('_')
    conn = sqlite3.connect(subzones)
    c = conn.cursor()
    sql='''select ang from elementsdiv where name = '%s' and x like %s and y like %s ''' %(name, nx, ny)
    print sql
    c.execute(sql)
    ang = float(c.fetchall()[0][0])
    if ang<=45 and ang>=-45:
        c1X = str(coords.split(' ')[1].strip(','))
        c1Y = str(coords.split(' ')[2].strip(','))
        c2X = str(coords.split(' ')[3].strip(','))
        c2Y = str(coords.split(' ')[4].strip(','))
        c3X = str(coords.split(' ')[5].strip(','))
        c3Y = str(coords.split(' ')[6].strip(','))
        c4X = str(coords.split(' ')[7].strip(','))
        c4Y = str(coords.split(' ')[8].strip(','))
    elif ang>45:
        c1X = str(coords.split(' ')[3].strip(','))
        c1Y = str(coords.split(' ')[4].strip(','))
        c2X = str(coords.split(' ')[5].strip(','))
        c2Y = str(coords.split(' ')[6].strip(','))
        c3X = str(coords.split(' ')[7].strip(','))
        c3Y = str(coords.split(' ')[8].strip(','))
        c4X = str(coords.split(' ')[1].strip(','))
        c4Y = str(coords.split(' ')[2].strip(','))
    elif ang<-45:
        c1X = str(coords.split(' ')[7].strip(','))
        c1Y = str(coords.split(' ')[8].strip(','))
        c2X = str(coords.split(' ')[1].strip(','))
        c2Y = str(coords.split(' ')[2].strip(','))
        c3X = str(coords.split(' ')[3].strip(','))
        c3Y = str(coords.split(' ')[4].strip(','))
        c4X = str(coords.split(' ')[5].strip(','))
        c4Y = str(coords.split(' ')[6].strip(','))

    #dependiendo de la posicion del norte hay que componer las coordenadas de
    #forma distinta

    gcp2 = ' -gcp 0 '+h+' '+c4X + ' '+c4Y
    gcp3 = ' -gcp '+w+' '+h +' '+ c1X+' '+c1Y
    gcp4 = ' -gcp '+w+' 0 '+ c2X + ' ' + c2Y
    gcp1 = ' -gcp 0 0 '+ c3X+ ' '+c3Y

    src_dataset = ' tiles/_'+page+'.png'
    dst_dataset = ' tiles/_'+page+'.tiff'
    of = '-of GTiff '
    a_srs = '-a_srs EPSG:25831 '

    ogrR  = 'gdal_translate '
    ogrR += of #+a_srs
    ogrR +=   gcp2 + gcp3 + gcp4 + gcp1
    ogrR += src_dataset
    ogrR += dst_dataset
    ##print ogrR
    os.system(ogrR)

    #####################################
    zone = getZone(coords.split(' ')[0].split('_')[0])
    f = open('wkt.csv', 'wt')
    f.write('WKT,\n')
    f.write(str('"'+zone+'"'))
    f.close()
    ogrR ="gdalwarp tiles/_" + page + ".tiff"
    ogrR+= " tiles/" + page + ".tiff"
    ogrR+= " -cutline wkt.csv -dstalpha"
    os.system(ogrR)

    ####################################


    #ogrR = 'gdalwarp -r cubic -order 1 -overwrite -co COMPRESS=LZW -dstalpha'
    #ogrR += " tiles/_"+page+".tiff"
    #ogrR += " tiles/"+page+".tiff"

    #os.system(ogrR)

    return

#lee la imagen y recorta
def retrieve_relevant_area(fname,zonaq=(141,150,160,170),restriccio1=240,restriccio2=150):
    """
    Retrieve relevant exam area from image
    """
    img = cv2.imread(fname)  ##(3543, 2556, 3)

    img_size = img.shape[:2][::-1] ##(2556, 3543)
    gray = cv2.imread(fname, 0)
    thresh = otsu(gray)
    save_img(thresh, '01_otsu.png')

    imUL = cv2.imread('/home/pablo/_projectes/arrels_enric/img/UL.jpg', 0)
    imDL = cv2.imread('/home/pablo/_projectes/arrels_enric/img/DL.jpg', 0)
    imUR = cv2.imread('/home/pablo/_projectes/arrels_enric/img/UR.jpg', 0)
    imDR = cv2.imread('/home/pablo/_projectes/arrels_enric/img/DR.jpg', 0)

    # intreressa tenir la mateixa mida
    img = scipy.misc.imresize(img, (3507, 2480))
    gray = scipy.misc.imresize(gray, (3507, 2480))
    thresh = scipy.misc.imresize(thresh,(3507, 2480))

    # el tamany dels triangles amb els que volem detectar interessa.
    # Si son més grans no detectarem els petits i si són molt petits detectarem coses no desitjades
    imUL = scipy.misc.imresize(imUL, (110, 110))
    imDL = scipy.misc.imresize(imDL, (110, 110))
    imUR = scipy.misc.imresize(imUR, (110, 110))
    imDR = scipy.misc.imresize(imDR, (110, 110))

    # binaritzem, i en el cas de la imatge invertim el color
    gray = np.double(np.double(gray) / np.max(gray) > 0.7)
    gray = np.uint8(np.abs(gray - 1))

    imUL = np.uint8(np.double(np.double(imUL) / np.max(imUL) > 0.7))

    imDL = np.uint8(np.double(np.double(imDL) / np.max(imDL) > 0.7))

    imUR = np.uint8(np.double(np.double(imUR) / np.max(imUR) > 0.7))

    imDR = np.uint8(np.double(np.double(imDR) / np.max(imDR) > 0.7))

    imtotal = np.zeros(np.shape(gray))
    imtotal2 = np.zeros(np.shape(gray))

    # iterem per diversos tamanys per assegurar que detectem les cantonades

    # for quadrat in (110,120,130, 140, 150, 160):
    for quadrat in zonaq:
        # cantons=quatre_cantonades(im,retall)
        a = gray[:quadrat, :quadrat]
        b = gray[:quadrat, -quadrat:]
        c = gray[-quadrat:, :quadrat]
        d = gray[-quadrat:, -quadrat:]
        # a = scipy.signal.medfilt(a)
        # b = scipy.signal.medfilt(b)
        # c = scipy.signal.medfilt(c)
        # d = scipy.signal.medfilt(d)

        triangleUL = detect(a, imUL, restriccio1)
        triangleUL = np.uint8(np.double((np.double(triangleUL) / (np.max(triangleUL) if np.max(triangleUL) != 0 else 1)) > 0.7))

        triangleUR = detect(b, imUR, restriccio1)
        triangleUR = np.uint8(np.double((np.double(triangleUR) / (np.max(triangleUR) if np.max(triangleUR) != 0 else 1)) > 0.7))

        triangleDL = detect(c, imDL, restriccio1)
        triangleDL = np.uint8(np.double((np.double(triangleDL) / (np.max(triangleDL) if np.max(triangleDL) != 0 else 1)) > 0.7))

        triangleDR = detect(d, imDR, restriccio1)
        triangleDR = np.uint8(np.double((np.double(triangleDR) / (np.max(triangleDR) if np.max(triangleDR) != 0 else 1)) > 0.7))
        imtotal[:quadrat, :quadrat] = triangleUL
        imtotal[:quadrat, -quadrat:] = triangleUR
        imtotal[-quadrat:, :quadrat] = triangleDL
        imtotal[-quadrat:, -quadrat:] = triangleDR

        imtotal = np.uint8(np.double(imtotal) / (np.max(imtotal) if np.max(imtotal) != 0 else 1))
        imtotal2 = imtotal + imtotal2


    imtotal2 = np.uint8(np.double(imtotal2 >= 1))

    top_left, top_right, bottom_left, bottom_right = find_corners(imtotal2, maxim=10,quadrat=restriccio2)

    # draw page border
    #cv2.rectangle(img, top_left, bottom_right, (0,255,0), 10)
    cv2.line(img, top_left, top_right,(255,0,255),5)
    cv2.line(img, bottom_right, top_right,(0, 255,255),5)
    cv2.line(img, bottom_left, bottom_right,(255,255,0),5)
    cv2.line(img, top_left, bottom_left,(255,0,0),5)
    save_img(img, '10_contours.png')


    # skew perspective to corners
    pts1 = np.float32([top_left, top_right, bottom_left, bottom_right])
    pts2 = np.float32([[0,0],[PAGE_SIZE[0],0],[0,PAGE_SIZE[1]],PAGE_SIZE])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    img = cv2.warpPerspective(thresh, M, PAGE_SIZE)


    save_img(img, '20_trimmed.png')

    ###########################################################################
    ###########################################################################
    # check if page one or two
    # find marker on page
    template = cv2.imread(PAGE_MARKER,0)
    w, h = template.shape[::-1]
    ##busca la posicion en la pagina (deben tener el mismo tamaño)
    res = cv2.matchTemplate(img, rotate_180(template), cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = min_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    ###########################################################################
    ##aqui detectamos si la hoja esta girada
    if top_left[1]>PAGE_SIZE[1]/2:
        img = rotate_180(img)
        #volvemos a buscar la posicion correcta del template
        res = cv2.matchTemplate(img, template, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = min_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

    img_crop = img[top_left[1]:(top_left[1] + h), top_left[0]:(top_left[0] + w) ]
    #el testigo de lo que hemos encontrado (no cal ya)
    save_img(img_crop, '30_crop.png')
    # para debug
    cv2.rectangle(img,top_left, bottom_right, 128, 10)

    ###########################################################################
    ###########################################################################
    # check position of marker to determine if page one or two
    if_division = (100, 312)
    if_chapter = (447, 700)
    if_form = (700, 970)
    print top_left, bottom_right, PAGE_SIZE
    is_division = (top_left[0] < 100 and bottom_right[0] < 312 )
    is_chapter =  (top_left[0] > 447 and bottom_right[0] < 700 )
    is_form =     (top_left[0] > 700 and top_left[0] < 970 )
    result = -1
    if is_division == True:
        result = 0
    elif is_chapter == True:
        result = 1
    elif is_form == True:
        result = 2
    save_img(img, '40_find_image_type.png')
    return img, result

def read_division(img):
    qrt = img[422:692, 28:294]
    mapa = img[728:2220, 38:1508]
    cbar = img[268:331, 966:1509]
    #save_img(cbar, 'tiles/cbar.png')

    qrt=scipy.signal.medfilt(qrt)

    save_img(qrt, 'qr.png')

    bbox = qrdecode('process/qr.png')
    print bbox
    if bbox == None or bbox == 'NULL':
        return
    try:
        page = bbox.split(' ')[0].strip(',')
    except:
        return
    save_img(mapa, '_'+page+'.png', folder='tiles/')
    addcoords(mapa, bbox)
    return 'ok'

def getHeigherH(img,n):

    m = 8 #margin
    w, h = img.shape[::-1]
    val = -1
    cnt = 0 #num pixels fill#puedo poner algo porsiaca ruido 10 o 20
    for a in range(n):
        x = w/n*a
        xx = w/n*(a+1)
        ans = img[ : , x:xx ]
        wa, ha = ans.shape[::-1]

        coor1 = (int(m), int(m))
        coor2 = (int(m), int(ha-2*m))
        coor3 = (int(wa-m*2), int(m))
        coor4 = (int(wa-m*2), int(ha-m*2))
        #print a, wa, ha, [coor1, coor2, coor3, coor4]
        fillCnt = isFilled(ans, [coor1, coor2, coor3, coor4])
        #save_img(ans, 'celda.png')
        if fillCnt > cnt:
            save_img(ans, 'celda.png')
            cnt = fillCnt
            val = a
    print val,
    return val

def getHeigherV(img,n):
    m = 8 #margin
    w, h = img.shape[::-1]
    val = -1
    cnt = 0 #num pixels fill#puedo poner algo porsiaca ruido 10 o 20
    for a in range(n):
        y = h/n*a
        yy = h/n*(a+1)
        ans = img[ y:yy, : ]
        wa, ha = ans.shape[::-1]
        coor1 = (int(m), int(m))
        coor2 = (int(m), int(ha-m))
        coor3 = (int(wa-m), int(m))
        coor4 = (int(wa-m), int(ha-m))
        fillCnt = isFilled(ans, [coor1, coor2, coor3, coor4])

        if fillCnt > cnt:
            #save_img(ans, 'celda.png')
            cnt = fillCnt
            val = a

    return val


def read_form(img):
    ## coger qr
    ##qrt  = img[42:223, 510:686]
    qrt = img[32:233, 500:696]
    save_img(qrt, 'qr.png')
    ide = qrdecode('process/qr.png')
    zona = ide.split('_')[0]
    print ide


    division = ide.split('_')[1]+', '+ide.split('_')[2]

    try:
        division = ide.split('_')[1]+', '+ide.split('_')[2]
    except:
        print 'pass'
        #return
    ##no = ide.split('_')[3]  ##ahora siempre hay un unico forumlario
    form = img[348:2221, 177:1509]
    save_img(form, 'form.png')

    items = 10
    w, h = form.shape[::-1]
    cnta = 0

    for r in range(items):
        ## respuesta
        y = h/items*r
        yy =h/items*(r+1)
        item = form[y:yy, : ]
        save_img(item, 'item_'+str(r)+'.png')
        answers={}

        ## conteo personas
        item_p = item[ 83:114, 0 : 1131] #############################calibrar
        save_img(item_p, 'item_p_'+str(r)+'.png')
        item_p_w, item_p_h = item_p.shape[::-1]
        list_p = ['homes', 'dones', 'no se sap', 'animals']
        for rr in range(4):
            #print 'rrrrr: ',r, rr,   (item_p_w/4*(r+1))- (item_p_w/4*r)
            item_p_t=item_p[ : , (item_p_w/4*rr):(item_p_w/4*(rr+1))]
            val = getHeigherH(item_p_t, 8)+1
            answers[list_p[rr]]=val
        print

        ## conteo descripcion
        item_d = item[ 44:, 1129 : 1164]
        save_img(item_d, 'item_d_'+str(r)+'.png')
        item_d_w, item_d_h = item_d.shape[::-1]
        list_d = ['al ras', 'sota cobert', 'dins cotxe', 'dins caixer']
        val = getHeigherV(item_d, 4)
        if val != -1:
            answers[list_d[val]]=1

        save_ans(answers,r+1, ide, division, zonesDict)

def save_ans(answers, r, ide, division, zonesDict):
    '''

    '''
    doc = ezodf.opendoc(ods)
    sheet = doc.sheets['conteig']
    nr = sheet.nrows()
    sheet.append_rows(1)
    c_districte = int(ide.split('_')[0][:-2])
    n_districte = zonesDict[int(ide.split('_')[0])][1]
    zona = ide.split('_')[0]
    dx = int(ide.split('_')[1])
    dy = int(ide.split('_')[2])

    #sheet[nr, 0].set_value(districte)
    sheet[nr, 1].set_value(c_districte)
    sheet[nr, 2].set_value(n_districte)
    sheet[nr, 3].set_value(zona)
    sheet[nr, 4].set_value(dx)
    sheet[nr, 5].set_value(dy)
    sheet[nr, 6].set_value(r)
    sheet[nr, 7].set_value(answers.get('homes'))
    sheet[nr, 8].set_value(answers.get('dones'))
    sheet[nr, 9].set_value(answers.get('no se sap'))
    sheet[nr, 10].set_value(answers.get('animals'))
    if answers.get('al ras') != None:
        sheet[nr, 11].set_value(answers.get('al ras'))
    if answers.get('sota cobert') != None:
        sheet[nr, 12].set_value(answers.get('sota cobert'))
    if answers.get('dins cotxe') != None:
        sheet[nr, 13].set_value(answers.get('dins cotxe'))
    if answers.get('dins caixer') != None:
        sheet[nr, 14].set_value(answers.get('dins caixer'))

    doc.save()
    return

def prepareOds():
    '''
    '''
    camps = ['total', 'id_districtes', 'districtes', 'id_zones', 'subzona_x','subzona_y','id', 'homes', 'dones', 'no se sap', 'animals', 'al ras', 'sota cobert', 'dins cotxe', 'dins caixer']

    if os.path.isfile(ods) == True:
        return

    doc = ezodf.newdoc(doctype="ods", filename=ods)
    sheets  = doc.sheets
    sheets += ezodf.Table('total')
    sheets += ezodf.Table('districtes')
    sheets += ezodf.Table('zones')
    sheets += ezodf.Table('subzones')
    sheets += ezodf.Table('conteig')

    for sheet in doc.sheets:
        for c, n in enumerate(camps):
            doc.sheets[sheet.name]
            doc.sheets[sheet.name].append_columns(1)
            doc.sheets[sheet.name][0,c].set_value(n)

    #fill fields districtes
    conn = sqlite3.connect(zones)
    c = conn.cursor()
    c.execute('''select cast(c_distri as integer), n_distri from zones  group by c_distri order by cast(c_distri as integer)''')
    for rown , row  in enumerate(c.fetchall()):
        doc.sheets['districtes'].append_rows(1)
        doc.sheets['districtes'][rown+1,1].set_value(row[0])
        doc.sheets['districtes'][rown+1,2].set_value(row[1])
    conn.close()
    doc.save()

    #fill fields zones
    zonesDict={}
    conn = sqlite3.connect(zones)
    c = conn.cursor()
    c.execute('''select cast(c_distri as integer), n_distri, cast(name as integer) from zones  group by name order by cast(name as integer)''')
    for rown , row  in enumerate(c.fetchall()):
        doc.sheets['zones'].append_rows(1)
        doc.sheets['zones'][rown+1,1].set_value(row[0])
        doc.sheets['zones'][rown+1,2].set_value(row[1])
        doc.sheets['zones'][rown+1,3].set_value(row[2])
        zonesDict[row[2]]=(row[0], row[1])
    conn.close()
    doc.save()

    #fill fields subzones
    conn = sqlite3.connect(subzones)
    c = conn.cursor()
    c.execute('''select cast(name as integer), x, y from elementsdiv order by cast(name as integer), x, y''')
    for rown , row  in enumerate(c.fetchall()):
        doc.sheets['zones'].append_rows(1)
        doc.sheets['zones'][rown+1,1].set_value(zonesDict[row[0]][0])
        doc.sheets['zones'][rown+1,2].set_value(zonesDict[row[0]][1])
        doc.sheets['zones'][rown+1,3].set_value(row[0])
        doc.sheets['zones'][rown+1,4].set_value(row[1])
        doc.sheets['zones'][rown+1,5].set_value(row[2])
    conn.close()
    doc.save()
    return


## crea el listado de zonas para luego monatr el excel
def createZD():
    zonesDict={}
    conn = sqlite3.connect(zones)
    c = conn.cursor()
    c.execute('''select cast(c_distri as integer), n_distri, cast(name as integer) from zones  group by name order by cast(name as integer)''')
    for rown , row  in enumerate(c.fetchall()):
        zonesDict[row[2]]=(row[0], row[1])
    conn.close()
    return zonesDict



if __name__ == "__main__":


    scans=[]
    prepareOds()
    zonesDict = createZD()
    for f in sorted(os.listdir(scanFolder)):
        print f
        if f[-4:] == '.jpg':
            scans.append(scanFolder+f)
    try:

        pag = str(open('index.txt', 'r').read())
        inici=int(scans.index(pag))
    except:
        inici = 0

    print inici
    scans=scans[inici:]

    errorfile=open('errors.txt','w+')


    for f in scans:
        print f,type(f)
        img, page_type = retrieve_relevant_area(f)
        if page_type == 0:
            r = read_division(img)
            if r == None:
                errorfile.write(str(f)+'\n')
                print 'ERROR in : ', f
        elif page_type == 2:
            pass
            #read_form(img)

        index =open('index.txt', 'w+')
        index.write(f)
        index.close()
    errorfile.close()

    ferrors=open('errors.txt','r')

    errorfile = open('errors2.txt', 'w+')
    for f in ferrors.readlines():
        #elimina el salt de linia \n
        f=f.rstrip()
        img, page_type = retrieve_relevant_area(f,zonaq=(200,210,220,240),restriccio1=210,restriccio2=220)
        if page_type == 0:
            r = read_division(img)
            if r == None:
                errorfile.write(str(f) + '\n')
                print 'ERROR in : ', f
        elif page_type == 2:
            pass
            # read_form(img)

    errorfile.close()