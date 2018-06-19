## http://www.blog.pythonlibrary.org/2012/07/11/pypdf2-the-new-fork-of-pypdf/
## https://pythonhosted.org/PyPDF2/PdfFileMerger.html
import PyPDF2
import os
import PIL.Image
import routes


root = routes.r_proj


def png2pdf():
    QEpdfs=[]
    for f in os.listdir(root+'out/'):
        if f[-4:] == '.png':
            QEpdfs.append(f)
    QEpdfs = sorted(QEpdfs)

    for d in QEpdfs:
        im=PIL.Image.open(root+'out/'+d)
        im.convert("RGB").save(root+'pdf/'+'_'.join(d[0:-4].split('_')[1:])+'.pdf', "PDF", quality=150)
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


def mergePdfsGrouped(name):
    '''
    agrupa los pdfs segun el valor de distrito que es el ultimo numeor despues del _

    '''
    QEpdfs=[]
    for f in os.listdir(root+'pdf/'):
        if f[-4:] == '.pdf':
            QEpdfs.append(f)
    QEpdfs = sorted(QEpdfs)

    todo = []
    for f in QEpdfs:
        todo.append(f.split('_')[-1])
    todo = set(todo)

    for di in todo:
        print di
        fileName = root+name+'_'+di+'.pdf'
        merger=PyPDF2.PdfFileMerger()
        merger.write(open(fileName, 'wb'))
        for f in QEpdfs:
            if  f.split('_')[-1] == di:
                path = open(root+'pdf/'+f, 'rb')
                merger.append(fileobj=path)
                print '.'
        merger.write(open(fileName, 'ab'))
        merger.close()
    return


png2pdf()
#mergePdfs('tarragona_2')
mergePdfsGrouped('badalona')