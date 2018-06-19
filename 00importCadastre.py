'''
use ogr to import cadastre shapefiles to spatialite
'''

import routes
import glob
import zipfile
import os
import subprocess as sub

def unzip(f):
    '''
    descomprime el archivo f.zip en la misma carpeta

    '''
    zfile = zipfile.ZipFile(f)
    print '/'.join(f.split('/')[:-1])
    zfile.extractall( routes.r_datain+'files')

    return

def createFolder(folder):
    dir_exists = os.path.isdir(folder)
    if dir_exists is False:
        os.makedirs(folder)
        print '>>> created folder :', folder
    return


def getGeoType(File):
    #ogrR = "ogrinfo -ro PG:'host="+host+" user="+user+" dbname="+dbname+"'"
    ogrR =["ogrinfo" ,File]
    p = sub.Popen(ogrR, stdout=sub.PIPE,stderr = sub.PIPE)
    output, errors = p.communicate()
    print output

    out = output.split('(')[1].strip(') \n')#[:-2]

    if out == 'Polygon':
        result = 'MULTIPOLYGON'
    elif out == 'Line String':
        result = 'MULTILINESTRING'
    elif out =='Point':
        result = 'MULTIPOINT'
    elif out == 'Multi Polygon':
        result = 'MULTIPOLYGON'

    return result


def insert2sqlite(fileName):
    '''

    ogr2ogr -f SQLite -dsco SPATIALITE=YES db_name.sqlite /path/to/gis_data -nlt PROMOTE_TO_MULTI

    ogr2ogr -update -append -f SQLite mydb.sqlite -nln "newtable" -a_srs "EPSG:4326" shapefile.shp

    :param fileName:
    :return:
    '''
    print ('>>> importing : ', fileName)
    #check if exists
    Type = getGeoType(fileName)
    print Type

    #Type = 'Point'

    ogrR = "ogr2ogr -overwrite -f SQLITE "  # -overwrite
    ogrR += '-dsco SPATIALITE=YES '
    ogrR += (routes.r_proj+'cartobase/'+fileName.replace('.SHP', '.sqlite').lower().split('/')[-1]).replace(' ', '\ ')
    ogrR += " -t_srs 'epsg:25831'"
    ogrR += " -s_srs 'epsg:25831'"
    ogrR += " -dim 2"
    ogrR += " -lco LAUNDER=YES"
    ogrR += " -lco GEOMETRY_NAME=geom"
    ogrR += ' -nlt ' + Type +' '
    ogrR +=  " -nln " + 'elements '
    ogrR += fileName.replace(' ', '\ ')
    ogrR += ' -progress'
    print ogrR
    os.system(ogrR)
    return

############################################################################
############################################################################
############################################################################
############################################################################

def import():

    files ={
        'MASA.zip' :'',
        'PARCELA.zip' :'',
        'ELEMLIN.zip' :'',
        'CONSTRU.zip' :''
    }

    createFolder(routes.r_datain+'files')

    #uncompress
    folder = ''

    for file in glob.glob(routes.r_datain+"*.zip"):
        unzip(file)

    for file in glob.glob(routes.r_datain+"files/*.zip"):
        if file.split('/')[-1] in files.keys():
            unzip(file)

    #import
    shapefiles = []
    for s in glob.glob(routes.r_datain+"files/*.SHP"):
        shapefiles.append(s.split('/')[-1])
    for file in files.keys():
        if file.split('.')[0]+'.SHP' in shapefiles:
            insert2sqlite(routes.r_datain + "files/" + file.split('.')[0] + '.SHP')
    return


if __name__ == "__main__":
    import()


