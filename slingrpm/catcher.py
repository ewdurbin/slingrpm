import os.path

class Catcher:

  def __init__(self, targetrepo=""):
    if not os.path.isfile(os.path.join(targetrepo, '.slingrpm.conf')):
      raise Exception
    self.targetrepo = targetrepo
