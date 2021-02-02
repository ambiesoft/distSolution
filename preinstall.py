import sys
import subprocess
import pkg_resources
from importlib import import_module

def importWithInstall(toImport, installOnly=False):
  required = {toImport}
  installed = {pkg.key for pkg in pkg_resources.working_set}
  missing = required - installed

  if missing:
      python = sys.executable
      subprocess.check_call([python, '-m', 'pip', 'install', *missing]) #, stdout=subprocess.DEVNULL)

  if installOnly:
    return
    
  # find module name to import
  metadata_dir = pkg_resources.get_distribution(toImport).egg_info
  gname = open('%s/%s' % (metadata_dir, 'top_level.txt')).read().rstrip()

  # make global val
  globals()[gname] = import_module(gname)


importWithInstall('easywebdav', installOnly=True)