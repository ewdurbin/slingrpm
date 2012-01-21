
import subprocess
import os.path
from slingrpm import SlingConfig

def execute(cmd):
  fd = open('execute.log', 'a')
  fd.write('slingrpm/yumrepo')
  retcode = subprocess.check_call([cmd], stderr=fd, stdout=fd, shell=True)
  fd.close()
  return retcode

class YumRepo:

  def __init__(self, repopath):
    if not os.path.isdir(repopath):
      raise Exception
    if not os.path.isfile(os.path.join(repopath, '.slingrpm.conf')):
      raise Exception
    self.repopath = repopath
    self.slingconfig = SlingConfig(os.path.join(repopath, '.slingrpm.conf'))

  def updatemetadata(self):
    try:
      return execute('createrepo %s %s' % (self.slingconfig.repolocation, self.slingconfig.createrepoopts))
    except:
      raise
