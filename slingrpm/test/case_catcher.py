import konira
import os
import os.path

import testutils
from slingrpm import Catcher 
from slingrpm import SlingerFileServer

describe "receiving a package with Catcher":
 
  before all:
    testutils.setuprepos()

    self.badrepopath = os.path.join(os.getcwd(),'testarea/repos/badrepo/')
    self.repopath = os.path.join(os.getcwd(),'testarea/repos/repo/')

  before each:
    self.slinger = SlingerFileServer(os.path.join(os.getcwd(), 'slingrpm/test'))
    self.slinger.start()
    self.port = self.slinger.port
    self.filetoget = os.path.join(os.getcwd(), 'slingrpm/test/empty-0-1.i386.rpm')
    self.nonfiletoget = os.path.join(os.getcwd(), 'slingrpm/test/empty-0-10.i386.rpm')
 
  it "throws an exception if the specified repo is not on the filesystem":
    raises Exception: catcher = Catcher(targetrepo=self.badrepopath, slinghost='localhost', slingport=self.port, file=self.filetoget)

  it "accepts a targetrepo, host, port and file for catching an RPM":
    catcher = Catcher(targetrepo=self.repopath, slinghost='localhost', slingport=self.port, file=self.filetoget)
    assert catcher

  it "remembers the path to the targetrepo":
    catcher = Catcher(targetrepo=self.repopath, slinghost='localhost', slingport=self.port, file=self.filetoget)
    assert catcher.targetrepo == self.repopath 

  it "can obtain a full path to the repository from .slingrpm.conf":
    catcher = Catcher(targetrepo=self.repopath, slinghost='localhost', slingport=self.port, file=self.filetoget)
    assert os.path.isdir(catcher.config.repolocation)

  it "can obtain a subdirectory in the repository for pushing packages into":
    catcher = Catcher(targetrepo=self.repopath, slinghost='localhost', slingport=self.port, file=self.filetoget)
    assert catcher.config.packagedir == os.path.join(catcher.config.repolocation, "")

  it "can obtain a set of parameters for running createrepo on the target repo":
    catcher = Catcher(targetrepo=self.repopath, slinghost='localhost', slingport=self.port, file=self.filetoget)
    assert catcher.config.createrepoopts == "--update --excludes .slingrpm.conf --checksum sha" 

  it "obtains the file when pull method is called":
    catcher = Catcher(targetrepo=self.repopath, slinghost='localhost', slingport=self.port, file=self.filetoget)
    catcher.pull()
    assert os.path.isfile(os.path.join(catcher.packagedir, os.path.basename(self.filetoget)))
    os.remove(os.path.join(catcher.packagedir, os.path.basename(self.filetoget)))

  it "raises an exception if pull method is called on nonexistant file":
    catcher = Catcher(targetrepo=self.repopath, slinghost='localhost', slingport=self.port, file=self.nonfiletoget)
    raises Exception: catcher.pull()

  after each:
    self.slinger.stop()

  after all:
    testutils.teardownrepos()


