from urlparse import urlparse
from urllib import urlopen

class RPM:

  def __init__(self, targetrepo=""):
      response = urlopen(targetrepo + 'repodata/repomd.xml')
      if response.getcode() != 200:
	raise Exception
      self.targetrepo = targetrepo

  def push(self):
    pass

