import os.path
import ConfigParser
import urllib

class ConfigSling:

  def __init__(self, configlocation=None):
    self.repolocation = None
    self.packagedir = None
    self.createrepoopts = None
    self.commport = None
    if configlocation:
      self.read(configlocation)

  def read(self, configlocation):
    if not configlocation.startswith('http') and not os.path.isfile(configlocation):
      raise Exception
    self.configlocation = configlocation

    try:
      config = ConfigParser.RawConfigParser()
      if configlocation.startswith('http'):
        fp = urllib.urlopen(self.configlocation)
        config.readfp(fp)
      else:
        config.read(self.configlocation)
      self.config = config

      self.repolocation = self.config.get('SlingRPM', 'repolocation') 
      packagedir = self.config.get('SlingRPM', 'packagedir')
      self.packagedir = os.path.join(self.repolocation, packagedir)
      self.createrepoopts = self.config.get('SlingRPM', 'createrepoopts')
      self.commport = self.config.get('SlingRPM', 'commport')
    except:
      raise

  def new(self, configlocation):
    if os.path.isfile(configlocation):
      raise Exception
    config = ConfigParser.RawConfigParser()
    config.add_section('SlingRPM')
    config.set('SlingRPM', 'repolocation', os.path.dirname(configlocation))
    config.set('SlingRPM', 'packagedir', 'packages')
    config.set('SlingRPM', 'commport', 64666)
    config.set('SlingRPM', 'createrepoopts', '--update --excludes .slingrpm.conf --checksum sha')
    with open(configlocation, 'wb') as configfile:
      config.write(configfile)
    self.read(configlocation)
    
