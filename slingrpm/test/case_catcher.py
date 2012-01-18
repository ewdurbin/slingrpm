import konira

import os.path

import testutils
from slingrpm import Catcher 

describe "receiving a package":
 
  before all:
    testutils.setuprepos()

    self.badrepopath = os.path.join(os.getcwd(),'testarea/badrepo/')
    self.repopath = os.path.join(os.getcwd(),'testarea/repo/')

  before each:
    pass
 
  it "throws an exception if the specified repo is not on the filesystem":
    raises Exception: catcher = Catcher(targetrepo=self.badrepopath)

  it "remembers the path to the targetrepo":
    catcher = Catcher(targetrepo=self.repopath)
    assert catcher.targetrepo == self.repopath 

  after each:
    pass
    
  after all:
    testutils.teardownrepos()


