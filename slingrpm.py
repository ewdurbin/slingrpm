from urlparse import urlparse
from urllib import urlopen

class SlingRPM:

  def __init__(self, targetrepo=""):
      response = urlopen(targetrepo + 'repodata/repomd.xml')
      if response.getcode() != 200:
	raise Exception
      self.targetrepo = targetrepo

  def push(self):
    pass

class CatchRPM:

  def __init__(self, repo=""):
    pass
