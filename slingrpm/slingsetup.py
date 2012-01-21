import os.path
import sys
import subprocess
import ConfigParser

from slingconfig import SlingConfig
from yumrepo import YumRepo

from exceptions import NoRepoException
from exceptions import AlreadySlingEnabledException 

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
    repo = YumRepo(self.config.repolocation)
    if not os.path.isdir(os.path.join(fullrepopath, 'repodata')):
      repo.updatemetadata()

    self.config = SlingConfig(os.path.join(fullrepopath, '.slingrpm.conf'))
