import konira
import os
import os.path

import testutils
from slingrpm import Slinger

describe "pushing rpms with Slinger":

  before all:
    testutils.setuprepos()
    self.server = testutils.TempServer()
    self.httpport = str(self.server.port)
    self.server.start()
    self.goodhttprepo = "http://localhost:" + self.httpport + "/testarea/repo/"
    self.vanillarepo = "http://localhost:" + self.httpport + "/testarea/realrepo/"
    self.badhttprepo = "http://localhost:" + self.httpport + "/testarea/badrepo/"

    self.filetoserve = os.path.join(os.getcwd(), 'slingrpm/test/empty-0-1.i386.rpm')

  before each:
    pass
    
  it "throws an exception if you dont specify the repo":
    raises Exception: Slinger(file=self.filetoserve)

  it "throws an exception if you dont specify a file":
    raises Exception: Slinger(targetrepo=self.goodrepo)

  it "throws an exception if the specified repo is not an http location":
    raises Exception: slinger = Slinger(targetrepo="/foo/bar/bazz/", file=self.filetoserve)

  it "throws an exception if the specified repo is not a yum repo":
    raises Exception: slinger = Slinger(targetrepo=self.badhttprepo, file=self.filetoserve)

  it "throws an exception if the specified repo is not setup for slingrpm":
    raises Exception: slinger = Slinger(targetrepo=self.vanillarepo, file=self.filetoserve)

  it "likes repos with a repmod and slingrpm":
    slinger = Slinger(targetrepo=self.goodhttprepo, file=self.filetoserve)
    assert slinger

  it "remembers the repo it's been set to publish to":
    slinger = Slinger(targetrepo=self.goodhttprepo, file=self.filetoserve)
    assert slinger.targetrepo == self.goodhttprepo

  it "can obtain a full path to the repository from .slingrpm.conf":
    slinger = Slinger(targetrepo=self.goodhttprepo, file=self.filetoserve)
    assert os.path.isdir(slinger.config.repolocation)

  it "can obtain a subdirectory in the repository for pushing packages into":
    slinger = Slinger(targetrepo=self.goodhttprepo, file=self.filetoserve)
    assert slinger.config.packagedir == os.path.join(slinger.config.repolocation, "")

  it "can obtain a daemon port to bind to for communicating":
    slinger = Slinger(targetrepo=self.goodhttprepo, file=self.filetoserve)
    assert slinger.config.commport == str(64666)

  it "starts a SlingerFileServer when serve method is called":
    slinger = Slinger(targetrepo=self.goodhttprepo, file=self.filetoserve)
    slinger.serve()
    assert slinger.fileserver.proc.is_alive()
    slinger.fileserver.stop()

  it "stores the port that the SlingerFileServer was started on when serve method is called":
    slinger = Slinger(targetrepo=self.goodhttprepo, file=self.filetoserve)
    slinger.serve()
    assert slinger.fileserver.port != 0
    slinger.fileserver.stop()

  after each:
    pass

  after all:
    self.server.stop()
    testutils.teardownrepos()


