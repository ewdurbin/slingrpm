import konira
from slingrpm import SlingRPM
from slingrpm import CatchRPM
import os.path

describe "pushing a rpm package to our centralized repo":

  it "throws an exception if you dont specify the repo":
    raises Exception: SlingRPM()
  it "throws an exception if the specified repo is not an http location":
    raises Exception: pusher = SlingRPM(targetrepo="/foo/bar/bazz/")
  it "throws an exception if the specified repo is not a yum repo":
    raises Exception: pusher = SlingRPM(targetrepo="http://localhost:8000/foo/")
  it "throws an exception if the specified repo is not setup for slingrpm":
    raises Exception: pusher = SlingRPM(targetrepo="http://mirrors.kernel.org/centos/6/cr/x86_64/")
  it "likes repos with a repmod and slingrpm":
    pusher = SlingRPM("http://localhost:8000/")
    assert pusher
  it "can obtain a full path to the repository from .slingrpm.conf":
    pusher = SlingRPM("http://localhost:8000/")
    assert os.path.isdir(pusher.targetpath)

describe "receiving a package":
  it "needs a directory on the filesystem for a repo to live":
    catcher = CatchRPM(targetrepo='/home/ernestd/testrepo')
    assert os.path.isdir(catcher.targetrepo)
  it "throws an exception if the target repo is not setup for slingrpm":
    raises Exception: catcher = CatchRPM(targetrepo='/home/ernestd/testrepobad')
    
    
