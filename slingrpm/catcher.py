import os.path

import slingrpm

class Catcher:

  def __init__(self, targetrepo=""):
    if not os.path.isfile(os.path.join(targetrepo, '.slingrpm.conf')):
      raise Exception

    self.targetrepo = targetrepo
    self.config = slingrpm.SlingConfig()
    self.config.read(self.targetrepo + '.slingrpm.conf')
