## http://www.blog.pythonlibrary.org/2012/07/11/pypdf2-the-new-fork-of-pypdf/
## https://pythonhosted.org/PyPDF2/PdfFileMerger.html
import PyPDF2
import os


root='output/'
#select files
QEpdfs=[]
for f in os.listdir(root):
    if f[-4:] == '.pdf':
        QEpdfs.append(f)

QEpdfs = sorted(QEpdfs)

##make listdir
chap=[]
for q in QEpdfs:
    if q[0:2] not in chap:
        chap.append(q[0:2])


chap = sorted(chap)
for c in chap:
    print c
    merger=PyPDF2.PdfFileMerger()
    merger.write(open('districte_'+c+'.pdf', 'wb')) #crea el archivo vacio para unir
    for d in range(0,len(QEpdfs)):
        if QEpdfs[d][0:2]==c:
            path=open(root+QEpdfs[d], 'rb') #abre el pdf a incrustar
            merger.append(fileobj=path)
    merger.write(open('districte_'+c+'.pdf', 'ab'))
    merger.close()

'''
merger=PyPDF2.PdfFileMerger()
c=0
merger.write(open('test.pdf', 'wb'))


for d in range(0,len(QEpdfs)):
    print QEpdfs[d]
    path=open(root+QEpdfs[d], 'rb')
    merger.append(fileobj=path)

merger.write(open('test.pdf', 'ab'))
merger.close()
'''
print