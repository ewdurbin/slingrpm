import os.path
import time

import slingrpm

class Catcher:

  def __init__(self, targetrepo="", slinghost="", slingport=0, file=""):
    if not os.path.isfile(os.path.join(targetrepo, '.slingrpm.conf')):
      raise Exception

    self.targetrepo = targetrepo
    self.slinghost = slinghost
    self.slingport = slingport
    self.config = slingrpm.SlingConfig()
    self.config.read(self.targetrepo + '.slingrpm.conf')
    self.packagedir = self.config.packagedir
    self.package = os.path.basename(file)
    self.dest = os.path.join(self.packagedir, self.package)
    self.puller = slingrpm.CatcherFilePuller(self.dest, file, self.slinghost, self.slingport)

  def pull(self):
    self.puller.start()
    while self.puller.status_queue.empty():
      time.sleep(.001)
    if not self.puller.status_queue.get() == 'FILE RECEIVED':
      raise Exception
    
