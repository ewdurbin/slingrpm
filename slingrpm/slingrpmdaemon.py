import ConfigParser
import os.path

class SlingRPMDaemon:

  def __init__(self, conf='/etc/slingrpm/daemon.conf'):
    self.read(conf)

  def read(self, conf):
    if not os.path.isfile(conf):
      raise Exception
    self.conf = conf

    try:
      config = ConfigParser.RawConfigParser()
      config.read(self.conf)
      self.config = config

      self.listenport = self.config.get('SlingRPMDaemon', 'listenport')
    except:
      raise


    

