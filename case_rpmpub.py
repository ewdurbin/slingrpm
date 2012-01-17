import shutil
import time
import os.path
import os

from testutils import TempServer

import konira
from slingrpm import SlingRPM
from slingrpm import CatchRPM

def touch(filename, content="foo"):
  f = open(filename, 'w')
  f.write(content)
  f.close()

def setuprepos():
  if os.path.isdir('testarea'):
    shutil.rmtree('testarea')
  os.makedirs('testarea/badrepo')
  os.makedirs('testarea/repo/repodata')
  os.makedirs('testarea/realrepo/repodata')

  touch('testarea/repo/.slingrpm.conf')
  touch('testarea/repo/repodata/repomd.xml')
  touch('testarea/realrepo/repodata/repomd.xml')

def teardownrepos():
  if os.path.isdir('testarea'):
    shutil.rmtree('testarea')

describe "pushing a rpm package to our centralized repo":

  before all:
    setuprepos()
    self.server = TempServer()
    self.server.start()
    
  after all:
    self.server.stop()
    teardownrepos()

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
    setuprepos()

    self.badrepopath = os.path.join(os.getcwd(),'testarea/badrepo/')
    self.repopath = os.path.join(os.getcwd(),'testarea/repo/')

  after all:
    teardownrepos()
 
  it "throws an exception if the specified repo is not on the filesystem":
    raises Exception: catcher = CatchRPM(targetrepo=self.badrepopath)

  it "remembers the path to the targetrepo":
    catcher = CatchRPM(targetrepo=self.repopath)
    assert catcher.targetrepo == self.repopath 
    




