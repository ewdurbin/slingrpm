from urlparse import urlparse
from urllib import urlopen

class SlingRPM:

  def __init__(self, targetrepo=""):
    repomd = urlopen(targetrepo + 'repodata/repomd.xml')
    if repomd.getcode() != 200:
      raise Exception

    slingrpmconf = urlopen(targetrepo + '.slingrpm.conf')
    if slingrpmconf.getcode() != 200:
      raise Exception

    self.targetpath = '/'
    self.targetrepo = targetrepo

import os.path

class CatchRPM:

  def __init__(self, targetrepo=""):
    if not os.path.isfile(os.path.join(targetrepo, '.slingrpm.conf')):
      raise Exception
    self.targetrepo = targetrepo
