import os.path
import sys
import subprocess
import ConfigParser

from slingconfig import SlingConfig

from exceptions import NoRepoException
from exceptions import AlreadySlingEnabledException 

def execute(cmd):
  fd = open('execute.log', 'a')
  retcode = subprocess.check_call([cmd], stderr=fd, stdout=fd, shell=True)
  fd.close()
  return retcode

class SlingSetup:

  def __init__(self, repopath):
    fullrepopath = os.path.abspath(repopath)
    if not os.path.isdir(fullrepopath):
      raise NoRepoException('directory not found at: ' + fullrepopath)
    if not os.path.isfile(os.path.join(fullrepopath, '.slingrpm.conf')):
      self.config = SlingConfig()
      self.config.new(os.path.join(fullrepopath, '.slingrpm.conf'))
    else:
      raise AlreadySlingEnabledException('repo at : ' + fullrepopath + ' already sling enabled!')
    if not os.path.isdir(os.path.join(fullrepopath, 'repodata')):
      execute('createrepo ' + fullrepopath + " " +self.config.createrepoopts)

    self.config = SlingConfig(os.path.join(fullrepopath, '.slingrpm.conf'))
