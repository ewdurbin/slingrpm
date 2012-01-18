import sys
import os.path

import testutils

import konira

from slingrpm import SlingRPM
from catchrpm import CatchRPM
from setupsling import SetupSling

from slingrpm import NoRepoException
from slingrpm import AlreadySlingEnabledException 

describe "setting up a sling enabled repository":

  before all:
    pass

  before each:
    testutils.setuprepos() 
 
  it "raises NoRepoException if target repo is not a directory which exists":
    raises NoRepoException: repo = SetupSling('testarea/norepo')

  it "sets up an empty repository if no repomd.xml exists":
    repo = SetupSling('testarea/freshrepo')
    assert os.path.isfile('testarea/freshrepo/repodata/repomd.xml')

  it "sets up a .slingrpm.conf if none exists":
    repo = SetupSling('testarea/freshrepo')
    assert os.path.isfile('testarea/freshrepo/.slingrpm.conf')

  it "raises AlreadySlingEnabledException if repo is already sling enabled":
    raises AlreadySlingEnabledException: repo = SetupSling('testarea/repo')

  after each:
    testutils.teardownrepos()

  after all:
    pass

describe "pushing a rpm package to our centralized repo":

  before all:
    testutils.setuprepos()
    self.server = testutils.TempServer()
    self.server.start()

  before each:
    pass
    
  it "throws an exception if you dont specify the repo":
    raises Exception: SlingRPM()

  it "throws an exception if the specified repo is not an http location":
    raises Exception: pusher = SlingRPM(targetrepo="/foo/bar/bazz/")

  it "throws an exception if the specified repo is not a yum repo":
    raises Exception: pusher = SlingRPM(targetrepo="http://localhost:65001/testarea/badrepo/")

  it "throws an exception if the specified repo is not setup for slingrpm":
    raises Exception: pusher = SlingRPM(targetrepo="http://localhost:65001/testarea/realrepo/")

  it "likes repos with a repmod and slingrpm":
    pusher = SlingRPM("http://localhost:65001/testarea/repo/")
    assert pusher

  it "can obtain a full path to the repository from .slingrpm.conf":
    pusher = SlingRPM("http://localhost:65001/testarea/repo/")
    assert os.path.isdir(pusher.targetpath)

  it "remembers the repo it's been set to publish to":
    pusher = SlingRPM("http://localhost:65001/testarea/repo/")
    assert pusher.targetrepo == "http://localhost:65001/testarea/repo/"

  after each:
    pass

  after all:
    self.server.stop()
    testutils.teardownrepos()

describe "receiving a package":
 
  before all:
    testutils.setuprepos()

    self.badrepopath = os.path.join(os.getcwd(),'testarea/badrepo/')
    self.repopath = os.path.join(os.getcwd(),'testarea/repo/')
 
  it "throws an exception if the specified repo is not on the filesystem":
    raises Exception: catcher = CatchRPM(targetrepo=self.badrepopath)

  it "remembers the path to the targetrepo":
    catcher = CatchRPM(targetrepo=self.repopath)
    assert catcher.targetrepo == self.repopath 
    
  after all:
    testutils.teardownrepos()



