import konira

import testutils
import os
import os.path

from slingrpm import SlingRPMDaemon

goodconf = os.path.join(os.getcwd(), 'testarea/etc/slingrpm/daemon.conf')
badconf = os.path.join(os.getcwd(), 'testarea/etc/slingrpm/bad.conf')
noconf = os.path.join(os.getcwd(), 'testarea/etc/slingrpm/no.conf')

describe "the SlingRPMDaemon":

  before all:
    testutils.mocketc()

  it "accepts a configuration file on initialization":
    daemon = SlingRPMDaemon(goodconf)
    assert daemon

  it "raises an exception if the config file DNE":
    raises Exception: daemon = SlingRPMDaemon(noconf)

  it "raises an exception if the config file sucks":
    raises Exception: daemon = SlingRPMDaemon(badconf)

  it "reads the configuration and exposes a listening port":
    daemon = SlingRPMDaemon(goodconf)
    assert int(daemon.listenport) == 64666

  after all:
    testutils.unmocketc()
