from urlparse import urlparse
from urllib import urlopen
import os.path

import slingrpm

class Slinger:

  def __init__(self, targetrepo="", file=""):
    repomd = urlopen(targetrepo + 'repodata/repomd.xml')
    if repomd.getcode() != 200:
      raise Exception

    if not os.path.isfile(file):
      raise Exception

    self.targetrepo = targetrepo
    self.config = slingrpm.SlingConfig()
    self.config.read(self.targetrepo + '.slingrpm.conf')

    self.servedir = os.path.dirname(file)

    self.fileserver = slingrpm.SlingerFileServer(self.servedir)

  def serve(self):
    self.fileserver.start()

  def stop(self):
    self.fileserver.proc.terminate()
    self.fileserver.proc.join()
