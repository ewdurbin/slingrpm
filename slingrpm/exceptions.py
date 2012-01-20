class NoRepoException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value) # pragma: no cover

class AlreadySlingEnabledException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value) # pragma: no cover
