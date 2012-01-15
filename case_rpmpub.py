import konira
from slingrpm import SlingRPM
from slingrpm import CatchRPM
import os.path

describe "pushing a rpm package to our centralized repo":

  it "throws an exception if you dont specify the repo":
    raises Exception: SlingRPM()
  it "throws an exception if the specified repo is not an http location":
    raises Exception: pusher = SlingRPM(targetrepo="foo/bar/bazz")
  it "throws an exception if the specified repo is not a yum repo":
    raises Exception: pusher = SlingRPM(targetrepo="http://localhost:8000/foo")
  it "likes repos with a repmod":
    pusher = SlingRPM("http://localhost:8000/")
    assert pusher

describe "receiving a package":
  it "needs a directory on the filesystem for a repo to live":
    catcher = CatchRPM(repo='/home/pair/testrepo')
    assert os.path.isdir(catcher.targetrepo)
