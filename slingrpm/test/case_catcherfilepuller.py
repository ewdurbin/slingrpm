import konira

from slingrpm import CatcherFilePuller 
from slingrpm import SlingerFileServer
import testutils
import os
import os.path

describe "receiving a package with CatcherFilePuller":
 
  before all:
    pass

  before each:
    testutils.setuprepos()
    self.slinger = SlingerFileServer(os.path.join(os.getcwd(), 'testarea/repo'), 1024)
    self.filetoget = os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf')
    self.nonfiletoget = os.path.join(os.getcwd(), 'testarea/repo/no.file')
    self.dst = os.path.join(os.getcwd(), 'testarea/recvd.file')
 
  it "initializes with a destpath, srcpath, host and port":
    catcher = CatcherFilePuller(self.dst, self.filetoget, '127.0.0.1', self.slinger.port)
    assert catcher

  it "raises Exception if destpath exists":
    raises Exception: catcher = CatcherFilePuller(self.filetoget, self.filetoget, '127.0.0.1', self.slinger.port)

  it "gets a file when get_file is called":
    catcher = CatcherFilePuller(self.dst, self.filetoget, '127.0.0.1', self.slinger.port)
    catcher.get_file()
    assert os.path.isfile(self.dst)

  it "raises Exception if get_file is called for non existant file": 
    catcher = CatcherFilePuller(self.dst, self.nonfiletoget, '127.0.0.1', self.slinger.port)
    raises Exception: catcher.get_file()

  it "raises Exception if get_file is called for file outside of serve directory": 
    catcher = CatcherFilePuller(self.dst, '/etc/hosts', '127.0.0.1', self.slinger.port)
    raises Exception: catcher.get_file()

  after each:
    self.slinger.stop()
    testutils.teardownrepos()
    
  after all:
    pass
