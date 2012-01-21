import konira
import os
import os.path
import shutil

import testutils
from slingrpm import SlingSetup
from slingrpm import SlingConfig
from slingrpm import NoRepoException
from slingrpm import AlreadySlingEnabledException

describe "setting up a sling enabled repository with SlingSetup":

  before all:
    testutils.setuprepos() 

  before each:
    pass
 
  it "raises NoRepoException if target repo is not a directory which exists":
    raises NoRepoException: repo = SlingSetup('testarea/norepo')

  it "sets up an empty repository if no repomd.xml exists":
    repo = SlingSetup('testarea/freshrepo')
    assert os.path.isfile('testarea/freshrepo/repodata/repomd.xml')

  it "sets up repository metadata if no repomd.xml exists":
    repo = SlingSetup('testarea/realrepo')
    assert os.path.isfile('testarea/realrepo/repodata/repomd.xml')

  it "sets up a .slingrpm.conf if none exists":
    repo = SlingSetup('testarea/freshrepo')
    assert os.path.isfile('testarea/freshrepo/.slingrpm.conf')

  it "raises AlreadySlingEnabledException if repo is already sling enabled":
    raises AlreadySlingEnabledException: repo = SlingSetup('testarea/repo')

  it "remembers the full path of the repository":
    repo = SlingSetup('testarea/freshrepo')
    assert repo.config.repolocation == os.path.join(os.getcwd(), 'testarea/freshrepo')

  it "configures .slingrpm.conf to store the correct repoistory path":
    repo = SlingSetup('testarea/freshrepo')
    config = SlingConfig('testarea/freshrepo/.slingrpm.conf')
    assert config

  after each:
    if os.path.isdir('testarea/freshrepo/repodata'):
      shutil.rmtree('testarea/freshrepo/repodata')
    if os.path.isfile('testarea/freshrepo/.slingrpm.conf'):
      os.remove('testarea/freshrepo/.slingrpm.conf')
    pass

  after all:
    testutils.teardownrepos()


