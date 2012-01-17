from urlparse import urlparse
from urllib import urlopen

class SlingRPM:

  def __init__(self, targetrepo=""):
      response = urlopen(targetrepo + 'repodata/repomd.xml')
      if response.getcode() != 200:
	raise Exception
      response = urlopen(targetrepo + '.slingrpm.conf')
      if response.getcode() != 200:
	raise Exception
      self.targetpath = '/'
      self.targetrepo = targetrepo

  def push(self):
    pass

import os.path

class CatchRPM:

  def __init__(self, targetrepo=""):
    if not os.path.isfile(os.path.join(targetrepo, '.slingrpm.conf')):
      raise Exception
    self.targetrepo = targetrepo
