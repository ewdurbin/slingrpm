from urlparse import urlparse
from urllib import urlopen

import slingrpm

class Slinger:

  def __init__(self, targetrepo=""):
    repomd = urlopen(targetrepo + 'repodata/repomd.xml')
    if repomd.getcode() != 200:
      raise Exception

    self.targetrepo = targetrepo
    self.config = slingrpm.SlingConfig()
    self.config.read(self.targetrepo + '.slingrpm.conf')
