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
    raises NoRepoException: repo = SlingSetup('testarea/repos/norepo')

  it "sets up an empty repository if no repomd.xml exists":
    repo = SlingSetup('testarea/repos/freshrepo')
    assert os.path.isfile('testarea/repos/freshrepo/repodata/repomd.xml')

  it "sets up repository metadata if no repomd.xml exists":
    repo = SlingSetup('testarea/repos/realrepo')
    assert os.path.isfile('testarea/repos/realrepo/repodata/repomd.xml')

  it "sets up a .slingrpm.conf if none exists":
    repo = SlingSetup('testarea/repos/freshrepo')
    assert os.path.isfile('testarea/repos/freshrepo/.slingrpm.conf')

  it "raises AlreadySlingEnabledException if repo is already sling enabled":
    raises AlreadySlingEnabledException: repo = SlingSetup('testarea/repos/repo')

  it "remembers the full path of the repository":
    repo = SlingSetup('testarea/repos/freshrepo')
    assert repo.config.repolocation == os.path.join(os.getcwd(), 'testarea/repos/freshrepo')

  it "configures .slingrpm.conf to store the correct repoistory path":
    repo = SlingSetup('testarea/repos/freshrepo')
    config = SlingConfig('testarea/repos/freshrepo/.slingrpm.conf')
    assert config

  after each:
    if os.path.isdir('testarea/repos/freshrepo/repodata'):
      shutil.rmtree('testarea/repos/freshrepo/repodata')
    if os.path.isfile('testarea/repos/freshrepo/.slingrpm.conf'):
      os.remove('testarea/repos/freshrepo/.slingrpm.conf')
    pass

  after all:
    testutils.teardownrepos()


