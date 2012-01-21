import konira

import os
import os.path

import testutils
from slingrpm import SlingConfig
from slingrpm import YumRepo

goodrepo = os.path.join(os.getcwd(),'testarea/repos/repo/')
realrepo = os.path.join(os.getcwd(),'testarea/repos/realrepo/')
freshrepo = os.path.join(os.getcwd(),'testarea/repos/freshrepo/')
norepo = os.path.join(os.getcwd(),'testarea/repos/norepo/')


describe "slingrpms representation of a yum repository":

  before all:
    testutils.setuprepos()

  it "accepts a directory as an initialization argument":
    repo = YumRepo(goodrepo)
    assert repo

  it "raises an exception if the path is not a directory":
    raises Exception: repo = YumRepo(norepo)

  it "raises an exception if the path is not a slingrpm repository":
    raises Exception: repo = YumRepo(realrepo)

  it "loads the configuration from a valid repository":
    repo = YumRepo(goodrepo)
    assert isinstance(repo.slingconfig, type(SlingConfig()))

  it "has a method which updates the repo metadata with configured options":
    repo = YumRepo(goodrepo)
    assert repo.updatemetadata() == 0

  after all:
    testutils.teardownrepos()
