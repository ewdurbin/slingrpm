import os.path
import ConfigParser

from ConfigParser import MissingSectionHeaderError

class ConfigSling:

  def __init__(self, configlocation):
    if not os.path.isfile(configlocation):
      raise Exception
    self.configlocation = configlocation
    config = ConfigParser.RawConfigParser()
    try:
      config.read(self.configlocation)
    except MissingSectionHeaderError:
      raise Exception 
