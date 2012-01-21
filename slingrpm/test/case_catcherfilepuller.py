import konira

from slingrpm import CatcherFilePuller 
from slingrpm import SlingerFileServer
import testutils
import os
import os.path
import time

describe "receiving a package with CatcherFilePuller":
 
  before all:
    testutils.setuprepos()

  before each:
    self.slinger = SlingerFileServer(os.path.join(os.getcwd(), 'slingrpm/test'), 32)
    self.slinger.start()
    self.filetoget = os.path.join(os.getcwd(), 'slingrpm/test/empty-0-1.i386.rpm')
    self.nonfiletoget = os.path.join(os.getcwd(), 'slingrpm/test/empty-0-2.i386.rpm')
    self.dst = os.path.join(os.getcwd(), 'testarea/repos/repo/empty-0-1.i386.rpm')
 
  it "initializes with a destpath, srcpath, host and port":
    catcher = CatcherFilePuller(self.dst, self.filetoget, '127.0.0.1', self.slinger.port)
    assert catcher

  it "raises Exception if destpath exists":
    raises Exception: catcher = CatcherFilePuller(self.filetoget, self.filetoget, '127.0.0.1', self.slinger.port)

  it "gets a file when get_file is called":
    catcher = CatcherFilePuller(self.dst, self.filetoget, '127.0.0.1', self.slinger.port)
    catcher.start()
    while catcher.status_queue.empty():
      time.sleep(.001)
    assert os.path.isfile(self.dst)

  it "raises Exception if get_file is called for non existant file": 
    catcher = CatcherFilePuller(self.dst, self.nonfiletoget, '127.0.0.1', self.slinger.port)
    raises Exception: catcher.get_file()

  it "raises Exception if get_file is called for file outside of serve directory": 
    catcher = CatcherFilePuller(self.dst, '/etc/hosts', '127.0.0.1', self.slinger.port)
    raises Exception: catcher.get_file()

  after each:
    if os.path.isfile(self.dst):
      os.remove(self.dst)
    self.slinger.stop()
    
  after all:
    testutils.teardownrepos()
