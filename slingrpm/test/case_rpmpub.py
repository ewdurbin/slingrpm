import sys
import os.path

import testutils

import konira

from slingrpm import SlingRPM
from catchrpm import CatchRPM

describe "pushing a rpm package to our centralized repo":

  before all:
    testutils.setuprepos()
    self.server = testutils.TempServer()
    self.server.start()
    
  after all:
    self.server.stop()
    testutils.teardownrepos()

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

describe "receiving a package":
 
  before all:
    testutils.setuprepos()

    self.badrepopath = os.path.join(os.getcwd(),'testarea/badrepo/')
    self.repopath = os.path.join(os.getcwd(),'testarea/repo/')

  after all:
    testutils.teardownrepos()
 
  it "throws an exception if the specified repo is not on the filesystem":
    raises Exception: catcher = CatchRPM(targetrepo=self.badrepopath)

  it "remembers the path to the targetrepo":
    catcher = CatchRPM(targetrepo=self.repopath)
    assert catcher.targetrepo == self.repopath 
    




