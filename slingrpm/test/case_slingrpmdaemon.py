import konira

import testutils

from slingrpm import SlingRPMDaemon

describe "the SlingRPMDaemon":

  before all:
    testutils.mocketc()

  it "accepts a configuration file on initialization":
    daemon = SlingRPMDaemon('testarea/etc/slingrpm/daemon.conf')
    assert daemon

  after all:
    testutils.unmocketc()
