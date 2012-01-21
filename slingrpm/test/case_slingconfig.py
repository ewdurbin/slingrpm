import konira
import os
import os.path

import testutils
from slingrpm import SlingConfig

describe "working with the configuration file via SlingConfig":

  before all:
    testutils.setuprepos() 
    self.server = testutils.TempServer()
    self.httpport = str(self.server.port)
    self.server.start()

  before each:
    pass

  it "accepts a full path to a valid repo for an .rpmsling.conf as an input":
    config = SlingConfig(os.path.join(os.getcwd(), 'testarea/repos/repo', '.slingrpm.conf'))
    assert config

  it "reads configs from http locations":
    config = SlingConfig("http://localhost:" + self.httpport + "/testarea/repos/repo/.slingrpm.conf")
    assert config

  it "raises an Exception if the config file does not exist":
    raises Exception: config = SlingConfig(os.path.join(os.getcwd(), 'testarea/repos/norepo', '.slingrpm.conf'))

  it "raises an Exception if the config file is not a valid ConfigParser config":
    raises Exception: config = SlingConfig(os.path.join(os.getcwd(), 'testarea/repos/badconfrepo', '.slingrpm.conf')) 

  it "exposes the full path to the config":
    config = SlingConfig(os.path.join(os.getcwd(), 'testarea/repos/repo', '.slingrpm.conf'))
    assert config.configlocation == os.path.join(os.getcwd(), 'testarea/repos/repo', '.slingrpm.conf')

  it "exposes the full path to the repository":
    config = SlingConfig(os.path.join(os.getcwd(), 'testarea/repos/repo', '.slingrpm.conf'))
    assert config.repolocation == os.path.join(os.getcwd(), 'testarea/repos/repo')

  it "exposes the subdirectory for uploaded packages":
    config = SlingConfig(os.path.join(os.getcwd(), 'testarea/repos/repo', '.slingrpm.conf'))
    assert config.packagedir == os.path.join(os.getcwd(), 'testarea/repos/repo/')

  it "exposes a port to bind to for communicating":
    config = SlingConfig(os.path.join(os.getcwd(), 'testarea/repos/repo', '.slingrpm.conf'))
    assert config.commport == "64666"

  it "exposes a parameters for the createrepo script to run":
    config = SlingConfig(os.path.join(os.getcwd(), 'testarea/repos/repo', '.slingrpm.conf'))
    assert config.createrepoopts == "--update --excludes .slingrpm.conf --checksum sha"

  after each:
    pass

  after all:
    self.server.stop()
    testutils.teardownrepos() 
