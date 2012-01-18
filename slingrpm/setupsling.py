import os.path
import sys
import subprocess
import ConfigParser

from configsling import ConfigSling

from slingrpm import NoRepoException
from slingrpm import AlreadySlingEnabledException 

def execute(cmd):
  fd = open('execute.log', 'a')
  retcode = subprocess.check_call([cmd], stderr=fd, stdout=fd, shell=True)
  fd.close()
  return retcode

class SetupSling:

  def __init__(self, repopath):
    fullrepopath = os.path.abspath(repopath)
    if not os.path.isdir(fullrepopath):
      raise NoRepoException('directory not found at: ' + fullrepopath)
    if not os.path.isdir(os.path.join(fullrepopath, 'repodata')):
      execute('createrepo ' + fullrepopath)
    if not os.path.isfile(os.path.join(fullrepopath, '.slingrpm.conf')):
      config = ConfigSling()
      config.new(os.path.join(fullrepopath, '.slingrpm.conf'))
    else:
      raise AlreadySlingEnabledException('repo at : ' + fullrepopath + ' already sling enabled!')

    self.repolocation = fullrepopath
