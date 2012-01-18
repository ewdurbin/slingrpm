import konira
import os.path

import testutils
from slingrpm import Slinger
from slingrpm import SlingConfig

describe "pushing rpms with Slinger":

  before all:
    testutils.setuprepos()
    self.server = testutils.TempServer()
    self.httpport = str(self.server.port)
    self.server.start()

  before each:
    pass
    
  it "throws an exception if you dont specify the repo":
    raises Exception: Slinger()

  it "throws an exception if the specified repo is not an http location":
    raises Exception: pusher = Slinger(targetrepo="/foo/bar/bazz/")

  it "throws an exception if the specified repo is not a yum repo":
    raises Exception: pusher = Slinger(targetrepo="http://localhost:" + self.httpport + "/testarea/badrepo/")

  it "throws an exception if the specified repo is not setup for slingrpm":
    raises Exception: pusher = Slinger(targetrepo="http://localhost:" + self.httpport + "/testarea/realrepo/")

  it "likes repos with a repmod and slingrpm":
    pusher = Slinger("http://localhost:" + self.httpport + "/testarea/repo/")
    assert pusher

  it "can obtain a full path to the repository from .slingrpm.conf":
    pusher = Slinger("http://localhost:" + self.httpport + "/testarea/repo/")
    assert os.path.isdir(pusher.targetpath)

  it "remembers the repo it's been set to publish to":
    pusher = Slinger("http://localhost:" + self.httpport + "/testarea/repo/")
    assert pusher.targetrepo == "http://localhost:" + self.httpport + "/testarea/repo/"

  it "reads configs from http or https locations":
    config = SlingConfig("http://localhost:" + self.httpport + "/testarea/repo/.slingrpm.conf")
    assert config

  after each:
    pass

  after all:
    self.server.stop()
    testutils.teardownrepos()


