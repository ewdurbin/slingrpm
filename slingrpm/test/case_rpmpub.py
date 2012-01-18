import konira
import testutils
import sys
import os.path
import ConfigParser

from slingrpm import SlingRPM
from catchrpm import CatchRPM
from setupsling import SetupSling
from configsling import ConfigSling

from slingrpm import NoRepoException
from slingrpm import AlreadySlingEnabledException 

describe "working with the configuration file via ConfigSling":

  before all:
    testutils.setuprepos() 

  before each:
    pass

  it "accepts a full path to a valid repo for an .rpmsling.conf as an input":
    config = ConfigSling(os.path.join(os.getcwd(), 'testarea/repo', '.slingrpm.conf'))
    assert config

  it "raises an Exception if the config file does not exist":
    raises Exception: config = ConfigSling(os.path.join(os.getcwd(), 'testarea/norepo', '.slingrpm.conf'))

  it "raises an Exception if the config file is not a valid ConfigParser config":
    raises Exception: config = ConfigSling(os.path.join(os.getcwd(), 'testarea/badconfrepo', '.slingrpm.conf')) 

  it "exposes the full path to the config":
    config = ConfigSling(os.path.join(os.getcwd(), 'testarea/repo', '.slingrpm.conf'))
    assert config.configlocation == os.path.join(os.getcwd(), 'testarea/repo', '.slingrpm.conf')

  it "exposes the full path to the repository":
    config = ConfigSling(os.path.join(os.getcwd(), 'testarea/repo', '.slingrpm.conf'))
    assert config.repolocation == os.path.join(os.getcwd(), 'testarea/repo')

  it "exposes the subdirectory for uploaded packages":
    config = ConfigSling(os.path.join(os.getcwd(), 'testarea/repo', '.slingrpm.conf'))
    assert config.packagedir == os.path.join(os.getcwd(), 'testarea/repo/')

  it "exposes a port to bind to for communicating":
    config = ConfigSling(os.path.join(os.getcwd(), 'testarea/repo', '.slingrpm.conf'))
    assert config.commport == "64666"

  it "exposes a parameters for the createrepo script to run":
    config = ConfigSling(os.path.join(os.getcwd(), 'testarea/repo', '.slingrpm.conf'))
    assert config.createrepoopts == "--update --excludes .slingrpm.conf --checksum sha"

  after each:
    pass

  after all:
    testutils.teardownrepos() 

describe "setting up a sling enabled repository with SetupSling":

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

  it "remembers the full path of the repository":
    repo = SetupSling('testarea/freshrepo')
    assert repo.config.repolocation == os.path.join(os.getcwd(), 'testarea/freshrepo')

  it "configures .slingrpm.conf to store the correct repoistory path":
    repo = SetupSling('testarea/freshrepo')
    config = ConfigSling('testarea/freshrepo/.slingrpm.conf')
    assert config

  after each:
    testutils.teardownrepos()

  after all:
    pass

describe "pushing a rpm package to our centralized repo":

  before all:
    testutils.setuprepos()
    self.server = testutils.TempServer()
    self.httpport = str(self.server.port)
    self.server.start()

  before each:
    pass
    
  it "throws an exception if you dont specify the repo":
    raises Exception: SlingRPM()

  it "throws an exception if the specified repo is not an http location":
    raises Exception: pusher = SlingRPM(targetrepo="/foo/bar/bazz/")

  it "throws an exception if the specified repo is not a yum repo":
    raises Exception: pusher = SlingRPM(targetrepo="http://localhost:" + self.httpport + "/testarea/badrepo/")

  it "throws an exception if the specified repo is not setup for slingrpm":
    raises Exception: pusher = SlingRPM(targetrepo="http://localhost:" + self.httpport + "/testarea/realrepo/")

  it "likes repos with a repmod and slingrpm":
    pusher = SlingRPM("http://localhost:" + self.httpport + "/testarea/repo/")
    assert pusher

  it "can obtain a full path to the repository from .slingrpm.conf":
    pusher = SlingRPM("http://localhost:" + self.httpport + "/testarea/repo/")
    assert os.path.isdir(pusher.targetpath)

  it "remembers the repo it's been set to publish to":
    pusher = SlingRPM("http://localhost:" + self.httpport + "/testarea/repo/")
    assert pusher.targetrepo == "http://localhost:" + self.httpport + "/testarea/repo/"

  it "reads configs from http or https locations":
    config = ConfigSling("http://localhost:" + self.httpport + "/testarea/repo/.slingrpm.conf")
    assert config

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

  before each:
    pass
 
  it "throws an exception if the specified repo is not on the filesystem":
    raises Exception: catcher = CatchRPM(targetrepo=self.badrepopath)

  it "remembers the path to the targetrepo":
    catcher = CatchRPM(targetrepo=self.repopath)
    assert catcher.targetrepo == self.repopath 

  after each:
    pass
    
  after all:
    testutils.teardownrepos()




