#copy templates into
from shutil import copyfile
import glob
import routes

for source in glob.glob('templates/'+"*.*"):
    copyfile(source, routes.r_proj+source.split('/')[-1])