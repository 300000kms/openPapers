//tutorial

antes de empezar:
    copiar los archivos de openpapers en una carpeta
    configurara routes.py
    - indicar el nombre del proyecto
    - indicar el nombre de los archivos zonas y distritos (cada uno debe tener un campo id y name)

    decargar el archivo shapefile del catastro de la ciudad a mapear

    lanzar
    00createProject.py: crea la estructura de carpetas necesaria
    00importCadastre.py: descomprime el catastro que se deberia encontrar en datain y lo convierte a sqlite
    01buildzones.py: crea el archivo de las zonas como resultado de la interseccion con distritos
    02rotatebounds.py: crea los bounds de las zonas a mapear
    03buildqgisfiles.py: monta los archivos para qgis
    03divide.py: divide en hojas
    04generateComp.py: se lanza desde qgis con el archivo abierto
    05/06 segun como se quiera el output final....
