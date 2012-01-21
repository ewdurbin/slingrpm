import konira
import os.path

import testutils
from slingrpm import Catcher 

describe "receiving a package with Catcher":
 
  before all:
    testutils.setuprepos()

    self.badrepopath = os.path.join(os.getcwd(),'testarea/badrepo/')
    self.repopath = os.path.join(os.getcwd(),'testarea/repo/')

  before each:
    pass
 
  it "throws an exception if the specified repo is not on the filesystem":
    raises Exception: catcher = Catcher(targetrepo=self.badrepopath)

  it "throws an exception if no repo is specified":
    raises Exception: catcher = Catcher()

  it "remembers the path to the targetrepo":
    catcher = Catcher(targetrepo=self.repopath)
    assert catcher.targetrepo == self.repopath 

  it "can obtain a full path to the repository from .slingrpm.conf":
    catcher = Catcher(targetrepo=self.repopath)
    assert os.path.isdir(catcher.config.repolocation)

  it "can obtain a subdirectory in the repository for pushing packages into":
    catcher = Catcher(targetrepo=self.repopath)
    assert catcher.config.packagedir == os.path.join(catcher.config.repolocation, "")

  it "can obtain a set of parameters for running createrepo on the target repo":
    catcher = Catcher(targetrepo=self.repopath)
    assert catcher.config.createrepoopts == "--update --excludes .slingrpm.conf --checksum sha" 

  after each:
   pass
    
  after all:
    testutils.teardownrepos()


