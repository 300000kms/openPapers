## http://www.blog.pythonlibrary.org/2012/07/11/pypdf2-the-new-fork-of-pypdf/
## https://pythonhosted.org/PyPDF2/PdfFileMerger.html
import PyPDF2
import os
import PIL.Image


root='/media/pablueke/CE0A39130A38FA53/_sync/17037 arrels_reus/project_tarragona/'


def png2pdf():
    QEpdfs=[]
    for f in os.listdir(root+'out/'):
        if f[-4:] == '.png':
            QEpdfs.append(f)
    QEpdfs = sorted(QEpdfs)
    for d in QEpdfs:
        im=PIL.Image.open(root+'out/'+d)
        im.convert("RGB").save(root+'pdf/'+d[0:-4]+'.pdf', "PDF", quality=150)
        print '.',
    return


def mergePdfs(name):
    QEpdfs=[]
    for f in os.listdir(root+'pdf/'):
        if f[-4:] == '.pdf':
            QEpdfs.append(f)
    QEpdfs = sorted(QEpdfs)
    merger=PyPDF2.PdfFileMerger()
    merger.write(open(root+name+'.pdf', 'wb')) #crea el archivo vacio para unir
    for d in range(0,len(QEpdfs)):
        path = open(root+'pdf/'+QEpdfs[d], 'rb')
        merger.append(fileobj=path)
    merger.write(open(root+name+'.pdf', 'ab'))
    merger.close()
    return

png2pdf()
mergePdfs('tarragona')